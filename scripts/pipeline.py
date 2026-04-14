"""
Amazon India E-Commerce Analytics - Main Pipeline Orchestrator
==============================================================

This script orchestrates the complete data pipeline:
1. Load raw data
2. Clean and standardize
3. Load into database
4. Generate EDA analysis
5. Prepare for dashboard

Usage:
    python scripts/pipeline.py [--stage all|clean|eda|database]

Author: Data Science Team  
Date: 2025-04-08
"""

import os
import sys
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import json

# Ensure logs directory exists  
Path('logs').mkdir(exist_ok=True)

# Create a custom formatting class that replaces Unicode characters
class ASCIIFormatter(logging.Formatter):
    """Formatter that replaces Unicode characters with ASCII equivalents"""
    def format(self, record):
        # Replace common Unicode symbols with ASCII
        replacements = {
            '✓': '[OK]',
            '✗': '[FAIL]',
            '→': '->',
            '●': '*',
            '○': 'o',
        }
        msg = super().format(record)
        for unicode_char, ascii_char in replacements.items():
            msg = msg.replace(unicode_char, ascii_char)
        return msg

# Configure logging with proper encoding handling
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('logs/pipeline.log', encoding='utf-8')

formatter = ASCIIFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    DATA_RAW_PATH, DATA_PROCESSED_PATH, 
    DATABASE_URL, SCRIPTS_PATH, DB_PATH, REPORTS_PATH
)
from scripts.data_cleaning.data_cleaner import DataCleaningPipeline
from scripts.database.db_manager import DatabaseManager
from scripts.eda.comprehensive_eda_analyzer import ComprehensiveEDAAnalyzer
from scripts.utils.report_generator import ReportGenerator
from scripts.utils.product_processor import ProductProcessor


