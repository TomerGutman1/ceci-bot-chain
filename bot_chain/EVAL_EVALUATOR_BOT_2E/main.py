"""
EVAL Evaluator Bot 2E - Results evaluation and quality scoring.
Evaluates SQL query results for relevance, quality, and completeness.
Provides weighted scoring and explanations for ranking decisions.
"""

import json
import asyncio
import openai
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re
import math

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.logging import setup_logging, log_api_call, log_gpt_usage
from common.config import get_config

# ====================================
# CONFIGURATION & LOGGING
# ====================================
logger = setup_logging('EVAL_EVALUATOR_BOT_2E')
config = get_config('EVAL_EVALUATOR_BOT_2E')
app = FastAPI(
    title="EVAL Evaluator Bot 2E",
    description="Evaluates query results for relevance and quality",
    version="1.0.0"
)

# Configure OpenAI
openai.api_key = config.openai_api_key

# ====================================
# PYDANTIC MODELS
# ====================================
class RelevanceLevel(str, Enum):
    """Relevance levels for evaluation."""
    HIGHLY_RELEVANT = "highly_relevant"
    RELEVANT = "relevant"
    PARTIALLY_RELEVANT = "partially_relevant"
    NOT_RELEVANT = "not_relevant"

class QualityMetric(BaseModel):
    """Individual quality metric score."""
    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    explanation: str

class EvaluationRequest(BaseModel):
    """Request for result evaluation."""
    conv_id: str = Field(..., description="Conversation ID")
    original_query: str = Field(..., description="Original user query")
    intent: str = Field(..., description="Detected intent")
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    sql_query: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    result_count: int = Field(..., description="Number of results returned")
    execution_time_ms: float = Field(..., description="Query execution time")

class EvaluationResponse(BaseModel):
    """Evaluation response with scores and explanations."""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    relevance_level: RelevanceLevel = Field(..., description="Relevance classification")
    quality_metrics: List[QualityMetric] = Field(..., description="Individual quality metrics")
    content_analysis: Dict[str, Any] = Field(..., description="Content analysis results")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Evaluation confidence")
    explanation: str = Field(..., description="Human-readable explanation")
    processing_time_ms: float = Field(..., description="Evaluation processing time")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    evaluation_count: int

# ====================================
# EVALUATION WEIGHTS AND THRESHOLDS
# ====================================
EVALUATION_WEIGHTS = {
    "relevance": 0.35,           # How relevant are results to query
    "completeness": 0.25,        # Are results complete/comprehensive
    "accuracy": 0.20,            # Are results accurate and up-to-date
    "entity_match": 0.15,        # Do results match extracted entities
    "performance": 0.05          # Query performance and efficiency
}

RELEVANCE_THRESHOLDS = {
    RelevanceLevel.HIGHLY_RELEVANT: 0.85,
    RelevanceLevel.RELEVANT: 0.70,
    RelevanceLevel.PARTIALLY_RELEVANT: 0.40,
    RelevanceLevel.NOT_RELEVANT: 0.0
}

