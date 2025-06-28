"""
Unit tests for CLARIFY Clarification Bot 2C.
Tests clarification question generation for ambiguous queries.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Test data for different types of ambiguous queries
AMBIGUOUS_QUERIES = {
    "vague_general": {
        "query": "מה קורה?",
        "intent": "search",
        "entities": {},
        "confidence": 0.3,
        "clarification_type": "vague_intent"
    },
    "missing_government": {
        "query": "החלטות בנושא חינוך",
        "intent": "search", 
        "entities": {"topic": "חינוך"},
        "confidence": 0.6,
        "clarification_type": "missing_entities"
    },
    "missing_topic": {
        "query": "החלטות ממשלה 37",
        "intent": "search",
        "entities": {"government_number": 37},
        "confidence": 0.7,
        "clarification_type": "missing_entities"
    },
    "ambiguous_time": {
        "query": "החלטות האחרונות",
        "intent": "search",
        "entities": {},
        "confidence": 0.5,
        "clarification_type": "ambiguous_time"
    },
    "low_confidence": {
        "query": "אולי משהו על זה",
        "intent": "search",
        "entities": {},
        "confidence": 0.2,
        "clarification_type": "low_confidence"
    }
}

CLEAR_QUERIES = {
    "specific_decision": {
        "query": "החלטה 660 של ממשלה 37",
        "intent": "specific_decision",
        "entities": {"government_number": 37, "decision_number": 660},
        "confidence": 0.95,
        "clarification_type": "none"
    },
    "clear_search": {
        "query": "החלטות ממשלה 37 בנושא חינוך מ-2023",
        "intent": "search",
        "entities": {"government_number": 37, "topic": "חינוך", "year": 2023},
        "confidence": 0.9,
        "clarification_type": "none"
    }
}

class TestClarificationBot:
    """Test the clarification bot functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Import here to handle module naming issues
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from CLARIFY_CLARIFY_BOT_2C.main import (
                generate_clarification_with_gpt,
                generate_fallback_clarification, 
                generate_suggested_refinements,
                ClarificationType,
                CLARIFICATION_TEMPLATES,
                GOVERNMENT_SUGGESTIONS,
                TOPIC_SUGGESTIONS
            )
            self.clarify_imported = True
            self.generate_clarification_with_gpt = generate_clarification_with_gpt
            self.generate_fallback_clarification = generate_fallback_clarification
            self.generate_suggested_refinements = generate_suggested_refinements
            self.ClarificationType = ClarificationType
            self.CLARIFICATION_TEMPLATES = CLARIFICATION_TEMPLATES
            self.GOVERNMENT_SUGGESTIONS = GOVERNMENT_SUGGESTIONS
            self.TOPIC_SUGGESTIONS = TOPIC_SUGGESTIONS
        except ImportError:
            self.clarify_imported = False

