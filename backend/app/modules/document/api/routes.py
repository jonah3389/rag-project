#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理相关路由
"""
import os
from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.document import crud
from app.modules.document.schemas.document import (
    DocumentProcessTask,
    DocumentProcessTaskCreate,
)
from app.modules.document.services.minio import MinioService

router = APIRouter()
minio_service = MinioService()


@router.post("/upload", response_model=DocumentProcessTask)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    knowledge_base_id: int = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    上传文档并创建处理任务
    """
    # 检查文件类型
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持 {', '.join(allowed_extensions)}",
        )
    
    # 上传到 MinIO
    file_content = await file.read()
    file_path = f"documents/{current_user.id}/{file.filename}"
    minio_service.upload_file(file_path, file_content, file.content_type)
    
    # 创建处理任务
    task_in = DocumentProcessTaskCreate(
        file_name=file.filename,
        file_path=file_path,
        file_type=file_extension[1:],
        knowledge_base_id=knowledge_base_id,
    )
    task = crud.document_task.create_with_owner(
        db=db, obj_in=task_in, owner_id=current_user.id
    )
    
    # 触发异步处理任务
    from app.modules.document.tasks.document_processing import process_document
    process_document.delay(task.id)
    
    return task


@router.get("/tasks", response_model=List[DocumentProcessTask])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户的所有文档处理任务
    """
    tasks = crud.document_task.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return tasks


@router.get("/tasks/{task_id}", response_model=DocumentProcessTask)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定文档处理任务
    """
    task = crud.document_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return task


@router.delete("/tasks/{task_id}", response_model=DocumentProcessTask)
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除文档处理任务
    """
    task = crud.document_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    
    # 从 MinIO 中删除文件
    try:
        minio_service.delete_file(task.file_path)
    except Exception as e:
        pass  # 忽略删除文件的错误
    
    task = crud.document_task.remove(db=db, id=task_id)
    return task