# ====================================
# QUALITY METRICS EVALUATORS
# ====================================
def evaluate_relevance(query: str, intent: str, entities: Dict, results: List[Dict]) -> QualityMetric:
    """Evaluate how relevant results are to the original query."""
    if not results:
        return QualityMetric(
            name="relevance",
            score=0.0,
            weight=EVALUATION_WEIGHTS["relevance"],
            explanation="No results returned"
        )
    
    score = 0.5  # Base score
    explanation_parts = []
    
    # Check entity matching in results
    entity_matches = 0
    total_entities = len(entities)
    
    if total_entities > 0:
        for result in results[:5]:  # Check first 5 results
            for entity_key, entity_value in entities.items():
                if entity_key == "government_number" and "government_number" in result:
                    if result["government_number"] == entity_value:
                        entity_matches += 1
                        break
                elif entity_key == "topic" and "topics" in result:
                    if isinstance(result["topics"], list) and entity_value in result["topics"]:
                        entity_matches += 1
                        break
                elif entity_key == "decision_number" and "decision_number" in result:
                    if result["decision_number"] == entity_value:
                        entity_matches += 1
                        break
        
        entity_match_ratio = entity_matches / min(len(results), 5)
        score += entity_match_ratio * 0.4
        explanation_parts.append(f"{entity_matches}/{min(len(results), 5)} results match key entities")
    
    # Intent-specific relevance scoring
    if intent == "search":
        # For search, check if results have diverse topics
        if len(results) > 1:
            score += 0.1
            explanation_parts.append("Multiple results for search query")
    elif intent == "count":
        # For count, exact number matters
        score = 0.9 if len(results) == 1 else 0.6
        explanation_parts.append(f"Count query returned {len(results)} result(s)")
    elif intent == "specific_decision":
        # For specific decision, should return 1 exact match
        score = 0.95 if len(results) == 1 else 0.3
        explanation_parts.append(f"Specific decision query returned {len(results)} result(s)")
    
    # Adjust for result quality
    if results and len(results) > 0:
        # Check if results have required fields
        first_result = results[0]
        required_fields = ["title", "content", "decision_date"]
        present_fields = sum(1 for field in required_fields if field in first_result and first_result[field])
        field_score = present_fields / len(required_fields)
        score += field_score * 0.1
        explanation_parts.append(f"{present_fields}/{len(required_fields)} required fields present")
    
    score = min(1.0, score)
    explanation = "; ".join(explanation_parts) if explanation_parts else "Basic relevance evaluation"
    
    return QualityMetric(
        name="relevance",
        score=score,
        weight=EVALUATION_WEIGHTS["relevance"],
        explanation=explanation
    )

def evaluate_completeness(query: str, intent: str, entities: Dict, results: List[Dict]) -> QualityMetric:
    """Evaluate completeness of results."""
    if not results:
        return QualityMetric(
            name="completeness",
            score=0.0,
            weight=EVALUATION_WEIGHTS["completeness"],
            explanation="No results to evaluate completeness"
        )
    
    score = 0.5  # Base score
    explanation_parts = []
    
    # Check expected result count based on intent
    if intent == "search":
        if len(results) >= 10:
            score = 0.9
            explanation_parts.append("Comprehensive search results (10+ items)")
        elif len(results) >= 5:
            score = 0.8
            explanation_parts.append("Good search results (5-9 items)")
        elif len(results) >= 1:
            score = 0.6
            explanation_parts.append("Limited search results (1-4 items)")
    elif intent == "count":
        # Count should always return exactly one result
        score = 1.0 if len(results) == 1 else 0.3
        explanation_parts.append(f"Count query completeness: {len(results)} result(s)")
    elif intent == "specific_decision":
        # Specific decision should return exactly one result
        score = 1.0 if len(results) == 1 else 0.2
        explanation_parts.append(f"Specific decision completeness: {len(results)} result(s)")
    
    # Check data completeness in results
    if results:
        complete_results = 0
        for result in results[:5]:  # Check first 5
            required_fields = ["title", "content", "decision_date", "government_number"]
            present_fields = sum(1 for field in required_fields if field in result and result[field] is not None)
            if present_fields >= 3:  # At least 3 of 4 required fields
                complete_results += 1
        
        completeness_ratio = complete_results / min(len(results), 5)
        score = (score + completeness_ratio) / 2
        explanation_parts.append(f"{complete_results}/{min(len(results), 5)} results have complete data")
    
    explanation = "; ".join(explanation_parts)
    
    return QualityMetric(
        name="completeness",
        score=score,
        weight=EVALUATION_WEIGHTS["completeness"],
        explanation=explanation
    )

