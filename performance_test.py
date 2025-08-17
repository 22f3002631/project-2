import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_single_request(test_name, files):
    """Test a single request and measure response time"""
    start_time = time.time()
    try:
        response = requests.post('https://project-2-nn6u.onrender.com/', 
                               files=files,
                               timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            return {
                'test': test_name,
                'success': True,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'response_size': len(str(data))
            }
        else:
            return {
                'test': test_name,
                'success': False,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'error': 'HTTP Error'
            }
    except Exception as e:
        end_time = time.time()
        return {
            'test': test_name,
            'success': False,
            'response_time': end_time - start_time,
            'error': str(e)
        }

# Test data for different scenarios
test_cases = {
    'network': {
        'questions.txt': ('questions.txt', '''1. How many edges are in the network?
2. Which node has the highest degree?
3. What is the average degree of the network?
4. What is the density of the network?
5. What is the shortest path length between Alice and Eve?'''),
        'edges.csv': ('edges.csv', '''source,target
Alice,Bob
Bob,Carol
Bob,David
Bob,Eve
Carol,David
David,Eve
Alice,Carol''')
    },
    'sales': {
        'questions.txt': ('questions.txt', '''1. What is the total sales amount?
2. Which region has the highest sales?
3. What is the correlation between day and sales?
4. What is the median sales value?
5. What is the total sales tax (10%)?'''),
        'sample-sales.csv': ('sample-sales.csv', '''order_id,date,region,sales
1,2024-01-01,North,100
2,2024-01-02,South,150
3,2024-01-03,East,120
4,2024-01-04,West,200
5,2024-01-05,North,110
6,2024-01-06,South,160
7,2024-01-07,East,130
8,2024-01-08,West,170''')
    },
    'weather': {
        'questions.txt': ('questions.txt', '''1. What is the average temperature?
2. Which date had the maximum precipitation?
3. What is the minimum temperature?
4. What is the correlation between temperature and precipitation?
5. What is the average precipitation?'''),
        'sample-weather.csv': ('sample-weather.csv', '''date,temperature_c,precip_mm
2024-01-01,5,0.5
2024-01-02,4,0.8
2024-01-03,6,0.2
2024-01-04,3,1.2
2024-01-05,7,0.0
2024-01-06,2,2.5
2024-01-07,8,0.1
2024-01-08,5,1.0
2024-01-09,4,0.9
2024-01-10,7,0.8''')
    }
}

print('=== PERFORMANCE AND CONCURRENCY TESTING ===')

# Test 1: Sequential requests to measure baseline performance
print('\n1. SEQUENTIAL PERFORMANCE TEST')
sequential_results = []
for test_name, files in test_cases.items():
    result = test_single_request(test_name, files)
    sequential_results.append(result)
    status = "SUCCESS" if result["success"] else "FAILED"
    print(f'{test_name.upper()}: {result["response_time"]:.2f}s - {status}')
    if not result['success']:
        print(f'  Error: {result.get("error", "Unknown")}')

# Test 2: Concurrent requests to test concurrency handling
print('\n2. CONCURRENT PERFORMANCE TEST (3 simultaneous requests)')
start_time = time.time()

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for test_name, files in test_cases.items():
        future = executor.submit(test_single_request, test_name, files)
        futures.append(future)
    
    results = []
    for future in as_completed(futures):
        result = future.result()
        results.append(result)

end_time = time.time()
total_concurrent_time = end_time - start_time

print(f'Total concurrent execution time: {total_concurrent_time:.2f}s')
for result in results:
    status = "SUCCESS" if result["success"] else "FAILED"
    print(f'{result["test"].upper()}: {result["response_time"]:.2f}s - {status}')
    if not result['success']:
        print(f'  Error: {result.get("error", "Unknown")}')

# Test 3: Timeout resilience test
print('\n3. TIMEOUT RESILIENCE TEST')
print('Testing if requests complete within 5-minute timeout...')

# All tests should complete well under 5 minutes
successful_results = [r for r in results if r['success']]
if successful_results:
    max_time = max(result['response_time'] for result in successful_results)
    print(f'Maximum response time: {max_time:.2f}s')
    print(f'5-minute timeout compliance: {"PASS" if max_time < 300 else "FAIL"}')
else:
    print('No successful requests to measure timeout compliance')

print('\n=== SUMMARY ===')
success_count = sum(1 for result in results if result['success'])
print(f'Successful concurrent requests: {success_count}/3')
if successful_results:
    max_time = max(result['response_time'] for result in successful_results)
    print(f'All requests under 5-minute timeout: {"YES" if max_time < 300 else "NO"}')
else:
    print('All requests under 5-minute timeout: NO (no successful requests)')
print(f'Concurrency support: {"WORKING" if success_count == 3 else "ISSUES DETECTED"}')
