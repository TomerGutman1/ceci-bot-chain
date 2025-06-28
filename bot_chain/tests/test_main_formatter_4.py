"""
Unit tests for MAIN Formatter 4.
Tests response formatting for different output formats and presentation styles.
"""

import pytest
import json
from typing import Dict, List

# Test data representing formatted search results
SAMPLE_FORMATTED_RESULTS = [
    {
        "id": 1,
        "government_number": 37,
        "decision_number": 660,
        "decision_date": "2023-05-15",
        "title": "החלטה בנושא חינוך דיגיטלי",
        "content": "החלטה מפורטת על קידום החינוך הדיגיטלי במערכת החינוך הישראלית. כולל תקציב של 500 מיליון שקל לשלוש שנים לצורך רכישת ציוד טכנולוגי מתקדם ופיתוח תוכניות לימוד חדשניות.",
        "topics": ["חינוך", "טכנולוגיה"],
        "ministries": ["משרד החינוך"],
        "status": "approved",
        "_ranking": {
            "total_score": 0.95,
            "bm25_score": 0.90,
            "semantic_score": 0.88,
            "entity_score": 1.0,
            "temporal_score": 0.95,
            "popularity_score": 0.85,
            "explanation": "דירוג היברידי"
        }
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
        "status": "approved",
        "_ranking": {
            "total_score": 0.85,
            "explanation": "דירוג לפי רלוונטיות"
        }
    }
]

SAMPLE_COUNT_RESULT = [{"count": 42}]

SAMPLE_EVALUATION = {
    "overall_score": 0.87,
    "relevance_level": "highly_relevant",
    "confidence": 0.92
}

