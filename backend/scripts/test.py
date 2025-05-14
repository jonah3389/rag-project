#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/4/26 17:17
# @Author  : Groot
# @File    : test.py
# @Software: PyCharm

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# llm_service = OpenAIService({"openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "openai_model": "qwen-vl-max-latest", "openai_api_key": "sk-9d64fad24f9e402c81e99add13cfae97"})

config = {
    "output_format": "markdown",
    # "use_llm": True,
    # "llm_service": "marker.services.openai.OpenAIService",
}

config_parser = ConfigParser(config)
# ollama_config = {
#     "ollama_base_url": "http://localhost:11434",
#     "ollama_model": "llama3.2-vision",
#     "llm_service": "marker.services.ollama.OllamaService",
# }

converter = PdfConverter(
    config={
        "output_format": "markdown",
        "output_dir": "output",
        "use_llm": False,
        "llm_service": "marker.services.openai.OpenAIService",
        "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "openai_model": "qwen-vl-max-latest",
        "openai_api_key": "e4121ff513d74e89b9e1c9c1cdfd7085",  # "sk-9d64fad24f9e402c81e99add13cfae97",  # e4121ff513d74e89b9e1c9c1cdfd7085
    },
    # config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service="marker.services.openai.OpenAIService",
    # llm_service="marker.services.ollama.OllamaService",
)

rendered = converter(
    "/Users/groot/PycharmProjects/rag-in-action/90-文档-Data/复杂PDF/billionaires_page.pdf"
)

text, _, images = text_from_rendered(rendered)
for k, v in images.items():
    text.replace(f"![]({k})", "描述信息")
print(text)
print("-----------")
print(images)
