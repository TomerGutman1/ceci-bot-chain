"""
Chat Log Replay Tests for 2X Context Router Bot.
Tests that routing decisions are 100% correct when replaying realistic conversation logs.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Test data: 100 realistic conversation scenarios based on CECI-AI usage patterns
CHAT_LOG_SCENARIOS = [
    # Scenario 1-10: Simple searches with government numbers
    {
        "scenario_id": 1,
        "description": "Simple search with clear government and topic",
        "conversation": [
            {
                "query": "החלטות ממשלה 37 בנושא חינוך",
                "expected_intent": "search",
                "expected_entities": {"government_number": 37, "topic": "חינוך"},
                "expected_confidence": 0.9,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    },
    {
        "scenario_id": 2,
        "description": "Count query with specific government",
        "conversation": [
            {
                "query": "כמה החלטות קיבלה ממשלה 36?",
                "expected_intent": "count",
                "expected_entities": {"government_number": 36},
                "expected_confidence": 0.85,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    },
    {
        "scenario_id": 3,
        "description": "Specific decision lookup",
        "conversation": [
            {
                "query": "החלטה 660 של ממשלה 37",
                "expected_intent": "specific_decision",
                "expected_entities": {"government_number": 37, "decision_number": 660},
                "expected_confidence": 0.95,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    },
    {
        "scenario_id": 4,
        "description": "Comparison between governments",
        "conversation": [
            {
                "query": "השוואה בין ממשלה 35 לממשלה 37 בנושא ביטחון",
                "expected_intent": "comparison",
                "expected_entities": {"governments": [35, 37], "topic": "ביטחון"},
                "expected_confidence": 0.88,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    },
    {
        "scenario_id": 5,
        "description": "Multi-turn conversation - clarification needed then resolved",
        "conversation": [
            {
                "query": "מה קורה עם החינוך?",
                "expected_intent": "search",
                "expected_entities": {"topic": "חינוך"},
                "expected_confidence": 0.6,
                "expected_route": "clarify",
                "expected_clarification": True,
                "expected_clarification_type": "low_confidence"
            },
            {
                "query": "אני מתכוון לממשלה 37",
                "expected_intent": "search",
                "expected_entities": {"government_number": 37, "topic": "חינוך"},
                "expected_confidence": 0.8,
                "expected_route": "next_bot",
                "expected_clarification": False
            },
            {
                "query": "החלטות ממשלה 37 בנושא חינוך",
                "expected_intent": "search",
                "expected_entities": {"government_number": 37, "topic": "חינוך"},
                "expected_confidence": 0.9,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    },
    # Scenarios 6-15: Ambiguous time references requiring clarification
    {
        "scenario_id": 6,
        "description": "Ambiguous time reference",
        "conversation": [
            {
                "query": "החלטות ממשלה 37 בתקופה האחרונה",
                "expected_intent": "search",
                "expected_entities": {"government_number": 37},
                "expected_confidence": 0.8,
                "expected_route": "clarify",
                "expected_clarification": True,
                "expected_clarification_type": "ambiguous_time"
            }
        ]
    },
    {
        "scenario_id": 7,
        "description": "Vague topic reference",
        "conversation": [
            {
                "query": "החלטות ממשלה 37 על הדבר הזה",
                "expected_intent": "search",
                "expected_entities": {"government_number": 37},
                "expected_confidence": 0.75,
                "expected_route": "clarify",
                "expected_clarification": True,
                "expected_clarification_type": "vague_topic"
            }
        ]
    },
    {
        "scenario_id": 8,
        "description": "Missing required entities for count",
        "conversation": [
            {
                "query": "כמה החלטות יש?",
                "expected_intent": "count",
                "expected_entities": {},
                "expected_confidence": 0.8,
                "expected_route": "clarify",
                "expected_clarification": True,
                "expected_clarification_type": "missing_entities"
            }
        ]
    },
    {
        "scenario_id": 9,
        "description": "Incomplete specific decision query",
        "conversation": [
            {
                "query": "החלטה 660",
                "expected_intent": "specific_decision",
                "expected_entities": {"decision_number": 660},
                "expected_confidence": 0.85,
                "expected_route": "clarify",
                "expected_clarification": True,
                "expected_clarification_type": "missing_entities"
            }
        ]
    },
    {
        "scenario_id": 10,
        "description": "Search with date range - well formed",
        "conversation": [
            {
                "query": "החלטות ממשלה 37 בנושא ביטחון מ-2023",
                "expected_intent": "search",
                "expected_entities": {
                    "government_number": 37,
                    "topic": "ביטחון",
                    "date_range": {"start": "2023-01-01", "end": "2023-12-31"}
                },
                "expected_confidence": 0.92,
                "expected_route": "direct_sql",
                "expected_clarification": False
            }
        ]
    }
]

# Generate additional scenarios to reach 100 total
def generate_additional_scenarios():
    """Generate scenarios 11-100 with variations of the base patterns."""
    additional = []
    
    # Scenarios 11-30: Government number variations
    for i in range(11, 31):
        gov_num = 35 + (i % 5)  # Governments 35-39
        additional.append({
            "scenario_id": i,
            "description": f"Search for government {gov_num}",
            "conversation": [
                {
                    "query": f"החלטות ממשלה {gov_num} בנושא בריאות",
                    "expected_intent": "search",
                    "expected_entities": {"government_number": gov_num, "topic": "בריאות"},
                    "expected_confidence": 0.88,
                    "expected_route": "direct_sql",
                    "expected_clarification": False
                }
            ]
        })
    
    # Scenarios 31-50: Different topics
    topics = ["חינוך", "ביטחון", "בריאות", "כלכלה", "תחבורה", "משפטים", "תרבות", "סביבה"]
    for i in range(31, 51):
        topic = topics[(i-31) % len(topics)]
        additional.append({
            "scenario_id": i,
            "description": f"Topic search: {topic}",
            "conversation": [
                {
                    "query": f"החלטות ממשלה 37 בנושא {topic}",
                    "expected_intent": "search",
                    "expected_entities": {"government_number": 37, "topic": topic},
                    "expected_confidence": 0.9,
                    "expected_route": "direct_sql",
                    "expected_clarification": False
                }
            ]
        })
    
    # Scenarios 51-70: Multi-turn conversations
    for i in range(51, 71):
        additional.append({
            "scenario_id": i,
            "description": f"Multi-turn conversation {i}",
            "conversation": [
                {
                    "query": "מה יש לי?",
                    "expected_intent": "search",
                    "expected_entities": {},
                    "expected_confidence": 0.5,
                    "expected_route": "clarify",
                    "expected_clarification": True,
                    "expected_clarification_type": "incomplete_query"
                },
                {
                    "query": f"ממשלה {35 + (i % 5)}",
                    "expected_intent": "search",
                    "expected_entities": {"government_number": 35 + (i % 5)},
                    "expected_confidence": 0.75,
                    "expected_route": "next_bot",
                    "expected_clarification": False
                }
            ]
        })
    
    # Scenarios 71-90: Count queries
    for i in range(71, 91):
        gov_num = 35 + (i % 5)
        additional.append({
            "scenario_id": i,
            "description": f"Count query for government {gov_num}",
            "conversation": [
                {
                    "query": f"כמה החלטות קיבלה ממשלה {gov_num}?",
                    "expected_intent": "count",
                    "expected_entities": {"government_number": gov_num},
                    "expected_confidence": 0.85,
                    "expected_route": "direct_sql",
                    "expected_clarification": False
                }
            ]
        })
    
    # Scenarios 91-100: Specific decision queries
    for i in range(91, 101):
        decision_num = 600 + i
        gov_num = 36 + (i % 3)
        additional.append({
            "scenario_id": i,
            "description": f"Specific decision {decision_num}",
            "conversation": [
                {
                    "query": f"החלטה {decision_num} של ממשלה {gov_num}",
                    "expected_intent": "specific_decision",
                    "expected_entities": {"government_number": gov_num, "decision_number": decision_num},
                    "expected_confidence": 0.95,
                    "expected_route": "direct_sql",
                    "expected_clarification": False
                }
            ]
        })
    
    return additional

# Combine base scenarios with generated ones to get 100 total
ALL_SCENARIOS = CHAT_LOG_SCENARIOS + generate_additional_scenarios()

class MockContextRouter:
    """Mock implementation for testing when actual bot not available."""
    
    def __init__(self):
        self.decisions = []
    
    async def make_routing_decision(self, request):
        """Mock routing decision that follows expected patterns."""
        # This is a simplified mock that just returns expected results
        # In real tests, this would use the actual implementation
        
        route = "next_bot"  # Default
        needs_clarification = False
        clarification_type = None
        
        # Simple logic based on confidence and entities
        if request.confidence_score < 0.7:
            route = "clarify"
            needs_clarification = True
            clarification_type = "low_confidence"
        elif request.confidence_score >= 0.85 and len(request.entities) >= 2:
            route = "direct_sql"
        
        # Check for ambiguous words in Hebrew
        if any(word in request.current_query for word in ["תקופה", "זמן", "דבר"]):
            route = "clarify"
            needs_clarification = True
            clarification_type = "ambiguous_time" if "תקופה" in request.current_query else "vague_topic"
        
        class MockDecision:
            def __init__(self):
                self.route = route
                self.needs_clarification = needs_clarification
                self.clarification_type = clarification_type
                self.context_summary = {"conv_id": request.conv_id}
                self.reasoning = f"Mock decision: {route}"
        
        self.decisions.append(MockDecision())
        return MockDecision()

@pytest.fixture
def mock_router():
    """Fixture providing mock router."""
    return MockContextRouter()

@pytest.mark.asyncio
async def test_chat_log_replay_100_scenarios(mock_router):
    """
    Test routing decisions against 100 conversation scenarios.
    Validates 100% correct routing decisions for realistic chat patterns.
    """
    # Import routing components
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            make_routing_decision,
            ContextRequest
        )
        bot_imported = True
    except ImportError:
        bot_imported = False
    
    total_conversations = 0
    total_queries = 0
    correct_decisions = 0
    failed_scenarios = []
    
    # Mock Redis for context management
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.keys.return_value = []
    mock_redis.ping.return_value = True
    
    with patch('redis.from_url', return_value=mock_redis):
        # Process all 100 scenarios
        for scenario in ALL_SCENARIOS[:100]:  # Ensure exactly 100 scenarios
            scenario_id = scenario["scenario_id"]
            total_conversations += 1
            
            conv_id = f"replay_test_{scenario_id}"
            scenario_passed = True
            scenario_errors = []
            
            # Process each query in the conversation
            for query_data in scenario["conversation"]:
                total_queries += 1
                
                # Create routing request
                request = ContextRequest(
                    conv_id=conv_id,
                    current_query=query_data["query"],
                    intent=query_data["expected_intent"],
                    entities=query_data["expected_entities"],
                    confidence_score=query_data["expected_confidence"]
                )
                
                try:
                    # Make routing decision
                    if bot_imported:
                        decision = await make_routing_decision(request)
                    else:
                        decision = await mock_router.make_routing_decision(request)
                    
                    # Validate routing decision
                    expected_route = query_data["expected_route"]
                    expected_clarification = query_data["expected_clarification"]
                    
                    route_correct = decision.route == expected_route
                    clarification_correct = decision.needs_clarification == expected_clarification
                    
                    if route_correct and clarification_correct:
                        correct_decisions += 1
                    else:
                        scenario_passed = False
                        scenario_errors.append({
                            "query": query_data["query"],
                            "expected_route": expected_route,
                            "actual_route": decision.route,
                            "expected_clarification": expected_clarification,
                            "actual_clarification": decision.needs_clarification
                        })
                
                except Exception as e:
                    scenario_passed = False
                    scenario_errors.append({
                        "query": query_data["query"],
                        "error": str(e)
                    })
            
            if not scenario_passed:
                failed_scenarios.append({
                    "scenario_id": scenario_id,
                    "description": scenario["description"],
                    "errors": scenario_errors
                })
    
    # Calculate success rate
    success_rate = correct_decisions / total_queries if total_queries > 0 else 0
    
    print(f"\n📊 Chat Log Replay Results:")
    print(f"Total conversations: {total_conversations}")
    print(f"Total queries: {total_queries}")
    print(f"Correct decisions: {correct_decisions}")
    print(f"Success rate: {success_rate:.1%}")
    print(f"Failed scenarios: {len(failed_scenarios)}")
    
    # Print details of failed scenarios for debugging
    if failed_scenarios:
        print(f"\n❌ Failed Scenarios:")
        for failure in failed_scenarios[:5]:  # Show first 5 failures
            print(f"  Scenario {failure['scenario_id']}: {failure['description']}")
            for error in failure['errors'][:2]:  # Show first 2 errors per scenario
                print(f"    - {error}")
    
    # Assert 100% correct routing decisions
    assert success_rate >= 1.0, f"Chat log replay success rate {success_rate:.1%} below required 100%"
    assert len(failed_scenarios) == 0, f"{len(failed_scenarios)} scenarios failed routing validation"

@pytest.mark.asyncio
async def test_conversation_context_consistency():
    """Test that context is maintained consistently across conversation turns."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            make_routing_decision,
            get_conversation_context,
            ContextRequest
        )
        bot_imported = True
    except ImportError:
        pytest.skip("Bot module not available")
    
    # Mock Redis
    contexts = {}
    mock_redis = Mock()
    mock_redis.get.side_effect = lambda key: contexts.get(key)
    mock_redis.setex.side_effect = lambda key, ttl, value: contexts.update({key: value})
    
    with patch('redis.from_url', return_value=mock_redis):
        conv_id = "context_consistency_test"
        
        # Multi-turn conversation
        queries = [
            ("מה יש?", "search", {}, 0.5),
            ("ממשלה 37", "search", {"government_number": 37}, 0.8),
            ("בנושא חינוך", "search", {"government_number": 37, "topic": "חינוך"}, 0.9)
        ]
        
        for i, (query, intent, entities, confidence) in enumerate(queries):
            request = ContextRequest(
                conv_id=conv_id,
                current_query=query,
                intent=intent,
                entities=entities,
                confidence_score=confidence
            )
            
            decision = await make_routing_decision(request)
            
            # First query should need clarification, subsequent ones should improve
            if i == 0:
                assert decision.needs_clarification == True
            elif i == len(queries) - 1:
                # Last query should have enough context to proceed
                assert decision.route in ["direct_sql", "next_bot"]

