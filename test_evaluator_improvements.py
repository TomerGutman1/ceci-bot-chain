#!/usr/bin/env python3
"""Test script to verify evaluator bot improvements"""

import asyncio
import json
import aiohttp
from datetime import datetime

async def test_evaluator(decision_number: int, government_number: int = 37):
    """Test the evaluator bot with a specific decision"""
    
    evaluator_url = "http://localhost:8014/evaluate"
    
    payload = {
        "conv_id": f"test-{datetime.now().isoformat()}",
        "government_number": government_number,
        "decision_number": decision_number,
        "original_query": f"נתח את החלטה {decision_number}"
    }
    
    print(f"\n{'='*60}")
    print(f"Testing Evaluator Bot with Decision {decision_number}")
    print(f"{'='*60}\n")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(evaluator_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract key information
                    overall_score = result.get('overall_score', 0) * 100
                    relevance_level = result.get('relevance_level', 'unknown')
                    explanation = result.get('explanation', '')
                    criteria = result.get('content_analysis', {}).get('criteria_breakdown', [])
                    
                    print(f"✅ Success! Overall Score: {overall_score:.1f}%")
                    print(f"Relevance Level: {relevance_level}")
                    print(f"\nExplanation Preview:\n{explanation[:500]}...")
                    
                    # Check for duplicate citations
                    if criteria:
                        citations = [c.get('reference_from_document', '') for c in criteria]
                        unique_citations = set(citations)
                        
                        print(f"\n📋 Citation Analysis:")
                        print(f"Total citations: {len(citations)}")
                        print(f"Unique citations: {len(unique_citations)}")
                        
                        if len(unique_citations) == 1:
                            print("⚠️ WARNING: All citations are identical!")
                            print(f"Citation: {list(unique_citations)[0][:100]}...")
                        else:
                            print("✅ Citations are properly varied")
                            print("\nFirst 3 unique citations:")
                            for i, citation in enumerate(list(unique_citations)[:3]):
                                print(f"{i+1}. {citation[:80]}...")
                    
                    # Check summary quality
                    summary = result.get('content_analysis', {}).get('feasibility_analysis', '')
                    if summary:
                        print(f"\n📝 Summary Quality Check:")
                        print(f"Length: {len(summary)} characters")
                        if summary == "סיכום הניתוח" or len(summary) < 50:
                            print("⚠️ WARNING: Summary appears to be generic or too short")
                        else:
                            print("✅ Summary appears to have meaningful content")
                            print(f"Preview: {summary[:150]}...")
                    
                else:
                    print(f"❌ Error: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")

async def main():
    """Run tests on multiple decisions"""
    
    test_cases = [
        (550, 37),    # Original problematic decision
        (2989, 37),   # Simple decision test
        (1111, 37),   # Short content test  
        (2222, 37),   # Declarative decision test
    ]
    
    for decision_num, gov_num in test_cases:
        await test_evaluator(decision_num, gov_num)
        await asyncio.sleep(1)  # Small delay between tests

if __name__ == "__main__":
    print("🧪 Testing Evaluator Bot Improvements")
    print("Make sure the evaluator bot is running on port 8014")
    asyncio.run(main())