#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """文档基础模型"""

    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    """创建文档模型"""

    pass


class DocumentUpdate(DocumentBase):
    """更新文档模型"""

    title: Optional[str] = None


class DocumentInDBBase(DocumentBase):
    """数据库中的文档模型"""

    id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Document(DocumentInDBBase):
    """API 返回的文档模型"""

    pass


class KnowledgeBaseBase(BaseModel):
    """知识库基础模型"""

    name: str
    description: Optional[str] = None


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """创建知识库模型"""

    pass


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库模型"""

    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeBaseInDBBase(KnowledgeBaseBase):
    """数据库中的知识库模型"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBase(KnowledgeBaseInDBBase):
    """API 返回的知识库模型"""

    documents: List[Document] = []


class SearchQuery(BaseModel):
    """搜索查询模型"""

    query: str
    limit: Optional[int] = 5
    filter: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """搜索结果模型"""

    content: str
    score: float
    document: Document
    metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# 导入 TaskStatus
from app.modules.knowledge.models.knowledge_base import TaskStatus


class DocumentProcessTaskBase(BaseModel):
    """文档处理任务基础模型"""

    file_name: str
    file_type: str
    knowledge_base_id: Optional[int] = None  # 与数据库保持一致
    user_id: int


class DocumentProcessTaskCreate(DocumentProcessTaskBase):
    """创建文档处理任务模型"""

    file_path: str


class DocumentProcessTaskUpdate(BaseModel):
    """更新文档处理任务模型"""

    status: Optional[TaskStatus] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    document_id: Optional[int] = None


class DocumentProcessTaskInDBBase(DocumentProcessTaskBase):
    """数据库中的文档处理任务模型"""

    id: int
    file_path: str
    status: TaskStatus
    result: Optional[str] = None
    error_message: Optional[str] = None
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessTask(DocumentProcessTaskInDBBase):
    """API 返回的文档处理任务模型"""

    document: Optional[Document] = None
