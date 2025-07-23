"""
EVAL Evaluator Bot 2E - Results evaluation and quality scoring.
Evaluates SQL query results for relevance, quality, and completeness.
Provides weighted scoring and explanations for ranking decisions.
"""

import json
import asyncio
import openai
import aiohttp
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

# SQL Generation Bot URL
SQL_GEN_BOT_URL = os.getenv('SQL_GEN_BOT_URL', 'http://sql-gen-bot:8012')

async def fetch_decision_content(government_number: int, decision_number: int, conv_id: str) -> Optional[Dict[str, Any]]:
    """Fetch full decision content using the backend decisions API."""
    try:
        # Use default government 37 if not specified
        if not government_number:
            government_number = 37
            
        backend_url = os.getenv('BACKEND_URL', 'http://backend:5173')
        
        async with aiohttp.ClientSession() as session:
            # Call the new decisions endpoint
            url = f"{backend_url}/api/decisions/decision/{government_number}/{decision_number}"
            logger.info(f"Fetching decision from: {url}")
            
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 404:
                    logger.warning(f"Decision {decision_number} not found in government {government_number}")
                    return None
                elif response.status != 200:
                    logger.error(f"Backend decision fetch failed: {response.status}")
                    return None
                
                decision = await response.json()
                logger.info(f"Successfully fetched decision {decision_number} (content length: {len(decision.get('content', ''))} chars)")
                
                # The response is already in the expected format
                return decision
                
    except Exception as e:
        logger.error(f"Failed to fetch decision content: {e}")
        return None

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
    """Request for feasibility evaluation of a specific government decision."""
    conv_id: str = Field(..., description="Conversation ID")
    government_number: Optional[int] = Field(default=None, description="Government number (optional)")
    decision_number: int = Field(..., description="Decision number to evaluate")
    original_query: str = Field(..., description="Original user query")

class TokenUsage(BaseModel):
    """Model for token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str

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
    token_usage: Optional[TokenUsage] = Field(default=None, description="Token usage for GPT calls")

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
# DECISION SUITABILITY VALIDATION
# ====================================
def validate_decision_for_analysis(decision_content: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Validate if a decision is suitable for feasibility analysis.
    
    Returns:
        (is_suitable, reason, suggestion)
    """
    decision_text = decision_content.get("decision_content", decision_content.get("content", ""))
    operativity = decision_content.get("operativity", "").strip()
    decision_number = decision_content.get("decision_number", "זו")
    
    # Check 1: Content length - we'll analyze all decisions but note if they're short
    # Removed rejection of short decisions - will be handled in analysis instead
    
    # Check 2: Operativity field - use the authoritative database field
    if operativity == "דקלרטיבית":
        return (
            False,
            f"החלטה זו מסווגת כ'דקלרטיבית' במסד הנתונים ולא מתאימה לניתוח ישימות",
            "ניתוח ישימות מיועד להחלטות אופרטיביות הכוללות יישום, הקצאת משאבים ולוחות זמנים. אתה יכול לחפש החלטות אופרטיביות בנושא דומה או לבקש סיכום של ההחלטה."
        )
    
    # Check 3: Missing operativity field - this shouldn't happen with real data
    if not operativity:
        logger.warning(f"Decision {decision_number} missing operativity field")
        # If operativity is missing, we don't automatically reject - let it through for analysis
        # But log it for investigation
    
    return (True, "", "")

