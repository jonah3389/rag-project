#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库基础配置
"""

from sqlalchemy.ext.declarative import declarative_base, declared_attr


class CustomBase:
    """自定义基类"""

    @declared_attr
    def __tablename__(cls) -> str:
        """
        生成表名，将驼峰命名转换为下划线命名
        例如：KnowledgeBase -> knowledge_base

        Returns:
            str: 表名
        """
        import re

        # 将驼峰命名转换为下划线命名
        name = re.sub("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", cls.__name__)
        return name.lower()


# 创建基类
Base = declarative_base(cls=CustomBase)

# 注意：为避免循环导入，我们不在这里导入模型
# 相关模型的导入应该在 base_class.py 中进行
