# Git 操作记录

## 初始化仓库

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "初始化项目：完成后端基础架构和前端框架搭建"

# 将 master 分支重命名为 main
git branch -M main
```

## 分支管理

创建了以下功能分支：

1. **feature/frontend-development**：前端开发分支
   ```bash
   git checkout -b feature/frontend-development
   ```

2. **feature/backend-development**：后端开发分支
   ```bash
   git checkout -b feature/backend-development
   ```

3. **feature/env-setup**：环境配置分支
   ```bash
   git checkout -b feature/env-setup
   ```

## 提交记录

### main 分支

1. 初始提交
   ```bash
   git commit -m "初始化项目：完成后端基础架构和前端框架搭建"
   ```

2. 添加 .gitignore 文件
   ```bash
   git add .gitignore
   git commit -m "添加 .gitignore 文件"
   ```

### feature/env-setup 分支

1. 添加 Docker 开发环境配置
   ```bash
   git add docker-compose.yml backend/Dockerfile frontend/Dockerfile .env.example
   git commit -m "添加 Docker 开发环境配置"
   ```

### feature/backend-development 分支

1. 添加初始化脚本目录和超级用户配置
   ```bash
   git add backend/scripts/ backend/app/core/config.py
   git commit -m "添加初始化脚本目录和超级用户配置"
   ```

### feature/frontend-development 分支

1. 添加前端工具函数、自定义 Hook 和通用组件
   ```bash
   git add frontend/src/shared/utils/api.ts frontend/src/shared/hooks/useForm.ts frontend/src/shared/hooks/useApi.ts frontend/src/shared/components/Button.tsx
   git commit -m "添加前端工具函数、自定义 Hook 和通用组件"
   ```

## 分支合并计划

后续开发完成后，将按照以下顺序合并分支：

1. 将 `feature/env-setup` 合并到 `main`
   ```bash
   git checkout main
   git merge feature/env-setup
   ```

2. 将 `feature/backend-development` 合并到 `main`
   ```bash
   git checkout main
   git merge feature/backend-development
   ```

3. 将 `feature/frontend-development` 合并到 `main`
   ```bash
   git checkout main
   git merge feature/frontend-development
   ```

## 分支状态

当前各分支状态：

- **main**: 基础项目结构 + .gitignore 文件
- **feature/env-setup**: 添加了 Docker 开发环境配置
- **feature/backend-development**: 添加了初始化脚本目录和超级用户配置
- **feature/frontend-development**: 添加了前端工具函数、自定义 Hook 和通用组件
