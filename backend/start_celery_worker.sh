#!/bin/bash
# 启动Celery Worker

# 切换到项目目录
cd "$(dirname "$0")"

# 激活虚拟环境（如果有的话）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 启动Celery Worker
celery -A celery_app.celery worker --loglevel=info -P solo
