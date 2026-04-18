"""
Key Challenges Addressed:
1. Date format standardization (DD/MM/YYYY, DD-MM-YY, YYYY-MM-DD, invalid dates)
2. Price cleaning (symbols, commas, text values)
3. Rating standardization (various formats to 1-5 scale)
4. City name standardization (case variations, alternate names)
5. Boolean column normalization (True/False, Yes/No, 1/0)
6. Category standardization (naming variations)
7. Delivery days cleaning (text formats, outliers)
8. Duplicate transaction detection
9. Outlier detection and correction (decimal point errors)
10. Payment method standardization

"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Tuple, List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """Main data cleaning class handling all 10 cleaning challenges"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the cleaning pipeline
        
        Args:
            df: Raw DataFrame to be cleaned
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_report = {}
        
    # ==================== CHALLENGE 1: Date Format Standardization ====================
    def clean_dates(self, date_column: str, target_format: str = '%Y-%m-%d') -> pd.DataFrame:
        """
        Challenge 1: Handle multiple date formats and invalid dates
        Standardizes all dates to YYYY-MM-DD format
        
        Args:
            date_column: Column name containing dates
            target_format: Target date format
            
        Returns:
            DataFrame with cleaned dates
        """
        logger.info(f"Cleaning date column: {date_column}")
        valid_dates = []
        invalid_count = 0
        
        for date_val in self.df[date_column]:
            if pd.isna(date_val):
                valid_dates.append(pd.NaT)
                continue
            
            date_str = str(date_val).strip()
            parsed_date = None
            
            # Try multiple date formats
            formats = ['%d/%m/%Y', '%d-%m-%y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%Y']
            
            for fmt in formats:
                try:
                    parsed_date = pd.to_datetime(date_str, format=fmt)
                    # Validate date is reasonable (2015-2025)
                    if 2015 <= parsed_date.year <= 2025:
                        break
                    else:
                        parsed_date = None
                except:
                    continue
            
            if parsed_date is None:
                # Try pandas intelligent parsing as last resort
                try:
                    parsed_date = pd.to_datetime(date_str, errors='coerce')
                    if pd.isna(parsed_date) or not (2015 <= parsed_date.year <= 2025):
                        parsed_date = pd.NaT
                        invalid_count += 1
                except:
                    parsed_date = pd.NaT
                    invalid_count += 1
            
            valid_dates.append(parsed_date)
        
        self.df[date_column] = pd.to_datetime(valid_dates)
        self.cleaning_report['dates'] = {
            'total_records': len(self.df),
            'invalid_dates': invalid_count,
            'valid_dates': len(self.df) - invalid_count
        }
        logger.info(f"Date cleaning complete: {invalid_count} invalid dates handled")
        
        return self
    
    # ==================== CHALLENGE 2: Price Cleaning ====================
    def clean_prices(self, price_column: str) -> pd.DataFrame:
        """
        Challenge 2: Handle mixed data types in price column
        Converts various price formats to numeric values
        
        Args:
            price_column: Column name containing prices
            
        Returns:
            DataFrame with cleaned prices
        """
        logger.info(f"Cleaning price column: {price_column}")
        numeric_prices = []
        invalid_count = 0
        
        for price_val in self.df[price_column]:
            if pd.isna(price_val):
                numeric_prices.append(np.nan)
                continue
            
            price_str = str(price_val).strip()
            
            # Skip special values
            if price_str.lower() in ['price on request', 'por', 'contact seller', 'na']:
                numeric_prices.append(np.nan)
                continue
            
            # Remove currency symbols and whitespace
            price_str = price_str.replace('₹', '').replace('Rs', '').replace('Rs.', '').strip()
            
            # Remove commas (Indian numbering system)
            price_str = price_str.replace(',', '')
            
            # Extract numeric value
            try:
                numeric_price = float(re.sub(r'[^\d.]', '', price_str))
                
                # Validate price range (0 to 10M INR)
                if 0 < numeric_price < 10000000:
                    numeric_prices.append(numeric_price)
                else:
                    numeric_prices.append(np.nan)
                    invalid_count += 1
            except:
                numeric_prices.append(np.nan)
                invalid_count += 1
        
        self.df[price_column] = numeric_prices
        self.cleaning_report['prices'] = {
            'total_records': len(self.df),
            'invalid_prices': invalid_count,
            'valid_prices': len(self.df) - invalid_count
        }
        logger.info(f"Price cleaning complete: {invalid_count} invalid prices handled")
        
        return self
    
    # ==================== CHALLENGE 3: Rating Standardization ====================
    def clean_ratings(self, rating_column: str, valid_range: Tuple[float, float] = (1.0, 5.0)) -> pd.DataFrame:
        """
        Challenge 3: Standardize ratings in various formats to 1.0-5.0 scale
        
        Args:
            rating_column: Column name containing ratings
            valid_range: Valid rating range (min, max)
            
        Returns:
            DataFrame with cleaned ratings
        """
        logger.info(f"Cleaning rating column: {rating_column}")
        standardized_ratings = []
        invalid_count = 0
        
        for rating_val in self.df[rating_column]:
            if pd.isna(rating_val):
                # Strategy: Fill with mean rating
                standardized_ratings.append(np.nan)
                continue
            
            rating_str = str(rating_val).strip().lower()
            rating_numeric = None
            
            # Handle various formats: "5.0", "4 stars", "3/5", "2.5/5.0"
            
            # Format: "X stars"
            if 'star' in rating_str:
                rating_str = rating_str.replace('stars', '').replace('star', '').strip()
                try:
                    rating_numeric = float(rating_str)
                except:
                    pass
            
            # Format: "X/5" or "X/5.0"
            elif '/' in rating_str:
                try:
                    parts = rating_str.split('/')
                    numerator = float(parts[0].strip())
                    denominator = float(parts[1].strip() if len(parts) > 1 else 5)
                    rating_numeric = (numerator / denominator) * 5
                except:
                    pass
            
            # Format: numeric
            else:
                try:
                    rating_numeric = float(rating_str)
                except:
                    pass
            
            # Validate rating
            if rating_numeric is not None and valid_range[0] <= rating_numeric <= valid_range[1]:
                standardized_ratings.append(rating_numeric)
            else:
                standardized_ratings.append(np.nan)
                invalid_count += 1
        
        # Fill NaN with median rating
        self.df[rating_column] = standardized_ratings
        median_rating = self.df[rating_column].median()
        self.df[rating_column].fillna(median_rating, inplace=True)
        
        self.cleaning_report['ratings'] = {
            'total_records': len(self.df),
            'invalid_ratings': invalid_count,
            'filled_with_median': self.df[rating_column].isna().sum()
        }
        logger.info(f"Rating cleaning complete: {invalid_count} invalid ratings handled")
        
        return self
    
    # ==================== CHALLENGE 4: Geographic Data Cleaning ====================
    def clean_cities(self, city_column: str, standardization_map: Dict[str, str] = None) -> pd.DataFrame:
        """
        Challenge 4: Standardize city names and handle variations
        
        Args:
            city_column: Column name containing city names
            standardization_map: Dictionary mapping variations to standard names
            
        Returns:
            DataFrame with cleaned cities
        """
        logger.info(f"Cleaning city column: {city_column}")
        
        if standardization_map is None:
            standardization_map = {
                'bangalore': 'Bengaluru',
                'bengaluru': 'Bengaluru',
                'mumbai': 'Mumbai',
                'bombay': 'Mumbai',
                'delhi': 'Delhi',
                'new delhi': 'Delhi',
                'kolkata': 'Kolkata',
                'calcutta': 'Kolkata',
            }
        
        cleaned_cities = []
        invalid_count = 0
        
        for city_val in self.df[city_column]:
            if pd.isna(city_val):
                cleaned_cities.append(city_val)
                invalid_count += 1
                continue
            
            city_str = str(city_val).strip().lower()
            
            # Handle slash-separated variations (e.g., "Bangalore/Bengaluru")
            if '/' in city_str:
                city_str = city_str.split('/')[0].strip().lower()
            
            # Apply standardization map
            standardized = standardization_map.get(city_str, city_str.title())
            cleaned_cities.append(standardized)
        
        self.df[city_column] = cleaned_cities
        self.cleaning_report['cities'] = {
            'total_records': len(self.df),
            'missing_cities': invalid_count,
            'unique_cities': self.df[city_column].nunique()
        }
        logger.info(f"City cleaning complete: {invalid_count} missing cities")
        
        return self
    
    # ==================== CHALLENGE 5: Boolean Columns Standardization ====================
    def clean_booleans(self, boolean_columns: List[str]) -> pd.DataFrame:
        """
        Challenge 5: Standardize boolean columns with mixed formats
        
        Args:
            boolean_columns: List of boolean column names
            
        Returns:
            DataFrame with cleaned boolean columns
        """
        logger.info(f"Cleaning {len(boolean_columns)} boolean columns")
        
        boolean_mapping = {
            'true': True, 'yes': True, 'y': True, '1': True, 1: True,
            'false': False, 'no': False, 'n': False, '0': False, 0: False
        }
        
        for col in boolean_columns:
            if col not in self.df.columns:
                logger.warning(f"Column {col} not found")
                continue
            
            cleaned_booleans = []
            for val in self.df[col]:
                if pd.isna(val):
                    # Strategy: Fill NaN with mode (most common value)
                    cleaned_booleans.append(np.nan)
                else:
                    val_lower = str(val).strip().lower()
                    cleaned_booleans.append(boolean_mapping.get(val_lower, np.nan))
            
            self.df[col] = cleaned_booleans
            # Fill NaN with mode
            mode_val = pd.Series(cleaned_booleans).mode()
            if len(mode_val) > 0:
                self.df[col].fillna(mode_val[0], inplace=True)
        
        self.cleaning_report['booleans'] = {'columns_cleaned': len(boolean_columns)}
        logger.info(f"Boolean cleaning complete for {len(boolean_columns)} columns")
        
        return self
    
    # ==================== CHALLENGE 6: Category Standardization ====================
    def clean_categories(self, category_column: str) -> pd.DataFrame:
        """
        Challenge 6: Standardize product categories with naming variations
        
        Args:
            category_column: Column name containing categories
            
        Returns:
            DataFrame with cleaned categories
        """
        logger.info(f"Cleaning category column: {category_column}")
        
        # Create standardization map from variations to standard names
        category_variations = {
            'electronics': 'Electronics',
            'electronic': 'Electronics',
            'electronicss': 'Electronics',  # Typo fix
            'electronics & accessories': 'Electronics',
            'home & kitchen': 'Home & Kitchen',
            'home': 'Home & Kitchen',
            'fashion': 'Fashion',
            'clothing': 'Fashion',
            'books': 'Books',
            'beauty & personal care': 'Beauty & Personal Care',
            'beauty': 'Beauty & Personal Care',
            'sports & outdoors': 'Sports & Outdoors',
            'sports': 'Sports & Outdoors',
            'toys & games': 'Toys & Games',
            'toys': 'Toys & Games',
            'grocery': 'Grocery'
        }
        
        cleaned_categories = []
        invalid_count = 0
        
        for cat_val in self.df[category_column]:
            if pd.isna(cat_val):
                cleaned_categories.append(np.nan)
                invalid_count += 1
                continue
            
            cat_str = str(cat_val).strip().lower()
            standardized = category_variations.get(cat_str, cat_str.title())
            cleaned_categories.append(standardized)
        
        self.df[category_column] = cleaned_categories
        self.cleaning_report['categories'] = {
            'total_records': len(self.df),
            'missing_categories': invalid_count,
            'unique_categories': self.df[category_column].nunique()
        }
        logger.info(f"Category cleaning complete: {invalid_count} missing categories")
        
        return self
    
    # ==================== CHALLENGE 7: Delivery Days Cleaning ====================
    def clean_delivery_days(self, delivery_column: str) -> pd.DataFrame:
        """
        Challenge 7: Clean delivery days with text entries and outliers
        
        Args:
            delivery_column: Column name containing delivery days
            
        Returns:
            DataFrame with cleaned delivery days
        """
        logger.info(f"Cleaning delivery days column: {delivery_column}")
        
        delivery_mapping = {
            'same day': 0,
            'same-day': 0,
            'next day': 1,
            '1-2 days': 1.5,
            '2-3 days': 2.5,
        }
        
        cleaned_days = []
        invalid_count = 0
        
        for day_val in self.df[delivery_column]:
            if pd.isna(day_val):
                cleaned_days.append(np.nan)
                continue
            
            day_str = str(day_val).strip().lower()
            
            # Check mapping first
            if day_str in delivery_mapping:
                cleaned_days.append(delivery_mapping[day_str])
            else:
                # Try to extract numeric value
                try:
                    numeric_days = float(re.sub(r'[^\d.]', '', day_str))
                    
                    # Validate: delivery should be 0-30 days
                    if 0 <= numeric_days <= 30:
                        cleaned_days.append(numeric_days)
                    else:
                        cleaned_days.append(np.nan)
                        invalid_count += 1
                except:
                    cleaned_days.append(np.nan)
                    invalid_count += 1
        
        self.df[delivery_column] = cleaned_days
        # Fill NaN with median
        median_days = self.df[delivery_column].median()
        self.df[delivery_column].fillna(median_days, inplace=True)
        
        self.cleaning_report['delivery_days'] = {
            'total_records': len(self.df),
            'invalid_days': invalid_count,
            'filled_with_median': median_days
        }
        logger.info(f"Delivery days cleaning complete: {invalid_count} invalid entries")
        
        return self
    
    # ==================== CHALLENGE 8: Duplicate Detection & Handling ====================
    def handle_duplicates(self, subset_columns: List[str] = None) -> pd.DataFrame:
        """
        Challenge 8: Identify and handle duplicate transactions
        
        Args:
            subset_columns: Columns to check for duplicates (customer_id, product_id, date, amount)
            
        Returns:
            DataFrame with handled duplicates
        """
        logger.info("Handling duplicate transactions")
        
        if subset_columns is None:
            subset_columns = ['customer_id', 'product_id', 'order_date', 'final_amount_inr']
        
        # Check which columns exist
        available_cols = [col for col in subset_columns if col in self.df.columns]
        
        if not available_cols:
            logger.warning("No subset columns available for duplicate detection")
            return self
        
        initial_rows = len(self.df)
        
        # Identify duplicates
        duplicate_mask = self.df.duplicated(subset=available_cols, keep='first')
        duplicates_df = self.df[duplicate_mask]
        
        # Analyze duplicates: could be bulk orders or errors
        # Strategy: Keep first occurrence, log suspicious patterns
        
        self.df = self.df[~duplicate_mask]
        
        self.cleaning_report['duplicates'] = {
            'initial_rows': initial_rows,
            'duplicates_found': len(duplicates_df),
            'rows_after_dedup': len(self.df)
        }
        logger.info(f"Duplicate handling complete: {len(duplicates_df)} duplicates removed")
        
        return self
    
    # ==================== CHALLENGE 9: Outlier Detection & Correction ====================
    def handle_outliers(self, price_column: str, method: str = 'iqr') -> pd.DataFrame:
        """
        Challenge 9: Identify and correct price outliers
        
        Args:
            price_column: Column name containing prices
            method: 'iqr' for interquartile range or 'zscore'
            
        Returns:
            DataFrame with corrected outliers
        """
        logger.info(f"Handling outliers in {price_column} using {method} method")
        
        if method == 'iqr':
            Q1 = self.df[price_column].quantile(0.25)
            Q3 = self.df[price_column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
        elif method == 'zscore':
            mean = self.df[price_column].mean()
            std = self.df[price_column].std()
            
            lower_bound = mean - 3 * std
            upper_bound = mean + 3 * std
        
        outliers_mask = (self.df[price_column] < lower_bound) | (self.df[price_column] > upper_bound)
        outliers_count = outliers_mask.sum()
        
        # Correct outliers to upper bound (likely decimal point errors)
        self.df.loc[outliers_mask, price_column] = self.df.loc[outliers_mask, price_column].clip(upper=upper_bound)
        
        self.cleaning_report['outliers'] = {
            'outliers_detected': outliers_count,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'method': method
        }
        logger.info(f"Outlier handling complete: {outliers_count} outliers corrected")
        
        return self
    
    # ==================== CHALLENGE 10: Payment Method Standardization ====================
    def clean_payment_methods(self, payment_column: str, payment_mapping: Dict[str, str] = None) -> pd.DataFrame:
        """
        Challenge 10: Standardize payment method categories
        
        Args:
            payment_column: Column name containing payment methods
            payment_mapping: Dictionary mapping variations to standard categories
            
        Returns:
            DataFrame with cleaned payment methods
        """
        logger.info(f"Cleaning payment methods column: {payment_column}")
        
        if payment_mapping is None:
            payment_mapping = {
                'upi': 'UPI',
                'phonepe': 'UPI',
                'googlepay': 'UPI',
                'bhim': 'UPI',
                'credit card': 'Credit Card',
                'credit_card': 'Credit Card',
                'cc': 'Credit Card',
                'amex': 'Credit Card',
                'debit card': 'Debit Card',
                'debit_card': 'Debit Card',
                'dc': 'Debit Card',
                'cod': 'Cash on Delivery',
                'cash on delivery': 'Cash on Delivery',
                'c.o.d': 'Cash on Delivery',
                'cash': 'Cash on Delivery',
                'amazon pay': 'Digital Wallet',
                'paypal': 'Digital Wallet',
                'wallet': 'Digital Wallet',
                'digital wallet': 'Digital Wallet',
                'net banking': 'Net Banking',
                'internet banking': 'Net Banking',
                'ib': 'Net Banking',
                'bank transfer': 'Net Banking'
            }
        
        cleaned_methods = []
        invalid_count = 0
        
        for method_val in self.df[payment_column]:
            if pd.isna(method_val):
                cleaned_methods.append(np.nan)
                invalid_count += 1
                continue
            
            method_str = str(method_val).strip().lower()
            standardized = payment_mapping.get(method_str, 'Other')
            cleaned_methods.append(standardized)
        
        self.df[payment_column] = cleaned_methods
        
        self.cleaning_report['payment_methods'] = {
            'total_records': len(self.df),
            'missing_methods': invalid_count,
            'unique_methods': self.df[payment_column].nunique()
        }
        logger.info(f"Payment method cleaning complete: {invalid_count} missing methods")
        
        return self
    
    # ==================== Helper Methods ====================
    def get_cleaning_report(self) -> Dict[str, Any]:
        """
        Get comprehensive cleaning report
        
        Returns:
            Dictionary containing cleaning statistics
        """
        return self.cleaning_report
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """Get cleaned DataFrame"""
        return self.df
    
    def compare_before_after(self) -> Dict[str, Any]:
        """
        Compare original vs cleaned data
        
        Returns:
            Dictionary with comparison statistics
        """
        comparison = {
            'original_shape': self.original_df.shape,
            'cleaned_shape': self.df.shape,
            'rows_removed': self.original_df.shape[0] - self.df.shape[0],
            'missing_values_before': self.original_df.isnull().sum().sum(),
            'missing_values_after': self.df.isnull().sum().sum()
        }
        return comparison


def load_and_clean_data(filepath: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load raw data and apply complete cleaning pipeline
    
    Args:
        filepath: Path to raw CSV file
        
    Returns:
        Tuple of (cleaned_df, cleaning_report)
    """
    logger.info(f"Loading data from {filepath}")
    df = pd.read_csv(filepath)
    
    cleaner = DataCleaningPipeline(df)
    
    # Apply cleaning operations
    (cleaner
     .clean_dates('order_date')
     .clean_prices('original_price_inr')
     .clean_prices('final_amount_inr')
     .clean_ratings('customer_rating')
     .clean_cities('customer_city')
     .clean_booleans(['is_prime_member', 'is_prime_eligible', 'is_festival_sale'])
     .clean_categories('category')
     .clean_delivery_days('delivery_days')
     .handle_duplicates()
     .handle_outliers('original_price_inr')
     .clean_payment_methods('payment_method'))
    
    return cleaner.get_cleaned_data(), cleaner.get_cleaning_report()


if __name__ == "__main__":
    # Example usage
    print("Data Cleaning Pipeline Module")
    print("Import this module to use DataCleaningPipeline class")
