# Backend

本目录用于存放账户业务子系统 Python 后端代码。

## 技术栈

- Python
- FastAPI
- SQLAlchemy
- MySQL / SQLite

开发初期默认使用 SQLite，便于本地快速启动；联调和最终部署时切换到 MySQL。

## 本地启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Windows 激活虚拟环境：

```bash
.venv\Scripts\activate
```

启动后访问：

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/account/health

## 当前已完成的基础能力

- 后端项目骨架
- 统一响应格式
- 公共枚举
- 数据库连接配置
- `Customer`、`Staff`、`Approver` 基础模型
- 客户/工作人员基础查询与创建接口
- `AccountApplication`、`ApprovalRecord` 开户申请与审批模型
- 开户申请提交、查询、审批通过、审批拒绝、审批记录查询接口

后续 B/C 在此结构下继续补充账户管理、账户关联与日志模块。
