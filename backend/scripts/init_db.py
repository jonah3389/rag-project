#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入顺序很重要，先导入基础模块
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import SessionLocal, engine

# 导入所有模型以确保它们被注册到 Base.metadata
from app.modules.auth.models.user import User
from app.modules.chat.models.conversation import Conversation, Message
from app.modules.knowledge.models.knowledge_base import KnowledgeBase, Document, DocumentProcessTask
from app.modules.llm.models.llm_config import LLMConfig

# 最后导入 User 模型和相关模块
from app.modules.auth import crud, schemas

# 设置日志
logger = setup_logging()


def init_db(db) -> None:
    """
    初始化数据库

    Args:
        db: 数据库会话
    """
    # 设置时区
    with engine.connect() as connection:
        connection.execute(text("SET time_zone = '+08:00'"))
        connection.commit()
        logger.info("数据库时区设置为 +08:00")
    
    # 创建超级用户
    user = crud.user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.user.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="超级管理员",
        )
        user = crud.user.create_user(db, user_in=user_in)
        logger.info(f"创建超级用户: {user.username}")

    # 创建默认 LLM 配置
    llm_config = (
        db.query(LLMConfig)
        .filter(LLMConfig.user_id == user.id, LLMConfig.is_default == True)
        .first()
    )

    if not llm_config:
        llm_config = LLMConfig(
            name="默认 OpenAI 配置",
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=settings.OPENAI_API_KEY,
            api_base=settings.OPENAI_API_BASE,
            is_default=True,
            user_id=user.id,
        )
        db.add(llm_config)
        db.commit()
        logger.info(f"创建默认 LLM 配置: {llm_config.name}")


def main() -> None:
    """
    主函数
    """
    logger.info("创建数据库表")
    Base.metadata.create_all(bind=engine)

    logger.info("初始化数据")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    logger.info("数据库初始化完成")


if __name__ == "__main__":
    main()
