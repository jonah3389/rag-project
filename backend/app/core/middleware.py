#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件配置
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """
    设置 CORS 中间件
    
    Args:
        app: FastAPI 应用实例
    """
    # 允许的源
    origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    
    # 如果没有配置源，则允许所有源
    if not origins:
        origins = ["*"]
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,  # 预检请求缓存时间（秒）
    )


class CORSPreflightMiddleware(BaseHTTPMiddleware):
    """
    处理 CORS 预检请求的中间件
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        # 如果是 OPTIONS 请求，直接返回 200 响应
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            
            # 添加 CORS 头
            origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
            if not origins:
                origins = ["*"]
            
            origin = request.headers.get("origin", "")
            if origin in origins or "*" in origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                response.headers["Access-Control-Allow-Origin"] = origins[0] if origins else "*"
            
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"  # 预检请求缓存时间（秒）
            
            return response
        
        # 其他请求正常处理
        return await call_next(request)


def setup_middlewares(app: FastAPI) -> None:
    """
    设置所有中间件
    
    Args:
        app: FastAPI 应用实例
    """
    # 设置 CORS 中间件
    setup_cors_middleware(app)
    
    # 添加 CORS 预检请求中间件
    app.add_middleware(CORSPreflightMiddleware)
