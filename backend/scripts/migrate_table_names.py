#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表名迁移脚本

将数据库表名从驼峰命名法修改为下划线命名法
例如：KnowledgeBase -> knowledge_base
"""

import re
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.logging import setup_logging

# 设置日志
logger = setup_logging()

# 需要迁移的表名映射
TABLE_MAPPINGS = {
    "knowledgebase": "knowledge_base",
    "documentprocesstask": "document_process_task",
    # 添加其他需要迁移的表名
}

def camel_to_snake(name):
    """
    将驼峰命名转换为下划线命名
    例如：KnowledgeBase -> knowledge_base
    """
    name = re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name)
    return name.lower()

def migrate_table_names():
    """
    迁移数据库表名
    """
    try:
        # 创建数据库引擎
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True,
            echo=True,
        )
        
        # 连接数据库
        with engine.connect() as connection:
            # 获取所有表名
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            logger.info(f"当前数据库表: {tables}")
            
            # 迁移表名
            for old_name, new_name in TABLE_MAPPINGS.items():
                if old_name in tables:
                    logger.info(f"迁移表名: {old_name} -> {new_name}")
                    try:
                        # 检查新表名是否已存在
                        if new_name in tables:
                            logger.warning(f"表 {new_name} 已存在，跳过迁移")
                            continue
                        
                        # 重命名表
                        connection.execute(text(f"RENAME TABLE `{old_name}` TO `{new_name}`"))
                        logger.info(f"表名迁移成功: {old_name} -> {new_name}")
                    except Exception as e:
                        logger.error(f"表名迁移失败: {old_name} -> {new_name}, 错误: {e}")
                else:
                    logger.warning(f"表 {old_name} 不存在，跳过迁移")
            
            # 验证迁移结果
            result = connection.execute(text("SHOW TABLES"))
            tables_after = [row[0] for row in result]
            logger.info(f"迁移后数据库表: {tables_after}")
            
            logger.info("表名迁移完成")
    
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("开始迁移数据库表名")
    success = migrate_table_names()
    if success:
        logger.info("数据库表名迁移成功")
    else:
        logger.error("数据库表名迁移失败")
