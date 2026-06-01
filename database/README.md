# Database

本目录用于维护账户业务子系统数据库脚本和字段规范。

## 命名规则

- 表名使用小写复数：`customers`、`fund_accounts`
- 字段名使用 `snake_case`：`customer_id`、`created_at`
- ID 使用字符串，示例：`CUST000001`、`FUND000001`
- 金额使用 `DECIMAL(18, 2)`，代码中使用 `Decimal`，禁止使用 `float`
- 时间字段统一保留 `created_at`、`updated_at`

## 第一阶段 MVP 表

- `customers`
- `staff`
- `account_applications`
- `approval_records`
- `securities_accounts`
- `fund_accounts`
- `account_associations`
- `operation_logs`

当前已落地组长负责的基础表：`customers`、`staff`。

## 统一枚举

- 账户状态：`NORMAL`、`FROZEN`、`LOST`、`CLOSED`
- 资金账户密码类型：`TRADE`、`WITHDRAW`
- 账户关联状态：`ACTIVE`、`UNLINKED`