class TestFormatterBot:
    """Test the formatter bot functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Import here to handle module naming issues
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import (
                format_hebrew_date,
                truncate_hebrew_text,
                format_government_info,
                format_topics_and_ministries,
                format_markdown_response,
                format_json_response,
                format_html_response,
                format_plain_text_response,
                format_summary_response,
                OutputFormat,
                PresentationStyle
            )
            self.formatter_imported = True
            self.format_hebrew_date = format_hebrew_date
            self.truncate_hebrew_text = truncate_hebrew_text
            self.format_government_info = format_government_info
            self.format_topics_and_ministries = format_topics_and_ministries
            self.format_markdown_response = format_markdown_response
            self.format_json_response = format_json_response
            self.format_html_response = format_html_response
            self.format_plain_text_response = format_plain_text_response
            self.format_summary_response = format_summary_response
            self.OutputFormat = OutputFormat
            self.PresentationStyle = PresentationStyle
        except ImportError:
            self.formatter_imported = False

class TestTextFormatting(TestFormatterBot):
    """Test basic text formatting functions."""
    
    def test_hebrew_date_formatting(self):
        """Test Hebrew date formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        # Test valid date
        formatted = self.format_hebrew_date("2023-05-15")
        assert "15" in formatted
        assert "מאי" in formatted
        assert "2023" in formatted
        
        # Test invalid date
        formatted = self.format_hebrew_date("invalid-date")
        assert formatted == "invalid-date"
        
        # Test empty date
        formatted = self.format_hebrew_date("")
        assert formatted == "תאריך לא זמין"
    
    def test_text_truncation(self):
        """Test Hebrew text truncation."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        short_text = "טקסט קצר"
        assert self.truncate_hebrew_text(short_text, 100) == short_text
        
        long_text = "זהו טקסט ארוך מאוד שצריך להיחתך " * 10
        truncated = self.truncate_hebrew_text(long_text, 50)
        assert len(truncated) <= 53  # 50 + "..."
        assert truncated.endswith("...")
    
    def test_government_info_formatting(self):
        """Test government information formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        result = SAMPLE_FORMATTED_RESULTS[0]
        formatted = self.format_government_info(result)
        
        assert "ממשלה 37" in formatted
        assert "החלטה 660" in formatted
        assert "מאי" in formatted  # Date should be formatted
        assert "2023" in formatted
    
    def test_topics_and_ministries_formatting(self):
        """Test topics and ministries formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        result = SAMPLE_FORMATTED_RESULTS[0]
        formatted = self.format_topics_and_ministries(result)
        
        assert "נושאים:" in formatted or "נושא:" in formatted
        assert "חינוך" in formatted
        assert "משרד החינוך" in formatted

class TestMarkdownFormatting(TestFormatterBot):
    """Test Markdown output formatting."""
    
    def test_markdown_detailed_formatting(self):
        """Test detailed Markdown formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_markdown_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.DETAILED,
            include_metadata=True,
            include_scores=True,
            evaluation_summary=SAMPLE_EVALUATION
        )
        
        assert "# תוצאות חיפוש:" in formatted
        assert "החלטות בנושא חינוך" in formatted
        assert "נמצאו 2 תוצאות" in formatted
        assert "## 1. החלטה בנושא חינוך דיגיטלי" in formatted
        assert "ממשלה 37" in formatted
        assert "ציון: 0.95" in formatted  # Scoring info
        assert "איכות התוצאות: 0.87" in formatted  # Evaluation
    
    def test_markdown_compact_formatting(self):
        """Test compact Markdown formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_markdown_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.COMPACT,
            include_metadata=False,
            include_scores=False
        )
        
        assert "**1. החלטה בנושא חינוך דיגיטלי**" in formatted
        assert "ממשלה 37" in formatted
        assert "ציון:" not in formatted  # No scores
        assert "איכות התוצאות:" not in formatted  # No evaluation
    
    def test_markdown_list_formatting(self):
        """Test list Markdown formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_markdown_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.LIST
        )
        
        assert "1. **החלטה בנושא חינוך דיגיטלי**" in formatted
        assert "(ממשלה 37, החלטה 660)" in formatted
        assert "2. **תקציב משרד החינוך" in formatted
    
    def test_markdown_count_formatting(self):
        """Test count query Markdown formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_markdown_response(
            SAMPLE_COUNT_RESULT,
            "כמה החלטות ממשלה 37",
            "count",
            self.PresentationStyle.DETAILED
        )
        
        assert "# תוצאות ספירה:" in formatted
        assert "מספר ההחלטות:** 42" in formatted

class TestJSONFormatting(TestFormatterBot):
    """Test JSON output formatting."""
    
    def test_json_basic_formatting(self):
        """Test basic JSON formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_json_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            include_metadata=True,
            include_scores=True,
            evaluation_summary=SAMPLE_EVALUATION
        )
        
        # Parse JSON to validate structure
        data = json.loads(formatted)
        
        assert data["query"] == "החלטות בנושא חינוך"
        assert data["intent"] == "search"
        assert data["total_results"] == 2
        assert len(data["results"]) == 2
        
        # Check first result
        first_result = data["results"][0]
        assert first_result["title"] == "החלטה בנושא חינוך דיגיטלי"
        assert first_result["government_number"] == 37
        assert "ranking" in first_result  # Scores included
        
        # Check metadata
        assert "metadata" in data
        assert data["metadata"]["evaluation"] == SAMPLE_EVALUATION
    
    def test_json_without_scores(self):
        """Test JSON formatting without scores."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_json_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            include_metadata=False,
            include_scores=False
        )
        
        data = json.loads(formatted)
        first_result = data["results"][0]
        
        assert "ranking" not in first_result
        assert "metadata" not in data

class TestHTMLFormatting(TestFormatterBot):
    """Test HTML output formatting."""
    
    def test_html_detailed_formatting(self):
        """Test detailed HTML formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_html_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.DETAILED,
            include_metadata=True,
            include_scores=True,
            evaluation_summary=SAMPLE_EVALUATION
        )
        
        assert "<!DOCTYPE html>" in formatted
        assert "dir='rtl'" in formatted  # RTL for Hebrew
        assert "lang='he'" in formatted
        assert "<title>תוצאות חיפוש: החלטות בנושא חינוך</title>" in formatted
        assert "נמצאו 2 תוצאות" in formatted
        assert "החלטה בנושא חינוך דיגיטלי" in formatted
        assert "ציון: 0.95" in formatted  # Scores included
        assert "איכות התוצאות: 0.87" in formatted  # Evaluation
    
    def test_html_compact_formatting(self):
        """Test compact HTML formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_html_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.COMPACT,
            include_metadata=False,
            include_scores=False
        )
        
        assert "החלטה בנושא חינוך דיגיטלי" in formatted
        assert "ציון:" not in formatted  # No scores
        assert "summary-box" not in formatted  # No metadata box

class TestPlainTextFormatting(TestFormatterBot):
    """Test plain text output formatting."""
    
    def test_plain_text_detailed_formatting(self):
        """Test detailed plain text formatting."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_plain_text_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search",
            self.PresentationStyle.DETAILED,
            include_metadata=True,
            evaluation_summary=SAMPLE_EVALUATION
        )
        
        assert "תוצאות חיפוש: החלטות בנושא חינוך" in formatted
        assert "=" * 50 in formatted
        assert "נמצאו 2 תוצאות" in formatted
        assert "1. החלטה בנושא חינוך דיגיטלי" in formatted
        assert "ממשלה 37" in formatted
        assert "איכות התוצאות: 0.87" in formatted

