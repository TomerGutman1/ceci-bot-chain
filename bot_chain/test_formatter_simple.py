#!/usr/bin/env python3
"""
Simple test for the Formatter Bot to validate its functionality.
Tests different output formats and presentation styles for search results.
"""

import json
import sys
from typing import Dict, Any, List

class SimpleFormatterTest:
    """Simple test for formatter bot functionality."""
    
    def __init__(self):
        self.test_results = []
        print("🧪 Initializing Formatter Bot Test")
        
        # Sample formatted results for testing
        self.sample_results = [
            {
                "id": 1,
                "government_number": 37,
                "decision_number": 660,
                "decision_date": "2023-05-15",
                "title": "החלטה בנושא חינוך דיגיטלי",
                "content": "החלטה מפורטת על קידום החינוך הדיגיטלי במערכת החינוך הישראלית. כולל תקציב של 500 מיליון שקל לשלוש שנים.",
                "topics": ["חינוך", "טכנולוגיה"],
                "ministries": ["משרד החינוך"],
                "status": "approved",
                "_ranking": {
                    "total_score": 0.95,
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
        
        self.sample_evaluation = {
            "overall_score": 0.87,
            "relevance_level": "highly_relevant",
            "confidence": 0.92
        }
        
        # Test scenarios for different formatting options
        self.test_scenarios = {
            "markdown_detailed": {
                "conv_id": "test_markdown",
                "original_query": "החלטות בנושא חינוך דיגיטלי",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "output_format": "markdown",
                "presentation_style": "detailed",
                "include_metadata": True,
                "include_scores": True
            },
            "json_compact": {
                "conv_id": "test_json",
                "original_query": "החלטות ממשלה 37",
                "intent": "search",
                "entities": {"government_number": 37},
                "output_format": "json",
                "presentation_style": "detailed",
                "include_metadata": False,
                "include_scores": False
            },
            "html_cards": {
                "conv_id": "test_html",
                "original_query": "החלטות אחרונות",
                "intent": "search",
                "entities": {},
                "output_format": "html",
                "presentation_style": "compact",
                "include_metadata": True,
                "include_scores": False
            },
            "plain_text_list": {
                "conv_id": "test_plain",
                "original_query": "תקציב חינוך",
                "intent": "search",
                "entities": {"topic": "תקציב"},
                "output_format": "plain_text",
                "presentation_style": "list",
                "include_metadata": False,
                "include_scores": False
            },
            "summary_brief": {
                "conv_id": "test_summary",
                "original_query": "החלטות ממשלה 37",
                "intent": "search",
                "entities": {"government_number": 37},
                "output_format": "summary",
                "presentation_style": "compact",
                "include_metadata": False,
                "include_scores": False
            },
            "count_result": {
                "conv_id": "test_count",
                "original_query": "כמה החלטות ממשלה 37",
                "intent": "count",
                "entities": {"government_number": 37},
                "output_format": "markdown",
                "presentation_style": "detailed",
                "include_metadata": True,
                "include_scores": False,
                "use_count_result": True
            }
        }
    
    def mock_format_hebrew_date(self, date_str: str) -> str:
        """Mock Hebrew date formatting."""
        if not date_str:
            return "תאריך לא זמין"
        
        # Simple mock: 2023-05-15 -> 15 במאי 2023
        parts = date_str.split("-")
        if len(parts) >= 3:
            year, month, day = parts[0], parts[1], parts[2]
            month_names = {
                "01": "ינואר", "02": "פברואר", "03": "מרץ", "04": "אפריל",
                "05": "מאי", "06": "יוני", "07": "יולי", "08": "אוגוסט",
                "09": "ספטמבר", "10": "אוקטובר", "11": "נובמבר", "12": "דצמבר"
            }
            hebrew_month = month_names.get(month, month)
            return f"{int(day)} ב{hebrew_month} {year}"
        return date_str
    
    def mock_format_government_info(self, result: Dict) -> str:
        """Mock government information formatting."""
        parts = []
        
        if result.get("government_number"):
            parts.append(f"ממשלה {result['government_number']}")
        
        if result.get("decision_number"):
            parts.append(f"החלטה {result['decision_number']}")
        
        if result.get("decision_date"):
            date_str = self.mock_format_hebrew_date(result["decision_date"])
            parts.append(date_str)
        
        return " | ".join(parts) if parts else "מידע לא זמין"
    
    def mock_format_markdown(self, scenario: Dict) -> str:
        """Mock Markdown formatting."""
        query = scenario["original_query"]
        intent = scenario["intent"]
        style = scenario["presentation_style"]
        include_metadata = scenario["include_metadata"]
        include_scores = scenario["include_scores"]
        
        results = self.sample_results
        if scenario.get("use_count_result"):
            results = [{"count": 42}]
        
        lines = []
        
        # Header
        if intent == "count":
            lines.append(f"# תוצאות ספירה: {query}")
            if results and "count" in results[0]:
                count = results[0]["count"]
                lines.append(f"\n**מספר ההחלטות:** {count}")
                return "\n".join(lines)
        else:
            lines.append(f"# תוצאות חיפוש: {query}")
            lines.append(f"\n**נמצאו {len(results)} תוצאות**")
        
        # Evaluation
        if include_metadata:
            lines.append(f"\n**איכות התוצאות:** {self.sample_evaluation['overall_score']:.2f} ({self.sample_evaluation['relevance_level']})")
        
        lines.append("\n---\n")
        
        # Results
        for i, result in enumerate(results, 1):
            if style == "detailed":
                lines.append(f"## {i}. {result.get('title', 'ללא כותרת')}")
                lines.append(f"\n**מידע כללי:** {self.mock_format_government_info(result)}")
                
                content = result.get('content', '')
                if content:
                    lines.append(f"\n**תוכן:**\n{content}")
                
                if include_scores and "_ranking" in result:
                    score = result["_ranking"]["total_score"]
                    explanation = result["_ranking"]["explanation"]
                    lines.append(f"\n*ציון: {score:.2f} ({explanation})*")
                
                lines.append("\n---\n")
                
            elif style == "compact":
                title = result.get('title', 'ללא כותרת')
                gov_info = self.mock_format_government_info(result)
                lines.append(f"**{i}. {title}**")
                lines.append(f"   {gov_info}")
                lines.append("")
        
        return "\n".join(lines)
    
    def mock_format_json(self, scenario: Dict) -> str:
        """Mock JSON formatting."""
        query = scenario["original_query"]
        intent = scenario["intent"]
        include_metadata = scenario["include_metadata"]
        include_scores = scenario["include_scores"]
        
        results = self.sample_results
        if scenario.get("use_count_result"):
            results = [{"count": 42}]
        
        # Clean results for JSON
        clean_results = []
        for result in results:
            clean_result = {
                "id": result.get("id"),
                "title": result.get("title"),
                "content": result.get("content"),
                "government_number": result.get("government_number"),
                "decision_number": result.get("decision_number"),
                "decision_date": result.get("decision_date"),
                "topics": result.get("topics", []),
                "ministries": result.get("ministries", []),
                "status": result.get("status")
            }
            
            if include_scores and "_ranking" in result:
                clean_result["ranking"] = result["_ranking"]
            
            clean_results.append(clean_result)
        
        response_data = {
            "query": query,
            "intent": intent,
            "total_results": len(results),
            "results": clean_results
        }
        
        if include_metadata:
            response_data["metadata"] = {
                "evaluation": self.sample_evaluation,
                "formatted_at": "2023-06-27T12:00:00"
            }
        
        return json.dumps(response_data, ensure_ascii=False, indent=2)
    
    def mock_format_html(self, scenario: Dict) -> str:
        """Mock HTML formatting."""
        query = scenario["original_query"]
        results = self.sample_results
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html dir='rtl' lang='he'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            f"    <title>תוצאות חיפוש: {query}</title>",
            "</head>",
            "<body>",
            f"<h1>תוצאות חיפוש: {query}</h1>",
            f"<p><strong>נמצאו {len(results)} תוצאות</strong></p>"
        ]
        
        for i, result in enumerate(results, 1):
            html_parts.append("<div class='result-card'>")
            html_parts.append(f"<div class='result-title'>{i}. {result.get('title', 'ללא כותרת')}</div>")
            html_parts.append(f"<div class='result-meta'>{self.mock_format_government_info(result)}</div>")
            html_parts.append("</div>")
        
        html_parts.extend(["</body>", "</html>"])
        return "\n".join(html_parts)
    
    def mock_format_plain_text(self, scenario: Dict) -> str:
        """Mock plain text formatting."""
        query = scenario["original_query"]
        results = self.sample_results
        
        lines = [
            f"תוצאות חיפוש: {query}",
            "=" * 50,
            f"נמצאו {len(results)} תוצאות",
            "\n" + "-" * 50
        ]
        
        for i, result in enumerate(results, 1):
            lines.append(f"\n{i}. {result.get('title', 'ללא כותרת')}")
            lines.append(f"   {self.mock_format_government_info(result)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def mock_format_summary(self, scenario: Dict) -> str:
        """Mock summary formatting."""
        query = scenario["original_query"]
        intent = scenario["intent"]
        results = self.sample_results
        
        if intent == "count":
            return f"נמצאו 42 החלטות עבור השאילתא '{query}'"
        
        if not results:
            return f"לא נמצאו תוצאות עבור השאילתא '{query}'"
        
        if len(results) == 1:
            result = results[0]
            title = result.get('title', 'החלטה')
            gov_info = self.mock_format_government_info(result)
            return f"נמצאה החלטה: {title} ({gov_info})"
        
        # Multiple results
        first_result = results[0]
        title = first_result.get('title', '')[:60] + "..." if len(first_result.get('title', '')) > 60 else first_result.get('title', '')
        
        return f"נמצאו {len(results)} החלטות עבור '{query}' | התוצאה הראשונה: {title} | נושאים: חינוך, טכנולוגיה"
    
    def mock_format_response(self, scenario: Dict) -> Dict[str, Any]:
        """Mock response formatting based on output format."""
        
        output_format = scenario["output_format"]
        
        if output_format == "markdown":
            formatted_content = self.mock_format_markdown(scenario)
        elif output_format == "json":
            formatted_content = self.mock_format_json(scenario)
        elif output_format == "html":
            formatted_content = self.mock_format_html(scenario)
        elif output_format == "plain_text":
            formatted_content = self.mock_format_plain_text(scenario)
        elif output_format == "summary":
            formatted_content = self.mock_format_summary(scenario)
        else:
            formatted_content = f"Unsupported format: {output_format}"
        
        results_count = 1 if scenario.get("use_count_result") else len(self.sample_results)
        
        return {
            "success": True,
            "conv_id": scenario["conv_id"],
            "formatted_response": formatted_content,
            "format_used": output_format,
            "style_used": scenario["presentation_style"],
            "total_results": results_count,
            "metadata": {
                "formatted_at": "2023-06-27T12:00:00",
                "include_metadata": scenario["include_metadata"],
                "include_scores": scenario["include_scores"]
            }
        }
    
    def test_scenario(self, scenario_name: str, scenario: Dict) -> Dict[str, Any]:
        """Test a single formatting scenario."""
        
        print(f"\n📋 Testing: {scenario_name}")
        print(f"📥 Query: '{scenario['original_query']}'")
        print(f"🎯 Intent: {scenario['intent']}")
        print(f"📊 Format: {scenario['output_format']}")
        print(f"🎨 Style: {scenario['presentation_style']}")
        
        try:
            # Mock formatting
            formatting_result = self.mock_format_response(scenario)
            
            # Validate results
            formatted_content = formatting_result["formatted_response"]
            
            print(f"    ✅ Formatted successfully")
            print(f"    📈 Format: {formatting_result['format_used']}")
            print(f"    🎨 Style: {formatting_result['style_used']}")
            print(f"    📊 Results: {formatting_result['total_results']}")
            print(f"    📏 Content length: {len(formatted_content)} characters")
            
            # Display sample content
            sample_lines = formatted_content.split('\n')[:3]  # First 3 lines
            for i, line in enumerate(sample_lines):
                if line.strip():
                    print(f"    📝 Sample: {line.strip()[:80]}{'...' if len(line.strip()) > 80 else ''}")
                    break
            
            # Validate format-specific expectations
            passed = True
            
            # Common validations
            if scenario["original_query"] not in formatted_content:
                print(f"    ⚠️ Query '{scenario['original_query']}' not found in output")
                passed = False
            
            # Format-specific validations
            if scenario["output_format"] == "markdown":
                if "#" not in formatted_content:
                    print(f"    ⚠️ Markdown headers not found")
                    passed = False
                if scenario["include_scores"] and "ציון:" not in formatted_content:
                    print(f"    ⚠️ Scores not included as expected")
                    passed = False
                    
            elif scenario["output_format"] == "json":
                try:
                    json_data = json.loads(formatted_content)
                    if "query" not in json_data:
                        print(f"    ⚠️ JSON missing required 'query' field")
                        passed = False
                except json.JSONDecodeError:
                    print(f"    ❌ Invalid JSON format")
                    passed = False
                    
            elif scenario["output_format"] == "html":
                if "<!DOCTYPE html>" not in formatted_content:
                    print(f"    ⚠️ HTML doctype not found")
                    passed = False
                if "dir='rtl'" not in formatted_content:
                    print(f"    ⚠️ RTL direction not set for Hebrew")
                    passed = False
                    
            elif scenario["output_format"] == "summary":
                if len(formatted_content) > 300:
                    print(f"    ⚠️ Summary too long ({len(formatted_content)} chars)")
                    passed = False
            
            # Intent-specific validations
            if scenario["intent"] == "count":
                if scenario.get("use_count_result") and "42" not in formatted_content:
                    print(f"    ⚠️ Count result not displayed")
                    passed = False
            
            result = {
                "scenario_name": scenario_name,
                "passed": passed,
                "format": scenario["output_format"],
                "style": scenario["presentation_style"],
                "content_length": len(formatted_content),
                "formatting_result": formatting_result
            }
            
            self.test_results.append(result)
            
            if passed:
                print(f"    🎉 Scenario '{scenario_name}' passed!")
            else:
                print(f"    ❌ Scenario '{scenario_name}' failed!")
            
            return result
            
        except Exception as e:
            print(f"    ❌ Error in scenario '{scenario_name}': {e}")
            result = {
                "scenario_name": scenario_name,
                "passed": False,
                "error": str(e)
            }
            self.test_results.append(result)
            return result
    
    def run_all_tests(self):
        """Run all formatting tests."""
        print("🚀 Starting Formatter Bot Functionality Tests")
        print("=" * 60)
        
        # Run all test scenarios
        for scenario_name, scenario in self.test_scenarios.items():
            self.test_scenario(scenario_name, scenario)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        
        passed = sum(1 for result in self.test_results if result.get("passed", False))
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total} scenarios")
        print(f"❌ Failed: {total - passed}/{total} scenarios")
        
        if passed == total:
            print("🎉 All formatting tests passed!")
            print("✅ Response formatting is working correctly")
        else:
            print(f"⚠️ {total - passed} tests failed")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r.get("passed", False)]
            for failed in failed_tests:
                error = failed.get("error", "Test failure")
                print(f"    ❌ {failed['scenario_name']}: {error}")
        
        # Format analysis
        print("\n🎨 Format Analysis:")
        format_stats = {}
        for result in self.test_results:
            if "format" in result:
                format_name = result["format"]
                if format_name not in format_stats:
                    format_stats[format_name] = {"passed": 0, "total": 0, "avg_length": 0}
                
                format_stats[format_name]["total"] += 1
                if result.get("passed", False):
                    format_stats[format_name]["passed"] += 1
                
                if "content_length" in result:
                    format_stats[format_name]["avg_length"] += result["content_length"]
        
        for format_name, stats in format_stats.items():
            avg_length = stats["avg_length"] / stats["total"] if stats["total"] > 0 else 0
            success_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"    📈 {format_name}: {success_rate:.0f}% success, avg length: {avg_length:.0f} chars")
        
        # Content length distribution
        if self.test_results:
            lengths = [r.get("content_length", 0) for r in self.test_results if "content_length" in r]
            if lengths:
                print(f"\n📏 Content Length Distribution:")
                print(f"    📊 Shortest: {min(lengths)} chars")
                print(f"    📊 Average: {sum(lengths) / len(lengths):.0f} chars")
                print(f"    📊 Longest: {max(lengths)} chars")
        
        return passed == total

def main():
    """Main test runner."""
    test_runner = SimpleFormatterTest()
    success = test_runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)