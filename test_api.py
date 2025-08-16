#!/usr/bin/env python3
"""
Simple test script for the Data Analyst Agent API
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_wikipedia_questions():
    """Test Wikipedia scraping questions"""
    try:
        # Read the sample questions
        with open('sample_questions/wikipedia_example.txt', 'r') as f:
            questions_content = f.read()
        
        # Prepare the request
        files = {
            'questions.txt': ('questions.txt', questions_content, 'text/plain')
        }
        
        print("Testing Wikipedia questions...")
        response = requests.post('http://localhost:5000/api/', files=files, timeout=120)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response type: {type(result)}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Validate response structure
            if isinstance(result, list) and len(result) == 4:
                print("✓ Response has correct structure (4-element array)")
                
                # Check types
                if isinstance(result[0], int):
                    print("✓ First element is integer (count)")
                if isinstance(result[1], str):
                    print("✓ Second element is string (movie title)")
                if isinstance(result[2], (int, float)):
                    print("✓ Third element is numeric (correlation)")
                if isinstance(result[3], str) and result[3].startswith('data:image/'):
                    print("✓ Fourth element is base64 image")
                
                return True
            else:
                print("✗ Response structure incorrect")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Wikipedia test failed: {e}")
        return False

def test_simple_question():
    """Test a simple question"""
    try:
        questions_content = "What is 2 + 2?"
        
        files = {
            'questions.txt': ('questions.txt', questions_content, 'text/plain')
        }
        
        print("Testing simple question...")
        response = requests.post('http://localhost:5000/api/', files=files, timeout=30)
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Simple test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Data Analyst Agent API Tests ===\n")
    
    # Test health endpoint
    if not test_health_endpoint():
        print("Health check failed. Is the server running?")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test simple question
    test_simple_question()
    
    print("\n" + "="*50 + "\n")
    
    # Test Wikipedia questions
    test_wikipedia_questions()
    
    print("\n=== Tests completed ===")

if __name__ == '__main__':
    main()
