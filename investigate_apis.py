import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def investigate_aipipe_structure():
    """Investigate Aipipe API structure and available endpoints"""
    print("🔍 INVESTIGATING AIPIPE API STRUCTURE")
    print("=" * 50)
    
    base_urls = [
        'https://aipipe.org',
        'https://api.aipipe.org',
        'https://aipipe.org/api'
    ]
    
    common_paths = [
        '/',
        '/v1',
        '/api',
        '/docs',
        '/openapi.json',
        '/swagger',
        '/.well-known',
        '/health',
        '/status'
    ]
    
    for base_url in base_urls:
        print(f"\n🌐 Testing base URL: {base_url}")
        
        for path in common_paths:
            try:
                url = f"{base_url}{path}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ {path} - Status: {response.status_code}")
                    
                    # Try to get useful info from response
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"     JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        except:
                            pass
                    elif 'html' in content_type:
                        # Look for API documentation links
                        text = response.text.lower()
                        if 'api' in text or 'documentation' in text:
                            print(f"     Contains API/documentation references")
                    
                elif response.status_code == 404:
                    print(f"  ❌ {path} - Not found")
                else:
                    print(f"  ⚠️ {path} - Status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {path} - Connection failed")
            except requests.exceptions.Timeout:
                print(f"  ❌ {path} - Timeout")
            except Exception as e:
                print(f"  ❌ {path} - Error: {str(e)}")

def test_aipipe_authentication():
    """Test different authentication methods for Aipipe"""
    print("\n🔐 TESTING AIPIPE AUTHENTICATION METHODS")
    print("=" * 50)
    
    api_key = os.getenv('AIPIPE_API_KEY')
    if not api_key:
        print("❌ No Aipipe API key found")
        return
    
    # Test different authentication headers
    auth_methods = [
        {'Authorization': f'Bearer {api_key}'},
        {'Authorization': f'Token {api_key}'},
        {'X-API-Key': api_key},
        {'api-key': api_key},
        {'apikey': api_key}
    ]
    
    # Test different possible endpoints
    endpoints = [
        'https://aipipe.org/v1/models',
        'https://aipipe.org/api/v1/models',
        'https://aipipe.org/models',
        'https://api.aipipe.org/v1/models',
        'https://aipipe.org/v1/chat/completions',
        'https://aipipe.org/api/v1/chat/completions'
    ]
    
    for endpoint in endpoints:
        print(f"\n🎯 Testing endpoint: {endpoint}")
        
        for i, headers in enumerate(auth_methods, 1):
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                auth_type = list(headers.keys())[0]
                
                if response.status_code == 200:
                    print(f"  ✅ Auth method {i} ({auth_type}): SUCCESS")
                    try:
                        data = response.json()
                        print(f"     Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"     Response: {response.text[:100]}...")
                    return  # Found working method
                elif response.status_code == 401:
                    print(f"  ❌ Auth method {i} ({auth_type}): Unauthorized")
                elif response.status_code == 404:
                    print(f"  ❌ Auth method {i} ({auth_type}): Not found")
                else:
                    print(f"  ⚠️ Auth method {i} ({auth_type}): Status {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Auth method {i} ({auth_type}): {str(e)}")

def investigate_openai_key():
    """Investigate OpenAI API key issues"""
    print("\n🔍 INVESTIGATING OPENAI API KEY")
    print("=" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    print(f"Key format: {api_key[:15]}...{api_key[-10:]}")
    print(f"Key length: {len(api_key)} characters")
    print(f"Starts with 'sk-': {'✅' if api_key.startswith('sk-') else '❌'}")
    
    # Check if it's a project key vs user key
    if api_key.startswith('sk-proj-'):
        print("Key type: ✅ Project API key")
    elif api_key.startswith('sk-'):
        print("Key type: ✅ User API key")
    else:
        print("Key type: ❌ Unknown format")
    
    # Test with a simple request
    print("\n🧪 Testing OpenAI API connectivity...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test the models endpoint first (simpler than chat)
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ OpenAI API key is working!")
            models = response.json()
            print(f"Available models: {len(models.get('data', []))}")
        elif response.status_code == 401:
            print("❌ Authentication failed")
            error_data = response.json()
            print(f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def check_environment_loading():
    """Check if environment variables are loading correctly"""
    print("\n🔧 CHECKING ENVIRONMENT VARIABLE LOADING")
    print("=" * 45)
    
    # Check if .env file exists
    env_file_exists = os.path.exists('.env')
    print(f".env file exists: {'✅' if env_file_exists else '❌'}")
    
    if env_file_exists:
        with open('.env', 'r') as f:
            content = f.read()
            print(f".env file size: {len(content)} characters")
            print(f"Contains OPENAI_API_KEY: {'✅' if 'OPENAI_API_KEY' in content else '❌'}")
            print(f"Contains AIPIPE_API_KEY: {'✅' if 'AIPIPE_API_KEY' in content else '❌'}")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    aipipe_key = os.getenv('AIPIPE_API_KEY')
    
    print(f"\nLoaded OPENAI_API_KEY: {'✅' if openai_key else '❌'}")
    if openai_key:
        print(f"  Length: {len(openai_key)}")
        print(f"  Preview: {openai_key[:20]}...{openai_key[-10:]}")
    
    print(f"Loaded AIPIPE_API_KEY: {'✅' if aipipe_key else '❌'}")
    if aipipe_key:
        print(f"  Length: {len(aipipe_key)}")
        print(f"  Preview: {aipipe_key[:20]}...{aipipe_key[-10:]}")

def main():
    """Run comprehensive API investigation"""
    print("🕵️ COMPREHENSIVE API INVESTIGATION")
    print("=" * 60)
    
    # Check environment loading
    check_environment_loading()
    
    # Investigate OpenAI issues
    investigate_openai_key()
    
    # Investigate Aipipe structure
    investigate_aipipe_structure()
    
    # Test Aipipe authentication
    test_aipipe_authentication()
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
