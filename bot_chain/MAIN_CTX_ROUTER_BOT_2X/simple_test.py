"""
Simple test for reference resolution without Redis dependency.
"""

import re
from typing import Dict, Any, List
from reference_config import reference_config, HEBREW_ENTITY_LABELS


def test_pattern_extraction():
    """Test basic pattern extraction."""
    print("🧪 Testing Pattern Extraction")
    
    patterns = reference_config.get_compiled_patterns()
    
    test_cases = [
        ("החלטה 276", "decision_number", "276"),
        ("ממשלה 36", "government_number", "36"), 
        ("של ממשלה 37", "government_number", "37"),
        ("בין 1/1/2023 - 31/1/2023", "date_range", "1/1/2023"),
    ]
    
    for text, expected_type, expected_value in test_cases:
        print(f"\nTesting: '{text}'")
        found = False
        
        for entity_type, entity_patterns in patterns.items():
            for pattern in entity_patterns:
                match = pattern.search(text)
                if match:
                    captured = match.group(1)
                    if entity_type == expected_type:
                        if captured == expected_value:
                            print(f"  ✅ {entity_type}: {captured}")
                            found = True
                        else:
                            print(f"  ⚠️  {entity_type}: {captured} (expected {expected_value})")
                    break
        
        if not found:
            print(f"  ❌ No match for {expected_type}")


def test_user_history_filtering():
    """Test filtering user messages from conversation history."""
    print("\n🧪 Testing User History Filtering")
    
    # Simulate conversation history with bot responses
    conversation_history = [
        {"speaker": "user", "clean_text": "החלטה 2989 של ממשלה 37"},
        {"speaker": "bot", "clean_text": "נמצאה החלטה 2989 של ממשלה 37. הנה תקציר..."},
        {"speaker": "user", "clean_text": "איך זה קשור לחינוך?"},
        {"speaker": "bot", "clean_text": "החלטה זו משפיעה על תקציב החינוך..."},
    ]
    
    # Filter only user messages
    user_turns = [turn for turn in conversation_history if turn.get('speaker') == 'user']
    
    print(f"Total turns: {len(conversation_history)}")
    print(f"User turns: {len(user_turns)}")
    
    for i, turn in enumerate(user_turns):
        print(f"  User turn {i+1}: '{turn['clean_text']}'")
    
    # Extract entities from user turns
    patterns = reference_config.get_compiled_patterns()
    
    for turn in user_turns:
        text = turn['clean_text']
        print(f"\nExtracting from: '{text}'")
        
        for entity_type, entity_patterns in patterns.items():
            for pattern in entity_patterns:
                match = pattern.search(text)
                if match:
                    print(f"  Found {entity_type}: {match.group(1)}")
                    break


def test_enrichment_logic():
    """Test query enrichment logic."""
    print("\n🧪 Testing Query Enrichment Logic")
    
    test_cases = [
        {
            "original": "תן לי את זה",
            "entities": {"decision_number": "2989", "government_number": "37"},
            "expected": "הבא לי את החלטה 2989 של ממשלה 37"
        },
        {
            "original": "החלטה 276", 
            "entities": {"decision_number": "276", "government_number": "36"},
            "expected": "החלטה 276 של ממשלה 36"
        },
        {
            "original": "ממשלה 34",
            "entities": {"decision_number": "88", "government_number": "34"}, 
            "expected": "הבא לי את החלטה 88 של ממשלה 34"
        }
    ]
    
    def enrich_query_simple(original_query: str, resolved_entities: Dict[str, Any]) -> str:
        """Simple enrichment logic."""
        enriched = original_query
        
        # Add decision number if resolved
        if 'decision_number' in resolved_entities:
            decision_num = resolved_entities['decision_number']
            if 'החלטה' not in enriched:
                enriched = f"הבא לי את החלטה {decision_num}"
            
        # Add government number if resolved
        if 'government_number' in resolved_entities:
            gov_num = resolved_entities['government_number']
            if 'ממשלה' not in enriched:
                enriched += f" של ממשלה {gov_num}"
        
        return enriched.strip()
    
    for case in test_cases:
        result = enrich_query_simple(case["original"], case["entities"])
        status = "✅" if result == case["expected"] else "❌"
        print(f"\n{status} Original: '{case['original']}'")
        print(f"    Entities: {case['entities']}")
        print(f"    Result: '{result}'")
        print(f"    Expected: '{case['expected']}'")


def test_clarification_generation():
    """Test Hebrew clarification generation."""
    print("\n🧪 Testing Clarification Generation")
    
    def generate_clarification_simple(known_parts: Dict[str, Any], missing_slots: List[str]) -> str:
        """Simple clarification generation."""
        # Build known parts summary
        known_labels = []
        for key, value in known_parts.items():
            if key in HEBREW_ENTITY_LABELS and value:
                if key == 'date_range' and isinstance(value, list):
                    known_labels.append(f"{HEBREW_ENTITY_LABELS[key]} {value[0]} עד {value[1]}")
                else:
                    known_labels.append(f"{HEBREW_ENTITY_LABELS[key]} {value}")
        
        # Build missing parts labels
        missing_labels = [HEBREW_ENTITY_LABELS.get(slot, slot) for slot in missing_slots]
        
        # Construct clarification prompt
        if known_labels:
            known_text = ", ".join(known_labels)
            missing_text = " או ".join(missing_labels)
            prompt = f"לא ברור לי אם התכוונת ל־{known_text} או ל־{missing_text}. תוכל בבקשה לציין למה אתה מתכוון ולהרחיב קצת?"
        else:
            missing_text = " ו".join(missing_labels)
            prompt = f"לא ברור לי מה {missing_text} שאתה מחפש. תוכל בבקשה לציין בבירור?"
        
        return prompt
    
    test_cases = [
        {
            "known": {"government_number": "36"},
            "missing": ["decision_number"],
            "expected_contains": ["מספר ממשלה 36", "מספר החלטה"]
        },
        {
            "known": {},
            "missing": ["decision_number", "government_number"],
            "expected_contains": ["מספר החלטה", "מספר ממשלה"]
        }
    ]
    
    for i, case in enumerate(test_cases):
        result = generate_clarification_simple(case["known"], case["missing"])
        print(f"\nTest case {i+1}:")
        print(f"  Known: {case['known']}")
        print(f"  Missing: {case['missing']}")
        print(f"  Generated: '{result}'")
        
        # Check if expected content is present
        all_found = all(expected in result for expected in case["expected_contains"])
        status = "✅" if all_found else "❌"
        print(f"  {status} Contains expected elements: {case['expected_contains']}")


if __name__ == "__main__":
    print("🚀 Running Simple Reference Resolution Tests")
    print("=" * 60)
    
    test_pattern_extraction()
    test_user_history_filtering()
    test_enrichment_logic()
    test_clarification_generation()
    
    print("\n" + "=" * 60)
    print("✅ All simple tests completed!")