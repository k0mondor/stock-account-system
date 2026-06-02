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
