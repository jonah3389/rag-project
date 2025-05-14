#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行所有迁移任务
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import setup_logging
from scripts.migrate_table_names import migrate_table_names
from scripts.associate_files_tasks import associate_files_tasks

# 设置日志
logger = setup_logging()

def run_migrations():
    """
    执行所有迁移任务
    """
    logger.info("开始执行迁移任务")
    
    # 1. 迁移表名
    logger.info("步骤 1: 迁移表名")
    success = migrate_table_names()
    if not success:
        logger.error("表名迁移失败，终止迁移")
        return False
    
    # 等待一段时间，确保表名迁移完成
    logger.info("等待 2 秒，确保表名迁移完成")
    time.sleep(2)
    
    # 2. 关联上传文件和处理任务
    logger.info("步骤 2: 关联上传文件和处理任务")
    success = associate_files_tasks()
    if not success:
        logger.error("关联上传文件和处理任务失败")
        return False
    
    logger.info("所有迁移任务执行完成")
    return True

if __name__ == "__main__":
    success = run_migrations()
    if success:
        logger.info("迁移成功")
        sys.exit(0)
    else:
        logger.error("迁移失败")
        sys.exit(1)