def evaluate_accuracy(query: str, intent: str, entities: Dict, results: List[Dict]) -> QualityMetric:
    """Evaluate accuracy of results."""
    if not results:
        return QualityMetric(
            name="accuracy",
            score=0.0,
            weight=EVALUATION_WEIGHTS["accuracy"],
            explanation="No results to evaluate accuracy"
        )
    
    score = 0.7  # Base score for returned results
    explanation_parts = []
    
    # Check date consistency
    date_consistent = True
    for result in results[:3]:  # Check first 3
        if "decision_date" in result:
            try:
                # Basic date format validation
                date_str = str(result["decision_date"])
                if len(date_str) >= 4:  # Has year
                    year = int(date_str[:4])
                    if year < 1948 or year > 2025:  # Israeli government dates
                        date_consistent = False
                        break
            except:
                date_consistent = False
                break
    
    if date_consistent:
        score += 0.1
        explanation_parts.append("Date consistency check passed")
    else:
        score -= 0.2
        explanation_parts.append("Date consistency issues detected")
    
    # Check government number consistency
    if "government_number" in entities:
        expected_gov = entities["government_number"]
        gov_consistent = True
        for result in results[:3]:
            if "government_number" in result:
                if result["government_number"] != expected_gov:
                    gov_consistent = False
                    break
        
        if gov_consistent:
            score += 0.1
            explanation_parts.append("Government number consistency verified")
        else:
            score -= 0.2
            explanation_parts.append("Government number inconsistencies found")
    
    # Check for reasonable content length
    content_quality = 0
    for result in results[:3]:
        if "content" in result and result["content"]:
            content_len = len(str(result["content"]))
            if 50 <= content_len <= 5000:  # Reasonable content length
                content_quality += 1
    
    if content_quality > 0:
        content_score = content_quality / min(len(results), 3)
        score += content_score * 0.1
        explanation_parts.append(f"{content_quality}/{min(len(results), 3)} results have quality content")
    
    score = max(0.0, min(1.0, score))
    explanation = "; ".join(explanation_parts) if explanation_parts else "Basic accuracy evaluation"
    
    return QualityMetric(
        name="accuracy",
        score=score,
        weight=EVALUATION_WEIGHTS["accuracy"],
        explanation=explanation
    )

def evaluate_entity_match(query: str, intent: str, entities: Dict, results: List[Dict]) -> QualityMetric:
    """Evaluate how well results match extracted entities."""
    if not entities:
        return QualityMetric(
            name="entity_match",
            score=1.0,  # Perfect score if no entities to match
            weight=EVALUATION_WEIGHTS["entity_match"],
            explanation="No entities to match"
        )
    
    if not results:
        return QualityMetric(
            name="entity_match",
            score=0.0,
            weight=EVALUATION_WEIGHTS["entity_match"],
            explanation="No results to match entities against"
        )
    
    total_entities = len(entities)
    matched_entities = 0
    match_details = []
    
    # Check each entity type
    for entity_key, entity_value in entities.items():
        entity_matched = False
        
        if entity_key == "government_number":
            for result in results:
                if "government_number" in result and result["government_number"] == entity_value:
                    entity_matched = True
                    break
        elif entity_key == "topic":
            for result in results:
                if "topics" in result and isinstance(result["topics"], list):
                    if entity_value in result["topics"]:
                        entity_matched = True
                        break
                elif "title" in result or "content" in result:
                    # Fuzzy topic matching in title/content
                    text_to_search = f"{result.get('title', '')} {result.get('content', '')}"
                    if entity_value in text_to_search:
                        entity_matched = True
                        break
        elif entity_key == "decision_number":
            for result in results:
                if "decision_number" in result and result["decision_number"] == entity_value:
                    entity_matched = True
                    break
        elif entity_key == "date_range":
            # Check if results fall within date range
            if isinstance(entity_value, dict) and "start" in entity_value:
                start_year = int(entity_value["start"][:4])
                for result in results:
                    if "decision_date" in result:
                        try:
                            result_year = int(str(result["decision_date"])[:4])
                            if result_year >= start_year:
                                entity_matched = True
                                break
                        except:
                            pass
        
        if entity_matched:
            matched_entities += 1
            match_details.append(f"{entity_key}:✓")
        else:
            match_details.append(f"{entity_key}:✗")
    
    score = matched_entities / total_entities if total_entities > 0 else 1.0
    explanation = f"Entity matching: {matched_entities}/{total_entities} ({', '.join(match_details)})"
    
    return QualityMetric(
        name="entity_match",
        score=score,
        weight=EVALUATION_WEIGHTS["entity_match"],
        explanation=explanation
    )

