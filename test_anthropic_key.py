import os
import sys
import requests
import json

def test_anthropic_key(api_key):
    """Test if the provided Anthropic API key is valid by making a simple API call."""
    
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json"
    }
    
    # Using the messages API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Simple request payload
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, this is a test message to verify my API key is working."}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Print status code and response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Your Anthropic API key is working correctly.")
            print("\nResponse preview:")
            response_json = response.json()
            if "content" in response_json and len(response_json["content"]) > 0:
                print(response_json["content"][0]["text"])
            return True
        else:
            print("❌ Error: Your Anthropic API key may not be valid.")
            print("\nError details:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Check for API key in various possible environment variables
    possible_env_vars = [
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_KEY",
        "CLAUDE_API_KEY",
        "CLAUDE_KEY",
        "API_KEY"
    ]
    
    api_key = None
    for env_var in possible_env_vars:
        if os.environ.get(env_var):
            api_key = os.environ.get(env_var)
            print(f"Found API key in environment variable: {env_var}")
            break
    
    # If not in environment, check command line arguments
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]
        print("Using API key from command line argument")
    
    # Hardcoded key for testing (only for demonstration)
    if not api_key:
        # Try a hardcoded key for testing purposes
        api_key = "sk-ant-api03-7-JlrWGJXtPtRDULDOZm_qWQ-6IgGbQ9Jd0bYQ3EE5G9kFmnfNvlKRZQPuS8AZI-zJcwQ-zGkj5AAAF8HleAA"
        print("Using hardcoded API key for testing")
    
    if api_key:
        test_anthropic_key(api_key)
    else:
        print("No API key found. Please provide your Anthropic API key either:")
        print("1. As an environment variable: ANTHROPIC_API_KEY, ANTHROPIC_KEY, CLAUDE_API_KEY, CLAUDE_KEY, or API_KEY")
        print("2. As a command line argument: python test_anthropic_key.py YOUR_API_KEY")
