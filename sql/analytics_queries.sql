-- ============================================================================
-- Amazon India Analytics - Core Analytics Queries
-- Ready-to-use SQL queries for business intelligence
-- ============================================================================

-- ============================================================================
-- 1. REVENUE ANALYTICS QUERIES
-- ============================================================================

-- Monthly Revenue with Growth Rate
SELECT 
    order_year,
    order_month,
    SUM(final_amount_inr) as monthly_revenue,
    COUNT(DISTINCT transaction_id) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(final_amount_inr) as avg_order_value,
    LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year, order_month) as prev_month_revenue
FROM transactions
GROUP BY order_year, order_month
ORDER BY order_year DESC, order_month DESC;

-- Annual Revenue Summary
SELECT 
    order_year,
    SUM(final_amount_inr) as annual_revenue,
    COUNT(DISTINCT transaction_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(final_amount_inr) as avg_order_value,
    ROUND(100.0 * (SUM(final_amount_inr) - LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year)) / LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year), 2) as yoy_growth_percent
FROM transactions
GROUP BY order_year
ORDER BY order_year DESC;

-- Revenue by Category with Performance Metrics
SELECT 
    category,
    SUM(final_amount_inr) as total_revenue,
    COUNT(DISTINCT transaction_id) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(final_amount_inr) as avg_order_value,
    AVG(discount_percent) as avg_discount_percent,
    AVG(customer_rating) as avg_customer_rating,
    COUNT(DISTINCT product_id) as unique_products
FROM transactions
GROUP BY category
ORDER BY total_revenue DESC;

-- ============================================================================
-- 2. CUSTOMER ANALYTICS QUERIES
-- ============================================================================

-- Customer Segmentation by RFM
SELECT 
    customer_id,
    MAX(order_date) as last_purchase_date,
    COUNT(DISTINCT transaction_id) as purchase_frequency,
    SUM(final_amount_inr) as total_monetary_value,
    CAST((julianday('now') - julianday(MAX(order_date))) as INTEGER) as recency_days,
    CASE 
        WHEN SUM(final_amount_inr) > (SELECT AVG(total_spending) FROM (
            SELECT SUM(final_amount_inr) as total_spending FROM transactions GROUP BY customer_id
        )) THEN 'High Value'
        ELSE 'Regular Value'
    END as customer_segment
FROM transactions
GROUP BY customer_id
ORDER BY total_monetary_value DESC;

-- Prime Member Analysis
SELECT 
    is_prime_member,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT transaction_id) as order_count,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_order_value,
    AVG(customer_rating) as avg_satisfaction,
    AVG(delivery_days) as avg_delivery_days,
    SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) as return_count,
    ROUND(100.0 * SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as return_rate_percent
FROM transactions
GROUP BY is_prime_member;

-- Top Customers by Lifetime Value
SELECT 
    customer_id,
    COUNT(DISTINCT transaction_id) as total_purchases,
    SUM(final_amount_inr) as lifetime_value,
    MIN(order_date) as first_purchase_date,
    MAX(order_date) as last_purchase_date,
    ROUND(CAST((julianday(MAX(order_date)) - julianday(MIN(order_date))) as REAL) / 365, 1) as customer_age_years,
    COUNT(DISTINCT category) as categories_purchased
FROM transactions
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 100;

-- ============================================================================
-- 3. GEOGRAPHIC ANALYTICS
-- ============================================================================

-- City-wise Revenue Performance
SELECT 
    customer_city,
    customer_state,
    SUM(final_amount_inr) as city_revenue,
    COUNT(DISTINCT transaction_id) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(final_amount_inr) as avg_order_value,
    AVG(customer_rating) as avg_rating,
    AVG(delivery_days) as avg_delivery_days
FROM transactions
WHERE customer_city IS NOT NULL
GROUP BY customer_city, customer_state
ORDER BY city_revenue DESC;

-- State-wise Market Analysis
SELECT 
    customer_state,
    SUM(final_amount_inr) as state_revenue,
    COUNT(DISTINCT transaction_id) as order_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT customer_city) as cities_in_state,
    AVG(final_amount_inr) as avg_order_value
FROM transactions
WHERE customer_state IS NOT NULL
GROUP BY customer_state
ORDER BY state_revenue DESC;

-- ============================================================================
-- 4. PRODUCT ANALYTICS
-- ============================================================================

