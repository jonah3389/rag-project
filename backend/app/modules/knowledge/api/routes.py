#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库相关路由
"""

import logging

from app.modules.auth.api.deps import get_current_active_user
from app.modules.auth.models.user import User
from app.modules.knowledge.tasks.document_processing import process_document
from fastapi import APIRouter, Depends

router = APIRouter()

logger = logging.getLogger(__name__)


def process_document_task(task_id: int):
    """
    处理文档任务

    使用Celery执行文档处理，不会阻塞主应用程序

    Args:
        task_id: 任务 ID
    """
    logger.info(f"提交文档处理任务到Celery: {task_id}")

    # 使用Celery提交任务
    result = process_document.delay(task_id)

    # 不等待任务完成，立即返回
    logger.info(f"文档处理任务已提交到Celery: {task_id}, 任务ID: {result.id}")

    return result


@router.get("/test")
def test_route():
    """
    测试路由
    """
    logger.info("测试路由被调用")
    return {"message": "API 正常工作"}


@router.get("/test-auth")
def test_auth_route(current_user: User = Depends(get_current_active_user)):
    """
    测试认证路由
    """
    logger.info(f"认证测试路由被调用，用户 ID: {current_user.id}")
    return {
        "message": "认证成功",
        "user_id": current_user.id,
        "username": current_user.username,
    }
