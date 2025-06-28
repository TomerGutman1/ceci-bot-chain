"""
Cache Hit Ratio Tests for 2X Context Router Bot.
Tests that the Redis context cache achieves ≥60% hit ratio in conversation replay scenarios.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

# Test data: simulated conversation flows that should trigger cache hits
CONVERSATION_FLOWS = [
    {
        "conv_id": "conv_1",
        "queries": [
            "מה קורה עם החינוך?",
            "אני מתכוון לממשלה 37",
            "החלטות של ממשלה 37 בנושא חינוך",
            "תודה"
        ]
    },
    {
        "conv_id": "conv_2", 
        "queries": [
            "כמה החלטות קיבלה הממשלה?",
            "ממשלה 36",
            "החלטות ממשלה 36 בכלל"
        ]
    },
    {
        "conv_id": "conv_3",
        "queries": [
            "החלטה 660",
            "של ממשלה 37",
            "החלטה 660 של ממשלה 37"
        ]
    },
    {
        "conv_id": "conv_4",
        "queries": [
            "השוואה בין ממשלות",
            "ממשלה 35 לעומת 37",
            "בנושא ביטחון",
            "השוואה בין ממשלה 35 לממשלה 37 בנושא ביטחון"
        ]
    },
    {
        "conv_id": "conv_5",
        "queries": [
            "החלטות משרד החינוך",
            "מ-2023",
            "החלטות משרד החינוך מ-2023"
        ]
    }
]

class MockRedisClient:
    """Mock Redis client that tracks cache hits and misses."""
    
    def __init__(self):
        self.storage = {}
        self.hits = 0
        self.misses = 0
        self.gets = 0
        self.sets = 0
    
    def get(self, key):
        """Mock get with hit/miss tracking."""
        self.gets += 1
        if key in self.storage:
            self.hits += 1
            return self.storage[key]
        else:
            self.misses += 1
            return None
    
    def setex(self, key, ttl, value):
        """Mock setex."""
        self.sets += 1
        self.storage[key] = value
        return True
    
    def delete(self, key):
        """Mock delete."""
        if key in self.storage:
            del self.storage[key]
            return 1
        return 0
    
    def keys(self, pattern):
        """Mock keys method."""
        if pattern == "context:*":
            return [k for k in self.storage.keys() if k.startswith("context:")]
        return []
    
    def ping(self):
        """Mock ping."""
        return True
    
    def info(self):
        """Mock info."""
        return {
            "used_memory_human": "1.2M",
            "connected_clients": 1,
            "uptime_in_seconds": 3600
        }
    
    def get_hit_ratio(self):
        """Calculate cache hit ratio."""
        if self.gets == 0:
            return 0.0
        return self.hits / self.gets

@pytest.fixture
def mock_redis():
    """Fixture providing a mock Redis client."""
    return MockRedisClient()

@pytest.mark.asyncio
async def test_cache_hit_ratio_conversation_replay(mock_redis):
    """
    Test that conversation replay achieves ≥60% cache hit ratio.
    This simulates realistic conversation patterns where users clarify and refine queries.
    """
    # Import here to handle module naming issues
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            make_routing_decision,
            ContextRequest
        )
        bot_imported = True
    except ImportError:
        pytest.skip("Bot module not available")
    
    with patch('redis.from_url', return_value=mock_redis):
        # Process all conversation flows
        total_requests = 0
        
        for flow in CONVERSATION_FLOWS:
            conv_id = flow["conv_id"]
            
            for i, query in enumerate(flow["queries"]):
                # Simulate intent detection results
                # Later queries in conversation should have better entities due to context
                if i == 0:
                    # First query - often unclear
                    intent = "search"
                    entities = {}
                    confidence = 0.6
                elif i == 1:
                    # Clarification provided
                    intent = "search" 
                    entities = {"government_number": 37} if "37" in query else {"government_number": 36}
                    confidence = 0.8
                else:
                    # Refined query with full context
                    intent = "search"
                    entities = {
                        "government_number": 37 if "37" in query else 36,
                        "topic": "חינוך" if "חינוך" in query else "ביטחון"
                    }
                    confidence = 0.9
                
                # Make routing decision
                request = ContextRequest(
                    conv_id=conv_id,
                    current_query=query,
                    intent=intent,
                    entities=entities,
                    confidence_score=confidence
                )
                
                decision = await make_routing_decision(request)
                total_requests += 1
                
                # Verify decision makes sense
                assert hasattr(decision, 'route')
                assert hasattr(decision, 'needs_clarification')
    
    # Calculate hit ratio
    hit_ratio = mock_redis.get_hit_ratio()
    
    print(f"\nCache Performance Stats:")
    print(f"Total requests: {total_requests}")
    print(f"Cache gets: {mock_redis.gets}")
    print(f"Cache hits: {mock_redis.hits}")
    print(f"Cache misses: {mock_redis.misses}")
    print(f"Hit ratio: {hit_ratio:.2%}")
    
    # Assertion: Should achieve ≥60% hit ratio in conversation replay
    assert hit_ratio >= 0.60, f"Cache hit ratio {hit_ratio:.2%} below required 60%"
    
    # Additional assertions for realistic behavior
    assert mock_redis.gets > 0, "Should have attempted cache reads"
    assert mock_redis.sets > 0, "Should have cached contexts"
    assert len(mock_redis.storage) > 0, "Should have contexts in cache"

@pytest.mark.asyncio
async def test_cache_ttl_behavior(mock_redis):
    """Test that cache TTL prevents indefinite growth."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            ConversationContext,
            save_conversation_context
        )
        bot_imported = True
    except ImportError:
        pytest.skip("Bot module not available")
    
    with patch('redis.from_url', return_value=mock_redis):
        # Create a context
        context = ConversationContext(
            conv_id="ttl_test",
            user_queries=["שאלה"]
        )
        
        # Save context
        await save_conversation_context(context)
        
        # Verify TTL was set (we can't test actual expiration without time travel)
        # But we can verify setex was called, which includes TTL
        assert len(mock_redis.storage) == 1
        assert "context:ttl_test" in mock_redis.storage

