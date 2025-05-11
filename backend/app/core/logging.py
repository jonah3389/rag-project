#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置
"""

import logging
import sys
from pathlib import Path

# 日志文件路径
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
LOG_FILE = LOG_PATH / "app.log"


def setup_logging():
    """
    配置日志
    """
    # 配置标准库日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(LOG_FILE),
        ],
    )

    # 获取 logger
    logger = logging.getLogger("app")

    return logger
