#!/usr/bin/env python3
"""
Test script for Decision Guide Bot improvements:
1. Document size limits and warnings
2. Seed parameter for consistency
3. Analysis caching
"""

import requests
import json
import time
import hashlib

# Bot endpoint
BASE_URL = "http://localhost:8018"

# Test documents
SHORT_DOC = """
טיוטת החלטת ממשלה בנושא חינוך
הממשלה מחליטה להקים צוות לבחינת רפורמה בחינוך.
"""

MEDIUM_DOC = """
טיוטת החלטת ממשלה בנושא חינוך

הממשלה מחליטה:
1. להקים צוות בינמשרדי לבחינת רפורמה במערכת החינוך
2. הצוות יגיש המלצותיו תוך 90 ימים
3. משרד החינוך יקצה תקציב של 10 מיליון ש"ח ליישום ההמלצות
4. יוקם מנגנון מעקב ובקרה על יישום ההחלטה
""" * 100  # ~8,000 chars

LARGE_DOC = MEDIUM_DOC * 10  # ~80,000 chars (warning threshold)
HUGE_DOC = MEDIUM_DOC * 20   # ~160,000 chars (exceeds max)

def test_document_size_limits():
    """Test document size warnings and limits"""
    print("\n=== Testing Document Size Limits ===")
    
    # Test 1: Small document (should work fine)
    print("\n1. Testing small document...")
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": SHORT_DOC,
            "documentInfo": {"type": "text", "originalName": "small.txt", "size": len(SHORT_DOC)},
            "requestId": "test-small"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Has size warning: {'שים לב: המסמך ארוך' in str(result.get('recommendations', []))}")
    
    # Test 2: Large document (should show warning)
    print("\n2. Testing large document (warning expected)...")
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": LARGE_DOC,
            "documentInfo": {"type": "text", "originalName": "large.txt", "size": len(LARGE_DOC)},
            "requestId": "test-large"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    recommendations = result.get('recommendations', [])
    has_warning = any('שים לב: המסמך ארוך' in rec for rec in recommendations)
    print(f"Has size warning: {has_warning}")
    if has_warning:
        print(f"Warning message: {[r for r in recommendations if 'שים לב' in r][0]}")
    
    # Test 3: Huge document (should be rejected)
    print("\n3. Testing huge document (rejection expected)...")
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": HUGE_DOC,
            "documentInfo": {"type": "text", "originalName": "huge.txt", "size": len(HUGE_DOC)},
            "requestId": "test-huge"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    retry_status = result.get('retry_status', '')
    print(f"Retry status: {retry_status}")
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"Message: {recommendations[0]}")

def test_consistency_with_caching():
    """Test that same document gets consistent results"""
    print("\n=== Testing Consistency with Caching ===")
    
    # Clear cache first
    print("\nClearing cache...")
    clear_response = requests.post(f"{BASE_URL}/clear-cache")
    print(f"Cache cleared: {clear_response.json()}")
    
    # Create a test document
    test_doc = """
    טיוטת החלטת ממשלה בנושא בריאות
    
    הממשלה מחליטה:
    1. להקים צוות לבחינת הרחבת סל הבריאות
    2. הצוות יכלול נציגים ממשרד הבריאות, משרד האוצר וקופות החולים
    3. הצוות יגיש המלצותיו תוך 120 ימים
    4. תוקצה תקציב של 50 מיליון ש"ח לביצוע פיילוט
    5. יוקם מנגנון מעקב רבעוני על התקדמות היישום
    """
    
    # Calculate hash
    doc_hash = hashlib.md5(test_doc.encode()).hexdigest()
    print(f"\nDocument hash: {doc_hash}")
    
    # Run analysis 3 times
    scores = []
    for i in range(3):
        print(f"\nRun {i+1}...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={
                "text": test_doc,
                "documentInfo": {"type": "text", "originalName": "test.txt", "size": len(test_doc)},
                "requestId": f"consistency-test-{i}"
            }
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        
        # Extract scores
        criteria_scores = result.get('criteria_scores', [])
        total_score = sum(cs['score'] for cs in criteria_scores)
        scores.append(total_score)
        
        model_used = result.get('model_used', 'unknown')
        print(f"Model used: {model_used}")
        print(f"Response time: {elapsed:.2f}s")
        print(f"Total score: {total_score}")
        print(f"Number of criteria: {len(criteria_scores)}")
    
    # Check consistency
    print(f"\n=== Consistency Results ===")
    print(f"All scores: {scores}")
    print(f"All scores identical: {len(set(scores)) == 1}")
    print(f"Score variance: {max(scores) - min(scores)}")

def test_cache_performance():
    """Test cache performance improvement"""
    print("\n=== Testing Cache Performance ===")
    
    # Clear cache
    requests.post(f"{BASE_URL}/clear-cache")
    
    test_doc = """
    טיוטת החלטת ממשלה בנושא תחבורה
    
    הממשלה מחליטה:
    1. להקים רשות לתחבורה ציבורית
    2. הרשות תפעל תחת משרד התחבורה
    3. תוקצה תקציב שנתי של 100 מיליון ש"ח
    4. הרשות תגיש דוח שנתי על פעילותה
    """
    
    # First request (no cache)
    print("\nFirst request (no cache)...")
    start = time.time()
    response1 = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": test_doc,
            "documentInfo": {"type": "text", "originalName": "cache-test.txt", "size": len(test_doc)},
            "requestId": "cache-test-1"
        }
    )
    time1 = time.time() - start
    print(f"Response time: {time1:.2f}s")
    print(f"Model used: {response1.json().get('model_used')}")
    
    # Second request (should use cache)
    print("\nSecond request (with cache)...")
    start = time.time()
    response2 = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": test_doc,
            "documentInfo": {"type": "text", "originalName": "cache-test.txt", "size": len(test_doc)},
            "requestId": "cache-test-2"
        }
    )
    time2 = time.time() - start
    print(f"Response time: {time2:.2f}s")
    print(f"Model used: {response2.json().get('model_used')}")
    
    print(f"\nPerformance improvement: {time1/time2:.1f}x faster with cache")

def main():
    """Run all tests"""
    print("Decision Guide Bot Improvements Test Suite")
    print("=========================================")
    
    # Check if service is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("ERROR: Decision Guide Bot is not running!")
            print("Please start the service first: docker compose up decision-guide-bot")
            return
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Decision Guide Bot!")
        print("Please start the service first: docker compose up decision-guide-bot")
        return
    
    # Run tests
    test_document_size_limits()
    test_consistency_with_caching()
    test_cache_performance()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()