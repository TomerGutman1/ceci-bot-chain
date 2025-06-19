#!/usr/bin/env python3
"""Test Supabase connection"""

import os
from dotenv import load_dotenv
import supabase
from supabase import create_client, Client
import inspect

# Load environment variables
load_dotenv()

print("Testing Supabase connection...")
print(f"Supabase module location: {supabase.__file__}")
print(f"Supabase version: {supabase.__version__ if hasattr(supabase, '__version__') else 'Unknown'}")

# Check create_client signature
print("\nChecking create_client signature:")
sig = inspect.signature(create_client)
print(f"Parameters: {list(sig.parameters.keys())}")

# Try to create client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"\nURL: {url[:30]}..." if url else "URL: None")
print(f"Key: {'*' * 10} (hidden)" if key else "Key: None")

try:
    # Try without any extra parameters
    client = create_client(url, key)
    print("\n✓ Successfully created client!")
    
    # Try to fetch some data
    response = client.table("israeli_government_decisions").select("*").limit(1).execute()
    print(f"✓ Successfully fetched data! Got {len(response.data)} record(s)")
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
    
    # Try to understand where the error comes from
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
