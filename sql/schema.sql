-- ============================================================================
-- Amazon India Analytics Database Schema
-- Complete database structure for e-commerce analytics
-- ============================================================================

-- ============================================================================
-- 1. TRANSACTIONS TABLE (Main transaction data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    order_month INTEGER,
    order_quarter INTEGER,
    order_year INTEGER,
    product_name TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    brand TEXT,
    product_rating REAL,
    original_price_inr REAL NOT NULL,
    discount_percent REAL DEFAULT 0,
    final_amount_inr REAL NOT NULL,
    delivery_charges REAL DEFAULT 0,
    customer_city TEXT NOT NULL,
    customer_state TEXT,
    age_group TEXT,
    is_prime_member BOOLEAN DEFAULT 0,
    payment_method TEXT,
    delivery_days INTEGER,
    return_status TEXT,
    return_reason TEXT,
    customer_rating REAL,
    is_festival_sale BOOLEAN DEFAULT 0,
    festival_name TEXT,
    customer_spending_tier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indices for transactions table
CREATE INDEX idx_transactions_order_date ON transactions(order_date);
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_product_id ON transactions(product_id);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_city ON transactions(customer_city);
CREATE INDEX idx_transactions_state ON transactions(customer_state);
CREATE INDEX idx_transactions_payment_method ON transactions(payment_method);
CREATE INDEX idx_transactions_year_month ON transactions(order_year, order_month);


-- ============================================================================
-- 2. PRODUCTS TABLE (Product master data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    brand TEXT NOT NULL,
    base_price_2015 REAL,
    current_price REAL,
    weight_kg REAL,
    rating REAL,
    review_count INTEGER DEFAULT 0,
    is_prime_eligible BOOLEAN DEFAULT 1,
    launch_year INTEGER,
    model TEXT,
    product_status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category) REFERENCES categories(category_id)
);

-- Indices for products table
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_status ON products(product_status);
CREATE UNIQUE INDEX idx_products_name_brand ON products(product_name, brand);


