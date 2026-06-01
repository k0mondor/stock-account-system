# 账户业务子系统(ACCOUNT) - 使用文档

## 系统概述

本模块实现股票交易系统中的**账户业务子系统**，主要负责：
- **客户与业务受理**：处理客户开户申请
- **账户申请与审批**：审批流程、创建账户、建立绑定关系

## 核心功能

### 1. 开户申请提交 (`POST /api/v1/account/applications/submit`)

**功能说明**：客户提交开户申请

**请求示例**：
```json
{
  "username": "user001",
  "real_name": "张三",
  "id_card": "110101199003011234",
  "phone": "13800000001",
  "email": "user001@example.com"
}
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": {
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "username": "user001",
    "real_name": "张三",
    "id_card": "110101199003011234",
    "phone": "13800000001",
    "email": "user001@example.com",
    "status": "PENDING",
    "created_at": "2026-06-01T10:00:00"
  },
  "code": 0,
  "message": "申请提交成功",
  "timestamp": "2026-06-01T10:00:00"
}
```

### 2. 申请查询 (`GET /api/v1/account/applications/query`)

**功能说明**：查询开户申请列表，支持多条件筛选

**查询参数**：
- `application_id` (可选) - 申请编号
- `username` (可选) - 用户名
- `id_card` (可选) - 身份证号
- `status` (可选) - 申请状态 (PENDING/APPROVED/REJECTED)

**请求示例**：
```
GET /api/v1/account/applications/query?status=PENDING
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": [
    {
      "application_id": "APP1A2B3C4D5E6F7G8H",
      "investor_id": null,
      "username": "user001",
      "real_name": "张三",
      "id_card": "110101199003011234",
      "status": "PENDING",
      "created_at": "2026-06-01T10:00:00"
    }
  ],
  "code": 0,
  "message": "查询成功",
  "timestamp": "2026-06-01T10:00:00"
}
```

### 3. 获取申请详情 (`GET /api/v1/account/applications/{application_id}`)

**功能说明**：获取单个申请的详细信息

**请求示例**：
```
GET /api/v1/account/applications/APP1A2B3C4D5E6F7G8H
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": {
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "investor_id": null,
    "username": "user001",
    "real_name": "张三",
    "id_card": "110101199003011234",
    "phone": "13800000001",
    "email": "user001@example.com",
    "status": "PENDING",
    "fund_account_id": null,
    "security_account_id": null,
    "approval_reason": null,
    "approval_at": null,
    "created_at": "2026-06-01T10:00:00",
    "updated_at": "2026-06-01T10:00:00"
  },
  "code": 0,
  "message": "查询成功",
  "timestamp": "2026-06-01T10:00:00"
}
```

### 4. 审批通过 (`POST /api/v1/account/applications/approve`)

**功能说明**：管理员审批通过申请，系统自动创建：
- 投资者用户账户
- 资金账户
- 证券账户
- 账户绑定关系（一对一）

**请求示例**：
```json
{
  "application_id": "APP1A2B3C4D5E6F7G8H",
  "approver_id": "ADMIN001",
  "approver_name": "李四",
  "action": "APPROVE",
  "reason": "申请资料完整，符合开户条件"
}
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": {
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "investor_id": "INV1A2B3C4D5E6F7G8",
    "status": "APPROVED",
    "fund_account_id": "FUND1A2B3C4D5E",
    "security_account_id": "SEC1A2B3C4D5E6F",
    "approval_reason": "申请资料完整，符合开户条件",
    "approval_at": "2026-06-01T10:05:00"
  },
  "code": 0,
  "message": "审批通过成功，账户已创建",
  "timestamp": "2026-06-01T10:05:00"
}
```

**创建的账户信息**：
- `investor_id`: 投资者编号（示例：INV...）
- `fund_account_id`: 资金账户号（示例：FUND...）
- `security_account_id`: 证券账户号（示例：SEC...）
- 默认密码：123456（用户需要登录后修改）

### 5. 拒绝申请 (`POST /api/v1/account/applications/reject`)

**功能说明**：管理员拒绝申请

**请求示例**：
```json
{
  "application_id": "APP1A2B3C4D5E6F7G8H",
  "approver_id": "ADMIN001",
  "approver_name": "李四",
  "action": "REJECT",
  "reason": "身份证信息与数据库不符"
}
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": {
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "status": "REJECTED",
    "approval_reason": "身份证信息与数据库不符",
    "approval_at": "2026-06-01T10:05:00"
  },
  "code": 0,
  "message": "申请已拒绝",
  "timestamp": "2026-06-01T10:05:00"
}
```

### 6. 获取审批历史 (`GET /api/v1/account/applications/{application_id}/approval-history`)

**功能说明**：查看申请的完整审批历史记录

