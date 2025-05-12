#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库基础类
"""

# 导入基类
from app.db.base import Base

# 认证模块 - 最后导入，因为它依赖其他模型
from app.modules.auth.models.user import User

# 导入所有模型，以便 Alembic 可以创建迁移
# 注意：这个文件应该在需要导入所有模型的地方使用，而不是在 base.py 中
# 聊天模块 - 先导入，避免循环引用问题
from app.modules.chat.models.conversation import Conversation, Message

# 文档处理模块
from app.modules.document.models.document import DocumentProcessTask

# 知识库模块
from app.modules.knowledge.models.knowledge_base import Document, KnowledgeBase

# LLM 配置模块
from app.modules.llm.models.llm_config import LLMConfig

# 导出所有模型
__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "KnowledgeBase",
    "Document",
    "DocumentProcessTask",
    "LLMConfig",
]
