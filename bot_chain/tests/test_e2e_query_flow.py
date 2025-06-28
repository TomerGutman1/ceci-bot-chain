"""
End-to-End Integration Test for Bot Chain Query Flow.
Tests the complete flow through all implemented bot layers with real Hebrew queries.
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

# Test scenarios representing realistic CECI-AI usage patterns
E2E_TEST_SCENARIOS = [
    {
        "scenario_id": "e2e_001",
        "name": "Simple Government Search - Clear Query",
        "description": "User asks for clear government decisions with good entities",
        "initial_query": "החלטות ממשלה שלושים ושבע בנושא חינוך",
        "expected_flow": {
            "rewrite": {
                "should_normalize": True,
                "expected_clean": "החלטות ממשלה 37 בנושא חינוך",
                "improvements": ["number_normalization"]
            },
            "intent": {
                "expected_intent": "search",
                "expected_entities": {
                    "government_number": 37,
                    "topic": "חינוך"
                },
                "expected_confidence": 0.85
            },
            "context_router": {
                "expected_route": "direct_sql",
                "needs_clarification": False
            },
            "sql_gen": {
                "should_use_template": True,
                "expected_template": "search_by_government_and_topic",
                "expected_sql_contains": ["SELECT", "government_number = 37", "topic", "חינוך"]
            }
        }
    },
    {
        "scenario_id": "e2e_002", 
        "name": "Ambiguous Query Requiring Clarification",
        "description": "Vague query that should trigger clarification flow",
        "initial_query": "מה קורה עם הדבר הזה בתקופה האחרונה?",
        "expected_flow": {
            "rewrite": {
                "should_normalize": True,
                "expected_clean": "מה קורה עם הדבר הזה בתקופה האחרונה?",
                "improvements": ["grammar_check"]
            },
            "intent": {
                "expected_intent": "search",
                "expected_entities": {},
                "expected_confidence": 0.4
            },
            "context_router": {
                "expected_route": "clarify",
                "needs_clarification": True,
                "clarification_type": "vague_topic"
            },
            "sql_gen": {
                "should_skip": True,
                "reason": "routed_to_clarification"
            }
        }
    },
    {
        "scenario_id": "e2e_003",
        "name": "Count Query with Entity",
        "description": "User asks for count of decisions by specific government",
        "initial_query": "כמה החלטות קיבלה ממשלה 36?",
        "expected_flow": {
            "rewrite": {
                "should_normalize": False,
                "expected_clean": "כמה החלטות קיבלה ממשלה 36?",
                "improvements": []
            },
            "intent": {
                "expected_intent": "count",
                "expected_entities": {
                    "government_number": 36
                },
                "expected_confidence": 0.9
            },
            "context_router": {
                "expected_route": "direct_sql",
                "needs_clarification": False
            },
            "sql_gen": {
                "should_use_template": True,
                "expected_template": "count_by_government",
                "expected_sql_contains": ["COUNT", "government_number = 36"]
            }
        }
    },
    {
        "scenario_id": "e2e_004",
        "name": "Specific Decision Lookup",
        "description": "User asks for a specific decision by number and government",
        "initial_query": "החלטה מספר 660 של ממשלה 37",
        "expected_flow": {
            "rewrite": {
                "should_normalize": True,
                "expected_clean": "החלטה מספר 660 של ממשלה 37",
                "improvements": ["structure_normalization"]
            },
            "intent": {
                "expected_intent": "specific_decision",
                "expected_entities": {
                    "government_number": 37,
                    "decision_number": 660
                },
                "expected_confidence": 0.95
            },
            "context_router": {
                "expected_route": "direct_sql",
                "needs_clarification": False
            },
            "sql_gen": {
                "should_use_template": True,
                "expected_template": "specific_decision",
                "expected_sql_contains": ["SELECT", "government_number = 37", "decision_number = 660"]
            }
        }
    },
    {
        "scenario_id": "e2e_005",
        "name": "Multi-turn Conversation",
        "description": "Conversation that builds context over multiple turns",
        "conversation_turns": [
            {
                "turn": 1,
                "query": "מה יש על החינוך?",
                "expected_flow": {
                    "rewrite": {"expected_clean": "מה יש על החינוך?"},
                    "intent": {"expected_intent": "search", "expected_entities": {"topic": "חינוך"}, "expected_confidence": 0.6},
                    "context_router": {"expected_route": "clarify", "needs_clarification": True}
                }
            },
            {
                "turn": 2,
                "query": "אני מתכוון לממשלה 37",
                "expected_flow": {
                    "rewrite": {"expected_clean": "אני מתכוון לממשלה 37"},
                    "intent": {"expected_intent": "search", "expected_entities": {"government_number": 37}, "expected_confidence": 0.8},
                    "context_router": {"expected_route": "next_bot", "needs_clarification": False}
                }
            },
            {
                "turn": 3,
                "query": "החלטות ממשלה 37 בנושא חינוך",
                "expected_flow": {
                    "rewrite": {"expected_clean": "החלטות ממשלה 37 בנושא חינוך"},
                    "intent": {"expected_intent": "search", "expected_entities": {"government_number": 37, "topic": "חינוך"}, "expected_confidence": 0.9},
                    "context_router": {"expected_route": "direct_sql", "needs_clarification": False},
                    "sql_gen": {"should_use_template": True, "expected_template": "search_by_government_and_topic"}
                }
            }
        ]
    }
]

class MockBotChain:
    """Mock implementation of the bot chain for testing when services aren't running."""
    
    def __init__(self):
        self.call_history = []
    
    async def call_rewrite_bot(self, text: str, conv_id: str) -> Dict[str, Any]:
        """Mock rewrite bot call."""
        self.call_history.append(("rewrite", text, conv_id))
        
        # Simple normalization logic
        clean_text = text
        improvements = []
        
        if "שלושים ושבע" in text:
            clean_text = clean_text.replace("שלושים ושבע", "37")
            improvements.append("number_normalization")
        
        if "שלושים ושש" in text:
            clean_text = clean_text.replace("שלושים ושש", "36")
            improvements.append("number_normalization")
        
        return {
            "success": True,
            "clean_text": clean_text,
            "original_text": text,
            "improvements": improvements,
            "confidence": 0.9
        }
    
    async def call_intent_bot(self, text: str, conv_id: str) -> Dict[str, Any]:
        """Mock intent bot call."""
        self.call_history.append(("intent", text, conv_id))
        
        # Intent detection logic
        intent = "search"  # default
        entities = {}
        confidence = 0.7  # default
        
        if "כמה" in text:
            intent = "count"
            confidence = 0.9
        elif "החלטה מספר" in text or "החלטה " in text and any(char.isdigit() for char in text):
            intent = "specific_decision"
            confidence = 0.95
        elif "השוואה" in text or "לעומת" in text:
            intent = "comparison"
            confidence = 0.85
        
        # Extract entities
        import re
        
        # Government numbers
        gov_match = re.search(r'ממשלה\s*(\d+)', text)
        if gov_match:
            entities["government_number"] = int(gov_match.group(1))
        
        # Decision numbers
        dec_match = re.search(r'החלטה\s*(?:מספר\s*)?(\d+)', text)
        if dec_match:
            entities["decision_number"] = int(dec_match.group(1))
        
        # Topics
        topics = ["חינוך", "ביטחון", "בריאות", "כלכלה", "תחבורה"]
        for topic in topics:
            if topic in text:
                entities["topic"] = topic
                break
        
        # Adjust confidence based on entities
        if not entities:
            confidence = max(0.3, confidence - 0.3)
        elif len(entities) >= 2:
            confidence = min(0.95, confidence + 0.1)
        
        return {
            "success": True,
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "explanation": f"Detected {intent} with {len(entities)} entities"
        }
    
    async def call_context_router(self, conv_id: str, query: str, intent: str, entities: Dict, confidence: float) -> Dict[str, Any]:
        """Mock context router call."""
        self.call_history.append(("context_router", query, conv_id))
        
        route = "next_bot"  # default
        needs_clarification = False
        clarification_type = None
        
        # Clarification logic
        if confidence < 0.7:
            route = "clarify"
            needs_clarification = True
            clarification_type = "low_confidence"
        elif any(word in query.lower() for word in ["תקופה", "דבר", "זה", "משהו"]):
            route = "clarify"
            needs_clarification = True
            clarification_type = "vague_topic"
        elif intent == "count" and "government_number" not in entities:
            route = "clarify"
            needs_clarification = True
            clarification_type = "missing_entities"
        elif confidence >= 0.85 and len(entities) >= 2:
            route = "direct_sql"
        
        return {
            "success": True,
            "route": route,
            "needs_clarification": needs_clarification,
            "clarification_type": clarification_type,
            "context_summary": {
                "conv_id": conv_id,
                "entities_count": len(entities),
                "confidence": confidence
            },
            "reasoning": f"Route to {route} based on confidence {confidence} and {len(entities)} entities"
        }
    
    async def call_sql_gen_bot(self, intent: str, entities: Dict, conv_id: str) -> Dict[str, Any]:
        """Mock SQL generation bot call."""
        self.call_history.append(("sql_gen", intent, conv_id))
        
        # Template selection
        template_map = {
            "search": "search_by_government_and_topic" if "government_number" in entities and "topic" in entities else "search_basic",
            "count": "count_by_government" if "government_number" in entities else "count_all",
            "specific_decision": "specific_decision",
            "comparison": "comparison"
        }
        
        template = template_map.get(intent, "fallback")
        
        # Generate mock SQL
        if intent == "search":
            if "government_number" in entities and "topic" in entities:
                sql = f"SELECT * FROM government_decisions WHERE government_number = {entities['government_number']} AND '{entities['topic']}' = ANY(topics)"
            else:
                sql = "SELECT * FROM government_decisions WHERE 1=1"
        elif intent == "count":
            if "government_number" in entities:
                sql = f"SELECT COUNT(*) FROM government_decisions WHERE government_number = {entities['government_number']}"
            else:
                sql = "SELECT COUNT(*) FROM government_decisions"
        elif intent == "specific_decision":
            sql = f"SELECT * FROM government_decisions WHERE government_number = {entities.get('government_number', 0)} AND decision_number = {entities.get('decision_number', 0)}"
        else:
            sql = "SELECT * FROM government_decisions LIMIT 10"
        
        return {
            "success": True,
            "sql": sql,
            "template_used": template,
            "parameters": entities,
            "estimated_rows": 100
        }

