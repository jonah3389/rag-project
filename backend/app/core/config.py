#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

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
    SECRET_KEY: str = (
        "YYVNy41zUn3UWRIVUV89l2AnF-lwL2wLhJUlKLJl1x4"  # secrets.token_urlsafe(32)
    )
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

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        "mysql+pymysql://root:password@localhost/rag_platform?charset=utf8mb4&time_zone=Asia/Shanghai"
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
    REDIS_PASSWORD: Optional[str] = "REDIS_STRONG_PASSWORD"

    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # LLM 配置
    OPENAI_API_KEY: str = "sk-e4121ff513d74e89b9e1c9c1cdfd7085"
    OPENAI_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OPENAI_MODEL: str = "qwen-vl-max"  # 也可以使用 qwen-vl-max-latest
    ANTHROPIC_API_KEY: str = "sk-ant-your-anthropic-api-key"

    # DashScope 特定配置
    DASHSCOPE_MAX_RETRIES: int = 5
    DASHSCOPE_TIMEOUT: int = 120

    # 文件存储配置
    DATA_DIR: str = "data"
    TEMP_DIR: str = "data/temp"
    UPLOAD_DIR: str = "data/uploads"
    VECTOR_DB_DIR: str = "data/vector_db"

    # 文档处理配置
    USE_LLM_FOR_DOCUMENT_PROCESSING: bool = True
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

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