-- Top Products by Revenue
SELECT 
    product_id,
    product_name,
    category,
    brand,
    COUNT(DISTINCT transaction_id) as units_sold,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_selling_price,
    AVG(customer_rating) as avg_rating,
    SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) as return_count,
    ROUND(100.0 * SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as return_rate_percent
FROM transactions
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 50;

-- Category Performance Summary
SELECT 
    category,
    COUNT(DISTINCT product_id) as products_in_category,
    SUM(final_amount_inr) as category_revenue,
    COUNT(DISTINCT transaction_id) as order_count,
    AVG(final_amount_inr) as avg_price,
    AVG(customer_rating) as avg_rating,
    AVG(discount_percent) as avg_discount,
    MIN(order_date) as first_sale_date,
    MAX(order_date) as last_sale_date
FROM transactions
GROUP BY category
ORDER BY category_revenue DESC;

-- ============================================================================
-- 5. PAYMENT & OPERATIONAL ANALYTICS
-- ============================================================================

-- Payment Method Analysis
SELECT 
    payment_method,
    COUNT(DISTINCT transaction_id) as transaction_count,
    SUM(final_amount_inr) as total_value,
    AVG(final_amount_inr) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_users,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) as market_share_percent,
    AVG(customer_rating) as avg_satisfaction
FROM transactions
WHERE payment_method IS NOT NULL
GROUP BY payment_method
ORDER BY total_value DESC;

-- Delivery Performance by City
SELECT 
    customer_city,
    COUNT(DISTINCT transaction_id) as total_orders,
    AVG(delivery_days) as avg_delivery_days,
    MIN(delivery_days) as min_delivery_days,
    MAX(delivery_days) as max_delivery_days,
    SUM(CASE WHEN delivery_days <= 3 THEN 1 ELSE 0 END) as on_time_count,
    ROUND(100.0 * SUM(CASE WHEN delivery_days <= 3 THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percent
FROM transactions
WHERE customer_city IS NOT NULL
GROUP BY customer_city
ORDER BY avg_delivery_days ASC;

-- ============================================================================
-- 6. SEASONAL & PROMOTIONAL ANALYTICS
-- ============================================================================

-- Festival Sales Impact Analysis
SELECT 
    festival_name,
    order_year,
    COUNT(DISTINCT transaction_id) as festival_orders,
    SUM(final_amount_inr) as festival_revenue,
    AVG(final_amount_inr) as avg_order_value,
    AVG(discount_percent) as avg_discount,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
WHERE is_festival_sale = 1 AND festival_name IS NOT NULL
GROUP BY festival_name, order_year
ORDER BY order_year DESC, festival_revenue DESC;

-- Monthly Seasonality Pattern
SELECT 
    order_month,
    COUNT(DISTINCT transaction_id) as order_count,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(customer_rating) as avg_satisfaction
FROM transactions
GROUP BY order_month
ORDER BY order_month;

-- ============================================================================
-- 7. DISCOUNT & PROMOTIONAL EFFECTIVENESS
-- ============================================================================

-- Discount Impact on Sales
SELECT 
    CASE 
        WHEN discount_percent = 0 THEN 'No Discount'
        WHEN discount_percent <= 10 THEN '1-10%'
        WHEN discount_percent <= 25 THEN '11-25%'
        WHEN discount_percent <= 50 THEN '26-50%'
        ELSE '50%+'
    END as discount_range,
    COUNT(DISTINCT transaction_id) as order_count,
    SUM(final_amount_inr) as total_revenue,
    AVG(final_amount_inr) as avg_order_value,
    AVG(customer_rating) as avg_rating,
    SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) as return_count
FROM transactions
GROUP BY discount_range
ORDER BY 
    CASE discount_range
        WHEN 'No Discount' THEN 1
        WHEN '1-10%' THEN 2
        WHEN '11-25%' THEN 3
        WHEN '26-50%' THEN 4
        ELSE 5
    END;

-- ============================================================================
-- 8. CUSTOMER RETENTION & LOYALTY
-- ============================================================================

-- Repeat Purchase Analysis
SELECT 
    repeat_status,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(order_count) as total_orders,
    SUM(total_spending) as total_revenue,
    ROUND(AVG(total_spending), 2) as avg_customer_value
FROM (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as order_count,
        SUM(final_amount_inr) as total_spending,
        CASE 
            WHEN COUNT(DISTINCT transaction_id) = 1 THEN 'One-time'
            WHEN COUNT(DISTINCT transaction_id) BETWEEN 2 AND 5 THEN 'Occasional'
            ELSE 'Regular'
        END as repeat_status
    FROM transactions
    GROUP BY customer_id
)
GROUP BY repeat_status;

-- ============================================================================
-- 9. QUALITY & RETURN ANALYSIS
-- ============================================================================

-- Return Rate by Category
SELECT 
    category,
    COUNT(DISTINCT transaction_id) as total_orders,
    SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) as return_count,
    ROUND(100.0 * SUM(CASE WHEN return_status IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as return_rate_percent,
    AVG(CASE WHEN return_status IS NOT NULL THEN customer_rating ELSE NULL END) as avg_return_rating,
    AVG(CASE WHEN return_status IS NULL THEN customer_rating ELSE NULL END) as avg_nonreturn_rating
FROM transactions
GROUP BY category
ORDER BY return_rate_percent DESC;

-- ============================================================================
-- 10. TIME-BASED TRENDS
-- ============================================================================

-- Growth Rate Analysis (Month-over-Month)
SELECT 
    order_year,
    order_month,
    SUM(final_amount_inr) as monthly_revenue,
    LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year, order_month) as prev_month_revenue,
    ROUND(100.0 * (SUM(final_amount_inr) - LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year, order_month)) / LAG(SUM(final_amount_inr)) OVER (ORDER BY order_year, order_month), 2) as mom_growth_percent
