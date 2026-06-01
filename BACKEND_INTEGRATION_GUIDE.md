# 给后端同学的前端联调指南

## 一、前端项目位置

实际前端项目在 `frontend/` 目录下：
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/vite.config.js`
- `frontend/src/` 及其子目录

> 注意：根目录下的 `package-lock.json` 是历史遗留文件，前端安装和运行应在 `frontend/` 目录内执行。

---

## 二、前端当前结构是否正常

当前前端文件结构已经合理：
- `frontend/src/api/httpClient.js`：统一 Axios 配置、支持 token、支持 mock 开关
- `frontend/src/api/accountApi.js`：后端接口定义层
- `frontend/src/services/accountService.js`：业务层，负责 API 参数映射和结果转换
- `frontend/src/api/mockInterceptor.js`：Mock 数据拦截器
- `frontend/.env.example`：环境变量示例

这部分已经准备好了，主要需要后端确认接口细节和返回字段。

---

## 三、Mock 转真实 API 的处理情况

已经做了切换逻辑：

- 开发时可使用 `VITE_USE_MOCK=true`，前端会走 `mockInterceptor` 返回模拟数据
- 联调时设置 `VITE_USE_MOCK=false`，前端会走真实后端地址

配置示例：

```bash
# frontend/.env.local
VITE_API_BASE_URL=http://localhost:8080
VITE_ACCOUNT_PREFIX=/api/v1/account
VITE_USE_MOCK=false
```

如果你把这个配置写在本地 `.env.local`，它不会被提交到仓库。

---

## 四、后端需要提供的接口

前端当前调用的接口如下：

1. 登录
   - `POST /api/v1/account/auth/login`
   - 前端直接把登录表单 body 传给后端

2. 修改密码
   - `POST /api/v1/account/auth/password`
   - 请求 body 格式：
     ```json
     {
       "fund_account_id": "FND00000001",
       "password_type": "TRADE" | "WITHDRAW",
       "old_password": "oldpwd",
       "new_password": "newpwd"
     }
     ```

3. 查询基金账户
   - `GET /api/v1/account/fund-accounts/{fundAccountId}`

4. 查询关联关系
   - `GET /api/v1/account/associations`
   - 支持查询参数：
     - `fund_account_id`
     - `security_account_id`
     - `investor_id`

---

## 五、后端返回数据的字段格式

前端业务层期望后端返回的数据字段如下：

### 基金账户
```json
{
  "fund_account_id": "FND00000001",
  "investor_id": 10001,
  "bank_card_no": "6222021234567890",
  "available_amount": 120000.00,
  "frozen_amount": 30000.00,
  "status": "NORMAL"
}
```

### 关联关系
```json
{
  "association_id": "ASSOC00000001",
  "investor_id": 10001,
  "fund_account_id": "FND00000001",
  "security_account_id": "SEC00000001",
  "association_status": "ACTIVE",
  "associated_at": "2026-01-10T09:05:00"
}
```

如果返回字段名不同，前端需要调整 `frontend/src/services/accountService.js` 的映射函数。

---

## 六、后端返回格式建议

前端 `httpClient` 目前对响应格式做了基础判断：

- 如果返回对象里包含 `success` 字段，且 `success=true`，则返回 `data`
- 如果 `success=false`，会抛出错误
- 如果没有 `success` 字段，则直接返回后端响应体

因此后端可以选择两种返回方式之一：

1. 推荐：统一包装
```json
{
  "success": true,
  "data": { /* 业务数据 */ }
}
```

2. 或者直接返回业务数据对象
```json
{
  "fund_account_id": "FND00000001",
  ...
}
```

---

## 七、后端需要确认的点

1. `VITE_ACCOUNT_PREFIX=/api/v1/account` 是否与后端实际路径一致
2. 登录接口是否返回 token，并且前端会把 token 存到 `localStorage.token`
3. 修改密码接口字段名是否与前端一致
4. 数据字段命名是否保持与 `accountService` 中的 `snake_case` 结构一致

---

## 八、结论

- 前端这边的文件结构和 mock 切换逻辑已经准备好了
- 只要后端按上面接口和字段规范对齐，联调就可以直接开始
- 你这边唯一要确认的是：
  - `VITE_API_BASE_URL`、`VITE_ACCOUNT_PREFIX`
  - 后端接口返回字段是否和映射一致

如果后端同学确认字段不一致，我可以继续帮你把 `accountService` 的字段映射改成他们实际返回的字段。