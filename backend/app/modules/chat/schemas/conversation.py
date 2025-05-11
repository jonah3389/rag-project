#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话相关的 Pydantic 模型
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    """消息基础模型"""
    role: str
    content: str


class MessageCreate(MessageBase):
    """创建消息模型"""
    pass


class MessageUpdate(MessageBase):
    """更新消息模型"""
    pass


class MessageInDBBase(MessageBase):
    """数据库中的消息模型"""
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Message(MessageInDBBase):
    """API 返回的消息模型"""
    pass


class ConversationBase(BaseModel):
    """对话基础模型"""
    title: str
    llm_config_id: Optional[int] = None
    knowledge_base_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    """创建对话模型"""
    pass


class ConversationUpdate(BaseModel):
    """更新对话模型"""
    title: Optional[str] = None
    llm_config_id: Optional[int] = None
    knowledge_base_id: Optional[int] = None


class ConversationInDBBase(ConversationBase):
    """数据库中的对话模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Conversation(ConversationInDBBase):
    """API 返回的对话模型"""
    messages: List[Message] = []