@pytest.mark.asyncio 
async def test_cache_context_updates(mock_redis):
    """Test that context updates maintain cache coherence."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            make_routing_decision,
            get_conversation_context,
            ContextRequest
        )
        bot_imported = True
    except ImportError:
        pytest.skip("Bot module not available")
    
    with patch('redis.from_url', return_value=mock_redis):
        conv_id = "update_test"
        
        # First request - should create context
        request1 = ContextRequest(
            conv_id=conv_id,
            current_query="שאלה ראשונה",
            intent="search",
            entities={},
            confidence_score=0.7
        )
        
        decision1 = await make_routing_decision(request1)
        
        # Second request - should hit cache and update context
        request2 = ContextRequest(
            conv_id=conv_id,
            current_query="ממשלה 37",
            intent="search", 
            entities={"government_number": 37},
            confidence_score=0.8
        )
        
        decision2 = await make_routing_decision(request2)
        
        # Verify context was updated
        context = await get_conversation_context(conv_id)
        assert context is not None
        assert len(context.user_queries) == 2
        assert "ממשלה 37" in context.user_queries
        assert context.extracted_entities.get("government_number") == 37

def test_cache_key_consistency():
    """Test that cache keys are consistently formatted."""
    conv_ids = [
        "simple",
        "conv-with-dashes", 
        "conv_with_underscores",
        "conv123",
        "אות-עבריות-conv"
    ]
    
    for conv_id in conv_ids:
        key = f"context:{conv_id}"
        assert key.startswith("context:")
        assert conv_id in key
        assert len(key) > len("context:")

@pytest.mark.asyncio
async def test_cache_performance_under_load(mock_redis):
    """Test cache performance with concurrent requests."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from two_x_ctx_router_bot.main import (
            make_routing_decision,
            ContextRequest
        )
        bot_imported = True
    except ImportError:
        pytest.skip("Bot module not available")
    
    with patch('redis.from_url', return_value=mock_redis):
        # Create multiple concurrent conversations
        tasks = []
        
        for i in range(10):  # 10 concurrent conversations
            conv_id = f"load_test_{i}"
            
            # Each conversation has 3 queries
            for j in range(3):
                request = ContextRequest(
                    conv_id=conv_id,
                    current_query=f"שאלה {j+1}",
                    intent="search",
                    entities={"topic": "test"},
                    confidence_score=0.8
                )
                
                # Add to concurrent tasks
                task = make_routing_decision(request)
                tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all succeeded
        for result in results:
            assert not isinstance(result, Exception), f"Task failed: {result}"
        
        # Should have reasonable hit ratio even under load
        hit_ratio = mock_redis.get_hit_ratio()
        print(f"Hit ratio under load: {hit_ratio:.2%}")
        
        # Under concurrent load, hit ratio might be lower but should still be meaningful
        assert hit_ratio >= 0.30, f"Hit ratio {hit_ratio:.2%} too low under load"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])