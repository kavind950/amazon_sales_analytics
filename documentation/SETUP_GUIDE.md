# 🚀 Amazon India Analytics - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Data Setup](#data-setup)
5. [Running the Pipeline](#running-the-pipeline)
6. [Dashboard Usage](#dashboard-usage)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

---

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 4GB (8GB+ recommended for 1M records)
- **Disk Space**: 5GB for data and database
- **Processor**: Dual-core or better

### Software Requirements
- **Python**: 3.8 or higher
- **Git**: For version control (optional)
- **pip**: Python package manager (comes with Python)
- **SQLite3**: Comes with Python

### Knowledge Requirements
- Basic Python programming
- Understanding of pandas DataFrames
- SQL query basics
- Familiarity with command line/terminal

---

## Installation

### Step 1: Clone or Download the Project

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/amazon-india-analytics.git
cd amazon-india-analytics
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to `C:\Users\[YourUsername]\Documents\Amazon_India` (Windows)
   or `~/Documents/Amazon_India` (Mac/Linux)

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
# Navigate to project directory
cd Amazon_India

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd Amazon_India

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal after successful activation.

### Step 3: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

### Step 4: Install Required Packages

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

**Alternative - Install packages individually:**
```bash
pip install pandas==2.1.3
pip install numpy==1.24.3
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install plotly==5.18.0
pip install sqlalchemy==2.0.23
pip install python-dotenv==1.0.0
pip install streamlit==1.28.1
pip install requests==2.31.0
```

### Step 5: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip packages
pip list

# Test imports
python -c "import pandas; import matplotlib; import streamlit; print('All packages installed successfully!')"
```

---

## Configuration

### Step 1: Review Configuration File

Open `config.py` and verify/update:

```python
# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"

# Database
DB_NAME = "amazon_india_analytics.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Data quality settings
MISSING_VALUE_THRESHOLD = 0.5
DATE_FORMATS = ['%d/%m/%Y', '%d-%m-%y', '%Y-%m-%d']

# Visualization
COLOR_PALETTE = {
    'primary': '#FF9900',      # Amazon Orange
    'secondary': '#146EB4',    # Amazon Blue
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545'
}
```

### Step 2: Create .env File (Optional for Production)

Create `.env` file in project root:
```
DATABASE_URL=sqlite:///amazon_india_analytics.db
DEBUG=False
LOG_LEVEL=INFO
```

### Step 3: Create Logs Directory

```bash
mkdir logs
```

---

## Data Setup

### Step 1: Prepare Raw Data Files

The project expects data files in the `data/raw/` directory:

```
Amazon_India/
└── data/
    └── raw/
        ├── amazon_india_2015.csv
        ├── amazon_india_2016.csv
        ├── ...
        ├── amazon_india_2025.csv
        └── amazon_india_products_catalog.csv
```

### Step 2: Data File Format

**Transaction Files (amazon_india_YYYY.csv):**
- Should contain columns described in DATA_DICTIONARY.md
- Expected size: 50K-150K rows per year
- Format: CSV with headers

**Product Catalog (amazon_india_products_catalog.csv):**
- Contains product master data
- Approximately 2000+ unique products
- Key columns: product_id, product_name, category, brand, base_price_2015

### Step 3: Download/Create Sample Data

**Option A: Use Provided Sample Generator**
```bash
python scripts/generate_sample_data.py
```

**Option B: Create Minimal Test Data**
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample data
dates = pd.date_range('2025-01-01', periods=1000, freq='D')
df = pd.DataFrame({
    'transaction_id': [f'TXN_{i:08d}' for i in range(1000)],
    'customer_id': [f'CUST_{np.random.randint(1000, 5000):05d}' for _ in range(1000)],
    'product_id': [f'PROD_{np.random.randint(1, 201):04d}' for _ in range(1000)],
    'order_date': dates,
    'category': np.random.choice(['Electronics', 'Fashion', 'Home & Kitchen'], 1000),
    'final_amount_inr': np.random.uniform(500, 100000, 1000),
    'customer_city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore'], 1000),
    'is_prime_member': np.random.choice([0, 1], 1000),
    'payment_method': np.random.choice(['UPI', 'Credit Card', 'COD'], 1000),
    'customer_rating': np.random.uniform(1, 5, 1000),
})

df.to_csv('data/raw/amazon_india_sample.csv', index=False)
```

### Step 4: Verify Data Files

```bash
# Check data directory
ls -la data/raw/

# Verify file sizes
python -c "import os; [print(f'{f}: {os.path.getsize(f\"data/raw/{f}\")/1024/1024:.1f}MB') for f in os.listdir('data/raw/')]"
```

---

## Running the Pipeline

### Option 1: Run Complete Pipeline (Recommended)

```bash
# With virtual environment activated
python scripts/pipeline.py
```

**What this does:**
1. ✓ Loads all raw data files
2. ✓ Executes complete cleaning pipeline (10 cleaning operations)
3. ✓ Saves cleaned data to `data/processed/`
4. ✓ Creates SQLite database
5. ✓ Loads cleaned data into database
6. ✓ Generates EDA analysis
7. ✓ Creates visualizations
8. ✓ Generates pipeline report

**Expected output:**
```
Started Data Pipeline Execution...
=====================================================
STAGE 1: LOADING RAW DATA
=====================================================
Loading: amazon_india_2025.csv
  → Loaded 125,000 records
✓ Total records loaded: 1,000,000
...
Pipeline execution completed!
```

### Option 2: Run Step-by-Step

**Step 1: Load and Clean Data**
```python
import pandas as pd
from scripts.data_cleaning.data_cleaner import DataCleaningPipeline
from config import DATA_RAW_PATH, DATA_PROCESSED_PATH

# Load raw data
df = pd.read_csv(DATA_RAW_PATH / 'amazon_india_sample.csv')

# Initialize cleaner
cleaner = DataCleaningPipeline(df)

# Apply cleaning operations
cleaner.clean_dates('order_date')
cleaner.clean_prices('final_amount_inr')
cleaner.clean_ratings('customer_rating')

# Save cleaned data
cleaned_df = cleaner.get_cleaned_data()
cleaned_df.to_csv(DATA_PROCESSED_PATH / 'cleaned_data.csv', index=False)
```

**Step 2: Setup Database**
```python
from scripts.database.db_manager import setup_database
from config import DATABASE_URL

db = setup_database(DATABASE_URL)
db.load_data_to_database(cleaned_df, 'transactions')
```

**Step 3: Generate EDA**
```python
from scripts.eda.eda_analyzer import EDAAnalyzer

analyzer = EDAAnalyzer(cleaned_df)
fig, insights = analyzer.revenue_trend_analysis()
```

### Option 3: Run Individual Components

**Just Clean Data:**
```bash
python -c "
from scripts.data_cleaning.data_cleaner import load_and_clean_data
from config import DATA_RAW_PATH
df, report = load_and_clean_data(str(DATA_RAW_PATH / 'amazon_india_2025.csv'))
print(report)
"
```

**Just Analyze:**
```bash
python -c "
import pandas as pd
from scripts.eda.eda_analyzer import generate_eda_summary_report
from config import DATA_PROCESSED_PATH

df = pd.read_csv(DATA_PROCESSED_PATH / 'cleaned_data.csv')
summary = generate_eda_summary_report(df)
for key, value in summary.items():
    print(f'{key}: {value}')
"
```

---

## Dashboard Usage

### Step 1: Start Streamlit Dashboard

```bash
# Ensure virtual environment is activated
streamlit run dashboard/app.py
```

You should see:
```
Local URL: http://localhost:8501
Network URL: http://[Your-IP]:8501
```

### Step 2: Open in Browser

- Automatically opens at `http://localhost:8501`
- Or manually navigate to that URL

### Step 3: Use Dashboard Features

**Navigation:**
- Use tabs at top: Revenue | Customers | Products | Payments | Seasonal | Details
- Use sidebar for advanced filters

**Filters:**
- Year(s): Select one or multiple years
- Category: Filter by product category
- City: Filter by customer city
- Prime Member: Toggle Prime/Non-Prime

**Visualizations:**
- Interactive charts with hover information
- Download charts as PNG
- Responsive design works on tablets

**Data Export:**
- Scroll to "Transaction Details" tab
- View raw data
- Export/Copy data as needed

### Step 4: Common Dashboard Tasks

**View Revenue Trend:**
1. Click "Revenue" tab
2. Observe yearly revenue trend graph
3. Check top categories by revenue

**Analyze Customers:**
1. Click "Customers" tab
2. Compare Prime vs Non-Prime metrics
3. Check top cities

**Check Products:**
1. Click "Products" tab
2. View category distribution
3. Check average ratings

**Seasonal Analysis:**
1. Click "Seasonal" tab
2. View revenue heatmap by month/year
3. Identify peak seasons

---

## Troubleshooting

### Issue 1: Virtual Environment Not Activating

**Error:**
```
'venv\Scripts\activate' is not recognized as an internal or external command
```

**Solution:**
```bash
# Windows - Try PowerShell
.\venv\Scripts\Activate.ps1

# Or set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Package Installation Fails

**Error:**
```
ERROR: Could not install packages due to EnvironmentError
```

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with --no-cache-dir
pip install -r requirements.txt --no-cache-dir

# Install specific version if needed
pip install pandas==2.1.3 --no-binary pandas
```

### Issue 3: Data Files Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/amazon_india_2025.csv'
```

**Solution:**
1. Verify files exist: `ls data/raw/`
2. Check file names match pattern: `amazon_india_YYYY.csv`
3. Ensure files are in correct directory: `Amazon_India/data/raw/`

### Issue 4: Database Lock Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Close any open dashboard instances
# Delete .streamlit/cache folder
rm -rf ~/.streamlit/cache

# Restart pipeline
python scripts/pipeline.py
```

### Issue 5: Dashboard Won't Start

**Error:**
```
StreamlitAPIException: When you use @st.cache_data without specifying a ttl, cached data expires...
```

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart dashboard
streamlit run dashboard/app.py
```

### Issue 6: Out of Memory

**Error:**
```
MemoryError: Unable to allocate X.XX GiB
```

**Solution:**
1. Reduce data size for testing
2. Process data in chunks
3. Increase available RAM or close background apps

### Issue 7: Python Version Mismatch

**Error:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Use specific Python version
python3.10 -m pip install -r requirements.txt
```

---

## Performance Optimization

### Data Processing Speed
1. **Batch Size**: Adjust `BATCH_SIZE` in config.py (default: 10,000)
2. **Parallel Processing**: Use multiprocessing for independent operations
3. **Subset Testing**: Test on 10% of data first

### Database Performance
1. **Enable Indexing**: Indices already created in schema.sql
2. **Query Optimization**: Use aggregation views
3. **Connection Pooling**: Configured in SQLAlchemy

### Dashboard Speed
1. **Caching**: Use `@st.cache_data` decorator
2. **Lazy Loading**: Load data on tab click
3. **Limit Rows**: Default shows 100,000 max rows

### Code Optimization Example
```python
# Slow: Loading all data every time
df = pd.read_csv('data/processed/cleaned_data.csv')

# Fast: Cache the data
@st.cache_data
def load_data():
    return pd.read_csv('data/processed/cleaned_data.csv')

df = load_data()
```

---

## Advanced Setup

### Using PostgreSQL Instead of SQLite

```python
from sqlalchemy import create_engine

# PostgreSQL connection
DATABASE_URL = "postgresql://user:password@localhost/amazon_india_db"

# Update in config.py and db_manager.py
```

### Automated Pipeline Execution

**Windows Task Scheduler:**
```bash
# Create batch file: run_pipeline.bat
@echo off
cd C:\path\to\Amazon_India
call venv\Scripts\activate
python scripts/pipeline.py
```

**Linux Cron Job:**
```bash
# Add to crontab
0 2 * * 0 cd /path/to/Amazon_India && source venv/bin/activate && python scripts/pipeline.py

# Edit crontab
crontab -e
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "dashboard/app.py"]
```

---

## Next Steps After Setup

1. ✓ Review `DATA_DICTIONARY.md` for field definitions
2. ✓ Explore `documentation/BUSINESS_INSIGHTS.md` for key findings
3. ✓ Run sample queries from `sql/` directory
4. ✓ Customize dashboard in `dashboard/app.py`
5. ✓ Add your own analyses in `scripts/eda/`

---

## Getting Help

**Documentation:**
- README.md - Project overview
- DATA_DICTIONARY.md - Field definitions
- Individual script docstrings - Function help

**Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Test Data:**
```bash
python -c "
import pandas as pd
from config import DATA_PROCESSED_PATH

df = pd.read_csv(DATA_PROCESSED_PATH / 'cleaned_data.csv')
print(df.info())
print(df.describe())
print(df.head())
"
```

---

**Last Updated**: March 2025
**Document Version**: 1.0
**For Version**: Project 1.0.0
