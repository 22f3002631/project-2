import os
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

openai_key = os.getenv('OPENAI_API_KEY')
aipipe_key = os.getenv('AIPIPE_API_KEY')

print('Environment Variable Check:')
print(f'OpenAI Key: {openai_key[:20] if openai_key else "None"}...{openai_key[-10:] if openai_key else "None"}')
print(f'Aipipe Key: {aipipe_key[:20] if aipipe_key else "None"}...{aipipe_key[-10:] if aipipe_key else "None"}')
print(f'OpenAI Key Length: {len(openai_key) if openai_key else 0}')

# Test OpenAI API with new key
if openai_key:
    import requests
    import json
    
    print('\nTesting OpenAI API with updated key...')
    
    headers = {
        'Authorization': f'Bearer {openai_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "user", "content": "What is 2+2? Answer briefly."}
        ],
        'max_tokens': 50,
        'temperature': 0.1
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f'✅ OpenAI API SUCCESS!')
            print(f'Response: {content}')
        else:
            print(f'❌ OpenAI API FAILED')
            print(f'Response: {response.text}')
            
    except Exception as e:
        print(f'❌ Request failed: {str(e)}')
