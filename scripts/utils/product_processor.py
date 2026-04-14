"""
Product Catalog Processor
Handles cleaning and processing of product catalog data
"""

import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProductProcessor:
    """Process and clean product catalog data"""
    
    def __init__(self, input_path: str = None, output_path: str = None):
        """
        Initialize product processor
        
        Args:
            input_path: Path to raw product CSV
            output_path: Path to save processed product CSV
        """
        self.input_path = input_path or r'data\raw\amazon_india_products_catalog.csv'
        self.output_path = output_path or r'data\processed\amazon_india_products_cleaned.csv'
        self.df = None
        self.processing_log = {}
    
    def load_products(self) -> pd.DataFrame:
        """Load product catalog"""
        try:
            self.df = pd.read_csv(self.input_path)
            self.processing_log['loaded_records'] = len(self.df)
            logger.info(f"Loaded {len(self.df):,} product records")
            return self.df
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            raise
    
    def clean_products(self) -> pd.DataFrame:
        """Apply cleaning operations to product data"""
        if self.df is None:
            self.load_products()
        
        initial_count = len(self.df)
        
        # Remove duplicates by product_id
        if 'product_id' in self.df.columns:
            self.df = self.df.drop_duplicates(subset=['product_id'], keep='first')
            self.processing_log['duplicates_removed'] = initial_count - len(self.df)
        
        # Handle missing values
        for col in self.df.columns:
            if col in ['product_name', 'category']:
                # Fill empty names with category info
                if self.df[col].isnull().any():
                    self.df[col] = self.df[col].fillna('Unknown')
        
        # Clean numeric columns
        numeric_cols = ['price', 'rating', 'review_count', 'weight', 'dimensions']
        for col in numeric_cols:
            if col in self.df.columns:
                # Convert to numeric
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Remove rows where product_name is still missing
        if 'product_name' in self.df.columns:
            self.df = self.df[self.df['product_name'].notna() & (self.df['product_name'] != '')]
        
        # Clean product names (strip whitespace, standardize case)
        if 'product_name' in self.df.columns:
            self.df['product_name'] = self.df['product_name'].str.strip().str.title()
        
        # Clean categories
        if 'category' in self.df.columns:
            self.df['category'] = self.df['category'].str.strip().str.title()
        
        # Standardize values
        if 'rating' in self.df.columns:
            # Ensure ratings are between 0-5
            self.df['rating'] = self.df['rating'].clip(0, 5)
        
        self.processing_log['final_records'] = len(self.df)
        self.processing_log['retention_rate'] = (len(self.df) / initial_count * 100) if initial_count > 0 else 100
        
        logger.info(f"Cleaned: {initial_count:,} → {len(self.df):,} records ({self.processing_log['retention_rate']:.1f}% retained)")
        return self.df
    
    def enrich_products(self) -> pd.DataFrame:
        """Add derived columns for analysis"""
        if self.df is None or len(self.df) == 0:
            return self.df
        
        # Calculate price category
        if 'price' in self.df.columns and self.df['price'].notna().any():
            price_median = self.df['price'].median()
            self.df['price_category'] = pd.cut(
                self.df['price'],
                bins=[0, price_median * 0.5, price_median, price_median * 2, float('inf')],
                labels=['Budget', 'Economy', 'Premium', 'Luxury']
            )
        
        # Rating category
        if 'rating' in self.df.columns and self.df['rating'].notna().any():
            self.df['rating_category'] = pd.cut(
                self.df['rating'],
                bins=[0, 2, 3.5, 4.2, 5.01],
                labels=['Poor', 'Average', 'Good', 'Excellent'],
                include_lowest=True
            )
        
        # Product popularity (based on reviews)
        if 'review_count' in self.df.columns and self.df['review_count'].notna().any():
            review_quartiles = self.df['review_count'].quantile([0.25, 0.5, 0.75])
            self.df['popularity'] = pd.cut(
                self.df['review_count'],
                bins=[0, review_quartiles[0.25], review_quartiles[0.5], review_quartiles[0.75], float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        logger.info("Products enriched with derived columns")
        return self.df
    
    def get_statistics(self) -> dict:
        """Generate statistics about processed products"""
        if self.df is None or len(self.df) == 0:
            return {}
        
        stats = {
            'total_products': len(self.df),
            'total_categories': self.df['category'].nunique() if 'category' in self.df.columns else 0,
        }
        
        # Add numeric statistics
        for col in ['price', 'rating', 'review_count', 'weight']:
            if col in self.df.columns and self.df[col].notna().any():
                stats[f'{col}_mean'] = self.df[col].mean()
                stats[f'{col}_median'] = self.df[col].median()
                stats[f'{col}_std'] = self.df[col].std()
        
        # Category distribution
        if 'category' in self.df.columns:
            stats['category_distribution'] = self.df['category'].value_counts().to_dict()
        
        # Price range
        if 'price' in self.df.columns and self.df['price'].notna().any():
            stats['price_range'] = {
                'min': self.df['price'].min(),
                'max': self.df['price'].max(),
                'median': self.df['price'].median()
            }
        
        logger.info(f"Product Statistics: {stats['total_products']} products, {stats['total_categories']} categories")
        return stats
    
    def save_processed(self) -> str:
        """Save processed product data"""
        try:
            # Ensure output directory exists
            output_dir = Path(self.output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save CSV
            self.df.to_csv(self.output_path, index=False)
            logger.info(f"Saved processed products to {self.output_path}")
            
            return self.output_path
        except Exception as e:
            logger.error(f"Failed to save processed products: {e}")
            raise
    
    def process_all(self) -> pd.DataFrame:
        """Complete processing pipeline for products"""
        logger.info("Starting product processing pipeline...")
        
        # Load
        self.load_products()
        
        # Clean
        self.clean_products()
        
        # Enrich
        self.enrich_products()
        
        # Get stats
        stats = self.get_statistics()
        self.processing_log.update(stats)
        
        # Save
        self.save_processed()
        
        logger.info("Product processing pipeline completed")
        return self.df
    
    def get_processing_report(self) -> dict:
        """Get detailed processing report"""
        return {
            'input_file': self.input_path,
            'output_file': self.output_path,
            'processing_summary': self.processing_log,
            'timestamp': pd.Timestamp.now().isoformat()
        }
