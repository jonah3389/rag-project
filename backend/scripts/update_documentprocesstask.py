#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 documentprocesstask 表结构
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.core.config import settings

def update_documentprocesstask_table():
    """更新 documentprocesstask 表结构"""
    # 创建数据库连接
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    # 连接数据库
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        try:
            # 检查表是否存在
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'rag_platform' AND table_name = 'documentprocesstask'"
            ))
            if result.scalar() == 0:
                print("表 documentprocesstask 不存在，无需更新")
                return
            
            # 1. 将 error 列重命名为 error_message
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = 'rag_platform' AND table_name = 'documentprocesstask' "
                "AND column_name = 'error_message'"
            ))
            if result.scalar() > 0:
                print("列 error_message 已存在，无需重命名")
            else:
                # 检查 error 列是否存在
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.columns "
                    "WHERE table_schema = 'rag_platform' AND table_name = 'documentprocesstask' "
                    "AND column_name = 'error'"
                ))
                if result.scalar() > 0:
                    # 重命名 error 列为 error_message
                    conn.execute(text(
                        "ALTER TABLE documentprocesstask "
                        "CHANGE COLUMN error error_message TEXT NULL"
                    ))
                    print("已将 error 列重命名为 error_message")
                else:
                    # 添加 error_message 列
                    conn.execute(text(
                        "ALTER TABLE documentprocesstask "
                        "ADD COLUMN error_message TEXT NULL"
                    ))
                    print("已添加 error_message 列")
            
            # 2. 修改 status 列类型
            result = conn.execute(text(
                "SELECT column_type FROM information_schema.columns "
                "WHERE table_schema = 'rag_platform' AND table_name = 'documentprocesstask' "
                "AND column_name = 'status'"
            ))
            column_type = result.scalar()
            if column_type == "enum('PENDING','PROCESSING','COMPLETED','FAILED')":
                print("列 status 类型已正确，无需修改")
            else:
                # 修改 status 列类型
                conn.execute(text(
                    "ALTER TABLE documentprocesstask "
                    "MODIFY COLUMN status ENUM('PENDING','PROCESSING','COMPLETED','FAILED') NOT NULL DEFAULT 'PENDING'"
                ))
                print("已修改 status 列类型")
            
            # 3. 确保 user_id 列不为空
            # 注意：如果已有记录的 user_id 为 NULL，需要先设置一个默认值
            result = conn.execute(text(
                "SELECT COUNT(*) FROM documentprocesstask WHERE user_id IS NULL"
            ))
            null_count = result.scalar()
            if null_count > 0:
                # 将 NULL 值设置为默认管理员用户 ID (1)
                conn.execute(text(
                    "UPDATE documentprocesstask SET user_id = 1 WHERE user_id IS NULL"
                ))
                print(f"已将 {null_count} 条记录的 user_id 从 NULL 更新为 1")
            
            # 修改 user_id 列为不可为空
            conn.execute(text(
                "ALTER TABLE documentprocesstask "
                "MODIFY COLUMN user_id INT NOT NULL"
            ))
            print("已修改 user_id 列为不可为空")
            
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