class TestClarificationGeneration(TestClarificationBot):
    """Test clarification question generation logic."""
    
    @pytest.mark.asyncio
    async def test_missing_entities_clarification(self):
        """Test clarification for missing entities."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query_data = AMBIGUOUS_QUERIES["missing_government"]
        clarification_type = self.ClarificationType.MISSING_ENTITIES
        
        result = await self.generate_fallback_clarification(
            query_data["query"],
            query_data["intent"],
            query_data["entities"], 
            clarification_type
        )
        
        assert "questions" in result
        assert len(result["questions"]) >= 1
        assert "explanation" in result
        
        # Should ask about missing government
        government_question = next(
            (q for q in result["questions"] if "ממשלה" in q["question"]), 
            None
        )
        assert government_question is not None
        assert len(government_question["suggestions"]) > 0
    
    @pytest.mark.asyncio 
    async def test_ambiguous_time_clarification(self):
        """Test clarification for ambiguous time references."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query_data = AMBIGUOUS_QUERIES["ambiguous_time"]
        clarification_type = self.ClarificationType.AMBIGUOUS_TIME
        
        result = await self.generate_fallback_clarification(
            query_data["query"],
            query_data["intent"],
            query_data["entities"],
            clarification_type
        )
        
        assert "questions" in result
        time_question = result["questions"][0]
        assert "תקופה" in time_question["question"] or "זמן" in time_question["question"]
        assert len(time_question["suggestions"]) > 0
        
        # Should include time-related suggestions
        suggestions_text = " ".join(time_question["suggestions"])
        assert any(word in suggestions_text for word in ["שנה", "אחרונות", "2023", "תקופה"])
    
    @pytest.mark.asyncio
    async def test_vague_intent_clarification(self):
        """Test clarification for vague intent."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query_data = AMBIGUOUS_QUERIES["vague_general"]
        clarification_type = self.ClarificationType.VAGUE_INTENT
        
        result = await self.generate_fallback_clarification(
            query_data["query"],
            query_data["intent"],
            query_data["entities"],
            clarification_type
        )
        
        assert "questions" in result
        intent_question = result["questions"][0]
        assert "מה" in intent_question["question"] or "איך" in intent_question["question"]
        assert len(intent_question["suggestions"]) >= 3
        
        # Should include action-oriented suggestions
        suggestions_text = " ".join(intent_question["suggestions"])
        assert any(word in suggestions_text for word in ["חיפוש", "החלטות", "לספור", "למצוא"])

class TestSuggestedRefinements(TestClarificationBot):
    """Test suggested query refinements."""
    
    @pytest.mark.asyncio
    async def test_refinements_for_missing_government(self):
        """Test refinements when government number is missing."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query_data = AMBIGUOUS_QUERIES["missing_government"]
        clarification_type = self.ClarificationType.MISSING_ENTITIES
        
        refinements = await self.generate_suggested_refinements(
            query_data["query"],
            query_data["intent"],
            query_data["entities"],
            clarification_type
        )
        
        assert len(refinements) > 0
        
        # Should suggest adding government numbers
        refinements_text = " ".join(refinements)
        assert "37" in refinements_text or "36" in refinements_text
        
        # Should not duplicate original query
        assert query_data["query"] not in refinements
    
    @pytest.mark.asyncio
    async def test_refinements_for_missing_topic(self):
        """Test refinements when topic is missing."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query_data = AMBIGUOUS_QUERIES["missing_topic"]
        clarification_type = self.ClarificationType.MISSING_ENTITIES
        
        refinements = await self.generate_suggested_refinements(
            query_data["query"],
            query_data["intent"],
            query_data["entities"],
            clarification_type
        )
        
        assert len(refinements) > 0
        
        # Should suggest adding topics
        refinements_text = " ".join(refinements)
        assert any(topic in refinements_text for topic in ["חינוך", "ביטחון", "נושא"])
    
    @pytest.mark.asyncio
    async def test_refinements_for_count_intent(self):
        """Test refinements for count queries without 'כמה'."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        query = "החלטות ממשלה 37"
        intent = "count"
        entities = {"government_number": 37}
        clarification_type = self.ClarificationType.MISSING_ENTITIES
        
        refinements = await self.generate_suggested_refinements(
            query, intent, entities, clarification_type
        )
        
        # Should suggest adding "כמה"
        refinements_text = " ".join(refinements)
        assert "כמה" in refinements_text

class TestGPTIntegration(TestClarificationBot):
    """Test GPT-powered clarification generation."""
    
    @pytest.mark.asyncio
    async def test_gpt_clarification_success(self):
        """Test successful GPT clarification generation."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "questions": [
                {
                    "type": "missing_government",
                    "question": "איזה ממשלה אתה מחפש?",
                    "suggestions": ["ממשלה 37", "ממשלה 36", "כל הממשלות"]
                }
            ],
            "explanation": "נדרש מספר ממשלה לחיפוש מדויק"
        })
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_response):
            query_data = AMBIGUOUS_QUERIES["missing_government"]
            clarification_type = self.ClarificationType.MISSING_ENTITIES
            
            result = await self.generate_clarification_with_gpt(
                query_data["query"],
                query_data["intent"],
                query_data["entities"],
                clarification_type
            )
            
            assert "questions" in result
            assert len(result["questions"]) == 1
            assert "ממשלה" in result["questions"][0]["question"]
            assert "ממשלה 37" in result["questions"][0]["suggestions"]
    
    @pytest.mark.asyncio
    async def test_gpt_clarification_fallback(self):
        """Test fallback when GPT fails."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        with patch('openai.ChatCompletion.acreate', side_effect=Exception("API Error")):
            query_data = AMBIGUOUS_QUERIES["missing_government"]
            clarification_type = self.ClarificationType.MISSING_ENTITIES
            
            result = await self.generate_clarification_with_gpt(
                query_data["query"],
                query_data["intent"],
                query_data["entities"],
                clarification_type
            )
            
            # Should still return a valid clarification structure
            assert "questions" in result
            assert "explanation" in result
            assert len(result["questions"]) > 0

