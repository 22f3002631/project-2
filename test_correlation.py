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

# Check median
median = df['sales'].median()
print(f'\nMedian: {median}')
print(f'Expected: 140')

# Check total sales
total = df['sales'].sum()
print(f'\nTotal: {total}')
print(f'Expected: 1140')
