#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

import secrets
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # 基本配置
    PROJECT_NAME: str = "智能体综合应用平台"
    PROJECT_DESCRIPTION: str = "基于大语言模型的综合性应用平台"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天

    # CORS 配置
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = [
        "http://localhost:5173",  # 前端开发服务器
        "http://localhost:5174",  # 前端开发服务器（备用端口）
        "http://localhost:4173",  # 前端预览服务器
        "http://localhost:3000",  # 可能的其他前端服务器
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        "mysql+pymysql://root:password@localhost/rag_platform"
    )

    # MinIO 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "rag-platform"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # LLM 配置
    OPENAI_API_KEY: str = "sk-your-openai-api-key"
    ANTHROPIC_API_KEY: str = "sk-ant-your-anthropic-api-key"

    # 超级用户配置
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    # Pydantic v2 推荐的配置方式
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
    )


settings = Settings()