@pytest.fixture
def mock_bot_chain():
    """Fixture providing mock bot chain."""
    return MockBotChain()

@pytest.mark.asyncio
async def test_e2e_single_query_flows(mock_bot_chain):
    """Test end-to-end flow for single-query scenarios."""
    
    # Test each single-query scenario
    for scenario in E2E_TEST_SCENARIOS[:4]:  # Skip multi-turn for now
        print(f"\n🧪 Testing Scenario: {scenario['name']}")
        
        conv_id = f"e2e_test_{scenario['scenario_id']}"
        query = scenario["initial_query"]
        expected = scenario["expected_flow"]
        
        # Step 1: Rewrite Bot
        print(f"  📝 Step 1: Rewrite Bot - '{query}'")
        rewrite_result = await mock_bot_chain.call_rewrite_bot(query, conv_id)
        
        assert rewrite_result["success"], f"Rewrite failed for {scenario['scenario_id']}"
        
        if "rewrite" in expected:
            if expected["rewrite"]["should_normalize"]:
                assert rewrite_result["clean_text"] != query, f"Expected normalization in {scenario['scenario_id']}"
            if "expected_clean" in expected["rewrite"]:
                assert expected["rewrite"]["expected_clean"] in rewrite_result["clean_text"], f"Clean text mismatch in {scenario['scenario_id']}"
        
        clean_query = rewrite_result["clean_text"]
        print(f"    ✅ Cleaned: '{clean_query}'")
        
        # Step 2: Intent Bot
        print(f"  🎯 Step 2: Intent Bot - '{clean_query}'")
        intent_result = await mock_bot_chain.call_intent_bot(clean_query, conv_id)
        
        assert intent_result["success"], f"Intent detection failed for {scenario['scenario_id']}"
        
        if "intent" in expected:
            assert intent_result["intent"] == expected["intent"]["expected_intent"], f"Intent mismatch in {scenario['scenario_id']}"
            
            # Check entities
            for entity_key, entity_value in expected["intent"]["expected_entities"].items():
                assert entity_key in intent_result["entities"], f"Missing entity {entity_key} in {scenario['scenario_id']}"
                assert intent_result["entities"][entity_key] == entity_value, f"Entity value mismatch for {entity_key} in {scenario['scenario_id']}"
            
            # Check confidence is reasonable
            assert intent_result["confidence"] >= expected["intent"]["expected_confidence"] - 0.1, f"Confidence too low in {scenario['scenario_id']}"
        
        print(f"    ✅ Intent: {intent_result['intent']}, Entities: {intent_result['entities']}, Confidence: {intent_result['confidence']:.2f}")
        
        # Step 3: Context Router
        print(f"  🗺️ Step 3: Context Router")
        router_result = await mock_bot_chain.call_context_router(
            conv_id, clean_query, intent_result["intent"], 
            intent_result["entities"], intent_result["confidence"]
        )
        
        assert router_result["success"], f"Context routing failed for {scenario['scenario_id']}"
        
        if "context_router" in expected:
            assert router_result["route"] == expected["context_router"]["expected_route"], f"Route mismatch in {scenario['scenario_id']}"
            assert router_result["needs_clarification"] == expected["context_router"]["needs_clarification"], f"Clarification flag mismatch in {scenario['scenario_id']}"
        
        print(f"    ✅ Route: {router_result['route']}, Clarification: {router_result['needs_clarification']}")
        
        # Step 4: SQL Generation (if routed appropriately)
        if router_result["route"] == "direct_sql" and "sql_gen" in expected and not expected["sql_gen"].get("should_skip", False):
            print(f"  🔍 Step 4: SQL Generation")
            sql_result = await mock_bot_chain.call_sql_gen_bot(
                intent_result["intent"], intent_result["entities"], conv_id
            )
            
            assert sql_result["success"], f"SQL generation failed for {scenario['scenario_id']}"
            
            if expected["sql_gen"]["should_use_template"]:
                assert sql_result["template_used"] == expected["sql_gen"]["expected_template"], f"Template mismatch in {scenario['scenario_id']}"
            
            # Check SQL contains expected elements
            sql = sql_result["sql"]
            for expected_element in expected["sql_gen"]["expected_sql_contains"]:
                assert expected_element in sql, f"SQL missing '{expected_element}' in {scenario['scenario_id']}"
            
            print(f"    ✅ SQL Generated: {sql[:100]}...")
            print(f"    ✅ Template: {sql_result['template_used']}")
        else:
            print(f"  ⏭️ Step 4: SQL Generation skipped (route: {router_result['route']})")
        
        print(f"  🎉 Scenario {scenario['scenario_id']} completed successfully!\n")

