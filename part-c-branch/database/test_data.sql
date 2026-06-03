INSERT INTO customers (
    customer_id,
    customer_name,
    id_number,
    phone,
    customer_status,
    created_at,
    updated_at
) VALUES (
    'CUST000001',
    '测试客户',
    '110101200001010001',
    '13800000001',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT INTO staff (
    staff_id,
    staff_name,
    role,
    phone,
    staff_status,
    created_at,
    updated_at
) VALUES
    ('STAFF000001', '业务受理员', 'STAFF', '13800000002', 'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('APR000001', '审批人员', 'APPROVER', '13800000003', 'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO account_applications (
    application_id,
    customer_id,
    applicant_name,
    id_number,
    phone,
    app_status,
    proc_status,
    submitted_at,
    created_at,
    updated_at
) VALUES (
    'APP000001',
    'CUST000001',
    '测试客户',
    '110101200001010001',
    '13800000001',
    'SUBMITTED',
    'PENDING',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT INTO fund_accounts (
    fund_account_id,
    investor_id,
    bank_card_no,
    available_balance,
    frozen_amount,
    total_amount,
    account_status,
    created_at,
    updated_at
) VALUES (
    'FUND000001',
    'CUST000001',
    '6222021234567890123',
    0.00,
    0.00,
    0.00,
    'NORMAL',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- ==================== Part C: 账户关联与日志审计测试数据 ====================

-- 账户关联测试数据
INSERT INTO account_associations (
    association_id,
    investor_id,
    fund_account_id,
    security_account_id,
    association_status,
    associated_at,
    created_at,
    updated_at
) VALUES (
    'ASC000001',
    'CUST000001',
    'FUND000001',
    'SEC000001',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 操作日志测试数据
INSERT INTO operation_logs (
    log_id,
    operator_id,
    operator_name,
    operation_type,
    target_type,
    target_id,
    operation_detail,
    operation_result,
    fail_reason,
    created_at
) VALUES
    ('LOG000001', 'STAFF000001', '业务受理员', 'OPEN_ACCOUNT', 'APPLICATION', 'APP000001', '为客户开设证券账户与资金账户', 'SUCCESS', NULL, CURRENT_TIMESTAMP),
    ('LOG000002', 'APR000001', '审批人员', 'APPROVE', 'APPLICATION', 'APP000001', '审批通过开户申请', 'SUCCESS', NULL, CURRENT_TIMESTAMP),
    ('LOG000003', 'STAFF000001', '业务受理员', 'LINK', 'ASSOCIATION', 'ASC000001', '关联证券账户 SEC000001 与资金账户 FUND000001', 'SUCCESS', NULL, CURRENT_TIMESTAMP),
    ('LOG000004', 'STAFF000001', '业务受理员', 'DEPOSIT', 'FUND', 'FUND000001', '存款 ¥50,000.00', 'SUCCESS', NULL, CURRENT_TIMESTAMP);
