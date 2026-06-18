-- Sample test data for Tally AI Analytics
-- Run after sample_schema.sql:
--   psql -U tally_user -d tally_db -f sql/sample_data.sql

TRUNCATE TABLE sales, purchases, inventory, products, customers, vendors RESTART IDENTITY CASCADE;

INSERT INTO customers (customer_name, email, phone, city, state, customer_type) VALUES
('Acme Corp', 'contact@acme.com', '9876500001', 'Mumbai', 'Maharashtra', 'Enterprise'),
('Bright Retail', 'info@bright.com', '9876500002', 'Delhi', 'Delhi', 'Retail'),
('City Traders', 'sales@citytraders.com', '9876500003', 'Bangalore', 'Karnataka', 'Wholesale'),
('Delta Industries', 'admin@delta.com', '9876500004', 'Chennai', 'Tamil Nadu', 'Enterprise'),
('East Point Stores', 'hello@eastpoint.com', '9876500005', 'Kolkata', 'West Bengal', 'Retail'),
('Fresh Foods Ltd', 'orders@freshfoods.com', '9876500006', 'Pune', 'Maharashtra', 'Wholesale'),
('Global Tech', 'biz@globaltech.com', '9876500007', 'Hyderabad', 'Telangana', 'Enterprise'),
('Horizon Mart', 'support@horizon.com', '9876500008', 'Ahmedabad', 'Gujarat', 'Retail'),
('Infinity Solutions', 'team@infinity.com', '9876500009', 'Jaipur', 'Rajasthan', 'Enterprise'),
('Jetstream Co', 'sales@jetstream.com', '9876500010', 'Lucknow', 'Uttar Pradesh', 'Retail'),
('Kumar Enterprises', 'kumar@ent.com', '9876500011', 'Mumbai', 'Maharashtra', 'Wholesale'),
('Lighthouse Trading', 'lt@trade.com', '9876500012', 'Surat', 'Gujarat', 'Retail');

INSERT INTO vendors (vendor_name, contact_person, email, city, payment_terms) VALUES
('Prime Suppliers', 'Raj Patel', 'raj@prime.com', 'Mumbai', 'Net 30'),
('Quality Goods Inc', 'Anita Shah', 'anita@quality.com', 'Delhi', 'Net 45'),
('Reliable Parts', 'Vikram Singh', 'vikram@reliable.com', 'Bangalore', 'Net 30'),
('Standard Materials', 'Priya Nair', 'priya@standard.com', 'Chennai', 'Net 15');

INSERT INTO products (product_name, category, unit_price, cost_price, sku) VALUES
('Laptop Pro 15', 'Electronics', 75000.00, 58000.00, 'EL-LP15'),
('Wireless Mouse', 'Electronics', 899.00, 450.00, 'EL-WM01'),
('Office Chair', 'Furniture', 8500.00, 5200.00, 'FR-OC01'),
('Standing Desk', 'Furniture', 22000.00, 14000.00, 'FR-SD01'),
('A4 Paper Ream', 'Stationery', 320.00, 180.00, 'ST-A4R1'),
('Ink Cartridge', 'Stationery', 1200.00, 750.00, 'ST-INK1'),
('LED Monitor 27', 'Electronics', 18500.00, 13200.00, 'EL-MN27'),
('Filing Cabinet', 'Furniture', 6500.00, 4100.00, 'FR-FC01'),
('Notebook Pack', 'Stationery', 450.00, 220.00, 'ST-NBP1'),
('USB-C Hub', 'Electronics', 2499.00, 1400.00, 'EL-UCH1');

INSERT INTO inventory (product_id, warehouse, quantity_on_hand, reorder_level) VALUES
(1, 'Main', 45, 10),
(2, 'Main', 320, 50),
(3, 'Main', 28, 5),
(4, 'Main', 12, 5),
(5, 'Main', 500, 100),
(6, 'Main', 85, 20),
(7, 'Main', 22, 8),
(8, 'Main', 3, 5),
(9, 'Main', 8, 50),
(10, 'Main', 60, 15),
(1, 'East', 18, 10),
(2, 'East', 4, 50),
(5, 'East', 120, 100);

INSERT INTO sales (customer_id, product_id, sale_date, quantity, unit_price, discount_pct, region) VALUES
(1, 1, '2025-01-15', 5, 75000.00, 5.00, 'West'),
(1, 7, '2025-01-20', 10, 18500.00, 3.00, 'West'),
(2, 2, '2025-01-22', 50, 899.00, 0.00, 'North'),
(3, 5, '2025-02-01', 200, 320.00, 2.00, 'South'),
(4, 3, '2025-02-05', 15, 8500.00, 0.00, 'South'),
(5, 9, '2025-02-10', 30, 450.00, 0.00, 'East'),
(6, 4, '2025-02-15', 8, 22000.00, 5.00, 'West'),
(7, 1, '2025-03-01', 12, 75000.00, 8.00, 'South'),
(8, 6, '2025-03-05', 25, 1200.00, 0.00, 'West'),
(9, 10, '2025-03-10', 40, 2499.00, 2.00, 'North'),
(10, 2, '2025-03-15', 100, 899.00, 5.00, 'North'),
(11, 7, '2025-04-01', 6, 18500.00, 0.00, 'West'),
(12, 5, '2025-04-05', 150, 320.00, 0.00, 'North'),
(1, 4, '2025-04-10', 4, 22000.00, 3.00, 'West'),
(3, 1, '2025-04-15', 3, 75000.00, 0.00, 'South'),
(4, 8, '2025-05-01', 2, 6500.00, 0.00, 'South'),
(6, 3, '2025-05-05', 20, 8500.00, 5.00, 'West'),
(7, 5, '2025-05-10', 300, 320.00, 1.00, 'South'),
(9, 1, '2025-05-15', 8, 75000.00, 10.00, 'North'),
(2, 10, '2025-06-01', 55, 2499.00, 0.00, 'North'),
(5, 7, '2025-06-05', 14, 18500.00, 2.00, 'East'),
(8, 3, '2025-06-10', 10, 8500.00, 0.00, 'West'),
(11, 6, '2025-06-12', 40, 1200.00, 0.00, 'West'),
(12, 2, '2025-06-14', 75, 899.00, 3.00, 'North');

INSERT INTO purchases (vendor_id, product_id, purchase_date, quantity, unit_cost) VALUES
(1, 1, '2025-01-01', 30, 58000.00),
(1, 7, '2025-01-01', 25, 13200.00),
(2, 2, '2025-01-05', 200, 450.00),
(2, 5, '2025-01-05', 400, 180.00),
(3, 3, '2025-01-10', 40, 5200.00),
(3, 4, '2025-01-10', 15, 14000.00),
(4, 6, '2025-02-01', 100, 750.00),
(4, 9, '2025-02-01', 60, 220.00),
(1, 10, '2025-03-01', 80, 1400.00),
(2, 8, '2025-03-15', 10, 4100.00);