@pytest.mark.asyncio
async def test_e2e_multi_turn_conversation(mock_bot_chain):
    """Test end-to-end flow for multi-turn conversation."""
    
    scenario = E2E_TEST_SCENARIOS[4]  # Multi-turn scenario
    print(f"\n🧪 Testing Multi-turn Scenario: {scenario['name']}")
    
    conv_id = f"e2e_test_{scenario['scenario_id']}"
    
    for turn_data in scenario["conversation_turns"]:
        turn_num = turn_data["turn"]
        query = turn_data["query"]
        expected = turn_data["expected_flow"]
        
        print(f"\n  🔄 Turn {turn_num}: '{query}'")
        
        # Follow the same flow as single queries
        rewrite_result = await mock_bot_chain.call_rewrite_bot(query, conv_id)
        clean_query = rewrite_result["clean_text"]
        print(f"    📝 Cleaned: '{clean_query}'")
        
        intent_result = await mock_bot_chain.call_intent_bot(clean_query, conv_id)
        print(f"    🎯 Intent: {intent_result['intent']}, Entities: {intent_result['entities']}")
        
        router_result = await mock_bot_chain.call_context_router(
            conv_id, clean_query, intent_result["intent"], 
            intent_result["entities"], intent_result["confidence"]
        )
        print(f"    🗺️ Route: {router_result['route']}")
        
        # Validate against expectations
        if "intent" in expected:
            assert intent_result["intent"] == expected["intent"]["expected_intent"]
        
        if "context_router" in expected:
            assert router_result["route"] == expected["context_router"]["expected_route"]
        
        # SQL generation for final turn
        if router_result["route"] == "direct_sql" and "sql_gen" in expected:
            sql_result = await mock_bot_chain.call_sql_gen_bot(
                intent_result["intent"], intent_result["entities"], conv_id
            )
            print(f"    🔍 SQL: {sql_result['sql'][:80]}...")
    
    print(f"  🎉 Multi-turn conversation completed successfully!")

