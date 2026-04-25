import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Optional
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class ComprehensiveEDAAnalyzer:
    """All 20 EDA analysis questions with comprehensive visualizations"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with cleaned transaction data"""
        self.df = df.copy()
        self._prepare_data()
        logger.info(f"EDA Analyzer initialized with {len(df):,} records")
    
    def _prepare_data(self):
        """Prepare data for analysis"""
        if 'order_date' in self.df.columns:
            self.df['order_date'] = pd.to_datetime(self.df['order_date'], errors='coerce')
            self.df['order_year'] = self.df['order_date'].dt.year
            self.df['order_month'] = self.df['order_date'].dt.month
            self.df['order_quarter'] = self.df['order_date'].dt.quarter
            self.df['order_week'] = self.df['order_date'].dt.isocalendar().week
            self.df['day_of_week'] = self.df['order_date'].dt.dayofweek
    
    # ==================== Q1: Revenue Trend Analysis ====================
    def q1_revenue_trend_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Question 1: Revenue growth trends 2015-2025"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        yearly = self.df.groupby('order_year')['final_amount_inr'].agg(['sum', 'count']).reset_index()
        yearly['growth'] = yearly['sum'].pct_change() * 100
        
        # Yearly revenue with trend
        axes[0, 0].plot(yearly['order_year'], yearly['sum']/1e7, marker='o', linewidth=2, markersize=8, color='#FF9900')
        axes[0, 0].fill_between(yearly['order_year'], yearly['sum']/1e7, alpha=0.3, color='#FF9900')
        axes[0, 0].set_title('Yearly Revenue Trend (2015-2025)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Revenue (Crores INR)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Growth rate
        colors = ['green' if x > 0 else 'red' for x in yearly['growth'].fillna(0)]
        axes[0, 1].bar(yearly['order_year'], yearly['growth'].fillna(0), color=colors, alpha=0.7)
        axes[0, 1].set_title('Year-over-Year Growth Rate (%)', fontsize=12, fontweight='bold')
        axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Monthly trend
        monthly = self.df.groupby(['order_year', 'order_month'])['final_amount_inr'].sum().reset_index()
        monthly['date'] = pd.to_datetime(monthly[['order_year', 'order_month']].rename(columns={'order_year': 'year', 'order_month': 'month'}).assign(day=1))
        axes[1, 0].plot(monthly['date'], monthly['final_amount_inr']/1e5, color='#146EB4', alpha=0.7)
        axes[1, 0].set_title('Monthly Revenue Trend', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Orders per year
        axes[1, 1].bar(yearly['order_year'], yearly['count']/1000, color='#28A745', alpha=0.7)
        axes[1, 1].set_title('Orders per Year (in thousands)', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, {'total_revenue': self.df['final_amount_inr'].sum(), 'avg_growth': yearly['growth'].mean()}
    
    # ==================== Q2: Seasonal Patterns ====================
    def q2_seasonal_patterns(self) -> Tuple[plt.Figure, Dict]:
        """Question 2: Seasonal sales patterns and peak months"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Monthly heatmap
        pivot_monthly = self.df.pivot_table(values='final_amount_inr', 
                                          index='order_month', 
                                          columns='order_year', 
                                          aggfunc='sum')
        sns.heatmap(pivot_monthly/1e6, annot=True, fmt='.0f', cmap='YlOrRd', ax=axes[0, 0], cbar_kws={'label': 'Revenue (Million)'})
        axes[0, 0].set_title('Monthly Revenue Heatmap (Year vs Month)', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Month')
        
        # Peak months
        monthly_avg = self.df.groupby('order_month')['final_amount_inr'].mean()
        axes[0, 1].bar(monthly_avg.index, monthly_avg.values, color='#FF6B6B', alpha=0.7)
        axes[0, 1].set_title('Average Revenue by Month', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Month')
        axes[0, 1].set_ylabel('Average Revenue (INR)')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Quarter analysis
        quarterly = self.df.groupby(['order_year', 'order_quarter'])['final_amount_inr'].sum().reset_index()
        pivot_quarterly = quarterly.pivot(index='order_quarter', columns='order_year', values='final_amount_inr')
        sns.heatmap(pivot_quarterly/1e7, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1, 0], cbar_kws={'label': 'Revenue (Crores)'})
        axes[1, 0].set_title('Quarterly Revenue Heatmap', fontsize=12, fontweight='bold')
        
        # Day of week analysis
        dow_revenue = self.df.groupby('day_of_week')['final_amount_inr'].agg(['sum', 'count'])
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        axes[1, 1].bar(range(7), dow_revenue['sum']/1e6, color='#00B894', alpha=0.7)
        axes[1, 1].set_xticks(range(7))
        axes[1, 1].set_xticklabels(dow_names, rotation=45, ha='right')
        axes[1, 1].set_title('Revenue by Day of Week', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Revenue (Million INR)')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        peak_month = monthly_avg.idxmax()
        return fig, {'peak_month': peak_month, 'low_month': monthly_avg.idxmin()}
    
    # ==================== Q3: Customer RFM Segmentation ====================
    def q3_rfm_segmentation(self) -> Tuple[plt.Figure, Dict]:
        """Question 3: RFM customer segmentation analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # RFM Calculation
        reference_date = self.df['order_date'].max()
        rfm = self.df.groupby('customer_id').agg({
            'order_date': lambda x: (reference_date - x.max()).days,  # Recency
            'customer_id': 'count',  # Frequency
            'final_amount_inr': 'sum'  # Monetary
        }).rename(columns={'order_date': 'recency', 'customer_id': 'frequency', 'final_amount_inr': 'monetary'})
        
        # R, F, M quartiles
        rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
        rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')
        rfm['M'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4], duplicates='drop')
        
        # Recency distribution
        axes[0, 0].hist(rfm['recency'], bins=30, color='#667eea', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Recency Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Days since last purchase')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Frequency distribution
        axes[0, 1].hist(rfm['frequency'], bins=30, color='#764ba2', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Frequency Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Number of purchases')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # R vs F scatter
        axes[1, 0].scatter(rfm['recency'], rfm['frequency'], alpha=0.5, c=rfm['monetary'], cmap='viridis', s=50)
        axes[1, 0].set_title('Recency vs Frequency (colored by Monetary)', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Recency (days)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Monetary distribution
        axes[1, 1].hist(rfm['monetary'], bins=30, color='#f093fb', alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('Monetary Value Distribution', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Total spending (INR)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, {'total_customers': len(rfm), 'avg_clv': rfm['monetary'].mean()}
    
    # ==================== Q4: Payment Method Evolution ====================
    def q4_payment_evolution(self) -> Tuple[plt.Figure, Dict]:
        """Question 4: Payment method trends over time"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'payment_method' not in self.df.columns:
            logger.warning("Payment method column not found")
            return fig, {}
        
        # Stacked area chart
        payment_trend = self.df.groupby(['order_year', 'payment_method'])['final_amount_inr'].sum().unstack(fill_value=0)
        payment_trend.plot(kind='area', stacked=True, ax=axes[0, 0], alpha=0.7)
        axes[0, 0].set_title('Payment Method Market Share Over Time (Revenue)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Revenue (INR)')
        axes[0, 0].legend(loc='upper left', fontsize=9)
        
        # Payment method distribution
        payment_dist = self.df.groupby('payment_method')['final_amount_inr'].sum().sort_values(ascending=False)
        axes[0, 1].pie(payment_dist.values, labels=payment_dist.index, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Current Payment Method Distribution', fontsize=12, fontweight='bold')
        
        # Count by payment method
        payment_count = self.df.groupby('payment_method').size().sort_values(ascending=False)
        axes[1, 0].barh(payment_count.index, payment_count.values, color='#17A2B8', alpha=0.7)
        axes[1, 0].set_title('Transaction Count by Payment Method', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Count')
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Average transaction value by payment
        payment_avg = self.df.groupby('payment_method')['final_amount_inr'].mean().sort_values(ascending=False)
        axes[1, 1].bar(range(len(payment_avg)), payment_avg.values, color='#FFC300', alpha=0.7)
        axes[1, 1].set_xticks(range(len(payment_avg)))
        axes[1, 1].set_xticklabels(payment_avg.index, rotation=45, ha='right')
        axes[1, 1].set_title('Average Transaction Value by Payment Method', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Amount (INR)')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, {'dominant_payment': payment_dist.index[0], 'payment_methods': len(payment_dist)}
    
    # ==================== Q5: Category Performance ====================
    def q5_category_performance(self) -> Tuple[plt.Figure, Dict]:
        """Question 5: Category-wise performance analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'category' not in self.df.columns:
            logger.warning("Category column not found")
            return fig, {}
        
        category_stats = self.df.groupby('category').agg({
            'final_amount_inr': ['sum', 'count', 'mean']
        }).round(2)
        category_stats.columns = ['revenue', 'orders', 'avg_order_value']
        category_stats = category_stats.sort_values('revenue', ascending=False)
        
        # Revenue by category
        axes[0, 0].barh(category_stats.index, category_stats['revenue']/1e6, color='#FF9900', alpha=0.7)
        axes[0, 0].set_title('Revenue by Category', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Revenue (Million INR)')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Category market share
        axes[0, 1].pie(category_stats['revenue'], labels=category_stats.index, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Category Market Share by Revenue', fontsize=12, fontweight='bold')
        
        # Orders by category
        category_order_share = self.df.groupby('category').size().sort_values(ascending=False)
        axes[1, 0].pie(category_order_share.values, labels=category_order_share.index, autopct='%1.1f%%', startangle=90)
        axes[1, 0].set_title('Category Market Share by Order Count', fontsize=12, fontweight='bold')
        
        # Average order value
        axes[1, 1].bar(range(len(category_stats)), category_stats['avg_order_value'], color='#28A745', alpha=0.7)
        axes[1, 1].set_xticks(range(len(category_stats)))
        axes[1, 1].set_xticklabels(category_stats.index, rotation=45, ha='right')
        axes[1, 1].set_title('Average Order Value by Category', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Average Order Value (INR)')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, {'top_category': category_stats.index[0], 'total_categories': len(category_stats)}
    
    # ==================== Q6: Prime Membership Impact ====================
    def q6_prime_impact(self) -> Tuple[plt.Figure, Dict]:
        """Question 6: Prime membership customer behavior analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'is_prime_member' not in self.df.columns:
            logger.warning("Prime membership column not found")
            return fig, {}
        
        prime_df = self.df.copy()
        prime_df['membership'] = prime_df['is_prime_member'].map({1: 'Prime', 0: 'Non-Prime'})
        
        # Revenue comparison
        prime_revenue = prime_df.groupby('membership')['final_amount_inr'].sum()
        axes[0, 0].pie(prime_revenue.values, labels=prime_revenue.index, autopct='%1.1f%%', colors=['#28A745', '#FF6B6B'])
        axes[0, 0].set_title('Revenue: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        
        # Average order value
        prime_aov = prime_df.groupby('membership')['final_amount_inr'].mean()
        axes[0, 1].bar(prime_aov.index, prime_aov.values, color=['#28A745', '#FF6B6B'], alpha=0.7)
        axes[0, 1].set_title('Average Order Value: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Average Order Value (INR)')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Order frequency
        prime_orders = prime_df.groupby('membership').size()
        axes[1, 0].bar(prime_orders.index, prime_orders.values, color=['#28A745', '#FF6B6B'], alpha=0.7)
        axes[1, 0].set_title('Order Count: Prime vs Non-Prime', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Order Count')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Category preference
        if 'category' in self.df.columns:
            category_prime = prime_df.groupby(['membership', 'category']).size().unstack(fill_value=0)
            category_prime_pct = category_prime.div(category_prime.sum(axis=1), axis=0) * 100
            category_prime_pct.plot(kind='bar', ax=axes[1, 1], stacked=False)
            axes[1, 1].set_title('Category Preferences: Prime vs Non-Prime', fontsize=12, fontweight='bold')
            axes[1, 1].set_ylabel('Percentage (%)')
            axes[1, 1].legend(loc='upper right', fontsize=8)
            plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=0)
        
        plt.tight_layout()
        prime_count = len(prime_df[prime_df['is_prime_member'] == 1]['customer_id'].unique())
        return fig, {'prime_customers': prime_count, 'prime_revenue_share': prime_revenue[1]/prime_revenue.sum() if 1 in prime_revenue.index else 0}
    
    # ==================== Q7: Geographic Analysis ====================
    def q7_geographic_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Question 7: Geographic performance across cities/states"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'customer_city' not in self.df.columns:
            logger.warning("City column not found")
            return fig, {}
        
        city_stats = self.df.groupby('customer_city').agg({
            'final_amount_inr': ['sum', 'count', 'mean']
        }).round(2)
        city_stats.columns = ['revenue', 'orders', 'avg_order_value']
        city_stats = city_stats.sort_values('revenue', ascending=False)
        
        # Top cities by revenue
        top_cities = city_stats.head(10)
        axes[0, 0].barh(top_cities.index, top_cities['revenue']/1e6, color='#FF6B6B', alpha=0.7)
        axes[0, 0].set_title('Top 10 Cities by Revenue', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Revenue (Million INR)')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Top cities by order count
        top_cities_orders = self.df.groupby('customer_city').size().sort_values(ascending=False).head(10)
        axes[0, 1].barh(top_cities_orders.index, top_cities_orders.values, color='#17A2B8', alpha=0.7)
        axes[0, 1].set_title('Top 10 Cities by Order Count', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Order Count')
        axes[0, 1].grid(True, alpha=0.3, axis='x')
        
        # Revenue per city distribution
        axes[1, 0].hist(city_stats['revenue']/1e6, bins=20, color='#667eea', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Revenue Distribution Across Cities', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Revenue (Million INR)')
        axes[1, 0].set_ylabel('Number of Cities')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # City concentration (Lorenz curve approximation)
        city_revenue_sorted = city_stats['revenue'].sort_values(ascending=False)
        cumsum = np.cumsum(city_revenue_sorted)
        cumsum_pct = cumsum / cumsum.iloc[-1] * 100
        axes[1, 1].plot(range(len(cumsum_pct)), cumsum_pct, marker='o', markersize=4, color='#28A745', linewidth=2)
        axes[1, 1].set_title('Revenue Concentration by City', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('City Rank')
        axes[1, 1].set_ylabel('Cumulative Revenue (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        city_conc = cumsum_pct.iloc[min(10, len(cumsum_pct)-1)] if len(cumsum_pct) > 0 else 0
        return fig, {'total_cities': len(city_stats), 'top_city': city_stats.index[0], 'city_concentration': city_conc}
    
    # ==================== Q8-20: Additional Analysis Methods ====================
    
    def q8_festival_impact(self) -> Tuple[plt.Figure, Dict]:
        """Question 8: Festival sales impact analysis"""
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))
        
        if 'is_festival_sale' not in self.df.columns:
            logger.warning("Festival column not found")
            return fig, {}
        
        festival_df = self.df.copy()
        festival_df['type'] = festival_df['is_festival_sale'].map({1: 'Festival Sale', 0: 'Regular Sale'})
        
        # Revenue comparison
        festival_revenue = festival_df.groupby('type')['final_amount_inr'].agg(['sum', 'count', 'mean'])
        axes[0].bar(festival_revenue.index, festival_revenue['sum']/1e6, color=['#FF9900', '#146EB4'], alpha=0.7)
        axes[0].set_title('Revenue: Festival vs Regular Sales', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Revenue (Million INR)')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Metrics comparison
        if len(festival_revenue) >= 2:
            festival_metrics = festival_revenue[['sum', 'count', 'mean']].T
            x = np.arange(3)
            row1 = festival_metrics.iloc[:, 0] if len(festival_metrics.columns) > 0 else np.zeros(3)
            row2 = festival_metrics.iloc[:, 1] if len(festival_metrics.columns) > 1 else np.zeros(3)
            axes[1].bar(x - 0.2, row1.values/1e6 if len(row1) > 0 else np.zeros(3), 0.4, label='Festival Sales', color='#FF9900', alpha=0.7)
            axes[1].bar(x + 0.2, row2.values/1e6 if len(row2) > 0 else np.zeros(3), 0.4, label='Regular Sales', color='#146EB4', alpha=0.7)
            axes[1].set_title('Performance Metrics Comparison', fontsize=12, fontweight='bold')
            axes[1].set_ylabel('Value (Million INR)')
            axes[1].set_xticks(x)
            axes[1].set_xticklabels(['Total Revenue', 'Transactions', 'Avg Order Value'])
            axes[1].legend()
            axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        festival_pct = (festival_revenue.loc['Festival Sale', 'sum'] / festival_revenue['sum'].sum() * 100) if 'Festival Sale' in festival_revenue.index else 0
        return fig, {'festival_revenue_share': festival_pct}
    
    def q9_customer_rating_patterns(self) -> Tuple[plt.Figure, Dict]:
        """Question 9: Customer rating patterns and impact"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'customer_rating' not in self.df.columns:
            logger.warning("Rating column not found")
            return fig, {}
        
        rating_df = self.df.dropna(subset=['customer_rating'])
        
        # Rating distribution
        axes[0, 0].hist(rating_df['customer_rating'], bins=20, color='#FFD700', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Customer Rating Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Rating')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Average rating by category
        if 'category' in self.df.columns:
            category_rating = rating_df.groupby('category')['customer_rating'].mean().sort_values(ascending=False)
            axes[0, 1].bar(range(len(category_rating)), category_rating.values, color='#FF6B6B', alpha=0.7)
            axes[0, 1].set_xticks(range(len(category_rating)))
            axes[0, 1].set_xticklabels(category_rating.index, rotation=45, ha='right')
            axes[0, 1].set_title('Average Rating by Category', fontsize=12, fontweight='bold')
            axes[0, 1].set_ylabel('Average Rating')
            axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Rating vs revenue
        rating_revenue = rating_df.groupby(pd.cut(rating_df['customer_rating'], bins=5))['final_amount_inr'].agg(['sum', 'count', 'mean'])
        axes[1, 0].bar(range(len(rating_revenue)), rating_revenue['sum']/1e6, color='#28A745', alpha=0.7)
        axes[1, 0].set_title('Revenue by Rating Range', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Revenue (Million INR)')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Rating trends over time
        rating_by_year = rating_df.groupby('order_year')['customer_rating'].mean()
        axes[1, 1].plot(rating_by_year.index, rating_by_year.values, marker='o', linewidth=2, markersize=8, color='#667eea')
        axes[1, 1].set_title('Average Rating Trend Over Years', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average Rating')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'avg_rating': rating_df['customer_rating'].mean(), 'high_rating_pct': (rating_df['customer_rating'] >= 4).sum() / len(rating_df) * 100}
    
    def q10_price_demand_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Question 10: Price vs demand analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Price distribution
        axes[0, 0].hist(self.df['final_amount_inr'], bins=50, color='#667eea', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Price Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Price (INR)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Price vs discount correlation
        if 'discount_percent' in self.df.columns:
            axes[0, 1].scatter(self.df['discount_percent'], self.df['final_amount_inr'], alpha=0.3, s=10)
            axes[0, 1].set_title('Discount vs Final Price', fontsize=12, fontweight='bold')
            axes[0, 1].set_xlabel('Discount (%)')
            axes[0, 1].set_ylabel('Final Price (INR)')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Revenue by price range
        price_bins = pd.cut(self.df['final_amount_inr'], bins=5)
        price_revenue = self.df.groupby(price_bins)['final_amount_inr'].agg(['sum', 'count'])
        axes[1, 0].bar(range(len(price_revenue)), price_revenue['sum']/1e6, color='#FF9900', alpha=0.7)
        axes[1, 0].set_title('Revenue by Price Range', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Revenue (Million INR)')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Order count by price range
        axes[1, 1].bar(range(len(price_revenue)), price_revenue['count'], color='#28A745', alpha=0.7)
        axes[1, 1].set_title('Order Count by Price Range', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Order Count')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig, {'avg_price': self.df['final_amount_inr'].mean(), 'median_price': self.df['final_amount_inr'].median()}
    
    def q11_delivery_performance(self) -> Tuple[plt.Figure, Dict]:
        """Question 11: Delivery performance analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'delivery_days' not in self.df.columns:
            logger.warning("Delivery days column not found")
            return fig, {}
        
        delivery_df = self.df.dropna(subset=['delivery_days'])
        
        # Delivery days distribution
        axes[0, 0].hist(delivery_df['delivery_days'], bins=30, color='#FF6B6B', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Delivery Days Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Delivery Days')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # On-time delivery (assume <= 3 days is on-time)
        delivery_df['on_time'] = delivery_df['delivery_days'] <= 3
        on_time_pct = delivery_df['on_time'].sum() / len(delivery_df) * 100
        axes[0, 1].pie([on_time_pct, 100-on_time_pct], labels=['On-time (≤3 days)', 'Late (>3 days)'],
                       autopct='%1.1f%%', colors=['#28A745', '#FF6B6B'])
        axes[0, 1].set_title('On-Time Delivery Performance', fontsize=12, fontweight='bold')
        
        # Delivery days by category
        if 'category' in self.df.columns:
            delivery_by_cat = delivery_df.groupby('category')['delivery_days'].mean().sort_values()
            axes[1, 0].barh(delivery_by_cat.index, delivery_by_cat.values, color='#17A2B8', alpha=0.7)
            axes[1, 0].set_title('Average Delivery Days by Category', fontsize=12, fontweight='bold')
            axes[1, 0].set_xlabel('Average Days')
            axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Delivery days trend
        delivery_by_year = delivery_df.groupby('order_year')['delivery_days'].mean()
        axes[1, 1].plot(delivery_by_year.index, delivery_by_year.values, marker='o', linewidth=2, markersize=8, color='#667eea')
        axes[1, 1].set_title('Average Delivery Days Trend', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average Delivery Days')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'avg_delivery_days': delivery_df['delivery_days'].mean(), 'on_time_pct': on_time_pct}
    
    def q12_return_satisfaction(self) -> Tuple[plt.Figure, Dict]:
        """Question 12: Return patterns and satisfaction correlation"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'is_returned' not in self.df.columns:
            if 'return_status' in self.df.columns:
                self.df['is_returned'] = (self.df['return_status'] == 'Returned').astype(int)
            else:
                logger.warning("Return column not found")
                return fig, {}
        
        return_df = self.df.copy()
        return_df['status'] = return_df['is_returned'].map({1: 'Returned', 0: 'Kept'})
        
        # Return rate
        return_rate = (return_df['is_returned'].sum() / len(return_df) * 100)
        axes[0, 0].pie([return_rate, 100-return_rate], labels=['Returned', 'Kept'], autopct='%1.1f%%',
                       colors=['#FF6B6B', '#28A745'])
        axes[0, 0].set_title(f'Overall Return Rate: {return_rate:.2f}%', fontsize=12, fontweight='bold')
        
        # Return by category
        return_by_cat = return_df.groupby('category')['is_returned'].apply(lambda x: x.sum()/len(x)*100).sort_values(ascending=False)
        axes[0, 1].bar(range(len(return_by_cat)), return_by_cat.values, color='#FF6B6B', alpha=0.7)
        axes[0, 1].set_xticks(range(len(return_by_cat)))
        axes[0, 1].set_xticklabels(return_by_cat.index, rotation=45, ha='right')
        axes[0, 1].set_title('Return Rate by Category', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Return Rate (%)')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Return vs rating
        if 'customer_rating' in self.df.columns:
            rating_return = return_df.groupby('status')['customer_rating'].mean()
            axes[1, 0].bar(rating_return.index, rating_return.values, color=['#FF6B6B', '#28A745'], alpha=0.7)
            axes[1, 0].set_title('Average Rating: Returned vs Kept', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylabel('Average Rating')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Return trend over time
        return_trend = return_df.groupby('order_year')['is_returned'].apply(lambda x: x.sum()/len(x)*100)
        axes[1, 1].plot(return_trend.index, return_trend.values, marker='o', linewidth=2, markersize=8, color='#667eea')
        axes[1, 1].set_title('Return Rate Trend Over Years', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Return Rate (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'return_rate': return_rate, 'high_return_category': return_by_cat.index[0] if len(return_by_cat) > 0 else 'N/A'}
    
    def q13_discount_effectiveness(self) -> Tuple[plt.Figure, Dict]:
        """Question 13: Discount and promotional effectiveness"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'discount_percent' not in self.df.columns:
            logger.warning("Discount column not found")
            return fig, {}
        
        discount_df = self.df[self.df['discount_percent'] > 0].copy()
        
        # Discount distribution
        axes[0, 0].hist(discount_df['discount_percent'], bins=30, color='#FFD700', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Discount Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Discount (%)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Discount vs order volume
        discount_bins = pd.cut(self.df['discount_percent'], bins=[0, 10, 20, 30, 50, 100])
        discount_volume = self.df.groupby(discount_bins).size()
        axes[0, 1].bar(range(len(discount_volume)), discount_volume.values, color='#28A745', alpha=0.7)
        axes[0, 1].set_title('Order Volume by Discount Range', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Order Count')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Revenue impact
        discount_revenue = self.df.groupby(discount_bins)['final_amount_inr'].sum()
        axes[1, 0].bar(range(len(discount_revenue)), discount_revenue.values/1e6, color='#FF9900', alpha=0.7)
        axes[1, 0].set_title('Revenue by Discount Range', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Revenue (Million INR)')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Discount trend
        discount_trend = self.df.groupby('order_year')['discount_percent'].mean()
        axes[1, 1].plot(discount_trend.index, discount_trend.values, marker='o', linewidth=2, markersize=8, color='#FF6B6B')
        axes[1, 1].set_title('Average Discount Trend', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average Discount (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'avg_discount': self.df['discount_percent'].mean(), 'items_with_discount': len(discount_df)/len(self.df)*100}
    
    def q14_revenue_per_customer_clv(self) -> Tuple[plt.Figure, Dict]:
        """Question 14: Customer lifetime value and cohort analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'customer_id' not in self.df.columns:
            logger.warning("Customer ID column not found")
            return fig, {}
        
        # CLV distribution
        clv = self.df.groupby('customer_id')['final_amount_inr'].sum()
        axes[0, 0].hist(clv, bins=50, color='#667eea', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Customer Lifetime Value Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('CLV (INR)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # CLV segments
        clv_segments = pd.qcut(clv, q=4, labels=['Low', 'Medium', 'High', 'VIP'])
        segment_dist = clv_segments.value_counts()
        axes[0, 1].pie(segment_dist.values, labels=segment_dist.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Customer Segmentation (by CLV)', fontsize=12, fontweight='bold')
        
        # Cohort by first purchase year
        first_purchase = self.df.groupby('customer_id')['order_year'].min()
        customer_clv = self.df.groupby('customer_id')['final_amount_inr'].sum().sort_values(ascending=False).head(10)
        axes[1, 0].barh(range(len(customer_clv)), customer_clv.values, color='#28A745', alpha=0.7)
        axes[1, 0].set_title('Top 10 Customers by Total CLV', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Total Spending (INR)')
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # CLV by purchase year
        customer_year_clv = self.df.groupby('order_year')['final_amount_inr'].agg(['sum', 'count', lambda x: x.mean()])
        axes[1, 1].plot(customer_year_clv.index, customer_year_clv.iloc[:, 2], marker='o', linewidth=2, markersize=8, color='#FF6B6B')
        axes[1, 1].set_title('Average CLV Trend', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Average CLV (INR)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'avg_clv': clv.mean(), 'median_clv': clv.median(), 'vip_customers': segment_dist['VIP']}
    
    def q15_category_trends(self) -> Tuple[plt.Figure, Dict]:
        """Question 15: Category evolution and trends"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'category' not in self.df.columns:
            logger.warning("Category column not found")
            return fig, {}
        
        # Category trends over time (stacked area)
        category_trend = self.df.groupby(['order_year', 'category'])['final_amount_inr'].sum().unstack(fill_value=0)
        category_trend.plot(kind='area', stacked=True, ax=axes[0, 0], alpha=0.7)
        axes[0, 0].set_title('Category Revenue Trends (2015-2025)', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylabel('Revenue (INR)')
        axes[0, 0].legend(loc='upper left', fontsize=8)
        
        # Market share evolution
        top_categories = self.df.groupby('category')['final_amount_inr'].sum().nlargest(5).index
        top_cat_trend = category_trend[top_categories]
        top_cat_share = top_cat_trend.div(top_cat_trend.sum(axis=1), axis=0) * 100
        top_cat_share.plot(ax=axes[0, 1], marker='o', linewidth=2)
        axes[0, 1].set_title('Market Share Evolution (Top 5)', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Market Share (%)')
        axes[0, 1].legend(loc='upper right', fontsize=8)
        axes[0, 1].grid(True, alpha=0.3)
        
        # New vs established categories
        category_first_year = self.df.groupby('category')['order_year'].min().sort_values()
        axes[1, 0].barh(category_first_year.index, category_first_year.values, color='#667eea', alpha=0.7)
        axes[1, 0].set_title('Category Launch Year', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('First Year')
        axes[1, 0].grid(True, alpha=0.3, axis='x')
        
        # Category growth rates
        category_cagr = []
        for cat in top_categories:
            data = category_trend[cat]
            if data.iloc[0] > 0:
                cagr = (data.iloc[-1] / data.iloc[0]) ** (1/len(data)) - 1
                category_cagr.append({'category': cat, 'cagr': cagr * 100})
        if category_cagr:
            cagr_df = pd.DataFrame(category_cagr).sort_values('cagr', ascending=True)
            axes[1, 1].barh(cagr_df['category'], cagr_df['cagr'], color=['red' if x < 0 else 'green' for x in cagr_df['cagr']], alpha=0.7)
            axes[1, 1].set_title('Category CAGR (Compound Annual Growth Rate)', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('CAGR (%)')
            axes[1, 1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig, {'top_category': top_categories[0], 'new_categories': len(category_first_year[category_first_year > category_first_year.min()+5])}
    
    def q16_monthly_revenue_volatility(self) -> Tuple[plt.Figure, Dict]:
        """Question 16: Monthly revenue volatility and seasonality strength"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Monthly revenue
        monthly = self.df.groupby(['order_year', 'order_month'])['final_amount_inr'].sum().reset_index()
        
        # Monthly boxplot
        monthly_boxplot = self.df.groupby('order_month')['final_amount_inr'].apply(list)
        axes[0, 0].boxplot(monthly_boxplot.values, labels=monthly_boxplot.index)
        axes[0, 0].set_title('Revenue Distribution by Month', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Revenue (INR)')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Volatility over time (rolling std)
        monthly_series = monthly.groupby(['order_month'])['final_amount_inr'].mean()
        rolling_volatility = []
        for i in range(len(monthly_series)):
            if i >= 3:
                rollstd = monthly_series.iloc[i-3:i+1].std()
                rolling_volatility.append(rollstd)
        
        axes[0, 1].plot(range(len(rolling_volatility)), rolling_volatility, marker='o', color='#FF6B6B', linewidth=2)
        axes[0, 1].set_title('Revenue Volatility (Rolling 4-Month Window)', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Standard Deviation (INR)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Coefficient of variation by year
        cv_by_year = []
        for year in sorted(self.df['order_year'].unique()):
            year_data = self.df[self.df['order_year'] == year].groupby('order_month')['final_amount_inr'].sum()
            cv = year_data.std() / year_data.mean() if year_data.mean() > 0 else 0
            cv_by_year.append({'year': year, 'cv': cv})
        
        cv_df = pd.DataFrame(cv_by_year)
        axes[1, 0].plot(cv_df['year'], cv_df['cv'], marker='o', color='#667eea', linewidth=2, markersize=8)
        axes[1, 0].set_title('Coefficient of Variation by Year', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('CV (Volatility)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Year-over-year comparison heatmap
        pivot_yoy = monthly.pivot(index='order_month', columns='order_year', values='final_amount_inr')
        sns.heatmap(pivot_yoy/1e6, annot=True, fmt='.0f', cmap='RdYlGn', ax=axes[1, 1], cbar_kws={'label': 'Revenue (Million)'})
        axes[1, 1].set_title('Monthly Revenue Heatmap (Year-Month)', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return fig, {'avg_volatility': np.mean(rolling_volatility) if rolling_volatility else 0}
    
    def q17_top_products_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Question 17: Top products and brand performance"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'product_name' not in self.df.columns:
            logger.warning("Product name column not found")
            return fig, {}
        
        # Top 10 products by revenue
        top_products = self.df.groupby('product_name')['final_amount_inr'].sum().sort_values(ascending=False).head(10)
        axes[0, 0].barh(range(len(top_products)), top_products.values/1e5, color='#FF9900', alpha=0.7)
        axes[0, 0].set_yticks(range(len(top_products)))
        axes[0, 0].set_yticklabels([p[:30] + '...' if len(p) > 30 else p for p in top_products.index], fontsize=9)
        axes[0, 0].set_xlabel('Revenue (Hundred Thousand INR)')
        axes[0, 0].set_title('Top 10 Products by Revenue', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Top products by volume
        top_products_vol = self.df.groupby('product_name').size().sort_values(ascending=False).head(10)
        axes[0, 1].barh(range(len(top_products_vol)), top_products_vol.values, color='#28A745', alpha=0.7)
        axes[0, 1].set_yticks(range(len(top_products_vol)))
        axes[0, 1].set_yticklabels([p[:30] + '...' if len(p) > 30 else p for p in top_products_vol.index], fontsize=9)
        axes[0, 1].set_xlabel('Number of Orders')
        axes[0, 1].set_title('Top 10 Products by Order Count', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='x')
        
        # Product concentration
        all_products = self.df.groupby('product_name')['final_amount_inr'].sum().sort_values(ascending=False)
        cumsum = np.cumsum(all_products.values)
        cumsum_pct = cumsum / cumsum[-1] * 100
        concentration_20 = cumsum_pct[min(19, len(cumsum_pct)-1)]
        axes[1, 0].plot(range(min(100, len(cumsum_pct))), cumsum_pct[:100], color='#667eea', linewidth=2)
        axes[1, 0].fill_between(range(min(100, len(cumsum_pct))), cumsum_pct[:100], alpha=0.3, color='#667eea')
        axes[1, 0].axhline(y=80, color='red', linestyle='--', label='80% mark')
        axes[1, 0].set_title('Revenue Concentration (Pareto)', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Number of Products')
        axes[1, 0].set_ylabel('Cumulative Revenue (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Product rating vs sales
        if 'customer_rating' in self.df.columns:
            product_rating_sales = self.df.groupby('product_name').agg({
                'customer_rating': 'mean',
                'final_amount_inr': ['count', 'sum']
            }).reset_index()
            product_rating_sales.columns = ['product', 'rating', 'count', 'revenue']
            product_rating_sales = product_rating_sales[product_rating_sales['rating'] > 0].head(20)
            axes[1, 1].scatter(product_rating_sales['rating'], product_rating_sales['count'], 
                             s=product_rating_sales['revenue']/1e4, alpha=0.6, c=product_rating_sales['revenue'], cmap='viridis')
            axes[1, 1].set_title('Product Rating vs Sales Volume', fontsize=12, fontweight='bold')
            axes[1, 1].set_xlabel('Average Rating')
            axes[1, 1].set_ylabel('Order Count (bubble size = revenue)')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'total_products': len(all_products), 'top_product': top_products.index[0], 'concentration_20pct': concentration_20}
    
    def q18_customer_acquisition_retention(self) -> Tuple[plt.Figure, Dict]:
        """Question 18: Customer acquisition and retention trends"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'customer_id' not in self.df.columns:
            logger.warning("Customer ID column not found")
            return fig, {}
        
        # New customers per year
        first_purchase = self.df.groupby('customer_id')['order_year'].min()
        new_customers = first_purchase.value_counts().sort_index()
        axes[0, 0].bar(new_customers.index, new_customers.values, color='#FF9900', alpha=0.7)
        axes[0, 0].set_title('New Customers per Year', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('New Customers')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Repeat customer rate
        customer_purchases = self.df.groupby('customer_id').size()
        repeat_pct = (customer_purchases > 1).sum() / len(customer_purchases) * 100
        axes[0, 1].pie([repeat_pct, 100-repeat_pct], labels=[f'Repeat ({repeat_pct:.1f}%)', f'One-time ({100-repeat_pct:.1f}%)'],
                       colors=['#28A745', '#FF6B6B'], autopct='%1.1f%%')
        axes[0, 1].set_title('Customer Repeat Purchase Rate', fontsize=12, fontweight='bold')
        
        # Cohort retention
        retention_by_cohort = []
        for cohort_year in sorted(self.df['order_year'].unique())[:-1]:
            cohort_customers = set(self.df[self.df['order_year'] == cohort_year]['customer_id'])
            if cohort_customers:
                for year_offset in range(1, 4):
                    retention_year = cohort_year + year_offset
                    if retention_year <= self.df['order_year'].max():
                        retained = len(set(self.df[self.df['order_year'] == retention_year]['customer_id']) & cohort_customers)
                        retention_rate = retained / len(cohort_customers) * 100
                        retention_by_cohort.append({
                            'cohort': cohort_year,
                            'year_offset': year_offset,
                            'retention': retention_rate
                        })
        
        if retention_by_cohort:
            retention_df = pd.DataFrame(retention_by_cohort)
            for cohort in retention_df['cohort'].unique():
                cohort_data = retention_df[retention_df['cohort'] == cohort].sort_values('year_offset')
                axes[1, 0].plot(cohort_data['year_offset'], cohort_data['retention'], marker='o', label=f'Cohort {cohort}')
            axes[1, 0].set_title('Customer Retention by Cohort', fontsize=12, fontweight='bold')
            axes[1, 0].set_xlabel('Years Since First Purchase')
            axes[1, 0].set_ylabel('Retention Rate (%)')
            axes[1, 0].legend(fontsize=8)
            axes[1, 0].grid(True, alpha=0.3)
        
        # Customer lifetime trend
        clv = self.df.groupby('customer_id')['final_amount_inr'].sum()
        first_year = first_purchase
        clv_by_year = self.df.groupby(pd.cut(first_year, bins=list(sorted(self.df['order_year'].unique())))).apply(
            lambda x: clv.loc[x.index].mean()
        )
        axes[1, 1].plot(range(len(clv_by_year)), clv_by_year.values, marker='o', color='#667eea', linewidth=2, markersize=8)
        axes[1, 1].set_title('Average CLV by Cohort', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Average CLV (INR)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'repeat_rate': repeat_pct, 'new_customers_recent': new_customers.iloc[-1]}
    
    def q19_customer_frequency_distribution(self) -> Tuple[plt.Figure, Dict]:
        """Question 19: Customer frequency and engagement patterns"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        if 'customer_id' not in self.df.columns:
            logger.warning("Customer ID column not found")
            return fig, {}
        
        customer_freq = self.df.groupby('customer_id').size()
        
        # Frequency distribution
        axes[0, 0].hist(customer_freq, bins=30, color='#667eea', alpha=0.7, edgecolor='black', log=True)
        axes[0, 0].set_title('Customer Purchase Frequency Distribution (log scale)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Number of Purchases')
        axes[0, 0].set_ylabel('Number of Customers (log)')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Engagement segments
        freq_bins = [0, 1, 2, 5, 10, float('inf')]
        freq_labels = ['1 purchase', '2-1 purchases', '2-5 purchases', '5-10 purchases', '10+ purchases']
        customer_segment = pd.cut(customer_freq, bins=freq_bins, labels=freq_labels, include_lowest=True)
        segment_dist = customer_segment.value_counts()
        axes[0, 1].pie(segment_dist.values, labels=segment_dist.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Customer Engagement Segments', fontsize=12, fontweight='bold')
        
        # Revenue by frequency segment
        revenue_by_segment = self.df.groupby(pd.cut(self.df.groupby('customer_id').cumcount(), 
                                                     bins=[-1, 0, 1, 4, 9, float('inf')]))['final_amount_inr'].sum()
        axes[1, 0].bar(range(len(revenue_by_segment)), revenue_by_segment.values/1e6, color='#FF9900', alpha=0.7)
        axes[1, 0].set_title('Revenue by Purchase Frequency Segment', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylabel('Revenue (Million INR)')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Average revenue per frequency
        revenue_per_freq = self.df.groupby('customer_id')['final_amount_inr'].sum().sort_values(ascending=False)
        axes[1, 1].scatter(customer_freq, revenue_per_freq, alpha=0.3, s=20)
        axes[1, 1].set_title('Frequency vs Customer Lifetime Value', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Purchase Frequency')
        axes[1, 1].set_ylabel('Total Revenue (INR)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig, {'avg_frequency': customer_freq.mean(), 'max_frequency': customer_freq.max(), 'one_time_rate': (customer_freq == 1).sum()/len(customer_freq)*100}
    
    def q20_business_health_dashboard(self) -> Tuple[plt.Figure, Dict]:
        """Question 20: Business health executive dashboard"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Key metrics
        summary = self.generate_summary()
        
        # Total Revenue (large card)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.text(0.5, 0.5, f"₹{summary['total_revenue']/1e7:.1f}Cr", ha='center', va='center', fontsize=24, fontweight='bold')
        ax1.text(0.5, 0.1, 'Total Revenue', ha='center', va='center', fontsize=12)
        ax1.axis('off')
        ax1.set_facecolor('#E8F5E9')
        
        # Total Orders
        ax2 = fig.add_subplot(gs[0, 1])
        total_orders = len(self.df)
        ax2.text(0.5, 0.5, f"{total_orders/1e3:.0f}K", ha='center', va='center', fontsize=24, fontweight='bold')
        ax2.text(0.5, 0.1, 'Total Orders', ha='center', va='center', fontsize=12)
        ax2.axis('off')
        ax2.set_facecolor('#E3F2FD')
        
        # Unique Customers
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.text(0.5, 0.5, f"{summary['unique_customers']/1000:.0f}K", ha='center', va='center', fontsize=24, fontweight='bold')
        ax3.text(0.5, 0.1, 'Unique Customers', ha='center', va='center', fontsize=12)
        ax3.axis('off')
        ax3.set_facecolor('#FFF3E0')
        
        # AOV
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.text(0.5, 0.5, f"₹{summary['avg_order_value']/1000:.1f}K", ha='center', va='center', fontsize=24, fontweight='bold')
        ax4.text(0.5, 0.1, 'Avg Order Value', ha='center', va='center', fontsize=12)
        ax4.axis('off')
        ax4.set_facecolor('#F3E5F5')
        
        # Categories
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.text(0.5, 0.5, f"{summary['unique_categories']}", ha='center', va='center', fontsize=24, fontweight='bold')
        ax5.text(0.5, 0.1, 'Active Categories', ha='center', va='center', fontsize=12)
        ax5.axis('off')
        ax5.set_facecolor('#FCE4EC')
        
        # Time Period
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.text(0.5, 0.5, summary['time_period'], ha='center', va='center', fontsize=18, fontweight='bold')
        ax6.text(0.5, 0.1, 'Time Period', ha='center', va='center', fontsize=12)
        ax6.axis('off')
        ax6.set_facecolor('#E0F2F1')
        
        # Revenue trend mini
        ax7 = fig.add_subplot(gs[2, :2])
        yearly = self.df.groupby('order_year')['final_amount_inr'].sum()
        ax7.plot(yearly.index, yearly.values/1e7, marker='o', linewidth=2, color='#FF9900')
        ax7.fill_between(yearly.index, yearly.values/1e7, alpha=0.3, color='#FF9900')
        ax7.set_title('Revenue Trend', fontsize=11, fontweight='bold')
        ax7.set_ylabel('Revenue (Crores ₹)')
        ax7.grid(True, alpha=0.3)
        
        # Top category mini pie
        ax8 = fig.add_subplot(gs[2, 2])
        if 'category' in self.df.columns:
            top_cat = self.df.groupby('category')['final_amount_inr'].sum().nlargest(5)
            ax8.pie(top_cat.values, labels=top_cat.index, autopct='%1.0f%%', textprops={'fontsize': 8})
            ax8.set_title('Top 5 Categories', fontsize=11, fontweight='bold')
        
        plt.suptitle('Business Health Dashboard', fontsize=16, fontweight='bold', y=0.98)
        return fig, summary
    
    def generate_summary(self) -> Dict:
        """Generate summary of all analyses"""
        return {
            'total_records': len(self.df),
            'time_period': f"{self.df['order_year'].min()}-{self.df['order_year'].max()}",
            'total_revenue': self.df['final_amount_inr'].sum(),
            'avg_order_value': self.df['final_amount_inr'].mean(),
            'unique_customers': self.df['customer_id'].nunique() if 'customer_id' in self.df.columns else 0,
            'unique_categories': self.df['category'].nunique() if 'category' in self.df.columns else 0
        }
    
    # ==================== Method Aliases for Dashboard Compatibility ====================
    # These aliases ensure the dashboard can call methods with the expected names
    
    def q2_seasonal_pattern_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q2_seasonal_patterns"""
        return self.q2_seasonal_patterns()
    
    def q3_rfm_segmentation_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q3_rfm_segmentation"""
        return self.q3_rfm_segmentation()
    
    def q4_payment_method_evolution(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q4_payment_evolution"""
        return self.q4_payment_evolution()
    
    def q5_category_performance_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q5_category_performance"""
        return self.q5_category_performance()
    
    def q6_prime_membership_impact(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q6_prime_impact"""
        return self.q6_prime_impact()
    
    def q8_festival_impact_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q8_festival_impact"""
        return self.q8_festival_impact()
    
    def q9_rating_distribution_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q9_customer_rating_patterns"""
        return self.q9_customer_rating_patterns()
    
    def q10_price_demand_relationship(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q10_price_demand_analysis"""
        return self.q10_price_demand_analysis()
    
    def q11_delivery_performance_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q11_delivery_performance"""
        return self.q11_delivery_performance()
    
    def q12_return_satisfaction_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q12_return_satisfaction"""
        return self.q12_return_satisfaction()
    
    def q13_discount_effectiveness_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q13_discount_effectiveness"""
        return self.q13_discount_effectiveness()
    
    def q14_customer_lifetime_value_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q14_revenue_per_customer_clv"""
        return self.q14_revenue_per_customer_clv()
    
    def q15_category_trend_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q15_category_trends"""
        return self.q15_category_trends()
    
    def q16_revenue_volatility_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q16_monthly_revenue_volatility"""
        return self.q16_monthly_revenue_volatility()
    
    def q18_customer_acquisition_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q18_customer_acquisition_retention"""
        return self.q18_customer_acquisition_retention()
    
    def q19_customer_retention_analysis(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q19_customer_frequency_distribution"""
        return self.q19_customer_frequency_distribution()
    
    def q20_executive_dashboard(self) -> Tuple[plt.Figure, Dict]:
        """Alias for q20_business_health_dashboard"""
        return self.q20_business_health_dashboard()
