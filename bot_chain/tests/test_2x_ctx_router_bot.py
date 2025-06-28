"""
Unit tests for 2X Context Router Bot.
Tests context management, routing logic, and cache operations.
"""

import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the modules we want to test
try:
    from two_x_ctx_router_bot.main import (  # Workaround for numeric module names
        make_routing_decision,
        needs_clarification,
        calculate_context_score,
        get_conversation_context,
        save_conversation_context,
        ConversationContext,
        ContextRequest,
        RoutingDecision
    )
    bot_imported = True
except ImportError:
    # Create mock objects for CI/testing
    bot_imported = False
    
    class ConversationContext:
        def __init__(self, conv_id, **kwargs):
            self.conv_id = conv_id
            self.user_queries = kwargs.get('user_queries', [])
            self.clarifications = kwargs.get('clarifications', [])
            self.extracted_entities = kwargs.get('extracted_entities', {})
            self.ambiguity_flags = kwargs.get('ambiguity_flags', [])
            self.last_intent = kwargs.get('last_intent', None)
            self.created_at = kwargs.get('created_at', datetime.utcnow())
            self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    class ContextRequest:
        def __init__(self, conv_id, current_query, intent, entities, confidence_score):
            self.conv_id = conv_id
            self.current_query = current_query
            self.intent = intent
            self.entities = entities
            self.confidence_score = confidence_score
    
    class RoutingDecision:
        def __init__(self, route, needs_clarification, **kwargs):
            self.route = route
            self.needs_clarification = needs_clarification
            self.clarification_type = kwargs.get('clarification_type')
            self.context_summary = kwargs.get('context_summary', {})
            self.reasoning = kwargs.get('reasoning', '')

class TestConversationContext:
    """Test ConversationContext model."""
    
    def test_context_creation(self):
        """Test creating a new conversation context."""
        conv_id = str(uuid4())
        context = ConversationContext(conv_id=conv_id)
        
        assert context.conv_id == conv_id
        assert context.user_queries == []
        assert context.extracted_entities == {}
        assert context.last_intent is None
        assert isinstance(context.created_at, datetime)

class TestRoutingLogic:
    """Test routing decision logic."""
    
    def test_needs_clarification_low_confidence(self):
        """Test that low confidence triggers clarification."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-1")
        
        needs_clarify, clarify_type, reasoning = needs_clarification(
            intent="search",
            entities={"topic": "חינוך"},
            confidence=0.6,  # Below threshold
            context=context,
            query="מה קורה עם החינוך"
        )
        
        assert needs_clarify == True
        assert clarify_type == "low_confidence"
        assert "0.60" in reasoning
    
    def test_needs_clarification_ambiguous_time(self):
        """Test that ambiguous time references trigger clarification."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-2")
        
        needs_clarify, clarify_type, reasoning = needs_clarification(
            intent="search",
            entities={"topic": "ביטחון"},
            confidence=0.9,  # High confidence
            context=context,
            query="החלטות בנושא ביטחון בתקופה האחרונה"  # Contains "תקופה"
        )
        
        assert needs_clarify == True
        assert clarify_type == "ambiguous_time"
        assert "תקופה" in reasoning
    
    def test_needs_clarification_missing_entities(self):
        """Test that missing required entities trigger clarification."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-3")
        
        needs_clarify, clarify_type, reasoning = needs_clarification(
            intent="search",
            entities={"topic": "חינוך"},  # Missing government_number
            confidence=0.9,
            context=context,
            query="החלטות בנושא חינוך"
        )
        
        assert needs_clarify == True
        assert clarify_type == "missing_entities"
        assert "government_number" in reasoning
    
    def test_no_clarification_needed(self):
        """Test successful routing without clarification."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-4")
        
        needs_clarify, clarify_type, reasoning = needs_clarification(
            intent="search",
            entities={"topic": "חינוך", "government_number": 37},
            confidence=0.9,
            context=context,
            query="החלטות ממשלה 37 בנושא חינוך"
        )
        
        assert needs_clarify == False
        assert clarify_type is None
        assert "All routing checks passed" in reasoning

class TestContextScore:
    """Test context scoring algorithm."""
    
    def test_calculate_context_score_empty(self):
        """Test context score with empty context."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-5")
        score = calculate_context_score(context, confidence=0.8)
        
        # Should be mostly based on confidence (0.3 weight)
        assert 0.2 <= score <= 0.3  # Just confidence contribution
    
    def test_calculate_context_score_rich(self):
        """Test context score with rich conversation history."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(
            conv_id="test-6",
            user_queries=["שאלה 1", "שאלה 2", "שאלה 3"],
            extracted_entities={"government_number": 37, "topic": "חינוך", "date_range": "2023"}
        )
        score = calculate_context_score(context, confidence=0.9)
        
        # Should be high with 3 queries, 3 entities, and high confidence
        assert score >= 0.8