-- ============================================================================
-- 3. CUSTOMERS TABLE (Customer master data with aggregations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_city TEXT NOT NULL,
    customer_state TEXT,
    age_group TEXT,
    registration_date DATE,
    total_purchases INTEGER DEFAULT 0,
    total_spending REAL DEFAULT 0,
    is_prime_member BOOLEAN DEFAULT 0,
    prime_signup_date DATE,
    first_purchase_date DATE,
    last_purchase_date DATE,
    customer_segment TEXT,
    customer_lifetime_value REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for customers table
CREATE INDEX idx_customers_city ON customers(customer_city);
CREATE INDEX idx_customers_state ON customers(customer_state);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_prime_member ON customers(is_prime_member);
CREATE INDEX idx_customers_age_group ON customers(age_group);


-- ============================================================================
-- 4. CATEGORIES TABLE (Product categories hierarchy)
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    subcategory_name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample categories insert
INSERT OR IGNORE INTO categories (category_name, subcategory_name) VALUES
    ('Electronics', 'Computers'),
    ('Electronics', 'Mobile'),
    ('Electronics', 'Accessories'),
    ('Home & Kitchen', 'Furniture'),
    ('Home & Kitchen', 'Bedding'),
    ('Fashion', 'Men'),
    ('Fashion', 'Women'),
    ('Fashion', 'Kids'),
    ('Books', 'Fiction'),
    ('Books', 'Non-Fiction'),
    ('Beauty & Personal Care', 'Skin Care'),
    ('Beauty & Personal Care', 'Hair Care'),
    ('Sports & Outdoors', 'Sports Equipment'),
    ('Sports & Outdoors', 'Outdoor Gear'),
    ('Toys & Games', 'Educational'),
    ('Toys & Games', 'Action Figures'),
    ('Grocery', 'Fresh'),
    ('Grocery', 'Packaged');


-- ============================================================================
-- 5. TIME DIMENSION TABLE (Date dimension for time-based analysis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_dimension (
    date_id INTEGER PRIMARY KEY,
    calendar_date DATE UNIQUE,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    week_of_year INTEGER,
    day_of_week INTEGER,
    day_name TEXT,
    month_name TEXT,
    is_weekend BOOLEAN,
    is_festival BOOLEAN DEFAULT 0,
    festival_name TEXT,
    fiscal_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for time dimension
CREATE INDEX idx_time_date ON time_dimension(calendar_date);
CREATE INDEX idx_time_year_month ON time_dimension(year, month);
CREATE INDEX idx_time_festival ON time_dimension(is_festival);


-- ============================================================================
-- 6. DAILY AGGREGATIONS TABLE (Pre-aggregated daily metrics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS daily_aggregations (
    aggregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    aggregation_date DATE UNIQUE,
    total_revenue REAL,
    total_orders INTEGER,
    total_customers INTEGER,
    avg_order_value REAL,
    unique_products_sold INTEGER,
    total_discount_given REAL,
    returns_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_daily_agg_date ON daily_aggregations(aggregation_date);


-- ============================================================================
-- 7. MONTHLY AGGREGATIONS TABLE (Pre-aggregated monthly metrics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS monthly_aggregations (
    aggregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    month INTEGER,
    total_revenue REAL,
    total_orders INTEGER,
    total_customers INTEGER,
    avg_order_value REAL,
    unique_products_sold INTEGER,
    growth_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month)
);

CREATE INDEX idx_monthly_agg_year_month ON monthly_aggregations(year, month);


-- ============================================================================
-- 8. CUSTOMER SEGMENT TABLE (RFM Segmentation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    recency_score INTEGER,
    frequency_score INTEGER,
    monetary_score INTEGER,
    rfm_segment TEXT,
    segment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_segment_customer_id ON customer_segments(customer_id);
CREATE INDEX idx_segment_rfm_segment ON customer_segments(rfm_segment);


-- ============================================================================
-- 9. PRODUCT PERFORMANCE TABLE (Aggregated product metrics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    product_name TEXT,
    category TEXT,
    brand TEXT,
    total_units_sold INTEGER,
    total_revenue REAL,
    avg_customer_rating REAL,
    return_count INTEGER,
    return_rate REAL,
    performance_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_perf_product_id ON product_performance(product_id);
CREATE INDEX idx_perf_date ON product_performance(performance_date);


-- ============================================================================
-- 10. GEOGRAPHIC ANALYSIS TABLE (City and state-level aggregations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS geographic_analysis (
    geo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    state TEXT,
    tier TEXT,
    total_revenue REAL,
    total_orders INTEGER,
    total_customers INTEGER,
    avg_order_value REAL,
    analysis_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, analysis_date)
);

CREATE INDEX idx_geo_city ON geographic_analysis(city);
CREATE INDEX idx_geo_state ON geographic_analysis(state);
CREATE INDEX idx_geo_tier ON geographic_analysis(tier);


-- ============================================================================
-- 11. PAYMENT ANALYSIS TABLE (Payment method trends)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payment_analysis (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_method TEXT,
    transaction_date DATE,
    transaction_count INTEGER,
    total_amount REAL,
    avg_amount REAL,
    unique_customers INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(payment_method, transaction_date)
);

CREATE INDEX idx_payment_method ON payment_analysis(payment_method);
CREATE INDEX idx_payment_date ON payment_analysis(transaction_date);


-- ============================================================================
-- 12. FESTIVAL ANALYSIS TABLE (Festival sales tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS festival_analysis (
    festival_id INTEGER PRIMARY KEY AUTOINCREMENT,
    festival_name TEXT,
    festival_year INTEGER,
    festival_start_date DATE,
    festival_end_date DATE,
    pre_festival_revenue REAL,
    festival_revenue REAL,
    post_festival_revenue REAL,
    festival_total_orders INTEGER,
    avg_discount_percent REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(festival_name, festival_year)
);

CREATE INDEX idx_festival_name ON festival_analysis(festival_name);
CREATE INDEX idx_festival_year ON festival_analysis(festival_year);


-- ============================================================================
-- View: Monthly Revenue Summary
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_monthly_revenue AS
SELECT 
    order_year,
    order_month,
    SUM(final_amount_inr) as total_revenue,
    COUNT(DISTINCT transaction_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(final_amount_inr) as avg_order_value
FROM transactions
GROUP BY order_year, order_month
ORDER BY order_year, order_month;


-- ============================================================================
-- View: Category Performance
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_category_performance AS
SELECT 
    category,
    SUM(final_amount_inr) as total_revenue,
    COUNT(transaction_id) as total_orders,
    AVG(final_amount_inr) as avg_order_value,
    AVG(customer_rating) as avg_customer_rating,
    COUNT(DISTINCT product_id) as unique_products
FROM transactions
GROUP BY category
ORDER BY total_revenue DESC;


-- ============================================================================
-- View: Geographic Revenue Analysis
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_geographic_revenue AS
SELECT 
    customer_city,
    customer_state,
    SUM(final_amount_inr) as city_revenue,
    COUNT(DISTINCT transaction_id) as city_orders,
    COUNT(DISTINCT customer_id) as city_customers
FROM transactions
GROUP BY customer_city, customer_state
ORDER BY city_revenue DESC;


-- ============================================================================
-- View: Prime vs Non-Prime Analysis
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_prime_analysis AS
SELECT 
    is_prime_member,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(transaction_id) as total_orders,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_order_value
FROM transactions
GROUP BY is_prime_member;


-- ============================================================================
-- View: Payment Method Analysis
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_payment_analysis AS
SELECT 
    payment_method,
    COUNT(transaction_id) as total_transactions,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_amount,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
GROUP BY payment_method
ORDER BY total_revenue DESC;
