#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档 CRUD 操作
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.knowledge.models.knowledge_base import Document
from app.modules.knowledge.schemas.knowledge_base import DocumentCreate, DocumentUpdate


def get(db: Session, id: int) -> Optional[Document]:
    """
    获取文档
    
    Args:
        db: 数据库会话
        id: 文档 ID
        
    Returns:
        Optional[Document]: 文档对象或 None
    """
    return db.query(Document).filter(Document.id == id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """
    获取多个文档
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[Document]: 文档列表
    """
    return db.query(Document).offset(skip).limit(limit).all()


def get_multi_by_knowledge_base(
    db: Session, knowledge_base_id: int, skip: int = 0, limit: int = 100
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
        db.query(Document)
        .filter(Document.knowledge_base_id == knowledge_base_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, obj_in: DocumentCreate) -> Document:
    """
    创建文档
    
    Args:
        db: 数据库会话
        obj_in: 文档创建模型
        
    Returns:
        Document: 创建的文档对象
    """
    db_obj = Document(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_with_knowledge_base(
    db: Session, obj_in: DocumentCreate, knowledge_base_id: int
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
    db_obj = Document(**obj_in_data, knowledge_base_id=knowledge_base_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Document, obj_in: DocumentUpdate) -> Document:
    """
    更新文档
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的文档对象
        obj_in: 文档更新模型
        
    Returns:
        Document: 更新后的文档对象
    """
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> Document:
    """
    删除文档
    
    Args:
        db: 数据库会话
        id: 文档 ID
        
    Returns:
        Document: 删除的文档对象
    """
    obj = db.query(Document).get(id)
    db.delete(obj)
    db.commit()
    return obj
