#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class KnowledgeBase(Base):
    """知识库模型"""
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="knowledge_base")


class Document(Base):
    """文档模型"""
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=True)
    file_type = Column(String(32), nullable=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledgebase.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
