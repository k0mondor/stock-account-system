# Database

本目录用于维护账户业务子系统数据库脚本和字段规范。

## 命名规则

- 表名使用小写复数：`customers`、`fund_accounts`
- 字段名使用 `snake_case`：`customer_id`、`created_at`
- ID 使用字符串，示例：`CUST000001`、`FUND000001`
- 金额使用 `DECIMAL(18, 2)`，代码中使用 `Decimal`，禁止使用 `float`
- 交易密码和取款密码仅保存哈希值，且两个密码哈希字段均为必填
- 时间字段统一保留 `created_at`、`updated_at`
- 关联历史使用 `disassociated_at` 保存解除时间，不删除历史记录
- 当前 `ACTIVE` 关联在资金账户和证券账户两个方向均由唯一索引约束
- 资金流水使用 `operator_staff_id` 记录柜台操作员，交易系统自动流水可为空

## 第一阶段 MVP 表

- `customers`
- `staff`
- `account_applications`
- `approval_records`
- `securities_accounts`
- `fund_accounts`
- `account_associations`
- `account_state_change_records`
- `security_positions`
- `position_transaction_records`
- `operation_logs`

上述 MVP 表以及资金流水表 `fund_transaction_records` 均已落地。

`schema.sql` 面向 MySQL，使用生成列实现“仅当前有效关联唯一”；SQLite
开发库由后端启动迁移创建等价的部分唯一索引。

## 统一枚举

- 账户状态：`NORMAL`、`FROZEN`、`LOST`、`CLOSED`
- 资金账户密码类型：`TRADE`、`WITHDRAW`
- 账户关联状态：`ACTIVE`、`UNLINKED`
- 开户申请状态：`SUBMITTED`、`CANCELLED`
- 开户处理状态：`PENDING`、`APPROVED`、`REJECTED`、`COMPLETED`
