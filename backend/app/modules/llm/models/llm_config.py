#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 配置模型
"""

from datetime import datetime, timezone

from app.db.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


def get_now_datetime():
    """获取当前时间（带时区）"""
    return datetime.now(timezone.utc)


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
    created_at = Column(DateTime, default=get_now_datetime)
    updated_at = Column(DateTime, default=get_now_datetime, onupdate=get_now_datetime)

    # 关系
    user = relationship("User", back_populates="llm_configs")
    conversations = relationship("Conversation", back_populates="llm_config")
