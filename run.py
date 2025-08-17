#!/usr/bin/env python3
"""
Test runner script for the Data Analyst Agent
This script is called by the evaluation system to test the deployed application.
"""

import sys
import requests
import json
import os
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py <url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    api_url = f"{url}/api/"
    
    # Look for questions.txt file in current directory
    questions_file = Path("questions.txt")
    if not questions_file.exists():
        # Try to find it in common locations
        possible_paths = [
            Path("questions.txt"),
            Path("./questions.txt"),
            Path("../questions.txt"),
        ]
        
        for path in possible_paths:
            if path.exists():
                questions_file = path
                break
        else:
            print(json.dumps({"error": "questions.txt file not found"}))
            sys.exit(1)
    
    try:
        # Read the questions file
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_content = f.read()
        
        # Prepare the file upload
        files = {
            'questions.txt': ('questions.txt', questions_content, 'text/plain')
        }
        
        # Make the API request
        response = requests.post(api_url, files=files, timeout=300)
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                result = response.json()
                print(json.dumps(result))
            except json.JSONDecodeError:
                # If not JSON, return the raw response
                print(response.text)
        else:
            print(json.dumps({
                "error": f"HTTP {response.status_code}: {response.text}"
            }))
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Request failed: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
