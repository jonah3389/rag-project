#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 配置相关路由
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.llm import crud
from app.modules.llm.schemas.llm_config import (
    LLMConfig,
    LLMConfigCreate,
    LLMConfigUpdate,
)

router = APIRouter()


@router.post("/configs", response_model=LLMConfig)
def create_llm_config(
    *,
    db: Session = Depends(get_db),
    llm_config_in: LLMConfigCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新的 LLM 配置
    """
    # 如果设置为默认，则将其他配置设为非默认
    if llm_config_in.is_default:
        crud.llm_config.reset_default(db=db, owner_id=current_user.id)
    
    llm_config = crud.llm_config.create_with_owner(
        db=db, obj_in=llm_config_in, owner_id=current_user.id
    )
    return llm_config


@router.get("/configs", response_model=List[LLMConfig])
def read_llm_configs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前用户的所有 LLM 配置
    """
    llm_configs = crud.llm_config.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return llm_configs


@router.get("/configs/{llm_config_id}", response_model=LLMConfig)
def read_llm_config(
    *,
    db: Session = Depends(get_db),
    llm_config_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定 LLM 配置
    """
    llm_config = crud.llm_config.get(db=db, id=llm_config_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM 配置不存在",
        )
    if llm_config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return llm_config


@router.put("/configs/{llm_config_id}", response_model=LLMConfig)
def update_llm_config(
    *,
    db: Session = Depends(get_db),
    llm_config_id: int,
    llm_config_in: LLMConfigUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新 LLM 配置
    """
    llm_config = crud.llm_config.get(db=db, id=llm_config_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM 配置不存在",
        )
    if llm_config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    
    # 如果设置为默认，则将其他配置设为非默认
    if llm_config_in.is_default:
        crud.llm_config.reset_default(db=db, owner_id=current_user.id)
    
    llm_config = crud.llm_config.update(
        db=db, db_obj=llm_config, obj_in=llm_config_in
    )
    return llm_config


@router.delete("/configs/{llm_config_id}", response_model=LLMConfig)
def delete_llm_config(
    *,
    db: Session = Depends(get_db),
    llm_config_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除 LLM 配置
    """
    llm_config = crud.llm_config.get(db=db, id=llm_config_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM 配置不存在",
        )
    if llm_config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    llm_config = crud.llm_config.remove(db=db, id=llm_config_id)
    return llm_config


@router.get("/providers", response_model=List[dict])
def read_providers() -> Any:
    """
    获取支持的 LLM 提供商列表
    """
    providers = [
        {
            "id": "openai",
            "name": "OpenAI",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        },
        {
            "id": "google",
            "name": "Google",
            "models": ["gemini-pro", "gemini-ultra"],
        },
        {
            "id": "zhipu",
            "name": "智谱 AI",
            "models": ["glm-4", "glm-3-turbo"],
        },
        {
            "id": "baidu",
            "name": "百度文心",
            "models": ["ernie-bot-4", "ernie-bot"],
        },
    ]
    return providers
