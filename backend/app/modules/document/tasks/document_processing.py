#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理任务
"""
import io
import json
import os
import tempfile
from typing import Dict, List, Optional

from celery import shared_task
from sqlalchemy.orm import Session

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.modules.document import crud
from app.modules.document.services.minio import MinioService
from app.modules.knowledge import crud as knowledge_crud
from app.modules.knowledge.schemas.knowledge_base import DocumentCreate

logger = setup_logging()
minio_service = MinioService()


@shared_task
def process_document(task_id: int):
    """
    处理文档
    
    Args:
        task_id: 任务 ID
    """
    db = SessionLocal()
    try:
        # 获取任务
        task = crud.document_task.get(db, id=task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return
        
        # 更新任务状态
        crud.document_task.update_status(db, task_id=task_id, status="processing")
        
        # 下载文件
        file_content = minio_service.download_file(task.file_path)
        
        # 根据文件类型处理
        if task.file_type == "pdf":
            text_content = process_pdf(file_content)
        elif task.file_type in ["doc", "docx"]:
            text_content = process_docx(file_content)
        elif task.file_type == "txt":
            text_content = process_txt(file_content)
        else:
            raise ValueError(f"不支持的文件类型: {task.file_type}")
        
        # 如果指定了知识库，则创建文档
        if task.knowledge_base_id:
            document_in = DocumentCreate(
                title=task.file_name,
                content=text_content,
                file_path=task.file_path,
                file_type=task.file_type,
            )
            knowledge_crud.document.create_with_knowledge_base(
                db=db,
                obj_in=document_in,
                knowledge_base_id=task.knowledge_base_id,
            )
        
        # 更新任务状态
        crud.document_task.update_status(
            db,
            task_id=task_id,
            status="completed",
            result=json.dumps({"text_content": text_content[:1000] + "..." if len(text_content) > 1000 else text_content}),
        )
        
    except Exception as e:
        logger.error(f"处理文档失败: {e}")
        # 更新任务状态
        crud.document_task.update_status(
            db,
            task_id=task_id,
            status="failed",
            error=str(e),
        )
    finally:
        db.close()


def process_pdf(file_content: bytes) -> str:
    """
    处理 PDF 文件
    
    Args:
        file_content: 文件内容
        
    Returns:
        str: 文本内容
    """
    import PyPDF2
    
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_content = ""
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text_content += page.extract_text() + "\n\n"
    
    return text_content


def process_docx(file_content: bytes) -> str:
    """
    处理 DOCX 文件
    
    Args:
        file_content: 文件内容
        
    Returns:
        str: 文本内容
    """
    import docx2txt
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        text_content = docx2txt.process(temp_file_path)
        return text_content
    finally:
        os.unlink(temp_file_path)


def process_txt(file_content: bytes) -> str:
    """
    处理 TXT 文件
    
    Args:
        file_content: 文件内容
        
    Returns:
        str: 文本内容
    """
    # 尝试不同的编码
    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
    
    for encoding in encodings:
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # 如果所有编码都失败，使用 latin-1（它可以解码任何字节序列）
    return file_content.decode("latin-1")
