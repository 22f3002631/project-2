#!/usr/bin/env python3
"""
Deployment verification script for Data Analyst Agent
Tests the deployed API to ensure it meets testing requirements
"""

import requests
import json
import time
import concurrent.futures
import sys

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_endpoint(base_url, test_name, questions_content):
    """Test the API endpoint with given questions"""
    start_time = time.time()
    
    try:
        files = {
            'questions.txt': ('questions.txt', questions_content, 'text/plain')
        }
        
        print(f"🔄 Testing {test_name}...")
        response = requests.post(f"{base_url}/api/", files=files, timeout=300)
        
        elapsed = time.time() - start_time
        print(f"⏱️  {test_name} completed in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ {test_name} - Valid JSON response")
                print(f"📊 Response type: {type(result)}")
                if isinstance(result, list):
                    print(f"📊 Array length: {len(result)}")
                elif isinstance(result, dict):
                    print(f"📊 Object keys: {list(result.keys())}")
                return True, elapsed, result
            except json.JSONDecodeError:
                print(f"❌ {test_name} - Invalid JSON response")
                return False, elapsed, None
        else:
            print(f"❌ {test_name} - HTTP {response.status_code}: {response.text}")
            return False, elapsed, None
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ {test_name} - TIMEOUT after {elapsed:.2f} seconds")
        return False, elapsed, None
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {test_name} - Error: {e}")
        return False, elapsed, None

def test_concurrent_requests(base_url):
    """Test concurrent API requests to simulate testing environment"""
    
    # Define test cases
    test_cases = [
        ("Wikipedia Test", """
Scrape the list of highest grossing films from Wikipedia. It is at the URL:
https://en.wikipedia.org/wiki/List_of_highest-grossing_films

Answer the following questions and respond with a JSON array of strings containing the answer.

1. How many $2 bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between the Rank and Peak?
4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
"""),
        ("Simple Analysis", "What is the average of the numbers 1, 2, 3, 4, 5?"),
        ("Data Question", "Analyze the following data and provide basic statistics: [10, 20, 30, 40, 50]")
    ]
    
    print(f"\n🚀 Starting concurrent request test...")
    print(f"📡 Testing {len(test_cases)} simultaneous requests")
    
    # Execute concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for test_name, questions in test_cases:
            future = executor.submit(test_api_endpoint, base_url, test_name, questions)
            futures.append((test_name, future))
        
        # Collect results
        results = []
        for test_name, future in futures:
            success, elapsed, response = future.result()
            results.append((test_name, success, elapsed, response))
    
    # Report results
    print(f"\n📋 Concurrent Test Results:")
    print(f"{'Test Name':<20} {'Status':<10} {'Time (s)':<10} {'Response':<20}")
    print("-" * 70)
    
    all_passed = True
    for test_name, success, elapsed, response in results:
        status = "✅ PASS" if success else "❌ FAIL"
        response_summary = "Valid JSON" if success else "Failed"
        print(f"{test_name:<20} {status:<10} {elapsed:<10.2f} {response_summary:<20}")
        if not success:
            all_passed = False
    
    return all_passed

def main():
    """Main verification function"""
    if len(sys.argv) != 2:
        print("Usage: python verify_deployment.py <base_url>")
        print("Example: python verify_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🔍 Verifying deployment at: {base_url}")
    print("=" * 60)
    
    # Test health endpoint
    if not test_health_endpoint(base_url):
        print("❌ Health check failed. Deployment verification failed.")
        sys.exit(1)
    
    # Test concurrent requests
    if test_concurrent_requests(base_url):
        print(f"\n🎉 All tests passed! Deployment is ready for automated testing.")
        print(f"🔗 API Endpoint: {base_url}/api/")
        print(f"🔗 Health Check: {base_url}/health")
    else:
        print(f"\n❌ Some tests failed. Please review and fix issues before submission.")
        sys.exit(1)

if __name__ == "__main__":
    main()
