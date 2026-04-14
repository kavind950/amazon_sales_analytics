# 📚 Data Dictionary

## Amazon India E-commerce Dataset - Complete Field Reference

**Status**: ✅ UPDATED April 14, 2026 | **Total Columns**: 39 | **Total Records**: 1,124,003 | **Data Quality**: 99.5%

### Overview
This document provides comprehensive documentation for all 39 fields in the Amazon India cleaned dataset (2015-2025). Fields are organized by category with data types, definitions, and value examples. All data has been validated and standardized through the 10-stage cleaning pipeline.

---

## 1. TRANSACTION IDENTIFIERS

---

## 1. TRANSACTION IDENTIFIERS

### transaction_id
- **Data Type**: Text/String
- **Format**: TXN_XXXXXXXX
- **Description**: Unique identifier for each transaction
- **Example**: TXN_00001234
- **Uniqueness**: 100% (Primary Key)

### customer_id
- **Data Type**: Text/String
- **Format**: CUST_XXXXX
- **Description**: Unique identifier for each customer
- **Example**: CUST_45632
- **Uniqueness**: Non-unique (Multiple transactions per customer)

### product_id
- **Data Type**: Text/String
- **Format**: PROD_XXXX
- **Description**: Unique identifier for each product
- **Example**: PROD_0125
- **Uniqueness**: Non-unique (Multiple sales per product)

---

## 2. TEMPORAL FIELDS

### order_date
- **Data Type**: Date (YYYY-MM-DD)
- **Range**: 2015-01-01 to 2025-12-31
- **Description**: Date when order was placed
- **Example**: 2024-05-15
- **Missing Values**: < 1%
- **Source**: Automatically parsed from transactions

### order_month
- **Data Type**: Integer
- **Range**: 1-12
- **Description**: Month of order placement
- **Mapping**: 1=Jan, 2=Feb, ..., 12=Dec
- **Example**: 5 (May)
- **Derivation**: Extracted from order_date

### order_quarter
- **Data Type**: Integer
- **Range**: 1-4
- **Description**: Quarter in fiscal/calendar year
- **Mapping**: 1=Q1 (Jan-Mar), 2=Q2 (Apr-Jun), etc.
- **Example**: 2
- **Derivation**: Calculated from order_month

### order_year
- **Data Type**: Integer
- **Range**: 2015-2025
- **Description**: Year of order placement
- **Example**: 2024
- **Distribution**: Balanced across all years
- **Derivation**: Extracted from order_date

---

## 3. PRODUCT DETAILS

### product_name
- **Data Type**: Text/String
- **Length**: 10-200 characters
- **Description**: Full product name including variants
- **Example**: "Samsung Galaxy A12 (Blue) 128GB"
- **Missing Values**: < 0.5%
- **Notes**: May contain size, color, variant info

### category
- **Data Type**: Text/String (Categorical)
- **Valid Values**: 
  - Electronics (100% of cleaned data)
- **Example**: "Electronics"
- **Missing Values**: < 0.1%
- **Distribution**: 1,124,003 records (100% Electronics)
- **Standardized Values**: 
  - All variations (ELECTRONICS, Electronics, Electronicss, Electronic, Electronics & Accessories) → "Electronics"
  - This is because the raw dataset contains ONLY electronics products
- **Cleaning Process**: Challenge 6 - Category Standardization
- **Status**: PRODUCTION READY ✅

### subcategory
- **Data Type**: Text/String (Categorical)
- **Valid Values**: 25+ values per category
- **Example**: "Smartphones", "Laptops", "Headphones"
- **Missing Values**: 5-10%
- **Hierarchy**: Subcategory depends on Category

### brand
- **Data Type**: Text/String (Categorical)
- **Unique Values**: 100+ brands
- **Common Brands**: Samsung, Apple, Sony, LG, HP, Dell, Xiaomi, OnePlus
- **Example**: "Samsung"
- **Missing Values**: < 2%
- **Coverage**: Indian and global brands

### product_rating
- **Data Type**: Numeric (Float)
- **Range**: 1.0 - 5.0
- **Scale**: 1=Poor, 2=Fair, 3=Average, 4=Good, 5=Excellent
- **Example**: 4.3
- **Missing Values**: 10-15%
- **Source**: Aggregated customer ratings from product page

---

## 4. PRICING INFORMATION

### original_price_inr
- **Data Type**: Numeric (Float)
- **Currency**: Indian Rupees (INR)
- **Range**: ₹100 - ₹1,000,000
- **Example**: 24,999.00
- **Missing Values**: 2-5%
- **Note**: List price before any discounts
- **Data Quality Issues**: Mixed formats (₹, commas, spaces)

### discount_percent
- **Data Type**: Numeric (Float)
- **Range**: 0 - 100 (percentage)
- **Example**: 25.5
- **Missing Values**: 1-3%
- **Description**: Discount percentage applied to original price
- **Calculation**: (original_price - final_amount) / original_price * 100