**请求示例**：
```
GET /api/v1/account/applications/APP1A2B3C4D5E6F7G8H/approval-history
```

**成功响应** (200)：
```json
{
  "success": true,
  "data": {
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "histories": [
      {
        "history_id": "HIS1A2B3C4D5E",
        "action": "SUBMIT",
        "action_by": "user001",
        "action_by_name": "张三",
        "old_status": null,
        "new_status": "PENDING",
        "remark": "申请提交",
        "created_at": "2026-06-01T10:00:00"
      },
      {
        "history_id": "HIS2A2B3C4D5E",
        "action": "APPROVE",
        "action_by": "ADMIN001",
        "action_by_name": "李四",
        "old_status": "PENDING",
        "new_status": "APPROVED",
        "remark": "申请资料完整，符合开户条件",
        "created_at": "2026-06-01T10:05:00"
      }
    ]
  },
  "code": 0,
  "message": "查询成功",
  "timestamp": "2026-06-01T10:05:00"
}
```

## 申请状态流转

```
PENDING (待审批)
    ├─ APPROVE → APPROVED (已批准)
    │              └─ 自动创建：投资者 + 资金账户 + 证券账户 + 绑定
    └─ REJECT  → REJECTED (已拒绝)
```

## 错误处理

### 常见错误码

| 错误码 | 含义 | 状态码 |
|--------|------|--------|
| 0 | 成功 | 200 |
| 40001 | 请求格式错误 | 400 |
| 40401 | 资源不存在 | 404 |
| 40900 | 资源冲突（用户名/身份证已存在） | 409 |
| 50001 | 服务内部错误 | 500 |

### 错误响应示例

```json
{
  "success": false,
  "data": null,
  "code": 40900,
  "message": "用户名已被使用: user001",
  "timestamp": "2026-06-01T10:00:00"
}
```

## 数据流流程

### 申请提交流程
1. 客户提交申请信息
2. 系统验证用户名、身份证是否重复
3. 创建申请记录（状态：PENDING）
4. 创建审批历史记录（SUBMIT）

### 审批通过流程
1. 管理员审批申请
2. **自动创建投资者用户**
   - 生成 investor_id
   - 设置默认密码（123456）
3. **自动创建资金账户**
   - 生成 fund_account_id
   - 初始资金：0.00
4. **自动创建证券账户**
   - 生成 security_account_id
5. **自动建立账户绑定**
   - 创建 AccountAssociation
   - 绑定状态：ACTIVE（一对一绑定）
6. 更新申请状态（APPROVED）
7. 创建审批历史记录（APPROVE）

## 数据库表结构

### account_applications（开户申请表）
```sql
CREATE TABLE account_applications (
    application_id VARCHAR(50) PRIMARY KEY,
    investor_id VARCHAR(50),
    username VARCHAR(100) UNIQUE NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    id_card VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    fund_account_id VARCHAR(50),
    security_account_id VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    approver_id VARCHAR(50),
    approver_name VARCHAR(100),
    approval_reason TEXT,
    approval_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

### approval_histories（审批历史表）
```sql
CREATE TABLE approval_histories (
    history_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    action_by VARCHAR(50) NOT NULL,
    action_by_name VARCHAR(100),
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    remark TEXT,
    created_at DATETIME
);
```

## 集成注意事项

1. **密码管理**
   - 审批通过后，系统为新用户设置默认密码：`123456`
   - 用户首次登录后需要修改密码
   - 交易密码和取款密码初始值相同

2. **账户绑定**
   - 一个投资者 = 一个资金账户 + 一个证券账户
   - 绑定关系为一对一，不支持多账户

3. **日志记录**
   - 所有申请和审批操作均记录在 approval_histories 表中
   - 保留完整的审计跟踪

4. **错误恢复**
   - 如果审批通过过程中出现错误，整个事务会回滚
   - 申请状态保持不变

## 测试用例

### 完整申请流程测试

```bash
# 1. 提交申请
curl -X POST http://localhost:8000/api/v1/account/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "real_name": "测试用户",
    "id_card": "110101199003011234",
    "phone": "13800000001",
    "email": "test@example.com"
  }'

# 响应：获取 application_id

# 2. 查询申请
curl http://localhost:8000/api/v1/account/applications/query?status=PENDING

# 3. 审批通过
curl -X POST http://localhost:8000/api/v1/account/applications/approve \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP1A2B3C4D5E6F7G8H",
    "approver_id": "ADMIN001",
    "approver_name": "管理员",
    "action": "APPROVE",
    "reason": "申请资料完整"
  }'

# 4. 查看审批历史
curl http://localhost:8000/api/v1/account/applications/APP1A2B3C4D5E6F7G8H/approval-history
```

## API 文档

访问 `http://localhost:8000/docs` 可查看完整的 Swagger API 文档。
