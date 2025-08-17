import os
import json
import time
import requests
from dotenv import load_dotenv
from llm_integration import LLMIntegration

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that environment variables are properly configured"""
    print("=== ENVIRONMENT VARIABLE CONFIGURATION TEST ===")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    aipipe_key = os.getenv('AIPIPE_API_KEY')
    
    print(f"OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    if openai_key:
        print(f"  Length: {len(openai_key)} characters")
        print(f"  Starts with: {openai_key[:10]}...")
    
    print(f"AIPIPE_API_KEY: {'✅ SET' if aipipe_key else '❌ MISSING'}")
    if aipipe_key:
        print(f"  Length: {len(aipipe_key)} characters")
        print(f"  Starts with: {aipipe_key[:10]}...")
    
    return bool(openai_key), bool(aipipe_key)

def test_llm_initialization():
    """Test LLM integration initialization"""
    print("\n=== LLM INTEGRATION INITIALIZATION TEST ===")
    
    try:
        llm = LLMIntegration()
        
        print(f"OpenAI Client: {'✅ INITIALIZED' if llm.openai_client else '❌ NOT INITIALIZED'}")
        print(f"Aipipe Client: {'✅ INITIALIZED' if llm.aipipe_client else '❌ NOT INITIALIZED'}")
        
        return llm
    except Exception as e:
        print(f"❌ INITIALIZATION FAILED: {str(e)}")
        return None

def test_openai_api():
    """Test OpenAI API functionality"""
    print("\n=== OPENAI API FUNCTIONALITY TEST ===")
    
    try:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Test with a simple prompt
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
                {"role": "user", "content": "Analyze this simple question: 'What is 2+2?' Respond with JSON containing 'question', 'answer', and 'confidence'."}
            ],
            max_tokens=100,
            temperature=0.1
        )
        end_time = time.time()
        
        content = response.choices[0].message.content
        response_time = end_time - start_time
        
        print(f"✅ OpenAI API SUCCESS")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Response length: {len(content)} characters")
        print(f"  Response preview: {content[:100]}...")
        
        # Try to parse as JSON
        try:
            json_response = json.loads(content)
            print(f"  JSON parsing: ✅ SUCCESS")
            return True, response_time, json_response
        except json.JSONDecodeError:
            print(f"  JSON parsing: ❌ FAILED")
            return True, response_time, content
            
    except Exception as e:
        print(f"❌ OpenAI API FAILED: {str(e)}")
        return False, 0, None

def test_aipipe_api():
    """Test Aipipe API functionality"""
    print("\n=== AIPIPE API FUNCTIONALITY TEST ===")
    
    try:
        aipipe_key = os.getenv('AIPIPE_API_KEY')
        
        headers = {
            'Authorization': f'Bearer {aipipe_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
                {"role": "user", "content": "Analyze this simple question: 'What is 3+3?' Respond with JSON containing 'question', 'answer', and 'confidence'."}
            ],
            'max_tokens': 100,
            'temperature': 0.1
        }
        
        start_time = time.time()
        response = requests.post(
            'https://aipipe.org/openrouter/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print(f"✅ Aipipe API SUCCESS")
            print(f"  Response time: {response_time:.2f}s")
            print(f"  Response length: {len(content)} characters")
            print(f"  Response preview: {content[:100]}...")
            
            # Try to parse as JSON
            try:
                json_response = json.loads(content)
                print(f"  JSON parsing: ✅ SUCCESS")
                return True, response_time, json_response
            except json.JSONDecodeError:
                print(f"  JSON parsing: ❌ FAILED")
                return True, response_time, content
        else:
            print(f"❌ Aipipe API FAILED: HTTP {response.status_code}")
            print(f"  Error: {response.text}")
            return False, response_time, None
            
    except Exception as e:
        print(f"❌ Aipipe API FAILED: {str(e)}")
        return False, 0, None

def test_llm_integration_methods():
    """Test LLM integration methods"""
    print("\n=== LLM INTEGRATION METHODS TEST ===")
    
    llm = LLMIntegration()
    
    # Test question processing
    test_question = "What is the correlation between two variables in a dataset?"
    test_files = {}
    
    try:
        start_time = time.time()
        result = llm.process_question(test_question, test_files)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"✅ LLM Integration SUCCESS")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Result type: {type(result)}")
        print(f"  Result preview: {str(result)[:100]}...")
        
        return True, response_time, result
        
    except Exception as e:
        print(f"❌ LLM Integration FAILED: {str(e)}")
        return False, 0, None

def test_fallback_behavior():
    """Test fallback behavior when LLM is not available"""
    print("\n=== FALLBACK BEHAVIOR TEST ===")
    
    # Temporarily disable API keys to test fallback
    original_openai = os.environ.get('OPENAI_API_KEY')
    original_aipipe = os.environ.get('AIPIPE_API_KEY')
    
    try:
        # Remove API keys temporarily
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        if 'AIPIPE_API_KEY' in os.environ:
            del os.environ['AIPIPE_API_KEY']
        
        llm = LLMIntegration()
        
        test_question = "How many items are in the dataset?"
        test_files = {}
        
        start_time = time.time()
        result = llm.process_question(test_question, test_files)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"✅ Fallback behavior SUCCESS")
        print(f"  Response time: {response_time:.2f}s")
        print(f"  Fallback result: {result}")
        
        return True, response_time, result
        
    except Exception as e:
        print(f"❌ Fallback behavior FAILED: {str(e)}")
        return False, 0, None
        
    finally:
        # Restore API keys
        if original_openai:
            os.environ['OPENAI_API_KEY'] = original_openai
        if original_aipipe:
            os.environ['AIPIPE_API_KEY'] = original_aipipe

def main():
    """Run comprehensive LLM integration tests"""
    print("🧪 COMPREHENSIVE LLM INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Test 1: Environment Variables
    openai_configured, aipipe_configured = test_environment_variables()
    
    # Test 2: LLM Initialization
    llm = test_llm_initialization()
    
    # Test 3: OpenAI API
    openai_success, openai_time, openai_result = test_openai_api() if openai_configured else (False, 0, None)
    
    # Test 4: Aipipe API
    aipipe_success, aipipe_time, aipipe_result = test_aipipe_api() if aipipe_configured else (False, 0, None)
    
    # Test 5: LLM Integration Methods
    integration_success, integration_time, integration_result = test_llm_integration_methods()
    
    # Test 6: Fallback Behavior
    fallback_success, fallback_time, fallback_result = test_fallback_behavior()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    print(f"Environment Configuration: {'✅ PASS' if openai_configured and aipipe_configured else '⚠️ PARTIAL' if openai_configured or aipipe_configured else '❌ FAIL'}")
    print(f"LLM Initialization: {'✅ PASS' if llm else '❌ FAIL'}")
    print(f"OpenAI API: {'✅ PASS' if openai_success else '❌ FAIL'} ({openai_time:.2f}s)")
    print(f"Aipipe API: {'✅ PASS' if aipipe_success else '❌ FAIL'} ({aipipe_time:.2f}s)")
    print(f"LLM Integration: {'✅ PASS' if integration_success else '❌ FAIL'} ({integration_time:.2f}s)")
    print(f"Fallback Behavior: {'✅ PASS' if fallback_success else '❌ FAIL'} ({fallback_time:.2f}s)")
    
    # Overall assessment
    total_tests = 6
    passed_tests = sum([
        openai_configured and aipipe_configured,
        bool(llm),
        openai_success,
        aipipe_success,
        integration_success,
        fallback_success
    ])
    
    print(f"\nOverall Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - LLM Integration fully functional!")
    elif passed_tests >= 4:
        print("✅ MOSTLY WORKING - LLM Integration functional with minor issues")
    else:
        print("⚠️ ISSUES DETECTED - LLM Integration needs attention")

if __name__ == "__main__":
    main()
