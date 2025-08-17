import pandas as pd
import numpy as np
from io import StringIO

# Create the exact test data from the sales test
sales_data = '''order_id,date,region,sales
1,2024-01-01,North,100
2,2024-01-02,South,150
3,2024-01-03,East,120
4,2024-01-04,West,200
5,2024-01-05,North,110
6,2024-01-06,South,160
7,2024-01-07,East,130
8,2024-01-08,West,170'''

# Parse the data
df = pd.read_csv(StringIO(sales_data))

# Calculate day of month
df['day'] = pd.to_datetime(df['date']).dt.day
print('Data:')
print(df[['day', 'sales']])

# Calculate correlation
correlation = df['day'].corr(df['sales'])
print(f'\nCorrelation: {correlation}')
print(f'Expected: 0.2228124549277306')
print(f'Match: {abs(correlation - 0.2228124549277306) < 0.001}')

# Try different approaches
print('\n=== Different approaches ===')

# Method 1: Direct correlation
print(f'Method 1 (direct): {df["day"].corr(df["sales"])}')

# Method 2: Using numpy
print(f'Method 2 (numpy): {np.corrcoef(df["day"], df["sales"])[0,1]}')

# Method 3: Manual calculation
x = df['day'].values
y = df['sales'].values
mean_x = np.mean(x)
mean_y = np.mean(y)
numerator = np.sum((x - mean_x) * (y - mean_y))
denominator = np.sqrt(np.sum((x - mean_x)**2) * np.sum((y - mean_y)**2))
manual_corr = numerator / denominator
print(f'Method 3 (manual): {manual_corr}')

# Check if we need to use order_id instead
df['order_id_day'] = df['order_id']
correlation_order = df['order_id_day'].corr(df['sales'])
print(f'Order ID correlation: {correlation_order}')
print(f'Order ID Expected match: {abs(correlation_order - 0.2228124549277306) < 0.001}')
