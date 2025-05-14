#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份数据库数据
"""

import json
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal, engine

# 设置日志
logger = setup_logging()

# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "../data/backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    """备份数据库数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
    
    db = SessionLocal()
    try:
        # 获取所有表
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"找到 {len(tables)} 个表: {tables}")
        
        # 备份数据
        backup_data = {}
        for table in tables:
            logger.info(f"备份表: {table}")
            result = db.execute(text(f"SELECT * FROM `{table}`"))
            rows = [dict(row._mapping) for row in result]
            
            # 处理不可序列化的数据类型
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
                    elif hasattr(value, "__dict__"):
                        row[key] = str(value)
            
            backup_data[table] = rows
            logger.info(f"表 {table} 备份了 {len(rows)} 条记录")
        
        # 保存备份文件
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据库备份成功，文件: {backup_file}")
        return backup_file
    
    except Exception as e:
        logger.error(f"备份数据库时出错: {e}")
        return None
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始备份数据库")
    backup_file = backup_database()
    if backup_file:
        logger.info(f"数据库备份成功: {backup_file}")
    else:
        logger.error("数据库备份失败")
