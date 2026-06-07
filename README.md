# stock-account-system

证券公司账户业务子系统，包含前端柜台/审批界面、FastAPI 后端、数据库脚本与跨模块联调说明。当前仓库以“本地可启动、前后端可联调、可供其他组接入”为目标，默认开发环境使用 SQLite，支持切换到 MySQL。

## 项目范围

本模块覆盖以下核心业务：

- 开户申请提交、审批通过、审批驳回
- 审批通过后连续生成证券账户、资金账户及一对一有效绑定
- 证券账户查询、挂失、补办、注销、持仓查询与持仓变动
- 资金账户查询、存款、取款、挂失、补办、销户、密码修改、流水查询
- 账户关联查询、校验、创建、解除、历史追踪
- 账户状态校验、状态变更历史、操作日志审计

当前前端默认定位是内部柜台与审批工作台，不提供管理端登录能力。`/login` 页面仅作为角色入口页；后端 `auth` 路由提供的是交易客户端资金账户登录与密码修改接口，不是后台员工登录。

## 仓库结构

```text
backend/                 FastAPI 后端
database/                schema、测试数据、数据库规范
frontend/                Vue 3 + Vite 前端
接口V2_修正版(3).md        课程/小组阶段性接口说明参考
```

关键目录说明：

- `backend/app/routers`: 对外 HTTP API
- `backend/app/services`: 业务规则与事务处理
- `backend/tests`: 后端业务测试
- `frontend/src/views/staff`: 柜台页面
- `frontend/src/views/approver`: 审批页面
- `frontend/src/utils/request.js`: 兼容旧页面调用方式的统一门面
- `frontend/src/api/httpClient.js`: Axios 客户端、鉴权头注入、统一响应解包
- `frontend/src/api/accountApi.js`: 基础 endpoint 封装
- `frontend/src/services/accountService.js`: 已抽出的通用账户关联/日志/资金账户映射能力

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

当前真实后端已联通的主要前端业务包括：

- 开户申请提交
- 审批列表查询、审批通过、审批驳回
- 证券账户列表查询、单户详情查询
- 资金账户查询、关联查询、资金流水查询
- 存款、取款、修改资金密码
- 证券账户挂失/补办、资金账户挂失/补办
- 证券账户销户、资金账户销户
- 操作日志查询

说明：

- 柜台与审批页面以服务令牌模式联调
- 投资者资金账户登录接口已在后端实现，但当前仓库前端未把它做成后台员工登录

## 业务约束

接入或联调时请特别注意以下规则：

- 不提供“自由开证券账户”或“自由开资金账户”接口；标准开户流程是“提交申请 -> 审批通过 -> 连续开户”
- 证券账户与资金账户当前有效绑定为一对一，数据库层有唯一约束
- 挂失补办恢复的是原账户状态，不生成新账户号
- 销户、挂失、补办类接口必须提交 `customer_id_number`，后端会做客户身份核验
- 资金销户前要求余额、冻结金额、总金额满足规则
- 证券销户前要求无持仓，并会同步解除有效关联
- 交易冻结、释放、结算时，服务端会再次校验关联关系和账户状态，调用方不能只依赖前置校验

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

以下列出其他组联调时最常用的 API 入口，完整定义以 `/docs` 为准。

### 基础资料

- `POST /api/v1/account/customers`
- `GET /api/v1/account/customers`
- `GET /api/v1/account/customers/{customer_id}`
- `POST /api/v1/account/staff`
- `GET /api/v1/account/staff`

### 开户申请与审批

- `POST /api/v1/account/applications`
- `GET /api/v1/account/applications`
- `GET /api/v1/account/applications/{application_id}`
- `POST /api/v1/account/applications/{application_id}/approve`
- `POST /api/v1/account/applications/{application_id}/reject`
- `GET /api/v1/account/applications/{application_id}/approval-records`

### 资金账户

