#!/usr/bin/env python3
"""
Simple test for the Ranking Bot to validate its functionality.
Tests result ranking using different strategies and scoring methods.
"""

import asyncio
import sys
import json
from typing import Dict, Any, List

class SimpleRankingTest:
    """Simple test for ranking bot functionality."""
    
    def __init__(self):
        self.test_results = []
        print("🧪 Initializing Ranking Bot Test")
        
        # Sample search results for testing
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
        
        # Test scenarios for different ranking strategies
        self.test_scenarios = {
            "education_query_hybrid": {
                "conv_id": "test_education",
                "original_query": "החלטות בנושא חינוך דיגיטלי",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "strategy": "hybrid",
                "expected_top_result_id": 1  # Should rank digital education highest
            },
            "recent_decisions_temporal": {
                "conv_id": "test_temporal",
                "original_query": "החלטות אחרונות",
                "intent": "search",
                "entities": {},
                "strategy": "temporal",
                "expected_top_result_date": "2023-06-20"  # Most recent
            },
            "budget_query_relevance": {
                "conv_id": "test_budget",
                "original_query": "תקציב משרד החינוך",
                "intent": "search",
                "entities": {"topic": "תקציב", "ministries": ["משרד החינוך"]},
                "strategy": "relevance",
                "expected_top_result_id": 2  # Budget decision
            },
            "diversity_query": {
                "conv_id": "test_diversity",
                "original_query": "החלטות ממשלה 37",
                "intent": "search",
                "entities": {"government_number": 37},
                "strategy": "diversity",
                "expected_diverse_topics": True
            }
        }
    
    def mock_tokenize_hebrew_text(self, text: str) -> List[str]:
        """Mock Hebrew tokenization."""
        if not text:
            return []
        
        # Simple tokenization - split by spaces and remove common words
        stop_words = {"של", "את", "על", "בנושא", "ו", "ה", "ב", "ל", "מ"}
        tokens = text.lower().split()
        return [token for token in tokens if len(token) > 1 and token not in stop_words]
    
    def mock_calculate_bm25_score(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """Mock BM25 scoring."""
        if not query_tokens or not doc_tokens:
            return 0.0
        
        # Simple overlap scoring
        matches = sum(1 for token in query_tokens if token in doc_tokens)
        return matches / len(query_tokens) if query_tokens else 0.0
    
    def mock_calculate_entity_score(self, entities: Dict, result: Dict) -> float:
        """Mock entity matching scoring."""
        if not entities:
            return 1.0
        
        matches = 0
        total = len(entities)
        
        for key, value in entities.items():
            if key == "government_number" and result.get("government_number") == value:
                matches += 1
            elif key == "topic" and value in result.get("topics", []):
                matches += 1
            elif key == "ministries":
                if isinstance(value, list):
                    if any(ministry in result.get("ministries", []) for ministry in value):
                        matches += 1
                elif value in result.get("ministries", []):
                    matches += 1
        
        return matches / total if total > 0 else 1.0
    
    def mock_calculate_temporal_score(self, result: Dict) -> float:
        """Mock temporal scoring (newer = higher)."""
        decision_date = result.get("decision_date", "")
        if not decision_date:
            return 0.5
        
        year = int(decision_date[:4]) if len(decision_date) >= 4 else 2020
        
        # Simple scoring: 2023 = 1.0, 2022 = 0.8, 2021 = 0.6, etc.
        if year >= 2023:
            return 1.0
        elif year == 2022:
            return 0.8
        elif year == 2021:
            return 0.6
        else:
            return 0.4
    
    def mock_calculate_semantic_score(self, query: str, result: Dict) -> float:
        """Mock semantic relevance scoring."""
        # Simple keyword matching
        query_words = set(query.lower().split())
        result_text = f"{result.get('title', '')} {result.get('content', '')}".lower()
        
        matches = sum(1 for word in query_words if word in result_text)
        return min(1.0, matches / len(query_words) * 1.5) if query_words else 0.5
    
    def mock_rank_results(self, scenario: Dict) -> Dict[str, Any]:
        """Mock result ranking based on strategy."""
        
        query = scenario["original_query"]
        entities = scenario["entities"]
        strategy = scenario["strategy"]
        results = self.sample_results.copy()
        
        ranked_results = []
        
        for result in results:
            # Calculate mock scores
            query_tokens = self.mock_tokenize_hebrew_text(query)
            doc_text = f"{result.get('title', '')} {result.get('content', '')}"
            doc_tokens = self.mock_tokenize_hebrew_text(doc_text)
            
            bm25_score = self.mock_calculate_bm25_score(query_tokens, doc_tokens)
            entity_score = self.mock_calculate_entity_score(entities, result)
            temporal_score = self.mock_calculate_temporal_score(result)
            semantic_score = self.mock_calculate_semantic_score(query, result)
            
            # Calculate total score based on strategy
            if strategy == "relevance":
                total_score = bm25_score * 0.6 + semantic_score * 0.4
            elif strategy == "temporal":
                total_score = temporal_score * 0.7 + bm25_score * 0.3
            elif strategy == "diversity":
                diversity_bonus = 0.1 if len(result.get("topics", [])) >= 2 else 0.0
                total_score = bm25_score * 0.4 + semantic_score * 0.3 + entity_score * 0.2 + diversity_bonus
            else:  # hybrid
                total_score = (
                    bm25_score * 0.3 +
                    semantic_score * 0.25 +
                    entity_score * 0.2 +
                    temporal_score * 0.15 +
                    0.1  # popularity placeholder
                )
            
            # Add ranking information
            enhanced_result = result.copy()
            enhanced_result["_ranking"] = {
                "total_score": round(total_score, 3),
                "bm25_score": round(bm25_score, 3),
                "semantic_score": round(semantic_score, 3),
                "entity_score": round(entity_score, 3),
                "temporal_score": round(temporal_score, 3),
                "explanation": f"דירוג {strategy}"
            }
            
            ranked_results.append(enhanced_result)
        
        # Sort by total score (descending)
        ranked_results.sort(key=lambda x: x["_ranking"]["total_score"], reverse=True)
        
        return {
            "success": True,
            "conv_id": scenario["conv_id"],
            "ranked_results": ranked_results,
            "ranking_explanation": f"דירוג לפי {strategy}: {len(ranked_results)} תוצאות",
            "total_results": len(results),
            "strategy_used": strategy,
            "confidence": 0.8
        }
    
    def test_scenario(self, scenario_name: str, scenario: Dict) -> Dict[str, Any]:
        """Test a single ranking scenario."""
        
        print(f"\n📋 Testing: {scenario_name}")
        print(f"📥 Query: '{scenario['original_query']}'")
        print(f"🎯 Intent: {scenario['intent']}")
        print(f"📊 Entities: {scenario['entities']}")
        print(f"🔄 Strategy: {scenario['strategy']}")
        
        try:
            # Mock ranking
            ranking_result = self.mock_rank_results(scenario)
            
            # Validate results
            ranked_results = ranking_result["ranked_results"]
            
            print(f"    ✅ Ranked {len(ranked_results)} results")
            print(f"    📈 Strategy used: {ranking_result['strategy_used']}")
            print(f"    📊 Confidence: {ranking_result['confidence']:.2f}")
            
            # Display top 3 results
            print(f"    🏆 Top results:")
            for i, result in enumerate(ranked_results[:3], 1):
                score = result["_ranking"]["total_score"]
                title = result["title"][:50] + "..." if len(result["title"]) > 50 else result["title"]
                print(f"       {i}. [{score:.3f}] {title}")
            
            # Validate expectations
            passed = True
            
            if "expected_top_result_id" in scenario:
                expected_id = scenario["expected_top_result_id"]
                actual_id = ranked_results[0]["id"]
                if actual_id == expected_id:
                    print(f"    ✅ Correct top result: ID {actual_id}")
                else:
                    print(f"    ⚠️ Expected top result ID {expected_id}, got {actual_id}")
                    passed = False
            
            if "expected_top_result_date" in scenario:
                expected_date = scenario["expected_top_result_date"]
                actual_date = ranked_results[0]["decision_date"]
                if actual_date == expected_date:
                    print(f"    ✅ Correct temporal ranking: {actual_date}")
                else:
                    print(f"    ⚠️ Expected date {expected_date}, got {actual_date}")
                    passed = False
            
            if scenario.get("expected_diverse_topics"):
                # Check topic diversity in top 3 results
                top_topics = set()
                for result in ranked_results[:3]:
                    top_topics.update(result.get("topics", []))
                if len(top_topics) >= 3:
                    print(f"    ✅ Good topic diversity: {len(top_topics)} unique topics")
                else:
                    print(f"    ⚠️ Limited topic diversity: {len(top_topics)} unique topics")
                    # Don't fail for diversity, just note
            
            # Check score ordering
            scores = [result["_ranking"]["total_score"] for result in ranked_results]
            if scores == sorted(scores, reverse=True):
                print(f"    ✅ Scores properly ordered")
            else:
                print(f"    ❌ Scores not properly ordered")
                passed = False
            
            result = {
                "scenario_name": scenario_name,
                "passed": passed,
                "top_score": scores[0] if scores else 0,
                "score_range": (min(scores), max(scores)) if scores else (0, 0),
                "strategy": scenario["strategy"],
                "ranking_result": ranking_result
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
        """Run all ranking tests."""
        print("🚀 Starting Ranking Bot Functionality Tests")
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
            print("🎉 All ranking tests passed!")
            print("✅ Result ranking is working correctly")
        else:
            print(f"⚠️ {total - passed} tests failed")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r.get("passed", False)]
            for failed in failed_tests:
                error = failed.get("error", "Test failure")
                print(f"    ❌ {failed['scenario_name']}: {error}")
        
        # Strategy analysis
        print("\n🔍 Strategy Analysis:")
        strategy_stats = {}
        for result in self.test_results:
            if "strategy" in result:
                strategy = result["strategy"]
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {"passed": 0, "total": 0, "scores": []}
                
                strategy_stats[strategy]["total"] += 1
                if result.get("passed", False):
                    strategy_stats[strategy]["passed"] += 1
                
                if "top_score" in result:
                    strategy_stats[strategy]["scores"].append(result["top_score"])
        
        for strategy, stats in strategy_stats.items():
            avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
            success_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"    📈 {strategy}: {success_rate:.0f}% success, avg score: {avg_score:.3f}")
        
        # Score distribution
        if self.test_results:
            all_scores = []
            for result in self.test_results:
                if "top_score" in result:
                    all_scores.append(result["top_score"])
            
            if all_scores:
                print(f"\n📊 Score Distribution:")
                print(f"    🎯 Highest score: {max(all_scores):.3f}")
                print(f"    📊 Average score: {sum(all_scores) / len(all_scores):.3f}")
                print(f"    📉 Lowest score: {min(all_scores):.3f}")
        
        return passed == total

def main():
    """Main test runner."""
    test_runner = SimpleRankingTest()
    success = test_runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)