import requests
import json
import time

def test_retry_resilience(max_retries=4):
    """Test retry resilience by making multiple requests"""
    
    # Test data
    files = {
        'questions.txt': ('questions.txt', '''1. How many edges are in the network?
2. Which node has the highest degree?'''),
        'edges.csv': ('edges.csv', '''source,target
Alice,Bob
Bob,Carol''')
    }
    
    print('=== RETRY RESILIENCE TEST ===')
    print(f'Testing {max_retries} consecutive requests to simulate retry behavior...')
    
    results = []
    total_start_time = time.time()
    
    for attempt in range(1, max_retries + 1):
        print(f'\nAttempt {attempt}/{max_retries}:')
        start_time = time.time()
        
        try:
            response = requests.post('https://project-2-nn6u.onrender.com/', 
                                   files=files,
                                   timeout=300)  # 5 minute timeout
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f'  SUCCESS - {response_time:.2f}s')
                results.append({
                    'attempt': attempt,
                    'success': True,
                    'response_time': response_time,
                    'status_code': response.status_code
                })
            else:
                print(f'  FAILED - HTTP {response.status_code} - {response_time:.2f}s')
                results.append({
                    'attempt': attempt,
                    'success': False,
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'error': 'HTTP Error'
                })
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f'  FAILED - {str(e)} - {response_time:.2f}s')
            results.append({
                'attempt': attempt,
                'success': False,
                'response_time': response_time,
                'error': str(e)
            })
        
        # Small delay between attempts to simulate real retry behavior
        if attempt < max_retries:
            time.sleep(1)
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    print(f'\n=== RETRY TEST SUMMARY ===')
    print(f'Total test time: {total_time:.2f}s')
    
    successful_attempts = [r for r in results if r['success']]
    failed_attempts = [r for r in results if not r['success']]
    
    print(f'Successful attempts: {len(successful_attempts)}/{max_retries}')
    print(f'Failed attempts: {len(failed_attempts)}/{max_retries}')
    
    if successful_attempts:
        avg_response_time = sum(r['response_time'] for r in successful_attempts) / len(successful_attempts)
        max_response_time = max(r['response_time'] for r in successful_attempts)
        min_response_time = min(r['response_time'] for r in successful_attempts)
        
        print(f'Average response time: {avg_response_time:.2f}s')
        print(f'Min response time: {min_response_time:.2f}s')
        print(f'Max response time: {max_response_time:.2f}s')
        print(f'All under 5-minute timeout: {"YES" if max_response_time < 300 else "NO"}')
    
    if failed_attempts:
        print('\nFailed attempt details:')
        for attempt in failed_attempts:
            print(f'  Attempt {attempt["attempt"]}: {attempt.get("error", "Unknown error")}')
    
    # Overall assessment
    success_rate = len(successful_attempts) / max_retries * 100
    print(f'\nSuccess rate: {success_rate:.1f}%')
    
    if success_rate >= 75:
        print('ASSESSMENT: EXCELLENT - High reliability for retry scenarios')
    elif success_rate >= 50:
        print('ASSESSMENT: GOOD - Acceptable reliability for retry scenarios')
    else:
        print('ASSESSMENT: POOR - May have issues with retry scenarios')
    
    return results

if __name__ == "__main__":
    test_retry_resilience()