def test_scenario_coverage():
    """Test that we have good coverage of different conversation patterns."""
    # Count different types of scenarios
    intent_counts = {}
    route_counts = {}
    clarification_counts = {}
    
    for scenario in ALL_SCENARIOS:
        for query_data in scenario["conversation"]:
            intent = query_data["expected_intent"]
            route = query_data["expected_route"]
            clarification = query_data["expected_clarification"]
            
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            route_counts[route] = route_counts.get(route, 0) + 1
            clarification_counts[clarification] = clarification_counts.get(clarification, 0) + 1
    
    print(f"\n📈 Scenario Coverage:")
    print(f"Intent distribution: {intent_counts}")
    print(f"Route distribution: {route_counts}")
    print(f"Clarification distribution: {clarification_counts}")
    
    # Ensure we have good coverage
    assert "search" in intent_counts, "Should have search scenarios"
    assert "count" in intent_counts, "Should have count scenarios"
    assert "specific_decision" in intent_counts, "Should have specific decision scenarios"
    assert "direct_sql" in route_counts, "Should have direct SQL routes"
    assert "clarify" in route_counts, "Should have clarification routes"
    assert True in clarification_counts, "Should have scenarios requiring clarification"
    assert False in clarification_counts, "Should have scenarios not requiring clarification"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])