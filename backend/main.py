#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体综合应用平台 - 后端主入口
"""

import uvicorn
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middlewares
from app.db.base_class import Base
from app.db.session import engine

# 导入各模块的路由
from app.modules.auth.api.routes import router as auth_router
from app.modules.chat.api.routes import router as chat_router
from app.modules.knowledge.api.routes import router as knowledge_router
from app.modules.llm.api.routes import router as llm_router

# 设置日志
logger = setup_logging()


# 尝试创建数据库表
try:
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建成功")
except OperationalError as e:
    logger.error(f"无法连接到数据库: {e}")
    logger.error("MySQL 是应用的核心依赖，无法继续运行")
    import sys

    sys.exit(1)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# 设置中间件
setup_middlewares(app)

# 注册路由
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["智能客服"])
app.include_router(
    knowledge_router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["知识库"]
)
# 文档处理功能已集成到知识库模块中
app.include_router(llm_router, prefix=f"{settings.API_V1_STR}/llm", tags=["LLM配置"])


@app.get("/")
async def root():
    return {"message": "欢迎使用智能体综合应用平台 API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
