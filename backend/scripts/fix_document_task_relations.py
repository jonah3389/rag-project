#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复文档和任务之间的关联关系
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.modules.knowledge.models.knowledge_base import Document, DocumentProcessTask

# 设置日志
logger = setup_logging()

def fix_document_task_relations():
    """修复文档和任务之间的关联关系"""
    db = SessionLocal()
    try:
        # 获取所有没有关联文档的任务
        tasks_without_document = (
            db.query(DocumentProcessTask)
            .filter(DocumentProcessTask.document_id.is_(None))
            .all()
        )
        
        logger.info(f"找到 {len(tasks_without_document)} 个没有关联文档的任务")
        
        # 遍历每个任务，尝试找到对应的文档
        for task in tasks_without_document:
            logger.info(f"处理任务 ID: {task.id}, 文件路径: {task.file_path}")
            
            # 根据文件路径查找文档
            document = (
                db.query(Document)
                .filter(Document.file_path == task.file_path)
                .first()
            )
            
            if document:
                logger.info(f"找到对应文档 ID: {document.id}, 标题: {document.title}")
                
                # 直接使用 SQLAlchemy 更新
                task.document_id = document.id
                db.commit()
                
                # 验证更新是否成功
                db.refresh(task)
                if task.document_id == document.id:
                    logger.info(f"成功关联任务 {task.id} 和文档 {document.id}")
                else:
                    logger.error(f"关联任务 {task.id} 和文档 {document.id} 失败")
            else:
                logger.warning(f"未找到任务 {task.id} 对应的文档，文件路径: {task.file_path}")
        
        # 验证修复结果
        tasks_without_document_after = (
            db.query(DocumentProcessTask)
            .filter(DocumentProcessTask.document_id.is_(None))
            .all()
        )
        
        logger.info(f"修复后还有 {len(tasks_without_document_after)} 个没有关联文档的任务")
        
        # 如果还有未关联的任务，尝试使用原始 SQL 更新
        if tasks_without_document_after:
            logger.info("尝试使用原始 SQL 更新未关联的任务")
            
            for task in tasks_without_document_after:
                # 使用原始 SQL 查询对应的文档
                result = db.execute(
                    text(
                        "SELECT id FROM document WHERE file_path = :file_path LIMIT 1"
                    ),
                    {"file_path": task.file_path},
                )
                
                document_id = result.scalar()
                if document_id:
                    # 使用原始 SQL 更新任务
                    db.execute(
                        text(
                            "UPDATE document_process_task SET document_id = :document_id WHERE id = :task_id"
                        ),
                        {"document_id": document_id, "task_id": task.id},
                    )
                    db.commit()
                    logger.info(f"使用原始 SQL 成功关联任务 {task.id} 和文档 {document_id}")
        
        return True
    
    except Exception as e:
        logger.error(f"修复文档和任务关联关系时出错: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始修复文档和任务之间的关联关系")
    success = fix_document_task_relations()
    if success:
        logger.info("修复文档和任务关联关系成功")
    else:
        logger.error("修复文档和任务关联关系失败")
