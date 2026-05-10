import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

n = 5000

categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports', 'Beauty', 'Toys', 'Automotive']
regions = ['North', 'South', 'East', 'West', 'Central']
channels = ['Website', 'Mobile App', 'Marketplace', 'Social Media']
payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Wallet']
customer_segments = ['New', 'Returning', 'VIP', 'At-Risk']
shipping_status = ['Delivered', 'Shipped', 'Processing', 'Returned', 'Cancelled']

# Category-based pricing
cat_price_range = {
    'Electronics': (500, 80000),
    'Clothing': (200, 5000),
    'Home & Kitchen': (300, 15000),
    'Books': (100, 800),
    'Sports': (400, 20000),
    'Beauty': (150, 3000),
    'Toys': (200, 4000),
    'Automotive': (800, 50000),
}

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

dates = [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(n)]

category_list = [random.choice(categories) for _ in range(n)]
prices = [round(random.uniform(*cat_price_range[c]), 2) for c in category_list]
quantities = np.random.choice([1, 2, 3, 4, 5], n, p=[0.5, 0.25, 0.12, 0.08, 0.05])
discounts = np.random.choice([0, 5, 10, 15, 20, 25], n, p=[0.4, 0.15, 0.2, 0.1, 0.1, 0.05])
revenue = [round(p * q * (1 - d/100), 2) for p, q, d in zip(prices, quantities, discounts)]
ratings = np.round(np.clip(np.random.normal(4.0, 0.8, n), 1, 5), 1)

df = pd.DataFrame({
    'order_id': [f'ORD{100000 + i}' for i in range(n)],
    'order_date': dates,
    'customer_id': [f'CUST{random.randint(1000, 9999)}' for _ in range(n)],
    'customer_segment': [random.choice(customer_segments) for _ in range(n)],
    'category': category_list,
    'product_name': [f'{c} Product {random.randint(1,50)}' for c in category_list],
    'region': [random.choice(regions) for _ in range(n)],
    'channel': [random.choice(channels) for _ in range(n)],
    'payment_method': [random.choice(payment_methods) for _ in range(n)],
    'unit_price': prices,
    'quantity': quantities,
    'discount_pct': discounts,
    'revenue': revenue,
    'shipping_status': [random.choice(shipping_status) for _ in range(n)],
    'rating': ratings,
    'return_flag': [1 if s == 'Returned' else 0 for s in [random.choice(shipping_status) for _ in range(n)]],
})

df['order_date'] = pd.to_datetime(df['order_date'])
df['month'] = df['order_date'].dt.month
df['quarter'] = df['order_date'].dt.quarter
df['year'] = df['order_date'].dt.year
df['profit'] = df['revenue'] * np.random.uniform(0.1, 0.4, n).round(2)

df.to_csv('/home/claude/ecommerce_data.csv', index=False)
print(f"Dataset created: {df.shape}")
print(df.head(3))
