#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class DocumentProcessTask(Base):
    """文档处理任务模型"""
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False, default="pending")  # pending, processing, completed, failed
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledgebase.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="document_tasks")
    knowledge_base = relationship("KnowledgeBase")
