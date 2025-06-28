"""
Unit tests for EVAL Evaluator Bot 2E.
Tests result evaluation, quality scoring, and GPT-powered content analysis.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Test data representing different types of query results
SAMPLE_GOVERNMENT_DECISIONS = [
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
    }
]

SAMPLE_EMPTY_RESULTS = []

SAMPLE_INCOMPLETE_RESULTS = [
    {
        "id": 3,
        "government_number": 37,
        "title": "החלטה חסרת פרטים",
        # Missing: decision_date, content, topics
    }
]

class TestEvaluatorBot:
    """Test the evaluator bot functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Import here to handle module naming issues
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from EVAL_EVALUATOR_BOT_2E.main import (
                evaluate_relevance,
                evaluate_completeness,
                evaluate_accuracy,
                evaluate_entity_match,
                evaluate_performance,
                EVALUATION_WEIGHTS,
                RelevanceLevel
            )
            self.evaluator_imported = True
            self.evaluate_relevance = evaluate_relevance
            self.evaluate_completeness = evaluate_completeness
            self.evaluate_accuracy = evaluate_accuracy
            self.evaluate_entity_match = evaluate_entity_match
            self.evaluate_performance = evaluate_performance
            self.EVALUATION_WEIGHTS = EVALUATION_WEIGHTS
            self.RelevanceLevel = RelevanceLevel
        except ImportError:
            self.evaluator_imported = False

class TestRelevanceEvaluation(TestEvaluatorBot):
    """Test relevance evaluation logic."""
    
    def test_relevance_with_matching_entities(self):
        """Test relevance evaluation with results that match entities."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37 בנושא חינוך"
        intent = "search"
        entities = {"government_number": 37, "topic": "חינוך"}
        results = SAMPLE_GOVERNMENT_DECISIONS
        
        metric = self.evaluate_relevance(query, intent, entities, results)
        
        assert metric.name == "relevance"
        assert metric.weight == self.EVALUATION_WEIGHTS["relevance"]
        assert metric.score >= 0.7  # Should be high relevance
        assert "entities" in metric.explanation.lower() or "match" in metric.explanation.lower()
    
    def test_relevance_with_no_results(self):
        """Test relevance evaluation with no results."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות שלא קיימות"
        intent = "search"
        entities = {"government_number": 99}
        results = SAMPLE_EMPTY_RESULTS
        
        metric = self.evaluate_relevance(query, intent, entities, results)
        
        assert metric.score == 0.0
        assert "no results" in metric.explanation.lower()
    
    def test_relevance_intent_specific_scoring(self):
        """Test that relevance scoring adapts to different intents."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        entities = {"government_number": 37, "decision_number": 660}
        results = [SAMPLE_GOVERNMENT_DECISIONS[0]]  # Single specific result
        
        # Specific decision intent should score higher with 1 result
        metric_specific = self.evaluate_relevance(
            "החלטה 660 של ממשלה 37", "specific_decision", entities, results
        )
        
        # Search intent with 1 result should score lower
        metric_search = self.evaluate_relevance(
            "החלטות ממשלה 37", "search", {"government_number": 37}, results
        )
        
        assert metric_specific.score > metric_search.score

class TestCompletenessEvaluation(TestEvaluatorBot):
    """Test completeness evaluation logic."""
    
    def test_completeness_with_full_data(self):
        """Test completeness with complete results."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37 בנושא חינוך"
        intent = "search"
        entities = {"government_number": 37, "topic": "חינוך"}
        results = SAMPLE_GOVERNMENT_DECISIONS
        
        metric = self.evaluate_completeness(query, intent, entities, results)
        
        assert metric.score >= 0.6  # Should be reasonably complete
        assert "complete" in metric.explanation.lower() or "data" in metric.explanation.lower()
    
    def test_completeness_with_incomplete_data(self):
        """Test completeness with incomplete results."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37"
        intent = "search"
        entities = {"government_number": 37}
        results = SAMPLE_INCOMPLETE_RESULTS
        
        metric = self.evaluate_completeness(query, intent, entities, results)
        
        assert metric.score < 0.8  # Should be lower due to incomplete data
    
    def test_completeness_count_intent(self):
        """Test completeness evaluation for count intent."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "כמה החלטות קיבלה ממשלה 37?"
        intent = "count"
        entities = {"government_number": 37}
        
        # Count should prefer exactly 1 result
        single_result = [{"count": 15}]
        metric_single = self.evaluate_completeness(query, intent, entities, single_result)
        
        multiple_results = SAMPLE_GOVERNMENT_DECISIONS
        metric_multiple = self.evaluate_completeness(query, intent, entities, multiple_results)
        
        assert metric_single.score > metric_multiple.score

