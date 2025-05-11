#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库相关的 Pydantic 模型
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
