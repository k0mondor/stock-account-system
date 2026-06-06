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

### 联调 MySQL 配置（如需使用 MySQL）

修改 `.env` 文件中的 `DATABASE_URL`：

```env
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/stock_account_db?charset=utf8mb4
AUTH_TOKEN_SECRET=replace-with-a-long-random-secret
SERVICE_TOKEN=replace-with-a-shared-service-token
```

确保数据库已创建：

```sql
CREATE DATABASE IF NOT EXISTS stock_account_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Windows 激活虚拟环境：

```bash
.venv\Scripts\activate
```

启动后访问：

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/account/health

## 当前已完成的能力

- 后端项目骨架
- 统一响应格式
- 公共枚举
- 数据库连接配置
- `Customer`、`Staff`、`Approver` 基础模型
- 客户/工作人员基础查询与创建接口
- `AccountApplication`、`ApprovalRecord` 开户申请与审批模型
- 开户申请提交、查询、审批通过、审批拒绝、审批记录查询接口
- 审批通过后事务性创建证券账户、资金账户和一对一有效绑定
- 资金账户查询、存款、取款和注销
- 证券账户查询和注销
- 账户关联查询、业务校验、创建和解除
- 账户关联历史、账户状态变更历史查询
- 当前有效绑定的数据库级一对一唯一约束
- 账户状态校验与带请求追踪 ID 的操作日志
- 交易客户端登录及交易密码/取款密码修改
- 带签名和过期时间的投资者访问令牌
- 客户端账户归属校验及内部服务令牌鉴权
- 交易资金冻结、释放、结算与资金流水查询
- 证券持仓查询、冻结、释放与结算
- 证券账户/资金账户挂失补办、冻结解冻与状态变更留痕

证券账户和资金账户不提供相互独立的自由开户接口。开户申请审批通过时，
系统连续创建两个账户并建立一对一绑定。

## 新增业务接口

- `POST /api/v1/account/fund-accounts/{id}/deposits`
- `POST /api/v1/account/fund-accounts/{id}/withdrawals`
- `DELETE /api/v1/account/fund-accounts/{id}`
- `GET /api/v1/account/security-accounts`
- `GET /api/v1/account/security-accounts/{id}`
- `DELETE /api/v1/account/security-accounts/{id}`
- `GET /api/v1/account/associations/history`
- `GET /api/v1/account/status/history`
- `POST /api/v1/account/fund-accounts/{id}/password/reset`

审批接口
`POST /api/v1/account/applications/{application_id}/approve`
除审批人和审批意见外，还需要提交：

```json
{
  "approver_id": "APR000001",
  "approval_opinion": "同意",
  "bank_card_no": "6222021234567890123",
  "trade_password": "123456",
  "withdraw_password": "123456"
}
```

`database/test_data.sql` 中测试资金账户的交易密码和取款密码均为
`123456`。

交易客户端通过 `/auth/password` 凭原密码修改密码；工作人员代理重置
通过资金账户内部业务接口完成，并校验工作人员权限和客户证件号码。

除登录和健康检查外，HTTP 接口必须携带
`Authorization: Bearer <token>`。交易客户端使用登录返回的投资者令牌；
柜台、审批、交易和管理等内部调用使用 `.env` 中配置的 `SERVICE_TOKEN`。
资金或持仓冻结、释放、结算会在服务端再次校验一对一有效绑定及双方账户
状态，不能只依赖调用方预先调用关联校验接口。

挂失、补办和销户请求必须提交 `customer_id_number`，后端会将其与账户
所属客户档案核对。账户关联历史响应包含 `disassociated_at`，柜台资金
流水包含 `operator_staff_id`。

启动时会自动为已有开发库补充解除时间、流水操作员字段和当前有效绑定
唯一索引。旧 SQLite 表无法原地补充外键；需要完整外键结构时，应备份
数据后重新创建开发库。