- `GET /api/v1/account/fund-accounts/{fund_account_id}`
- `GET /api/v1/account/fund-accounts/{fund_account_id}/transactions`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/deposits`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/withdrawals`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/password/reset`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/lost`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/reissue`
- `DELETE /api/v1/account/fund-accounts/{fund_account_id}`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/freeze`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/release`
- `POST /api/v1/account/fund-accounts/{fund_account_id}/settlements`

### 证券账户

- `GET /api/v1/account/security-accounts`
- `GET /api/v1/account/security-accounts/{security_account_id}`
- `GET /api/v1/account/security-accounts/{security_account_id}/positions`
- `POST /api/v1/account/security-accounts/{security_account_id}/positions/freeze`
- `POST /api/v1/account/security-accounts/{security_account_id}/positions/release`
- `POST /api/v1/account/security-accounts/{security_account_id}/positions/settlements`
- `POST /api/v1/account/security-accounts/{security_account_id}/lost`
- `POST /api/v1/account/security-accounts/{security_account_id}/reissue`
- `DELETE /api/v1/account/security-accounts/{security_account_id}`

### 关联、状态与日志

- `GET /api/v1/account/associations`
- `GET /api/v1/account/associations/check`
- `GET /api/v1/account/associations/history`
- `POST /api/v1/account/associations`
- `DELETE /api/v1/account/associations`
- `POST /api/v1/account/status/check`
- `POST /api/v1/account/status/change`
- `GET /api/v1/account/status/history`
- `POST /api/v1/account/operation-logs`
- `GET /api/v1/account/operation-logs`

### 交易客户端认证

- `POST /api/v1/account/auth/login`
- `POST /api/v1/account/auth/password`

## 给其他组的对接 Guide

### 柜台前端 / 审批前端

适用场景：

- 内部业务页面联调
- 申请审批、柜台受理、日志查询

接入建议：

- 使用 `SERVICE_TOKEN`
- 默认以 `http://localhost:8000/api/v1/account` 为后端前缀
- 优先走根仓库前端现有门面，不要再新增一套平行 mock 语义

### 中央交易系统

适用场景：

- 下单前账户状态校验
- 冻结/释放交易资金
- 冻结/释放/结算证券持仓
- 成交后资金与持仓结算

推荐对接顺序：

1. 使用资金账户、证券账户或服务令牌获取访问权限
2. 下单前调用 `POST /status/check` 与 `GET /associations/check`
3. 委托受理后调用资金或持仓冻结接口
4. 成交或撤单后调用释放/结算接口
5. 如需审计，补记 `POST /operation-logs`

对接注意事项：

- 资金冻结/释放接口使用 `fund_account_id`
- 持仓冻结/释放接口使用 `security_account_id + stock_code`
- 结算接口请求体中区分业务单号、成交单号、消息号，便于幂等和追踪
- 服务端会再次校验账户状态与当前有效绑定，不满足条件会直接拒绝
- 若中央交易系统只持有投资者令牌，则只能访问与该令牌归属一致的账户

### 基础资料或客户中心模块

适用场景：

- 同步客户基础信息
- 补录工作人员主数据

建议：

- 统一复用 `customers`、`staff` 表，不要在外围系统维护另一套账户归属真相源
- 若外部系统先建客户，再发起开户申请，请确保 `customer_id`、`id_number` 唯一且稳定

### 运维/审计/管理类模块

适用场景：

- 查询账户状态变更历史
- 检索柜台操作日志
- 排查联调问题

建议：

- 统一接 `operation-logs`、`status/history`、`associations/history`
- 对外展示时保留 `request_id`、`operator_id`、`operator_name` 等追踪字段

## 常见问题

### 为什么前端页面能进，但不是员工登录？

因为当前前端的 `/login` 是角色入口页，不是后台鉴权页；后端现有登录接口是交易客户端资金账户登录。

### 为什么有 `mock` 相关代码还保留？

当前前端已移除 mock 数据源，页面统一通过真实后端联调。

### 为什么有些接口要求 `customer_id_number`？

这是后端做挂失、补办、销户等高风险操作时的客户身份校验要求，不应在前端省略。

## 开发分工

- 组长：基础数据、仓库整合、接口联调、数据库规范
- A：开户申请与审批
- B：证券账户和资金账户管理
- C：账户关联与日志审计
- D：Vue 3 前端页面与联调
