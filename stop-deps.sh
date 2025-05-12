#!/bin/bash

# 停止依赖服务
echo "正在停止依赖服务（MySQL、Redis、MinIO）..."
docker-compose -f docker-compose-deps.yml down

echo "依赖服务已停止。"
