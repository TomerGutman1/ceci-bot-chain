#!/usr/bin/env python3
"""
Comprehensive EVAL Bot Testing Script
Tests the full pipeline from user query to final EVAL output.
Shows first 100 characters of output and detailed error logs.
"""

import json
import time
import sys
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configuration
BACKEND_URL = "http://localhost:5001"
INTENT_BOT_URL = "http://localhost:8011"
SQL_GEN_BOT_URL = "http://localhost:8012"
EVAL_BOT_URL = "http://localhost:8014"

# Test queries for EVAL intent  
TEST_QUERIES = [
    "נתח לעומק את החלטה 1 ממשלה 37",  # Use a simple decision that likely exists
    "אני רוצה ניתוח מעמיק של החלטה 2 ממשלה 37",
]

class TestLogger:
    """Simple logger for test output."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info_logs = []
    
    def info(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] INFO: {message}"
        print(log_msg)
        self.info_logs.append(log_msg)
    
    def warning(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] WARN: {message}"
        print(f"\033[93m{log_msg}\033[0m")  # Yellow
        self.warnings.append(log_msg)
    
    def error(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] ERROR: {message}"
        print(f"\033[91m{log_msg}\033[0m")  # Red
        self.errors.append(log_msg)
    
    def success(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] SUCCESS: {message}"
        print(f"\033[92m{log_msg}\033[0m")  # Green
        self.info_logs.append(log_msg)

logger = TestLogger()

def check_service_health(service_name: str, url: str) -> bool:
    """Check if a service is healthy."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.success(f"{service_name} is healthy: {data.get('status', 'unknown')}")
            return True
        else:
            logger.error(f"{service_name} health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"{service_name} health check failed: {e}")
        return False

def test_intent_detection(query: str, conv_id: str) -> Optional[Dict[str, Any]]:
    """Test intent detection for EVAL queries."""
    logger.info(f"Testing intent detection for: '{query}'")
    
    try:
        payload = {
            "text": query,
            "conv_id": conv_id,
            "trace_id": f"test_{int(time.time())}"
        }
        
        response = requests.post(
            f"{INTENT_BOT_URL}/intent",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            intent_type = result.get("intent_type")
            confidence = result.get("confidence", 0)
            entities = result.get("entities", {})
            
            logger.info(f"Intent detected: {intent_type} (confidence: {confidence:.2f})")
            logger.info(f"Entities: {entities}")
            
            if intent_type == "EVAL":
                logger.success("EVAL intent correctly detected!")
                return result
            else:
                logger.warning(f"Expected EVAL intent, got {intent_type}")
                return result
        else:
            error_text = response.text
            logger.error(f"Intent detection failed: HTTP {response.status_code} - {error_text}")
            return None
                
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        return None

def test_sql_generation(intent_data: Dict[str, Any], query: str, conv_id: str) -> Optional[Dict[str, Any]]:
    """Test SQL generation for decision lookup."""
    logger.info("Testing SQL generation for decision lookup")
    
    try:
        # Extract entities from intent
        entities = intent_data.get("entities", {})
        government_number = entities.get("government_number")
        decision_number = entities.get("decision_number")
        
        if not decision_number:
            logger.warning("No decision number found in entities")
            return None
        
        payload = {
            "intent": "search",
            "entities": {
                "government_number": government_number,
                "decision_number": decision_number
            },
            "conv_id": conv_id
        }
        
        response = requests.post(
            f"{SQL_GEN_BOT_URL}/sqlgen",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            sql_query = result.get("sql_query")
            parameters = result.get("parameters", [])
            token_usage = result.get("token_usage", {})
            
            logger.info(f"SQL generated: {sql_query[:100]}...")
            logger.info(f"Parameters: {parameters}")
            logger.info(f"Tokens used: {token_usage.get('total_tokens', 0)}")
            
            return result
        else:
            error_text = response.text
            logger.error(f"SQL generation failed: HTTP {response.status_code} - {error_text}")
            return None
                
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        return None

def test_eval_bot_direct(government_number: int, decision_number: int, query: str, conv_id: str) -> Optional[Dict[str, Any]]:
    """Test EVAL bot directly with decision parameters."""
    logger.info(f"Testing EVAL bot for decision {decision_number} from government {government_number}")
    
    try:
        payload = {
            "conv_id": conv_id,
            "government_number": government_number,
            "decision_number": decision_number,
            "original_query": query
        }
        
        response = requests.post(
            f"{EVAL_BOT_URL}/evaluate",
            json=payload,
            timeout=60  # Longer timeout for GPT analysis
        )
        
        if response.status_code == 200:
            result = response.json()
            
            overall_score = result.get("overall_score", 0)
            relevance_level = result.get("relevance_level", "unknown")
            token_usage = result.get("token_usage", {})
            explanation = result.get("explanation", "")
            
            logger.success(f"EVAL completed: Score {overall_score:.2f}, Level: {relevance_level}")
            logger.info(f"Tokens used: {token_usage.get('total_tokens', 0)}")
            logger.info(f"First 100 chars of explanation: {explanation[:100]}...")
            
            return result
        else:
            error_text = response.text
            logger.error(f"EVAL bot failed: HTTP {response.status_code} - {error_text}")
            return None
                
    except Exception as e:
        logger.error(f"EVAL bot error: {e}")
        return None

def test_full_backend_pipeline(query: str, conv_id: str) -> Optional[Dict[str, Any]]:
    """Test the full backend pipeline from query to response."""
    logger.info(f"Testing full backend pipeline for: '{query}'")
    
    try:
        payload = {
            "message": query,
            "sessionId": conv_id,
            "outputFormat": "detailed",
            "includeMetadata": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=120  # Long timeout for full pipeline
        )
        
        if response.status_code == 200:
            result = response.json()
            
            success = result.get("success", False)
            response_text = result.get("response", "")
            metadata = result.get("metadata", {})
            
            logger.info(f"Backend pipeline success: {success}")
            logger.info(f"Response length: {len(response_text)} characters")
            logger.info(f"First 100 chars: {response_text[:100]}...")
            
            if metadata:
                intent = metadata.get("intent")
                token_usage = metadata.get("token_usage", {})
                logger.info(f"Intent: {intent}")
                logger.info(f"Total tokens: {token_usage.get('total_tokens', 0)}")
            
            return result
        else:
            error_text = response.text
            logger.error(f"Backend pipeline failed: HTTP {response.status_code} - {error_text}")
            return None
                
    except Exception as e:
        logger.error(f"Backend pipeline error: {e}")
        return None

def run_comprehensive_test(query: str) -> Dict[str, Any]:
    """Run comprehensive test for a single query."""
    conv_id = f"test_{int(time.time())}_{hash(query) % 1000}"
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE EVAL TEST")
    print(f"Query: {query}")
    print(f"Conv ID: {conv_id}")
    print(f"{'='*80}")
    
    test_results = {
        "query": query,
        "conv_id": conv_id,
        "timestamp": datetime.now().isoformat(),
        "steps": {}
    }
    
    # Step 1: Health checks
    logger.info("Step 1: Checking service health...")
    services_healthy = True
    for service_name, url in [
        ("Intent Bot", INTENT_BOT_URL),
        ("SQL Gen Bot", SQL_GEN_BOT_URL),
        ("EVAL Bot", EVAL_BOT_URL),
        ("Backend", BACKEND_URL)
    ]:
        healthy = check_service_health(service_name, url)
        if not healthy:
            services_healthy = False
    
    test_results["steps"]["health_checks"] = {"success": services_healthy}
    
    if not services_healthy:
        logger.error("Some services are not healthy. Continuing with available services...")
    
    # Step 2: Intent detection
    logger.info("Step 2: Testing intent detection...")
    intent_result = test_intent_detection(query, conv_id)
    test_results["steps"]["intent_detection"] = {
        "success": intent_result is not None,
        "result": intent_result
    }
    
    # Step 3: SQL generation (if intent detected)
    sql_result = None
    if intent_result:
        logger.info("Step 3: Testing SQL generation...")
        sql_result = test_sql_generation(intent_result, query, conv_id)
        test_results["steps"]["sql_generation"] = {
            "success": sql_result is not None,
            "result": sql_result
        }
    
    # Step 4: Direct EVAL bot test (if we have decision info)
    eval_result = None
    if intent_result and intent_result.get("entities"):
        entities = intent_result["entities"]
        government_number = entities.get("government_number", 37)  # Default to 37
        decision_number = entities.get("decision_number")
        
        if decision_number:
            logger.info("Step 4: Testing EVAL bot directly...")
            eval_result = test_eval_bot_direct(government_number, decision_number, query, conv_id)
            test_results["steps"]["eval_bot_direct"] = {
                "success": eval_result is not None,
                "result": eval_result
            }
    
    # Step 5: Full backend pipeline test
    logger.info("Step 5: Testing full backend pipeline...")
    backend_result = test_full_backend_pipeline(query, conv_id)
    test_results["steps"]["backend_pipeline"] = {
        "success": backend_result is not None,
        "result": backend_result
    }
    
    return test_results

def main():
    """Main test function."""
    print("EVAL Bot Comprehensive Testing Script")
    print("=" * 50)
    
    all_results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        try:
            result = run_comprehensive_test(query)
            all_results.append(result)
            
            # Brief summary
            steps = result["steps"]
            success_count = sum(1 for step in steps.values() if step.get("success", False))
            total_steps = len(steps)
            
            print(f"\nTest {i} Summary: {success_count}/{total_steps} steps successful")
            
            # Show errors if any
            if logger.errors:
                print(f"Errors in this test: {len(logger.errors)}")
                for error in logger.errors[-3:]:  # Show last 3 errors
                    print(f"  {error}")
            
            # Clear logger for next test
            logger.errors.clear()
            logger.warnings.clear()
            
        except Exception as e:
            logger.error(f"Test {i} failed completely: {e}")
        
        # Wait between tests
        if i < len(TEST_QUERIES):
            time.sleep(2)
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    
    for i, result in enumerate(all_results, 1):
        query = result["query"]
        steps = result["steps"]
        success_count = sum(1 for step in steps.values() if step.get("success", False))
        total_steps = len(steps)
        
        status = "✅" if success_count == total_steps else "⚠️" if success_count > 0 else "❌"
        print(f"{status} Test {i}: {success_count}/{total_steps} - '{query[:50]}...'")
        
        # Show specific step results
        for step_name, step_data in steps.items():
            success = step_data.get("success", False)
            step_status = "✅" if success else "❌"
            print(f"  {step_status} {step_name}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"eval_test_results_{timestamp}.json"
    
    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\nDetailed results saved to: {results_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
    
    print(f"\nTest completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)