#!/usr/bin/env python3
"""
Quick test report generator - tests key functionality of the bot chain.
"""

import requests
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

# Service URLs
REWRITE_BOT_URL = "http://localhost:8010"
INTENT_BOT_URL = "http://localhost:8011"
SQL_GEN_BOT_URL = "http://localhost:8012"
CONTEXT_ROUTER_URL = "http://localhost:8013"
EVALUATOR_BOT_URL = "http://localhost:8014"

def test_bot_health(name: str, url: str) -> Dict[str, Any]:
    """Test if a bot is healthy."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return {
            "name": name,
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            "name": name,
            "status": "offline",
            "error": str(e)
        }

def test_rewrite_bot(query: str) -> Dict[str, Any]:
    """Test rewrite bot functionality."""
    conv_id = str(uuid.uuid4())
    try:
        response = requests.post(
            f"{REWRITE_BOT_URL}/rewrite",
            json={"text": query, "conv_id": conv_id},
            timeout=10
        )
        result = response.json()
        return {
            "success": response.status_code == 200,
            "clean_text": result.get("clean_text", ""),
            "token_usage": result.get("token_usage", {})
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_intent_bot(query: str) -> Dict[str, Any]:
    """Test intent detection."""
    conv_id = str(uuid.uuid4())
    try:
        response = requests.post(
            f"{INTENT_BOT_URL}/detect_intent",
            json={"text": query, "conv_id": conv_id},
            timeout=10
        )
        result = response.json()
        return {
            "success": response.status_code == 200,
            "intent": result.get("intent", ""),
            "entities": result.get("entities", {}),
            "confidence": result.get("confidence_score", 0)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_context_router(query: str, intent: str) -> Dict[str, Any]:
    """Test context router."""
    conv_id = str(uuid.uuid4())
    try:
        response = requests.post(
            f"{CONTEXT_ROUTER_URL}/route",
            json={
                "conv_id": conv_id,
                "current_query": query,
                "intent": intent,
                "entities": {},
                "confidence_score": 0.9
            },
            timeout=10
        )
        result = response.json()
        return {
            "success": response.status_code == 200,
            "route": result.get("route", ""),
            "needs_clarification": result.get("needs_clarification", False),
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_pipeline_test(query: str) -> Dict[str, Any]:
    """Run a query through the bot pipeline."""
    results = {"query": query, "steps": []}
    
    # Step 1: Rewrite
    rewrite_result = test_rewrite_bot(query)
    results["steps"].append({"bot": "rewrite", **rewrite_result})
    
    if not rewrite_result["success"]:
        return results
    
    # Step 2: Intent detection
    clean_text = rewrite_result.get("clean_text", query)
    intent_result = test_intent_bot(clean_text)
    results["steps"].append({"bot": "intent", **intent_result})
    
    if not intent_result["success"]:
        return results
    
    # Step 3: Context routing
    intent = intent_result.get("intent", "QUERY")
    router_result = test_context_router(clean_text, intent)
    results["steps"].append({"bot": "context_router", **router_result})
    
    return results

def generate_report():
    """Generate comprehensive test report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "health_checks": [],
        "pipeline_tests": [],
        "summary": {}
    }
    
    print("CECI Bot Chain Test Report")
    print("=" * 60)
    print(f"Generated: {report['timestamp']}")
    print()
    
    # Health checks
    print("1. SERVICE HEALTH CHECKS")
    print("-" * 40)
    
    bots = [
        ("Rewrite Bot", REWRITE_BOT_URL),
        ("Intent Bot", INTENT_BOT_URL),
        ("SQL Gen Bot", SQL_GEN_BOT_URL),
        ("Context Router", CONTEXT_ROUTER_URL),
        ("Evaluator Bot", EVALUATOR_BOT_URL)
    ]
    
    healthy_count = 0
    for name, url in bots:
        health = test_bot_health(name, url)
        report["health_checks"].append(health)
        
        status_icon = "✅" if health["status"] == "healthy" else "❌"
        print(f"{status_icon} {name}: {health['status']}", end="")
        
        if health["status"] == "healthy":
            print(f" (response time: {health['response_time']:.3f}s)")
            healthy_count += 1
        else:
            print(f" - {health.get('error', 'Unknown error')}")
    
    print(f"\nHealthy services: {healthy_count}/{len(bots)}")
    
    # Pipeline tests
    print("\n2. PIPELINE FUNCTIONALITY TESTS")
    print("-" * 40)
    
    test_queries = [
        ("החלטה 2989", "Specific decision lookup"),
        ("כמה החלטות יש בנושא חינוך?", "Statistical query"),
        ("תן לי את זה", "Reference resolution"),
        ("מה?", "Unclear query"),
        ("נתח את החלטה 1000", "Analysis request")
    ]
    
    for query, description in test_queries:
        print(f"\nTesting: {description}")
        print(f"Query: '{query}'")
        
        result = run_pipeline_test(query)
        report["pipeline_tests"].append(result)
        
        for step in result["steps"]:
            bot = step["bot"]
            success = step.get("success", False)
            icon = "✅" if success else "❌"
            
            if bot == "rewrite":
                print(f"  {icon} Rewrite: {step.get('clean_text', 'FAILED')}")
                if success and step.get("token_usage"):
                    print(f"     Tokens: {step['token_usage'].get('total_tokens', 0)}")
            
            elif bot == "intent":
                print(f"  {icon} Intent: {step.get('intent', 'FAILED')} (confidence: {step.get('confidence', 0):.2f})")
                if step.get("entities"):
                    print(f"     Entities: {json.dumps(step['entities'], ensure_ascii=False)}")
            
            elif bot == "context_router":
                print(f"  {icon} Router: {step.get('route', 'FAILED')}")
                if step.get("needs_clarification"):
                    print(f"     Needs clarification: Yes")
    
    # Summary
    print("\n3. TEST SUMMARY")
    print("-" * 40)
    
    total_tests = len(report["pipeline_tests"])
    successful_pipelines = sum(
        1 for test in report["pipeline_tests"] 
        if all(step.get("success", False) for step in test["steps"])
    )
    
    report["summary"] = {
        "total_health_checks": len(report["health_checks"]),
        "healthy_services": healthy_count,
        "total_pipeline_tests": total_tests,
        "successful_pipelines": successful_pipelines,
        "success_rate": successful_pipelines / total_tests if total_tests > 0 else 0
    }
    
    print(f"Health checks: {healthy_count}/{len(bots)} services healthy")
    print(f"Pipeline tests: {successful_pipelines}/{total_tests} successful")
    print(f"Success rate: {report['summary']['success_rate']:.1%}")
    
    # Key findings
    print("\n4. KEY FINDINGS")
    print("-" * 40)
    
    # Check for specific issues
    findings = []
    
    # Check if unclear queries trigger clarification
    unclear_tests = [t for t in report["pipeline_tests"] if "מה?" in t["query"]]
    if unclear_tests:
        router_step = next((s for s in unclear_tests[0]["steps"] if s["bot"] == "context_router"), None)
        if router_step and not router_step.get("needs_clarification"):
            findings.append("⚠️  UNCLEAR queries not triggering clarification")
    
    # Check if reference queries are recognized
    ref_tests = [t for t in report["pipeline_tests"] if "תן לי את זה" in t["query"]]
    if ref_tests:
        intent_step = next((s for s in ref_tests[0]["steps"] if s["bot"] == "intent"), None)
        if intent_step and intent_step.get("intent") != "RESULT_REF":
            findings.append("⚠️  Reference queries not detected as RESULT_REF")
    
    # Check token usage
    total_tokens = sum(
        step.get("token_usage", {}).get("total_tokens", 0)
        for test in report["pipeline_tests"]
        for step in test["steps"]
        if step.get("token_usage")
    )
    avg_tokens = total_tokens / total_tests if total_tests > 0 else 0
    findings.append(f"📊 Average tokens per query: {avg_tokens:.0f}")
    
    if findings:
        for finding in findings:
            print(f"  {finding}")
    else:
        print("  ✅ All tests passed without issues")
    
    # Save report
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("Report saved to: test_report.json")
    
    return report

if __name__ == "__main__":
    generate_report()