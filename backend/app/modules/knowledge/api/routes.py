#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库相关路由
"""

import logging
import os
from datetime import datetime
from typing import Any, List

from app.db.session import get_db
from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.knowledge import crud
from app.modules.knowledge.schemas.knowledge_base import (
    Document,
    DocumentCreate,
    DocumentProcessTask,
    DocumentProcessTaskCreate,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)
from app.modules.knowledge.services.minio import MinioService
from app.modules.knowledge.services.vector_store import VectorStore
from app.modules.knowledge.tasks.document_processing import process_document
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

router = APIRouter()

logger = logging.getLogger(__name__)


def process_document_task(task_id: int):
    """
    处理文档任务

    使用Celery执行文档处理，不会阻塞主应用程序

    Args:
        task_id: 任务 ID
    """
    logger.info(f"提交文档处理任务到Celery: {task_id}")

    # 使用Celery提交任务
    result = process_document.delay(task_id)

    # 不等待任务完成，立即返回
    logger.info(f"文档处理任务已提交到Celery: {task_id}, 任务ID: {result.id}")

    return result


@router.get("/test")
def test_route():
    """
    测试路由
    """
    logger.info("测试路由被调用")
    return {"message": "API 正常工作"}


@router.get("/test-auth")
def test_auth_route(current_user: User = Depends(get_current_active_user)):
    """
    测试认证路由
    """
    logger.info(f"认证测试路由被调用，用户 ID: {current_user.id}")
    return {
        "message": "认证成功",
        "user_id": current_user.id,
        "username": current_user.username,
    }


@router.post("/knowledge-bases", response_model=KnowledgeBase)
def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_in: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新知识库
    """
    knowledge_base = crud.knowledge_base.create_with_owner(
        db=db, obj_in=knowledge_base_in, owner_id=current_user.id
    )
    return knowledge_base


@router.get("/knowledge-bases", response_model=List[KnowledgeBase])
def read_knowledge_bases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户的所有知识库
    """
    knowledge_bases = crud.knowledge_base.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return knowledge_bases


@router.get("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def read_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return knowledge_base


@router.put("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def update_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    knowledge_base_in: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    knowledge_base = crud.knowledge_base.update(
        db=db, db_obj=knowledge_base, obj_in=knowledge_base_in
    )
    return knowledge_base


@router.delete("/knowledge-bases/{knowledge_base_id}", response_model=KnowledgeBase)
def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除知识库
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    # 删除向量数据库中的集合
    vector_store = VectorStore()
    collection_name = vector_store.get_knowledge_base_collection_name(knowledge_base_id)
    vector_store.delete_collection(collection_name)

    knowledge_base = crud.knowledge_base.remove(db=db, id=knowledge_base_id)
    return knowledge_base


@router.post("/knowledge-bases/{knowledge_base_id}/documents", response_model=Document)
def create_document(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新文档
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    document = crud.document.create_with_knowledge_base(
        db=db, obj_in=document_in, knowledge_base_id=knowledge_base_id
    )
    return document


@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents", response_model=List[Document]
)
def read_documents(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取知识库中的所有文档
    """
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    documents = crud.document.get_multi_by_knowledge_base(
        db=db, knowledge_base_id=knowledge_base_id, skip=skip, limit=limit
    )
    return documents


@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
    response_model=Document,
)
def read_document(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    document_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取知识库中的指定文档
    """
    # 检查知识库是否存在
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 检查权限
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    # 获取文档
    document = crud.document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )

    # 检查文档是否属于指定知识库
    if document.knowledge_base_id != knowledge_base_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文档不属于指定知识库",
        )

    return document


@router.delete(
    "/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
    response_model=Document,
)
def delete_document(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    document_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除知识库中的指定文档
    """
    # 检查知识库是否存在
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 检查权限
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    # 获取文档
    document = crud.document.get(db=db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )

    # 检查文档是否属于指定知识库
    if document.knowledge_base_id != knowledge_base_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文档不属于指定知识库",
        )

    # 从向量数据库中删除文档
    try:
        vector_store = VectorStore()
        collection_name = vector_store.get_knowledge_base_collection_name(
            knowledge_base_id
        )
        vector_store.delete_by_metadata(
            collection_name=collection_name,
            metadata_key="document_id",
            metadata_value=document_id,
        )
        logger.info(f"从向量数据库中删除文档: {document_id}")
    except Exception as e:
        logger.error(f"从向量数据库中删除文档时出错: {str(e)}")
        # 继续执行，不要因为向量数据库删除失败而中断整个流程

    # 如果文档有关联的文件，从MinIO中删除
    if document.file_path:
        try:
            minio_service = MinioService()
            minio_service.delete_file(document.file_path)
            logger.info(f"从MinIO中删除文件: {document.file_path}")
        except Exception as e:
            logger.error(f"从MinIO中删除文件时出错: {str(e)}")
            # 继续执行，不要因为MinIO删除失败而中断整个流程

    # 从数据库中删除文档
    document = crud.document.remove(db=db, id=document_id)
    logger.info(f"从数据库中删除文档: {document_id}")

    return document


