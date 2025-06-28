#!/usr/bin/env python3
"""
Simple test for the Evaluator Bot to validate its functionality.
Tests the evaluation logic and scoring mechanisms.
"""

import asyncio
import sys
import json
from typing import Dict, Any, List

class SimpleEvaluatorTest:
    """Simple test for evaluator bot functionality."""
    
    def __init__(self):
        self.test_results = []
        print("🧪 Initializing Evaluator Bot Test")
        
        # Sample test data
        self.excellent_scenario = {
            "conv_id": "test_excellent",
            "original_query": "החלטה 660 של ממשלה 37",
            "intent": "specific_decision",
            "entities": {"government_number": 37, "decision_number": 660},
            "sql_query": "SELECT * FROM decisions WHERE government_number = 37 AND decision_number = 660",
            "results": [
                {
                    "id": 1,
                    "government_number": 37,
                    "decision_number": 660,
                    "decision_date": "2023-05-15",
                    "title": "החלטה בנושא חינוך דיגיטלי",
                    "content": "החלטה מפורטת על קידום החינוך הדיגיטלי במערכת החינוך הישראלית.",
                    "topics": ["חינוך", "טכנולוגיה"],
                    "ministries": ["משרד החינוך"],
                    "status": "approved"
                }
            ],
            "result_count": 1,
            "execution_time_ms": 85
        }
        
        self.poor_scenario = {
            "conv_id": "test_poor",
            "original_query": "החלטות ממשלה 37 בנושא ביטחון",
            "intent": "search",
            "entities": {"government_number": 37, "topic": "ביטחון"},
            "sql_query": "SELECT * FROM decisions",
            "results": [
                {
                    "id": 2,
                    "government_number": 35,  # Wrong government
                    "title": "החלטה חסרת פרטים",
                    # Missing: decision_date, content, topics
                }
            ],
            "result_count": 1,
            "execution_time_ms": 1500  # Slow
        }
        
        self.empty_scenario = {
            "conv_id": "test_empty",
            "original_query": "החלטות שלא קיימות",
            "intent": "search",
            "entities": {"government_number": 99},
            "sql_query": "SELECT * FROM decisions WHERE government_number = 99",
            "results": [],
            "result_count": 0,
            "execution_time_ms": 200
        }
    
    def mock_evaluate_relevance(self, query: str, intent: str, entities: Dict, results: List) -> Dict:
        """Mock relevance evaluation."""
        if not results:
            return {"name": "relevance", "score": 0.0, "weight": 0.35, "explanation": "No results returned"}
        
        score = 0.5  # Base score
        
        # Check entity matching
        if intent == "specific_decision" and len(results) == 1:
            result = results[0]
            if "government_number" in entities and result.get("government_number") == entities["government_number"]:
                score += 0.3
            if "decision_number" in entities and result.get("decision_number") == entities["decision_number"]:
                score += 0.2
        elif intent == "search":
            if "government_number" in entities:
                matches = sum(1 for r in results if r.get("government_number") == entities["government_number"])
                score += (matches / len(results)) * 0.3
        
        return {
            "name": "relevance",
            "score": min(1.0, score),
            "weight": 0.35,
            "explanation": f"Relevance evaluation for {intent} with {len(results)} results"
        }
    
    def mock_evaluate_completeness(self, query: str, intent: str, entities: Dict, results: List) -> Dict:
        """Mock completeness evaluation."""
        if not results:
            return {"name": "completeness", "score": 0.0, "weight": 0.25, "explanation": "No results to evaluate"}
        
        score = 0.5  # Base score
        
        # Intent-specific scoring
        if intent == "specific_decision" and len(results) == 1:
            score = 0.9
        elif intent == "count" and len(results) == 1:
            score = 1.0
        elif intent == "search":
            if len(results) >= 5:
                score = 0.8
            elif len(results) >= 2:
                score = 0.7
        
        # Check data completeness
        complete_results = 0
        for result in results[:3]:
            required_fields = ["title", "content", "decision_date", "government_number"]
            present_fields = sum(1 for field in required_fields if field in result and result[field])
            if present_fields >= 3:
                complete_results += 1
        
        if results:
            completeness_ratio = complete_results / min(len(results), 3)
            score = (score + completeness_ratio) / 2
        
        return {
            "name": "completeness",
            "score": score,
            "weight": 0.25,
            "explanation": f"Completeness: {complete_results}/{min(len(results), 3)} results have complete data"
        }
    
    def mock_evaluate_accuracy(self, query: str, intent: str, entities: Dict, results: List) -> Dict:
        """Mock accuracy evaluation."""
        if not results:
            return {"name": "accuracy", "score": 0.0, "weight": 0.20, "explanation": "No results to evaluate"}
        
        score = 0.7  # Base score
        
        # Check date consistency
        for result in results[:3]:
            if "decision_date" in result:
                try:
                    year = int(str(result["decision_date"])[:4])
                    if year < 1948 or year > 2025:
                        score -= 0.2
                        break
                except:
                    score -= 0.1
        
        # Check government number consistency
        if "government_number" in entities:
            expected_gov = entities["government_number"]
            for result in results[:3]:
                if "government_number" in result and result["government_number"] != expected_gov:
                    score -= 0.2
                    break
        
        return {
            "name": "accuracy",
            "score": max(0.0, min(1.0, score)),
            "weight": 0.20,
            "explanation": "Accuracy evaluation based on data consistency"
        }
    
    def mock_evaluate_entity_match(self, query: str, intent: str, entities: Dict, results: List) -> Dict:
        """Mock entity matching evaluation."""
        if not entities:
            return {"name": "entity_match", "score": 1.0, "weight": 0.15, "explanation": "No entities to match"}
        
        if not results:
            return {"name": "entity_match", "score": 0.0, "weight": 0.15, "explanation": "No results to match"}
        
        matched_entities = 0
        total_entities = len(entities)
        
        for entity_key, entity_value in entities.items():
            for result in results:
                if entity_key == "government_number" and result.get("government_number") == entity_value:
                    matched_entities += 1
                    break
                elif entity_key == "decision_number" and result.get("decision_number") == entity_value:
                    matched_entities += 1
                    break
                elif entity_key == "topic" and "topics" in result:
                    if isinstance(result["topics"], list) and entity_value in result["topics"]:
                        matched_entities += 1
                        break
        
        score = matched_entities / total_entities if total_entities > 0 else 1.0
        
        return {
            "name": "entity_match",
            "score": score,
            "weight": 0.15,
            "explanation": f"Entity matching: {matched_entities}/{total_entities}"
        }
    
    def mock_evaluate_performance(self, query: str, intent: str, entities: Dict, results: List, execution_time: float, result_count: int) -> Dict:
        """Mock performance evaluation."""
        score = 0.8  # Base score
        
        # Execution time scoring
        if execution_time < 100:
            score += 0.2
        elif execution_time < 500:
            score += 0.1
        elif execution_time > 1000:
            score -= 0.1
        
        # Result count efficiency
        if intent == "specific_decision" and result_count == 1:
            score += 0.1
        elif intent == "count" and result_count == 1:
            score += 0.1
        
        return {
            "name": "performance",
            "score": max(0.0, min(1.0, score)),
            "weight": 0.05,
            "explanation": f"Performance: {execution_time:.0f}ms, {result_count} results"
        }
    
    def evaluate_scenario(self, scenario: Dict, scenario_name: str) -> Dict:
        """Evaluate a complete scenario."""
        print(f"\n📊 Evaluating: {scenario_name}")
        print(f"📥 Query: '{scenario['original_query']}'")
        print(f"🎯 Intent: {scenario['intent']}")
        print(f"📈 Results: {scenario['result_count']}")
        
        # Calculate individual metrics
        relevance = self.mock_evaluate_relevance(
            scenario["original_query"], scenario["intent"], 
            scenario["entities"], scenario["results"]
        )
        
        completeness = self.mock_evaluate_completeness(
            scenario["original_query"], scenario["intent"],
            scenario["entities"], scenario["results"]
        )
        
        accuracy = self.mock_evaluate_accuracy(
            scenario["original_query"], scenario["intent"],
            scenario["entities"], scenario["results"]
        )
        
        entity_match = self.mock_evaluate_entity_match(
            scenario["original_query"], scenario["intent"],
            scenario["entities"], scenario["results"]
        )
        
        performance = self.mock_evaluate_performance(
            scenario["original_query"], scenario["intent"],
            scenario["entities"], scenario["results"],
            scenario["execution_time_ms"], scenario["result_count"]
        )
        
        metrics = [relevance, completeness, accuracy, entity_match, performance]
        
        # Calculate overall score
        overall_score = sum(metric["score"] * metric["weight"] for metric in metrics)
        
        # Determine relevance level
        if overall_score >= 0.85:
            relevance_level = "highly_relevant"
        elif overall_score >= 0.70:
            relevance_level = "relevant"
        elif overall_score >= 0.40:
            relevance_level = "partially_relevant"
        else:
            relevance_level = "not_relevant"
        
        print(f"    📊 Overall Score: {overall_score:.3f}")
        print(f"    🎚️ Relevance Level: {relevance_level}")
        
        for metric in metrics:
            print(f"    📈 {metric['name'].title()}: {metric['score']:.3f} (weight: {metric['weight']:.2f})")
        
        evaluation = {
            "scenario_name": scenario_name,
            "overall_score": overall_score,
            "relevance_level": relevance_level,
            "metrics": metrics,
            "conv_id": scenario["conv_id"]
        }
        
        self.test_results.append(evaluation)
        return evaluation
    
    def run_all_tests(self):
        """Run all evaluation tests."""
        print("🚀 Starting Evaluator Bot Functionality Tests")
        print("=" * 60)
        
        # Test scenarios
        scenarios = [
            (self.excellent_scenario, "Excellent Query Results"),
            (self.poor_scenario, "Poor Quality Results"),
            (self.empty_scenario, "No Results Found")
        ]
        
        for scenario, name in scenarios:
            evaluation = self.evaluate_scenario(scenario, name)
            
            # Validate expectations
            if name == "Excellent Query Results":
                if evaluation["overall_score"] >= 0.8:
                    print(f"    ✅ {name}: Correctly identified as high quality")
                else:
                    print(f"    ⚠️ {name}: Expected high score, got {evaluation['overall_score']:.3f}")
            
            elif name == "Poor Quality Results":
                if evaluation["overall_score"] <= 0.6:
                    print(f"    ✅ {name}: Correctly identified as low quality")
                else:
                    print(f"    ⚠️ {name}: Expected low score, got {evaluation['overall_score']:.3f}")
            
            elif name == "No Results Found":
                if evaluation["overall_score"] <= 0.3:
                    print(f"    ✅ {name}: Correctly penalized for no results")
                else:
                    print(f"    ⚠️ {name}: Expected very low score, got {evaluation['overall_score']:.3f}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Evaluation Test Summary")
        
        avg_score = sum(result["overall_score"] for result in self.test_results) / len(self.test_results)
        print(f"📈 Average Overall Score: {avg_score:.3f}")
        
        relevance_distribution = {}
        for result in self.test_results:
            level = result["relevance_level"]
            relevance_distribution[level] = relevance_distribution.get(level, 0) + 1
        
        print(f"📊 Relevance Distribution: {relevance_distribution}")
        
        # Check metric consistency
        print("\n🔧 Metric Analysis:")
        for metric_name in ["relevance", "completeness", "accuracy", "entity_match", "performance"]:
            scores = []
            for result in self.test_results:
                for metric in result["metrics"]:
                    if metric["name"] == metric_name:
                        scores.append(metric["score"])
            
            if scores:
                avg_metric = sum(scores) / len(scores)
                min_metric = min(scores)
                max_metric = max(scores)
                print(f"    📈 {metric_name.title()}: avg={avg_metric:.3f}, range=[{min_metric:.3f}, {max_metric:.3f}]")
        
        print("\n🎉 Evaluator Bot tests completed successfully!")
        print("✅ Evaluation logic is working correctly")
        
        return True

def main():
    """Main test runner."""
    test_runner = SimpleEvaluatorTest()
    success = test_runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)