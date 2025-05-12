#!/bin/bash

# 从 .env.example 文件中读取环境变量
if [ -f .env ]; then
  source .env
  echo "从 .env 文件中读取环境变量"
else
  source .env.example
  echo "从 .env.example 文件中读取环境变量"
fi

# 设置默认值
REDIS_PASSWORD=${REDIS_PASSWORD:-REDIS_STRONG_PASSWORD}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME:-rag-platform}

# 导出环境变量，供 docker-compose 使用
export REDIS_PASSWORD
export MINIO_ACCESS_KEY
export MINIO_SECRET_KEY
export MINIO_BUCKET_NAME

# 启动依赖服务
echo "正在启动依赖服务（MySQL、Redis、MinIO）..."
docker-compose -f docker-compose-deps.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose-deps.yml ps

# 创建 MinIO 存储桶
echo "创建 MinIO 存储桶..."
docker run --rm --network host minio/mc config host add myminio http://localhost:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
docker run --rm --network host minio/mc mb --ignore-existing myminio/${MINIO_BUCKET_NAME}

echo "依赖服务已启动，可以开始开发了！"
echo "MySQL: localhost:3306 (用户名: root, 密码: password, 数据库: rag_platform)"
echo "Redis: localhost:6379 (密码: ${REDIS_PASSWORD})"
echo "MinIO: localhost:9000 (API), localhost:9001 (控制台) (用户名: ${MINIO_ACCESS_KEY}, 密码: ${MINIO_SECRET_KEY})"