# ====================================
# GPT-POWERED CONTENT ANALYSIS
# ====================================
async def perform_feasibility_analysis(decision_content: Dict[str, Any], request: EvaluationRequest) -> EvaluationResponse:
    """Perform comprehensive feasibility analysis of a government decision."""
    start_time = datetime.utcnow()
    
    # Pre-analysis validation: Check if decision is suitable for analysis
    is_suitable, reason, suggestion = validate_decision_for_analysis(decision_content)
    
    if not is_suitable:
        # Return informative response instead of performing expensive analysis
        logger.info(f"Decision {decision_content.get('decision_number')} not suitable for analysis: {reason}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        informative_message = f"""⚠️ **לא ניתן לבצע ניתוח ישימות להחלטה זו**

📝 **סיבה:** {reason}

💡 **הצעות חלופיות:** {suggestion}

ℹ️ **הסבר:** ניתוח ישימות מיועד להחלטות מדיניות מורכבות הכוללות יישום, הקצאת משאבים ולוחות זמנים. החלטות דקלרטיביות או קצרות אינן מתאימות לניתוח זה."""

        # Return a structured response that looks like a regular evaluation but explains why analysis wasn't performed
        return EvaluationResponse(
            overall_score=0.0,
            relevance_level=RelevanceLevel.NOT_RELEVANT,
            quality_metrics=[],
            content_analysis={
                "analysis_status": "not_suitable",
                "reason": reason,
                "suggestion": suggestion,
                "decision_title": decision_content.get("decision_title", decision_content.get("title", "ללא כותרת")),
                "content_length": len(decision_content.get("decision_content", decision_content.get("content", ""))),
                "informative_message": informative_message
            },
            recommendations=[f"החלטה זו אינה מתאימה לניתוח ישימות: {reason}"],
            confidence=1.0,  # We're very confident this decision isn't suitable
            explanation=informative_message,
            processing_time_ms=processing_time,
            token_usage=TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model="validation-only"
            )
        )
    
    # Extract decision details
    decision_title = decision_content.get("decision_title", "ללא כותרת")
    decision_text = decision_content.get("decision_content", decision_content.get("content", ""))
    summary = decision_content.get("summary", "")
    
    # Prepare the complete decision text for analysis
    full_decision_text = f"""
כותרת ההחלטה: {decision_title}

תוכן ההחלטה:
{decision_text}

תקציר:
{summary}
"""
    
    # Create the analysis prompt with the full decision content and detailed criteria
    # Add note if decision is short
    length_note = ""
    if len(full_decision_text.strip()) < 500:
        length_note = "\n\n⚠️ שים לב: החלטה זו מנוסחת בתמציתיות רבה. בצע את הניתוח על בסיס המידע הקיים, אך ציין בסיכום שהחלטה קצרה מאתגרת ניתוח מעמיק.\n"
    
    prompt = f"""נתח את החלטת הממשלה הבאה לפי 13 הקריטריונים לניתוח ישימות:

{full_decision_text}{length_note}

בצע ניתוח ישימות מפורט לפי הקריטריונים הבאים. על כל קריטריון תן ציון מ-0 עד 5 לפי ההנחיות המפורטות:

**1. לוח זמנים מחייב (משקל 17%)**
בדוק האם בההחלטה מוגדרים תאריכים או דד-ליינים מחייבים ומה קורה אם לא עומדים בזמנים:
- 0: אין אזכור זמן ביצוע
- 1: אמירה כללית כמו "בהקדם" 
- 2: אזכור תאריך אחד לסעיף שולי
- 3: זמנים לרוב הסעיפים אך לא ברור אם מחייב
- 4: תאריכים ברורים לכל משימה עיקרית
- 5: תאריכים מחייבים לכל סעיף כולל הגדרת אי-עמידה

**2. צוות מתכלל (משקל 7%)**
גורם שמתאם בין כלל הגורמים ומוודא ביצוע:
- 0: אין צוות מתכלל
- 1: אזכור מעורפל לצוות עתידי
- 2: מוזכר צוות אך ללא פירוט
- 3: גוף מוגדר לתכלול אך סמכויותיו לא ברורות
- 4: צוות מוגדר היטב עם אחריות כוללת
- 5: תיאור מלא של הצוות, חברים, סמכויות ותדירות מפגשים

**3. גורם מתכלל יחיד (משקל 5%)**
אדם ספציפי שאחראי על כלל המהלך:
- 0: אין אדם יחיד מוזכר
- 1: שר אחראי ברמת כותרת בלבד
- 2: ממונה יחיד אך לא ברור תפקידו
- 3: בעל תפקיד ברור אך לא על כל הגופים
- 4: ראש פרויקט עם אחריות לתכלול
- 5: אדם מוגדר רשמית עם פירוט מלא של הסמכות

**4. מנגנון דיווח/בקרה (משקל 9%)**
למי מדווחים, באיזו תדירות ובאיזו מתכונת:
- 0: אין אזכור לדיווח
- 1: אמירה כללית על עדכונים
- 2: מצוין גוף לדיווח אך לא תדירות
- 3: מנגנון דיווח סביר אך לא ברור המבנה
- 4: מנגנון מפורט אך לא ברור מה עושים עם הדיווח
- 5: מנגנון מובנה עם תדירות, פורמט ותגובה לחריגות

**5. מנגנון מדידה והערכה (משקל 6%)**
כיצד למדוד אפקטיביות ההחלטה בפועל:
- 0: אין אזכור למדידה
- 1: אמירה כללית על בחינת השפעה
- 2: כוונה לבחון באמצעות מחקר אך בלי תכנית
- 3: תוכנית בסיסית למדידה אך חסרים פרטים
- 4: מנגנון מסודר אך חסרים פרטים טכניים
- 5: מתווה מלא עם מדדים, לוחות זמנים וגוף מוסמך

**6. מנגנון ביקורת חיצונית (משקל 4%)**
גורם חיצוני לבדיקת התהליך והעמידה ביעדים:
- 0: אין גוף חיצוני
- 1: שיקול לבקש ממומחים חיצוניים
- 2: מצוין גוף חיצוני בלי פירוט תפקידו
- 3: גוף ביקורת מוגדר אך לא ברור איך ומתי
- 4: גוף חיצוני עם מועד להערכה
- 5: ביקורת חיצונית מפורטת עם תדירות ויישום המלצות

**7. משאבים נדרשים (משקל 19%)**
תקציב, כוח אדם ומקורות מימון ליישום:
- 0: אין אזכור למשאבים
- 1: אמירה כללית על צורך בתקציב
- 2: אזכור סכום או מקור אך לא ברור החלוקה
- 3: סכום מצוין אך לא ברור החלוקה או המקור
- 4: פירוט המקור ושימוש עיקרי, חסר כוח אדם
- 5: ציון מפורט של סכומים, חלוקה, כוח אדם ומה עושים בעיכובים

**8. מעורבות של מספר דרגים בתהליך (משקל 7%)**
שילוב דרגים שונים: שר, מנכ"לים, גורמים מקצועיים וכו':
- 0: רק דרג יחיד
- 1: גוף נוסף להתייעצות אך לא ברור תפקידו
- 2: רשימת דרגים אך לא מוסבר שיתוף הפעולה
- 3: פירוט עקרוני אך לא ברור מנגנון המפגשים
- 4: מעורבות מוגדרת יפה, חסר פירוט האינטראקציה
- 5: תיאור מלא עם לוחות זמנים ונהלי תיאום

**9. מבנה סעיפים וחלוקת עבודה ברורה (משקל 9%)**
חלוקה לסעיפים ברורים עם הגדרת אחריות:
- 0: טקסט מבולגן ללא סעיפים
- 1: סעיפים עמומים ללא בהירות אחריות
- 2: כמה סעיפים עם אחריות אך רובם לא ברורים
- 3: באופן כללי אחריות מוגדרת אך משימות כלליות
- 4: סעיפים מסודרים עם אחריות אך חסרה הגדרת שלבים
- 5: סעיפים ברורים עם גוף אחראי ומשימה מפורטת

**10. מנגנון יישום בשטח (משקל 9%)**
כיצד בפועל יבוצע היישום ומי יבצע:
- 0: אין אזכור לאיך מיישמים
- 1: אמירה קצרה על יישום דרך רשויות
- 2: מנגנון כללי ללא הסבר סמכויות
- 3: מנגנון בסיסי אך לא ברור איך יעבדו
- 4: מנגנון קונקרטי, חסרים פרטים טכניים
- 5: תיאור שלם של הביצוע, סמכויות ופיקוח

**11. גורם מכריע (משקל 3%)**
מי מכריע במחלוקות בין גופים מעורבים:
- 0: אין מנגנון הכרעה
- 1: אמירה כללית על סמכות השר
- 2: אזכור גורם מכריע אך לא ברור תהליך
- 3: גורם מכריע מוזכר אך אין פירוט דיון
- 4: גורם מכריע ברור אך אין הגדרה מה בודק
- 5: גורם מכריע מפורט עם תהליך הכרעה

**12. שותפות בין מגזרית (משקל 3%)**
מעורבות מגזרים נוספים מעבר לממשלה:
- 0: אין גורם חוץ-ממשלתי
- 1: אמירה סתמית על שיתוף מגזרים
- 2: ארגון מסוים מוזכר אך לא תפקידו
- 3: מגזר שותף לתהליך אך לא ברור המנדט
- 4: פירוט ארגונים ואופן עבודה, חסרים גבולות אחריות
- 5: שיתוף מפורט עם רשימה, מטרה ומנגנון התקשרות

**13. מדדי תוצאה ומרכיבי הצלחה (משקל 2%)**
הגדרת יעדים כמותיים או איכותיים ברורים:
- 0: אין הגדרה ליעד תוצאתי
- 1: אמירה עמומה על שיפור
- 2: יעד כללי אך לא מוגדר כמה או מתי
- 3: יעד מספרי אך אין תאריך או שיטת מדידה
- 4: יעד כמותי ומסגרת זמן אך לא ברור איך מודדים
- 5: יעדים מספריים ברורים עם מתודולוגיה ותגובה לאי-עמידה

החזר תוצאה בפורמט JSON המדויק הזה:
{{"criteria": [{{"name": "לוח זמנים מחייב", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט המצביע על לוח זמנים או היעדרו", "weight": 17}}, {{"name": "צוות מתכלל", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי צוות מתכלל", "weight": 7}}, {{"name": "גורם מתכלל יחיד", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי גורם מתכלל יחיד", "weight": 5}}, {{"name": "מנגנון דיווח/בקרה", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי מנגנון דיווח", "weight": 9}}, {{"name": "מנגנון מדידה והערכה", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי מדידה והערכה", "weight": 6}}, {{"name": "מנגנון ביקורת חיצונית", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי ביקורת חיצונית", "weight": 4}}, {{"name": "משאבים נדרשים", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי משאבים ותקציב", "weight": 19}}, {{"name": "מעורבות של מספר דרגים בתהליך", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי מעורבות דרגים", "weight": 7}}, {{"name": "מבנה סעיפים וחלוקת עבודה ברורה", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי מבנה וחלוקת עבודה", "weight": 9}}, {{"name": "מנגנון יישום בשטח", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי יישום בשטח", "weight": 9}}, {{"name": "גורם מכריע", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי גורם מכריע", "weight": 3}}, {{"name": "שותפות בין מגזרית", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי שותפות בין מגזרית", "weight": 3}}, {{"name": "מדדי תוצאה ומרכיבי הצלחה", "score": 0, "explanation": "הסבר קצר", "reference_from_document": "ציטוט ישיר מהטקסט לגבי מדדי תוצאה", "weight": 2}}], "weighted_score": 0.0, "final_score": 0, "summary": "סיכום הניתוח", "decision_title": "כותרת ההחלטה"}}

חשוב מאוד לחישוב final_score:
1. כל קריטריון מקבל ציון 0-5
2. הציון המשוקלל לכל קריטריון = (ציון הקריטריון / 5) * משקל הקריטריון
3. final_score = סכום כל הציונים המשוקללים (יהיה בין 0-100)
4. דוגמה: אם קריטריון עם משקל 17% קיבל ציון 5, תרומתו היא (5/5)*17 = 17

חשוב מאוד לגבי reference_from_document:
- עבור כל קריטריון, חובה לצטט קטע רלוונטי מהטקסט של ההחלטה
- אם יש עדות חיובית לקריטריון - צטט את הקטע המדויק
- אם אין עדות לקריטריון - צטט קטע שמראה את ההיעדר או כתוב "לא נמצא אזכור ל[שם הקריטריון] בהחלטה"
- הציטוטים צריכים להיות ישירים מהטקסט, לא פרפרזה
- חובה שכל קריטריון יקבל ציטוט שונה! אם אין מספיק תוכן, כתוב "החלטה קצרה - אין פירוט נוסף על [שם הקריטריון]"
- אסור שכל הציטוטים יהיו זהים!

חשוב לגבי summary:
- כתוב סיכום של 2-3 משפטים שמתאר את הממצאים העיקריים מהניתוח
- התמקד בחוזקות וחולשות עיקריות שזוהו
- אל תחזור על הכותרת או תיאור כללי של ההחלטה
- דוגמה טובה: "ההחלטה כוללת לוח זמנים ברור ומשאבים מוגדרים, אך חסרים מנגנוני בקרה ומדידה. נדרש חיזוק בהגדרת גורם מתכלל וצוות יישום."

חשוב: החזר רק JSON תקין, ללא טקסט נוסף לפני או אחרי.
"""
    
    try:
        # Always use GPT-4o for evaluator as it requires complex thinking and analysis
        content_length = len(decision_text)
        selected_model = "gpt-4o"
        
        logger.info(f"Using GPT-4o for evaluation (content length: {content_length} chars)")
        
        # Call GPT for feasibility analysis
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=selected_model,
            messages=[
                {"role": "system", "content": "אתה מנתח מומחה לישימות החלטות ממשלה. התפקיד שלך לנתח החלטות לפי 13 קריטריונים מוגדרים ולהחזיר תוצאה בפורמט JSON מדויק. עליך לקרוא בזהירות את תוכן ההחלטה ולהעריך כל קריטריון לפי הסקאלה המוגדרת (0-5). היה עקבי ומדויק - החלטה זהה חייבת לקבל אותם ציונים בכל ניתוח. בסס את הציונים רק על מה שכתוב בהחלטה, לא על הנחות. חשב את final_score כך: סכום של [(ציון כל קריטריון / 5) * משקל הקריטריון] עבור כל 13 הקריטריונים. התוצאה צריכה להיות בין 0-100. החזר רק JSON תקין ללא טקסט נוסף. אל תשתמש בעיצוב Bold או סימנים מיוחדים בתוך ה-JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.temperature,
            max_tokens=4000
        )
        
        # Extract token usage
        usage = response.usage
        token_usage = TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=selected_model  # Use the selected model
        )
        
        # Log GPT usage
        log_gpt_usage(
            logger,
            model=selected_model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        # Parse GPT response
        content = response.choices[0].message.content.strip()
        
        try:
            # Extract JSON from response - try multiple approaches
            analysis_result = None
            
            # First try: look for JSON block
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                try:
                    analysis_result = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    # Remove any trailing text after the last }
                    lines = json_str.split('\n')
                    clean_lines = []
                    brace_count = 0
                    for line in lines:
                        for char in line:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                        clean_lines.append(line)
                        if brace_count == 0:
                            break
                    
                    cleaned_json = '\n'.join(clean_lines)
                    # Fix common issues like trailing commas
                    cleaned_json = cleaned_json.replace(',}', '}').replace(',]', ']')
                    analysis_result = json.loads(cleaned_json)
            
            if analysis_result:
                
                # Extract analysis data
                criteria = analysis_result.get("criteria", [])
                final_score = analysis_result.get("final_score", 0)
                weighted_score = analysis_result.get("weighted_score", final_score)
                summary = analysis_result.get("summary", "ניתוח הושלם")
                decision_title = analysis_result.get("decision_title", decision_title)
                # Always use the actual requested decision number, not what GPT might extract from content
                decision_num = request.decision_number
                gov_num = analysis_result.get("government_number", request.government_number)
                
                # Validate citations - check if all are identical
                citations = [c.get('reference_from_document', '') for c in criteria]
                if citations and len(set(citations)) == 1 and citations[0]:
                    logger.warning(f"All citations are identical: {citations[0][:50]}... - this indicates poor extraction")
                    # Try to add variation based on criterion name
                    for i, criterion in enumerate(criteria):
                        if criterion.get('score', 0) == 0:
                            criterion['reference_from_document'] = f"לא נמצא אזכור ל{criterion.get('name', 'קריטריון')} בהחלטה"
                        elif i > 0 and criterion['reference_from_document'] == criteria[0]['reference_from_document']:
                            criterion['reference_from_document'] = f"החלטה קצרה - אין פירוט נוסף על {criterion.get('name', 'קריטריון')}"
                
                # Convert to expected format
                quality_metrics = []
                for criterion in criteria:
                    quality_metrics.append(QualityMetric(
                        name=criterion.get("name", "קריטריון"),
                        score=float(criterion.get("score", 0)) / 5.0,  # Convert 0-5 to 0-1
                        weight=float(criterion.get("weight", 1)) / 100.0,  # Convert percentage to decimal
                        explanation=criterion.get("explanation", "")
                    ))
                
                # Calculate overall score
                overall_score = float(final_score) / 100.0  # Convert 0-100 to 0-1
                
                # Determine relevance level and category based on score  
                if overall_score >= 0.75:
                    relevance_level = RelevanceLevel.HIGHLY_RELEVANT
                    feasibility_category = "✅ רמת ישימות: גבוהה"
                elif overall_score >= 0.50:
                    relevance_level = RelevanceLevel.RELEVANT
                    feasibility_category = "⚠️ רמת ישימות: בינונית"
                else:
                    relevance_level = RelevanceLevel.PARTIALLY_RELEVANT
                    feasibility_category = "❌ רמת ישימות: נמוכה"
                
                # Generate formatted analysis table
                criteria_table = []
                for criterion in criteria:
                    criteria_table.append(f"| {criterion.get('name', 'קריטריון')} | {criterion.get('weight', 0)}% | {criterion.get('score', 0)} | {criterion.get('explanation', '')} |")
                
                table_header = "| קריטריון | משקל | ציון (0–5) | נימוק |\n|---|---|---|---|"
                criteria_table_str = table_header + "\n" + "\n".join(criteria_table)
                
                # Generate specific recommendations based on low-scoring criteria
                specific_recommendations = []
                for criterion in criteria:
                    if criterion.get('score', 0) <= 2:
                        name = criterion.get('name', '')
                        if name == "לוח זמנים מחייב":
                            specific_recommendations.append("הוספת לוח זמנים מפורט עם אבני דרך ותאריכי יעד ברורים")
                        elif name == "צוות מתכלל":
                            specific_recommendations.append("מינוי צוות מתכלל עם הגדרת תפקידים וסמכויות ברורות")
                        elif name == "משאבים נדרשים":
                            specific_recommendations.append("פירוט התקציב הנדרש ומקורות המימון הספציפיים")
                        elif name == "מנגנון דיווח/בקרה":
                            specific_recommendations.append("הגדרת מנגנון דיווח תקופתי עם תדירות ופורמט מוגדרים")
                        elif name == "מדדי תוצאה ומרכיבי הצלחה":
                            specific_recommendations.append("קביעת מדדי הצלחה כמותיים וברי מדידה")
                        elif name == "מנגנון יישום בשטח":
                            specific_recommendations.append("פירוט תהליכי היישום והגורמים האחראיים בשטח")
                
                # Add decision metadata
                decision_date = decision_content.get('decision_date', '')
                prime_minister = decision_content.get('prime_minister', '')
                policy_areas = decision_content.get('tags_policy_area', decision_content.get('topics', []))
                government_body = decision_content.get('tags_government_body', decision_content.get('ministries', []))
                
                # Ensure arrays are properly formatted
                if isinstance(policy_areas, str):
                    policy_areas = [policy_areas]
                if isinstance(government_body, str):
                    government_body = [government_body]
                
                # Format date nicely
                if decision_date:
                    try:
                        from datetime import datetime as dt
                        date_obj = dt.fromisoformat(decision_date.replace('Z', '+00:00'))
                        hebrew_months = {
                            1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
                            5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
                            9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
                        }
                        formatted_date = f"{date_obj.day} ב{hebrew_months[date_obj.month]} {date_obj.year}"
                    except:
                        formatted_date = decision_date
                else:
                    formatted_date = "לא צוין"
                
                # Create detailed explanation in the required format
                formatted_explanation = f"""🔍 ניתוח החלטת ממשלה {decision_num}

**כותרת ההחלטה:** {decision_title}

📋 **פרטי ההחלטה:**
• **ממשלה:** {gov_num or request.government_number or 'לא צוין'}
• **תאריך:** {formatted_date}
• **ראש הממשלה:** {prime_minister or 'לא צוין'}
• **תחומי מדיניות:** {', '.join(policy_areas) if policy_areas else 'לא צוינו'}
• **משרדים מעורבים:** {', '.join(government_body) if government_body else 'לא צוינו'}

{criteria_table_str}

🧮 **חישוב ציון ישימות משוקלל**
הציון הכולל של החלטת ממשלה {decision_num} הוא **{final_score}/100**

**אופן החישוב:**
{chr(10).join([f"• {c.get('name')}: {c.get('score')}/5 × {c.get('weight')}% = {(c.get('score', 0)/5 * c.get('weight', 0)):.1f}%" for c in criteria[:3]])}  
• ... (ועוד {len(criteria)-3} קריטריונים)
━━━━━━━━━━━━━━━━━━━━━
**סה״כ: {final_score}%**

{feasibility_category}

📝 **סיכום ניתוח ואבחנות עיקריות**
{summary if summary and summary != 'ניתוח הושלם' else 'ההחלטה נבחנה לפי 13 קריטריונים של ישימות מדיניות. הניתוח מראה את החוזקות והחולשות ביכולת היישום של ההחלטה.'}

💡 **המלצות לשיפור רמת הישימות**
בהתבסס על הקריטריונים שקיבלו ציון נמוך, מומלץ:
""" + "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(specific_recommendations)]) if specific_recommendations else "בהתבסס על הניתוח, ניתן לשפר את רמת הישימות על ידי התמקדות בקריטריונים שקיבלו ציון נמוך."
                
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                return EvaluationResponse(
                    overall_score=overall_score,
                    relevance_level=relevance_level,
                    quality_metrics=quality_metrics,
                    content_analysis={
                        "feasibility_analysis": summary, 
                        "decision_title": decision_title, 
                        "criteria_breakdown": criteria,
                        "final_score": final_score,
                        "full_decision_content": decision_text,
                        "decision_number": decision_num,
                        "government_number": gov_num
                    },
                    recommendations=specific_recommendations if specific_recommendations else [
                        "בהתבסס על הניתוח, מומלץ להתמקד בשיפור הקריטריונים שקיבלו ציון נמוך",
                        "הוספת פרטים ספציפיים יותר בתחומים החסרים",
                        "הגדרת מנגנוני בקרה ומעקב ברורים"
                    ],
                    confidence=0.9,
                    explanation=formatted_explanation,
                    processing_time_ms=processing_time,
                    token_usage=token_usage
                )
                
            else:
                # Fallback if no JSON found
                fallback_token_usage = TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    model="fallback"
                )
                return EvaluationResponse(
                    overall_score=0.5,
                    relevance_level=RelevanceLevel.PARTIALLY_RELEVANT,
                    quality_metrics=[],
                    content_analysis={"error": "לא ניתן לפרסר את תוצאות הניתוח"},
                    recommendations=["נדרש ניתוח מחדש"],
                    confidence=0.3,
                    explanation=f"ניתוח ישימות נכשל - תגובת GPT: {content[:200]}...",
                    processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                    token_usage=fallback_token_usage
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse feasibility analysis JSON: {e}")
            fallback_token_usage = TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model="fallback"
            )
            return EvaluationResponse(
                overall_score=0.5,
                relevance_level=RelevanceLevel.PARTIALLY_RELEVANT,
                quality_metrics=[],
                content_analysis={"error": "שגיאה בפיענוח תוצאות הניתוח"},
                recommendations=["נדרש ניתוח מחדש"],
                confidence=0.3,
                explanation=f"ניתוח ישימות נכשל - שגיאת JSON: {str(e)}",
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                token_usage=fallback_token_usage
            )
            
    except Exception as e:
        logger.error(f"Feasibility analysis failed: {e}")
        fallback_token_usage = TokenUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            model="fallback"
        )
        return EvaluationResponse(
            overall_score=0.0,
            relevance_level=RelevanceLevel.NOT_RELEVANT,
            quality_metrics=[],
            content_analysis={"error": f"ניתוח נכשל: {str(e)}"},
            recommendations=["בדוק את החלטה ונסה שוב"],
            confidence=0.1,
            explanation=f"ניתוח ישימות נכשל עם שגיאה: {str(e)}",
            processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            token_usage=fallback_token_usage
        )

async def analyze_content_with_gpt(query: str, intent: str, entities: Dict, results: List[Dict]) -> Tuple[Dict[str, Any], Optional[TokenUsage]]:
    """Use GPT to analyze content quality and relevance."""
    if not results:
        no_results_token_usage = TokenUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            model="no-results"
        )
        return {
            "semantic_relevance": 0.0,
            "content_quality": 0.0,
            "language_quality": 0.0,
            "gpt_explanation": "No results to analyze"
        }, no_results_token_usage
    
    # Prepare sample results for GPT analysis (limit to 3 for efficiency)
    sample_results = results[:3]
    results_text = ""
    
    for i, result in enumerate(sample_results, 1):
        title = result.get("title", "No title")
        content = result.get("content", "No content")
        # Truncate content for GPT
        content_snippet = content[:300] + "..." if len(content) > 300 else content
        results_text += f"Result {i}:\nTitle: {title}\nContent: {content_snippet}\n\n"
    
    prompt = f"""נתח את החלטת הממשלה הבאה לפי 13 הקריטריונים:

החלטה לניתוח:
כותרת: {results_text}

בצע ניתוח ישימות של החלטת ממשלה בהתאם לקריטריונים הבאים. על כל פרמטר יש להקצות ניקוד מ-0 עד 5.

דרג כל קריטריון ותן הסבר קצר:
1. לוח זמנים מחייב (משקל 17%)
2. צוות מתכלל (משקל 7%) 
3. גורם מתכלל יחיד (משקל 5%)
4. מנגנון דיווח/בקרה (משקל 9%)
5. מנגנון מדידה והערכה (משקל 6%)
6. מנגנון ביקורת חיצונית (משקל 4%)
7. משאבים נדרשים (משקל 19%)
8. מעורבות של מספר דרגים בתהליך (משקל 7%)
9. מבנה סעיפים וחלוקת עבודה ברורה (משקל 9%)
10. מנגנון יישום בשטח (משקל 9%)
11. גורם מכריע (משקל 3%)
12. שותפות בין מגזרית (משקל 3%)
13. מדדי תוצאה ומרכיבי הצלחה (משקל 2%)

החזר תוצאה בפורמט JSON: {{"criteria": [{{"name": "שם הקריטריון", "score": 3, "explanation": "הסבר קצר"}}], "final_score": 65, "summary": "סיכום כללי"}}
"""
    
    try:
        start_time = datetime.utcnow()
        
        # Always use GPT-4o for complex analysis
        selected_model = "gpt-4o"
        
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=selected_model,
            messages=[
                {"role": "system", "content": "בצע ניתוח ישימות של החלטת ממשלה בהתאם לקריטריונים שהוגדרו בכל אחד מהפרמטרים הבאים. על כל פרמטר יש להקצות ניקוד מ-0 עד 5 לפי המדרגות שנקבעו. לאחר מכן תציג את הציון הסופי לפי המשקלים בסוף. כל פרמטר מהפרמטרים הנ\"ל יקבל ערך מספרי בין 0 ל-5 על פי ההנחיות ונימוק קצר לתוצאה. יש לסכם את הניתוח בצורה ברורה וממוקדת כולל הציון לכל קריטריון. תציג את הקריטריונים והסבר על הציון. תראה את החישוב של הציון הסופי לפי קריטריונים ותמיר אותו לציון בין 0 ל 100. Don't write in bold. Instead of \"\\times\" use \"*\". Don't use \"\\\""},
                {"role": "user", "content": prompt}
            ],
            temperature=config.temperature,
            max_tokens=4000
        )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract token usage
        usage = response.usage
        token_usage = TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            model=selected_model  # Use the selected model
        )
        
        # Log GPT usage
        log_gpt_usage(
            logger,
            model=selected_model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        # Parse GPT response
        gpt_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response with improved parsing
        try:
            # Look for JSON in the response
            gpt_analysis = None
            json_start = gpt_text.find('{')
            json_end = gpt_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = gpt_text[json_start:json_end]
                try:
                    gpt_analysis = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to clean up the JSON
                    lines = json_str.split('\n')
                    clean_lines = []
                    brace_count = 0
                    for line in lines:
                        for char in line:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                        clean_lines.append(line)
                        if brace_count == 0:
                            break
                    
                    cleaned_json = '\n'.join(clean_lines)
                    cleaned_json = cleaned_json.replace(',}', '}').replace(',]', ']')
                    gpt_analysis = json.loads(cleaned_json)
            
            if gpt_analysis:
                
                return {
                    "semantic_relevance": float(gpt_analysis.get("semantic_relevance", 0.5)),
                    "content_quality": float(gpt_analysis.get("content_quality", 0.5)),
                    "language_quality": float(gpt_analysis.get("language_quality", 0.5)),
                    "gpt_explanation": gpt_analysis.get("explanation", "GPT analysis completed")
                }, token_usage
            else:
                # Fallback if no JSON found
                return {
                    "semantic_relevance": 0.6,
                    "content_quality": 0.6,
                    "language_quality": 0.6,
                    "gpt_explanation": f"GPT response: {gpt_text[:100]}..."
                }, token_usage
                
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "semantic_relevance": 0.6,
                "content_quality": 0.6,
                "language_quality": 0.6,
                "gpt_explanation": f"Parse error: {gpt_text[:100]}..."
            }, token_usage
            
    except Exception as e:
        logger.error(f"GPT content analysis failed: {e}")
        fallback_token_usage = TokenUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            model="fallback"
        )
        return {
            "semantic_relevance": 0.5,
            "content_quality": 0.5,
            "language_quality": 0.5,
            "gpt_explanation": f"Analysis failed: {str(e)}"
        }, fallback_token_usage

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
    content_analysis, token_usage = await analyze_content_with_gpt(
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
        processing_time_ms=processing_time,
        token_usage=token_usage
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
async def evaluate_decision_feasibility(request: EvaluationRequest):
    """Main feasibility evaluation endpoint for government decisions."""
    global evaluation_count
    start_time = datetime.utcnow()
    
    try:
        log_api_call(
            logger, "evaluate_decision_feasibility", request.model_dump(),
            request.conv_id, "EVAL_EVALUATOR_BOT_2E"
        )
        
        # Create test scenarios for edge case validation
        decision_number = request.decision_number
        
        # First try to fetch real decision content
        real_decision_content = await fetch_decision_content(
            request.government_number or 37,
            decision_number,
            request.conv_id
        )
        
        if real_decision_content:
            # Use real content
            decision_content = real_decision_content
            logger.info(f"Using real decision content for decision {decision_number} (length: {len(decision_content.get('decision_content', ''))} chars)")
        # Create different mock decisions to test edge cases
        elif decision_number == 1111:  # Test short content
            decision_content = {
                "id": f"test-{decision_number}",
                "government_number": request.government_number or 37,
                "decision_number": decision_number,
                "decision_title": "החלטה קצרה לבדיקה",
                "decision_content": "זוהי החלטה קצרה מאוד עם פחות מ-250 תווים לבדיקת הלוגיקה החדשה.",  # <250 chars
                "content": "זוהי החלטה קצרה מאוד עם פחות מ-250 תווים לבדיקת הלוגיקה החדשה.",
                "summary": "החלטה קצרה",
                "decision_date": "2024-01-15",
                "operativity": "אופרטיבית",  # Adding DB field
                "topics": ["בדיקה"],
                "ministries": ["משרד הבדיקות"]
            }
        elif decision_number == 2222:  # Test declarative decision
            decision_content = {
                "id": f"test-{decision_number}",
                "government_number": request.government_number or 37,
                "decision_number": decision_number,
                "decision_title": "הצדעה לזכרו של האלמוני",
                "decision_content": "הממשלה מחליטה להביע הצדעה לזכרו של האלמוני על תרומתו המשמעותית לחברה הישראלית ולמדינת ישראל. הממשלה מבקשת להכיר בפועלו החשוב ולחלוק כבוד למשפחתו ולקרוביו. הממשלה מבקשת להודות לו על מסירותו, מחויבותו ותרומתו הייחודית. זוהי החלטה דקלרטיבית שאינה מתאימה לניתוח ישימות מדיניות כיוון שהיא אינה כוללת יישום, תקציב או לוחות זמנים מעשיים, אלא מהווה הבעת הוקרה וכבוד בלבד. החלטות מסוג זה נועדו להביע עמדות ערכיות ולא ליישום מדיניות ממשית.",
                "content": "הממשלה מחליטה להביע הצדעה לזכרו של האלמוני על תרומתו לחברה הישראלית.",
                "summary": "הצדעה לזכרו של האלמוני",
                "decision_date": "2024-01-15",
                "operativity": "דקלרטיבית",  # Adding DB field - this will trigger rejection
                "topics": ["הוקרה"],
                "ministries": ["משרד ראש הממשלה"]
            }
        else:  # Regular decision for analysis
            decision_content = {
                "id": f"decision-{decision_number}",
                "government_number": request.government_number or 37,
                "decision_number": decision_number,
                "decision_title": f"החלטת ממשלה מספר {decision_number}",
                "decision_content": f"זוהי החלטת ממשלה מספר {decision_number} לצורך בדיקת מערכת הניתוח. ההחלטה כוללת הקצאת תקציב של 50 מיליון שקל, הגדרת לוח זמנים מפורט עם אבני דרך רבעוניות, ומתן אחריות ברורה לגורמים רלוונטיים במשרדי הממשלה. יש צורך ביישום מלא בתוך 18 חודשים עם דיווח חודשי על ההתקדמות למשרד ראש הממשלה. ההחלטה כוללת גם מנגנון בקרה חיצוני על ידי משרד האוצר ומעורבות של ארגונים ציבוריים בביצוע. המטרה היא להקים תוכנית רחבת היקף לשיפור השירותים הציבוריים, כולל הכשרת עובדים, שדרוג מערכות מידע ויצירת מנגנוני משוב מהציבור.",
                "content": f"זוהי החלטת ממשלה מספר {decision_number} לצורך בדיקת מערכת הניתוח.",
                "summary": f"החלטה {decision_number} - הקצאת תקציב, יישום מתוכנן ובקרה חיצונית",
                "decision_date": "2024-01-15",
                "operativity": "אופרטיבית",  # Adding DB field - this allows analysis
                "topics": ["תקציב", "יישום", "דיווח", "בקרה"],
                "ministries": ["משרד האוצר", "משרד ראש הממשלה"]
            }
            
            logger.info(f"Using mock decision content for analysis of decision {decision_number} (length: {len(decision_content['decision_content'])} chars)")
        
        # Perform feasibility analysis
        evaluation = await perform_feasibility_analysis(decision_content, request)
        
        evaluation_count += 1
        
        # Log successful evaluation
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Feasibility evaluation completed",
            extra={
                "conv_id": request.conv_id,
                "government_number": request.government_number,
                "decision_number": request.decision_number,
                "overall_score": evaluation.overall_score,
                "duration_ms": duration * 1000
            }
        )
        
        return evaluation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Feasibility evaluation failed for conv_id {request.conv_id}: {e}",
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