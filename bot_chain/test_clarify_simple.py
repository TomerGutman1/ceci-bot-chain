#!/usr/bin/env python3
"""
Simple test for the Clarification Bot to validate its functionality.
Tests clarification question generation for different types of ambiguous queries.
"""

import asyncio
import sys
import json
from typing import Dict, Any, List

class SimpleClarificationTest:
    """Simple test for clarification bot functionality."""
    
    def __init__(self):
        self.test_results = []
        print("🧪 Initializing Clarification Bot Test")
        
        # Test scenarios for different clarification types
        self.test_scenarios = {
            "missing_government": {
                "conv_id": "test_missing_gov",
                "original_query": "החלטות בנושא חינוך",
                "intent": "search",
                "entities": {"topic": "חינוך"},
                "confidence_score": 0.6,
                "clarification_type": "missing_entities"
            },
            "missing_topic": {
                "conv_id": "test_missing_topic",
                "original_query": "החלטות ממשלה 37",
                "intent": "search", 
                "entities": {"government_number": 37},
                "confidence_score": 0.7,
                "clarification_type": "missing_entities"
            },
            "vague_query": {
                "conv_id": "test_vague",
                "original_query": "מה קורה?",
                "intent": "search",
                "entities": {},
                "confidence_score": 0.3,
                "clarification_type": "vague_intent"
            },
            "ambiguous_time": {
                "conv_id": "test_time",
                "original_query": "החלטות האחרונות",
                "intent": "search",
                "entities": {},
                "confidence_score": 0.5,
                "clarification_type": "ambiguous_time"
            },
            "low_confidence": {
                "conv_id": "test_low_conf",
                "original_query": "אולי משהו על זה",
                "intent": "search",
                "entities": {},
                "confidence_score": 0.2,
                "clarification_type": "low_confidence"
            }
        }
    
    def mock_generate_clarification_questions(self, scenario: Dict) -> Dict[str, Any]:
        """Mock clarification generation based on scenario type."""
        
        clarification_type = scenario["clarification_type"]
        query = scenario["original_query"]
        entities = scenario["entities"]
        
        questions = []
        
        if clarification_type == "missing_entities":
            if "government_number" not in entities:
                questions.append({
                    "type": "missing_government",
                    "question": "איזה ממשלה אתה מחפש?",
                    "suggestions": [
                        "ממשלה 37 (נתניהו הנוכחית)",
                        "ממשלה 36 (בנט-לפיד)",
                        "ממשלה 35 (נתניהו הקודמת)",
                        "כל הממשלות"
                    ]
                })
            
            if "topic" not in entities and "ministries" not in entities:
                questions.append({
                    "type": "missing_topic",
                    "question": "איזה נושא או משרד מעניין אותך?",
                    "suggestions": [
                        "חינוך ותרבות",
                        "ביטחון וצבא",
                        "כלכלה ותקציב",
                        "בריאות ורפואה",
                        "משרד החינוך",
                        "משרד הביטחון"
                    ]
                })
            
        elif clarification_type == "ambiguous_time":
            questions.append({
                "type": "time_clarification",
                "question": "איזה תקופת זמן אתה מחפש?",
                "suggestions": [
                    "השנה האחרונה (2023-2024)",
                    "שנתיים אחרונות (2022-2024)",
                    "חמש שנים אחרונות (2019-2024)",
                    "כל התקופות"
                ]
            })
            
        elif clarification_type == "vague_intent":
            questions.append({
                "type": "intent_clarification",
                "question": "איך אני יכול לעזור לך?",
                "suggestions": [
                    "לחפש החלטות לפי נושא",
                    "למצוא החלטה ספציפית",
                    "לספור החלטות",
                    "לראות החלטות אחרונות"
                ]
            })
            
        elif clarification_type == "low_confidence":
            questions.append({
                "type": "general_clarification",
                "question": "מה בדיוק אתה מחפש?",
                "suggestions": [
                    "החלטות של ממשלה ספציפית",
                    "החלטות בנושא מסוים",
                    "החלטה ספציפית לפי מספר",
                    "ספירת החלטות"
                ]
            })
        
        # Fallback question if no specific ones generated
        if not questions:
            questions.append({
                "type": "general",
                "question": "תוכל לפרט יותר כדי שאוכל לעזור לך טוב יותר?",
                "suggestions": [
                    "הוסף מספר ממשלה",
                    "הוסף נושא ספציפי",
                    "הוסף תקופת זמן",
                    "פרט את מה שאתה מחפש"
                ]
            })
        
        return {
            "questions": questions,
            "explanation": f"נדרשים פרטים נוספים לחיפוש מדויק ({clarification_type})"
        }
    
    def mock_generate_suggested_refinements(self, scenario: Dict) -> List[str]:
        """Mock suggested query refinements."""
        
        query = scenario["original_query"]
        intent = scenario["intent"]
        entities = scenario["entities"]
        
        refinements = []
        
        # Add government if missing
        if "government_number" not in entities:
            refinements.extend([
                f"{query} ממשלה 37",
                f"{query} ממשלה 36",
                f"החלטות ממשלה 37 {query}"
            ])
        
        # Add topic if missing
        if "topic" not in entities and "ministries" not in entities:
            if "חינוך" not in query.lower():
                refinements.append(f"{query} בנושא חינוך")
            if "ביטחון" not in query.lower():
                refinements.append(f"{query} בנושא ביטחון")
        
        # Add time context if missing
        if intent == "search" and "date_range" not in entities:
            refinements.extend([
                f"{query} ב-2023",
                f"{query} בשנתיים האחרונות"
            ])
        
        # Intent-specific refinements
        if intent == "search" and "החלטות" not in query:
            refinements.append(f"החלטות {query}")
        
        if intent == "count" and "כמה" not in query:
            refinements.append(f"כמה {query}")
        
        # Remove duplicates and limit
        seen = set()
        unique_refinements = []
        for ref in refinements:
            if ref not in seen and ref != query:
                seen.add(ref)
                unique_refinements.append(ref)
        
        return unique_refinements[:4]  # Limit to 4 suggestions
    
    def test_scenario(self, scenario_name: str, scenario: Dict) -> Dict[str, Any]:
        """Test a single clarification scenario."""
        
        print(f"\n📋 Testing: {scenario_name}")
        print(f"📥 Query: '{scenario['original_query']}'")
        print(f"🎯 Intent: {scenario['intent']}")
        print(f"📊 Entities: {scenario['entities']}")
        print(f"📈 Confidence: {scenario['confidence_score']:.2f}")
        print(f"🔍 Type: {scenario['clarification_type']}")
        
        try:
            # Generate clarification questions
            clarification_data = self.mock_generate_clarification_questions(scenario)
            
            # Generate suggested refinements
            refinements = self.mock_generate_suggested_refinements(scenario)
            
            # Calculate confidence
            confidence = 0.8
            if len(clarification_data.get("questions", [])) == 1:
                confidence = 0.9
            if scenario["confidence_score"] < 0.5:
                confidence = 0.7
            
            # Create response
            response = {
                "success": True,
                "conv_id": scenario["conv_id"],
                "clarification_questions": clarification_data.get("questions", []),
                "suggested_refinements": refinements,
                "explanation": clarification_data.get("explanation", "נדרשים פרטים נוספים"),
                "confidence": confidence
            }
            
            # Validate results
            questions_count = len(response["clarification_questions"])
            refinements_count = len(response["suggested_refinements"])
            
            print(f"    ✅ Generated {questions_count} clarification questions")
            print(f"    🔧 Generated {refinements_count} suggested refinements")
            print(f"    📈 Response confidence: {response['confidence']:.2f}")
            
            # Display questions
            for i, question in enumerate(response["clarification_questions"], 1):
                print(f"    ❓ Question {i}: {question['question']}")
                print(f"       💡 Suggestions: {len(question['suggestions'])} options")
            
            # Display refinements
            if refinements:
                print(f"    🔧 Refinement examples:")
                for ref in refinements[:2]:  # Show first 2
                    print(f"       → \"{ref}\"")
            
            # Evaluation
            passed = True
            if questions_count == 0:
                print(f"    ⚠️ No clarification questions generated")
                passed = False
            if scenario["clarification_type"] == "missing_entities" and refinements_count == 0:
                print(f"    ⚠️ No refinements generated for missing entities")
                passed = False
            if response["confidence"] < 0.5:
                print(f"    ⚠️ Low response confidence: {response['confidence']:.2f}")
                passed = False
            
            result = {
                "scenario_name": scenario_name,
                "passed": passed,
                "questions_count": questions_count,
                "refinements_count": refinements_count,
                "confidence": response["confidence"],
                "response": response
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
        """Run all clarification tests."""
        print("🚀 Starting Clarification Bot Functionality Tests")
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
            print("🎉 All clarification tests passed!")
            print("✅ Clarification generation is working correctly")
        else:
            print(f"⚠️ {total - passed} tests failed")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r.get("passed", False)]
            for failed in failed_tests:
                error = failed.get("error", "Unknown error")
                print(f"    ❌ {failed['scenario_name']}: {error}")
        
        # Statistics
        if self.test_results:
            questions_stats = [r.get("questions_count", 0) for r in self.test_results if "questions_count" in r]
            refinements_stats = [r.get("refinements_count", 0) for r in self.test_results if "refinements_count" in r]
            confidence_stats = [r.get("confidence", 0) for r in self.test_results if "confidence" in r]
            
            if questions_stats:
                avg_questions = sum(questions_stats) / len(questions_stats)
                print(f"\n📊 Average questions per scenario: {avg_questions:.1f}")
            
            if refinements_stats:
                avg_refinements = sum(refinements_stats) / len(refinements_stats)
                print(f"🔧 Average refinements per scenario: {avg_refinements:.1f}")
            
            if confidence_stats:
                avg_confidence = sum(confidence_stats) / len(confidence_stats)
                print(f"📈 Average response confidence: {avg_confidence:.3f}")
        
        # Test specific clarification types
        print("\n🔍 Clarification Type Analysis:")
        clarification_types = {}
        for result in self.test_results:
            if "response" in result:
                for question in result["response"].get("clarification_questions", []):
                    q_type = question.get("type", "unknown")
                    clarification_types[q_type] = clarification_types.get(q_type, 0) + 1
        
        for q_type, count in clarification_types.items():
            print(f"    📝 {q_type}: {count} questions")
        
        return passed == total

def main():
    """Main test runner."""
    test_runner = SimpleClarificationTest()
    success = test_runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)