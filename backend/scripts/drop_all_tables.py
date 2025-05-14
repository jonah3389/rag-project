#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除数据库中的所有表
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine

# 设置日志
logger = setup_logging()

def drop_all_tables():
    """删除数据库中的所有表"""
    try:
        # 获取所有表
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"找到 {len(tables)} 个表: {tables}")
        
        # 禁用外键约束
        with engine.connect() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 删除所有表
            for table in tables:
                logger.info(f"删除表: {table}")
                connection.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
            
            # 启用外键约束
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            connection.commit()
        
        logger.info("所有表已删除")
        return True
    
    except Exception as e:
        logger.error(f"删除表时出错: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始删除所有表")
    
    # 确认操作
    confirm = input("此操作将删除数据库中的所有表和数据，是否继续？(y/n): ")
    if confirm.lower() != 'y':
        logger.info("操作已取消")
        sys.exit(0)
    
    success = drop_all_tables()
    if success:
        logger.info("所有表已成功删除")
    else:
        logger.error("删除表失败")
