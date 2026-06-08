CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_name VARCHAR(64) NOT NULL,
    id_type VARCHAR(32),
    id_number VARCHAR(32) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    gender VARCHAR(16),
    address VARCHAR(255),
    occupation VARCHAR(64),
    education_level VARCHAR(32),
    employer VARCHAR(128),
    agent_id_number VARCHAR(32),
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
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS approval_records (
    approval_id VARCHAR(32) PRIMARY KEY,
    application_id VARCHAR(32) NOT NULL,
    approver_id VARCHAR(32) NOT NULL,
    approval_result VARCHAR(16) NOT NULL,
    approval_opinion TEXT,
    approved_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (application_id) REFERENCES account_applications(application_id),
    FOREIGN KEY (approver_id) REFERENCES staff(staff_id)
);

CREATE INDEX idx_applications_customer ON account_applications (customer_id);
CREATE INDEX idx_applications_status ON account_applications (app_status, proc_status);
CREATE INDEX idx_approval_records_application ON approval_records (application_id);

CREATE TABLE IF NOT EXISTS fund_accounts (
    fund_account_id VARCHAR(32) PRIMARY KEY,
    investor_id VARCHAR(32) NOT NULL,
    bank_card_no VARCHAR(32) NOT NULL,
    trade_password_hash VARCHAR(256) NOT NULL,
    withdraw_password_hash VARCHAR(256) NOT NULL,
    available_balance DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    frozen_amount DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    account_status VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_fund_accounts_investor ON fund_accounts (investor_id);
CREATE INDEX idx_fund_accounts_status ON fund_accounts (account_status);

CREATE TABLE IF NOT EXISTS fund_transaction_records (
    transaction_id VARCHAR(64) PRIMARY KEY,
    fund_account_id VARCHAR(32) NOT NULL,
    business_order_id VARCHAR(64),
    operator_staff_id VARCHAR(32),
    transaction_type VARCHAR(16) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    reason VARCHAR(256),
    occurred_at DATETIME NOT NULL,
    FOREIGN KEY (fund_account_id) REFERENCES fund_accounts(fund_account_id)
);

CREATE INDEX idx_fund_transaction_account_time
ON fund_transaction_records (fund_account_id, occurred_at);

CREATE UNIQUE INDEX uq_fund_transaction_business
ON fund_transaction_records (
    fund_account_id,
    business_order_id,
    transaction_type
);

CREATE TABLE IF NOT EXISTS account_state_change_records (
    change_id VARCHAR(32) PRIMARY KEY,
    account_type VARCHAR(16) NOT NULL,
    account_id VARCHAR(32) NOT NULL,
    previous_status VARCHAR(16) NOT NULL,
    target_status VARCHAR(16) NOT NULL,
    reason VARCHAR(256),
    operator_id VARCHAR(32) NOT NULL,
    operator_name VARCHAR(64) NOT NULL,
    changed_at DATETIME NOT NULL
);

CREATE INDEX idx_state_changes_account
ON account_state_change_records (account_type, account_id, changed_at);

CREATE TABLE IF NOT EXISTS securities_accounts (
    security_account_id VARCHAR(32) PRIMARY KEY,
    investor_id VARCHAR(32) NOT NULL,
    account_status VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_securities_accounts_investor ON securities_accounts (investor_id);
CREATE INDEX idx_securities_accounts_status ON securities_accounts (account_status);

CREATE TABLE IF NOT EXISTS security_positions (
    position_id VARCHAR(32) PRIMARY KEY,
    security_account_id VARCHAR(32) NOT NULL,
    investor_id VARCHAR(32) NOT NULL,
    stock_code VARCHAR(6) NOT NULL,
    stock_name VARCHAR(64),
    total_quantity INT NOT NULL DEFAULT 0,
    available_quantity INT NOT NULL DEFAULT 0,
    frozen_quantity INT NOT NULL DEFAULT 0,
    cost_price DECIMAL(18, 4),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (security_account_id) REFERENCES securities_accounts(security_account_id),
    FOREIGN KEY (investor_id) REFERENCES customers(customer_id),
    CONSTRAINT uq_security_position_stock UNIQUE (security_account_id, stock_code)
);

CREATE INDEX idx_security_positions_stock
ON security_positions (security_account_id, stock_code);

CREATE TABLE IF NOT EXISTS position_transaction_records (
    record_id VARCHAR(64) PRIMARY KEY,
    security_account_id VARCHAR(32) NOT NULL,
    business_order_id VARCHAR(64) NOT NULL,
    trade_id VARCHAR(64),
    stock_code VARCHAR(6) NOT NULL,
    change_type VARCHAR(16) NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(256),
    occurred_at DATETIME NOT NULL,
    FOREIGN KEY (security_account_id) REFERENCES securities_accounts(security_account_id),
    CONSTRAINT uq_position_transaction_business UNIQUE (
        security_account_id,
        business_order_id,
        change_type,
        stock_code
    )
);

CREATE INDEX idx_position_account_time
ON position_transaction_records (security_account_id, occurred_at);

-- ==================== Part C: 账户关联与日志审计 ====================

-- 账户关联表
CREATE TABLE IF NOT EXISTS account_associations (
    association_id VARCHAR(32) PRIMARY KEY,
    investor_id VARCHAR(32) NOT NULL,
    fund_account_id VARCHAR(32) NOT NULL,
    security_account_id VARCHAR(32) NOT NULL,
    association_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    associated_at DATETIME NOT NULL,
    disassociated_at DATETIME,
    active_fund_account_id VARCHAR(32) GENERATED ALWAYS AS (
        CASE WHEN association_status = 'ACTIVE' THEN fund_account_id ELSE NULL END
    ) STORED,
    active_security_account_id VARCHAR(32) GENERATED ALWAYS AS (
        CASE WHEN association_status = 'ACTIVE' THEN security_account_id ELSE NULL END
    ) STORED,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES customers(customer_id),
    FOREIGN KEY (fund_account_id) REFERENCES fund_accounts(fund_account_id),
    FOREIGN KEY (security_account_id) REFERENCES securities_accounts(security_account_id)
);

CREATE INDEX idx_associations_investor ON account_associations (investor_id);
CREATE INDEX idx_associations_fund ON account_associations (fund_account_id);
CREATE INDEX idx_associations_securities ON account_associations (security_account_id);
CREATE INDEX idx_associations_status ON account_associations (association_status);
CREATE UNIQUE INDEX uq_active_association_fund
ON account_associations (active_fund_account_id);
CREATE UNIQUE INDEX uq_active_association_security
ON account_associations (active_security_account_id);

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
