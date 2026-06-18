-- Sample business analytics schema for Tally AI Analytics
-- Run: psql -U tally_user -d tally_db -f sql/sample_schema.sql

CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    customer_name   VARCHAR(200) NOT NULL,
    email           VARCHAR(200),
    phone           VARCHAR(50),
    city            VARCHAR(100),
    state           VARCHAR(100),
    country         VARCHAR(100) DEFAULT 'India',
    customer_type   VARCHAR(50) DEFAULT 'Retail',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id       SERIAL PRIMARY KEY,
    vendor_name     VARCHAR(200) NOT NULL,
    contact_person  VARCHAR(200),
    email           VARCHAR(200),
    phone           VARCHAR(50),
    city            VARCHAR(100),
    payment_terms   VARCHAR(50) DEFAULT 'Net 30',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    unit_price      NUMERIC(12, 2) NOT NULL,
    cost_price      NUMERIC(12, 2) NOT NULL,
    sku             VARCHAR(50) UNIQUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id    SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    warehouse       VARCHAR(100) DEFAULT 'Main',
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    reorder_level   INTEGER DEFAULT 10,
    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id         SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    sale_date       DATE NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(12, 2) NOT NULL,
    discount_pct    NUMERIC(5, 2) DEFAULT 0,
    total_amount    NUMERIC(14, 2) GENERATED ALWAYS AS (
        quantity * unit_price * (1 - discount_pct / 100)
    ) STORED,
    region          VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id     SERIAL PRIMARY KEY,
    vendor_id       INTEGER NOT NULL REFERENCES vendors(vendor_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    purchase_date   DATE NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_cost       NUMERIC(12, 2) NOT NULL,
    total_cost      NUMERIC(14, 2) GENERATED ALWAYS AS (quantity * unit_cost) STORED
);

CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_purchases_vendor ON purchases(vendor_id);