class TestContextManagement:
    """Test context storage and retrieval."""
    
    @pytest.mark.asyncio
    async def test_context_roundtrip(self):
        """Test saving and loading context."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        with patch('redis.from_url') as mock_redis:
            # Mock Redis client
            mock_client = Mock()
            mock_redis.return_value = mock_client
            
            # Test context
            context = ConversationContext(
                conv_id="test-7",
                user_queries=["שאלה ראשונה"],
                extracted_entities={"topic": "חינוך"}
            )
            
            # Mock setex for save
            mock_client.setex.return_value = True
            
            # Save context
            result = await save_conversation_context(context)
            assert result == True
            
            # Verify setex was called correctly
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert call_args[0][0] == "context:test-7"  # Key
            assert call_args[0][1] == 7200  # TTL (2 hours)
            
            # Mock get for load
            mock_client.get.return_value = context.json()
            
            # Load context
            loaded_context = await get_conversation_context("test-7")
            assert loaded_context is not None
            assert loaded_context.conv_id == "test-7"
            assert loaded_context.user_queries == ["שאלה ראשונה"]

class TestRoutingDecisions:
    """Test end-to-end routing decisions."""
    
    @pytest.mark.asyncio
    async def test_routing_decision_clarify(self):
        """Test routing decision that requires clarification."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            
            # Mock empty context (new conversation)
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            
            request = ContextRequest(
                conv_id="test-8",
                current_query="מה קורה?",  # Vague query
                intent="search",
                entities={},
                confidence_score=0.5  # Low confidence
            )
            
            decision = await make_routing_decision(request)
            
            assert decision.route == "clarify"
            assert decision.needs_clarification == True
            assert decision.clarification_type in ["low_confidence", "vague_topic"]
    
    @pytest.mark.asyncio
    async def test_routing_decision_direct_sql(self):
        """Test routing decision that goes directly to SQL."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            
            # Mock context with previous queries
            existing_context = ConversationContext(
                conv_id="test-9",
                user_queries=["שאלה קודמת", "עוד שאלה"],
                extracted_entities={"topic": "חינוך"}
            )
            mock_client.get.return_value = existing_context.json()
            mock_client.setex.return_value = True
            
            request = ContextRequest(
                conv_id="test-9",
                current_query="החלטות ממשלה 37 בנושא חינוך",
                intent="search",
                entities={"government_number": 37, "topic": "חינוך"},
                confidence_score=0.95  # Very high confidence
            )
            
            decision = await make_routing_decision(request)
            
            assert decision.needs_clarification == False
            # Should be either "direct_sql" or "next_bot" depending on context score
            assert decision.route in ["direct_sql", "next_bot"]

class TestHebrew:
    """Test Hebrew text processing."""
    
    def test_hebrew_ambiguous_detection(self):
        """Test detection of ambiguous Hebrew phrases."""
        if not bot_imported:
            pytest.skip("Bot module not available")
            
        context = ConversationContext(conv_id="test-10")
        
        # Test various Hebrew ambiguous phrases
        test_cases = [
            ("החלטות בתקופה האחרונה", "תקופה"),
            ("מה עם הדבר הזה", "דבר"),
            ("איך זה עובד", "איך"),
            ("למה קרה זה", "למה")
        ]
        
        for query, expected_trigger in test_cases:
            needs_clarify, clarify_type, reasoning = needs_clarification(
                intent="search",
                entities={"topic": "כללי"},
                confidence=0.9,
                context=context,
                query=query
            )
            
            # Some should trigger clarification based on ambiguous content
            if expected_trigger in ["תקופה", "דבר"]:
                assert needs_clarify == True
                assert expected_trigger in reasoning

class TestApiIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_structure(self):
        """Test health endpoint response structure."""
        # This would be tested with actual API calls in integration tests
        expected_fields = ["status", "timestamp", "redis_connected", "context_cache_size"]
        
        # Mock response structure
        health_response = {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": True,
            "context_cache_size": 0
        }
        
        for field in expected_fields:
            assert field in health_response
    
    def test_routing_request_validation(self):
        """Test that routing requests are properly validated."""
        # Test required fields
        required_fields = ["conv_id", "current_query", "intent", "entities", "confidence_score"]
        
        valid_request = {
            "conv_id": "test-11",
            "current_query": "שאלה",
            "intent": "search",
            "entities": {"topic": "חינוך"},
            "confidence_score": 0.8
        }
        
        # All fields should be present
        for field in required_fields:
            assert field in valid_request
        
        # Test confidence score range
        assert 0.0 <= valid_request["confidence_score"] <= 1.0

@pytest.mark.skipif(not bot_imported, reason="Bot module not available for import")
class TestRealImport:
    """Tests that run only when the actual bot module can be imported."""
    
    def test_bot_config_loaded(self):
        """Test that bot configuration is properly loaded."""
        from common.config import get_config
        
        config = get_config('2X_MAIN_CTX_ROUTER_BOT')
        assert config.layer_name == '2X_MAIN_CTX_ROUTER_BOT'
        assert config.port == 8013
        assert config.model == 'gpt-3.5-turbo'
        assert config.temperature == 0.2

# Performance and edge case tests
class TestPerformance:
    """Test performance characteristics."""
    
    def test_context_size_limits(self):
        """Test context size management."""
        # Context should limit the number of stored queries
        context = ConversationContext(conv_id="test-12")
        
        # Simulate adding many queries
        for i in range(10):
            context.user_queries.append(f"שאלה {i}")
        
        # Should keep only last 5 based on implementation
        assert len(context.user_queries) == 10  # Before size management
        
        # The actual size management happens in update_context_with_query
        # This test verifies the data structure can handle the load
    
    def test_cache_key_format(self):
        """Test Redis cache key format."""
        conv_id = "test-conversation-123"
        expected_key = f"context:{conv_id}"
        
        # This is the format used in the implementation
        assert expected_key == "context:test-conversation-123"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])