FROM transactions
GROUP BY order_year, order_month
ORDER BY order_year DESC, order_month DESC;

-- Year-over-Year Comparison
SELECT 
    order_year,
    order_month,
    SUM(final_amount_inr) as revenue,
    LAG(SUM(final_amount_inr)) OVER (PARTITION BY order_month ORDER BY order_year) as prev_year_revenue,
    ROUND(100.0 * (SUM(final_amount_inr) - LAG(SUM(final_amount_inr)) OVER (PARTITION BY order_month ORDER BY order_year)) / LAG(SUM(final_amount_inr)) OVER (PARTITION BY order_month ORDER BY order_year), 2) as yoy_growth_percent
FROM transactions
GROUP BY order_year, order_month
ORDER BY order_year DESC, order_month;

-- ============================================================================
-- 11. CUSTOM FILTERING QUERIES
-- ============================================================================

-- High-Value Transactions
SELECT 
    transaction_id,
    customer_id,
    product_name,
    category,
    final_amount_inr,
    order_date,
    customer_city,
    customer_rating
FROM transactions
WHERE final_amount_inr > (SELECT AVG(final_amount_inr) + 2*STDEV(final_amount_inr) FROM transactions)
ORDER BY final_amount_inr DESC;

-- Data Quality Check
SELECT 
    'Null customer_id' as quality_check,
    COUNT(*) as count
FROM transactions
WHERE customer_id IS NULL

UNION ALL

SELECT 
    'Null order_date' as quality_check,
    COUNT(*) as count
FROM transactions
WHERE order_date IS NULL

UNION ALL

SELECT 
    'Invalid ratings' as quality_check,
    COUNT(*) as count
FROM transactions
WHERE customer_rating < 1 OR customer_rating > 5

UNION ALL

SELECT 
    'Negative prices' as quality_check,
    COUNT(*) as count
FROM transactions
WHERE final_amount_inr < 0;

-- ============================================================================
-- 12. EXECUTIVE DASHBOARD QUERIES
-- ============================================================================

-- Key Metrics Summary
SELECT 
    'Total Revenue' as metric,
    CAST(SUM(final_amount_inr) / 1000000 AS CHAR) || ' Million' as value
FROM transactions

UNION ALL

SELECT 
    'Total Orders' as metric,
    COUNT(DISTINCT transaction_id) as value
FROM transactions

UNION ALL

SELECT 
    'Active Customers' as metric,
    COUNT(DISTINCT customer_id) as value
FROM transactions

UNION ALL

SELECT 
    'Avg Order Value' as metric,
    '₹' || CAST(AVG(final_amount_inr) as CHAR) as value
FROM transactions

UNION ALL

SELECT 
    'Avg Customer Rating' as metric,
    CAST(AVG(customer_rating) as CHAR) as value
FROM transactions;

-- ============================================================================
-- USAGE NOTES
-- ============================================================================
-- Run these queries in:
-- 1. SQLite CLI: sqlite3 amazon_india_analytics.db
-- 2. Python: db.execute_query(query)
-- 3. Dashboard database settings
-- 4. Database management tools (DBeaver, SQLiteStudio)
--
-- Customize WHERE clauses to filter by:
-- - Date range: WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
-- - City: WHERE customer_city = 'Mumbai'
-- - Category: WHERE category = 'Electronics'
-- - Prime status: WHERE is_prime_member = 1
-- ============================================================================