class TestClarificationTypes(TestClarificationBot):
    """Test different clarification types."""
    
    def test_clarification_templates_exist(self):
        """Test that all clarification types have templates."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        for clarification_type in self.ClarificationType:
            assert clarification_type in self.CLARIFICATION_TEMPLATES
            templates = self.CLARIFICATION_TEMPLATES[clarification_type]
            assert len(templates) > 0
            assert all(isinstance(template, str) for template in templates)
    
    def test_suggestion_lists_populated(self):
        """Test that suggestion lists are properly populated."""
        if not self.clarify_imported:
            pytest.skip("Clarification module not available")
        
        assert len(self.GOVERNMENT_SUGGESTIONS) >= 4
        assert len(self.TOPIC_SUGGESTIONS) >= 6
        
        # Check Hebrew content
        assert any("ממשלה" in suggestion for suggestion in self.GOVERNMENT_SUGGESTIONS)
        assert any("חינוך" in suggestion for suggestion in self.TOPIC_SUGGESTIONS)

class TestClarificationAPI:
    """Test clarification API endpoints."""
    
    @pytest.mark.asyncio
    async def test_clarify_endpoint_missing_entities(self):
        """Test /clarify endpoint with missing entities."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from CLARIFY_CLARIFY_BOT_2C.main import app, ClarificationRequest
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            request_data = {
                "conv_id": "test_missing_entities",
                "original_query": "החלטות בנושא חינוך",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "confidence_score": 0.6,
                "clarification_type": "missing_entities",
                "context_history": []
            }
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = json.dumps({
                    "questions": [
                        {
                            "type": "missing_government",
                            "question": "איזה ממשלה אתה מחפש?",
                            "suggestions": ["ממשלה 37", "ממשלה 36"]
                        }
                    ],
                    "explanation": "נדרש מספר ממשלה"
                })
                
                response = client.post("/clarify", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert data["conv_id"] == "test_missing_entities"
                assert len(data["clarification_questions"]) >= 1
                assert len(data["suggested_refinements"]) > 0
                assert data["confidence"] > 0.0
                
        except ImportError:
            pytest.skip("Clarification module not available")
    
    def test_templates_endpoint(self):
        """Test /templates endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from CLARIFY_CLARIFY_BOT_2C.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/templates")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "clarification_types" in data
            assert "government_suggestions" in data
            assert "topic_suggestions" in data
            assert "total_templates" in data
            assert data["total_templates"] > 0
            
        except ImportError:
            pytest.skip("Clarification module not available")
    
    def test_health_endpoint(self):
        """Test /health endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from CLARIFY_CLARIFY_BOT_2C.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "CLARIFY_CLARIFY_BOT_2C" in data["service"]
            
        except ImportError:
            pytest.skip("Clarification module not available")

class TestIntegrationScenarios:
    """Test end-to-end clarification scenarios."""
    
    @pytest.mark.asyncio
    async def test_clarification_flow_for_ambiguous_query(self):
        """Test complete clarification flow for an ambiguous query."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from CLARIFY_CLARIFY_BOT_2C.main import (
                generate_fallback_clarification,
                generate_suggested_refinements,
                ClarificationType
            )
            
            # Simulate ambiguous query from user
            query = "מה עם החינוך?"
            intent = "search"
            entities = {"topic": "חינוך"}
            clarification_type = ClarificationType.MISSING_ENTITIES
            
            # Generate clarification
            clarification = await generate_fallback_clarification(
                query, intent, entities, clarification_type
            )
            
            # Generate refinements
            refinements = await generate_suggested_refinements(
                query, intent, entities, clarification_type
            )
            
            # Validate results
            assert len(clarification["questions"]) > 0
            assert len(refinements) > 0
            
            # Should ask about missing government
            government_question = next(
                (q for q in clarification["questions"] if "ממשלה" in q["question"]),
                None
            )
            assert government_question is not None
            
            # Refinements should be more specific than original
            for refinement in refinements:
                assert len(refinement) > len(query)
                assert refinement != query
            
        except ImportError:
            pytest.skip("Clarification module not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])