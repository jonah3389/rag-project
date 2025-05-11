#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话 CRUD 操作
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.chat.models.conversation import Conversation
from app.modules.chat.schemas.conversation import ConversationCreate, ConversationUpdate


def get(db: Session, id: int) -> Optional[Conversation]:
    """
    获取对话
    
    Args:
        db: 数据库会话
        id: 对话 ID
        
    Returns:
        Optional[Conversation]: 对话对象或 None
    """
    return db.query(Conversation).filter(Conversation.id == id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """
    获取多个对话
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[Conversation]: 对话列表
    """
    return db.query(Conversation).offset(skip).limit(limit).all()


def get_multi_by_owner(
    db: Session, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Conversation]:
    """
    获取用户的多个对话
    
    Args:
        db: 数据库会话
        owner_id: 用户 ID
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[Conversation]: 对话列表
    """
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, obj_in: ConversationCreate) -> Conversation:
    """
    创建对话
    
    Args:
        db: 数据库会话
        obj_in: 对话创建模型
        
    Returns:
        Conversation: 创建的对话对象
    """
    db_obj = Conversation(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_with_owner(
    db: Session, obj_in: ConversationCreate, owner_id: int
) -> Conversation:
    """
    创建用户的对话
    
    Args:
        db: 数据库会话
        obj_in: 对话创建模型
        owner_id: 用户 ID
        
    Returns:
        Conversation: 创建的对话对象
    """
    obj_in_data = obj_in.model_dump()
    db_obj = Conversation(**obj_in_data, user_id=owner_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, db_obj: Conversation, obj_in: ConversationUpdate
) -> Conversation:
    """
    更新对话
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的对话对象
        obj_in: 对话更新模型
        
    Returns:
        Conversation: 更新后的对话对象
    """
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> Conversation:
    """
    删除对话
    
    Args:
        db: 数据库会话
        id: 对话 ID
        
    Returns:
        Conversation: 删除的对话对象
    """
    obj = db.query(Conversation).get(id)
    db.delete(obj)
    db.commit()
    return obj
