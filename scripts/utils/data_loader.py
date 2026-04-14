"""
Data Loader Module
Provides utilities to load data from database or CSV files for production use
"""

import pandas as pd
import sqlite3
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data from database or cleaned CSV files"""
    
    @staticmethod
    def load_from_csv(csv_path: str) -> pd.DataFrame:
        """
        Load data from cleaned CSV file
        
        Args:
            csv_path: Path to cleaned CSV file
            
        Returns:
            DataFrame with transaction data
        """
        try:
            logger.info(f"Loading data from CSV: {csv_path}")
            df = pd.read_csv(csv_path)
            logger.info(f"Successfully loaded {len(df):,} records from CSV")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise
    
    @staticmethod
    def load_from_database(db_path: str, query: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from SQLite database
        
        Args:
            db_path: Path to SQLite database
            query: Optional custom SQL query
            
        Returns:
            DataFrame with transaction data
        """
        try:
            logger.info(f"Connecting to database: {db_path}")
            
            if not Path(db_path).exists():
                raise FileNotFoundError(f"Database not found: {db_path}")
            
            conn = sqlite3.connect(db_path)
            
            if query is None:
                query = "SELECT * FROM transactions LIMIT 1000000"  # Load all transactions
            
            logger.info(f"Executing query: {query[:50]}...")
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Successfully loaded {len(df):,} records from database")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
            raise
    
    @staticmethod
    def load_data(db_path: str, csv_path: Optional[str] = None, 
                  use_database: bool = True) -> pd.DataFrame:
        """
        Load data from either database or CSV (fallback)
        
        Args:
            db_path: Path to database
            csv_path: Path to CSV (fallback)
            use_database: Whether to try database first
            
        Returns:
            DataFrame with transaction data
        """
        if use_database:
            try:
                return DataLoader.load_from_database(db_path)
            except Exception as e:
                logger.warning(f"Database loading failed: {e}. Falling back to CSV...")
                if csv_path and Path(csv_path).exists():
                    return DataLoader.load_from_csv(csv_path)
                raise
        else:
            if csv_path and Path(csv_path).exists():
                return DataLoader.load_from_csv(csv_path)
            else:
                return DataLoader.load_from_database(db_path)
    
    @staticmethod
    def get_database_stats(db_path: str) -> dict:
        """
        Get basic statistics about database
        
        Args:
            db_path: Path to database
            
        Returns:
            Dictionary with database stats
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            stats = {"total_tables": len(tables), "tables": []}
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                stats["tables"].append({"name": table_name, "rows": row_count})
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
