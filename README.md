# 股票交易系统 - 账户业务子系统（ACCOUNT）

## 项目概述

本项目是股票交易系统中的 **账户业务子系统（ACCOUNT）** 模块，负责：
- 投资者登录认证
- 资金账户管理（冻结、释放、结算）
- 证券持仓管理（查询、冻结、释放、结算）
- 账户关联管理

## 技术栈

- **Python**: 3.11+
- **Web框架**: FastAPI
- **ASGI服务**: Uvicorn
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy + PyMySQL
- **数据校验**: Pydantic
- **数据库迁移**: Alembic

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接配置
│   ├── models/                 # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── user.py            # 用户模型
│   │   ├── fund_account.py    # 资金账户模型
│   │   ├── security_account.py # 证券账户模型
│   │   └── association.py     # 账户关联模型
│   ├── schemas/                # Pydantic数据模型
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证相关schema
│   │   ├── fund.py            # 资金账户schema
│   │   ├── security.py        # 证券账户schema
│   │   └── association.py     # 账户关联schema
│   ├── crud/                   # 数据访问层
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── fund_account.py
│   │   ├── security_account.py
│   │   └── association.py
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── fund.py        # 资金账户接口
│   │   │   ├── security.py    # 证券账户接口
│   │   │   └── association.py # 账户关联接口
│   │   └── routers.py         # 路由汇总
│   ├── services/              # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── fund_service.py
│   │   ├── security_service.py
│   │   └── association_service.py
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── jwt_utils.py       # JWT令牌工具
│       ├── exceptions.py      # 自定义异常
│       └── constants.py       # 常量定义
├── alembic/                   # 数据库迁移脚本
│   ├── versions/
│   └── env.py
├── requirements.txt
├── .env.example
└── main.py                    # 项目启动脚本

```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等
```

### 4. 数据库初始化

```bash
alembic upgrade head
```

### 5. 启动应用

```bash
python main.py
```

应用将在 `http://localhost:8000` 启动，API文档访问 `http://localhost:8000/docs`

## API文档

API遵循统一的响应格式：

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "code": 0,
  "message": "success",
  "timestamp": "2026-05-25T10:30:00+08:00"
}
```

### 失败响应
```json
{
  "success": false,
  "data": null,
  "code": 1001,
  "message": "error message",
  "timestamp": "2026-05-25T10:30:00+08:00"
}
```

## 接口列表

### 认证接口 (`/api/v1/account/auth`)
- `POST /login` - 投资者登录
- `POST /password` - 修改账户密码

### 资金账户接口 (`/api/v1/account/fund-accounts`)
- `GET /{fund_account_id}` - 查询资金账户
- `POST /{fund_account_id}/freeze` - 冻结资金
- `POST /{fund_account_id}/release` - 释放资金
- `POST /{fund_account_id}/settlements` - 资金结算

### 证券持仓接口 (`/api/v1/account/security-accounts`)
- `GET /{security_account_id}/positions` - 查询证券持仓
- `POST /{security_account_id}/positions/freeze` - 冻结持仓
- `POST /{security_account_id}/positions/release` - 释放持仓
- `POST /{security_account_id}/positions/settlements` - 证券结算

### 账户关联接口 (`/api/v1/account/associations`)
- `GET /` - 查询账户关联
- `GET /check` - 账户关联业务校验

## 环境变量

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/account_db

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 应用配置
DEBUG=False
APP_TITLE=股票交易系统-账户业务子系统
```

## 开发指南

### 添加新的API端点

1. 在 `app/schemas/` 中定义请求和响应schema
2. 在 `app/models/` 中定义数据库模型（如需要）
3. 在 `app/crud/` 中实现数据访问逻辑
4. 在 `app/services/` 中实现业务逻辑
5. 在 `app/api/v1/` 中定义API路由

### 数据库迁移

```bash
# 创建新的迁移脚本
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 测试

```bash
pytest tests/
```

## 部署

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 贡献指南

1. 从 `main` 分支创建个人feature分支
2. 在分支上进行开发和测试
3. 提交PR进行代码审查
4. 审查通过后合并到 `main` 分支

## 许可证

MIT
