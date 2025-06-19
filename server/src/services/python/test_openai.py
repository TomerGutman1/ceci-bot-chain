#!/usr/bin/env python3
"""Test OpenAI API Key"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"Key starts with: {api_key[:10]}..." if api_key else "No key found")
print(f"Key ends with: ...{api_key[-4:]}" if api_key else "")

# Test the key
try:
    client = openai.OpenAI(api_key=api_key)
    
    # Try a simple completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    
    print("\n✓ API Key is valid!")
    print(f"Response: {response.choices[0].message.content}")
    
except openai.RateLimitError as e:
    print(f"\n✗ Rate limit error: {e}")
    print("This usually means:")
    print("1. Your API key has exceeded its quota")
    print("2. You need to add billing/credits to your OpenAI account")
    
except openai.AuthenticationError as e:
    print(f"\n✗ Authentication error: {e}")
    print("The API key is invalid or expired")
    
except Exception as e:
    print(f"\n✗ Other error: {type(e).__name__}: {e}")
