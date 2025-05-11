#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 配置相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LLMConfigBase(BaseModel):
    """LLM 配置基础模型"""
    name: str
    provider: str
    model: str
    api_key: str
    api_base: Optional[str] = None
    parameters: Optional[str] = None
    is_default: bool = False


class LLMConfigCreate(LLMConfigBase):
    """创建 LLM 配置模型"""
    pass


class LLMConfigUpdate(BaseModel):
    """更新 LLM 配置模型"""
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    parameters: Optional[str] = None
    is_default: Optional[bool] = None


class LLMConfigInDBBase(LLMConfigBase):
    """数据库中的 LLM 配置模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LLMConfig(LLMConfigInDBBase):
    """API 返回的 LLM 配置模型"""
    pass
