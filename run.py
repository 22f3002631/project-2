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
        print(json.dumps({"error": "Usage: python run.py <url>"}))
        sys.exit(1)

    url = sys.argv[1].rstrip('/')
    api_url = f"{url}/api/"

    # Look for questions.txt file in current directory and common locations
    possible_paths = [
        Path("questions.txt"),
        Path("./questions.txt"),
        Path("../questions.txt"),
        Path("/home/usr_22f3002542_ds_study_iitm_ac_/tds-05-2025-p2-evals/promptfoos/project-data-analyst-agent-sample-network/questions.txt"),
        Path("/home/usr_22f3002542_ds_study_iitm_ac_/tds-05-2025-p2-evals/promptfoos/project-data-analyst-agent-sample-sales/questions.txt"),
        Path("/home/usr_22f3002542_ds_study_iitm_ac_/tds-05-2025-p2-evals/promptfoos/project-data-analyst-agent-sample-weather/questions.txt"),
    ]

    questions_file = None
    for path in possible_paths:
        if path.exists():
            questions_file = path
            break

    if questions_file is None:
        # If no questions.txt found, try to get it from the URL directly
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(response.text)
                return
            else:
                print(json.dumps({"error": f"No questions.txt file found and URL returned {response.status_code}"}))
                sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"No questions.txt file found and URL request failed: {str(e)}"}))
            sys.exit(1)
    
    try:
        # Read the questions file
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_content = f.read()

        # Prepare the file upload
        files = {
            'questions.txt': ('questions.txt', questions_content, 'text/plain')
        }

        # Try API endpoint first
        response = requests.post(api_url, files=files, timeout=300)

        if response.status_code == 200:
            try:
                # Try to parse as JSON
                result = response.json()
                print(json.dumps(result))
                return
            except json.JSONDecodeError:
                # If not JSON, return the raw response
                print(response.text)
                return

        # If API endpoint fails, try root endpoint
        root_response = requests.post(url, files=files, timeout=300)

        if root_response.status_code == 200:
            try:
                result = root_response.json()
                print(json.dumps(result))
                return
            except json.JSONDecodeError:
                print(root_response.text)
                return

        # If both fail, return error
        print(json.dumps({
            "error": f"API: HTTP {response.status_code}, Root: HTTP {root_response.status_code}"
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
