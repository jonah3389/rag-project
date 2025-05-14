"""
文档处理任务执行器
"""

import logging
import os
import tempfile
import time
from typing import Dict

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.knowledge.crud import document as document_crud
from app.modules.knowledge.crud import document_process_task as task_crud
from app.modules.knowledge.schemas.knowledge_base import (
    DocumentCreate,
    DocumentProcessTaskUpdate,
    TaskStatus,
)
from app.modules.knowledge.services.document_processor import DocumentProcessor
from app.modules.knowledge.services.minio import MinioService
from app.modules.knowledge.services.vector_store import VectorStore

logger = logging.getLogger(__name__)


def process_document(task_id: int) -> Dict:
    """
    处理文档任务

    此函数设计为在独立线程中运行，不会阻塞主应用程序

    Args:
        task_id: 任务ID

    Returns:
        处理结果
    """
    logger.info(f"开始处理文档任务: {task_id}")

    # 添加延迟，避免立即处理，给服务器一些喘息时间
    time.sleep(1)

    # 创建新的数据库会话
    db = SessionLocal()

    # 设置整体超时时间（10分钟）
    MAX_PROCESSING_TIME = 10 * 60  # 10分钟
    start_time = time.time()

    result = {"success": False, "task_id": task_id, "document_id": None, "error": None}

    temp_file_path = None

    try:
        # 获取任务信息
        task = task_crud.get(db=db, id=task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            result["error"] = "任务不存在"
            return result

        # 记录文件大小信息
        file_size_mb = 0
        try:
            minio_service = MinioService()
            file_size = minio_service.get_file_size(task.file_path)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"任务 {task_id} 文件大小: {file_size_mb:.2f} MB")

            # 根据文件大小调整超时时间
            if file_size_mb > 50:
                MAX_PROCESSING_TIME = 30 * 60  # 30分钟
                logger.info(
                    f"文件较大，调整最大处理时间为 {MAX_PROCESSING_TIME / 60} 分钟"
                )
            elif file_size_mb > 20:
                MAX_PROCESSING_TIME = 20 * 60  # 20分钟
                logger.info(
                    f"文件中等大小，调整最大处理时间为 {MAX_PROCESSING_TIME / 60} 分钟"
                )
        except Exception as e:
            logger.warning(f"获取文件大小失败: {str(e)}")

        # 更新任务状态为处理中
        task_crud.update(
            db=db,
            db_obj=task,
            obj_in=DocumentProcessTaskUpdate(status=TaskStatus.PROCESSING),
        )

        try:
            # 从 MinIO 下载文件
            minio_service = MinioService()
            file_content = minio_service.download_file(task.file_path)

            if not file_content:
                logger.error(f"从 MinIO 下载文件失败: {task.file_path}")
                task_crud.update(
                    db=db,
                    db_obj=task,
                    obj_in=DocumentProcessTaskUpdate(
                        status=TaskStatus.FAILED,
                        error_message="从 MinIO 下载文件失败",
                    ),
                )
                result["error"] = "从 MinIO 下载文件失败"
                return result

            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{task.file_type}"
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # 处理文档
                logger.info(f"开始处理文档: {task.file_path}")
                document_processor = DocumentProcessor(
                    use_llm=settings.USE_LLM_FOR_DOCUMENT_PROCESSING
                )

                # 检查是否已经超时
                elapsed_time = time.time() - start_time
                if (
                    elapsed_time > MAX_PROCESSING_TIME * 0.1
                ):  # 如果已经用了10%的时间仅仅是准备工作
                    logger.warning(
                        f"准备工作耗时过长: {elapsed_time:.2f}秒，可能会导致整体处理超时"
                    )

                # 处理文件，设置更严格的超时
                remaining_time = max(
                    int(MAX_PROCESSING_TIME - elapsed_time), 60
                )  # 至少给60秒
                logger.info(f"文件处理剩余时间: {remaining_time}秒")

                # 处理文件
                text, _, chunks = document_processor.process_file(
                    temp_file_path, task.file_type, timeout=remaining_time
                )  # 使用 _ 忽略不需要的 images 变量

                # 再次检查是否超时
                elapsed_time = time.time() - start_time
                if elapsed_time > MAX_PROCESSING_TIME * 0.8:  # 如果已经用了80%的时间
                    logger.warning(
                        f"文件处理耗时过长: {elapsed_time:.2f}秒，可能会影响后续处理"
                    )

                # 检查处理结果
                if text.startswith("文件处理超时") or text.startswith("处理文件时出错"):
                    logger.error(f"文件处理失败: {text}")
                    raise Exception(text)

                logger.info(
                    f"文档处理完成，文本长度: {len(text)}, 分块数量: {len(chunks)}"
                )

                if not text:
                    logger.error("无法从文档中提取文本内容")
                    task_crud.update(
                        db=db,
                        db_obj=task,
                        obj_in=DocumentProcessTaskUpdate(
                            status=TaskStatus.FAILED,
                            error_message="无法从文档中提取文本内容",
                        ),
                    )
                    result["error"] = "无法从文档中提取文本内容"
                    return result

                # 创建文档记录
                logger.info("创建文档记录")
                document_in = DocumentCreate(
                    title=task.file_name,
                    content=text,
                    file_type=task.file_type,
                    file_path=task.file_path,
                )
                document = document_crud.create_with_knowledge_base(
                    db=db, obj_in=document_in, knowledge_base_id=task.knowledge_base_id
                )
                logger.info(f"文档记录创建成功，ID: {document.id}")

                # 更新任务，关联文档
                logger.info(f"开始关联任务 {task.id} 和文档 {document.id}")
                try:
                    # 直接使用 SQLAlchemy 更新
                    task.document_id = document.id
                    db.commit()
                    db.refresh(task)
                    logger.info(
                        f"使用 SQLAlchemy 直接更新成功，任务 {task.id} 现在关联到文档 {document.id}"
                    )

                    # 再次检查关联是否成功
                    updated_task = task_crud.get(db=db, id=task.id)
                    logger.info(
                        f"更新后的任务 {updated_task.id} 关联的文档 ID: {updated_task.document_id}"
                    )

                    if updated_task.document_id != document.id:
                        logger.warning("直接更新失败，尝试使用 CRUD 更新")
                        # 如果直接更新失败，尝试使用 CRUD 更新
                        task_crud.update(
                            db=db,
                            db_obj=task,
                            obj_in=DocumentProcessTaskUpdate(document_id=document.id),
                        )
                        logger.info(
                            f"使用 CRUD 更新成功，任务 {task.id} 现在关联到文档 {document.id}"
                        )
                except Exception as e:
                    logger.error(f"关联任务和文档时出错: {str(e)}")
                    # 继续执行，不要因为关联失败而中断整个处理流程

                # 将文档分块添加到向量数据库
                if chunks:
                    logger.info(f"开始将 {len(chunks)} 个分块添加到向量数据库")
                    vector_store = VectorStore()
                    collection_name = vector_store.get_knowledge_base_collection_name(
                        task.knowledge_base_id
                    )
                    logger.info(f"向量数据库集合名称: {collection_name}")

                    # 准备元数据
                    metadatas = [
                        {
                            "document_id": document.id,
                            "document_title": document.title,
                            "chunk_index": i,
                            "knowledge_base_id": task.knowledge_base_id,
                        }
                        for i in range(len(chunks))
                    ]

                    # 添加到向量数据库
                    logger.info("添加文本到向量数据库")
                    vector_store.add_texts(
                        collection_name=collection_name,
                        texts=chunks,
                        metadatas=metadatas,
                    )
                    logger.info("向量数据库添加完成")

                # 更新任务状态为完成
                task_crud.update(
                    db=db,
                    db_obj=task,
                    obj_in=DocumentProcessTaskUpdate(status=TaskStatus.COMPLETED),
                )

                logger.info(f"文件处理任务完成: {task.file_name}")

                # 设置结果
                result["success"] = True
                result["document_id"] = document.id

            finally:
                # 删除临时文件
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info(f"临时文件已删除: {temp_file_path}")

        except Exception as e:
            logger.error(f"处理文档时出错: {str(e)}")
            # 更新任务状态为失败
            task_crud.update(
                db=db,
                db_obj=task,
                obj_in=DocumentProcessTaskUpdate(
                    status=TaskStatus.FAILED, error_message=str(e)
                ),
            )
            result["error"] = str(e)

    except Exception as e:
        logger.error(f"处理任务时出错: {str(e)}")
        result["error"] = str(e)

    finally:
        # 关闭数据库会话
        db.close()

        # 确保临时文件被删除
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"临时文件已删除: {temp_file_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {str(e)}")

    # 记录总处理时间
    total_time = time.time() - start_time
    logger.info(
        f"任务 {task_id} 处理完成，总耗时: {total_time:.2f}秒，结果: {result['success']}"
    )

    return result
