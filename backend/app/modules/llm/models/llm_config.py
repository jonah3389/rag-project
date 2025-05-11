#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 配置模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class LLMConfig(Base):
    """LLM 配置模型"""
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    provider = Column(String(64), nullable=False)  # openai, anthropic, etc.
    model = Column(String(64), nullable=False)  # gpt-4, claude-3, etc.
    api_key = Column(String(256), nullable=False)
    api_base = Column(String(256), nullable=True)
    parameters = Column(Text, nullable=True)  # JSON 字符串
    is_default = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="llm_configs")
    conversations = relationship("Conversation", back_populates="llm_config")
