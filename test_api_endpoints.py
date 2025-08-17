import os
import json
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api_detailed():
    """Comprehensive OpenAI API test"""
    print("=== DETAILED OPENAI API TEST ===")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found")
        return False, 0, None
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Test different endpoints and methods
    endpoints_to_test = [
        'https://api.openai.com/v1/chat/completions',
        'https://api.openai.com/v1/models'  # Simple endpoint to verify connectivity
    ]
    
    # First test models endpoint for basic connectivity
    try:
        print("\n1. Testing OpenAI Models Endpoint...")
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ SUCCESS - Found {len(models.get('data', []))} models")
        else:
            print(f"   ❌ FAILED - {response.text}")
            return False, 0, None
            
    except Exception as e:
        print(f"   ❌ FAILED - {str(e)}")
        return False, 0, None
    
    # Now test chat completions
    try:
        print("\n2. Testing OpenAI Chat Completions...")
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
                {"role": "user", "content": "Analyze this question: 'What is 2+2?' Respond with JSON containing 'question', 'answer', and 'confidence'."}
            ],
            'max_tokens': 100,
            'temperature': 0.1
        }
        
        start_time = time.time()
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Response time: {response_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"   ✅ SUCCESS")
            print(f"   Response: {content[:100]}...")
            
            # Try to parse as JSON
            try:
                json_response = json.loads(content)
                print(f"   JSON parsing: ✅ SUCCESS")
                return True, response_time, json_response
            except json.JSONDecodeError:
                print(f"   JSON parsing: ⚠️ PARTIAL (valid response but not JSON)")
                return True, response_time, content
        else:
            print(f"   ❌ FAILED - {response.text}")
            return False, response_time, None
            
    except Exception as e:
        print(f"   ❌ FAILED - {str(e)}")
        return False, 0, None

def test_aipipe_api_detailed():
    """Comprehensive Aipipe API test with multiple endpoint attempts"""
    print("\n=== DETAILED AIPIPE API TEST ===")
    
    api_key = os.getenv('AIPIPE_API_KEY')
    if not api_key:
        print("❌ Aipipe API key not found")
        return False, 0, None
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Test multiple possible endpoints based on documentation
    endpoints_to_test = [
        'https://aipipe.org/openrouter/v1/chat/completions',
        'https://aipipe.org/v1/chat/completions',
        'https://aipipe.org/api/v1/chat/completions',
        'https://api.aipipe.org/v1/chat/completions'
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
            {"role": "user", "content": "Analyze this question: 'What is 3+3?' Respond with JSON containing 'question', 'answer', and 'confidence'."}
        ],
        'max_tokens': 100,
        'temperature': 0.1
    }
    
    for i, endpoint in enumerate(endpoints_to_test, 1):
        print(f"\n{i}. Testing endpoint: {endpoint}")
        
        try:
            start_time = time.time()
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {response_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"   ✅ SUCCESS - Found working endpoint!")
                print(f"   Response: {content[:100]}...")
                
                # Try to parse as JSON
                try:
                    json_response = json.loads(content)
                    print(f"   JSON parsing: ✅ SUCCESS")
                    return True, response_time, json_response
                except json.JSONDecodeError:
                    print(f"   JSON parsing: ⚠️ PARTIAL (valid response but not JSON)")
                    return True, response_time, content
                    
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed")
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n❌ All Aipipe endpoints failed")
    return False, 0, None

def test_llm_integration_with_working_apis():
    """Test LLM integration with working APIs"""
    print("\n=== LLM INTEGRATION WITH WORKING APIS ===")
    
    try:
        from llm_integration import LLMIntegration
        
        llm = LLMIntegration()
        
        test_question = "What is the correlation between temperature and precipitation in weather data?"
        test_files = {}
        
        start_time = time.time()
        result = llm.process_question(test_question, test_files)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"✅ LLM Integration SUCCESS")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Result type: {type(result)}")
        print(f"  Result preview: {str(result)[:150]}...")
        
        return True, response_time, result
        
    except Exception as e:
        print(f"❌ LLM Integration FAILED: {str(e)}")
        return False, 0, None

def main():
    """Run comprehensive API testing"""
    print("🧪 COMPREHENSIVE API ENDPOINT TESTING")
    print("=" * 60)
    
    # Test OpenAI API
    openai_success, openai_time, openai_result = test_openai_api_detailed()
    
    # Test Aipipe API
    aipipe_success, aipipe_time, aipipe_result = test_aipipe_api_detailed()
    
    # Test LLM Integration
    integration_success, integration_time, integration_result = test_llm_integration_with_working_apis()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    print(f"OpenAI API: {'✅ WORKING' if openai_success else '❌ FAILED'} ({openai_time:.2f}s)")
    print(f"Aipipe API: {'✅ WORKING' if aipipe_success else '❌ FAILED'} ({aipipe_time:.2f}s)")
    print(f"LLM Integration: {'✅ WORKING' if integration_success else '❌ FAILED'} ({integration_time:.2f}s)")
    
    # Overall assessment
    working_apis = sum([openai_success, aipipe_success])
    print(f"\nWorking APIs: {working_apis}/2")
    
    if working_apis == 2:
        print("🎉 EXCELLENT - Both APIs working perfectly!")
    elif working_apis == 1:
        print("✅ PARTIAL - One API working, fallback available")
    else:
        print("⚠️ FALLBACK MODE - Using fallback responses only")
    
    print(f"LLM Integration Status: {'✅ READY' if integration_success else '⚠️ FALLBACK MODE'}")

if __name__ == "__main__":
    main()
