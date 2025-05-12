#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主初始化脚本
"""

import argparse
import logging

from init_db import main as init_db_main
from setup_env import main as setup_env_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="初始化脚本")
    parser.add_argument("--skip-env", action="store_true", help="跳过环境变量设置")
    parser.add_argument("--skip-db", action="store_true", help="跳过数据库初始化")

    return parser.parse_args()


def main():
    """
    主函数
    """
    args = parse_args()

    logger.info("开始初始化")

    # 设置环境变量
    if not args.skip_env:
        logger.info("设置环境变量")
        setup_env_main()
    else:
        logger.info("跳过环境变量设置")

    # 初始化数据库
    if not args.skip_db:
        logger.info("初始化数据库")
        init_db_main()
    else:
        logger.info("跳过数据库初始化")

    logger.info("初始化完成")


if __name__ == "__main__":
    main()
