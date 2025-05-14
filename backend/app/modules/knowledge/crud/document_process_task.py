#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理任务 CRUD 操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.modules.knowledge.models.knowledge_base import DocumentProcessTask
from app.modules.knowledge.schemas.knowledge_base import (
    DocumentProcessTaskCreate,
    DocumentProcessTaskUpdate,
)


class CRUDDocumentProcessTask(
    CRUDBase[DocumentProcessTask, DocumentProcessTaskCreate, DocumentProcessTaskUpdate]
):
    """文档处理任务 CRUD 操作类"""

    def get(self, db: Session, id: int) -> Optional[DocumentProcessTask]:
        """
        获取文档处理任务，并加载文档关系

        Args:
            db: 数据库会话
            id: 任务 ID

        Returns:
            Optional[DocumentProcessTask]: 文档处理任务对象
        """
        return (
            db.query(self.model)
            .options(joinedload(self.model.document))
            .filter(self.model.id == id)
            .first()
        )

    def get_multi_by_knowledge_base(
        self, db: Session, *, knowledge_base_id: int, skip: int = 0, limit: int = 100
    ) -> List[DocumentProcessTask]:
        """
        获取知识库的多个文档处理任务

        Args:
            db: 数据库会话
            knowledge_base_id: 知识库 ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[DocumentProcessTask]: 文档处理任务列表
        """
        return (
            db.query(self.model)
            .options(joinedload(self.model.document))
            .filter(self.model.knowledge_base_id == knowledge_base_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_knowledge_base(
        self, db: Session, *, obj_in: DocumentProcessTaskCreate, knowledge_base_id: int
    ) -> DocumentProcessTask:
        """
        创建知识库的文档处理任务

        Args:
            db: 数据库会话
            obj_in: 文档处理任务创建模型
            knowledge_base_id: 知识库 ID

        Returns:
            DocumentProcessTask: 创建的文档处理任务对象
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, knowledge_base_id=knowledge_base_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


document_process_task = CRUDDocumentProcessTask(DocumentProcessTask)
