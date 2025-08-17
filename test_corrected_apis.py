import os
import json
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_corrected_aipipe():
    """Test Aipipe with the correct endpoint from documentation"""
    print("🧪 TESTING CORRECTED AIPIPE ENDPOINT")
    print("=" * 45)
    
    api_key = os.getenv('AIPIPE_API_KEY')
    if not api_key:
        print("❌ Aipipe API key not found")
        return False, 0, None
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print("Endpoint: https://aipipe.org/openrouter/v1/chat/completions")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Use a model that should be available on OpenRouter
    payload = {
        'model': 'openai/gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
            {"role": "user", "content": "Analyze this question: 'What is 3+3?' Respond with JSON containing 'question', 'answer', and 'confidence'."}
        ],
        'max_tokens': 100,
        'temperature': 0.1
    }
    
    try:
        print("\n🚀 Making API request...")
        start_time = time.time()
        response = requests.post(
            'https://aipipe.org/openrouter/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Status: {response.status_code}")
        print(f"Response time: {response_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ SUCCESS!")
            print(f"Response: {content}")
            
            # Try to parse as JSON
            try:
                json_response = json.loads(content)
                print(f"JSON parsing: ✅ SUCCESS")
                print(f"Parsed response: {json.dumps(json_response, indent=2)}")
                return True, response_time, json_response
            except json.JSONDecodeError:
                print(f"JSON parsing: ⚠️ PARTIAL (valid response but not JSON)")
                return True, response_time, content
                
        elif response.status_code == 401:
            print(f"❌ Authentication failed")
            print(f"Response: {response.text}")
        elif response.status_code == 404:
            print(f"❌ Endpoint not found")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
        return False, response_time, None
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False, 0, None

def test_openai_with_different_models():
    """Test OpenAI API with different model specifications"""
    print("\n🧪 TESTING OPENAI WITH DIFFERENT APPROACHES")
    print("=" * 50)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found")
        return False, 0, None
    
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Try different models and approaches
    test_cases = [
        {
            'name': 'GPT-3.5-turbo (standard)',
            'model': 'gpt-3.5-turbo',
            'max_tokens': 50
        },
        {
            'name': 'GPT-3.5-turbo-0125 (specific version)',
            'model': 'gpt-3.5-turbo-0125',
            'max_tokens': 50
        },
        {
            'name': 'GPT-4o-mini (newer model)',
            'model': 'gpt-4o-mini',
            'max_tokens': 50
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🎯 Testing {test_case['name']}...")
        
        payload = {
            'model': test_case['model'],
            'messages': [
                {"role": "user", "content": "What is 2+2? Answer briefly."}
            ],
            'max_tokens': test_case['max_tokens'],
            'temperature': 0.1
        }
        
        try:
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
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {content}")
                return True, response_time, content
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
                print(f"   ❌ FAILED: {error_data.get('error', {}).get('message', response.text)}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    return False, 0, None

def test_llm_integration_updated():
    """Test the updated LLM integration"""
    print("\n🧪 TESTING UPDATED LLM INTEGRATION")
    print("=" * 40)
    
    try:
        from llm_integration import LLMIntegration
        
        llm = LLMIntegration()
        
        print(f"OpenAI Client: {'✅ INITIALIZED' if llm.openai_client else '❌ NOT INITIALIZED'}")
        print(f"Aipipe Client: {'✅ INITIALIZED' if llm.aipipe_client else '❌ NOT INITIALIZED'}")
        
        test_question = "What is the correlation between two variables in a dataset?"
        test_files = {}
        
        start_time = time.time()
        result = llm.process_question(test_question, test_files)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"✅ LLM Integration SUCCESS")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Result type: {type(result)}")
        print(f"  Result preview: {str(result)[:200]}...")
        
        return True, response_time, result
        
    except Exception as e:
        print(f"❌ LLM Integration FAILED: {str(e)}")
        return False, 0, None

def main():
    """Run corrected API tests"""
    print("🔧 TESTING CORRECTED API CONFIGURATIONS")
    print("=" * 60)
    
    # Test corrected Aipipe endpoint
    aipipe_success, aipipe_time, aipipe_result = test_corrected_aipipe()
    
    # Test OpenAI with different approaches
    openai_success, openai_time, openai_result = test_openai_with_different_models()
    
    # Test updated LLM integration
    integration_success, integration_time, integration_result = test_llm_integration_updated()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 CORRECTED API TEST SUMMARY")
    print("=" * 60)
    
    print(f"Aipipe API (corrected): {'✅ WORKING' if aipipe_success else '❌ FAILED'} ({aipipe_time:.2f}s)")
    print(f"OpenAI API (various models): {'✅ WORKING' if openai_success else '❌ FAILED'} ({openai_time:.2f}s)")
    print(f"LLM Integration: {'✅ WORKING' if integration_success else '❌ FAILED'} ({integration_time:.2f}s)")
    
    # Overall assessment
    working_apis = sum([aipipe_success, openai_success])
    print(f"\nWorking APIs: {working_apis}/2")
    
    if working_apis == 2:
        print("🎉 EXCELLENT - Both APIs working perfectly!")
    elif working_apis == 1:
        print("✅ PARTIAL - One API working, fallback available")
    else:
        print("⚠️ FALLBACK MODE - Using fallback responses only")
    
    print(f"LLM Integration Status: {'✅ READY' if integration_success else '⚠️ FALLBACK MODE'}")
    
    return working_apis, integration_success

if __name__ == "__main__":
    main()