def evaluate_performance(query: str, intent: str, entities: Dict, results: List[Dict], 
                        execution_time_ms: float, result_count: int) -> QualityMetric:
    """Evaluate query performance metrics."""
    score = 0.8  # Base performance score
    explanation_parts = []
    
    # Execution time scoring
    if execution_time_ms < 100:
        score += 0.2
        explanation_parts.append("Excellent response time (<100ms)")
    elif execution_time_ms < 500:
        score += 0.1
        explanation_parts.append("Good response time (<500ms)")
    elif execution_time_ms < 1000:
        explanation_parts.append("Acceptable response time (<1s)")
    else:
        score -= 0.1
        explanation_parts.append(f"Slow response time ({execution_time_ms:.0f}ms)")
    
    # Result count efficiency
    if intent == "count":
        if result_count == 1:
            score += 0.1
            explanation_parts.append("Efficient count query (1 result)")
    elif intent == "specific_decision":
        if result_count == 1:
            score += 0.1
            explanation_parts.append("Efficient specific query (1 result)")
        elif result_count > 1:
            score -= 0.1
            explanation_parts.append(f"Inefficient specific query ({result_count} results)")
    elif intent == "search":
        if 1 <= result_count <= 20:
            score += 0.05
            explanation_parts.append("Reasonable result count for search")
        elif result_count > 50:
            score -= 0.05
            explanation_parts.append("Large result set may impact performance")
    
    score = max(0.0, min(1.0, score))
    explanation = "; ".join(explanation_parts)
    
    return QualityMetric(
        name="performance",
        score=score,
        weight=EVALUATION_WEIGHTS["performance"],
        explanation=explanation
    )