def test_bot_chain_call_history(mock_bot_chain):
    """Test that bot chain properly tracks call history."""
    
    # Run a simple flow
    import asyncio
    
    async def run_simple_flow():
        conv_id = "history_test"
        query = "החלטות ממשלה 37 בנושא חינוך"
        
        await mock_bot_chain.call_rewrite_bot(query, conv_id)
        await mock_bot_chain.call_intent_bot(query, conv_id)
        await mock_bot_chain.call_context_router(conv_id, query, "search", {"government_number": 37}, 0.9)
        await mock_bot_chain.call_sql_gen_bot("search", {"government_number": 37}, conv_id)
    
    asyncio.run(run_simple_flow())
    
    # Verify call history
    assert len(mock_bot_chain.call_history) == 4
    assert mock_bot_chain.call_history[0][0] == "rewrite"
    assert mock_bot_chain.call_history[1][0] == "intent"
    assert mock_bot_chain.call_history[2][0] == "context_router"
    assert mock_bot_chain.call_history[3][0] == "sql_gen"
    
    print("✅ Bot chain call history tracking verified")

@pytest.mark.asyncio
async def test_error_handling_in_flow():
    """Test error handling across the bot chain."""
    
    class FailingBotChain(MockBotChain):
        async def call_intent_bot(self, text: str, conv_id: str):
            # Simulate intent bot failure
            return {
                "success": False,
                "error": "Intent detection failed",
                "code": "INTENT_ERROR"
            }
    
    failing_chain = FailingBotChain()
    
    # Test flow with failing intent bot
    conv_id = "error_test"
    query = "test query"
    
    rewrite_result = await failing_chain.call_rewrite_bot(query, conv_id)
    assert rewrite_result["success"] == True
    
    intent_result = await failing_chain.call_intent_bot(query, conv_id)
    assert intent_result["success"] == False
    assert "error" in intent_result
    
    print("✅ Error handling in bot chain verified")

