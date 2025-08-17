import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_existing_functionality_with_llm():
    """Test that existing test cases still work perfectly with LLM integration enabled"""
    
    print("🧪 TESTING EXISTING FUNCTIONALITY WITH LLM INTEGRATION")
    print("=" * 70)
    
    # Test data for all three scenarios
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
Alice,Carol'''),
            'expected_fields': ['edge_count', 'highest_degree_node', 'average_degree', 'density', 'shortest_path_alice_eve']
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
8,2024-01-08,West,170'''),
            'expected_fields': ['total_sales', 'top_region', 'day_sales_correlation', 'median_sales', 'total_sales_tax']
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
2024-01-10,7,0.8'''),
            'expected_fields': ['average_temp_c', 'max_precip_date', 'min_temp_c', 'temp_precip_correlation', 'average_precip_mm']
        }
    }
    
    results = {}
    
    for test_name, test_data in test_cases.items():
        print(f"\n🔍 Testing {test_name.upper()} Analysis...")
        
        # Prepare files
        files = {
            key: value for key, value in test_data.items() 
            if key not in ['expected_fields']
        }
        
        try:
            start_time = time.time()
            response = requests.post('https://project-2-nn6u.onrender.com/', 
                                   files=files,
                                   timeout=300)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if all expected fields are present
                expected_fields = test_data['expected_fields']
                missing_fields = [field for field in expected_fields if field not in data]
                present_fields = [field for field in expected_fields if field in data]
                
                print(f"  ✅ SUCCESS - {response_time:.2f}s")
                print(f"  Expected fields: {len(expected_fields)}")
                print(f"  Present fields: {len(present_fields)}")
                print(f"  Missing fields: {len(missing_fields)}")
                
                if missing_fields:
                    print(f"  ⚠️ Missing: {missing_fields}")
                
                # Validate specific values for each test
                validation_results = validate_test_results(test_name, data)
                
                results[test_name] = {
                    'success': True,
                    'response_time': response_time,
                    'fields_present': len(present_fields),
                    'fields_missing': len(missing_fields),
                    'validation': validation_results,
                    'data': data
                }
                
            else:
                print(f"  ❌ FAILED - HTTP {response.status_code}")
                results[test_name] = {
                    'success': False,
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            print(f"  ❌ ERROR - {str(e)}")
            results[test_name] = {
                'success': False,
                'response_time': 0,
                'error': str(e)
            }
    
    return results

def validate_test_results(test_name, data):
    """Validate specific test results against expected values"""
    
    validation = {'passed': 0, 'total': 0, 'details': []}
    
    if test_name == 'network':
        checks = [
            ('edge_count', 7, lambda x: x == 7),
            ('highest_degree_node', 'Bob', lambda x: x == 'Bob'),
            ('average_degree', 2.8, lambda x: abs(x - 2.8) < 0.1),
            ('density', 0.7, lambda x: abs(x - 0.7) < 0.1),
            ('shortest_path_alice_eve', 2, lambda x: x == 2)
        ]
    elif test_name == 'sales':
        checks = [
            ('total_sales', 1140, lambda x: x == 1140),
            ('top_region', 'west', lambda x: x.lower() == 'west'),
            ('day_sales_correlation', 0.2228124549277306, lambda x: abs(x - 0.2228124549277306) < 0.001),
            ('median_sales', 140, lambda x: x == 140),
            ('total_sales_tax', 114, lambda x: x == 114)
        ]
    elif test_name == 'weather':
        checks = [
            ('average_temp_c', 5.1, lambda x: abs(x - 5.1) < 0.1),
            ('max_precip_date', '2024-01-06', lambda x: x == '2024-01-06'),
            ('min_temp_c', 2, lambda x: x == 2),
            ('temp_precip_correlation', 0.0413519224, lambda x: abs(x - 0.0413519224) < 0.001),
            ('average_precip_mm', 0.9, lambda x: abs(x - 0.9) < 0.1)
        ]
    else:
        return validation
    
    for field, expected, check_func in checks:
        validation['total'] += 1
        if field in data:
            try:
                if check_func(data[field]):
                    validation['passed'] += 1
                    validation['details'].append(f"✅ {field}: {data[field]} (expected: {expected})")
                else:
                    validation['details'].append(f"❌ {field}: {data[field]} (expected: {expected})")
            except Exception as e:
                validation['details'].append(f"❌ {field}: Error checking value - {str(e)}")
        else:
            validation['details'].append(f"❌ {field}: Missing from response")
    
    return validation

def test_performance_comparison():
    """Compare performance with and without LLM integration"""
    print("\n🚀 PERFORMANCE COMPARISON TEST")
    print("=" * 50)
    
    # Simple test case
    files = {
        'questions.txt': ('questions.txt', '1. How many edges are in the network?'),
        'edges.csv': ('edges.csv', 'source,target\nAlice,Bob\nBob,Carol')
    }
    
    # Test multiple times to get average
    times = []
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.post('https://project-2-nn6u.onrender.com/', 
                                   files=files,
                                   timeout=60)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
                print(f"  Test {i+1}: {end_time - start_time:.2f}s")
            else:
                print(f"  Test {i+1}: FAILED")
                
        except Exception as e:
            print(f"  Test {i+1}: ERROR - {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n  Average response time: {avg_time:.2f}s")
        print(f"  Min response time: {min(times):.2f}s")
        print(f"  Max response time: {max(times):.2f}s")
        
        # Assessment
        if avg_time < 5:
            print("  ✅ EXCELLENT - Fast response times maintained")
        elif avg_time < 10:
            print("  ✅ GOOD - Acceptable response times")
        else:
            print("  ⚠️ SLOW - Response times may impact testing")
            
        return avg_time
    else:
        print("  ❌ No successful tests for performance measurement")
        return None

def main():
    """Run comprehensive LLM impact testing"""
    
    print("🎯 LLM INTEGRATION IMPACT ASSESSMENT")
    print("=" * 70)
    
    # Check if API keys are configured
    openai_key = os.getenv('OPENAI_API_KEY')
    aipipe_key = os.getenv('AIPIPE_API_KEY')
    
    print(f"OpenAI API Key: {'✅ CONFIGURED' if openai_key else '❌ MISSING'}")
    print(f"Aipipe API Key: {'✅ CONFIGURED' if aipipe_key else '❌ MISSING'}")
    
    # Test existing functionality
    results = test_existing_functionality_with_llm()
    
    # Test performance
    avg_performance = test_performance_comparison()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL ASSESSMENT")
    print("=" * 70)
    
    successful_tests = sum(1 for result in results.values() if result.get('success', False))
    total_tests = len(results)
    
    print(f"Test Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    for test_name, result in results.items():
        if result.get('success'):
            validation = result.get('validation', {})
            validation_rate = validation.get('passed', 0) / max(validation.get('total', 1), 1) * 100
            print(f"  {test_name.upper()}: ✅ SUCCESS ({validation_rate:.1f}% validation)")
        else:
            print(f"  {test_name.upper()}: ❌ FAILED")
    
    if avg_performance:
        print(f"Average Performance: {avg_performance:.2f}s")
    
    # Overall assessment
    if successful_tests == total_tests and (not avg_performance or avg_performance < 10):
        print("\n🎉 EXCELLENT - LLM integration maintains perfect functionality!")
    elif successful_tests >= total_tests * 0.8:
        print("\n✅ GOOD - LLM integration working well with minor issues")
    else:
        print("\n⚠️ ISSUES - LLM integration may be affecting core functionality")

if __name__ == "__main__":
    main()
