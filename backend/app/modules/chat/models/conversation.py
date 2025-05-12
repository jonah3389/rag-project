#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话模型
"""

from datetime import datetime

from app.db.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Conversation(Base):
    """对话模型"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    llm_config_id = Column(Integer, ForeignKey("llmconfig.id"), nullable=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledgebase.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship(
        "User", back_populates="conversations", lazy="joined"
    )  # 使用 joined 加载
    llm_config = relationship(
        "LLMConfig", back_populates="conversations", lazy="joined"
    )  # 使用 joined 加载
    knowledge_base = relationship(
        "KnowledgeBase", back_populates="conversations", lazy="joined"
    )  # 使用 joined 加载
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )  # 使用动态加载


class Message(Base):
    """消息模型"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")
