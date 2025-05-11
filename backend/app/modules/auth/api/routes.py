#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关路由
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.modules.auth import crud
from app.modules.auth.api.deps import get_current_active_user, get_current_active_superuser
from app.modules.auth.models.user import User
from app.modules.auth.schemas.user import User as UserSchema
from app.modules.auth.schemas.user import UserCreate, UserUpdate, Token

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    user = crud.user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用",
        )
    user = crud.user.create_user(db, user_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 兼容的令牌登录，获取访问令牌
    """
    user = crud.user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新当前用户信息
    """
    user = crud.user.update_user(db, db_user=current_user, user_in=user_in)
    return user


@router.get("/users", response_model=list[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    获取所有用户（仅超级用户）
    """
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db),
) -> Any:
    """
    通过 ID 获取用户（仅超级用户）
    """
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user
