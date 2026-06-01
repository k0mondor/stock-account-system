# stock-account-system

账户管理前端 Demo（Vue 3 + Vite + Element Plus），包含工作人员端与审批端两套界面，支持 Mock/HTTP 数据源切换，便于后续对接后端接口。

## 功能概览

### 工作人员端（/staff）

- 证券账户：查询、开设、挂失补办、注销
- 资金账户：查询、存取款、挂失补开、注销、修改密码
- 联合开户：同时开设证券账户与资金账户并建立关联
- 业务快捷导航：顶部点击展开
- 帮助面板：`?` 打开/关闭，`Esc` 关闭

### 审批端（/approver）

- 审批列表
- 操作日志
- 帮助面板：`?` 打开/关闭，`Esc` 关闭

## 技术栈

- Vite + Vue 3（SFC）
- Vue Router 4
- Element Plus + @element-plus/icons-vue
- Axios
- Python + FastAPI（后端，目录：`backend/`）
- SQLAlchemy + MySQL / SQLite（数据库）

## 本地运行

### 前端

```bash
cd frontend
npm install
npm run dev
```

构建产物：

```bash
cd frontend
npm run build
```

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

后端 API 文档：http://localhost:8000/docs

## 环境变量

本项目使用 Vite 环境变量（以 `VITE_` 开头）。

- `VITE_API_BASE_URL`
  - 后端域名/前缀（例如 `http://localhost:8000`）
- `VITE_ACCOUNT_PREFIX`
  - 账户域 API 前缀（默认 `/api/v1/account`）
- `VITE_USE_MOCK`
  - `true`：前端 Axios 层启用 Mock 拦截
  - `false`：前端 Axios 层调用真实后端
- `VITE_DATA_SOURCE`
  - `mock`：`frontend/src/utils/request.js` 走本地 Mock 数据
  - `http`：`frontend/src/utils/request.js` 走 HTTP 服务层

建议在 `frontend/` 目录下创建 `.env.local`（参考 `frontend/.env.example`）。

## Mock 与对接后端

### 数据源切换入口

- 页面仍统一从 `frontend/src/utils/request.js` 导入接口方法
- `VITE_DATA_SOURCE=mock|http` 控制旧门面层走 Mock 或 HTTP
- `VITE_USE_MOCK=true|false` 控制 Axios 层是否启用 Mock 拦截

### HTTP 分层（便于后端对齐与字段映射）

- `frontend/src/api/httpClient.js`
  - Axios 实例 + token 注入（`localStorage.token`）
  - 统一解包后端通用响应：当响应包含 `success` 字段时，成功返回 `data`，失败抛出 `Error(message)`
- `frontend/src/api/accountApi.js`
  - 仅封装 endpoint（prefix 可配置）
- `frontend/src/services/accountService.js`
  - 字段映射与格式转换（snake_case → camelCase、金额转 number）
- `frontend/src/utils/request.js`
  - 门面层：兼容现有页面调用方式，并做 Mock/HTTP 分流

### 当前已接入 HTTP 的能力

以 `VITE_DATA_SOURCE=http` 运行时，目前已接入：

- 资金账户查询（按资金账户号）：`getFundAccountByNo`
- 关联查询：`getAssociations`
- 修改资金密码：`changeFundPassword`

其余接口会直接报错 `后端接口未接入`，用于提醒补齐对接。

## 关键约定（字段与枚举）

### 资金账户金额字段

- 可用金额：`availableBalance`
- 冻结金额：`frozenAmount`

### 枚举对齐

- 账户状态：`NORMAL | LOST | FROZEN | CLOSED`
- 关联状态：`ACTIVE | UNLINKED`

详见：

- `frontend/src/constants/enums.js`

## 目录结构

```text
backend/              # Python FastAPI 后端
database/             # 数据库规范、schema、测试数据
frontend/
  package.json        # 前端依赖与脚本
  vite.config.js      # Vite 配置
  src/
    api/              # httpClient + endpoint 封装
    services/         # 字段映射/格式转换
    utils/request.js  # 接口门面（Mock/HTTP 切换）
    mock/             # 本地 Mock 数据
    views/
      common/         # 登录、日志等通用页
      staff/          # 工作人员端
      approver/       # 审批端
    components/       # PageHeader / HelpDrawer / BiText 等
    constants/        # enums / i18n
    router/           # 路由定义
    style.css         # 全局样式
```

## 接口文档

仓库根目录包含对齐参考：

- `接口V2_修正版(3).md`

## 开发分工

- 组长：基础数据、仓库整合、接口联调、数据库规范
- A：开户申请与审批
- B：证券账户和资金账户管理
- C：账户关联与日志审计
- D：Vue3 前端页面与联调
