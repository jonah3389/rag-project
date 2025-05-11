#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinIO 服务
"""
import io
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()


class MinioService:
    """MinIO 服务类"""
    
    def __init__(self):
        """初始化 MinIO 客户端"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建存储桶: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"MinIO 错误: {e}")
            raise
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: Optional[str] = None):
        """
        上传文件
        
        Args:
            file_path: 文件路径
            file_content: 文件内容
            content_type: 内容类型
        """
        try:
            file_stream = io.BytesIO(file_content)
            file_size = len(file_content)
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=file_stream,
                length=file_size,
                content_type=content_type,
            )
            logger.info(f"文件上传成功: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def download_file(self, file_path: str) -> bytes:
        """
        下载文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bytes: 文件内容
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
            )
            file_content = response.read()
            response.close()
            response.release_conn()
            logger.info(f"文件下载成功: {file_path}")
            return file_content
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            raise
    
    def delete_file(self, file_path: str):
        """
        删除文件
        
        Args:
            file_path: 文件路径
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
            )
            logger.info(f"文件删除成功: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"文件删除失败: {e}")
            raise
    
    def get_file_url(self, file_path: str, expires: int = 3600) -> str:
        """
        获取文件 URL
        
        Args:
            file_path: 文件路径
            expires: 过期时间（秒）
            
        Returns:
            str: 文件 URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                expires=expires,
            )
            return url
        except S3Error as e:
            logger.error(f"获取文件 URL 失败: {e}")
            raise
