#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentProcessTaskBase(BaseModel):
    """文档处理任务基础模型"""
    file_name: str
    file_path: str
    file_type: str
    knowledge_base_id: Optional[int] = None


class DocumentProcessTaskCreate(DocumentProcessTaskBase):
    """创建文档处理任务模型"""
    pass


class DocumentProcessTaskUpdate(BaseModel):
    """更新文档处理任务模型"""
    status: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None


class DocumentProcessTaskInDBBase(DocumentProcessTaskBase):
    """数据库中的文档处理任务模型"""
    id: int
    user_id: int
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessTask(DocumentProcessTaskInDBBase):
    """API 返回的文档处理任务模型"""
    pass
