#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 documentprocesstask 表结构，添加缺失的 document_id 列
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.core.config import settings

def update_documentprocesstask_table():
    """更新 documentprocesstask 表结构，添加缺失的 document_id 列"""
    # 创建数据库连接
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    # 连接数据库
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        try:
            # 检查 document_id 列是否存在
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = 'rag_platform' AND table_name = 'documentprocesstask' "
                "AND column_name = 'document_id'"
            ))
            if result.scalar() > 0:
                print("列 document_id 已存在，无需添加")
            else:
                # 添加 document_id 列
                conn.execute(text(
                    "ALTER TABLE documentprocesstask "
                    "ADD COLUMN document_id INT NULL, "
                    "ADD CONSTRAINT fk_documentprocesstask_document "
                    "FOREIGN KEY (document_id) REFERENCES document(id)"
                ))
                print("已添加 document_id 列")
            
            # 提交事务
            trans.commit()
            print("表 documentprocesstask 更新完成")
        
        except Exception as e:
            # 回滚事务
            trans.rollback()
            print(f"更新表结构时出错: {str(e)}")
            raise

if __name__ == "__main__":
    update_documentprocesstask_table()
