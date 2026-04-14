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
    tab_overview, tab_revenue, tab_business, tab_customer, tab_product, tab_promo, tab_evolution, tab_lifecycle, tab_executive, tab_details = st.tabs([
        "📋 Overview",
        "💰 Revenue & Time (Q1-Q3)",
        "🏢 Business Dims (Q4-Q6)", 
        "👥 Customer & Location (Q7-Q9)",
        "📦 Product & Price (Q10-Q12)",
        "🎯 Promotions (Q13-Q14)",
        "📈 Evolution (Q15-Q17)",
        "🔄 Lifecycle (Q18-Q19)",
        "🎖️ Executive (Q20)",
        "📊 Raw Data"
    ])
    
    # OVERVIEW TAB
    with tab_overview:
        st.markdown("## Dashboard Overview")
        col1, col2 = st.columns(2)
        with col1:
            render_revenue_analytics(filtered_df)
        with col2:
            render_customer_analytics(filtered_df)
        render_payment_analytics(filtered_df)
    
    # REVENUE & TIME TAB (Q1-Q3)
    with tab_revenue:
        if analyzer:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Q1: Revenue Trend")
                try:
                    fig, stats = analyzer.q1_revenue_trend_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q2: Seasonal Pattern")
                try:
                    fig, stats = analyzer.q2_seasonal_pattern_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col3:
                st.markdown("### Q3: RFM Segmentation")
                try:
                    fig, stats = analyzer.q3_rfm_segmentation_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # BUSINESS DIMENSIONS TAB (Q4-Q6)
    with tab_business:
        if analyzer:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Q4: Payment Evolution")
                try:
                    fig, stats = analyzer.q4_payment_method_evolution()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q5: Category Performance")
                try:
                    fig, stats = analyzer.q5_category_performance_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col3:
                st.markdown("### Q6: Prime Membership Impact")
                try:
                    fig, stats = analyzer.q6_prime_membership_impact()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # CUSTOMER & LOCATION TAB (Q7-Q9)
    with tab_customer:
        if analyzer:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Q7: Geographic Analysis")
                try:
                    fig, stats = analyzer.q7_geographic_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q8: Festival Impact")
                try:
                    fig, stats = analyzer.q8_festival_impact_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col3:
                st.markdown("### Q9: Rating Distribution")
                try:
                    fig, stats = analyzer.q9_rating_distribution_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # PRODUCT & PRICE TAB (Q10-Q12)
    with tab_product:
        if analyzer:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Q10: Price-Demand")
                try:
                    fig, stats = analyzer.q10_price_demand_relationship()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q11: Delivery Performance")
                try:
                    fig, stats = analyzer.q11_delivery_performance_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col3:
                st.markdown("### Q12: Return Satisfaction")
                try:
                    fig, stats = analyzer.q12_return_satisfaction_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # PROMOTIONS TAB (Q13-Q14)
    with tab_promo:
        if analyzer:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Q13: Discount Effectiveness")
                try:
                    fig, stats = analyzer.q13_discount_effectiveness_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q14: Customer Lifetime Value")
                try:
                    fig, stats = analyzer.q14_customer_lifetime_value_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # EVOLUTION TAB (Q15-Q17)
    with tab_evolution:
        if analyzer:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### Q15: Category Trends")
                try:
                    fig, stats = analyzer.q15_category_trend_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q16: Revenue Volatility")
                try:
                    fig, stats = analyzer.q16_revenue_volatility_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col3:
                st.markdown("### Q17: Top Products")
                try:
                    fig, stats = analyzer.q17_top_products_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # LIFECYCLE TAB (Q18-Q19)
    with tab_lifecycle:
        if analyzer:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Q18: Customer Acquisition")
                try:
                    fig, stats = analyzer.q18_customer_acquisition_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            with col2:
                st.markdown("### Q19: Retention Analysis")
                try:
                    fig, stats = analyzer.q19_customer_retention_analysis()
                    st.pyplot(fig)
                    st.json(stats)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # EXECUTIVE DASHBOARD TAB (Q20)
    with tab_executive:
        if analyzer:
            st.markdown("### Q20: Business Health - Executive Dashboard")
            try:
                fig, stats = analyzer.q20_executive_dashboard()
                st.pyplot(fig)
                st.json(stats)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("EDA Analyzer not available")
    
    # RAW DATA TAB
    with tab_details:
        st.markdown('## Transaction Details')
        st.dataframe(filtered_df.head(100), use_container_width=True)
        
        # Download data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="amazon_india_filtered_data.csv",
            mime="text/csv"
        )
    
    st.divider()
    
    # Footer
    st.markdown("""
        <div style='text-align: center; color: gray; margin-top: 2rem;'>
        <p>Amazon India Analytics Platform | Data Period: 2015-2025</p>
        <p>20 Comprehensive EDA Questions + Executive Dashboard</p>
        <p>Built with Streamlit, Pandas, and Python</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
