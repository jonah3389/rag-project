#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

from datetime import datetime

from app.db.base import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """用户模型"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    # 使用字符串引用和延迟加载避免循环导入问题
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",  # 使用动态加载
    )
    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",  # 使用动态加载
    )
    llm_configs = relationship(
        "LLMConfig",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",  # 使用动态加载
    )
    document_tasks = relationship(
        "DocumentProcessTask",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",  # 使用动态加载
    )
