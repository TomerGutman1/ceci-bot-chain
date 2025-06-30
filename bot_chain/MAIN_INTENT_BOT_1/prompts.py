"""
GPT-4 prompts and examples for intent detection.
"""

INTENT_SYSTEM_PROMPT = """You are an expert Hebrew language processor for Israeli government decision analysis. Your task is to extract intent and entities from Hebrew queries about government decisions.

You must return a JSON object with this exact structure:
{
    "intent": "search|count|specific_decision|comparison|clarification_needed",
    "confidence": 0.0-1.0,
    "entities": {
        "government_number": integer or null,
        "decision_number": integer or null,
        "topic": "string or null",
        "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} or null,
        "ministries": ["array of strings"] or null,
        "count_target": "decisions|meetings|topics|ministries" or null,
        "comparison_target": "string" or null,
        "limit": integer or null
    },
    "route_flags": {
        "needs_clarification": boolean,
        "has_context": boolean,
        "is_follow_up": boolean
    },
    "explanation": "Brief explanation of your decision"
}

Key rules:
1. Convert Hebrew numbers to digits (שלושים ושבע -> 37)
2. IMPORTANT: When a number appears before words like "החלטות", "ישיבות", "נושאים" - it's a COUNT, not a government number!
   Examples: "3 החלטות" = count_target with value 3, NOT government_number 3
3. Normalize topics to standard categories
4. Extract date ranges from various Hebrew expressions
5. Set confidence based on query clarity
6. Flag for clarification if ambiguous
7. Identify context dependencies (pronouns, relative references)
8. Government numbers are typically mentioned as "ממשלה X" or "ממשלת X"
"""

