#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 CRUD 操作
"""

from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.modules.knowledge.models.knowledge_base import KnowledgeBase
from app.modules.knowledge.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)


class CRUDKnowledgeBase(
    CRUDBase[KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate]
):
    """知识库 CRUD 操作类"""

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[KnowledgeBase]:
        """
        获取用户的多个知识库

        Args:
            db: 数据库会话
            owner_id: 用户 ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[KnowledgeBase]: 知识库列表
        """
        return (
            db.query(self.model)
            .filter(self.model.user_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, *, obj_in: KnowledgeBaseCreate, owner_id: int
    ) -> KnowledgeBase:
        """
        创建用户的知识库

        Args:
            db: 数据库会话
            obj_in: 知识库创建模型
            owner_id: 用户 ID

        Returns:
            KnowledgeBase: 创建的知识库对象
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, user_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


knowledge_base = CRUDKnowledgeBase(KnowledgeBase)