class PipelineOrchestrator:
    """Main orchestrator for the data pipeline"""
    
    def __init__(self):
        """Initialize the pipeline orchestrator"""
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.stages_completed = []
    
    def verify_directories(self):
        """Verify and create necessary directories"""
        try:
            DATA_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
            self.logger.info("✓ Directory structure verified")
        except Exception as e:
            self.errors.append(f"Directory creation failed: {e}")
            self.logger.error(f"✗ Directory creation failed: {e}")
    
    def create_directories(self):
        """Create necessary directories for pipeline"""
        self.verify_directories()
    
    def load_raw_data(self) -> pd.DataFrame:
        """
        Load raw data files
        
        Returns:
            Combined DataFrame from all year files
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("STAGE 1: LOADING RAW DATA")
            self.logger.info("=" * 60)
            
            all_data = []
            
            # List all transaction files
            transaction_files = list(DATA_RAW_PATH.glob('amazon_india_*.csv'))
            
            if not transaction_files:
                self.logger.warning("No transaction files found. Create sample data or download dataset.")
                return None
            
            for file in sorted(transaction_files):
                try:
                    self.logger.info(f"Loading: {file.name}")
                    df = pd.read_csv(file)
                    all_data.append(df)
                    self.logger.info(f"  → Loaded {len(df):,} records")
                except Exception as e:
                    self.logger.error(f"Failed to load {file.name}: {e}")
                    self.errors.append(f"Failed to load {file.name}: {e}")
            
            if not all_data:
                self.logger.error("No data could be loaded")
                return None
            
            # Combine all data
            raw_df = pd.concat(all_data, ignore_index=True)
            
            self.logger.info(f"✓ Total records loaded: {len(raw_df):,}")
            self.logger.info(f"✓ Memory usage: {raw_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            self.stages_completed.append('data_loading')
            return raw_df
            
        except Exception as e:
            self.errors.append(f"Data loading failed: {e}")
            self.logger.error(f"✗ Data loading failed: {e}")
            return None
    
    def clean_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute data cleaning pipeline
        
        Args:
            raw_df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 2: DATA CLEANING")
            self.logger.info("=" * 60)
            
            self.logger.info(f"Input data shape: {raw_df.shape}")
            self.logger.info(f"Missing values: {raw_df.isnull().sum().sum()}")
            
            # Initialize cleaner
            cleaner = DataCleaningPipeline(raw_df)
            
            # Apply all cleaning operations
            self.logger.info("\nApplying cleaning operations...")
            
            # Clean dates
            if 'order_date' in raw_df.columns:
                cleaner.clean_dates('order_date')
                self.logger.info("✓ Dates cleaned")
            
            # Clean prices
            if 'original_price_inr' in raw_df.columns:
                cleaner.clean_prices('original_price_inr')
                self.logger.info("✓ Original prices cleaned")
            
            if 'final_amount_inr' in raw_df.columns:
                cleaner.clean_prices('final_amount_inr')
                self.logger.info("✓ Final amounts cleaned")
            
            # Clean ratings
            if 'customer_rating' in raw_df.columns:
                cleaner.clean_ratings('customer_rating')
                self.logger.info("✓ Customer ratings cleaned")
            
            # Clean geographic data
            if 'customer_city' in raw_df.columns:
                cleaner.clean_cities('customer_city')
                self.logger.info("✓ Cities cleaned")
            
            # Clean booleans
            boolean_cols = [col for col in ['is_prime_member', 'is_prime_eligible', 'is_festival_sale'] 
                           if col in raw_df.columns]
            if boolean_cols:
                cleaner.clean_booleans(boolean_cols)
                self.logger.info(f"✓ Boolean columns cleaned: {boolean_cols}")
            
            # Clean categories
            if 'category' in raw_df.columns:
                cleaner.clean_categories('category')
                self.logger.info("✓ Categories cleaned")
            
            # Clean delivery days
            if 'delivery_days' in raw_df.columns:
                cleaner.clean_delivery_days('delivery_days')
                self.logger.info("✓ Delivery days cleaned")
            
            # Handle duplicates
            cleaner.handle_duplicates()
            self.logger.info("✓ Duplicates handled")
            
            # Handle outliers
            if 'original_price_inr' in raw_df.columns:
                cleaner.handle_outliers('original_price_inr')
                self.logger.info("✓ Outliers corrected")
            
            # Clean payment methods
            if 'payment_method' in raw_df.columns:
                cleaner.clean_payment_methods('payment_method')
                self.logger.info("✓ Payment methods cleaned")
            
            cleaned_df = cleaner.get_cleaned_data()
            cleaning_report = cleaner.get_cleaning_report()
            
            # Print cleaning summary
            self.logger.info("\nCleaning Summary:")
            self.logger.info(f"Output data shape: {cleaned_df.shape}")
            self.logger.info(f"Records removed: {len(raw_df) - len(cleaned_df):,}")
            self.logger.info(f"Remaining missing values: {cleaned_df.isnull().sum().sum()}")
            
            self.stages_completed.append('data_cleaning')
            return cleaned_df
            
        except Exception as e:
            self.errors.append(f"Data cleaning failed: {e}")
            self.logger.error(f"✗ Data cleaning failed: {e}")
            return None
    
    def save_cleaned_data(self, cleaned_df: pd.DataFrame):
        """Save cleaned data to CSV"""
        try:
            output_file = DATA_PROCESSED_PATH / 'amazon_india_cleaned.csv'
            cleaned_df.to_csv(output_file, index=False)
            self.logger.info(f"✓ Cleaned data saved: {output_file}")
        except Exception as e:
            self.errors.append(f"Failed to save cleaned data: {e}")
            self.logger.error(f"✗ Failed to save cleaned data: {e}")
    
    def process_product_catalog(self):
        """Process and clean product catalog"""
        try:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("PROCESSING PRODUCT CATALOG")
            self.logger.info("=" * 60)
            
            # Initialize processor
            processor = ProductProcessor(
                input_path=str(DATA_RAW_PATH / 'amazon_india_products_catalog.csv'),
                output_path=str(DATA_PROCESSED_PATH / 'amazon_india_products_cleaned.csv')
            )
            
            # Process products
            self.logger.info("Loading and processing product catalog...")
            processor.process_all()
            
            # Get report
            report = processor.get_processing_report()
            self.logger.info(f"✓ Products processed: {report['processing_summary'].get('final_records', 0):,} products")
            self.logger.info(f"✓ Products saved: {report['output_file']}")
            
            self.stages_completed.append('product_processing')
            
        except Exception as e:
            self.errors.append(f"Product processing failed: {e}")
            self.logger.warning(f"⚠ Product processing failed: {e}")

    
    def setup_database(self, cleaned_df: pd.DataFrame):
        """Setup database and load data"""
        try:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 3: DATABASE SETUP")
            self.logger.info("=" * 60)
            
            # Create database manager
            db_manager = DatabaseManager(DATABASE_URL)
            db_manager.create_connection()
            db_manager.create_tables()
            
            # Load transactions
            self.logger.info("Loading data into transactions table...")
            db_manager.load_data_to_database(cleaned_df, 'transactions')
            
            # Get table stats
            stats = db_manager.get_table_stats('transactions')
            self.logger.info(f"✓ Database setup complete: {stats['row_count']:,} records loaded")
            
            self.stages_completed.append('database_setup')
            
        except Exception as e:
            self.errors.append(f"Database setup failed: {e}")
            self.logger.error(f"✗ Database setup failed: {e}")
    
    def generate_eda(self, cleaned_df: pd.DataFrame):
        """Generate comprehensive EDA reports for all 20 questions"""
        try:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 4: EXPLORATORY DATA ANALYSIS (ALL 20 QUESTIONS)")
            self.logger.info("=" * 60)
            
            # Generate dataset summary
            self.logger.info("\nDataset Summary:")
            self.logger.info(f"  Total Records: {len(cleaned_df):,}")
            self.logger.info(f"  Total Columns: {len(cleaned_df.columns)}")
            self.logger.info(f"  Memory Usage: {cleaned_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Initialize comprehensive analyzer
            self.logger.info("\nInitializing comprehensive EDA analyzer...")
            analyzer = ComprehensiveEDAAnalyzer(cleaned_df)
            
            # Initialize report generator
            report_generator = ReportGenerator(str(REPORTS_PATH))
            
            # Define all 20 analyses
            analyses = [
                ('q1_revenue_trend_analysis', 'Q1: Revenue Trend Analysis (2015-2025)'),
                ('q2_seasonal_patterns', 'Q2: Seasonal Sales Patterns'),
                ('q3_rfm_segmentation', 'Q3: Customer RFM Segmentation'),
                ('q4_payment_evolution', 'Q4: Payment Method Evolution'),
                ('q5_category_performance', 'Q5: Category Performance Analysis'),
                ('q6_prime_impact', 'Q6: Prime Membership Impact'),
                ('q7_geographic_analysis', 'Q7: Geographic Analysis'),
                ('q8_festival_impact', 'Q8: Festival Sales Impact'),
                ('q9_customer_rating_patterns', 'Q9: Customer Rating Patterns'),
                ('q10_price_demand_analysis', 'Q10: Price vs Demand Analysis'),
                ('q11_delivery_performance', 'Q11: Delivery Performance'),
                ('q12_return_satisfaction', 'Q12: Return Patterns & Satisfaction'),
                ('q13_discount_effectiveness', 'Q13: Discount Effectiveness'),
                ('q14_revenue_per_customer_clv', 'Q14: Customer Lifetime Value (CLV)'),
                ('q15_category_trends', 'Q15: Category Evolution & Trends'),
                ('q16_monthly_revenue_volatility', 'Q16: Revenue Volatility Analysis'),
                ('q17_top_products_analysis', 'Q17: Top Products & Brand Performance'),
                ('q18_customer_acquisition_retention', 'Q18: Customer Acquisition & Retention'),
                ('q19_customer_frequency_distribution', 'Q19: Customer Frequency Distribution'),
                ('q20_business_health_dashboard', 'Q20: Business Health Executive Dashboard'),
            ]
            
            # Generate all analyses and save reports
            self.logger.info("\nGenerating and saving 20 comprehensive analyses...")
            generated_analyses = []
            failed_analyses = []
            saved_reports = []
            
            for method_name, display_name in analyses:
                try:
                    if hasattr(analyzer, method_name):
                        method = getattr(analyzer, method_name)
                        fig, stats = method()
                        generated_analyses.append((method_name, display_name))
                        
                        # Save figure as PNG (300 DPI)
                        fig_filename = f"{method_name}.png"
                        fig_path = report_generator.session_dir / fig_filename
                        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
                        plt.close(fig)
                        
                        # Save statistics as JSON
                        stats_filename = f"{method_name}_stats.json"
                        stats_path = report_generator.session_dir / stats_filename
                        with open(stats_path, 'w') as f:
                            json.dump(stats, f, indent=2, default=str)
                        
                        saved_reports.append({
                            'analysis': display_name,
                            'figure': str(fig_path),
                            'statistics': str(stats_path)
                        })
                        
                        self.logger.info(f"  [OK] {display_name}")
                    else:
                        failed_analyses.append(f"{display_name} - Method not found")
                        self.logger.warning(f"  [SKIP] {display_name} - Method not found")
                except Exception as e:
                    failed_analyses.append(f"{display_name} - {str(e)}")
                    self.logger.warning(f"  [WARN] {display_name} - {str(e)}")
            
            # Save report index
            report_index = {
                'generated_at': datetime.now().isoformat(),
                'total_analyses': len(generated_analyses),
                'total_failed': len(failed_analyses),
                'reports': saved_reports,
                'dataset_summary': analyzer.generate_summary()
            }
            
            index_path = report_generator.session_dir / "report_index.json"
            with open(index_path, 'w') as f:
                json.dump(report_index, f, indent=2, default=str)
            
            # Generate text summary report
            summary_path = report_generator.session_dir / "REPORT_SUMMARY.txt"
            with open(summary_path, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("AMAZON INDIA ANALYTICS - EDA REPORT SUMMARY\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Reports Location: {report_generator.session_dir}\n\n")
                f.write("ANALYSES GENERATED:\n")
                f.write("-" * 70 + "\n")
                for method_name, display_name in generated_analyses:
                    f.write(f"✓ {display_name}\n")
                f.write("\n")
                
                if failed_analyses:
                    f.write("FAILED ANALYSES:\n")
                    f.write("-" * 70 + "\n")
                    for failed in failed_analyses:
                        f.write(f"✗ {failed}\n")
                    f.write("\n")
                
                summary = analyzer.generate_summary()
                f.write("DATASET OVERVIEW:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Total Records: {summary.get('total_records', 0):,}\n")
                f.write(f"Time Period: {summary.get('time_period', 'N/A')}\n")
                f.write(f"Total Revenue: ₹{summary.get('total_revenue', 0)/1e7:.1f} Crores\n")
                f.write(f"Avg Order Value: ₹{summary.get('avg_order_value', 0):.0f}\n")
                f.write(f"Unique Customers: {summary.get('unique_customers', 0):,}\n")
                f.write(f"Categories: {summary.get('unique_categories', 0)}\n")
            
            # Generate comprehensive summary
            self.logger.info("\n" + "-" * 60)
            self.logger.info(f"✓ Generated {len(generated_analyses)}/20 analyses successfully")
            self.logger.info(f"✓ Saved all reports to: {report_generator.session_dir}")
            
            if failed_analyses:
                self.logger.warning(f"⚠ {len(failed_analyses)} analyses had issues:")
                for failed in failed_analyses:
                    self.logger.warning(f"  • {failed}")
            
            # Get comprehensive summary
            summary = analyzer.generate_summary()
            
            self.logger.info("\nDataset Overview:")
            self.logger.info(f"  Records: {summary.get('total_records', 0):,}")
            self.logger.info(f"  Time Period: {summary.get('time_period', 'N/A')}")
            self.logger.info(f"  Total Revenue: ₹{summary.get('total_revenue', 0)/1e7:.1f} Crores")
            self.logger.info(f"  Avg Order Value: ₹{summary.get('avg_order_value', 0):.0f}")
            self.logger.info(f"  Unique Customers: {summary.get('unique_customers', 0):,}")
            self.logger.info(f"  Categories: {summary.get('unique_categories', 0)}")
            
            self.stages_completed.append('eda_generation')
            
        except Exception as e:
            self.errors.append(f"EDA generation failed: {e}")
            self.logger.error(f"[FAIL] EDA generation failed: {e}")
    
    def print_pipeline_summary(self):
        """Print final pipeline summary"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        
        self.logger.info("\nStages Completed:")
        for i, stage in enumerate(self.stages_completed, 1):
            self.logger.info(f"  {i}. {stage.replace('_', ' ').title()}")
        
        if self.errors:
            self.logger.warning(f"\nWarnings/Errors ({len(self.errors)}):")
            for error in self.errors:
                self.logger.warning(f"  • {error}")
        
        self.logger.info("\n✓ Pipeline execution completed!")
        self.logger.info(f"Output location: {DATA_PROCESSED_PATH}")
        self.logger.info(f"Database location: {DB_PATH}")
        self.logger.info("\nNext steps:")
        self.logger.info("  1. Review cleaned data: data/processed/")
        self.logger.info("  2. Query database: scripts/database/db_manager.py")
        self.logger.info("  3. Launch dashboard: streamlit run dashboard/app.py")
    
    def run_full_pipeline(self):
        """Execute complete data pipeline"""
        try:
            start_time = datetime.now()
            self.logger.info("\nStarting Data Pipeline Execution...")
            self.logger.info(f"Start time: {start_time}")
            
            # Create directories
            self.create_directories()
            
            # Load raw data
            raw_df = self.load_raw_data()
            if raw_df is None:
                self.logger.error("Pipeline stopped: No data loaded")
                return False
            
            # Clean data
            cleaned_df = self.clean_data(raw_df)
            if cleaned_df is None:
                self.logger.error("Pipeline stopped: Cleaning failed")
                return False
            
            # Save cleaned data
            self.save_cleaned_data(cleaned_df)
            
            # Process product catalog
            self.process_product_catalog()
            
            # Setup database
            self.setup_database(cleaned_df)
            
            # Generate comprehensive EDA
            self.generate_eda(cleaned_df)
            
            # Print summary
            self.print_pipeline_summary()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"\nExecution time: {execution_time:.2f} seconds")
            self.logger.info(f"End time: {end_time}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return False


def main():
    """Main entry point"""
    pipeline = PipelineOrchestrator()
    success = pipeline.run_full_pipeline()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