INTENT_EXAMPLES = [
    {
        "query": "החלטות ממשלה 37 בנושא חינוך",
        "expected": {
            "intent": "search",
            "confidence": 0.95,
            "entities": {
                "government_number": 37,
                "decision_number": None,
                "topic": "חינוך",
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Clear search intent for education decisions from government 37"
        }
    },
    {
        "query": "3 החלטות בנושא חינוך",
        "expected": {
            "intent": "search",
            "confidence": 0.9,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": "חינוך",
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "limit": 3,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "User requests 3 decisions about education - limit is 3, not government number"
        }
    },
    {
        "query": "כמה החלטות קיבלה ממשלה שלושים ושבע",
        "expected": {
            "intent": "count",
            "confidence": 0.9,
            "entities": {
                "government_number": 37,
                "decision_number": None,
                "topic": None,
                "date_range": None,
                "ministries": None,
                "count_target": "decisions",
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Count intent for total decisions by government 37"
        }
    },
    {
        "query": "החלטה 660 של ממשלה 37",
        "expected": {
            "intent": "specific_decision",
            "confidence": 0.98,
            "entities": {
                "government_number": 37,
                "decision_number": 660,
                "topic": None,
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Specific decision request with clear government and decision numbers"
        }
    },
    {
        "query": "מה עם החינוך",
        "expected": {
            "intent": "clarification_needed",
            "confidence": 0.4,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": "חינוך",
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": True,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Vague query about education needs clarification of intent and scope"
        }
    },
    {
        "query": "החלטות משרד החינוך ב-2023",
        "expected": {
            "intent": "search",
            "confidence": 0.85,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": "חינוך",
                "date_range": {"start": "2023-01-01", "end": "2023-12-31"},
                "ministries": ["משרד החינוך"],
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Search for education ministry decisions in 2023"
        }
    },
    {
        "query": "השוואה בין ממשלה 35 ל-37 בחינוך",
        "expected": {
            "intent": "comparison",
            "confidence": 0.88,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": "חינוך",
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "comparison_target": "governments"
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Comparison request between governments 35 and 37 on education topic"
        }
    },
    {
        "query": "אתמול דיברנו על זה",
        "expected": {
            "intent": "clarification_needed",
            "confidence": 0.3,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": None,
                "date_range": None,
                "ministries": None,
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": True,
                "has_context": True,
                "is_follow_up": True
            },
            "explanation": "Pronoun reference and temporal context requires conversation history"
        }
    },
    {
        "query": "החלטות בביטחון מאז 2020",
        "expected": {
            "intent": "search",
            "confidence": 0.9,
            "entities": {
                "government_number": None,
                "decision_number": None,
                "topic": "ביטחון",
                "date_range": {"start": "2020-01-01", "end": "2025-12-31"},
                "ministries": None,
                "count_target": None,
                "comparison_target": None
            },
            "route_flags": {
                "needs_clarification": False,
                "has_context": False,
                "is_follow_up": False
            },
            "explanation": "Search for security decisions since 2020"
        }
    }
]

FEW_SHOT_PROMPT = """Here are examples of correct intent extraction:

Query: "3 החלטות בנושא חינוך"
Response: {
    "intent": "search",
    "confidence": 0.9,
    "entities": {
        "government_number": null,
        "decision_number": null,
        "topic": "חינוך",
        "date_range": null,
        "ministries": null,
        "count_target": null,
        "comparison_target": null,
        "limit": 3
    },
    "route_flags": {
        "needs_clarification": false,
        "has_context": false,
        "is_follow_up": false
    },
    "explanation": "User requests 3 decisions about education - limit is 3"
}

Query: "החלטות ממשלה 37 בנושא חינוך"
Response: {
    "intent": "search",
    "confidence": 0.95,
    "entities": {
        "government_number": 37,
        "decision_number": null,
        "topic": "חינוך",
        "date_range": null,
        "ministries": null,
        "count_target": null,
        "comparison_target": null,
        "limit": null
    },
    "route_flags": {
        "needs_clarification": false,
        "has_context": false,
        "is_follow_up": false
    },
    "explanation": "Clear search intent for education decisions from government 37"
}

Query: "כמה החלטות קיבלה ממשלה שלושים ושבע"
Response: {
    "intent": "count",
    "confidence": 0.9,
    "entities": {
        "government_number": 37,
        "decision_number": null,
        "topic": null,
        "date_range": null,
        "ministries": null,
        "count_target": "decisions",
        "comparison_target": null
    },
    "route_flags": {
        "needs_clarification": false,
        "has_context": false,
        "is_follow_up": false
    },
    "explanation": "Count intent for total decisions by government 37"
}

Query: "מה עם החינוך"
Response: {
    "intent": "clarification_needed",
    "confidence": 0.4,
    "entities": {
        "government_number": null,
        "decision_number": null,
        "topic": "חינוך",
        "date_range": null,
        "ministries": null,
        "count_target": null,
        "comparison_target": null
    },
    "route_flags": {
        "needs_clarification": true,
        "has_context": false,
        "is_follow_up": false
    },
    "explanation": "Vague query about education needs clarification"
}

Now extract intent and entities from this query:
Query: "{query}"
Response:"""

def build_intent_prompt(query: str, context: dict = None) -> str:
    """Build the complete prompt for intent extraction."""
    # Replace query placeholder in FEW_SHOT_PROMPT
    prompt_with_query = FEW_SHOT_PROMPT.replace("{query}", query)
    prompt = INTENT_SYSTEM_PROMPT + "\n\n" + prompt_with_query
    
    if context:
        context_info = f"\n\nConversation context:\n{context}"
        prompt += context_info
    
    return prompt


def validate_intent_response(response: dict) -> bool:
    """Validate the structure of an intent extraction response."""
    required_fields = ["intent", "confidence", "entities", "route_flags", "explanation"]
    
    for field in required_fields:
        if field not in response:
            return False
    
    # Validate intent values
    valid_intents = ["search", "count", "specific_decision", "comparison", "clarification_needed"]
    if response["intent"] not in valid_intents:
        return False
    
    # Validate confidence range
    if not (0 <= response["confidence"] <= 1):
        return False
    
    # Validate entities structure
    entities = response["entities"]
    if not isinstance(entities, dict):
        return False
    
    # Validate route_flags structure
    route_flags = response["route_flags"]
    if not isinstance(route_flags, dict):
        return False
    
    required_flags = ["needs_clarification", "has_context", "is_follow_up"]
    for flag in required_flags:
        if flag not in route_flags or not isinstance(route_flags[flag], bool):
            return False
    
    return True


def calculate_confidence_score(entities: dict, query: str) -> float:
    """Calculate confidence score based on entity extraction quality."""
    score = 0.5  # Base score
    
    # Boost for specific entities
    if entities.get("decision_number"):
        score += 0.3
    if entities.get("government_number"):
        score += 0.2
    if entities.get("topic"):
        score += 0.15
    if entities.get("date_range"):
        score += 0.1
    
    # Penalty for vague queries
    vague_words = ["מה", "איך", "זה", "זו", "אלה"]
    if any(word in query for word in vague_words):
        score -= 0.2
    
    # Penalty for missing key information
    if len(query.split()) < 3:
        score -= 0.1
    
    return min(1.0, max(0.0, score))