@router.post(
    "/knowledge-bases/{knowledge_base_id}/upload", response_model=DocumentProcessTask
)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    上传文档到知识库（异步处理）

    上传文件后立即返回任务信息，文件处理在后台异步进行
    """
    logger.info(
        f"开始处理文件上传: {file.filename}, 大小: {file.size if hasattr(file, 'size') else '未知'}"
    )

    # 检查知识库是否存在
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        logger.error(f"知识库不存在: {knowledge_base_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 检查权限
    if knowledge_base.user_id != current_user.id:
        logger.error(f"用户 {current_user.id} 没有权限访问知识库 {knowledge_base_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    # 检查文件类型
    file_extension = os.path.splitext(file.filename)[1].lower()
    logger.info(f"文件类型: {file_extension}")

    if file_extension not in [".pdf", ".txt", ".md", ".doc", ".docx"]:
        logger.error(f"不支持的文件类型: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，目前仅支持 PDF、TXT、Markdown、Word 文档",
        )

    # 读取文件内容
    file_content = await file.read()

    # 生成 MinIO 中的文件路径
    file_type = file_extension[1:]  # 去掉点号
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    minio_file_path = f"knowledge_base/{knowledge_base_id}/{timestamp}_{file.filename}"

    # 上传文件到 MinIO
    minio_service = MinioService()
    upload_success = minio_service.upload_file(
        file_path=minio_file_path,
        file_content=file_content,
        content_type=f"application/{file_type}",
    )

    if not upload_success:
        logger.error(f"上传文件到 MinIO 失败: {minio_file_path}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传文件到 MinIO 失败",
        )
    else:
        logger.info(f"上传文件到 MinIO 成功: {minio_file_path}")

    try:
        # 创建文档处理任务
        task_in = DocumentProcessTaskCreate(
            file_name=file.filename,
            file_path=minio_file_path,
            file_type=file_type,
            knowledge_base_id=knowledge_base_id,
            user_id=current_user.id,
        )

        task = crud.document_process_task.create(db=db, obj_in=task_in)
        logger.info(f"创建文档处理任务成功，ID: {task.id}")

        # 启动后台任务处理文档
        # 使用Celery处理文档，不会阻塞主应用程序
        logger.info(f"启动后台任务处理文档，任务ID: {task.id}")
        result = process_document.delay(task.id)
        logger.info(f"Celery任务已提交，任务ID: {result.id}")

        # 记录文件大小信息，帮助调试
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(f"文件大小: {file_size_mb:.2f} MB")

        return task

    except Exception as e:
        logger.error(f"创建文档处理任务时出错: {str(e)}")
        # 删除 MinIO 中的文件
        minio_service.delete_file(minio_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文档处理任务时出错: {str(e)}",
        )


@router.get("/document-tasks/{task_id}", response_model=DocumentProcessTask)
def get_document_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取文档处理任务状态
    """
    task = crud.document_process_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 检查权限
    knowledge_base = crud.knowledge_base.get(db=db, id=task.knowledge_base_id)
    if not knowledge_base or knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    return task


@router.get(
    "/knowledge-bases/{knowledge_base_id}/document-tasks",
    response_model=List[DocumentProcessTask],
)
def get_knowledge_base_document_tasks(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取知识库的所有文档处理任务
    """
    # 检查知识库是否存在
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 检查权限
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    tasks = crud.document_process_task.get_multi_by_knowledge_base(
        db=db, knowledge_base_id=knowledge_base_id, skip=skip, limit=limit
    )

    return tasks


@router.post("/knowledge-bases/{knowledge_base_id}/search")
def search_knowledge_base(
    *,
    db: Session = Depends(get_db),
    knowledge_base_id: int,
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    在知识库中搜索文档
    """
    # 检查知识库是否存在
    knowledge_base = crud.knowledge_base.get(db=db, id=knowledge_base_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 检查权限
    if knowledge_base.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )

    # 使用向量存储进行搜索
    vector_store = VectorStore()
    collection_name = vector_store.get_knowledge_base_collection_name(knowledge_base_id)

    try:
        # 执行搜索
        results = vector_store.search(
            collection_name=collection_name,
            query=query,
            limit=limit,
            filter={"knowledge_base_id": knowledge_base_id},
        )

        # 处理结果
        search_results = []
        for result in results:
            document_id = result.metadata.get("document_id")
            if document_id:
                document = crud.document.get(db=db, id=document_id)
                if document:
                    search_results.append(
                        {
                            "content": result.page_content,
                            "score": result.score,
                            "document": {
                                "id": document.id,
                                "title": document.title,
                                "file_type": document.file_type,
                            },
                            "metadata": result.metadata,
                        }
                    )

        return {
            "query": query,
            "results": search_results,
            "total": len(search_results),
        }

    except Exception as e:
        logger.error(f"搜索知识库时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识库时出错: {str(e)}",
        )
