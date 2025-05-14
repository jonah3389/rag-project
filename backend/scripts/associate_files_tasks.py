#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关联上传文件和处理任务

确保每个上传的文件都有对应的处理任务，并且每个处理任务都关联到正确的文档
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.core.logging import setup_logging
from app.modules.knowledge.models.knowledge_base import Document, DocumentProcessTask
from app.modules.knowledge.services.minio import MinioService

# 设置日志
logger = setup_logging()

def associate_files_tasks():
    """
    关联上传文件和处理任务
    
    1. 查找所有没有关联文档的处理任务
    2. 根据文件路径查找对应的文档
    3. 关联处理任务和文档
    """
    db = SessionLocal()
    try:
        # 查找所有已完成但没有关联文档的处理任务
        tasks = (
            db.query(DocumentProcessTask)
            .filter(DocumentProcessTask.document_id.is_(None))
            .all()
        )
        
        logger.info(f"找到 {len(tasks)} 个未关联文档的处理任务")
        
        # 初始化 MinIO 服务
        minio_service = MinioService()
        
        # 关联处理任务和文档
        for task in tasks:
            logger.info(f"处理任务 ID: {task.id}, 文件路径: {task.file_path}")
            
            # 根据文件路径查找对应的文档
            document = (
                db.query(Document)
                .filter(Document.file_path == task.file_path)
                .first()
            )
            
            if document:
                logger.info(f"找到对应文档 ID: {document.id}, 标题: {document.title}")
                
                # 关联处理任务和文档
                task.document_id = document.id
                db.commit()
                logger.info(f"成功关联任务 {task.id} 和文档 {document.id}")
            else:
                logger.warning(f"未找到任务 {task.id} 对应的文档，文件路径: {task.file_path}")
                
                # 检查 MinIO 中是否存在该文件
                if minio_service.download_file(task.file_path):
                    logger.info(f"MinIO 中存在文件: {task.file_path}")
                    
                    # 创建文档记录
                    document = Document(
                        title=task.file_name,
                        file_path=task.file_path,
                        file_type=task.file_type,
                        knowledge_base_id=task.knowledge_base_id,
                    )
                    db.add(document)
                    db.commit()
                    db.refresh(document)
                    
                    # 关联处理任务和文档
                    task.document_id = document.id
                    db.commit()
                    logger.info(f"创建并关联文档 {document.id} 到任务 {task.id}")
                else:
                    logger.error(f"MinIO 中不存在文件: {task.file_path}")
        
        # 验证关联结果
        tasks_after = (
            db.query(DocumentProcessTask)
            .filter(DocumentProcessTask.document_id.is_(None))
            .all()
        )
        
        logger.info(f"关联后还有 {len(tasks_after)} 个未关联文档的处理任务")
        
        return True
    
    except Exception as e:
        logger.error(f"关联文件和任务时出错: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始关联上传文件和处理任务")
    success = associate_files_tasks()
    if success:
        logger.info("关联上传文件和处理任务成功")
    else:
        logger.error("关联上传文件和处理任务失败")