### final_amount_inr
- **Data Type**: Numeric (Float)
- **Currency**: Indian Rupees (INR)
- **Range**: ₹100 - ₹900,000
- **Example**: 18,749.25
- **Missing Values**: < 1%
- **Note**: Final price paid by customer after discount
- **Derivation**: original_price - (original_price * discount_percent/100)

### delivery_charges
- **Data Type**: Numeric (Float)
- **Currency**: Indian Rupees (INR)
- **Range**: ₹0 - ₹500
- **Example**: 99.00
- **Missing Values**: 2-5%
- **Note**: ₹0 for Free Shipping offers or Prime members
- **Waived For**: Prime members (50% of transactions)

---

## 5. CUSTOMER INFORMATION

### customer_city
- **Data Type**: Text/String (Categorical)
- **Valid Values**: 30+ Indian cities
- **Metropolitan Cities**: Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata
- **Tier-1 Cities**: Pune, Jaipur, Lucknow, Chandigarh, Ahmedabad
- **Tier-2/3 Cities**: 15+ smaller cities
- **Example**: "Bangalore"
- **Missing Values**: < 5%
- **Data Quality Issues**: Name variations (Bangalore/Bengaluru, Delhi/New Delhi)

### customer_state
- **Data Type**: Text/String (Categorical)
- **Valid Values**: 28+ Indian states
- **Example**: "Karnataka"
- **Missing Values**: 3-8%
- **Coverage**: All major states with data availability

### age_group
- **Data Type**: Text/String (Categorical)
- **Valid Values**:
  - 18-25: Young adults
  - 26-35: Working professionals
  - 36-45: Mid-career
  - 46-55: Senior professionals
  - 55+: Senior citizens
- **Example**: "26-35"
- **Missing Values**: 15-20%
- **Note**: Inferred from registration data and purchase patterns

---

## 6. MEMBERSHIP & LOYALTY

### is_prime_member
- **Data Type**: Boolean (0/1)
- **Values**:
  - 0 = Non-Prime member (60% of transactions)
  - 1 = Prime member (40% of transactions)
- **Example**: 1
- **Missing Values**: < 1%
- **Impact**: Eligible for free/faster delivery
- **Age**: Prime membership duration tracked separately

