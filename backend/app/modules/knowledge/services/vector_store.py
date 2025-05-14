#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量数据库服务
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from app.core.config import settings
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """向量数据库服务"""

    def __init__(self, persist_directory: Optional[str] = None):
        """
        初始化向量数据库服务

        Args:
            persist_directory: 持久化目录，如果为 None，则使用内存存储
        """
        self.persist_directory = persist_directory or os.path.join(
            settings.DATA_DIR, "chroma_db"
        )

        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)

        # 初始化 Chroma 客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # 初始化文本嵌入模型
        self.embedding_model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        logger.info(f"向量数据库服务初始化完成，持久化目录: {self.persist_directory}")

    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        return self.embedding_model.encode(text).tolist()

    def get_collection(
        self, collection_name: str, create_if_not_exists: bool = True
    ) -> Any:
        """
        获取集合

        Args:
            collection_name: 集合名称
            create_if_not_exists: 如果集合不存在，是否创建

        Returns:
            集合对象
        """
        try:
            return self.client.get_collection(name=collection_name)
        except ValueError:
            if create_if_not_exists:
                return self.client.create_collection(name=collection_name)
            raise

    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        添加文本到向量数据库

        Args:
            collection_name: 集合名称
            texts: 文本列表
            metadatas: 元数据列表
            ids: ID 列表

        Returns:
            添加的文档 ID 列表
        """
        if not texts:
            logger.warning(f"尝试向集合 {collection_name} 添加空文本列表")
            return []

        logger.info(f"开始向集合 {collection_name} 添加 {len(texts)} 个文档")

        try:
            # 获取集合
            collection = self.get_collection(collection_name)
            logger.info(f"成功获取集合: {collection_name}")

            # 如果没有提供 ID，则生成 UUID
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
                logger.info(f"生成了 {len(ids)} 个文档 ID")

            # 检查元数据
            if metadatas and len(metadatas) != len(texts):
                logger.error(
                    f"元数据数量 ({len(metadatas)}) 与文本数量 ({len(texts)}) 不匹配"
                )
                raise ValueError("元数据数量与文本数量不匹配")

            # 获取嵌入向量
            logger.info("开始生成文本嵌入向量")
            embeddings = []
            for i, text in enumerate(texts):
                try:
                    embedding = self.get_embedding(text)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"为文本 {i} 生成嵌入向量时出错: {str(e)}")
                    raise
            logger.info(f"成功生成 {len(embeddings)} 个嵌入向量")

            # 添加到集合
            logger.info("开始添加文档到向量数据库")
            collection.add(
                documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids
            )

            logger.info(f"成功向集合 {collection_name} 添加了 {len(texts)} 个文档")

            return ids
        except Exception as e:
            logger.error(
                f"向集合 {collection_name} 添加文档时出错: {str(e)}", exc_info=True
            )
            raise

    def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        搜索向量数据库

        Args:
            collection_name: 集合名称
            query: 查询文本
            limit: 返回结果数量
            filter: 过滤条件

        Returns:
            搜索结果列表，每个结果包含文档内容、元数据和相似度分数
        """
        from dataclasses import dataclass

        @dataclass
        class SearchResult:
            page_content: str
            metadata: Dict[str, Any]
            score: float

        try:
            # 获取集合
            collection = self.get_collection(
                collection_name, create_if_not_exists=False
            )

            # 获取查询文本的嵌入向量
            query_embedding = self.get_embedding(query)

            # 搜索
            results = collection.query(
                query_embeddings=[query_embedding], n_results=limit, where=filter
            )

            # 解析结果
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            # 计算相似度分数 (1 - 距离)
            scores = [1 - distance for distance in distances]

            logger.info(
                f"在集合 {collection_name} 中搜索 '{query}' 找到 {len(documents)} 个结果"
            )

            # 构建结果列表
            search_results = []
            for i in range(len(documents)):
                search_results.append(
                    SearchResult(
                        page_content=documents[i],
                        metadata=metadatas[i] if i < len(metadatas) else {},
                        score=scores[i] if i < len(scores) else 0.0,
                    )
                )

            return search_results
        except ValueError as e:
            logger.error(f"搜索集合 {collection_name} 时出错: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"搜索集合 {collection_name} 时出错: {str(e)}")
            return []

    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合

        Args:
            collection_name: 集合名称

        Returns:
            是否成功删除
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"删除集合 {collection_name}")
            return True
        except ValueError as e:
            logger.error(f"删除集合 {collection_name} 时出错: {str(e)}")
            return False

    def delete_by_metadata(
        self,
        collection_name: str,
        metadata_key: str,
        metadata_value: Any,
    ) -> bool:
        """
        按元数据删除文档

        Args:
            collection_name: 集合名称
            metadata_key: 元数据键
            metadata_value: 元数据值

        Returns:
            是否成功删除
        """
        try:
            # 获取集合
            collection = self.get_collection(
                collection_name, create_if_not_exists=False
            )

            # 构建过滤条件
            where_filter = {metadata_key: metadata_value}

            # 查询匹配的文档
            results = collection.query(
                query_embeddings=None,
                where=where_filter,
                include=["documents", "metadatas", "embeddings", "distances", "ids"],
            )

            # 获取文档ID
            ids = results.get("ids", [[]])[0]

            if not ids:
                logger.warning(
                    f"在集合 {collection_name} 中没有找到匹配条件 {metadata_key}={metadata_value} 的文档"
                )
                return False

            # 删除文档
            collection.delete(ids=ids)

            logger.info(
                f"从集合 {collection_name} 中删除了 {len(ids)} 个匹配条件 {metadata_key}={metadata_value} 的文档"
            )

            return True
        except Exception as e:
            logger.error(
                f"从集合 {collection_name} 中删除匹配条件 {metadata_key}={metadata_value} 的文档时出错: {str(e)}"
            )
            return False

    def get_knowledge_base_collection_name(self, knowledge_base_id: int) -> str:
        """
        获取知识库集合名称

        Args:
            knowledge_base_id: 知识库 ID

        Returns:
            集合名称
        """
        return f"kb_{knowledge_base_id}"
