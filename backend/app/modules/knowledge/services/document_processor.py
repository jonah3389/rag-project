#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理服务
"""

import logging
import os
from typing import Dict, List, Tuple

from app.core.config import settings
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, use_llm: bool = False):
        """
        初始化文档处理器

        Args:
            use_llm: 是否使用 LLM 增强处理
        """
        self.use_llm = use_llm
        self.config = {
            "output_format": "markdown",
            "output_dir": settings.TEMP_DIR,
            "use_llm": use_llm,
        }

        # 如果使用 LLM，添加 LLM 配置
        if use_llm:
            self.config.update(
                {
                    "llm_service": "marker.services.openai.OpenAIService",
                    "openai_base_url": settings.OPENAI_API_BASE,
                    "openai_model": settings.OPENAI_MODEL,
                    "openai_api_key": settings.OPENAI_API_KEY,
                    "max_retries": settings.DASHSCOPE_MAX_RETRIES,  # 使用配置中的重试次数
                    "timeout": settings.DASHSCOPE_TIMEOUT,  # 使用配置中的超时时间
                }
            )

        self.config_parser = ConfigParser(self.config)

        # 创建 PDF 转换器
        self.pdf_converter = PdfConverter(
            config=self.config,
            artifact_dict=create_model_dict(),
            processor_list=self.config_parser.get_processors(),
            renderer=self.config_parser.get_renderer(),
            llm_service="marker.services.openai.OpenAIService" if use_llm else None,
        )

    def process_pdf(
        self, file_path: str, timeout: int = 240
    ) -> Tuple[str, Dict[str, str]]:
        """
        处理 PDF 文件

        Args:
            file_path: PDF 文件路径
            timeout: 处理超时时间（秒）

        Returns:
            提取的文本内容和图片信息
        """
        import multiprocessing
        import threading

        # 使用线程级别的超时处理，更安全且可以终止
        class TimeoutError(Exception):
            pass

        def process_pdf_with_timeout(file_path, result_dict):
            try:
                # 处理 PDF
                logger.info("开始调用 PDF 转换器")
                rendered = self.pdf_converter(file_path)
                logger.info("PDF 转换完成，开始提取文本和图片")

                # 提取文本和图片
                text, _, images = text_from_rendered(rendered)

                logger.info(
                    f"PDF 处理完成: {file_path}, 文本长度: {len(text)}, 图片数量: {len(images)}"
                )

                # 将结果存储在共享字典中
                result_dict["text"] = text
                result_dict["images"] = images
                result_dict["success"] = True
            except Exception as e:
                logger.error(f"处理 PDF 时出错: {str(e)}", exc_info=True)
                result_dict["error"] = str(e)
                result_dict["success"] = False

        try:
            logger.info(f"开始处理 PDF 文件: {file_path}")

            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return "", {}

            # 获取文件大小
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            logger.info(f"PDF 文件大小: {file_size_mb:.2f} MB")

            # 根据文件大小调整超时时间，但不要过度增加
            if file_size_mb > 50:
                adjusted_timeout = min(timeout * 2, 600)  # 最多10分钟
                logger.info(f"PDF文件非常大，调整超时时间为 {adjusted_timeout} 秒")
            elif file_size_mb > 20:
                adjusted_timeout = min(timeout * 1.5, 480)  # 最多8分钟
                logger.info(f"PDF文件较大，调整超时时间为 {adjusted_timeout} 秒")
            elif file_size_mb > 10:
                adjusted_timeout = min(timeout * 1.2, 360)  # 最多6分钟
                logger.info(f"PDF文件中等大小，调整超时时间为 {adjusted_timeout} 秒")
            else:
                adjusted_timeout = timeout

            # 使用Manager创建共享字典
            manager = multiprocessing.Manager()
            result_dict = manager.dict()
            result_dict["success"] = False

            # 创建并启动处理线程
            process_thread = threading.Thread(
                target=process_pdf_with_timeout, args=(file_path, result_dict)
            )
            process_thread.daemon = True  # 设置为守护线程，主线程结束时会被强制终止

            logger.info(f"启动PDF处理线程，超时时间: {adjusted_timeout}秒")
            process_thread.start()

            # 等待处理完成或超时
            process_thread.join(adjusted_timeout)

            # 检查是否超时
            if process_thread.is_alive():
                logger.error(f"PDF处理超时（{adjusted_timeout}秒），强制终止处理")
                # 线程仍在运行，表示超时
                return (
                    f"文件处理超时（{adjusted_timeout}秒），可能是因为文件过大或格式复杂。请尝试分割文件或转换为更简单的格式。",
                    {},
                )

            # 检查处理结果
            if result_dict.get("success", False):
                return result_dict.get("text", ""), result_dict.get("images", {})
            else:
                error_msg = result_dict.get("error", "未知错误")
                logger.error(f"PDF处理失败: {error_msg}")
                return f"处理文件时出错: {error_msg}", {}

        except Exception as e:
            logger.error(f"处理 PDF 文件时出错: {str(e)}", exc_info=True)
            return f"处理文件时出错: {str(e)}", {}

    def chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """
        将文本分块

        Args:
            text: 要分块的文本
            chunk_size: 每个块的最大大小
            overlap: 块之间的重叠大小

        Returns:
            分块后的文本列表
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # 如果不是文本末尾，尝试在句子边界切分
            if end < len(text):
                # 寻找最近的句子结束符
                sentence_end = max(
                    text.rfind(". ", start, end),
                    text.rfind("? ", start, end),
                    text.rfind("! ", start, end),
                    text.rfind("\n", start, end),
                )

                if sentence_end > start:
                    end = sentence_end + 1

            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def process_file(
        self, file_path: str, file_type: str, timeout: int = 300
    ) -> Tuple[str, Dict[str, str], List[str]]:
        """
        处理文件

        Args:
            file_path: 文件路径
            file_type: 文件类型
            timeout: 处理超时时间（秒）

        Returns:
            提取的文本内容、图片信息和分块后的文本
        """
        logger.info(f"开始处理文件: {file_path}, 类型: {file_type}")

        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 获取文件大小
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        logger.info(f"文件大小: {file_size_mb:.2f} MB")

        text = ""
        images = {}

        try:
            # 根据文件类型选择处理方法
            file_type = file_type.lower()
            logger.info(f"使用处理方法: {file_type}")

            if file_type == "pdf":
                logger.info(f"处理 PDF 文件: {file_path}")

                # 简化处理逻辑，只尝试一次，依赖process_pdf内部的超时机制
                logger.info(f"开始处理PDF文件: {file_path}, 超时时间: {timeout}秒")
                text, images = self.process_pdf(file_path, timeout=timeout)

                # 检查处理结果
                if text.startswith("文件处理超时") or text.startswith("处理文件时出错"):
                    logger.error(f"PDF处理失败: {text}")
                    # 不再重试，直接返回错误信息
                else:
                    logger.info(f"PDF处理成功，文本长度: {len(text)}")

            elif file_type in ["txt", "md"]:
                logger.info(f"处理文本文件: {file_path}")
                # 简单读取文本文件
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            elif file_type in ["doc", "docx"]:
                logger.info(f"处理 Word 文件: {file_path}")
                # 暂不支持 Word 文档
                logger.error("暂不支持 Word 文档处理")
                raise NotImplementedError("暂不支持 Word 文档处理")
            else:
                logger.error(f"不支持的文件类型: {file_type}")
                raise ValueError(f"不支持的文件类型: {file_type}")

            logger.info(f"文件处理完成，提取文本长度: {len(text)}")

            # 分块
            # if text:
            #     logger.info("开始文本分块")
            #     chunks = self.chunk_text(text)
            #     logger.info(f"分块完成，共 {len(chunks)} 个块")
            # else:
            #     logger.warning("没有提取到文本，跳过分块")
            #     chunks = []
            chunks = []

            return text, images, chunks

        except Exception as e:
            if "超时" in str(e):
                logger.error(f"处理文件超时: {str(e)}")
                error_text = "文件处理超时，可能是因为文件过大或格式复杂。请尝试分割文件或转换为更简单的格式。"
                return error_text, {}, [error_text]
            else:
                logger.error(f"处理文件时出错: {str(e)}", exc_info=True)
                error_text = f"处理文件时出错: {str(e)}"
                return error_text, {}, [error_text]
