#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置数据库：备份、删除所有表、重新创建表
"""

import os
import sys
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import setup_logging
from scripts.backup_database import backup_database
from scripts.drop_all_tables import drop_all_tables
from scripts.init_db import main as init_db

# 设置日志
logger = setup_logging()

def reset_database():
    """重置数据库"""
    logger.info("开始重置数据库")
    
    # 1. 备份数据库
    logger.info("步骤 1: 备份数据库")
    backup_file = backup_database()
    if not backup_file:
        logger.warning("数据库备份失败，但将继续执行重置操作")
    else:
        logger.info(f"数据库备份成功: {backup_file}")
    
    # 2. 删除所有表
    logger.info("步骤 2: 删除所有表")
    success = drop_all_tables()
    if not success:
        logger.error("删除表失败，终止重置操作")
        return False
    
    # 等待一段时间，确保表删除完成
    logger.info("等待 2 秒，确保表删除完成")
    time.sleep(2)
    
    # 3. 重新创建表
    logger.info("步骤 3: 重新创建表")
    try:
        init_db()
        logger.info("表创建成功")
    except Exception as e:
        logger.error(f"创建表时出错: {e}")
        return False
    
    logger.info("数据库重置完成")
    return True

if __name__ == "__main__":
    logger.info("开始执行数据库重置")
    
    # 确认操作
    confirm = input("此操作将删除数据库中的所有表和数据，是否继续？(y/n): ")
    if confirm.lower() != 'y':
        logger.info("操作已取消")
        sys.exit(0)
    
    success = reset_database()
    if success:
        logger.info("数据库重置成功")
    else:
        logger.error("数据库重置失败")
