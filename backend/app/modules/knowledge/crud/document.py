#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档 CRUD 操作
"""

from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.modules.knowledge.models.knowledge_base import Document
from app.modules.knowledge.schemas.knowledge_base import DocumentCreate, DocumentUpdate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """文档 CRUD 操作类"""

    def get_multi_by_knowledge_base(
        self, db: Session, *, knowledge_base_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        获取知识库的多个文档

        Args:
            db: 数据库会话
            knowledge_base_id: 知识库 ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[Document]: 文档列表
        """
        return (
            db.query(self.model)
            .filter(self.model.knowledge_base_id == knowledge_base_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_knowledge_base(
        self, db: Session, *, obj_in: DocumentCreate, knowledge_base_id: int
    ) -> Document:
        """
        创建知识库的文档

        Args:
            db: 数据库会话
            obj_in: 文档创建模型
            knowledge_base_id: 知识库 ID

        Returns:
            Document: 创建的文档对象
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, knowledge_base_id=knowledge_base_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


document = CRUDDocument(Document)