# ====================================
# GPT-POWERED CONTENT ANALYSIS
# ====================================
async def analyze_content_with_gpt(query: str, intent: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
    """Use GPT to analyze content quality and relevance."""
    if not results:
        return {
            "semantic_relevance": 0.0,
            "content_quality": 0.0,
            "language_quality": 0.0,
            "gpt_explanation": "No results to analyze"
        }
    
    # Prepare sample results for GPT analysis (limit to 3 for efficiency)
    sample_results = results[:3]
    results_text = ""
    
    for i, result in enumerate(sample_results, 1):
        title = result.get("title", "No title")
        content = result.get("content", "No content")
        # Truncate content for GPT
        content_snippet = content[:300] + "..." if len(content) > 300 else content
        results_text += f"Result {i}:\nTitle: {title}\nContent: {content_snippet}\n\n"
    
    prompt = f"""
תפקידך הוא להעריך את איכות התוצאות של חיפוש בהחלטות ממשלת ישראל.

שאילתת המשתמש: "{query}"
כוונה מזוהה: {intent}
ישויות שחולצו: {json.dumps(entities, ensure_ascii=False)}

תוצאות לבדיקה:
{results_text}

אנא העריך את הנושאים הבאים בסולם 0-1:
1. רלוונטיות סמנטית - עד כמה התוצאות רלוונטיות לשאילתא
2. איכות תוכן - עד כמה המידע מפורט ושימושי
3. איכות שפה - עד כמה הטקסט ברור וכתוב היטב

השב בפורמט JSON:
{{
    "semantic_relevance": 0.85,
    "content_quality": 0.75,
    "language_quality": 0.90,
    "explanation": "הסבר קצר בעברית על ההערכה"
}}
"""
    
    try:
        start_time = datetime.utcnow()
        
        response = await asyncio.create_task(
            openai.ChatCompletion.acreate(
                model=config.model,
                messages=[
                    {"role": "system", "content": "אתה מומחה הערכה לאיכות תוצאות חיפוש בהחלטות ממשלה."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=300
            )
        )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Log GPT usage
        log_gpt_usage(
            logger, "content_analysis", config.model,
            len(prompt.split()), len(response.choices[0].message.content.split()),
            duration, "EVAL_EVALUATOR_BOT_2E"
        )
        
        # Parse GPT response
        gpt_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            json_start = gpt_text.find('{')
            json_end = gpt_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = gpt_text[json_start:json_end]
                gpt_analysis = json.loads(json_str)
                
                return {
                    "semantic_relevance": float(gpt_analysis.get("semantic_relevance", 0.5)),
                    "content_quality": float(gpt_analysis.get("content_quality", 0.5)),
                    "language_quality": float(gpt_analysis.get("language_quality", 0.5)),
                    "gpt_explanation": gpt_analysis.get("explanation", "GPT analysis completed")
                }
            else:
                # Fallback if no JSON found
                return {
                    "semantic_relevance": 0.6,
                    "content_quality": 0.6,
                    "language_quality": 0.6,
                    "gpt_explanation": f"GPT response: {gpt_text[:100]}..."
                }
                
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "semantic_relevance": 0.6,
                "content_quality": 0.6,
                "language_quality": 0.6,
                "gpt_explanation": f"Parse error: {gpt_text[:100]}..."
            }
            
    except Exception as e:
        logger.error(f"GPT content analysis failed: {e}")
        return {
            "semantic_relevance": 0.5,
            "content_quality": 0.5,
            "language_quality": 0.5,
            "gpt_explanation": f"Analysis failed: {str(e)}"
        }

# ====================================
# MAIN EVALUATION LOGIC
# ====================================
async def evaluate_results(request: EvaluationRequest) -> EvaluationResponse:
    """Main evaluation logic combining all metrics."""
    start_time = datetime.utcnow()
    
    # Calculate individual quality metrics
    relevance_metric = evaluate_relevance(
        request.original_query, request.intent, request.entities, request.results
    )
    
    completeness_metric = evaluate_completeness(
        request.original_query, request.intent, request.entities, request.results
    )
    
    accuracy_metric = evaluate_accuracy(
        request.original_query, request.intent, request.entities, request.results
    )
    
    entity_match_metric = evaluate_entity_match(
        request.original_query, request.intent, request.entities, request.results
    )
    
    performance_metric = evaluate_performance(
        request.original_query, request.intent, request.entities, request.results,
        request.execution_time_ms, request.result_count
    )
    
    quality_metrics = [
        relevance_metric, completeness_metric, accuracy_metric,
        entity_match_metric, performance_metric
    ]
    
    # Calculate weighted overall score
    overall_score = sum(metric.score * metric.weight for metric in quality_metrics)
    
    # Determine relevance level
    relevance_level = RelevanceLevel.NOT_RELEVANT
    for level, threshold in sorted(RELEVANCE_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if overall_score >= threshold:
            relevance_level = level
            break
    
    # GPT-powered content analysis
    content_analysis = await analyze_content_with_gpt(
        request.original_query, request.intent, request.entities, request.results
    )
    
    # Generate recommendations
    recommendations = []
    
    if relevance_metric.score < 0.7:
        recommendations.append("שיפור רלוונטיות: שקול חידוד השאילתא או התאמת אלגוריתם החיפוש")
    
    if completeness_metric.score < 0.6:
        recommendations.append("שיפור שלמות: הרחב את היקף החיפוש או שפר מיון התוצאות")
    
    if accuracy_metric.score < 0.7:
        recommendations.append("שיפור דיוק: בדוק את איכות הנתונים ותהליכי הולידציה")
    
    if entity_match_metric.score < 0.8:
        recommendations.append("שיפור התאמת ישויות: שפר זיהוי ישויות או מיפוי מסד הנתונים")
    
    if performance_metric.score < 0.7:
        recommendations.append("שיפור ביצועים: אופטם שאילתות SQL או שפר אינדקסים")
    
    if not recommendations:
        recommendations.append("התוצאות באיכות טובה - המשך לשמור על הרמה")
    
    # Evaluation confidence based on result count and consistency
    confidence = 0.8  # Base confidence
    
    if len(request.results) >= 3:
        confidence += 0.1  # More confident with more results
    elif len(request.results) == 0:
        confidence -= 0.2  # Less confident with no results
    
    if overall_score > 0.8 or overall_score < 0.3:
        confidence += 0.1  # More confident in clear good/bad cases
    
    confidence = max(0.1, min(0.95, confidence))
    
    # Generate human-readable explanation
    explanation = f"""
הערכת איכות התוצאות:
- ציון כללי: {overall_score:.2f}/1.00 ({relevance_level.value})
- רלוונטיות: {relevance_metric.score:.2f} ({relevance_metric.explanation})
- שלמות: {completeness_metric.score:.2f} ({completeness_metric.explanation})
- דיוק: {accuracy_metric.score:.2f} ({accuracy_metric.explanation})
- התאמת ישויות: {entity_match_metric.score:.2f} ({entity_match_metric.explanation})
- ביצועים: {performance_metric.score:.2f} ({performance_metric.explanation})

ניתוח תוכן GPT: {content_analysis.get('gpt_explanation', 'לא זמין')}
""".strip()
    
    processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return EvaluationResponse(
        overall_score=overall_score,
        relevance_level=relevance_level,
        quality_metrics=quality_metrics,
        content_analysis=content_analysis,
        recommendations=recommendations,
        confidence=confidence,
        explanation=explanation,
        processing_time_ms=processing_time
    )

# ====================================
# API ENDPOINTS
# ====================================
evaluation_count = 0

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        evaluation_count=evaluation_count
    )

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_query_results(request: EvaluationRequest):
    """Main evaluation endpoint."""
    global evaluation_count
    start_time = datetime.utcnow()
    
    try:
        log_api_call(
            logger, "evaluate_query_results", request.dict(),
            request.conv_id, "EVAL_EVALUATOR_BOT_2E"
        )
        
        # Perform evaluation
        evaluation = await evaluate_results(request)
        
        evaluation_count += 1
        
        # Log successful evaluation
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Result evaluation completed",
            extra={
                "conv_id": request.conv_id,
                "overall_score": evaluation.overall_score,
                "relevance_level": evaluation.relevance_level.value,
                "result_count": len(request.results),
                "duration_ms": duration * 1000
            }
        )
        
        return evaluation
        
    except Exception as e:
        logger.error(
            f"Evaluation failed for conv_id {request.conv_id}: {e}",
            extra={"conv_id": request.conv_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )

@app.get("/metrics")
async def get_evaluation_metrics():
    """Get evaluation metrics and statistics."""
    return {
        "total_evaluations": evaluation_count,
        "evaluation_weights": EVALUATION_WEIGHTS,
        "relevance_thresholds": {k.value: v for k, v in RELEVANCE_THRESHOLDS.items()},
        "supported_intents": ["search", "count", "specific_decision", "comparison"],
        "quality_metrics": ["relevance", "completeness", "accuracy", "entity_match", "performance"]
    }

# ====================================
# STARTUP
# ====================================
if __name__ == "__main__":
    import uvicorn
    port = config.port if hasattr(config, 'port') else 8014
    uvicorn.run(app, host="0.0.0.0", port=port)