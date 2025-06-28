"""
Unit tests for QUERY Ranker Bot 3Q.
Tests result ranking, BM25 scoring, and GPT-powered relevance analysis.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Test data representing different types of search results
SAMPLE_SEARCH_RESULTS = [
    {
        "id": 1,
        "government_number": 37,
        "decision_number": 660,
        "decision_date": "2023-05-15",
        "title": "החלטה בנושא חינוך דיגיטלי",
        "content": "החלטה מפורטת על קידום החינוך הדיגיטלי במערכת החינוך הישראלית. כולל תקציב של 500 מיליון שקל לשלוש שנים.",
        "topics": ["חינוך", "טכנולוגיה"],
        "ministries": ["משרד החינוך"],
        "status": "approved"
    },
    {
        "id": 2,
        "government_number": 37,
        "decision_number": 661,
        "decision_date": "2023-06-20",
        "title": "תקציב משרד החינוך לשנת 2024",
        "content": "אישור תקציב משרד החינוך לשנת הכספים 2024 בסך 65 מיליארד שקל.",
        "topics": ["חינוך", "תקציב"],
        "ministries": ["משרד החינוך"],
        "status": "approved"
    },
    {
        "id": 3,
        "government_number": 37,
        "decision_number": 662,
        "decision_date": "2022-03-10",
        "title": "החלטה בנושא ביטחון סייבר",
        "content": "הקמת מערך ביטחון סייבר חדש במשרד הביטחון.",
        "topics": ["ביטחון", "טכנולוגיה"],
        "ministries": ["משרד הביטחון"],
        "status": "approved"
    },
    {
        "id": 4,
        "government_number": 36,
        "decision_number": 500,
        "decision_date": "2021-12-05",
        "title": "חוק תקציב המדינה 2022",
        "content": "אישור חוק תקציב המדינה לשנת 2022.",
        "topics": ["תקציב", "כלכלה"],
        "ministries": ["משרד האוצר"],
        "status": "approved"
    }
]

SAMPLE_EMPTY_RESULTS = []

class TestRankerBot:
    """Test the ranking bot functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Import here to handle module naming issues
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import (
                tokenize_hebrew_text,
                calculate_bm25_score,
                calculate_entity_match_score,
                calculate_temporal_score,
                calculate_popularity_score,
                prepare_corpus_statistics,
                RankingStrategy,
                RANKING_WEIGHTS
            )
            self.ranker_imported = True
            self.tokenize_hebrew_text = tokenize_hebrew_text
            self.calculate_bm25_score = calculate_bm25_score
            self.calculate_entity_match_score = calculate_entity_match_score
            self.calculate_temporal_score = calculate_temporal_score
            self.calculate_popularity_score = calculate_popularity_score
            self.prepare_corpus_statistics = prepare_corpus_statistics
            self.RankingStrategy = RankingStrategy
            self.RANKING_WEIGHTS = RANKING_WEIGHTS
        except ImportError:
            self.ranker_imported = False

class TestTextProcessing(TestRankerBot):
    """Test Hebrew text processing and tokenization."""
    
    def test_hebrew_tokenization(self):
        """Test Hebrew text tokenization."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        # Test Hebrew text
        hebrew_text = "החלטות ממשלה בנושא חינוך דיגיטלי"
        tokens = self.tokenize_hebrew_text(hebrew_text)
        
        assert len(tokens) > 0
        assert "החלטות" in tokens
        assert "ממשלה" in tokens
        assert "חינוך" in tokens
        assert "דיגיטלי" in tokens
        
        # Should filter out common stop words
        assert "בנושא" not in tokens or len("בנושא") <= 1
    
    def test_empty_text_tokenization(self):
        """Test tokenization of empty text."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        tokens = self.tokenize_hebrew_text("")
        assert tokens == []
        
        tokens = self.tokenize_hebrew_text(None)
        assert tokens == []
    
    def test_mixed_language_tokenization(self):
        """Test tokenization of mixed Hebrew/English text."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        mixed_text = "החלטה על AI ובינה מלאכותית"
        tokens = self.tokenize_hebrew_text(mixed_text)
        
        assert "החלטה" in tokens
        assert "בינה" in tokens
        assert "מלאכותית" in tokens
        # English/numbers should be filtered out in current implementation

class TestBM25Scoring(TestRankerBot):
    """Test BM25 relevance scoring."""
    
    def test_bm25_exact_match(self):
        """Test BM25 scoring with exact query match."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        query_tokens = ["חינוך", "דיגיטלי"]
        doc_tokens = ["חינוך", "דיגיטלי", "ממשלה", "החלטה"]
        corpus_stats = {"avg_doc_length": 4.0, "idf_חינוך": 1.0, "idf_דיגיטלי": 1.0}
        
        score = self.calculate_bm25_score(query_tokens, doc_tokens, corpus_stats)
        
        assert score > 0
        assert isinstance(score, float)
    
    def test_bm25_no_match(self):
        """Test BM25 scoring with no query match."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        query_tokens = ["ביטחון", "צבא"]
        doc_tokens = ["חינוך", "דיגיטלי", "ממשלה", "החלטה"]
        corpus_stats = {"avg_doc_length": 4.0}
        
        score = self.calculate_bm25_score(query_tokens, doc_tokens, corpus_stats)
        
        assert score == 0.0
    
    def test_bm25_partial_match(self):
        """Test BM25 scoring with partial query match."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        query_tokens = ["חינוך", "ביטחון"]  # Only "חינוך" matches
        doc_tokens = ["חינוך", "דיגיטלי", "ממשלה", "החלטה"]
        corpus_stats = {"avg_doc_length": 4.0, "idf_חינוך": 1.0}
        
        score = self.calculate_bm25_score(query_tokens, doc_tokens, corpus_stats)
        
        assert score > 0
        assert isinstance(score, float)