class TestAccuracyEvaluation(TestEvaluatorBot):
    """Test accuracy evaluation logic."""
    
    def test_accuracy_with_consistent_data(self):
        """Test accuracy with consistent, valid data."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37 בנושא חינוך"
        intent = "search"
        entities = {"government_number": 37}
        results = SAMPLE_GOVERNMENT_DECISIONS
        
        metric = self.evaluate_accuracy(query, intent, entities, results)
        
        assert metric.score >= 0.6  # Should have decent accuracy
        assert "consistency" in metric.explanation.lower() or "verified" in metric.explanation.lower()
    
    def test_accuracy_with_invalid_dates(self):
        """Test accuracy detection with invalid dates."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37"
        intent = "search"
        entities = {"government_number": 37}
        
        # Results with invalid dates
        invalid_results = [
            {
                "government_number": 37,
                "decision_date": "1900-01-01",  # Too early
                "title": "החלטה עם תאריך לא תקין",
                "content": "תוכן החלטה"
            }
        ]
        
        metric = self.evaluate_accuracy(query, intent, entities, invalid_results)
        
        assert metric.score < 0.7  # Should be penalized for invalid dates

class TestEntityMatching(TestEvaluatorBot):
    """Test entity matching evaluation."""
    
    def test_entity_match_perfect(self):
        """Test perfect entity matching."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטה 660 של ממשלה 37"
        intent = "specific_decision"
        entities = {"government_number": 37, "decision_number": 660}
        results = [SAMPLE_GOVERNMENT_DECISIONS[0]]  # Matches exactly
        
        metric = self.evaluate_entity_match(query, intent, entities, results)
        
        assert metric.score == 1.0  # Perfect match
        assert "2/2" in metric.explanation  # 2 out of 2 entities matched
    
    def test_entity_match_partial(self):
        """Test partial entity matching."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37 בנושא ביטחון"
        intent = "search"
        entities = {"government_number": 37, "topic": "ביטחון"}
        results = SAMPLE_GOVERNMENT_DECISIONS  # Matches government but not topic
        
        metric = self.evaluate_entity_match(query, intent, entities, results)
        
        assert 0.4 <= metric.score <= 0.6  # Partial match
        assert "1/2" in metric.explanation  # 1 out of 2 entities matched
    
    def test_entity_match_no_entities(self):
        """Test entity matching when no entities provided."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "כל ההחלטות"
        intent = "search"
        entities = {}
        results = SAMPLE_GOVERNMENT_DECISIONS
        
        metric = self.evaluate_entity_match(query, intent, entities, results)
        
        assert metric.score == 1.0  # Perfect score when no entities to match
        assert "no entities" in metric.explanation.lower()

class TestPerformanceEvaluation(TestEvaluatorBot):
    """Test performance evaluation logic."""
    
    def test_performance_excellent_speed(self):
        """Test performance evaluation with excellent response time."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37"
        intent = "search"
        entities = {"government_number": 37}
        results = SAMPLE_GOVERNMENT_DECISIONS
        execution_time_ms = 50  # Very fast
        result_count = len(results)
        
        metric = self.evaluate_performance(
            query, intent, entities, results, execution_time_ms, result_count
        )
        
        assert metric.score >= 0.9  # Should get high performance score
        assert "excellent" in metric.explanation.lower() or "fast" in metric.explanation.lower()
    
    def test_performance_slow_response(self):
        """Test performance evaluation with slow response time."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "החלטות ממשלה 37"
        intent = "search"
        entities = {"government_number": 37}
        results = SAMPLE_GOVERNMENT_DECISIONS
        execution_time_ms = 2000  # Slow
        result_count = len(results)
        
        metric = self.evaluate_performance(
            query, intent, entities, results, execution_time_ms, result_count
        )
        
        assert metric.score < 0.8  # Should be penalized for slow response
        assert "slow" in metric.explanation.lower()
    
    def test_performance_count_efficiency(self):
        """Test performance evaluation for count queries."""
        if not self.evaluator_imported:
            pytest.skip("Evaluator module not available")
        
        query = "כמה החלטות ממשלה 37?"
        intent = "count"
        entities = {"government_number": 37}
        
        # Efficient count (1 result)
        efficient_results = [{"count": 42}]
        metric_efficient = self.evaluate_performance(
            query, intent, entities, efficient_results, 100, 1
        )
        
        # Inefficient count (multiple results)
        inefficient_results = SAMPLE_GOVERNMENT_DECISIONS
        metric_inefficient = self.evaluate_performance(
            query, intent, entities, inefficient_results, 100, len(inefficient_results)
        )
        
        assert metric_efficient.score > metric_inefficient.score

class TestGPTContentAnalysis:
    """Test GPT-powered content analysis."""
    
    @pytest.mark.asyncio
    async def test_gpt_content_analysis_success(self):
        """Test successful GPT content analysis."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "semantic_relevance": 0.85,
            "content_quality": 0.78,
            "language_quality": 0.92,
            "explanation": "התוצאות רלוונטיות לשאילתא ובאיכות טובה"
        }
        '''
        
        with patch('openai.ChatCompletion.acreate', return_value=mock_response):
            try:
                from EVAL_EVALUATOR_BOT_2E.main import analyze_content_with_gpt
                
                result = await analyze_content_with_gpt(
                    "החלטות ממשלה 37 בנושא חינוך",
                    "search",
                    {"government_number": 37, "topic": "חינוך"},
                    SAMPLE_GOVERNMENT_DECISIONS
                )
                
                assert result["semantic_relevance"] == 0.85
                assert result["content_quality"] == 0.78
                assert result["language_quality"] == 0.92
                assert "רלוונטיות" in result["gpt_explanation"]
                
            except ImportError:
                pytest.skip("Evaluator module not available")
    
    @pytest.mark.asyncio
    async def test_gpt_content_analysis_no_results(self):
        """Test GPT content analysis with no results."""
        try:
            from EVAL_EVALUATOR_BOT_2E.main import analyze_content_with_gpt
            
            result = await analyze_content_with_gpt(
                "שאילתא ללא תוצאות",
                "search",
                {},
                SAMPLE_EMPTY_RESULTS
            )
            
            assert result["semantic_relevance"] == 0.0
            assert result["content_quality"] == 0.0
            assert result["language_quality"] == 0.0
            assert "no results" in result["gpt_explanation"].lower()
            
        except ImportError:
            pytest.skip("Evaluator module not available")

class TestIntegrationScenarios:
    """Test end-to-end evaluation scenarios."""
    
    @pytest.mark.asyncio
    async def test_excellent_query_evaluation(self):
        """Test evaluation of an excellent query result."""
        try:
            from EVAL_EVALUATOR_BOT_2E.main import evaluate_results, EvaluationRequest
            
            request = EvaluationRequest(
                conv_id="test_excellent",
                original_query="החלטה 660 של ממשלה 37",
                intent="specific_decision",
                entities={"government_number": 37, "decision_number": 660},
                sql_query="SELECT * FROM decisions WHERE gov=37 AND num=660",
                results=[SAMPLE_GOVERNMENT_DECISIONS[0]],
                result_count=1,
                execution_time_ms=85
            )
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = '{"semantic_relevance": 0.9, "content_quality": 0.85, "language_quality": 0.9, "explanation": "מצוין"}'
                
                evaluation = await evaluate_results(request)
                
                assert evaluation.overall_score >= 0.8  # Should be high quality
                assert evaluation.relevance_level.value in ["highly_relevant", "relevant"]
                assert len(evaluation.quality_metrics) == 5
                assert evaluation.confidence >= 0.8
                assert "660" in evaluation.explanation or "37" in evaluation.explanation
                
        except ImportError:
            pytest.skip("Evaluator module not available")
    
    @pytest.mark.asyncio
    async def test_poor_query_evaluation(self):
        """Test evaluation of a poor query result."""
        try:
            from EVAL_EVALUATOR_BOT_2E.main import evaluate_results, EvaluationRequest
            
            request = EvaluationRequest(
                conv_id="test_poor",
                original_query="החלטות ממשלה 37 בנושא ביטחון",
                intent="search",
                entities={"government_number": 37, "topic": "ביטחון"},
                sql_query="SELECT * FROM decisions",
                results=SAMPLE_INCOMPLETE_RESULTS,  # Poor quality results
                result_count=1,
                execution_time_ms=1500  # Slow
            )
            
            with patch('openai.ChatCompletion.acreate') as mock_openai:
                mock_openai.return_value = Mock()
                mock_openai.return_value.choices = [Mock()]
                mock_openai.return_value.choices[0].message.content = '{"semantic_relevance": 0.3, "content_quality": 0.2, "language_quality": 0.4, "explanation": "איכות נמוכה"}'
                
                evaluation = await evaluate_results(request)
                
                assert evaluation.overall_score <= 0.6  # Should be low quality
                assert evaluation.relevance_level.value in ["not_relevant", "partially_relevant"]
                assert len(evaluation.recommendations) > 0
                assert any("שיפור" in rec for rec in evaluation.recommendations)
                
        except ImportError:
            pytest.skip("Evaluator module not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])