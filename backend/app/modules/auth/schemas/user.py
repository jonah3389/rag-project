#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# 共享属性
class UserBase(BaseModel):
    """用户基础模型"""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# 创建用户时的属性
class UserCreate(UserBase):
    """创建用户模型"""

    email: EmailStr
    username: str
    password: str


# 更新用户时的属性
class UserUpdate(UserBase):
    """更新用户模型"""

    password: Optional[str] = None


# 数据库中存储的用户属性
class UserInDBBase(UserBase):
    """数据库中的用户模型"""

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Pydantic v2 语法
    model_config = ConfigDict(from_attributes=True)


# 返回给客户端的用户属性
class User(UserInDBBase):
    """API 返回的用户模型"""

    pass


# 存储在数据库中的用户附加属性
class UserInDB(UserInDBBase):
    """数据库中的用户模型（包含哈希密码）"""

    hashed_password: str


# 用户登录模型
class UserLogin(BaseModel):
    """用户登录模型"""

    username: str
    password: str


# 令牌模型
class Token(BaseModel):
    """令牌模型"""

    access_token: str
    token_type: str


# 令牌数据模型
class TokenPayload(BaseModel):
    """令牌数据模型"""

    sub: Optional[int] = None
