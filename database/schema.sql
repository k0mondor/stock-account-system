CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_name VARCHAR(64) NOT NULL,
    id_number VARCHAR(32) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    customer_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id VARCHAR(32) PRIMARY KEY,
    staff_name VARCHAR(64) NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'STAFF',
    phone VARCHAR(20),
    staff_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX idx_customers_id_number ON customers (id_number);
CREATE INDEX idx_staff_role ON staff (role);

CREATE TABLE IF NOT EXISTS account_applications (
    application_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    applicant_name VARCHAR(64) NOT NULL,
    id_number VARCHAR(32) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    app_status VARCHAR(16) NOT NULL DEFAULT 'SUBMITTED',
    proc_status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    fund_account_id VARCHAR(32),
    security_account_id VARCHAR(32),
    submitted_at DATETIME NOT NULL,
    processed_at DATETIME,
    remark TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_records (
    approval_id VARCHAR(32) PRIMARY KEY,
    application_id VARCHAR(32) NOT NULL,
    approver_id VARCHAR(32) NOT NULL,
    approval_result VARCHAR(16) NOT NULL,
    approval_opinion TEXT,
    approved_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE INDEX idx_applications_customer ON account_applications (customer_id);
CREATE INDEX idx_applications_status ON account_applications (app_status, proc_status);
CREATE INDEX idx_approval_records_application ON approval_records (application_id);

CREATE TABLE IF NOT EXISTS fund_accounts (
    fund_account_id VARCHAR(32) PRIMARY KEY,
    investor_id VARCHAR(32) NOT NULL,
    bank_card_no VARCHAR(32) NOT NULL,
    trade_password_hash VARCHAR(256),
    withdraw_password_hash VARCHAR(256),
    available_balance DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    frozen_amount DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    account_status VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX idx_fund_accounts_investor ON fund_accounts (investor_id);
CREATE INDEX idx_fund_accounts_status ON fund_accounts (account_status);

CREATE TABLE IF NOT EXISTS fund_transaction_records (
    transaction_id VARCHAR(64) PRIMARY KEY,
    fund_account_id VARCHAR(32) NOT NULL,
    business_order_id VARCHAR(64),
    transaction_type VARCHAR(16) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    reason VARCHAR(256),
    occurred_at DATETIME NOT NULL
);

CREATE INDEX idx_fund_transaction_account_time
ON fund_transaction_records (fund_account_id, occurred_at);

-- ==================== Part C: 账户关联与日志审计 ====================

-- 账户关联表
CREATE TABLE IF NOT EXISTS account_associations (
    association_id VARCHAR(32) PRIMARY KEY,
    investor_id VARCHAR(32) NOT NULL,
    fund_account_id VARCHAR(32) NOT NULL,
    security_account_id VARCHAR(32) NOT NULL,
    association_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    associated_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX idx_associations_investor ON account_associations (investor_id);
CREATE INDEX idx_associations_fund ON account_associations (fund_account_id);
CREATE INDEX idx_associations_securities ON account_associations (security_account_id);
CREATE INDEX idx_associations_status ON account_associations (association_status);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    log_id VARCHAR(32) PRIMARY KEY,
    operator_id VARCHAR(32) NOT NULL,
    operator_name VARCHAR(64) NOT NULL,
    operation_type VARCHAR(32) NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_id VARCHAR(64) NOT NULL,
    operation_detail TEXT,
    operation_result VARCHAR(16) NOT NULL DEFAULT 'SUCCESS',
    fail_reason TEXT,
    client_ip VARCHAR(64),
    request_id VARCHAR(64),
    created_at DATETIME NOT NULL
);

CREATE INDEX idx_operation_logs_operator ON operation_logs (operator_id);
CREATE INDEX idx_operation_logs_type ON operation_logs (operation_type);
CREATE INDEX idx_operation_logs_target ON operation_logs (target_id);
CREATE INDEX idx_operation_logs_time ON operation_logs (created_at);
