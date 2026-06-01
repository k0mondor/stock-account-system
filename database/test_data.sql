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
