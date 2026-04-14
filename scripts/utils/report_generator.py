"""
Report Generation Module
Generates and saves EDA analysis reports
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ReportGenerator:
    """Generate and save EDA reports"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"session_{self.timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        logger.info(f"Report directory: {self.session_dir}")
    
    def save_summary_stats(self, df: pd.DataFrame) -> str:
        """
        Generate and save summary statistics report
        
        Args:
            df: Input dataframe
            
        Returns:
            Path to saved report
        """
        try:
            summary = {
                "report_generated": datetime.now().isoformat(),
                "dataset_info": {
                    "total_records": len(df),
                    "total_columns": len(df.columns),
                    "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
                    "time_period": {
                        "start": str(df['order_date'].min()) if 'order_date' in df.columns else "N/A",
                        "end": str(df['order_date'].max()) if 'order_date' in df.columns else "N/A"
                    }
                },
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "numeric_summary": df.describe().to_dict()
            }
            
            report_file = self.session_dir / "summary_statistics.json"
            with open(report_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Summary statistics saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Failed to save summary statistics: {e}")
            raise
    
    def revenue_analysis_report(self, df: pd.DataFrame) -> str:
        """
        Generate revenue analysis report
        
        Args:
            df: Input dataframe
            
        Returns:
            Path to saved figure
        """
        try:
            if 'order_date' not in df.columns or 'final_amount_inr' not in df.columns:
                logger.warning("Required columns not found for revenue analysis")
                return ""
            
            df['order_year'] = pd.to_datetime(df['order_date']).dt.year
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            
            # Yearly revenue trend
            yearly_revenue = df.groupby('order_year')['final_amount_inr'].agg(['sum', 'count']).reset_index()
            axes[0, 0].plot(yearly_revenue['order_year'], yearly_revenue['sum']/1e7, marker='o', linewidth=2, markersize=8, color='#FF9900')
            axes[0, 0].fill_between(yearly_revenue['order_year'], yearly_revenue['sum']/1e7, alpha=0.3, color='#FF9900')
            axes[0, 0].set_title('Yearly Revenue Trend', fontsize=12, fontweight='bold')
            axes[0, 0].set_xlabel('Year')
            axes[0, 0].set_ylabel('Revenue (Crores INR)')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Monthly revenue
            df['order_month'] = pd.to_datetime(df['order_date']).dt.month
            monthly_revenue = df.groupby('order_month')['final_amount_inr'].sum()
            axes[0, 1].bar(monthly_revenue.index, monthly_revenue.values / 1e6, color='#146EB4', alpha=0.7)
            axes[0, 1].set_title('Revenue by Month', fontsize=12, fontweight='bold')
            axes[0, 1].set_xlabel('Month')
            axes[0, 1].set_ylabel('Revenue (Million INR)')
            axes[0, 1].grid(True, alpha=0.3, axis='y')
            
            # Revenue statistics
            revenue_stats = {
                'Total Revenue': df['final_amount_inr'].sum(),
                'Average Revenue': df['final_amount_inr'].mean(),
                'Median Revenue': df['final_amount_inr'].median(),
                'Max Revenue': df['final_amount_inr'].max(),
                'Min Revenue': df['final_amount_inr'].min()
            }
            axes[1, 0].axis('off')
            stats_text = '\n'.join([f"{k}: ₹{v:,.0f}" for k, v in revenue_stats.items()])
            axes[1, 0].text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Revenue distribution
            axes[1, 1].hist(df['final_amount_inr'], bins=50, color='#28A745', alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Revenue Distribution', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('Price (INR)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            report_file = self.session_dir / "01_revenue_analysis.png"
            plt.savefig(report_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Revenue analysis report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Failed to generate revenue analysis: {e}")
            return ""
    
    def category_analysis_report(self, df: pd.DataFrame) -> str:
        """
        Generate category analysis report
        
        Args:
            df: Input dataframe
            
        Returns:
            Path to saved figure
        """
        try:
            if 'category' not in df.columns or 'final_amount_inr' not in df.columns:
                logger.warning("Required columns not found for category analysis")
                return ""
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            
            # Revenue by category
            cat_revenue = df.groupby('category')['final_amount_inr'].sum().sort_values(ascending=False)
            axes[0, 0].barh(cat_revenue.index, cat_revenue.values, color='#146EB4', alpha=0.7)
            axes[0, 0].set_title('Revenue by Category', fontsize=12, fontweight='bold')
            axes[0, 0].set_xlabel('Revenue (INR)')
            axes[0, 0].grid(True, alpha=0.3, axis='x')
            
            # Order count by category
            cat_orders = df.groupby('category').size().sort_values(ascending=False)
            axes[0, 1].pie(cat_orders.values, labels=cat_orders.index, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Order Distribution by Category', fontsize=12, fontweight='bold')
            
            # Average order value by category
            cat_aov = df.groupby('category')['final_amount_inr'].mean().sort_values(ascending=False)
            axes[1, 0].bar(range(len(cat_aov)), cat_aov.values, color='#FF9900', alpha=0.7)
            axes[1, 0].set_xticks(range(len(cat_aov)))
            axes[1, 0].set_xticklabels(cat_aov.index, rotation=45, ha='right')
            axes[1, 0].set_title('Average Order Value by Category', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylabel('Order Value (INR)')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            
            # Top products
            if 'product_id' in df.columns:
                top_products = df.groupby('product_id')['final_amount_inr'].sum().sort_values(ascending=False).head(10)
                axes[1, 1].barh(range(len(top_products)), top_products.values, color='#28A745', alpha=0.7)
                axes[1, 1].set_yticks(range(len(top_products)))
                axes[1, 1].set_yticklabels(top_products.index)
                axes[1, 1].set_title('Top 10 Products by Revenue', fontsize=12, fontweight='bold')
                axes[1, 1].set_xlabel('Revenue (INR)')
                axes[1, 1].grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            report_file = self.session_dir / "02_category_analysis.png"
            plt.savefig(report_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Category analysis report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Failed to generate category analysis: {e}")
            return ""
    
    def payment_analysis_report(self, df: pd.DataFrame) -> str:
        """
        Generate payment method analysis report
        
        Args:
            df: Input dataframe
            
        Returns:
            Path to saved figure
        """
        try:
            if 'payment_method' not in df.columns:
                logger.warning("Payment method column not found")
                return ""
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Payment method revenue
            payment_revenue = df.groupby('payment_method')['final_amount_inr'].sum().sort_values(ascending=False)
            axes[0].pie(payment_revenue.values, labels=payment_revenue.index, autopct='%1.1f%%', startangle=90)
            axes[0].set_title('Revenue by Payment Method', fontsize=12, fontweight='bold')
            
            # Payment method transaction count
            payment_count = df.groupby('payment_method').size().sort_values(ascending=False)
            axes[1].barh(payment_count.index, payment_count.values, color='#6C5CE7', alpha=0.7)
            axes[1].set_title('Transaction Count by Payment Method', fontsize=12, fontweight='bold')
            axes[1].set_xlabel('Count')
            axes[1].grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            report_file = self.session_dir / "03_payment_analysis.png"
            plt.savefig(report_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Payment analysis report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Failed to generate payment analysis: {e}")
            return ""
    
    def geographic_analysis_report(self, df: pd.DataFrame) -> str:
        """
        Generate geographic analysis report
        
        Args:
            df: Input dataframe
            
        Returns:
            Path to saved figure
        """
        try:
            if 'customer_city' not in df.columns:
                logger.warning("City column not found")
                return ""
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Top cities by revenue
            city_revenue = df.groupby('customer_city')['final_amount_inr'].sum().sort_values(ascending=False).head(10)
            axes[0].barh(city_revenue.index, city_revenue.values, color='#FF6B6B', alpha=0.7)
            axes[0].set_title('Top 10 Cities by Revenue', fontsize=12, fontweight='bold')
            axes[0].set_xlabel('Revenue (INR)')
            axes[0].grid(True, alpha=0.3, axis='x')
            
            # Top cities by order count
            city_orders = df.groupby('customer_city').size().sort_values(ascending=False).head(10)
            axes[1].bar(range(len(city_orders)), city_orders.values, color='#00B894', alpha=0.7)
            axes[1].set_xticks(range(len(city_orders)))
            axes[1].set_xticklabels(city_orders.index, rotation=45, ha='right')
            axes[1].set_title('Top 10 Cities by Order Count', fontsize=12, fontweight='bold')
            axes[1].set_ylabel('Order Count')
            axes[1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            report_file = self.session_dir / "04_geographic_analysis.png"
            plt.savefig(report_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Geographic analysis report saved: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Failed to generate geographic analysis: {e}")
            return ""
    
    def generate_all_reports(self, df: pd.DataFrame) -> dict:
        """
        Generate all available reports
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with report paths
        """
        logger.info("Generating complete report suite...")
        
        reports = {
            "summary_statistics": self.save_summary_stats(df),
            "revenue_analysis": self.revenue_analysis_report(df),
            "category_analysis": self.category_analysis_report(df),
            "payment_analysis": self.payment_analysis_report(df),
            "geographic_analysis": self.geographic_analysis_report(df)
        }
        
        # Save report index
        index_file = self.session_dir / "report_index.json"
        with open(index_file, 'w') as f:
            json.dump({
                "session": self.timestamp,
                "generated_at": datetime.now().isoformat(),
                "reports": {k: str(v) for k, v in reports.items() if v}
            }, f, indent=2)
        
        logger.info(f"All reports generated successfully in: {self.session_dir}")
        return reports
