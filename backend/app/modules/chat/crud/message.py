#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息 CRUD 操作
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.chat.models.conversation import Message
from app.modules.chat.schemas.conversation import MessageCreate, MessageUpdate


def get(db: Session, id: int) -> Optional[Message]:
    """
    获取消息
    
    Args:
        db: 数据库会话
        id: 消息 ID
        
    Returns:
        Optional[Message]: 消息对象或 None
    """
    return db.query(Message).filter(Message.id == id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    """
    获取多个消息
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[Message]: 消息列表
    """
    return db.query(Message).offset(skip).limit(limit).all()


def get_multi_by_conversation(
    db: Session, conversation_id: int, skip: int = 0, limit: int = 100
) -> List[Message]:
    """
    获取对话的多个消息
    
    Args:
        db: 数据库会话
        conversation_id: 对话 ID
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        List[Message]: 消息列表
    """
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, obj_in: MessageCreate) -> Message:
    """
    创建消息
    
    Args:
        db: 数据库会话
        obj_in: 消息创建模型
        
    Returns:
        Message: 创建的消息对象
    """
    db_obj = Message(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_with_conversation(
    db: Session, obj_in: MessageCreate, conversation_id: int
) -> Message:
    """
    创建对话的消息
    
    Args:
        db: 数据库会话
        obj_in: 消息创建模型
        conversation_id: 对话 ID
        
    Returns:
        Message: 创建的消息对象
    """
    obj_in_data = obj_in.model_dump()
    db_obj = Message(**obj_in_data, conversation_id=conversation_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Message, obj_in: MessageUpdate) -> Message:
    """
    更新消息
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的消息对象
        obj_in: 消息更新模型
        
    Returns:
        Message: 更新后的消息对象
    """
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> Message:
    """
    删除消息
    
    Args:
        db: 数据库会话
        id: 消息 ID
        
    Returns:
        Message: 删除的消息对象
    """
    obj = db.query(Message).get(id)
    db.delete(obj)
    db.commit()
    return obj
