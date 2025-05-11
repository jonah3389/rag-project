#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置
"""
import logging
import sys
from pathlib import Path
from loguru import logger

# 日志文件路径
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
LOG_FILE = LOG_PATH / "app.log"


class InterceptHandler(logging.Handler):
    """
    拦截标准库日志并重定向到loguru
    """
    def emit(self, record):
        # 获取对应的 Loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    配置日志
    """
    # 移除所有处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # 配置标准库日志
    for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]

    # 配置 loguru
    logger.configure(
        handlers=[
            {"sink": sys.stderr, "level": "INFO"},
            {"sink": LOG_FILE, "level": "DEBUG", "rotation": "500 MB"},
        ]
    )
    
    return logger