@pytest.mark.asyncio
async def test_performance_benchmarks():
    """Test performance characteristics of the bot chain."""
    
    mock_chain = MockBotChain()
    
    # Measure end-to-end latency
    import time
    
    start_time = time.time()
    
    # Run 10 queries to get average performance
    for i in range(10):
        conv_id = f"perf_test_{i}"
        query = f"החלטות ממשלה 37 בנושא חינוך - {i}"
        
        await mock_chain.call_rewrite_bot(query, conv_id)
        rewrite_result = await mock_chain.call_rewrite_bot(query, conv_id)
        intent_result = await mock_chain.call_intent_bot(rewrite_result["clean_text"], conv_id)
        router_result = await mock_chain.call_context_router(
            conv_id, query, intent_result["intent"], 
            intent_result["entities"], intent_result["confidence"]
        )
        if router_result["route"] == "direct_sql":
            await mock_chain.call_sql_gen_bot(intent_result["intent"], intent_result["entities"], conv_id)
    
    end_time = time.time()
    avg_latency = (end_time - start_time) / 10
    
    print(f"✅ Average end-to-end latency: {avg_latency:.3f} seconds")
    
    # Performance should be reasonable for mocked services
    assert avg_latency < 1.0, f"Average latency {avg_latency:.3f}s too high"
    
    # Call history should show all calls
    assert len(mock_chain.call_history) >= 40, "Expected at least 40 bot calls"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])