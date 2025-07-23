#!/usr/bin/env python3
"""
Test script for Decision Guide Bot large document handling.
Tests the new chunking functionality for documents over 30K chars.
"""

import requests
import json
import time
import os

# Bot endpoint
BASE_URL = "http://localhost:8018"

# Test documents
def create_large_document(pages=72):
    """Create a large test document similar to real government decisions."""
    
    header = """טיוטת החלטת ממשלה
    
נושא: תוכנית לאומית מקיפה לשיפור מערכת הבריאות בישראל

רקע:
מערכת הבריאות בישראל מתמודדת עם אתגרים משמעותיים הכוללים עומס על בתי החולים, 
מחסור בכוח אדם רפואי, וצורך בחידוש תשתיות. על מנת להבטיח שירותי בריאות איכותיים 
ונגישים לכלל האוכלוסייה, נדרשת תוכנית לאומית מקיפה.

הממשלה מחליטה:

"""
    
    # Section template
    section_template = """
סעיף {num}: {title}

א. תיאור המטרה:
{goal}

ב. פעולות נדרשות:
1. {action1}
2. {action2}
3. {action3}

ג. גורם אחראי: {responsible}

ד. לוח זמנים: {timeline}

ה. תקציב נדרש: {budget}

ו. מדדי הצלחה:
- {metric1}
- {metric2}

"""
    
    sections_data = [
        {
            "title": "הרחבת כוח האדם הרפואי",
            "goal": "הגדלת מספר הרופאים והאחיות במערכת הבריאות ב-30% תוך 5 שנים",
            "action1": "פתיחת בתי ספר נוספים לרפואה וסיעוד",
            "action2": "יצירת מסלולי הכשרה מזורזים לעולים חדשים",
            "action3": "שיפור תנאי העסקה לצוותים רפואיים",
            "responsible": "משרד הבריאות בשיתוף משרד החינוך",
            "timeline": "תחילת יישום: רבעון ראשון 2025",
            "budget": "500 מיליון ש״ח לשנה",
            "metric1": "מספר בוגרי רפואה וסיעוד בשנה",
            "metric2": "שיעור התמדה של צוותים רפואיים"
        },
        {
            "title": "שדרוג תשתיות בתי חולים",
            "goal": "חידוש ושדרוג תשתיות פיזיות ודיגיטליות בכל בתי החולים הממשלתיים",
            "action1": "סקר מקיף של מצב התשתיות הקיימות",
            "action2": "תכנון ויישום פרויקטי שיפוץ ובנייה",
            "action3": "הטמעת מערכות מידע מתקדמות",
            "responsible": "משרד הבריאות בשיתוף משרד האוצר",
            "timeline": "השלמה עד סוף 2027",
            "budget": "3 מיליארד ש״ח פרוס על 3 שנים",
            "metric1": "אחוז בתי החולים שעברו שדרוג",
            "metric2": "שיפור בזמני המתנה לטיפולים"
        },
        {
            "title": "פיתוח רפואה מונעת וקהילתית",
            "goal": "הקמת מרכזי בריאות קהילתיים חדשים והרחבת שירותי רפואה מונעת",
            "action1": "הקמת 50 מרכזי בריאות קהילתיים חדשים",
            "action2": "הרחבת תוכניות סקר ומניעה",
            "action3": "פיתוח תוכניות חינוך לבריאות",
            "responsible": "משרד הבריאות וקופות החולים",
            "timeline": "יישום הדרגתי על פני 4 שנים",
            "budget": "800 מיליון ש״ח",
            "metric1": "מספר מטופלים במרכזים הקהילתיים",
            "metric2": "שיעור גילוי מוקדם של מחלות"
        }
    ]
    
    # Build document
    content = header
    
    # Repeat sections to reach desired size
    section_num = 1
    chars_per_page = 2500
    target_chars = pages * chars_per_page
    
    while len(content) < target_chars:
        for section_data in sections_data:
            section = section_template.format(
                num=section_num,
                **section_data
            )
            content += section
            section_num += 1
            
            if len(content) >= target_chars:
                break
    
    # Add footer
    footer = """

סיכום:
תוכנית זו מהווה צעד משמעותי בחיזוק מערכת הבריאות בישראל. יישומה המלא יביא לשיפור 
משמעותי באיכות ובזמינות שירותי הבריאות לכלל אזרחי ישראל.

מנגנון מעקב ובקרה:
1. הקמת ועדת היגוי בראשות מנכ"ל משרד הבריאות
2. דיווח רבעוני לממשלה על התקדמות היישום
3. ביקורת חיצונית שנתית על ידי מבקר המדינה
4. פרסום דוחות התקדמות לציבור

החלטה זו תיכנס לתוקף מיידית.
"""
    
    content += footer
    
    return content

