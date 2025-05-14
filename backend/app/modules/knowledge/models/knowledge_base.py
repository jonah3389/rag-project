#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库模型
"""

from datetime import datetime, timezone
from enum import Enum

import pytz
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base import Base

# 获取当前时区
local_tz = pytz.timezone("Asia/Shanghai")  # 使用中国时区


def get_now_datetime():
    """获取当前时间（带时区）"""
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"  # 等待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"  # 失败


class KnowledgeBase(Base):
    """知识库模型"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=get_now_datetime)
    updated_at = Column(DateTime, default=get_now_datetime, onupdate=get_now_datetime)

    # 关系
    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship(
        "Document", back_populates="knowledge_base", cascade="all, delete-orphan"
    )
    conversations = relationship("Conversation", back_populates="knowledge_base")
    document_process_tasks = relationship(
        "DocumentProcessTask",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )


class Document(Base):
    """文档模型"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=True)
    file_type = Column(String(32), nullable=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"), nullable=False)
    created_at = Column(DateTime, default=get_now_datetime)
    updated_at = Column(DateTime, default=get_now_datetime, onupdate=get_now_datetime)

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


class DocumentProcessTask(Base):
    """文档处理任务模型"""

    __tablename__ = "document_process_task"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(32), nullable=False)
    status = Column(
        SQLAlchemyEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    result = Column(Text, nullable=True)  # 处理结果
    error_message = Column(Text, nullable=True)  # 错误信息
    knowledge_base_id = Column(
        Integer, ForeignKey("knowledge_base.id"), nullable=True
    )  # 与数据库保持一致
    document_id = Column(Integer, ForeignKey("document.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=get_now_datetime)
    updated_at = Column(DateTime, default=get_now_datetime, onupdate=get_now_datetime)

    # 关系
    knowledge_base = relationship(
        "KnowledgeBase", back_populates="document_process_tasks"
    )
    document = relationship("Document", backref="process_task")
    user = relationship("User", back_populates="document_tasks")
