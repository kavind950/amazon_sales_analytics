"""
SQL Database Integration Module
Creates database schema and manages data loading for analytics
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """Manages database operations for Amazon India analytics"""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = None
        self.Session = None
        
    def create_connection(self):
        """Create database engine and session"""
        try:
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Database connection established: {self.database_url}")
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def load_data_to_database(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace'):
        """
        Load DataFrame to database table
        
        Args:
            df: Pandas DataFrame
            table_name: Target table name
            if_exists: 'replace', 'append', or 'fail'
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load data to {table_name}: {e}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_table_stats(self, table_name: str) -> dict:
        """
        Get statistics for a table
        
        Args:
            table_name: Table name
            
        Returns:
            Dictionary with table statistics
        """
        try:
            query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            result = self.execute_query(query)
            row_count = result['row_count'][0]
            
            return {
                'table_name': table_name,
                'row_count': row_count
            }
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return None


# SQL CREATE TABLE Statements
CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    order_month INTEGER,
    order_quarter INTEGER,
    order_year INTEGER,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    product_rating REAL,
    original_price_inr REAL,
    discount_percent REAL,
    final_amount_inr REAL,
    delivery_charges REAL,
    customer_city TEXT,
    customer_state TEXT,
    age_group TEXT,
    is_prime_member BOOLEAN,
    payment_method TEXT,
    delivery_days INTEGER,
    return_status TEXT,
    customer_rating REAL,
    is_festival_sale BOOLEAN,
    festival_name TEXT,
    customer_spending_tier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_order_date ON transactions(order_date);
CREATE INDEX idx_customer_id ON transactions(customer_id);
CREATE INDEX idx_product_id ON transactions(product_id);
CREATE INDEX idx_category ON transactions(category);
CREATE INDEX idx_city ON transactions(customer_city);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    base_price_2015 REAL,
    weight_kg REAL,
    rating REAL,
    is_prime_eligible BOOLEAN,
    launch_year INTEGER,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_category ON products(category);
CREATE INDEX idx_brand ON products(brand);
"""

CREATE_CUSTOMERS_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_city TEXT,
    customer_state TEXT,
    age_group TEXT,
    total_purchases INTEGER,
    total_spending REAL,
    is_prime_member BOOLEAN,
    first_purchase_date DATE,
    last_purchase_date DATE,
    customer_segment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_city ON customers(customer_city);
CREATE INDEX idx_state ON customers(customer_state);
CREATE INDEX idx_segment ON customers(customer_segment);
"""

CREATE_TIME_DIMENSION_TABLE = """
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
    is_festival BOOLEAN,
    festival_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_date ON time_dimension(calendar_date);
CREATE INDEX idx_year_month ON time_dimension(year, month);
"""

CREATE_DAILY_AGGREGATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS daily_aggregations (
    aggregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    total_revenue REAL,
    total_orders INTEGER,
    total_customers INTEGER,
    avg_order_value REAL,
    unique_products_sold INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agg_date ON daily_aggregations(date);
"""


# Core SQL Queries for Analytics
ANALYTICS_QUERIES = {
    'monthly_revenue': """
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
    """,
    
    'category_performance': """
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
    """,
    
    'customer_segmentation': """
    SELECT 
        customer_spending_tier,
        COUNT(DISTINCT customer_id) as unique_customers,
        SUM(final_amount_inr) as total_revenue,
        AVG(final_amount_inr) as avg_order_value,
        COUNT(transaction_id) as total_orders
    FROM transactions
    GROUP BY customer_spending_tier;
    """,
    
    'geographic_analysis': """
    SELECT 
        customer_city,
        customer_state,
        SUM(final_amount_inr) as city_revenue,
        COUNT(DISTINCT transaction_id) as city_orders,
        COUNT(DISTINCT customer_id) as city_customers
    FROM transactions
    GROUP BY customer_city, customer_state
    ORDER BY city_revenue DESC;
    """,
    
    'payment_method_analysis': """
    SELECT 
        payment_method,
        COUNT(transaction_id) as total_transactions,
        SUM(final_amount_inr) as total_revenue,
        AVG(final_amount_inr) as avg_transaction_value,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM transactions
    GROUP BY payment_method
    ORDER BY total_revenue DESC;
    """,
    
    'prime_vs_non_prime': """
    SELECT 
        is_prime_member,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(transaction_id) as total_orders,
        SUM(final_amount_inr) as total_revenue,
        AVG(final_amount_inr) as avg_order_value
    FROM transactions
    GROUP BY is_prime_member;
    """,
    
    'festival_impact': """
    SELECT 
        festival_name,
        is_festival_sale,
        COUNT(transaction_id) as total_orders,
        SUM(final_amount_inr) as total_revenue,
        AVG(final_amount_inr) as avg_order_value,
        AVG(discount_percent) as avg_discount
    FROM transactions
    WHERE is_festival_sale = 1
    GROUP BY festival_name
    ORDER BY total_revenue DESC;
    """,
    
    'product_performance': """
    SELECT 
        product_id,
        product_name,
        category,
        brand,
        COUNT(transaction_id) as units_sold,
        SUM(final_amount_inr) as total_revenue,
        AVG(customer_rating) as avg_customer_rating,
        COUNT(CASE WHEN return_status IS NOT NULL THEN 1 END) as return_count
    FROM transactions
    GROUP BY product_id
    ORDER BY total_revenue DESC
    LIMIT 100;
    """,
    
    'delivery_performance': """
    SELECT 
        customer_city,
        AVG(delivery_days) as avg_delivery_days,
        COUNT(transaction_id) as total_orders,
        COUNT(CASE WHEN delivery_days > 5 THEN 1 END) as delayed_orders,
        ROUND(100.0 * COUNT(CASE WHEN delivery_days > 5 THEN 1 END) / COUNT(*), 2) as delay_percentage
    FROM transactions
    GROUP BY customer_city
    ORDER BY avg_delivery_days DESC;
    """,
    
    'customer_lifetime_value': """
    SELECT 
        customer_id,
        COUNT(transaction_id) as purchase_count,
        SUM(final_amount_inr) as total_spending,
        AVG(final_amount_inr) as avg_order_value,
        MIN(order_date) as first_purchase,
        MAX(order_date) as last_purchase,
        is_prime_member
    FROM transactions
    GROUP BY customer_id
    ORDER BY total_spending DESC;
    """
}


def setup_database(database_url: str, drop_existing: bool = False):
    """
    Setup database with all tables and indices
    
    Args:
        database_url: SQLAlchemy database URL
        drop_existing: Whether to drop existing tables
    """
    manager = DatabaseManager(database_url)
    manager.create_connection()
    
    if drop_existing:
        logger.warning("Dropping existing tables...")
        manager.drop_tables()
    
    manager.create_tables()
    
    return manager


def run_sql_file(manager: DatabaseManager, sql_file_path: str):
    """
    Execute SQL commands from file
    
    Args:
        manager: DatabaseManager instance
        sql_file_path: Path to SQL file
    """
    try:
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Split and execute each statement
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                manager.engine.execute(statement)
        
        logger.info(f"SQL file executed: {sql_file_path}")
    except Exception as e:
        logger.error(f"Failed to execute SQL file: {e}")
        raise


if __name__ == "__main__":
    print("Database Integration Module")
    print("Import DatabaseManager to use database operations")
