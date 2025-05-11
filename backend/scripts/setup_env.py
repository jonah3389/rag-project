#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量设置脚本
"""
import os
import secrets
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent


def create_env_file():
    """
    创建 .env 文件
    """
    env_example_path = ROOT_DIR / ".env.example"
    env_path = ROOT_DIR / ".env"
    
    if not env_example_path.exists():
        logger.error(f".env.example 文件不存在: {env_example_path}")
        return False
    
    if env_path.exists():
        logger.info(f".env 文件已存在: {env_path}")
        return True
    
    # 复制 .env.example 到 .env
    shutil.copy(env_example_path, env_path)
    
    # 生成随机密钥
    secret_key = secrets.token_urlsafe(32)
    
    # 读取 .env 文件内容
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换密钥
    content = content.replace("your_secret_key_here", secret_key)
    
    # 写入 .env 文件
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"创建 .env 文件: {env_path}")
    logger.info(f"生成随机密钥: {secret_key}")
    
    return True


def main():
    """
    主函数
    """
    logger.info("设置环境变量")
    
    if create_env_file():
        logger.info("环境变量设置完成")
    else:
        logger.error("环境变量设置失败")


if __name__ == "__main__":
    main()
