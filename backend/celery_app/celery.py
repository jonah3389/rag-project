#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery 配置
"""
from celery import Celery

from app.core.config import settings

# 创建 Celery 实例
celery_app = Celery(
    "rag_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.modules.document.tasks.document_processing",
        "app.modules.knowledge.tasks.indexing",
    ],
)

# 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# 自动发现任务
celery_app.autodiscover_tasks()
