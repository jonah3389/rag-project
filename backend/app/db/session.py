#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库会话管理
"""

from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import setup_logging

# 设置日志
logger = setup_logging()

# 创建数据库引擎
try:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        echo=True,
        connect_args={"init_command": "SET time_zone = '+08:00'"},
    )
    # 创建会话工厂
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("数据库连接成功")
    is_db_available = True
except OperationalError as e:
    logger.error(f"无法连接到数据库: {e}")
    logger.warning("应用程序将在没有数据库的情况下继续运行，但数据库相关功能将不可用")
    # 创建一个空的会话工厂，用于在数据库不可用时返回 None
    SessionLocal = None
    is_db_available = False


def get_db() -> Generator[Optional[Session], None, None]:
    """
    获取数据库会话

    Yields:
        Optional[Session]: 数据库会话，如果数据库不可用则返回 None
    """
    if not is_db_available:
        logger.warning("数据库不可用，返回 None")
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库操作失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()
