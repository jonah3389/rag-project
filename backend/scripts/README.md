# 脚本说明

本目录包含项目的各种初始化和管理脚本。

## 脚本列表

### init.py

主初始化脚本，用于调用其他初始化脚本。

**用法**：

```bash
# 运行所有初始化脚本
python init.py

# 跳过环境变量设置
python init.py --skip-env

# 跳过数据库初始化
python init.py --skip-db

# 跳过环境变量设置和数据库初始化
python init.py --skip-env --skip-db
```

### setup_env.py

环境变量设置脚本，用于创建 .env 文件。

**用法**：

```bash
python setup_env.py
```

### init_db.py

数据库初始化脚本，用于创建数据库表和初始数据。

**用法**：

```bash
python init_db.py
```

## 注意事项

1. 所有脚本都应该在项目根目录下运行。
2. 初始化脚本会创建超级用户和默认 LLM 配置。
3. 环境变量设置脚本会生成随机密钥。