class TestEntityMatching(TestRankerBot):
    """Test entity matching scoring."""
    
    def test_perfect_entity_match(self):
        """Test perfect entity matching."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        entities = {"government_number": 37, "decision_number": 660}
        result = SAMPLE_SEARCH_RESULTS[0]  # Matches exactly
        
        score = self.calculate_entity_match_score(entities, result)
        
        assert score == 1.0  # Perfect match
    
    def test_partial_entity_match(self):
        """Test partial entity matching."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        entities = {"government_number": 37, "topic": "ביטחון"}  # Only government matches
        result = SAMPLE_SEARCH_RESULTS[0]  # Has government 37 but topic is "חינוך"
        
        score = self.calculate_entity_match_score(entities, result)
        
        assert 0.4 <= score <= 0.6  # Partial match (1 out of 2)
    
    def test_no_entity_match(self):
        """Test no entity matching."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        entities = {"government_number": 99, "topic": "משהו אחר"}
        result = SAMPLE_SEARCH_RESULTS[0]
        
        score = self.calculate_entity_match_score(entities, result)
        
        assert score == 0.0  # No match
    
    def test_empty_entities(self):
        """Test entity matching with no entities."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        entities = {}
        result = SAMPLE_SEARCH_RESULTS[0]
        
        score = self.calculate_entity_match_score(entities, result)
        
        assert score == 1.0  # No entities to match = perfect score

class TestTemporalScoring(TestRankerBot):
    """Test temporal relevance scoring."""
    
    def test_recent_decision_scoring(self):
        """Test scoring of recent decisions."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        # Use the most recent result (2023-06-20)
        result = SAMPLE_SEARCH_RESULTS[1]
        score = self.calculate_temporal_score(result)
        
        assert score > 0.5  # Recent decision should score well
        assert score <= 1.0
    
    def test_old_decision_scoring(self):
        """Test scoring of older decisions."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        # Use the oldest result (2021-12-05)
        result = SAMPLE_SEARCH_RESULTS[3]
        score = self.calculate_temporal_score(result)
        
        assert score < 0.8  # Older decision should score lower
        assert score >= 0.0
    
    def test_missing_date_scoring(self):
        """Test scoring when date is missing."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        result = {"title": "החלטה ללא תאריך"}  # No decision_date
        score = self.calculate_temporal_score(result)
        
        assert score == 0.5  # Neutral score for missing date

class TestPopularityScoring(TestRankerBot):
    """Test popularity-based scoring."""
    
    def test_comprehensive_result_scoring(self):
        """Test scoring of results with comprehensive content."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        # First result has more content and multiple topics
        result = SAMPLE_SEARCH_RESULTS[0]
        score = self.calculate_popularity_score(result)
        
        assert score > 0.5  # Should get bonus for content and topics
        assert score <= 1.0
    
    def test_minimal_result_scoring(self):
        """Test scoring of results with minimal content."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        minimal_result = {
            "title": "החלטה קצרה",
            "content": "תוכן מינימלי",
            "topics": [],
            "ministries": []
        }
        
        score = self.calculate_popularity_score(minimal_result)
        
        assert score >= 0.4  # Base score
        assert score <= 0.6

class TestCorpusStatistics(TestRankerBot):
    """Test corpus statistics calculation."""
    
    def test_corpus_stats_calculation(self):
        """Test corpus statistics preparation."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        stats = self.prepare_corpus_statistics(SAMPLE_SEARCH_RESULTS)
        
        assert "avg_doc_length" in stats
        assert stats["avg_doc_length"] > 0
        
        # Should have IDF values for common terms
        assert any(key.startswith("idf_") for key in stats.keys())
    
    def test_empty_corpus_stats(self):
        """Test corpus statistics with empty results."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        stats = self.prepare_corpus_statistics([])
        
        assert stats["avg_doc_length"] == 10.0  # Default value

class TestGPTIntegration(TestRankerBot):
    """Test GPT-powered semantic scoring."""
    
    @pytest.mark.asyncio
    async def test_gpt_semantic_scoring_success(self):
        """Test successful GPT semantic scoring."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"score": 0.85, "explanation": "רלוונטי מאוד לשאילתא"}'
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_response):
            try:
                from QUERY_RANKER_BOT_3Q.main import calculate_semantic_score_with_gpt
                
                score, explanation = await calculate_semantic_score_with_gpt(
                    "החלטות בנושא חינוך",
                    SAMPLE_SEARCH_RESULTS[0],
                    "search"
                )
                
                assert score == 0.85
                assert "רלוונטי" in explanation
                
            except ImportError:
                pytest.skip("Ranker module not available")
    
    @pytest.mark.asyncio
    async def test_gpt_semantic_scoring_fallback(self):
        """Test GPT semantic scoring fallback."""
        if not self.ranker_imported:
            pytest.skip("Ranker module not available")
        
        with patch('openai.ChatCompletion.acreate', side_effect=Exception("API Error")):
            try:
                from QUERY_RANKER_BOT_3Q.main import calculate_semantic_score_with_gpt
                
                score, explanation = await calculate_semantic_score_with_gpt(
                    "שאילתא",
                    SAMPLE_SEARCH_RESULTS[0],
                    "search"
                )
                
                assert score == 0.5  # Fallback score
                assert "fallback" in explanation
                
            except ImportError:
                pytest.skip("Ranker module not available")