### is_prime_eligible
- **Data Type**: Boolean (0/1)
- **Values**:
  - 0 = Not eligible for Prime (product doesn't qualify)
  - 1 = Eligible for Prime shipping
- **Example**: 1
- **Missing Values**: < 0.5%
- **Note**: Some products offered without Prime eligibility

---

## 7. PAYMENT INFORMATION

### payment_method
- **Data Type**: Text/String (Categorical)
- **Valid Values**:
  - UPI: Digital payment platforms (PhonePe, GooglePay, BHIM)
  - Credit Card: All credit card transactions
  - Debit Card: Direct bank account debit
  - Cash on Delivery (COD): Pay on delivery
  - Digital Wallet: Amazon Pay, PayPal, digital wallets
  - Net Banking: Bank transfer, internet banking
- **Example**: "UPI"
- **Missing Values**: 1-2%
- **Timeline**: Evolution from COD (2015) to UPI dominance (2025)
- **Trend**: UPI grows from 5% (2015) to 45% (2025)

---

## 8. DELIVERY & FULFILLMENT

### delivery_days
- **Data Type**: Integer
- **Range**: 0-30 days
- **Average**: 3-4 days
- **Example**: 3
- **Missing Values**: 3-5%
- **Variations by Service**:
  - Same Day: 0 days (Premium, limited to metro)
  - Express: 1 day
  - Standard Prime: 1-2 days
  - Regular: 3-5 days
- **Data Quality Issues**: Negative values, text entries ("Same Day"), outliers

### return_status
- **Data Type**: Text/String (Categorical)
- **Valid Values**:
  - Null/Empty: No return
  - "Returned": Product returned
  - "Returned - Refunded": Return processed
  - "Returned - Exchanged": Exchanged for another product
  - "Return Initiated": Return in process
- **Example**: Null or "Returned"
- **Missing Values**: 85% (No returns)
- **Return Rate**: ~15% of transactions

### return_reason
- **Data Type**: Text/String
- **Valid Values**: "Damaged", "Wrong Item", "Quality Issue", "Not As Described", etc.
- **Example**: "Damaged"
- **Missing Values**: 95%+ (only when return_status is not null)

---

## 9. CUSTOMER EXPERIENCE

### customer_rating
- **Data Type**: Numeric (Float)
- **Range**: 1.0 - 5.0
- **Scale**: 1=Very Dissatisfied, 5=Very Satisfied
- **Example**: 4.2
- **Missing Values**: 20-25%
- **Note**: Customer's rating of transaction experience, not product
- **Data Quality Issues**: Mixed formats ("5.0", "4 stars", "3/5"), text entries

---

## 10. BUSINESS CONTEXT

### is_festival_sale
- **Data Type**: Boolean (0/1)
- **Values**:
  - 0 = Regular sale (85% of transactions)
  - 1 = Festival sale (15% of transactions)
- **Example**: 1
- **Missing Values**: < 0.5%
- **Definition**: Transaction during major festival/promotional period

### festival_name
- **Data Type**: Text/String
- **Valid Values**:
  - "Diwali" (Oct-Nov)
  - "Christmas & New Year" (Dec)
  - "Prime Day" (Jul)
  - "Summer Sale" (May-Jun)
  - "Holi" (Mar)
  - "Independence Day" (Aug)
  - "Black Friday" (As per Amazon calendar)
- **Example**: "Diwali"
- **Missing Values**: 85% (is_festival_sale = 0)
- **Revenue Impact**: +40-60% during festivals

### customer_spending_tier
- **Data Type**: Text/String (Categorical)
- **Valid Values**:
  - "Budget": Annual spending < ₹10,000
  - "Value": Annual spending ₹10K-₹50K
  - "Premium": Annual spending ₹50K-₹200K
  - "Elite": Annual spending > ₹200K
- **Example**: "Premium"
- **Derivation**: Calculated from total annual spending
- **Missing Values**: < 1%

---

## 11. DERIVED FIELDS (CALCULATED)

### revenue_contribution
- **Calculation**: final_amount_inr
- **Note**: Key metric for revenue analysis

### profit_margin
- **Calculation**: (final_amount_inr - cost) / final_amount_inr * 100
- **Note**: Cost data not included in dataset; estimated at 20-30%

### customer_lifetime_value
- **Calculation**: Total spending by customer over entire period
- **Used For**: Customer segmentation and targeting

### repeat_purchase_flag
- **Calculation**: 1 if customer has multiple purchases, 0 otherwise
- **Used For**: Loyalty analysis

---

## 12. PRODUCT CATALOG FIELDS

(From amazon_india_products_catalog.csv)

### product_id
- **Data Type**: Text/String
- **Format**: PROD_XXXX
- **Length**: 8 characters
- **Primary Key**: Yes

### product_name
- **Data Type**: Text/String
- **Length**: 10-200 characters
- **Example**: "Samsung Galaxy A12 128GB"

### base_price_2015
- **Data Type**: Numeric (Float)
- **Currency**: INR
- **Description**: Product launch price in 2015
- **Use**: Price trend analysis

### launch_year
- **Data Type**: Integer
- **Range**: 2015-2025
- **Description**: Year product was added to catalog

### model
- **Data Type**: Text/String
- **Example**: "A12", "iPhone 15 Pro Max"
- **Note**: Product model/version identifier

### weight_kg
- **Data Type**: Numeric (Float)
- **Range**: 0.1-50 kg
- **Unit**: Kilograms
- **Used For**: Delivery optimization

---

## 13. DATA QUALITY & ISSUES

### Missing Values by Field (Approximate)
- order_date: < 1%
- product_id: < 0.5%
- customer_id: < 0.5%
- customer_rating: 20-25%
- age_group: 15-20%
- delivery_days: 3-5%
- original_price_inr: 2-5%
- delivery_charges: 2-5%

### Data Quality Issues Addressed in Cleaning
1. **Date format variations** (DD/MM/YYYY, DD-MM-YY, YYYY-MM-DD)
2. **Price formatting** (₹, commas, text entries)
3. **Rating inconsistencies** ("5.0", "4 stars", "3/5")
4. **City name variations** (Bangalore/Bengaluru)
5. **Boolean inconsistencies** (True/False, Yes/No, 1/0)
6. **Duplicate transactions** (2-3% of data)
7. **Outlier prices** (100x errors from decimal points)
8. **Negative delivery days**
9. **Invalid dates** (after 2025, before 2015)

---

## 14. STATISTICAL SUMMARY

### Revenue Fields
- **total_revenue_2015_2025**: ₹XXXXX Crores
- **avg_annual_revenue**: ₹XXXXX Crores
- **revenue_growth_cagr**: XX%

### Customer Fields
- **total_unique_customers**: X Million
- **avg_customers_per_year**: XXX,XXX
- **repeat_purchase_rate**: XX%

### Order Fields
- **total_orders**: X Million
- **avg_order_value**: ₹XXXXX
- **median_order_value**: ₹XXXXX

---

## 15. DATA DICTIONARY CONVENTIONS

- **Data Type**: Indicates format (Text, Integer, Float, Boolean, Date)
- **Range**: Minimum and maximum values
- **Example**: Sample value from actual data
- **Missing Values**: Percentage of null/empty values
- **Uniqueness**: Whether field values are unique
- **Distribution**: How values are spread across dataset

---

## 16. USAGE NOTES

### For Analysis
- Use `customer_id` and `order_date` for cohort analysis
- Use `is_prime_member` for segment analysis
- Use `order_year` and `order_month` for temporal analysis
- Use `customer_city` and `customer_state` for geographic analysis

### For Modeling
- Target variables: future_revenue, will_return, churn
- Features: all categorical and numeric fields except identifiers
- Time windows: rolling 30-90 day aggregations

### For Reporting
- Use `final_amount_inr` for revenue reporting
- Use `customer_rating` for satisfaction metrics
- Use `delivery_days` for operational KPIs
- Use `is_festival_sale` for seasonal segmentation

---

**Last Updated**: March 2025
**Version**: 1.0
**Format**: Markdown
