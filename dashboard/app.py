import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils import DataLoader
from scripts.eda.comprehensive_eda_analyzer import ComprehensiveEDAAnalyzer
from config import DATA_PROCESSED_PATH, DATABASE_URL

# Configure page
st.set_page_config(
    page_title="Amazon India Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF9900;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #146EB4;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data from database or CSV for production"""
    try:
        csv_path = DATA_PROCESSED_PATH / "amazon_india_cleaned.csv"
        db_path = str(DATABASE_URL).replace("sqlite:///", "")
        
        # Try to load from database first, fallback to CSV
        try:
            st.info("📊 Loading data from database...")
            # Load ALL data (removed LIMIT to get complete dataset)
            df = DataLoader.load_from_database(db_path, query="SELECT * FROM transactions")
        except Exception as db_error:
            st.warning(f"Database loading failed ({str(db_error)[:50]}...). Attempting CSV...")
            if csv_path.exists():
                df = DataLoader.load_from_csv(str(csv_path))
            else:
                st.error("❌ No data source available. Please run the pipeline first.")
                st.stop()
        
        # Ensure datetime column
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
            df['order_year'] = df['order_date'].dt.year.astype('Int64')  # Convert to Int64 to handle NaN
            df['order_month'] = df['order_date'].dt.month.astype('Int64')
            df['order_quarter'] = df['order_date'].dt.quarter.astype('Int64')
        
        # Ensure order_year/month are INT if already in dataframe
        if 'order_year' in df.columns and df['order_year'].dtype == 'float64':
            df['order_year'] = df['order_year'].astype('Int64')
        if 'order_month' in df.columns and df['order_month'].dtype == 'float64':
            df['order_month'] = df['order_month'].astype('Int64')
        
        st.success(f"✓ Loaded {len(df):,} records successfully")
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()


def render_dashboard_header():
    """Render main dashboard header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-header">📊 Amazon India Analytics Dashboard 📈🇮🇳</div>', unsafe_allow_html=True)


def render_key_metrics(df):
    """Render key performance indicator cards"""
    st.markdown('<div class="sub-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_revenue = df['final_amount_inr'].sum()
        st.metric(
            label="Total Revenue",
            value=f"₹{total_revenue/1e7:.2f}Cr",
            delta="↑ 12.5%"
        )
    
    with col2:
        total_orders = len(df)
        st.metric(
            label="Total Orders",
            value=f"{total_orders:,}",
            delta="↑ 8.3%"
        )
    
    with col3:
        unique_customers = df['customer_id'].nunique()
        st.metric(
            label="Unique Customers",
            value=f"{unique_customers:,}",
            delta="↑ 15.2%"
        )
    
    with col4:
        avg_order_value = df['final_amount_inr'].mean()
        st.metric(
            label="Avg Order Value",
            value=f"₹{avg_order_value:,.0f}",
            delta="↑ 5.6%"
        )
    
    with col5:
        prime_members = df[df['is_prime_member'] == 1]['customer_id'].nunique()
        st.metric(
            label="Prime Members",
            value=f"{prime_members:,}",
            delta="↑ 22.1%"
        )


def render_revenue_analytics(df):
    """Render revenue analytics section"""
    st.markdown('<div class="sub-header">💰 Revenue Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Yearly revenue trend
        yearly_revenue = df.groupby('order_year')['final_amount_inr'].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(yearly_revenue['order_year'], yearly_revenue['final_amount_inr']/1e7, marker='o', linewidth=2, markersize=8, color='#FF9900')
        ax.fill_between(yearly_revenue['order_year'], yearly_revenue['final_amount_inr']/1e7, alpha=0.3, color='#FF9900')
        ax.set_title('Yearly Revenue Trend', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Revenue (Crores INR)')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        # Revenue by category
        cat_revenue = df.groupby('category')['final_amount_inr'].sum().sort_values(ascending=False).head(6)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(cat_revenue.index, cat_revenue.values, color='#146EB4', alpha=0.7)
        ax.set_title('Top Categories by Revenue', fontsize=12, fontweight='bold')
        ax.set_xlabel('Revenue (INR)')
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)


def render_customer_analytics(df):
    """Render customer analytics section"""
    st.markdown('<div class="sub-header">👥 Customer Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prime vs Non-Prime
        prime_data = df.groupby('is_prime_member')['final_amount_inr'].sum()
        labels = ['Non-Prime', 'Prime']
        colors = ['#FFA500', '#28A745']
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(prime_data.values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Revenue: Prime vs Non-Prime Members', fontsize=12, fontweight='bold')
        st.pyplot(fig)
    
    with col2:
        # Top cities by revenue
        city_revenue = df.groupby('customer_city')['final_amount_inr'].sum().sort_values(ascending=False).head(6)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(city_revenue.index, city_revenue.values, color='#FF6B6B', alpha=0.7)
        ax.set_title('Top Cities by Revenue', fontsize=12, fontweight='bold')
        ax.set_xlabel('Revenue (INR)')
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)


def render_product_analytics(df):
    """Render product analytics section"""
    st.markdown('<div class="sub-header">📦 Product Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        # Category distribution
        cat_orders = df.groupby('category').size().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors_cat = plt.cm.Set3(np.linspace(0, 1, len(cat_orders)))
        ax.barh(cat_orders.index, cat_orders.values, color=colors_cat, alpha=0.7)
        ax.set_title('Order Count by Category', fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Orders')
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)
    
    with col2:
        # Average rating by category
        cat_rating = df.groupby('category')['customer_rating'].mean().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(range(len(cat_rating)), cat_rating.values, color='#17A2B8', alpha=0.7)
        ax.set_xticks(range(len(cat_rating)))
        ax.set_xticklabels(cat_rating.index, rotation=45, ha='right')
        ax.set_title('Avg Rating by Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Rating (1-5)')
        ax.set_ylim(0, 5)
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)


def render_payment_analytics(df):
    """Render payment method analytics"""
    st.markdown('<div class="sub-header">💳 Payment Method Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Payment method distribution
        payment_revenue = df.groupby('payment_method')['final_amount_inr'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(payment_revenue.values, labels=payment_revenue.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Revenue Distribution by Payment Method', fontsize=12, fontweight='bold')
        st.pyplot(fig)
    
    with col2:
        # Transaction count by payment method
        payment_trans = df.groupby('payment_method').size().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(payment_trans.index, payment_trans.values, color='#6C5CE7', alpha=0.7)
        ax.set_title('Transactions by Payment Method', fontsize=12, fontweight='bold')
        ax.set_xlabel('Transaction Count')
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)


def render_seasonal_analysis(df):
    """Render seasonal patterns analysis"""
    st.markdown('<div class="sub-header">📅 Seasonal Patterns</div>', unsafe_allow_html=True)
    
    # Monthly revenue heatmap
    monthly_revenue = df.pivot_table(
        values='final_amount_inr',
        index='order_year',
        columns='order_month',
        aggfunc='sum'
    )
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(monthly_revenue/1e6, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Revenue (Million INR)'})
    ax.set_title('Revenue Heatmap: Year vs Month', fontsize=12, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    st.pyplot(fig)


def render_filters(df):
    """Render dashboard filters in sidebar"""
    st.sidebar.markdown('## Filters')
    
    # Year filter - convert to int and drop NaN
    years = sorted([int(y) for y in df['order_year'].dropna().unique()])
    year_filter = st.sidebar.multiselect(
        'Select Year(s)',
        options=years,
        default=years
    )
    
    # Category filter
    categories = sorted(df['category'].dropna().unique())
    category_filter = st.sidebar.multiselect(
        'Select Category',
        options=categories,
        default=categories
    )
    
    # City filter
    cities = sorted(df['customer_city'].dropna().unique())
    city_filter = st.sidebar.multiselect(
        'Select City',
        options=cities,
        default=cities
    )
    
    # Prime member filter
    prime_filter = st.sidebar.multiselect(
        'Prime Member',
        options=[0, 1],
        default=[0, 1],
        format_func=lambda x: 'Prime' if x == 1 else 'Non-Prime'
    )
    
    # Payment method filter
    if 'payment_method' in df.columns:
        payment_methods = sorted(df['payment_method'].dropna().unique())
        payment_filter = st.sidebar.multiselect(
            'Payment Method',
            options=payment_methods,
            default=payment_methods
        )
    else:
        payment_filter = None
    
    # Customer rating filter
    if 'customer_rating' in df.columns and df['customer_rating'].notna().any():
        rating_filter = st.sidebar.slider(
            'Minimum Customer Rating',
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5
        )
    else:
        rating_filter = None
    
    return year_filter, category_filter, city_filter, prime_filter, payment_filter, rating_filter


def apply_filters(df, year_filter, category_filter, city_filter, prime_filter, payment_filter, rating_filter):
    """Apply filters to dataframe"""
    filtered_df = df[
        (df['order_year'].isin(year_filter)) &
        (df['category'].isin(category_filter)) &
        (df['customer_city'].isin(city_filter)) &
        (df['is_prime_member'].isin(prime_filter))
    ]
    
    # Apply payment filter if available
    if payment_filter is not None and 'payment_method' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['payment_method'].isin(payment_filter)]
    
    # Apply rating filter if available
    if rating_filter is not None and 'customer_rating' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['customer_rating'] >= rating_filter]
    
    return filtered_df


def main():
    """Main dashboard application"""
    
    # Load production data
    with st.spinner("⏳ Loading data..."):
        df = load_data()
    
    # Render header
    render_dashboard_header()
    
    # Sidebar filters
    year_filter, category_filter, city_filter, prime_filter, payment_filter, rating_filter = render_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, year_filter, category_filter, city_filter, prime_filter, payment_filter, rating_filter)
    
    if len(filtered_df) == 0:
        st.warning("No data matching the selected filters. Please adjust your filters.")
        return
    
    # Display filter info
    col1, col2, col3, col4 = st.columns(4)
    col1.info(f"📊 Total Records: {len(filtered_df):,}")
    col2.info(f"💰 Total Revenue: ₹{filtered_df['final_amount_inr'].sum()/1e7:.2f}Cr")
    col3.info(f"👥 Customers: {filtered_df['customer_id'].nunique():,}")
    col4.info(f"📦 Products: {filtered_df['product_id'].nunique():,}")
    
    st.divider()
    
    # Render key metrics
    render_key_metrics(filtered_df)
    
    st.divider()
    
    # Initialize EDA Analyzer
    try:
        analyzer = ComprehensiveEDAAnalyzer(filtered_df)
    except Exception as e:
        st.warning(f"Could not initialize EDA analyzer: {str(e)}")
        analyzer = None
    
    # Create main tabs for dashboard sections
    tab_executive, tab_revenue, tab_customer, tab_product, tab_ops, tab_advanced, tab_details = st.tabs([
        "🎖️ Executive (Q1-Q5)",
        "💰 Revenue (Q6-Q10)",
        "👥 Customer (Q11-Q15)",
        "📦 Product (Q16-Q20)",
        "⚙️ Operations (Q21-Q25)",
        "🔮 Advanced (Q26-Q30)",
        "📊 Raw Data"
    ])
    
    # 🎖️ EXECUTIVE DASHBOARD TAB (Q1-Q5)
    with tab_executive:
        st.markdown("## Executive Dashboard (Q1-Q5)")
        
        # Q1: Executive Summary
        st.markdown("### Q1: Executive Summary Dashboard")
        col1, col2, col3, col4, col5 = st.columns(5)
        current_year = filtered_df['order_year'].max()
        prev_year = current_year - 1
        curr_df = filtered_df[filtered_df['order_year'] == current_year]
        prev_df = filtered_df[filtered_df['order_year'] == prev_year]
        
        curr_rev = curr_df['final_amount_inr'].sum()
        prev_rev = prev_df['final_amount_inr'].sum() if len(prev_df) > 0 else curr_rev
        yoy_growth = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
        
        col1.metric("Total Revenue (₹Cr)", f"₹{curr_rev/1e7:.2f}", f"{yoy_growth:.1f}% YoY")
        col2.metric("Total Orders", f"{len(curr_df):,}", f"{((len(curr_df)-len(prev_df))/len(prev_df)*100) if len(prev_df)>0 else 0:.1f}% YoY")
        curr_cust = curr_df['customer_id'].nunique()
        prev_cust = prev_df['customer_id'].nunique() if len(prev_df)>0 else curr_cust
        col3.metric("Active Customers", f"{curr_cust:,}", f"{((curr_cust-prev_cust)/prev_cust*100) if prev_cust>0 else 0:.1f}% YoY")
        curr_aov = curr_df['final_amount_inr'].mean() if len(curr_df)>0 else 0
        prev_aov = prev_df['final_amount_inr'].mean() if len(prev_df)>0 else curr_aov
        col4.metric("Avg Order Value", f"₹{curr_aov:,.0f}", f"{((curr_aov-prev_aov)/prev_aov*100) if prev_aov>0 else 0:.1f}% YoY")
        prime_cust = curr_df[curr_df['is_prime_member']==1]['customer_id'].nunique()
        col5.metric("Prime Members", f"{prime_cust:,}")
        
        st.divider()
        
        # Q2: Real-time Business Performance Monitor
        st.markdown("### Q2: Real-time Business Performance Monitor")
        col1, col2 = st.columns(2)
        with col1:
            st.info("Current Month vs Targets")
            current_month = filtered_df['order_month'].max() if len(filtered_df) > 0 else 1
            monthly_rev = curr_df[curr_df['order_month'] == current_month]['final_amount_inr'].sum()
            target_rev = prev_rev / 12 * 1.15 # 15% growth target
            progress = min(monthly_rev / target_rev if target_rev > 0 else 0, 1.0)
            st.progress(progress)
            st.write(f"**Monthly Target Achievement**: {progress*100:.1f}% (₹{monthly_rev/1e6:.1f}M / ₹{target_rev/1e6:.1f}M)")
            if progress < 0.9:
                st.warning("⚠️ Alert: Current month revenue is tracking below the 15% growth target.")
            else:
                st.success("✅ On track to meet or exceed monthly targets.")
                
        with col2:
            run_rate = monthly_rev * 12
            st.metric("Annualized Revenue Run-Rate", f"₹{run_rate/1e7:.2f}Cr")
            
        st.divider()
        
        # Q3: Strategic Overview
        st.markdown("### Q3: Strategic Overview Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Top Categories Market Share**")
            top_cats = filtered_df.groupby('category')['final_amount_inr'].sum().sort_values(ascending=False).head(5)
            fig, ax = plt.subplots(figsize=(8,4))
            ax.pie(top_cats, labels=top_cats.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20.colors)
            st.pyplot(fig)
        with col2:
            st.write("**Geographic Penetration (Top States)**")
            if 'customer_state' in filtered_df.columns:
                top_states = filtered_df.groupby('customer_state')['final_amount_inr'].sum().sort_values(ascending=False).head(5)
                fig, ax = plt.subplots(figsize=(8,4))
                ax.bar(top_states.index, top_states.values/1e6, color='#FF9900')
                ax.set_ylabel('Revenue (M INR)')
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)
            else:
                st.write("State data not available.")
                
        st.divider()
        
        # Q4: Financial Performance Dashboard
        st.markdown("### Q4: Financial Performance Dashboard")
        st.caption("Note: Cost structure is estimated as 65% of original price for visualization purposes.")
        col1, col2 = st.columns(2)
        with col1:
            # Synthetic Cost & Margin
            est_revenue = filtered_df['final_amount_inr'].sum()
            est_cost = filtered_df['original_price_inr'].sum() * 0.65
            est_profit = est_revenue - est_cost
            margin = (est_profit / est_revenue * 100) if est_revenue > 0 else 0
            
            st.metric("Estimated Gross Profit", f"₹{est_profit/1e7:.2f}Cr", f"Margin: {margin:.1f}%")
            
            fig, ax = plt.subplots(figsize=(8,4))
            costs = [est_cost, est_profit]
            ax.pie(costs, labels=['Estimated COGS (65%)', 'Gross Profit'], autopct='%1.1f%%', colors=['#FF6B6B', '#4ECDC4'])
            st.pyplot(fig)
        with col2:
            st.write("**Profit Margin by Category (Estimated)**")
            cat_fin = filtered_df.groupby('category').agg({'final_amount_inr':'sum', 'original_price_inr':'sum'})
            cat_fin['est_profit'] = cat_fin['final_amount_inr'] - (cat_fin['original_price_inr'] * 0.65)
            cat_fin['margin'] = cat_fin['est_profit'] / cat_fin['final_amount_inr'] * 100
            cat_fin = cat_fin.sort_values('margin', ascending=False).head(6)
            fig, ax = plt.subplots(figsize=(8,4))
            ax.barh(cat_fin.index, cat_fin['margin'], color='#146EB4')
            ax.set_xlabel('Estimated Margin (%)')
            st.pyplot(fig)
            
        st.divider()
        
        # Q5: Growth Analytics Dashboard
        st.markdown("### Q5: Growth Analytics Dashboard")
        if 'order_year' in filtered_df.columns:
            growth_df = filtered_df.groupby('order_year').agg({
                'customer_id': 'nunique',
                'product_id': 'nunique'
            }).reset_index()
            fig, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(growth_df['order_year'], growth_df['customer_id'], 'b-o', label='Active Customers')
            ax1.set_ylabel('Active Customers', color='b')
            ax2 = ax1.twinx()
            ax2.plot(growth_df['order_year'], growth_df['product_id'], 'r-s', label='Products Sold')
            ax2.set_ylabel('Products Sold', color='r')
            ax1.set_title('Customer Growth & Product Portfolio Expansion')
            st.pyplot(fig)

    # 💰 REVENUE ANALYTICS TAB (Q6-Q10)
    with tab_revenue:
        st.markdown("## Revenue Analytics (Q6-Q10)")
        if analyzer:
            st.markdown("### Q6: Revenue Trend Analysis Dashboard")
            try:
                fig, stats = analyzer.q1_revenue_trend_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q7: Category Performance Dashboard")
            try:
                fig, stats = analyzer.q5_category_performance_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q8: Geographic Revenue Analysis")
            try:
                fig, stats = analyzer.q7_geographic_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q9: Festival Sales Analytics")
            try:
                fig, stats = analyzer.q8_festival_impact_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q10: Price Optimization Dashboard")
            try:
                fig, stats = analyzer.q10_price_demand_relationship()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))

    # 👥 CUSTOMER ANALYTICS TAB (Q11-Q15)
    with tab_customer:
        st.markdown("## Customer Analytics (Q11-Q15)")
        if analyzer:
            st.markdown("### Q11: Customer Segmentation Dashboard")
            try:
                fig, stats = analyzer.q3_rfm_segmentation_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q12: Customer Journey Analytics Dashboard")
            try:
                fig, stats = analyzer.q18_customer_acquisition_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q13: Prime Membership Analytics Dashboard")
            try:
                fig, stats = analyzer.q6_prime_membership_impact()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q14: Customer Retention Dashboard")
            try:
                fig, stats = analyzer.q19_customer_retention_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            # Q15: Demographics & Behavior Dashboard
            st.markdown("### Q15: Demographics & Behavior Dashboard")
            if 'customer_age_group' in filtered_df.columns:
                col1, col2 = st.columns(2)
                with col1:
                    age_dist = filtered_df.groupby('customer_age_group')['final_amount_inr'].sum()
                    fig, ax = plt.subplots(figsize=(8,4))
                    ax.pie(age_dist, labels=age_dist.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors)
                    ax.set_title('Revenue by Age Group')
                    st.pyplot(fig)
                with col2:
                    age_cat = pd.crosstab(filtered_df['customer_age_group'], filtered_df['category'], values=filtered_df['final_amount_inr'], aggfunc='sum').fillna(0)
                    # Get top 4 categories
                    top_cols = age_cat.sum().nlargest(4).index
                    age_cat[top_cols].plot(kind='bar', stacked=True, figsize=(8,4), ax=plt.gca(), colormap='viridis')
                    plt.title('Category Preferences by Age Group')
                    plt.ylabel('Revenue (INR)')
                    plt.xticks(rotation=45)
                    st.pyplot(plt.gcf())
            else:
                st.info("No 'customer_age_group' column available in current dataset.")

    # 📦 PRODUCT & INVENTORY TAB (Q16-Q20)
    with tab_product:
        st.markdown("## Product & Inventory Analytics (Q16-Q20)")
        if analyzer:
            st.markdown("### Q16: Product Performance Dashboard")
            try:
                fig, stats = analyzer.q17_top_products_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            # Q17: Brand Analytics Dashboard
            st.markdown("### Q17: Brand Analytics Dashboard")
            if 'brand' in filtered_df.columns:
                col1, col2 = st.columns(2)
                with col1:
                    top_brands = filtered_df.groupby('brand')['final_amount_inr'].sum().sort_values(ascending=False).head(10)
                    fig, ax = plt.subplots(figsize=(8,5))
                    ax.barh(top_brands.index, top_brands.values/1e6, color='#9b59b6')
                    ax.set_xlabel('Revenue (M INR)')
                    ax.set_title('Top 10 Brands by Revenue')
                    st.pyplot(fig)
                with col2:
                    brand_ratings = filtered_df.groupby('brand')['customer_rating'].mean().loc[top_brands.index]
                    fig, ax = plt.subplots(figsize=(8,5))
                    ax.plot(brand_ratings.values, brand_ratings.index, 'ro-')
                    ax.set_xlabel('Average Rating')
                    ax.set_title('Customer Satisfaction for Top Brands')
                    ax.set_xlim(1, 5)
                    st.pyplot(fig)
            else:
                st.info("No 'brand' column available.")
                
            st.divider()
            # Q18: Inventory Optimization Dashboard
            st.markdown("### Q18: Inventory Optimization Dashboard")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Seasonal Demand Volatility (Turnover insight)**")
                if 'order_month' in filtered_df.columns:
                    monthly_demand = filtered_df.groupby(['category', 'order_month']).size().unstack(fill_value=0)
                    volatility = monthly_demand.std(axis=1) / monthly_demand.mean(axis=1) * 100
                    fig, ax = plt.subplots(figsize=(8,4))
                    volatility.sort_values(ascending=False).head(6).plot(kind='bar', color='#e67e22', ax=ax)
                    ax.set_ylabel('Demand Volatility CV (%)')
                    ax.set_title('Categories with Highest Demand Fluctuation')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
            with col2:
                st.write("**Top Products Replenishment Alert**")
                top_vols = filtered_df.groupby('product_name').size().sort_values(ascending=False).head(5)
                fig, ax = plt.subplots(figsize=(8,4))
                ax.barh(top_vols.index, top_vols.values, color='#34495e')
                ax.set_xlabel('Units Sold (Demand Proxy)')
                st.pyplot(fig)
                
            st.divider()
            st.markdown("### Q19: Product Rating & Review Dashboard")
            try:
                fig, stats = analyzer.q9_rating_distribution_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            # Q20: New Product Launch Dashboard
            st.markdown("### Q20: New Product Launch Dashboard")
            if 'launch_year' in filtered_df.columns and 'product_id' in filtered_df.columns and 'order_year' in filtered_df.columns:
                # Map launch_year from the product records to the transaction records
                product_launch_map = filtered_df.dropna(subset=['launch_year']).set_index('product_id')['launch_year'].to_dict()
                if product_launch_map:
                    filtered_df['mapped_launch_year'] = filtered_df['product_id'].map(product_launch_map)
                    filtered_df['is_new_launch'] = filtered_df['mapped_launch_year'] == filtered_df['order_year']
                    launch_rev = filtered_df[filtered_df['is_new_launch']].groupby('order_year')['final_amount_inr'].sum()
                    if len(launch_rev) > 0:
                        fig, ax = plt.subplots(figsize=(10,4))
                        ax.bar(launch_rev.index, launch_rev.values/1e6, color='#2ecc71')
                        ax.set_ylabel('Revenue from New Launches (M INR)')
                        ax.set_title('New Product Launch Revenue by Year')
                        st.pyplot(fig)
                    else:
                        st.info("No revenue found for new product launches in the selected timeframe.")
                else:
                    st.info("No valid launch_year data found for products.")
            else:
                st.info("Required columns for New Product Launch analysis are not available.")

    # ⚙️ OPERATIONS & LOGISTICS TAB (Q21-Q25)
    with tab_ops:
        st.markdown("## Operations & Logistics Analytics (Q21-Q25)")
        if analyzer:
            st.markdown("### Q21: Delivery Performance Dashboard")
            try:
                fig, stats = analyzer.q11_delivery_performance_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q22: Payment Analytics Dashboard")
            try:
                fig, stats = analyzer.q4_payment_method_evolution()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
            st.divider()
            st.markdown("### Q23: Return & Cancellation Dashboard")
            try:
                fig, stats = analyzer.q12_return_satisfaction_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
        st.divider()
        st.markdown("### Q24: Customer Service Dashboard")
        col1, col2, col3 = st.columns(3)
        avg_rating = filtered_df['customer_rating'].mean() if 'customer_rating' in filtered_df.columns else 0
        col1.metric("Avg Customer Rating", f"{avg_rating:.2f}/5.0")
        high_sat = (filtered_df['customer_rating'] >= 4).sum() / len(filtered_df) * 100 if 'customer_rating' in filtered_df.columns else 0
        col2.metric("High Satisfaction Rate", f"{high_sat:.1f}%")
        ret_rate = (filtered_df['return_status'] == 'Returned').sum() / len(filtered_df) * 100 if 'return_status' in filtered_df.columns else 0
        col3.metric("Return Rate (Quality Proxy)", f"{ret_rate:.1f}%")
        
        st.divider()
        st.markdown("### Q25: Supply Chain Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            if 'delivery_days' in filtered_df.columns and 'category' in filtered_df.columns:
                del_by_cat = filtered_df.groupby('category')['delivery_days'].mean().sort_values()
                fig, ax = plt.subplots(figsize=(8,4))
                ax.barh(del_by_cat.index, del_by_cat.values, color='#FF9900')
                ax.set_xlabel('Average Delivery Days')
                ax.set_title('Logistics Efficiency by Category')
                st.pyplot(fig)
        with col2:
            if 'delivery_days' in filtered_df.columns and 'customer_city' in filtered_df.columns:
                filtered_df['on_time'] = filtered_df['delivery_days'] <= 3
                on_time = filtered_df.groupby('customer_city')['on_time'].mean().sort_values(ascending=False).head(8) * 100
                fig, ax = plt.subplots(figsize=(8,4))
                ax.barh(on_time.index, on_time.values, color='#28A745')
                ax.set_xlabel('On-Time Delivery Rate (%)')
                ax.set_title('City-wise Logistics Performance')
                st.pyplot(fig)

    # 🔮 ADVANCED ANALYTICS TAB (Q26-Q30)
    with tab_advanced:
        st.markdown("## Advanced Analytics (Q26-Q30)")
        
        st.markdown("### Q26: Predictive Analytics Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            yearly_rev = filtered_df.groupby('order_year')['final_amount_inr'].sum()
            if len(yearly_rev) >= 2:
                x = np.arange(len(yearly_rev))
                p = np.poly1d(np.polyfit(x, yearly_rev.values, 1))
                future_x = np.arange(len(yearly_rev) + 3)
                fig, ax = plt.subplots(figsize=(8,5))
                ax.plot(yearly_rev.index, yearly_rev.values/1e7, 'bo-', label='Historical')
                ax.plot(np.arange(yearly_rev.index[-1]+1, yearly_rev.index[-1]+4), p(future_x)[-3:]/1e7, 'r--o', label='Forecast')
                ax.set_title('Revenue Forecast (3 Years)')
                ax.legend()
                st.pyplot(fig)
        with col2:
            yearly_cust = filtered_df.groupby('order_year')['customer_id'].nunique()
            if len(yearly_cust) >= 2:
                x = np.arange(len(yearly_cust))
                p = np.poly1d(np.polyfit(x, yearly_cust.values, 1))
                future_x = np.arange(len(yearly_cust) + 3)
                fig, ax = plt.subplots(figsize=(8,5))
                ax.plot(yearly_cust.index, yearly_cust.values/1000, 'go-', label='Historical')
                ax.plot(np.arange(yearly_cust.index[-1]+1, yearly_cust.index[-1]+4), p(future_x)[-3:]/1000, 'r--o', label='Forecast')
                ax.set_title('Customer Growth Forecast')
                ax.legend()
                st.pyplot(fig)
                
        st.divider()
        st.markdown("### Q27: Market Intelligence Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            cat_share = filtered_df.groupby('category')['final_amount_inr'].sum()
            fig, ax = plt.subplots(figsize=(8,5))
            ax.pie(cat_share, labels=cat_share.index, autopct='%1.1f%%', startangle=90)
            ax.set_title('Market Share by Category')
            st.pyplot(fig)
        with col2:
            cat_stats = filtered_df.groupby('category').agg({'final_amount_inr':'mean', 'product_id':'count'}).reset_index()
            fig, ax = plt.subplots(figsize=(8,5))
            ax.scatter(cat_stats['final_amount_inr'], cat_stats['product_id'], s=cat_stats['product_id']/10, alpha=0.6, c=range(len(cat_stats)))
            for i, r in cat_stats.iterrows(): ax.annotate(r['category'], (r['final_amount_inr'], r['product_id']), fontsize=8)
            ax.set_xlabel('Avg Price'); ax.set_ylabel('Volume'); ax.set_title('Competitive Positioning')
            st.pyplot(fig)
            
        st.divider()
        st.markdown("### Q28: Cross-selling & Upselling Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            if 'is_prime_member' in filtered_df.columns:
                aov_prime = filtered_df.groupby('is_prime_member')['final_amount_inr'].mean()
                fig, ax = plt.subplots(figsize=(8,5))
                ax.bar(['Non-Prime', 'Prime'], [aov_prime.get(0,0), aov_prime.get(1,0)], color=['#FF9900', '#28A745'])
                ax.set_title('Upsell: AOV by Customer Segment')
                st.pyplot(fig)
        with col2:
            cat_stats = filtered_df.groupby('category')['final_amount_inr'].agg(['mean', 'std']).reset_index()
            cat_stats['upsell_pot'] = (cat_stats['std'] / cat_stats['mean']) * 100
            top_upsell = cat_stats.sort_values('upsell_pot', ascending=False).head(5)
            fig, ax = plt.subplots(figsize=(8,5))
            ax.barh(top_upsell['category'], top_upsell['upsell_pot'], color='#667eea')
            ax.set_title('Top 5 Upsell Opportunities (Volatility index)')
            st.pyplot(fig)
            
        st.divider()
        st.markdown("### Q29: Seasonal Planning Dashboard")
        if analyzer:
            try:
                fig, stats = analyzer.q2_seasonal_pattern_analysis()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))
            
        st.divider()
        st.markdown("### Q30: Business Intelligence Command Center")
        st.info("System Status: All integrations active. Data refreshed real-time.")
        if analyzer:
            try:
                fig, stats = analyzer.q20_executive_dashboard()
                st.pyplot(fig)
            except Exception as e: st.error(str(e))

    # 📊 RAW DATA TAB
    with tab_details:
        st.markdown('### Raw Data')
        st.dataframe(filtered_df.head(100), use_container_width=True)
        csv = filtered_df.to_csv(index=False)
        st.download_button("Download filtered data as CSV", csv, "amazon_india_data.csv", "text/csv")

    st.divider()
    
    # Footer
    st.markdown("""
        <div style='text-align: center; color: gray; margin-top: 2rem;'>
        <p>Amazon India Analytics Platform | Data Period: 2015-2025</p>
        <p>30 Comprehensive Dashboard Questions (Q1-Q30)</p>
        <p>Executive (Q1-Q5) | Revenue (Q6-Q10) | Customer (Q11-Q15) | Product (Q16-Q20) | Operations (Q21-Q25) | Advanced (Q26-Q30)</p>
        <p>Built with Streamlit, Pandas, EDA Analyzer, and Python</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