class TestRankingAPI:
    """Test ranking API endpoints."""
    
    @pytest.mark.asyncio
    async def test_rank_endpoint_basic(self):
        """Test /rank endpoint with basic request."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            request_data = {
                "conv_id": "test_ranking",
                "original_query": "החלטות בנושא חינוך",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "results": SAMPLE_SEARCH_RESULTS[:2],  # Use first 2 results
                "strategy": "hybrid",
                "max_results": 5
            }
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = '{"score": 0.8, "explanation": "רלוונטי"}'
                
                response = client.post("/rank", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert data["conv_id"] == "test_ranking"
                assert len(data["ranked_results"]) == 2
                assert data["strategy_used"] == "hybrid"
                assert data["confidence"] > 0.0
                
                # Check ranking information is included
                first_result = data["ranked_results"][0]
                assert "_ranking" in first_result
                assert "total_score" in first_result["_ranking"]
                
        except ImportError:
            pytest.skip("Ranker module not available")
    
    def test_strategies_endpoint(self):
        """Test /strategies endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/strategies")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "available_strategies" in data
            assert "hybrid" in data["available_strategies"]
            assert "relevance" in data["available_strategies"]
            assert "temporal" in data["available_strategies"]
            assert "diversity" in data["available_strategies"]
            assert data["default_strategy"] == "hybrid"
            
        except ImportError:
            pytest.skip("Ranker module not available")
    
    def test_stats_endpoint(self):
        """Test /stats endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "ranking_weights" in data
            assert "bm25_parameters" in data
            assert "temporal_decay_months" in data
            assert "hebrew_stop_words_count" in data
            assert data["temporal_decay_months"] == 24
            
        except ImportError:
            pytest.skip("Ranker module not available")
    
    def test_health_endpoint(self):
        """Test /health endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "QUERY_RANKER_BOT_3Q" in data["service"]
            
        except ImportError:
            pytest.skip("Ranker module not available")

class TestIntegrationScenarios:
    """Test end-to-end ranking scenarios."""
    
    @pytest.mark.asyncio
    async def test_education_query_ranking(self):
        """Test ranking for education-related query."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import (
                rank_results_by_strategy,
                RankingStrategy
            )
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = '{"score": 0.9, "explanation": "רלוונטי מאוד"}'
                
                ranked_pairs = await rank_results_by_strategy(
                    "החלטות בנושא חינוך דיגיטלי",
                    "search",
                    {"topic": "חינוך"},
                    SAMPLE_SEARCH_RESULTS,
                    RankingStrategy.HYBRID
                )
                
                assert len(ranked_pairs) == 4
                
                # First result should be most relevant (education + digital)
                first_result, first_score = ranked_pairs[0]
                assert first_result["id"] == 1  # Education + digital result
                assert first_score.total_score > 0.5
                
                # Scores should be in descending order
                scores = [score.total_score for _, score in ranked_pairs]
                assert scores == sorted(scores, reverse=True)
                
        except ImportError:
            pytest.skip("Ranker module not available")
    
    @pytest.mark.asyncio
    async def test_temporal_strategy_ranking(self):
        """Test temporal ranking strategy."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from QUERY_RANKER_BOT_3Q.main import (
                rank_results_by_strategy,
                RankingStrategy
            )
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = '{"score": 0.7, "explanation": "ניתוח זמני"}'
                
                ranked_pairs = await rank_results_by_strategy(
                    "החלטות ממשלה",
                    "search",
                    {},
                    SAMPLE_SEARCH_RESULTS,
                    RankingStrategy.TEMPORAL
                )
                
                assert len(ranked_pairs) == 4
                
                # Most recent decision should be first
                first_result, first_score = ranked_pairs[0]
                first_date = first_result["decision_date"]
                
                # Check that temporal score component is significant
                assert first_score.temporal_score > 0.3
                
        except ImportError:
            pytest.skip("Ranker module not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])