def test_large_document_analysis():
    """Test analysis of a 72-page document."""
    print("\n=== Testing Large Document Analysis (72 pages) ===")
    
    # Create large document
    large_doc = create_large_document(72)
    doc_size = len(large_doc)
    print(f"\nCreated test document:")
    print(f"- Size: {doc_size:,} characters")
    print(f"- Estimated pages: {doc_size // 2500}")
    print(f"- Expected chunks: {(doc_size // 30000) + 1}")
    
    # Clear cache first
    print("\nClearing cache...")
    clear_response = requests.post(f"{BASE_URL}/clear-cache")
    print(f"Cache cleared: {clear_response.json()}")
    
    # Analyze document
    print("\nSending document for analysis...")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "text": large_doc,
            "documentInfo": {
                "type": "text",
                "originalName": "large_gov_decision.txt",
                "size": doc_size
            },
            "requestId": "test-large-doc-72pages"
        },
        timeout=300  # 5 minutes timeout for large documents
    )
    
    elapsed = time.time() - start_time
    
    print(f"\nResponse received in {elapsed:.1f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        # Check basic response structure
        print("\n=== Analysis Results ===")
        print(f"Model used: {result.get('model_used', 'unknown')}")
        print(f"Misuse detected: {result.get('misuse_detected', False)}")
        print(f"Retry status: {result.get('retry_status', 'N/A')}")
        print(f"Progress status: {result.get('progress_status', 'N/A')}")
        
        # Check chunk info
        chunk_info = result.get('chunk_info', {})
        if chunk_info:
            print(f"\n=== Chunk Processing Info ===")
            print(f"Total chunks: {chunk_info.get('total_chunks', 'N/A')}")
            print(f"Successful chunks: {chunk_info.get('successful_chunks', 'N/A')}")
            print(f"Document length: {chunk_info.get('total_length', 'N/A'):,}")
        
        # Check criteria scores
        criteria_scores = result.get('criteria_scores', [])
        print(f"\n=== Criteria Analysis ===")
        print(f"Number of criteria analyzed: {len(criteria_scores)}")
        
        if criteria_scores:
            print("\nSample criteria scores:")
            for i, score in enumerate(criteria_scores[:5]):  # Show first 5
                print(f"- {score['criterion']}: {score['score']}/5")
            
            # Calculate average score
            total_score = sum(cs['score'] for cs in criteria_scores)
            avg_score = total_score / len(criteria_scores) if criteria_scores else 0
            print(f"\nAverage score: {avg_score:.2f}/5")
        
        # Check recommendations
        recommendations = result.get('recommendations', [])
        print(f"\n=== Recommendations ===")
        print(f"Number of recommendations: {len(recommendations)}")
        if recommendations:
            print("\nFirst recommendation:")
            print(f"- {recommendations[0]}")
        
        # Save full response for debugging
        with open('large_doc_test_response.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\nFull response saved to: large_doc_test_response.json")
        
    else:
        print("\n=== Error Response ===")
        print(response.text)

def test_chunking_consistency():
    """Test that chunked analysis produces consistent results."""
    print("\n=== Testing Chunking Consistency ===")
    
    # Create a medium-sized document that will be chunked
    medium_doc = create_large_document(20)  # ~50K chars
    doc_size = len(medium_doc)
    print(f"\nCreated test document: {doc_size:,} characters")
    
    # Run analysis twice
    scores = []
    for i in range(2):
        print(f"\nRun {i+1}...")
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={
                "text": medium_doc,
                "documentInfo": {
                    "type": "text",
                    "originalName": "consistency_test.txt",
                    "size": doc_size
                },
                "requestId": f"consistency-test-{i}"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            criteria_scores = result.get('criteria_scores', [])
            total_score = sum(cs['score'] for cs in criteria_scores)
            scores.append(total_score)
            print(f"Total score: {total_score}")
    
    # Check consistency
    if len(scores) == 2:
        print(f"\n=== Consistency Results ===")
        print(f"Run 1 score: {scores[0]}")
        print(f"Run 2 score: {scores[1]}")
        print(f"Difference: {abs(scores[0] - scores[1])}")
        print(f"Consistent: {'Yes' if scores[0] == scores[1] else 'No'}")

def main():
    """Run all tests."""
    print("Decision Guide Bot - Large Document Handling Test")
    print("==============================================")
    
    # Check if service is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("ERROR: Decision Guide Bot is not running!")
            print("Please start the service first: docker compose up decision-guide-bot")
            return
        print(f"✓ Service is healthy: {health.json()}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Decision Guide Bot!")
        print("Please start the service first: docker compose up decision-guide-bot")
        return
    
    # Run tests
    test_large_document_analysis()
    test_chunking_consistency()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()