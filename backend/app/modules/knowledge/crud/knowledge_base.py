#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 CRUD 操作
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.knowledge.models.knowledge_base import KnowledgeBase
from app.modules.knowledge.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate


def get(db: Session, id: int) -> Optional[KnowledgeBase]:
    """
    获取知识库
    
    Args:
        db: 数据库会话
        id: 知识库 ID
        
    Returns:
        Optional[KnowledgeBase]: 知识库对象或 None
    """
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeBase]:
    """
    获取多个知识库
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[KnowledgeBase]: 知识库列表
    """
    return db.query(KnowledgeBase).offset(skip).limit(limit).all()


def get_multi_by_owner(
    db: Session, owner_id: int, skip: int = 0, limit: int = 100
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
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.user_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, obj_in: KnowledgeBaseCreate) -> KnowledgeBase:
    """
    创建知识库
    
    Args:
        db: 数据库会话
        obj_in: 知识库创建模型
        
    Returns:
        KnowledgeBase: 创建的知识库对象
    """
    db_obj = KnowledgeBase(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_with_owner(
    db: Session, obj_in: KnowledgeBaseCreate, owner_id: int
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
    db_obj = KnowledgeBase(**obj_in_data, user_id=owner_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, db_obj: KnowledgeBase, obj_in: KnowledgeBaseUpdate
) -> KnowledgeBase:
    """
    更新知识库
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的知识库对象
        obj_in: 知识库更新模型
        
    Returns:
        KnowledgeBase: 更新后的知识库对象
    """
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> KnowledgeBase:
    """
    删除知识库
    
    Args:
        db: 数据库会话
        id: 知识库 ID
        
    Returns:
        KnowledgeBase: 删除的知识库对象
    """
    obj = db.query(KnowledgeBase).get(id)
    db.delete(obj)
    db.commit()
    return obj
