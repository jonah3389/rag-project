#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库基础配置
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr


class CustomBase:
    """自定义基类"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        生成表名
        
        Returns:
            str: 表名
        """
        return cls.__name__.lower()


# 创建基类
Base = declarative_base(cls=CustomBase)

# 导入所有模型，以便 Alembic 可以创建迁移
from app.modules.auth.models.user import User
from app.modules.chat.models.conversation import Conversation, Message
from app.modules.knowledge.models.knowledge_base import KnowledgeBase, Document
from app.modules.document.models.document import DocumentProcessTask
from app.modules.llm.models.llm_config import LLMConfig