class TestSummaryFormatting(TestFormatterBot):
    """Test summary output formatting."""
    
    def test_summary_single_result(self):
        """Test summary for single result."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_summary_response(
            [SAMPLE_FORMATTED_RESULTS[0]],
            "החלטה 660 ממשלה 37",
            "specific_decision"
        )
        
        assert "נמצאה החלטה:" in formatted
        assert "החלטה בנושא חינוך דיגיטלי" in formatted
        assert "ממשלה 37" in formatted
    
    def test_summary_multiple_results(self):
        """Test summary for multiple results."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_summary_response(
            SAMPLE_FORMATTED_RESULTS,
            "החלטות בנושא חינוך",
            "search"
        )
        
        assert "נמצאו 2 החלטות" in formatted
        assert "החלטות בנושא חינוך" in formatted
        assert "התוצאה הראשונה:" in formatted
        assert "נושאים:" in formatted
    
    def test_summary_count_result(self):
        """Test summary for count query."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_summary_response(
            SAMPLE_COUNT_RESULT,
            "כמה החלטות ממשלה 37",
            "count"
        )
        
        assert "נמצאו 42 החלטות" in formatted
        assert "כמה החלטות ממשלה 37" in formatted
    
    def test_summary_no_results(self):
        """Test summary for no results."""
        if not self.formatter_imported:
            pytest.skip("Formatter module not available")
        
        formatted = self.format_summary_response(
            [],
            "שאילתא ללא תוצאות",
            "search"
        )
        
        assert "לא נמצאו תוצאות" in formatted
        assert "שאילתא ללא תוצאות" in formatted

class TestFormatterAPI:
    """Test formatter API endpoints."""
    
    def test_format_endpoint_markdown(self):
        """Test /format endpoint with Markdown output."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            request_data = {
                "conv_id": "test_formatting",
                "original_query": "החלטות בנושא חינוך",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "ranked_results": SAMPLE_FORMATTED_RESULTS,
                "evaluation_summary": SAMPLE_EVALUATION,
                "ranking_explanation": "דירוג לפי רלוונטיות",
                "output_format": "markdown",
                "presentation_style": "detailed",
                "include_metadata": True,
                "include_scores": True
            }
            
            response = client.post("/format", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["conv_id"] == "test_formatting"
            assert data["format_used"] == "markdown"
            assert data["style_used"] == "detailed"
            assert data["total_results"] == 2
            
            # Check formatted content
            formatted_content = data["formatted_response"]
            assert "# תוצאות חיפוש:" in formatted_content
            assert "החלטה בנושא חינוך דיגיטלי" in formatted_content
            
        except ImportError:
            pytest.skip("Formatter module not available")
    
    def test_format_endpoint_json(self):
        """Test /format endpoint with JSON output."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            request_data = {
                "conv_id": "test_json",
                "original_query": "החלטות בנושא חינוך",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "ranked_results": SAMPLE_FORMATTED_RESULTS,
                "output_format": "json",
                "include_metadata": False,
                "include_scores": False
            }
            
            response = client.post("/format", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["format_used"] == "json"
            
            # Parse the JSON content
            json_content = json.loads(data["formatted_response"])
            assert json_content["query"] == "החלטות בנושא חינוך"
            assert len(json_content["results"]) == 2
            
        except ImportError:
            pytest.skip("Formatter module not available")
    
    def test_formats_endpoint(self):
        """Test /formats endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/formats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "available_formats" in data
            assert "available_styles" in data
            assert "markdown" in data["available_formats"]
            assert "json" in data["available_formats"]
            assert "html" in data["available_formats"]
            assert "plain_text" in data["available_formats"]
            assert "summary" in data["available_formats"]
            
            assert "detailed" in data["available_styles"]
            assert "compact" in data["available_styles"]
            
        except ImportError:
            pytest.skip("Formatter module not available")
    
    def test_health_endpoint(self):
        """Test /health endpoint."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "MAIN_FORMATTER_4" in data["service"]
            
        except ImportError:
            pytest.skip("Formatter module not available")

class TestIntegrationScenarios:
    """Test end-to-end formatting scenarios."""
    
    def test_full_search_formatting_flow(self):
        """Test complete search result formatting."""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from MAIN_FORMATTER_4.main import (
                format_markdown_response,
                PresentationStyle
            )
            
            # Test with comprehensive data
            formatted = format_markdown_response(
                SAMPLE_FORMATTED_RESULTS,
                "החלטות ממשלה 37 בנושא חינוך דיגיטלי",
                "search",
                PresentationStyle.DETAILED,
                include_metadata=True,
                include_scores=True,
                evaluation_summary=SAMPLE_EVALUATION,
                ranking_explanation="דירוג היברידי עם 5 גורמים"
            )
            
            # Validate comprehensive formatting
            assert "# תוצאות חיפוש:" in formatted
            assert "דירוג היברידי עם 5 גורמים" in formatted
            assert "איכות התוצאות: 0.87 (highly_relevant)" in formatted
            assert "## 1. החלטה בנושא חינוך דיגיטלי" in formatted
            assert "ציון: 0.95 (דירוג היברידי)" in formatted
            assert "500 מיליון שקל" in formatted  # Content included
            
        except ImportError:
            pytest.skip("Formatter module not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])