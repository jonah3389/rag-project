#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户 CRUD 操作
"""
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models.user import User
from app.modules.auth.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    通过 ID 获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        Optional[User]: 用户对象或 None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    通过邮箱获取用户
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        
    Returns:
        Optional[User]: 用户对象或 None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    通过用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        Optional[User]: 用户对象或 None
    """
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    获取用户列表
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        list[User]: 用户列表
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    创建用户
    
    Args:
        db: 数据库会话
        user_in: 用户创建模型
        
    Returns:
        User: 创建的用户对象
    """
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, *, db_user: User, user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    更新用户
    
    Args:
        db: 数据库会话
        db_user: 数据库中的用户对象
        user_in: 用户更新模型或字典
        
    Returns:
        User: 更新后的用户对象
    """
    user_data = db_user.__dict__.copy()
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    for field in user_data:
        if field in update_data:
            setattr(db_user, field, update_data[field])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, *, user_id: int) -> User:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        User: 删除的用户对象
    """
    user = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return user


def authenticate(db: Session, *, username: str, password: str) -> Optional[User]:
    """
    认证用户
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        Optional[User]: 认证成功的用户对象或 None
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
