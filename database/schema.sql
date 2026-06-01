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
