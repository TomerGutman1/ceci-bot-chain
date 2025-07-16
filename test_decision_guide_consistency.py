#!/usr/bin/env python3
import requests
import json
import time
import hashlib

# Test document - a simple government decision draft
test_document = """
החלטת ממשלה מס' 1234 בנושא שיפור החינוך הטכנולוגי

הממשלה מחליטה:

1. להקים צוות בין-משרדי בראשות מנכ"ל משרד החינוך לקידום החינוך הטכנולוגי בישראל.

2. להקצות סך של 50 מיליון ש"ח מתקציב המדינה למימון התוכנית.

3. הצוות יגיש דו"ח ביניים לממשלה תוך 6 חודשים מיום קבלת ההחלטה.

4. משרד החינוך יפעל בשיתוף עם משרד הכלכלה והתעשייה ליישום התוכנית.

5. יוקם מנגנון מעקב ובקרה רבעוני לבחינת התקדמות התוכנית.
"""

def test_decision_guide(base_url, num_tests=5):
    """Test the Decision Guide Bot multiple times to check for consistency"""
    
    results = []
    
    for i in range(num_tests):
        print(f"\nTest {i+1}/{num_tests}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/decision-guide/analyze",
                json={
                    "text": test_document,
                    "documentInfo": {
                        "type": "text",
                        "originalName": "test_decision.txt",
                        "size": len(test_document)
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract scores and weighted score
                scores = {}
                for criteria in data.get('criteriaScores', []):
                    scores[criteria['criterion']] = criteria['score']
                
                weighted_score = data.get('weightedScore', 0)
                
                result = {
                    'test_num': i + 1,
                    'weighted_score': weighted_score,
                    'scores': scores,
                    'hash': hashlib.md5(json.dumps(scores, sort_keys=True).encode()).hexdigest()
                }
                
                results.append(result)
                
                print(f"  Weighted Score: {weighted_score}")
                print(f"  Score Hash: {result['hash']}")
                
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  Exception: {str(e)}")
        
        # Small delay between tests
        if i < num_tests - 1:
            time.sleep(2)
    
    # Analyze consistency
    print("\n" + "="*50)
    print("CONSISTENCY ANALYSIS")
    print("="*50)
    
    if results:
        # Check if all results have the same hash
        unique_hashes = set(r['hash'] for r in results)
        weighted_scores = [r['weighted_score'] for r in results]
        
        print(f"\nNumber of unique score patterns: {len(unique_hashes)}")
        print(f"Weighted scores: {weighted_scores}")
        print(f"Min weighted score: {min(weighted_scores)}")
        print(f"Max weighted score: {max(weighted_scores)}")
        print(f"Score variance: {max(weighted_scores) - min(weighted_scores)}")
        
        if len(unique_hashes) == 1:
            print("\n✅ PERFECT CONSISTENCY - All tests produced identical scores!")
        else:
            print("\n❌ INCONSISTENCY DETECTED - Scores varied between tests")
            
            # Show differences
            print("\nScore variations by criteria:")
            all_criteria = set()
            for r in results:
                all_criteria.update(r['scores'].keys())
            
            for criterion in sorted(all_criteria):
                scores_for_criterion = [r['scores'].get(criterion, 'N/A') for r in results]
                unique_scores = set(s for s in scores_for_criterion if s != 'N/A')
                if len(unique_scores) > 1:
                    print(f"  {criterion}: {scores_for_criterion}")

if __name__ == "__main__":
    # Test against production
    print("Testing Decision Guide Bot consistency on PRODUCTION...")
    test_decision_guide("https://ceci-ai.ceci.org.il", num_tests=5)