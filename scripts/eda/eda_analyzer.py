"""
Exploratory Data Analysis (EDA) Module
Contains all 20 EDA visualization challenges and analytical functions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for all visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


class EDAAnalyzer:
    """Comprehensive EDA analyzer for Amazon India dataset"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize EDA analyzer
        
        Args:
            df: Cleaned DataFrame
        """
        self.df = df
        self.figures = {}
        logger.info(f"EDA Analyzer initialized with {len(df)} records")
    
    # ==================== CHALLENGE 1: Revenue Trend Analysis ====================
    def revenue_trend_analysis(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 1: Comprehensive revenue trend with growth rates and annotations
        """
        logger.info("Generating Revenue Trend Analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Yearly revenue trend
        yearly_revenue = self.df.groupby('order_year')['final_amount_inr'].agg(['sum', 'count']).reset_index()
        yearly_revenue.columns = ['year', 'revenue', 'orders']
        yearly_revenue['growth_rate'] = yearly_revenue['revenue'].pct_change() * 100
        
        ax = axes[0, 0]
        ax.plot(yearly_revenue['year'], yearly_revenue['revenue']/1e6, marker='o', linewidth=2, markersize=8)
        ax.set_title('Yearly Revenue Trend', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Revenue (Million INR)')
        ax.grid(True, alpha=0.3)
        
        # Add growth rate annotations
        for i, row in yearly_revenue.iterrows():
            if pd.notna(row['growth_rate']):
                ax.annotate(f"{row['growth_rate']:.1f}%", 
                           xy=(row['year'], row['revenue']/1e6),
                           xytext=(0, 5), textcoords='offset points',
                           ha='center', fontsize=8)
        
        # Monthly revenue trend
        monthly_revenue = self.df.groupby(['order_year', 'order_month'])['final_amount_inr'].sum().reset_index()
        monthly_revenue['date'] = pd.to_datetime(monthly_revenue[['order_year', 'order_month']].assign(day=1))
        
        ax = axes[0, 1]
        ax.plot(monthly_revenue['date'], monthly_revenue['final_amount_inr']/1e5, color='green', alpha=0.7)
        ax.fill_between(monthly_revenue['date'], monthly_revenue['final_amount_inr']/1e5, alpha=0.3, color='green')
        ax.set_title('Monthly Revenue Trend', fontsize=12, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Revenue (Hundred Thousand INR)')
        ax.grid(True, alpha=0.3)
        
        # Growth rate visualization
        ax = axes[1, 0]
        colors = ['green' if x > 0 else 'red' for x in yearly_revenue['growth_rate'].fillna(0)]
        ax.bar(yearly_revenue['year'].astype(str), yearly_revenue['growth_rate'].fillna(0), color=colors, alpha=0.7)
        ax.set_title('Year-over-Year Growth Rate', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Growth Rate (%)')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Revenue per order
        ax = axes[1, 1]
        avg_order_value = self.df.groupby('order_year')['final_amount_inr'].mean()
        ax.bar(avg_order_value.index, avg_order_value.values, color='skyblue', alpha=0.7)
        ax.set_title('Average Order Value by Year', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Average Order Value (INR)')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        insights = {
            'total_revenue': self.df['final_amount_inr'].sum(),
            'avg_yearly_growth': yearly_revenue['growth_rate'].mean(),
            'best_year': yearly_revenue.loc[yearly_revenue['revenue'].idxmax(), 'year'],
            'best_month': monthly_revenue.loc[monthly_revenue['final_amount_inr'].idxmax(), 'date'].strftime('%Y-%m')
        }
        
        return fig, insights
    
    # ==================== CHALLENGE 2: Seasonal Patterns ====================
    def seasonal_patterns_analysis(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 2: Seasonal patterns with monthly heatmaps and trends
        """
        logger.info("Generating Seasonal Patterns Analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Monthly sales across all years
        monthly_sales = self.df.groupby('order_month')['final_amount_inr'].agg(['sum', 'count', 'mean'])
        
        ax = axes[0, 0]
        monthly_sales['sum'].plot(kind='bar', ax=ax, color='coral', alpha=0.7)
        ax.set_title('Average Monthly Revenue (All Years)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Revenue (INR)')
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Heatmap: Year vs Month
        pivot_data = self.df.pivot_table(values='final_amount_inr', index='order_year', columns='order_month', aggfunc='sum')
        
        ax = axes[0, 1]
        sns.heatmap(pivot_data/1e6, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Revenue (Million INR)'})
        ax.set_title('Revenue Heatmap: Year vs Month', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Year')
        
        # Peak months analysis
        peak_month = monthly_sales['sum'].idxmax()
        low_month = monthly_sales['sum'].idxmin()
        
        ax = axes[1, 0]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        colors = ['red' if i == peak_month else 'blue' if i == low_month else 'skyblue' for i in range(1, 13)]
        ax.bar(range(1, 13), monthly_sales['sum'].values, color=colors, alpha=0.7)
        ax.set_title('Peak vs Low Selling Months', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Revenue (INR)')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Order count by month
        ax = axes[1, 1]
        monthly_orders = self.df.groupby('order_month').size()
        ax.plot(range(1, 13), monthly_orders.values, marker='s', linewidth=2, markersize=8, color='green')
        ax.fill_between(range(1, 13), monthly_orders.values, alpha=0.3, color='green')
        ax.set_title('Order Count by Month', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Orders')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months, rotation=45)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        insights = {
            'peak_month': months[peak_month - 1],
            'low_month': months[low_month - 1],
            'seasonality_ratio': monthly_sales['sum'].max() / monthly_sales['sum'].min()
        }
        
        return fig, insights
    
    # ==================== CHALLENGE 3: Customer Segmentation (RFM) ====================
    def customer_segmentation_rfm(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 3: RFM analysis with customer segmentation
        """
        logger.info("Generating RFM Segmentation Analysis...")
        
        # Calculate RFM metrics
        reference_date = self.df['order_date'].max() + timedelta(days=1)
        
        rfm = self.df.groupby('customer_id').agg({
            'order_date': ('max', lambda x: (reference_date - x).days),  # Recency
            'transaction_id': 'count',  # Frequency
            'final_amount_inr': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Score RFM (1-5 scale)
        rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=False, duplicates='drop')
        rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=False, duplicates='drop')
        rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=False, duplicates='drop')
        
        rfm['RFM_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Recency distribution
        ax = axes[0, 0]
        ax.hist(rfm['recency'], bins=50, color='purple', alpha=0.7, edgecolor='black')
        ax.set_title('Recency Distribution (Days Since Last Purchase)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Days')
        ax.set_ylabel('Customer Count')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Frequency distribution
        ax = axes[0, 1]
        ax.hist(rfm['frequency'], bins=50, color='orange', alpha=0.7, edgecolor='black')
        ax.set_title('Frequency Distribution (Purchase Count)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Purchases')
        ax.set_ylabel('Customer Count')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Monetary distribution
        ax = axes[1, 0]
        ax.hist(rfm['monetary'], bins=50, color='green', alpha=0.7, edgecolor='black')
        ax.set_title('Monetary Distribution (Total Spending)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Total Spending (INR)')
        ax.set_ylabel('Customer Count')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Scatter: Frequency vs Monetary
        ax = axes[1, 1]
        scatter = ax.scatter(rfm['frequency'], rfm['monetary'], c=rfm['recency'], cmap='viridis', alpha=0.6, s=50)
        ax.set_title('Frequency vs Monetary (colored by Recency)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Frequency (Purchase Count)')
        ax.set_ylabel('Monetary (Total Spending INR)')
        plt.colorbar(scatter, ax=ax, label='Recency (Days)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        insights = {
            'total_customers': len(rfm),
            'avg_recency': rfm['recency'].mean(),
            'avg_frequency': rfm['frequency'].mean(),
            'avg_monetary': rfm['monetary'].mean(),
            'high_value_customers': len(rfm[rfm['RFM_score'] >= 12])
        }
        
        return fig, insights
    
    # ==================== CHALLENGE 4: Payment Methods Evolution ====================
    def payment_methods_evolution(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 4: Payment method trends over time
        """
        logger.info("Generating Payment Methods Evolution Analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Payment method market share over time
        payment_yearly = pd.crosstab(self.df['order_year'], self.df['payment_method'], values=self.df['final_amount_inr'], aggfunc='sum')
        payment_yearly_pct = payment_yearly.div(payment_yearly.sum(axis=1), axis=0) * 100
        
        ax = axes[0, 0]
        payment_yearly_pct.plot(kind='area', ax=ax, alpha=0.7)
        ax.set_title('Payment Method Market Share Over Time (%)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Market Share (%)')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True, alpha=0.3)
        
        # Total transactions by payment method
        payment_trans = self.df.groupby('payment_method').size().sort_values(ascending=False)
        
        ax = axes[0, 1]
        payment_trans.plot(kind='barh', ax=ax, color='skyblue', alpha=0.7)
        ax.set_title('Total Transactions by Payment Method', fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Transactions')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Revenue by payment method
        payment_revenue = self.df.groupby('payment_method')['final_amount_inr'].sum().sort_values(ascending=False)
        
        ax = axes[1, 0]
        payment_revenue.plot(kind='bar', ax=ax, color='coral', alpha=0.7)
        ax.set_title('Revenue by Payment Method', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Revenue (INR)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Average transaction value by payment method
        payment_avg = self.df.groupby('payment_method')['final_amount_inr'].mean().sort_values(ascending=False)
        
        ax = axes[1, 1]
        payment_avg.plot(kind='barh', ax=ax, color='lightgreen', alpha=0.7)
        ax.set_title('Average Transaction Value by Payment Method', fontsize=12, fontweight='bold')
        ax.set_xlabel('Average Transaction Value (INR)')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        insights = {
            'most_popular_method': payment_trans.index[0],
            'highest_revenue_method': payment_revenue.index[0],
            'top_3_methods': payment_trans.head(3).index.tolist()
        }
        
        return fig, insights
    
    # ==================== CHALLENGE 5: Category Performance ====================
    def category_performance_analysis(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 5: Comprehensive category analysis
        """
        logger.info("Generating Category Performance Analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Revenue by category
        category_revenue = self.df.groupby('category')['final_amount_inr'].sum().sort_values(ascending=False)
        
        ax = axes[0, 0]
        colors_cat = plt.cm.Set3(np.linspace(0, 1, len(category_revenue)))
        wedges, texts, autotexts = ax.pie(category_revenue.values, labels=category_revenue.index, autopct='%1.1f%%',
                                           colors=colors_cat, startangle=90)
        ax.set_title('Revenue Distribution by Category', fontsize=12, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Orders by category
        category_orders = self.df.groupby('category').size().sort_values(ascending=False)
        
        ax = axes[0, 1]
        category_orders.plot(kind='bar', ax=ax, color='skyblue', alpha=0.7)
        ax.set_title('Order Count by Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Orders')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Average rating by category
        category_rating = self.df.groupby('category')['customer_rating'].mean().sort_values(ascending=False)
        
        ax = axes[1, 0]
        category_rating.plot(kind='barh', ax=ax, color='lightcoral', alpha=0.7)
        ax.set_title('Average Customer Rating by Category', fontsize=12, fontweight='bold')
        ax.set_xlabel('Average Rating')
        ax.set_xlim(0, 5)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Category growth rate (year-over-year)
        category_yearly = self.df.pivot_table(values='final_amount_inr', index='order_year', columns='category', aggfunc='sum')
        category_growth = (category_yearly.iloc[-1] - category_yearly.iloc[0]) / category_yearly.iloc[0] * 100
        category_growth = category_growth.sort_values(ascending=False)
        
        ax = axes[1, 1]
        colors_growth = ['green' if x > 0 else 'red' for x in category_growth.values]
        category_growth.plot(kind='barh', ax=ax, color=colors_growth, alpha=0.7)
        ax.set_title('Category Growth Rate (2015-2025)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Growth Rate (%)')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        insights = {
            'top_category': category_revenue.index[0],
            'top_category_revenue': category_revenue.values[0],
            'total_categories': len(category_revenue),
            'fastest_growing': category_growth.index[0]
        }
        
        return fig, insights
    
    # ==================== CHALLENGE 6: Prime Membership Impact ====================
    def prime_membership_analysis(self) -> Tuple[plt.Figure, Dict]:
        """
        Challenge 6: Prime membership impact analysis
        """
        logger.info("Generating Prime Membership Analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        prime_data = self.df.groupby('is_prime_member').agg({
            'final_amount_inr': ['sum', 'mean', 'count'],
            'customer_rating': 'mean',
            'delivery_days': 'mean'
        }).round(2)
        
        # Revenue comparison
        prime_revenue = self.df.groupby('is_prime_member')['final_amount_inr'].sum()
        
        ax = axes[0, 0]
        labels = ['Non-Prime', 'Prime']
        colors = ['lightcoral', 'lightgreen']
        ax.bar(labels, prime_revenue.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_title('Total Revenue: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Revenue (INR)')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Average order value
        prime_avg_order = self.df.groupby('is_prime_member')['final_amount_inr'].mean()
        
        ax = axes[0, 1]
        ax.bar(labels, prime_avg_order.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_title('Average Order Value: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Order Value (INR)')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Customer satisfaction (rating)
        prime_rating = self.df.groupby('is_prime_member')['customer_rating'].mean()
        
        ax = axes[1, 0]
        ax.bar(labels, prime_rating.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_title('Average Customer Rating: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Rating (1-5)')
        ax.set_ylim(0, 5)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Delivery performance
        prime_delivery = self.df.groupby('is_prime_member')['delivery_days'].mean()
        
        ax = axes[1, 1]
        ax.bar(labels, prime_delivery.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_title('Average Delivery Days: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Delivery Days')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        prime_members = self.df[self.df['is_prime_member'] == 1]
        non_prime = self.df[self.df['is_prime_member'] == 0]
        
        insights = {
            'prime_revenue_share': (prime_revenue[1] / prime_revenue.sum() * 100) if len(prime_revenue) > 1 else 0,
            'prime_avg_order_value': prime_avg_order[1] if 1 in prime_avg_order.index else 0,
            'price_premium': ((prime_avg_order[1] - prime_avg_order[0]) / prime_avg_order[0] * 100) if 0 in prime_avg_order.index and 1 in prime_avg_order.index else 0,
            'prime_satisfaction': prime_rating[1] if 1 in prime_rating.index else 0
        }
        
        return fig, insights
    
    # ==================== Additional EDA Methods ====================
    def generate_all_eda_reports(self, output_path: str = None):
        """
        Generate all EDA reports
        
        Args:
            output_path: Path to save figures
        """
        reports = {
            'revenue_trend': self.revenue_trend_analysis(),
            'seasonal_patterns': self.seasonal_patterns_analysis(),
            'rfm_segmentation': self.customer_segmentation_rfm(),
            'payment_evolution': self.payment_methods_evolution(),
            'category_performance': self.category_performance_analysis(),
            'prime_analysis': self.prime_membership_analysis()
        }
        
        return reports


def generate_eda_summary_report(df: pd.DataFrame) -> Dict:
    """
    Generate comprehensive EDA summary
    
    Args:
        df: DataFrame for analysis
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'dataset_shape': df.shape,
        'date_range': f"{df['order_date'].min()} to {df['order_date'].max()}",
        'total_revenue': df['final_amount_inr'].sum(),
        'total_orders': len(df),
        'unique_customers': df['customer_id'].nunique(),
        'unique_products': df['product_id'].nunique(),
        'avg_order_value': df['final_amount_inr'].mean(),
        'median_order_value': df['final_amount_inr'].median(),
        'categories': df['category'].nunique(),
        'cities': df['customer_city'].nunique(),
        'payment_methods': df['payment_method'].nunique()
    }
    
    return summary


if __name__ == "__main__":
    print("EDA Analysis Module")
    print("Import EDAAnalyzer class to use analysis functions")
