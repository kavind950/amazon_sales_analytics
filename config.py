"""
Configuration file for Amazon India Analytics Project
Contains all project-level settings, paths, and constants
"""

import os
from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).parent
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
SCRIPTS_PATH = PROJECT_ROOT / "scripts"
DASHBOARD_PATH = PROJECT_ROOT / "dashboard"
SQL_PATH = PROJECT_ROOT / "sql"
DOCUMENTATION_PATH = PROJECT_ROOT / "documentation"
REPORTS_PATH = PROJECT_ROOT / "reports"

# Database Configuration
DB_NAME = "amazon_india_analytics.db"
DB_PATH = PROJECT_ROOT / DB_NAME
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Data Files
PRODUCTS_CATALOG_FILE = "amazon_india_products_catalog.csv"
TRANSACTION_FILES_PATTERN = "amazon_india_{year}.csv"

# Data Quality Settings
MISSING_VALUE_THRESHOLD = 0.5  # 50% threshold for dropping columns
DATE_FORMATS = ['%d/%m/%Y', '%d-%m-%y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%Y']
VALID_DATE_RANGE = ('2015-01-01', '2025-12-31')

# Geographic Data
INDIAN_CITIES = {
    'Metropolitan': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata'],
    'Tier-1': ['Pune', 'Jaipur', 'Lucknow', 'Chandigarh', 'Ahmedabad', 'Indore'],
    'Tier-2': ['Nagpur', 'Vadodara', 'Srinagar', 'Aurangabad', 'Dhanbad'],
    'Tier-3': ['Agra', 'Nashik', 'Faridabad', 'Meerut', 'Visakhapatnam']
}

# City Standardization Mapping
CITY_STANDARDIZATION = {
    'Bangalore': 'Bengaluru',
    'Mumbai': 'Mumbai',
    'Bombay': 'Mumbai',
    'Delhi': 'Delhi',
    'New Delhi': 'Delhi',
    'Kolkata': 'Kolkata',
    'Calcutta': 'Kolkata',
}

# Product Categories
PRODUCT_CATEGORIES = [
    'Electronics',
    'Home & Kitchen',
    'Fashion',
    'Books',
    'Beauty & Personal Care',
    'Sports & Outdoors',
    'Toys & Games',
    'Grocery'
]

# Payment Methods
PAYMENT_METHODS = {
    'UPI': ['UPI', 'PhonePe', 'GooglePay', 'BHIM'],
    'Credit Card': ['Credit Card', 'CREDIT_CARD', 'CC', 'Amex', 'AMEX'],
    'Debit Card': ['Debit Card', 'DEBIT_CARD', 'DC'],
    'COD': ['Cash on Delivery', 'COD', 'C.O.D', 'Cash'],
    'Wallet': ['Amazon Pay', 'PayPal', 'Wallet', 'Digital Wallet'],
    'Net Banking': ['Net Banking', 'Internet Banking', 'IB', 'Bank Transfer']
}

# Rating Scales
VALID_RATING_RANGE = (1.0, 5.0)

# Delivery Performance
EXPECTED_DELIVERY_DAYS = {
    'Standard': 3,
    'Prime': 1,
    'Express': 1,
    'Regular': 4
}

# Festival Dates (2015-2025)
FESTIVAL_CALENDAR = {
    'Christmas': ('12-20', '12-25'),
    'Diwali': ('10-20', '11-15'),  # Approximate
    'New Year': ('12-25', '01-05'),
    'Prime Day': ('07-01', '07-31'),
    'Eid': ('03-01', '03-31'),  # Approximate, varies by year
    'Holi': ('02-01', '03-31'),  # Approximate
}

# Data Cleaning Standards
NUMERIC_COLUMNS_SCALING = {
    'price': (0, 1000000),  # Prices in INR
    'discount': (0, 100),  # Percentage
    'rating': (1.0, 5.0),
    'delivery_days': (0, 30)
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'page_title': 'Amazon India Analytics Dashboard',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Visualization Settings
COLOR_PALETTE = {
    'primary': '#FF9900',  # Amazon Orange
    'secondary': '#146EB4',  # Amazon Blue
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545',
    'info': '#17A2B8'
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = PROJECT_ROOT / 'logs' / 'project.log'

# Project Metadata
PROJECT_NAME = "Amazon India: Decade of Sales Analytics"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "Data Science Team"
PROJECT_DESCRIPTION = "End-to-end e-commerce analytics platform for Amazon India"

# Performance Settings
BATCH_SIZE = 10000  # For database operations
CACHE_TTL = 3600  # Cache time-to-live in seconds
MAX_ROWS_DASHBOARD = 100000  # Maximum rows to load in dashboard
