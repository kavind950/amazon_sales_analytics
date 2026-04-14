# 📚 E-Commerce Analytics: Domain Concepts & Statistical Foundation

## Table of Contents
1. [E-Commerce Fundamentals](#ecommerce)
2. [Statistical Methods for E-Commerce](#statistics)
3. [Probability Applications](#probability)
4. [Key E-Commerce Metrics](#metrics)
5. [RFM Analysis Deep Dive](#rfm)
6. [Forecasting & Prediction](#forecasting)
7. [A/B Testing for Decision Making](#testing)

---

## E-Commerce Fundamentals {#ecommerce}

### The E-Commerce Ecosystem

```
┌─────────────────────────────────────────────────┐
│           AMAZON INDIA E-COMMERCE FLOW           │
├─────────────────────────────────────────────────┤
│                                                   │
│  Customer Journey:                               │
│  ┌─────────────────────────────────────────┐   │
│  │ 1. DISCOVERY (Browse/Search)            │   │
│  │    └─ How do customers find products?   │   │
│  │                                          │   │
│  │ 2. CONSIDERATION (Compare/Read reviews) │   │
│  │    └─ What influences buying decision?  │   │
│  │                                          │   │
│  │ 3. PURCHASE (Buy & Checkout)            │   │
│  │    └─ Payment methods, discounts        │   │
│  │                                          │   │
│  │ 4. FULFILLMENT (Packaging & Delivery)   │   │
│  │    └─ How quickly do we deliver?       │   │
│  │                                          │   │
│  │ 5. POST-PURCHASE (Delivery, Returns)    │   │
│  │    └─ Satisfaction & retention          │   │
│  │                                          │   │
│  └─────────────────────────────────────────┘   │
│                                                   │
└─────────────────────────────────────────────────┘
```

### Key Stakeholders & Their Metrics

```
👤 CEO / CFO (Executive Level)
├─ Cares about: Revenue, Profit, Growth Rate, Market Share
├─ Views: Executive Dashboard
└─ Questions: "Are we growing? Is this profitable?"

📊 Category Managers (Product Level)
├─ Cares about: Category Revenue, ROI, Inventory Levels
├─ Views: Category Performance Dashboard
└─ Questions: "Which products should I stock more?"

💼 Marketing Managers (Customer Level)
├─ Cares about: CAC, Retention Rate, CLV
├─ Views: Customer Analytics Dashboard
└─ Questions: "How do I acquire customers efficiently?"

📦 Operations Managers (Logistics Level)
├─ Cares about: Delivery Time, Return Rate, Cost per Delivery
├─ Views: Operations Dashboard
└─ Questions: "Are we delivering on time and cost-effectively?"
```

### E-Commerce Business Models

```
AMAZON INDIA OPERATES IN:

1. MARKETPLACE (Primary)
   ├─ Products sold by various sellers
   ├─ Amazon acts as platform
   ├─ Revenue from marketplace fees
   └─ Metrics: GMV (Gross Merchandise Value), Fee Collection

2. 1ST PARTY RETAIL (Direct Sales)
   ├─ Amazon directly buys & sells
   ├─ Own inventory risk
   ├─ Direct profit/loss
   └─ Metrics: Revenue, Margin, Inventory Turnover

3. AMAZON PRIME
   ├─ Membership subscription (yearly)
   ├─ Benefits: Free shipping, exclusive deals, Prime Video
   ├─ High customer lifetime value
   └─ Metrics: Prime members, Churn rate, LTV
```

---

## Statistical Methods for E-Commerce {#statistics}

### 1. **Revenue Analysis & Trend Detection**

#### Trend Analysis: Is Business Growing?

```
METHOD: Linear Regression for Revenue Trend

Concept: Draw a line through historical revenue points
         that best represents the overall trend

Mathematical Formula:
y = mx + b

Where:
  y = Predicted Revenue
  x = Time (month, year, day)
  m = Slope (growth rate per time unit)
  b = Intercept (starting point)

Real Example:
Year    Revenue (₹ Crores)
2015    10
2016    15
2017    22
2018    32
2019    45
2020    58
2021    72
2022    85
2023    95
2024    108
2025    120

Linear regression finds line:
y = 11.5x - 23200
(Approximately ₹11.5 Crores growth per year)

Growth Rate = (120 - 10) / 10 / 10 years = 110% / 10 = 11% CAGR

Interpretation: Business growing at 11% Compound Annual Growth Rate
```

#### Seasonality Analysis Using Time Series Decomposition

```
TIME SERIES = TREND + SEASONAL + RESIDUAL

Example decomposition:
┌─────────────────────────────────┐
│ ORIGINAL SERIES                 │  
│    ╱╲    ╱╲         ╱╲         │
│   ╱  ╲  ╱  ╲       ╱  ╲        │
│  ╱    ╲╱    ╲     ╱    ╲       │
└─────────────────────────────────┘

BREAKS DOWN TO:

┌─────────────────────────────────┐
│ TREND (Long-term direction)     │
│      ╱                          │
│   ╱╱                            │
│ ╱╱                              │
│╱                                │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ SEASONAL (Repeating pattern)    │
│  ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱        │
│  Up-down-up-down pattern        │
│  (Diwali, Prime Day, Christmas) │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ RESIDUAL (Random noise)         │
│   ●  ●   ●   ●  ● ●  ●        │
│  ●  ●  ●   ●  ●  ●  ●         │
│ Random variations               │
└─────────────────────────────────┘

Python Code:
from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(revenue_series, model='additive', period=12)
result.plot()
```

### 2. **Customer Segmentation: RFM & Clustering**

#### RFM Analysis (Recency, Frequency, Monetary)

```
STEP 1: Calculate RFM Scores
════════════════════════════

Customer A:
├─ Recency: Bought 5 days ago (Recent! Score: 5/5)
├─ Frequency: Buys 3 times/month (Frequent! Score: 5/5)
└─ Monetary: Spends ₹50,000/year (High spender! Score: 5/5)
   Result: RFM = "5-5-5" (Champions!)

Customer B:
├─ Recency: Bought 200 days ago (Inactive! Score: 1/5)
├─ Frequency: Buys 1 time/year (Rare! Score: 1/5)
└─ Monetary: Spends ₹5,000/year (Low spender! Score: 1/5)
   Result: RFM = "1-1-1" (Lost customers!)

Customer C:
├─ Recency: Bought 10 days ago (Recent! Score: 5/5)
├─ Frequency: Buys 10 times/year (Very Frequent! Score: 5/5)
└─ Monetary: Spends ₹10,000/year (Medium spender! Score: 3/5)
   Result: RFM = "5-5-3" (Loyal Customers)

STEP 2: Segment into Groups
════════════════════════════

┌──────────────────────────────────────────────┐
│ SEGMENT PROFILES & ACTIONS                   │
├──────────────────────────────────────────────┤
│                                               │
│ Champions (5-5-5)                            │
│ ├─ Profile: Best customers, loyal, valuable │
│ ├─ Count: ~5% of customer base              │
│ ├─ Revenue %: 40-50% of total               │
│ └─ Action: VIP programs, exclusive access   │
│                                               │
│ Loyal Customers (4-5-5, 5-4-5)              │
│ ├─ Profile: Regular buyers, consistent      │
│ ├─ Count: ~15% of customer base             │
│ ├─ Revenue %: 30-35% of total               │
│ └─ Action: Rewards, recognition programs    │
│                                               │
│ Potential Loyalists (5-3-3, 4-4-3)          │
│ ├─ Profile: Recently bought, growing value  │
│ ├─ Count: ~20% of customer base             │
│ ├─ Revenue %: 10-15% of total               │
│ └─ Action: Nurture, engagement campaigns    │
│                                               │
│ At-Risk (1-4-5, 1-5-5)                      │
│ ├─ Profile: Were valuable, haven't bought   │
│ ├─ Count: ~10% of customer base             │
│ ├─ Revenue %: 5-10% of total                │
│ └─ Action: Win-back campaigns, surveys      │
│                                               │
│ Lost (1-1-1, 1-1-2)                         │
│ ├─ Profile: Inactive, low value             │
│ ├─ Count: ~50% of customer base             │
│ ├─ Revenue %: <5% of total                  │
│ └─ Action: Re-engagement or clean-up        │
│                                               │
└──────────────────────────────────────────────┘

BUSINESS INSIGHT:
Pareto Principle: 80% of revenue from 20% of customers
→ Focus resources on Champions & Loyal (top 20%)
→ Potential Loyalists need nurturing to become Champions
→ At-Risk need immediate win-back efforts
```

#### K-Means Clustering (Advanced Segmentation)

```
CONCEPT: Group customers by similarity using distance metrics

DISTANCE METRIC: Euclidean Distance
Distance = √[(R₁-R₂)² + (F₁-F₂)² + (M₁-M₂)²]

ALGORITHM:
1. Select K = number of segments (e.g., 4 clusters)
2. Randomly place K cluster centers
3. Assign each customer to nearest center
4. Recalculate center positions
5. Repeat until centers stop moving

VISUALIZATION:
If we use 2 dimensions (Frequency vs Monetary):

Monetary
   │
50,000 │     ●●●  ← Cluster 1: High spenders
       │    ●  ●
25,000 │   ●  ●   ← Cluster 2: Medium spenders
       │  ● ●
10,000 │ ●●●      ← Cluster 3: Low spenders
       │●●●
   1,000├─────────────────────── Frequency
       1    5    10    20    50

PYTHON CODE:
from sklearn.cluster import KMeans

# Prepare RFM data
rfm_data = df[['recency', 'frequency', 'monetary']]

# Apply K-Means (4 clusters)
kmeans = KMeans(n_clusters=4, random_state=42)
df['cluster'] = kmeans.fit_predict(rfm_data)

# Analyze clusters
for cluster in range(4):
    cluster_data = df[df['cluster'] == cluster]
    print(f"Cluster {cluster}:")
    print(f"  Size: {len(cluster_data)}")
    print(f"  Avg Recency: {cluster_data['recency'].mean():.1f} days")
    print(f"  Avg Frequency: {cluster_data['frequency'].mean():.1f} purchases")
    print(f"  Avg Monetary: ₹{cluster_data['monetary'].mean():,.0f}")
```

### 3. **Statistical Hypothesis Testing**

#### Chi-Square Test: Is There Association?

```
SCENARIO: Is Prime Membership associated with buying Electronics?

Hypothesis:
H₀ (Null): Prime membership is INDEPENDENT of Electronics purchase
H₁ (Alt): Prime membership is DEPENDENT on Electronics purchase

CONTINGENCY TABLE:
                    Buys Electronics    Doesn't Buy    Total
Prime Member             600                 200         800
Non-Prime              1000                 200       1,200
Total                  1600                 400       2,000

CALCULATION:
Chi-Square = Σ [(Observed - Expected)² / Expected]

Expected for "Prime & Electronics":
(800 × 1600) / 2000 = 640

Chi-Square ≈ 3.4

INTERPRETATION:
If P-value < 0.05: REJECT H₀ → Prime members significantly prefer Electronics
If P-value ≥ 0.05: FAIL TO REJECT H₀ → No significant association

In this example: P-value = 0.065 > 0.05
→ Not enough evidence that Prime membership affects Electronics preference
```

#### T-Test: Comparing Two Groups

```
SCENARIO: Do Prime members spend more than Non-Prime members?

H₀: Prime Average Spend = Non-Prime Average Spend
H₁: Prime Average Spend ≠ Non-Prime Average Spend

DATA:
Prime members:       ₹5000, 6000, 4500, 5500, 6500 (avg = ₹5,500)
Non-Prime members:   ₹2000, 2500, 3000, 1500, 2000 (avg = ₹2,200)

T-STATISTIC:
t = (Mean₁ - Mean₂) / (Combined StdDev × √(1/n₁ + 1/n₂))
t = (5500 - 2200) / (calculated) ≈ 12.5

INTERPRETATION:
If t > Critical Value (1.96 for 95% confidence):
→ REJECT H₀ → Prime members spend SIGNIFICANTLY MORE

In this case: 12.5 > 1.96 ✓
Conclusion: Prime members spend significantly more!
Marketing implication: Prime membership drives higher AOV

PYTHON CODE:
from scipy.stats import ttest_ind

prime_spending = df[df['is_prime']]['final_amount']
non_prime_spending = df[~df['is_prime']]['final_amount']

t_stat, p_value = ttest_ind(prime_spending, non_prime_spending)
print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("✓ Significant difference (Prime members spend more)")
else:
    print("✗ No significant difference")
```

### 4. **Correlation & Causation Analysis**

#### Understanding Correlations

```
PEARSON CORRELATION COEFFICIENT (r)
Range: -1 to +1

VISUAL REPRESENTATIONS:

Perfect Positive: r = +1
├─ Discount Percentage ↔ Sales Volume
│  As discount increases, sales increase
│  One increases → Other increases proportionally
│  
│  │     ●
│  │   ●
│  │ ●
│  ├─────────────
│  Discount %    Sales Volume

Strong Positive: r = +0.8
├─ Customer Tenure ↔ Lifetime Value
│  Longer customer = More lifetime value
│  Relationship exists but not perfect
│  
│  │    ●●  ●
│  │  ●  ●
│  │●  ●  ●
│  ├─────────────
│  Tenure (years)  LTV (₹)

Moderate Positive: r = +0.5
├─ Number of Reviews ↔ Product Rating
│  More reviews slightly correlate with rating
│  Weak relationship
│  
│  │  ●    ●
│  │   ● ●
│  │  ●  ● ●
│  ├─────────────
│  # Reviews     Rating

No Correlation: r ≈ 0
├─ Product Color ↔ Sales
│  Color doesn't predict sales
│  Completely random
│  
│  │  ●   ●  ●
│  │ ●  ●   ●
│  │  ●  ●  ●
│  ├─────────────
│  Color      Sales

Strong Negative: r = -0.8
├─ Product Price ↔ Units Sold
│  Higher price → Fewer units sold
│  Clear inverse relationship
│  
│  │  ●
│  │ ●  ●
│  │    ●
│  │      ●
│  ├─────────────
│  Price        Units Sold

Perfect Negative: r = -1
├─ Discount Amount ↔ Profit Margin
│  Larger discount → Lower profit margin
│  Perfect inverse relationship
│  
│  │  ●
│  │    ●
│  │      ●
│  │        ●
│  ├─────────────
│  Discount Amount  Profit Margin
```

#### IMPORTANT: Correlation ≠ Causation!

```
COMMON MISTAKES:

Example 1: Ice Cream Sales ↔ Shark Attacks
Correlation: +0.9 (Very strong positive!)
❌ WRONG Conclusion: "Eating ice cream causes shark attacks!"
✓ RIGHT Conclusion: Both increase in SUMMER (confounding variable)

Example 2: Number of Churches ↔ Crime Rate
Correlation: +0.7 (Strong positive!)
❌ WRONG Conclusion: "Churches cause crime!"
✓ RIGHT Conclusion: Both exist in larger CITIES (confounding variable)

E-COMMERCE EXAMPLE:

Observation: Correlation between "Coupons Sent" and "Sales" = +0.8

❌ WRONG: "Sending more coupons directly causes more sales"
(Why it's wrong: Could be that we send more coupons during peak season,
 and peak season naturally has higher sales anyway)

✓ RIGHT: Need to test if coupons actually DRIVE sales
(How to test: A/B test - give coupons to test group, not to control group,
 compare sales between groups)

DETERMINING CAUSATION:
1. Establish correlation ✓
2. Establish temporal order (cause before effect)
3. Rule out confounding variables
4. Conduct experiments (A/B tests)
5. Find plausible mechanism
```

---

## Probability Applications {#probability}

### 1. **Customer Lifetime Value Prediction**

```
CONCEPT: Estimate total profit from a customer relationship

P(Purchase in next month) = P(Will customer buy in next 30 days?)

Calculate from historical data:
   Customers who buy in any given month
   ────────────────────────────────────
   Total active customers

Example:
   3,000 customers bought in last month
   ─────────────────────────────────
   10,000 active customers = 0.30 = 30%

CLV MODEL:

CLV = Average Transaction Value × Purchase Frequency × Customer Lifespan
    - Customer Acquisition Cost

Example Calculation:
├─ Avg Transaction: ₹3,000
├─ Frequency: 4 times/year
├─ Lifespan: 5 years (average customer duration)
├─ CAC: ₹500
│
└─ CLV = (₹3,000 × 4 × 5) - ₹500 = ₹59,500

Implication: Willing to spend up to ₹59,500 to acquire customer!
```

### 2. **Churn Prediction: Who Will Leave?**

```
SCENARIO: Predict which customers will stop buying

Variables that predict churn:
├─ Days since last purchase: If > 90 days = high risk
├─ Purchase frequency trend: Decreasing = high risk
├─ Customer rating: If low = high risk
├─ Support tickets: If increasing = high risk
└─ Cancellations: If recent = high risk

LOGISTIC REGRESSION MODEL:

Probability of Churn = e^(w₀ + w₁x₁ + w₂x₂ + ...) / (1 + e^(w₀ + w₁x₁ + w₂x₂ + ...))

Simplified interpretation:
├─ Each variable has a "weight"
├─ Positive weight = increases churn probability
├─ Negative weight = decreases churn probability
└─ Model outputs probability (0 to 1)

EXAMPLE MODEL (Hypothetical):

Customer Score = -5 + (Days_Since_Purchase × 0.01) - (Avg_Order_Value × 0.0005) 
               + (Return_Rate × 2) - (Prime_Member × 1)

Customer A: 100 days inactive, ₹2,000 AOV, 5% returns, Prime
Score = -5 + (100×0.01) - (2000×0.0005) + (0.05×2) - 1
Score = -5 + 1 - 1 + 0.1 - 1 = -5.9
Churn Probability = 0.3% ✓ (Low risk)

Customer B: 200 days inactive, ₹500 AOV, 20% returns, Non-Prime
Score = -5 + (200×0.01) - (500×0.0005) + (0.20×2) - 0
Score = -5 + 2 - 0.25 + 0.4 = -2.85
Churn Probability = 5.4% (Moderate risk)

Customer C: 300 days inactive, ₹100 AOV, 30% returns, Non-Prime
Score = -5 + (300×0.01) - (100×0.0005) + (0.30×2) - 0
Score = -5 + 3 - 0.05 + 0.6 = -1.45
Churn Probability = 18% ✗ (High risk → Send win-back offer)
```

### 3. **Bayes' Theorem for Targeting**

```
MARKETING PROBLEM: 
"Should I send discount coupon to customer?"

Prior Probability:
├─ P(Customer converts) = 20% (baseline)

New Information:
├─ Customer viewed Electronics twice this week
├─ P(View Electronics | Converts) = 70% (70% of converters view Electronics)
├─ P(View Electronics | Doesn't Convert) = 30%

BAYES' THEOREM:
P(Converts | Views Electronics) = P(Views Electronics | Converts) × P(Converts)
                                    ────────────────────────────────────────
                                          P(Views Electronics)

Where:
P(Views Electronics) = P(Views | Converts) × P(Converts) 
                     + P(Views | Non-Converts) × P(Non-Converts)
                     = (0.70 × 0.20) + (0.30 × 0.80)
                     = 0.14 + 0.24 = 0.38

SOLUTION:
P(Converts | Views Electronics) = (0.70 × 0.20) / 0.38 = 0.137 / 0.38 = 36%

INTERPRETATION:
├─ Prior probability: 20% (baseline)
├─ After seeing Electronics view: 36% (78% increase!)
└─ Recommendation: YES, send coupon (36% > 20%)

This is why Amazon tracks what you view!
```

---

## Key E-Commerce Metrics {#metrics}

### Financial Metrics

```
1. REVENUE
   Definition: Total money earned from sales
   Formula: Revenue = Sum of all (Price × Quantity)
   Why Important: The "top line" of business
   Target: Always increasing

2. GROSS PROFIT
   Definition: Revenue - Cost of Goods Sold (COGS)
   Formula: Gross Profit = Revenue - COGS
   Why Important: Shows production efficiency
   Example: Revenue ₹100 - COGS ₹60 = GP ₹40

3. NET PROFIT
   Definition: Revenue - All Expenses (COGS + Operations + Marketing + etc)
   Formula: Net Profit = Revenue - All Costs
   Why Important: True profitability
   Example: Revenue ₹100 - Costs ₹75 = NP ₹25

4. PROFIT MARGIN
   Definition: What percentage of revenue is profit?
   Formula: Margin = (Profit / Revenue) × 100
   Why Important: Efficiency metric
   Example: ₹25 profit / ₹100 revenue = 25% margin

5. ROI (Return on Investment)
   Definition: Percentage return on marketing spend
   Formula: ROI = (Gain - Cost) / Cost × 100
   Why Important: Marketing efficiency
   Example: Spend ₹1000 → Sales ₹4000 → ROI = 300%
```

### Customer Metrics

```
1. CUSTOMER ACQUISITION COST (CAC)
   Definition: How much does it cost to acquire one customer?
   Formula: CAC = Total Marketing Spend / New Customers Acquired
   Why Important: Should be < CLV
   Example: Spent ₹10,00,000 / 1000 customers = ₹1000 CAC

2. LIFETIME VALUE (CLV or LTV)
   Definition: Total profit expected from a customer
   Formula: CLV = (Avg Order Value × Purchase Frequency × Lifespan) - CAC
   Why Important: Shows sustainability
   Example: ₹3000 × 4/year × 5 years - ₹1000 = ₹59,000 CLV

3. CAC PAYBACK PERIOD
   Definition: How many months to recover acquisition cost?
   Formula: CAC / (Average Monthly Profit per Customer)
   Why Important: Cash flow indicator
   Example: ₹1000 CAC / ₹100 monthly profit = 10 months

4. CHURN RATE
   Definition: Percentage of customers lost per period
   Formula: Churn = Lost Customers / Starting Customers × 100
   Why Important: Retention indicator
   Example: Lost 50 customers / 1000 starting = 5% monthly churn

5. RETENTION RATE
   Definition: Percentage of customers who stay
   Formula: Retention = 100% - Churn Rate
   Why Important: Inverse of churn
   Example: 100% - 5% churn = 95% retention rate

6. REPEAT PURCHASE RATE
   Definition: % of customers who buy more than once
   Formula: Repeat = Customers with 2+ purchases / Total Customers
   Why Important: Shows loyalty
   Example: 600 repeat customers / 1000 total = 60% repeat rate
```

### Product Metrics

```
1. CONVERSION RATE
   Definition: % of browsers who become buyers
   Formula: Conversion = Purchases / Product Views × 100
   Why Important: Shows product appeal
   Example: 500 buys / 10,000 views = 5% conversion

2. CLICK-THROUGH RATE (CTR)
   Definition: % of people who click product ad
   Formula: CTR = Clicks / Impressions × 100
   Why Important: Ad effectiveness
   Example: 100 clicks / 5000 impressions = 2% CTR

3. AVERAGE ORDER VALUE (AOV)
   Definition: Average spending per transaction
   Formula: AOV = Total Revenue / Number of Orders
   Why Important: Revenue optimization
   Example: ₹50,00,000 revenue / 1000 orders = ₹5000 AOV

4. RETURN RATE
   Definition: % of sold items returned
   Formula: Return Rate = Items Returned / Items Sold × 100
   Why Important: Product/service quality indicator
   Example: 50 returns / 1000 sold = 5% return rate

5. PRODUCT RATING
   Definition: Average customer rating (1-5 stars)
   Formula: Rating = Sum of All Ratings / Number of Reviews
   Why Important: Social proof, affects sales
   Example: 500 ratings, total 2000 stars = 4.0 rating

6. SELL-THROUGH RATE
   Definition: % of inventory sold in period
   Formula: STR = Units Sold / Units Available × 100
   Why Important: Inventory optimization
   Example: 800 sold / 1000 available = 80% STR
```

### Operational Metrics

```
1. AVERAGE DELIVERY TIME
   Definition: How many days from order to delivery?
   Formula: Avg Days = Sum of All Delivery Days / Total Orders
   Why Important: Customer satisfaction
   Example: 5,000 total days / 1000 orders = 5 days average

2. ON-TIME DELIVERY RATE
   Definition: % of deliveries meeting promised date
   Formula: OTD = Timely Deliveries / Total Deliveries × 100
   Why Important: Customer trust
   Example: 950 on-time / 1000 total = 95% OTD

3. INVENTORY TURNOVER
   Definition: How many times inventory is sold and replaced
   Formula: Turnover = COGS / Average Inventory
   Why Important: Efficiency, cash flow
   Example: ₹50,00,000 COGS / ₹10,00,000 avg inventory = 5× turnover

4. ORDER FULFILLMENT ACCURACY
   Definition: % of orders packed/shipped correctly
   Formula: Accuracy = Correct Orders / Total Orders × 100
   Why Important: Customer satisfaction
   Example: 990 correct / 1000 orders = 99% accuracy

5. WAREHOUSE EFFICIENCY
   Definition: Orders shipped per labor hour
   Formula: Efficiency = Orders Shipped / Labor Hours
   Why Important: Cost optimization
   Example: 500 orders / 50 hours = 10 orders/hour
```

---

## RFM Analysis Deep Dive {#rfm}

### Calculation Process

```
STEP-BY-STEP CALCULATION:

Data Available:
├─ Each customer's purchase history
├─ Date of each transaction
├─ Amount of each transaction
└─ Current date (reference point)

STEP 1: Calculate RECENCY

Definition: Days since last purchase

Example customer purchase history:
├─ Jan 1: ₹5000
├─ Feb 15: ₹3000
├─ Jun 10: ₹4000
└─ Sep 1: ₹2000 ← MOST RECENT

Today = Sep 20

Recency = Sep 20 - Sep 1 = 19 days

STEP 2: Calculate FREQUENCY

Definition: Number of purchases in period

Example customer:
├─ Jan 1: ₹5000 ✓
├─ Feb 15: ₹3000 ✓
├─ Jun 10: ₹4000 ✓
└─ Sep 1: ₹2000 ✓

Frequency = 4 purchases in last 12 months

STEP 3: Calculate MONETARY

Definition: Total amount spent

Example customer:
├─ Jan 1: ₹5000
├─ Feb 15: ₹3000
├─ Jun 10: ₹4000
├─ Sep 1: ₹2000
└─ TOTAL: ₹14,000

Monetary = ₹14,000

STEP 4: Assign Scores (1-5 scale)

Scale R (Recency):
├─ 5 = 0-30 days (Very recent!)
├─ 4 = 31-60 days
├─ 3 = 61-90 days
├─ 2 = 91-180 days
└─ 1 = 180+ days (Haven't bought in 6+ months!)

Our example: 19 days → Score 5

Scale F (Frequency):
├─ 5 = 10+ purchases/year
├─ 4 = 7-9 purchases/year
├─ 3 = 4-6 purchases/year
├─ 2 = 2-3 purchases/year
└─ 1 = 1 purchase/year or less

Our example: 4 purchases → Score 3

Scale M (Monetary):
├─ 5 = ₹50,000+ annually
├─ 4 = ₹30,000-50,000
├─ 3 = ₹15,000-30,000
├─ 2 = ₹5,000-15,000
└─ 1 = <₹5,000

Our example: ₹14,000 annually → Score 2

FINAL RFM SCORE: "5-3-2"
```

### RFM-Based Segments & Actions

```
┌────────────────────────────────────────────────────┐
│ CHAMPION CUSTOMERS (5-5-5, 5-5-4, 5-4-5, 4-5-5)  │
├────────────────────────────────────────────────────┤
│                                                     │
│ Characteristics:                                   │
│ ├─ Bought very recently                          │
│ ├─ Buy very frequently                           │
│ ├─ Spend the most money                          │
│ ├─ Probably Prime members                        │
│ └─ Highly satisfied                              │
│                                                     │
│ Size: ~5% of customer base                        │
│ Revenue: ~45% of total revenue                    │
│                                                     │
│ ACTIONS:                                          │
│ ├─ VIP Program: Exclusive benefits,              │
│ │  early access to new products                  │
│ ├─ Referral Rewards: Incentivize bringing        │
│ │  friends (high success rate)                   │
│ ├─ Personal Service: Dedicated support           │
│ ├─ Exclusive Discounts: Premium loyalty          │
│ │  rewards program                               │
│ └─ Engagement: Monthly personal offers           │
│                                                     │
│ Expected ROI: 200%+ from retention efforts      │
│                                                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ LOYAL CUSTOMERS (4-4-4, 5-4-4, 4-5-4, etc.)      │
├────────────────────────────────────────────────────┤
│                                                     │
│ Characteristics:                                   │
│ ├─ Regular buyers who show consistency           │
│ ├─ Good spending levels                          │
│ ├─ Stable purchase patterns                      │
│ └─ Room to increase spending                     │
│                                                     │
│ Size: ~15% of customer base                       │
│ Revenue: ~35% of total revenue                    │
│                                                     │
│ ACTIONS:                                          │
│ ├─ Loyalty Rewards: Points for each purchase     │
│ ├─ Tier Benefits: Silver/Gold status             │
│ ├─ Cross-sell: Introduce similar products        │
│ ├─ Upsell: Encourage higher-priced items         │
│ ├─ Recognition: "Thanks for being loyal" emails  │
│ └─ Exclusive Offers: Member-only deals           │
│                                                     │
│ Expected ROI: 150%+ from increased frequency/AOV│
│                                                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ POTENTIAL LOYALISTS (5-3-3, 4-3-3, 5-2-3, etc.)  │
├────────────────────────────────────────────────────┤
│                                                     │
│ Characteristics:                                   │
│ ├─ Recent activity = Good sign!                  │
│ ├─ Lower frequency = Can improve                 │
│ ├─ Medium spending = Growth potential            │
│ └─ Most valuable growth segment                  │
│                                                     │
│ Size: ~20% of customer base                       │
│ Revenue: ~10% of total revenue                    │
│                                                     │
│ ACTIONS:                                          │
│ ├─ Engagement Emails: "Check out related items"  │
│ ├─ Limited Offers: "Buy again soon" inducements │
│ ├─ Product Recommendations: Personalized         │
│ ├─ Onboarding: Prime membership offer            │
│ ├─ Content: Helpful buying guides                │
│ └─ Surveys: "What can we do better?"             │
│                                                     │
│ Expected ROI: 100%+ conversion to Loyal segment │
│                                                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ AT-RISK CUSTOMERS (1-5-5, 1-4-5, 2-5-5, etc.)   │
├────────────────────────────────────────────────────┤
│                                                     │
│ Characteristics:                                   │
│ ├─ WERE loyal but stopped buying recently!       │
│ ├─ Major red flag                                │
│ ├─ Often switching to competitors                │
│ └─ Justifies aggressive retention efforts        │
│                                                     │
│ Size: ~10% of customer base                       │
│ Revenue: ~8% of total revenue (declining)         │
│                                                     │
│ ACTIONS:                                          │
│ ├─ WIN-BACK CAMPAIGN:                            │
│ │  "We miss you! Here's 30% off"                 │
│ ├─ Personal Outreach: Phone call or email        │
│ ├─ Feedback Survey: "Why did you leave?"         │
│ ├─ Special Incentives: Exclusive win-back offer  │
│ ├─ Re-engagement: Show new products              │
│ └─ Last Resort: Extreme discount (one-time)      │
│                                                     │
│ Expected ROI: 50-75% successful re-activation    │
│                                                     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ LOST CUSTOMERS (1-1-1, 1-1-2, 1-2-1, etc.)      │
├────────────────────────────────────────────────────┤
│                                                     │
│ Characteristics:                                   │
│ ├─ Never bought recently                         │
│ ├─ Rarely bought even historically               │
│ ├─ Spent very little                             │
│ ├─ Likely bounced/browsed only                   │
│ └─ Low priority for resources                    │
│                                                     │
│ Size: ~50% of customer base                       │
│ Revenue: <2% of total revenue                     │
│                                                     │
│ ACTIONS:                                          │
│ ├─ Option 1: Ignore (focus on valuable customers)│
│ ├─ Option 2: Minimal Contact:                    │
│ │  Weekly newsletter only                        │
│ ├─ Option 3: Archive:                            │
│ │  Remove from active marketing                  │
│ └─ Option 4: Database Cleanup:                   │
│    Remove completely if no value potential      │
│                                                     │
│ Expected ROI: <10% (not worth effort)            │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Forecasting & Prediction {#forecasting}

### Time Series Forecasting Methods

```
SCENARIO: Predict next 12 months of revenue

METHOD 1: SIMPLE MOVING AVERAGE (Easiest)

Concept: Average of last N months

Formula: Forecast[t] = Average of previous 3 months

Example:
Month 1: ₹10 Cr
Month 2: ₹12 Cr
Month 3: ₹11 Cr

Forecast Month 4 = (10 + 12 + 11) / 3 = ₹11 Cr

Pros: Simple, easy to understand
Cons: Ignores trends, gives equal weight to all past values

─────────────────────────────────────────────────────

METHOD 2: EXPONENTIAL SMOOTHING (Better)

Concept: Give more weight to recent values

Formula: Forecast[t] = α × Actual[t-1] + (1-α) × Forecast[t-1]

Where α (alpha) is smoothing factor (0.1 to 0.3 typical)

Example with α = 0.3:
├─ Month 1 Actual: ₹10 Cr
├─ Month 2 Forecast: 0.3×10 + 0.7×10 = ₹10 Cr
├─ Month 2 Actual: ₹12 Cr
├─ Month 3 Forecast: 0.3×12 + 0.7×10 = ₹10.6 Cr
├─ Month 3 Actual: ₹11 Cr
└─ Month 4 Forecast: 0.3×11 + 0.7×10.6 = ₹10.78 Cr

Pros: Adapts to changes, recent data weighted more
Cons: Still relatively simple

─────────────────────────────────────────────────────

METHOD 3: ARIMA (Advanced)

Concept: Uses AutoRegressive Integrated Moving Average

Components:
├─ AR (AutoRegressive): Uses past values to predict
├─ I (Integrated): Handles trends and seasonality
└─ MA (Moving Average): Uses past errors

Suitable when data has clear patterns and seasonality

Pros: Handles trends and seasonality well
Cons: Requires larger dataset (100+ observations)

─────────────────────────────────────────────────────

FORECASTING ACCURACY METRICS:

MAPE (Mean Absolute Percentage Error)
├─ Measures accuracy as percentage deviation
├─ Formula: Average(|Actual - Forecast| / |Actual|) × 100
├─ Example: MAPE = 5% (model is 95% accurate)
└─ Interpretation: Lower is better

RMSE (Root Mean Squared Error)
├─ Penalizes larger errors more heavily
├─ Formula: √(Average((Actual - Forecast)²))
├─ Example: RMSE = ₹50 Cr
└─ Interpretation: Typical error is ₹50 Cr
```

---

## A/B Testing for Decision Making {#testing}

### Proper Experimental Design

```
SCENARIO: Does giving 20% discount increase sales?

TRADITIONAL (WRONG) APPROACH:
├─ Observe baseline sales without discount: ₹100 Cr/month
├─ Implement 20% discount
├─ Observe new sales: ₹130 Cr/month
├─ Conclude: "Discount increased sales by 30%!"
└─ Problem: Season changed, competitor left, other factors!

─────────────────────────────────────────────────────

A/B TEST (CORRECT) APPROACH:

Setup:
├─ Divide customers into 2 equal random groups
│  ├─ Group A (Control): No discount
│  └─ Group B (Treatment): 20% discount
├─ Run simultaneously for same time period
├─ Ensure randomization is truly random
└─ Sample size: Usually 1000+ per group minimum

Collection Period: 7-14 days

Results Measurement:
├─ Group A Results:
│  ├─ Revenue: ₹100 Cr
│  ├─ Avg Order Value: ₹3,000
│  └─ Conversion Rate: 5%
│
├─ Group B Results:
│  ├─ Revenue: ₹115 Cr
│  ├─ Avg Order Value: ₹2,850 (lower due to discount!)
│  └─ Conversion Rate: 6.5%
│
└─ Difference: Group B is 15% higher

Statistical Significance Test:
├─ Is 15% difference real or just random chance?
├─ Perform Chi-Square or T-test
├─ P-value = 0.03 (3% chance of being random)
└─ Conclusion: 97% confident difference is REAL

Decision:
├─ If P < 0.05: Statistically significant → Implement
├─ If P ≥ 0.05: Not significant → Test inconclusive
└─ In this case: YES, implement 20% discount

─────────────────────────────────────────────────────

SAMPLE SIZE CALCULATION:

For statistical validity, need sufficient sample size

Factors affecting sample size:
├─ Baseline conversion rate
├─ Expected improvement percentage
├─ Confidence level (usually 95%)
└─ Power (usually 80%)

Online calculator: optimizely.com/sample-size-calculator

Example:
├─ Baseline conversion: 5%
├─ Expected improvement: 10%
├─ Result: Need ~8,000 users per variant (16,000 total)
│  
└─ If tested with only 100 users: Results unreliable!
```

### Common E-Commerce A/B Tests

```
1. DISCOUNT TESTING
   Test: 10% vs 15% vs 20% discount
   Metric: Revenue, conversion rate, AOV
   Duration: 1-2 weeks

2. CHECKOUT PROCESS
   Test: 1-click vs 3-step checkout
   Metric: Checkout abandonment rate
   Duration: 2-4 weeks

3. PRODUCT PAGE LAYOUT
   Test: Gallery on left vs right
   Test: Show reviews first vs specs first
   Metric: Click-through to product, add-to-cart rate
   Duration: 1-2 weeks

4. EMAIL SUBJECT LINES
   Test: "Exclusive offer" vs "Limited time"
   Metric: Open rate, click rate
   Duration: 2-3 days

5. PRICING STRATEGY
   Test: ₹2,999 vs ₹3,099 vs ₹2,899
   Metric: Units sold, revenue
   Duration: 1-2 weeks

6. PAYMENT METHODS
   Test: Show credit card first vs UPI first
   Metric: Payment success rate, method preferences
   Duration: 1 week

7. RECOMMENDATION ALGORITHM
   Test: Algorithm A vs Algorithm B
   Metric: Cross-sell rate, average order value
   Duration: 2-4 weeks
```

---

## Summary: Key Takeaways

✅ **Statistics helps you:**
- Understand patterns (trends, seasonality)
- Segment customers (RFM, clustering)
- Test hypotheses (correlation, causation)
- Predict future (time series, regression)
- Make decisions (A/B testing, confidence intervals)

✅ **Probability helps you:**
- Calculate likelihoods (conversion rates, churn)
- Prioritize customers (Bayes' theorem)
- Optimize marketing (targeting, ROI)
- Plan inventory (demand distribution)

✅ **Apply to Amazon India:**
- Track revenue trends & growth
- Segment 1M customers by RFM
- Predict churn and lifetime value
- Test discount strategies
- Optimize for Diwali, Prime Day, festivals
- Make data-driven decisions

---

*Document created for Amazon India Data Science Project*
*Last updated: 2025-04-08*
