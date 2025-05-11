# 智能体综合应用平台

智能体综合应用平台是一个基于大语言模型的综合性应用平台，集成了多种智能功能，包括智能客服、知识库管理、文档处理等模块。该平台旨在为企业提供一站式的 AI 解决方案，帮助企业提升效率，降低成本。

## 核心功能

1. **智能客服系统**：基于大语言模型的智能客服系统，支持多轮对话、上下文理解、流式响应等功能。
2. **知识库管理**：支持文档上传、处理、搜索和检索，为智能客服提供知识支持。
3. **文档处理**：支持多种格式文档的处理和转换，包括 PDF、Word、TXT 等。
4. **LLM 配置管理**：支持多种 LLM 提供商，用户可自定义配置。

## 技术架构

- **前端**：React + TypeScript + Vite
- **后端**：FastAPI + SQLAlchemy + Celery
- **数据库**：MySQL
- **存储**：MinIO
- **消息队列**：Redis + Celery
- **AI 引擎**：AutoGen + 多种 LLM 提供商

## 项目结构

项目采用以功能模块为中心的组织方式，将相关的业务逻辑、API 接口、数据模型、服务、任务等组织在对应功能模块的专属目录下。

```
rag-project/
├── backend/                  # 后端代码
│   ├── app/                  # 应用核心
│   │   ├── core/             # 核心配置
│   │   ├── modules/          # 功能模块
│   │   │   ├── auth/         # 认证模块
│   │   │   ├── chat/         # 智能客服模块
│   │   │   ├── knowledge/    # 知识库模块
│   │   │   ├── document/     # 文档处理模块
│   │   │   └── llm/          # LLM 配置模块
│   │   ├── db/               # 数据库
│   │   └── utils/            # 通用工具
│   ├── celery_app/           # Celery 配置
│   ├── tests/                # 测试
│   └── main.py               # 应用入口
│
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── modules/          # 功能模块
│   │   │   ├── auth/         # 认证模块
│   │   │   ├── chat/         # 智能客服模块
│   │   │   ├── knowledge/    # 知识库模块
│   │   │   ├── document/     # 文档处理模块
│   │   │   └── llm/          # LLM 配置模块
│   │   ├── shared/           # 共享资源
│   │   └── App.tsx           # 应用入口
```

## 开发环境设置

### 后端

1. 创建 Python 虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

3. 启动后端服务

```bash
uvicorn main:app --reload
```

### 前端

1. 安装依赖

```bash
cd frontend
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

## API 文档

启动后端服务后，可以通过以下 URL 访问 API 文档：

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 部署

### 使用 Docker Compose

1. 构建并启动服务

```bash
docker-compose up -d
```

2. 访问应用

前端: http://localhost:3000
后端 API: http://localhost:8000

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件
