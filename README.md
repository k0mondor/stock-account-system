# stock-account-system

证券公司账户业务子系统，包含前端柜台/审批界面、FastAPI 后端与数据库脚本。当前仓库已按“账户对模型”重构，系统中的活跃业务主体不再是单个证券账户或资金账户，而是“证券账户 + 资金账户 + 当前有效绑定”的联合账户对。默认开发环境使用 SQLite，支持切换到 MySQL。

## 账户对模型

本系统当前以“账户对”作为核心业务对象，所有关键规则围绕证券账户、资金账户与当前有效绑定三者的一致性展开：

- 活跃业务主体始终是账户对，不是单独证券账户，也不是单独资金账户
- 开户只允许联合开户，审批通过后必须一次性创建证券账户、资金账户和唯一有效绑定
- 销户只允许联合销户，必须一次性关闭证券账户、资金账户并结束当前有效绑定
- 关联关系只允许查询、校验和历史追踪，不允许人工绑定、不允许人工解绑
- 禁止出现孤儿账户，即不存在“状态有效但没有有效绑定”的证券账户或资金账户
- 挂失/补办遵循双向对称联动：一侧挂失会影响另一侧，一侧补办会恢复对应联动状态
- 普通冻结/解冻不自动同步另一侧状态，但会影响联合销户、密码重置、交易等联合业务校验

## 核心业务

本模块当前覆盖以下核心业务：

- 联合开户：提交开户申请、审批通过、审批驳回
- 审批通过后在一个事务中连续创建证券账户、资金账户与唯一有效绑定
- 联合销户：校验账户对前置条件后，在一个事务中同时关闭证券账户、资金账户并结束当前有效绑定
- 证券账户查询、挂失、补办、密码重置、持仓查询与持仓变动
- 资金账户查询、存款、取款、挂失、补办、密码修改/重置、流水查询
- 账户关联查询、关联校验、关联历史追踪
- 账户状态校验、冻结/解冻、状态变更历史、操作日志审计

当前前端默认定位是内部柜台与审批工作台，不提供管理端登录能力。`/login` 页面仅作为角色入口页；后端 `auth` 路由提供的是交易客户端资金账户登录与密码修改接口，不是后台员工登录。

## 仓库目录

```text
backend/                 FastAPI 后端
database/                schema、测试数据、数据库规范
frontend/                Vue 3 + Vite 前端
接口V2_修正版(3).md        课程/小组阶段性接口说明参考
```

关键目录说明：

- `backend/app/main.py`: 后端应用入口与路由挂载
- `backend/app/routers`: 对外 HTTP API，按开户申请、资金账户、证券账户、联合销户、关联、状态等拆分
- `backend/app/services`: 核心业务规则、事务处理、账户对校验、挂失联动、日志写入
- `backend/app/schemas`: 请求/响应模型定义
- `backend/app/models`: 账户、绑定、申请、日志、持仓等数据模型
- `backend/tests`: 后端业务测试，覆盖联合开户、联合销户、挂失联动、状态限制、密码与旁路封口
- `frontend/src/views/staff`: 柜台页面，当前只保留联合开户、联合销户、查询、状态办理、挂失补办、密码重置等入口
- `frontend/src/views/approver`: 审批页面
- `frontend/src/utils/request`: 页面请求门面、字段兼容、会话辅助
- `frontend/src/api`: Axios 客户端与基础 endpoint 封装
- `frontend/src/services`: 前端轻量映射与复用逻辑

## 技术栈

- 前端: Vue 3、Vite、Vue Router 4、Element Plus、Axios
- 后端: Python、FastAPI、SQLAlchemy、Pydantic
- 数据库: SQLite（本地默认）、MySQL（联调/部署可切换）

## 快速启动

### 1. 启动后端

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

后端启动后可访问：

- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/api/v1/account/health](http://localhost:8000/api/v1/account/health)

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

默认开发地址：

- 前端: [http://localhost:5173](http://localhost:5173)
- 柜台端入口: `/staff`
- 审批端入口: `/approver`

### 3. 前端构建

```powershell
cd frontend
npm run build
```

## 环境变量

### 后端 `backend/.env`

参考 `backend/.env.example`：

```env
APP_NAME=stock-account-backend
APP_ENV=development
DATABASE_URL=sqlite:///./account_dev.sqlite3
CORS_ORIGINS=http://localhost:5173
AUTH_TOKEN_SECRET=replace-with-a-long-random-secret
SERVICE_TOKEN=replace-with-a-shared-service-token
ACCESS_TOKEN_EXPIRE_HOURS=8
```

说明：

- `DATABASE_URL`: 本地默认 SQLite；联调或部署可切换到 MySQL
- `SERVICE_TOKEN`: 内部模块、柜台端、审批端联调时使用的共享服务令牌
- `AUTH_TOKEN_SECRET`: 交易客户端投资者访问令牌的签名密钥

### 前端 `frontend/.env.*`

参考 `frontend/.env.example`，当前开发环境建议使用真实后端：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ACCOUNT_PREFIX=/api/v1/account
VITE_DEV_BEARER_TOKEN=replace-with-a-shared-service-token
```

说明：

- `VITE_API_BASE_URL`: 后端服务地址
- `VITE_ACCOUNT_PREFIX`: 账户域 API 前缀
- `VITE_DEV_BEARER_TOKEN`: 本地开发时自动注入 `Authorization: Bearer <token>`

建议：本地联调统一直连真实后端，不再保留 mock 数据源切换。

## 联调架构

前端当前仍保留兼容层，调用链路如下：

```text
页面 -> frontend/src/utils/request.js
     -> frontend/src/api/httpClient.js
     -> frontend/src/api/accountApi.js / 直接 HTTP 调用
     -> frontend/src/services/accountService.js（通用映射）
     -> backend/app/routers/*
     -> backend/app/services/*
```

分层原则：

- `request.js`: 兼容现有页面调用、聚合字段，对页面暴露稳定的请求门面
- `accountApi.js`: 只放通用 endpoint 封装，不放业务语义
- `accountService.js`: 放可复用的映射与轻业务转换
- 页面层: 只做表单校验、视图状态、提示文案

## 已打通的前后端能力

当前前后端已真实打通的主要业务能力如下：

- 联合开户申请提交
- 审批列表查询、审批通过、审批驳回
- 审批通过后联合创建证券账户、资金账户并建立唯一有效绑定
- 联合销户页面与联合销户接口联调
- 证券账户查询、证券密码重置、证券挂失/补办、证券持仓查询
- 资金账户查询、资金存款、资金取款、资金密码修改、资金密码重置、资金流水查询
- 关联查询、关联校验、关联历史查询
- 普通冻结/解冻、账户状态校验、状态历史查询
- 资金挂失影响证券、证券挂失影响资金的双向联动
- 操作日志查询

说明：

- 柜台与审批页面当前通过服务令牌联调
- `/login` 仍是 Demo 角色入口，不是完整员工登录系统
- 后端已收紧单边销户、人工绑定/解绑、单边高风险操作等旁路，旧路由保留但会明确拒绝

## 业务约束

当前实现遵守以下核心业务约束：

- 活跃业务主体是账户对，不是单独证券账户或单独资金账户
- 开户只允许联合开户，不允许单独开证券账户或单独开资金账户
- 审批通过后必须在一个事务中连续完成证券账户创建、资金账户创建和有效绑定创建
- 销户只允许联合销户，不允许单独证券销户或单独资金销户
- 联合销户前必须同时满足：证券账户和资金账户存在且属于同一投资者；两者之间存在且仅存在一条 `ACTIVE` 绑定；两个账户状态都为 `NORMAL`；资金账户 `available_balance = 0`、`frozen_amount = 0`、`total_amount = 0`；证券账户无持仓、无冻结持仓
- 关联关系只允许查询、校验、历史追踪，不允许人工绑定、不允许人工解绑
- 绑定关系只能在联合开户时建立，只能在联合销户时结束
- 不允许出现“状态有效但没有有效绑定的证券账户”或“状态有效但没有有效绑定的资金账户”
- 普通冻结/解冻只影响当前账户，不自动同步另一账户状态
- 但任一侧被冻结后，交易类业务、联合销户、高风险操作会受限
- 资金账户挂失时，资金账户变 `LOST`，关联证券账户自动变 `FROZEN`
- 资金账户补办恢复时，资金账户恢复 `NORMAL`；若证券账户是因该资金挂失被冻结，则同步恢复 `NORMAL`
- 证券账户挂失时，证券账户变 `LOST`，关联资金账户自动变 `FROZEN`
- 证券账户补办恢复时，证券账户恢复 `NORMAL`；若资金账户是因该证券挂失被冻结，则同步恢复 `NORMAL`
- 挂失、补办、联合销户等高风险操作必须提交 `customer_id_number`，后端会做身份核验
- 服务端会在交易资金变动、持仓变动、密码操作等关键流程再次校验账户对状态，调用方不能只依赖前置页面校验

统一枚举参考：

- 账户状态: `NORMAL | FROZEN | LOST | CLOSED`
- 关联状态: `ACTIVE | UNLINKED`
- 资金密码类型: `TRADE | WITHDRAW`

## 测试数据与数据库

数据库相关说明见 `database/README.md`，本地基线测试数据位于 `database/test_data.sql`。

联调时建议保留一套稳定基线数据，便于多组复现：

- 客户: `CUST000001`
- 开户申请: `APP000001`
- 资金账户: `FUND000001`
- 证券账户: `SEC000001`
- 账户关联: `ASC000001`

如果需要完整重建：

- SQLite 开发库可直接删除后按后端启动逻辑重新初始化
- MySQL 可使用 `database/schema.sql` 建表，再按需要导入测试数据

## 主要接口分组

以下按当前业务主线列出主要 API 分组，完整字段与全部路由定义以 `/docs` 为准。

### 联合开户与审批

- `POST /api/v1/account/applications`
- `GET /api/v1/account/applications`
- `POST /api/v1/account/applications/{application_id}/approve`
- `POST /api/v1/account/applications/{application_id}/reject`

### 联合销户

- `POST /api/v1/account/joint-accounts/close`

### 账户对查询与校验

- `GET /api/v1/account/associations`
- `GET /api/v1/account/associations/check`
- `GET /api/v1/account/associations/history`
- `POST /api/v1/account/status/check`
- `GET /api/v1/account/status/history`

### 证券与资金办理

- `GET /api/v1/account/fund-accounts/{fund_account_id}`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/deposits`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/withdrawals`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/password/reset`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/lost`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/reissue`
- `GET /api/v1/account/security-accounts/{security_account_id}`
- `POST /api/v1/account/security-accounts/{security_account_id}/password/reset`
- `GET /api/v1/account/security-accounts/{security_account_id}/positions`
- `POST /api/v1/account/security-accounts/{security_account_id}/lost`
- `POST /api/v1/account/security-accounts/{security_account_id}/reissue`

### 支撑能力

- `GET /api/v1/account/customers`
- `GET /api/v1/account/staff`
- `GET /api/v1/account/operation-logs`
- `POST /api/v1/account/auth/login`
- `POST /api/v1/account/auth/password`

说明：

- `DELETE /api/v1/account/fund-accounts/{fund_account_id}` 和 `DELETE /api/v1/account/security-accounts/{security_account_id}` 仍保留，但当前实现会拒绝单边销户
- `POST /api/v1/account/associations` 和 `DELETE /api/v1/account/associations` 仍保留，但当前实现会拒绝人工绑定和人工解绑
- 资金冻结/解冻、持仓冻结/解冻、结算等辅助接口仍存在，README 不再逐条展开，具体以 Swagger 为准
