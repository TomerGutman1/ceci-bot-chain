#!/usr/bin/env python3
"""
CLARIFY Clarification Bot 2C - Generate clarification questions for ambiguous queries.

This bot analyzes ambiguous or incomplete queries and generates appropriate 
clarification questions to help users provide more specific information
for better search results.
"""

import os
import asyncio
import openai
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.logging import setup_logging
from common.config import get_config

# Initialize logging and config
logger = setup_logging('CLARIFY_CLARIFY_BOT_2C')
config = get_config('CLARIFY_CLARIFY_BOT_2C')

# Configure OpenAI
openai.api_key = config.openai_api_key

app = FastAPI(
    title="CLARIFY_CLARIFY_BOT_2C",
    description="Clarification Question Generation Service",
    version="1.0.0"
)

class ClarificationType(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    MISSING_ENTITIES = "missing_entities"
    AMBIGUOUS_TIME = "ambiguous_time"
    AMBIGUOUS_TOPIC = "ambiguous_topic"
    VAGUE_INTENT = "vague_intent"
    MULTIPLE_INTERPRETATIONS = "multiple_interpretations"

@dataclass
class ClarificationQuestion:
    question: str
    type: ClarificationType
    suggested_responses: List[str]
    priority: int  # 1-3, lower is higher priority

class ClarificationRequest(BaseModel):
    conv_id: str
    original_query: str
    intent: str
    entities: Dict[str, Any]
    confidence_score: float
    clarification_type: str
    context_history: Optional[List[str]] = []

class ClarificationResponse(BaseModel):
    success: bool
    conv_id: str
    clarification_questions: List[Dict[str, Any]]
    suggested_refinements: List[str]
    explanation: str
    confidence: float

# Clarification question templates
CLARIFICATION_TEMPLATES = {
    ClarificationType.LOW_CONFIDENCE: [
        "אני לא בטוח שהבנתי את השאילתא שלך. האם אתה מחפש:",
        "יכול להיות שהתכוונת לאחד מהבאים:",
        "כדי לעזור לך טוב יותר, אפשר לוודא מה אתה מחפש:"
    ],
    
    ClarificationType.MISSING_ENTITIES: [
        "כדי לחפש החלטות ממשלה, צריך פרטים נוספים:",
        "החיפוש יהיה מדויק יותר אם תציין:",
        "איזה מהפרטים הבאים יכול לעזור לך:"
    ],
    
    ClarificationType.AMBIGUOUS_TIME: [
        "איזה תקופת זמן אתה מתכוון?",
        "כדי לחפש החלטות בתקופה נכונה, אפשר לוודא:",
        "תוכל לפרט על התקופה שאתה מחפש?"
    ],
    
    ClarificationType.AMBIGUOUS_TOPIC: [
        "איזה נושא ספציפי אתה מחפש?",
        "יש כמה נושאים שיכולים להתאים, איזה מהם:",
        "כדי לחפש בנושא הנכון, תוכל לבחור:"
    ],
    
    ClarificationType.VAGUE_INTENT: [
        "מה בדיוק אתה רוצה לעשות?",
        "איך אני יכול לעזור לך עם זה?",
        "תוכל להסביר מה אתה מחפש?"
    ],
    
    ClarificationType.MULTIPLE_INTERPRETATIONS: [
        "יש כמה דרכים להבין את השאילתא שלך:",
        "איזה מהפירושים הבאים נכון:",
        "כדי לתת לך תשובה מדויקת, תוכל לבחור:"
    ]
}

# Government and ministry suggestions
GOVERNMENT_SUGGESTIONS = [
    "ממשלה 37 (נתניהו הנוכחית)",
    "ממשלה 36 (בנט-לפיד)",
    "ממשלה 35 (נתניהו הקודמת)",
    "ממשלה 34 (נתניהו)",
    "כל הממשלות"
]

MINISTRY_SUGGESTIONS = [
    "משרד החינוך",
    "משרד הביטחון", 
    "משרד הבריאות",
    "משרד האוצר",
    "משרד המשפטים",
    "משרד הפנים",
    "משרד התחבורה",
    "משרד הסביבה"
]

TOPIC_SUGGESTIONS = [
    "חינוך ו תרבות",
    "ביטחון ו צבא",
    "כלכלה ו תקציב",
    "בריאות ו רפואה",
    "תחבורה ו תשתיות",
    "סביבה ו אנרגיה",
    "משפט ו חקיקה",
    "רווחה ו חברה"
]

TIME_SUGGESTIONS = [
    "השנה האחרונה (2023-2024)",
    "שנתיים אחרונות (2022-2024)", 
    "חמש שנים אחרונות (2019-2024)",
    "כל התקופות",
    "תקופה ספציפית (תאריך מדויק)"
]

async def generate_clarification_with_gpt(
    query: str, 
    intent: str, 
    entities: Dict, 
    clarification_type: ClarificationType,
    context_history: List[str] = []
) -> Dict[str, Any]:
    """Generate clarification questions using GPT-4."""
    
    try:
        # Build context from conversation history
        context_str = ""
        if context_history:
            context_str = f"הקשר השיחה: {' | '.join(context_history[-3:])}\n"  # Last 3 messages
        
        # Create system prompt for Hebrew clarification
        system_prompt = f"""אתה עוזר בעברית שמתמחה ביצירת שאלות הבהרה למערכת חיפוש החלטות ממשלה.

המטרה: לעזור למשתמשים לנסח שאילתות מדויקות יותר כשהשאילתא המקורית מעורפלת או חסרה מידע.

טיפוס הבהרה נדרש: {clarification_type.value}

הוראות:
1. צור 2-3 שאלות הבהרה קצרות ומדויקות
2. הצע 3-4 תשובות אפשריות לכל שאלה
3. התמקד במידע החסר החשוב ביותר לחיפוש
4. השתמש בעברית פשוטה וברורה
5. תן עדיפות לשאלות שיכולות לשפר את דיוק החיפוש

דוגמאות לסוגי שאלות:
- זמן: "איזה תקופה אתה מחפש?"
- נושא: "איזה תחום מעניין אותך?"
- ממשלה: "איזה ממשלה מתכוון?"
- משרד: "איזה משרד רלוונטי?"

החזר תשובה בפורמט JSON עם המפתחות:
- questions: רשימה של שאלות עם type, question, suggestions
- explanation: הסבר קצר למה צריך את ההבהרה
"""

        user_prompt = f"""{context_str}השאילתא המקורית: "{query}"
כוונה מזוהה: {intent}
ישויות מזוהות: {entities}
דרגת ביטחון: {len(entities)}/5 ישויות

צור שאלות הבהרה מתאימות."""

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.3  # Lower temperature for more consistent clarifications
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse as JSON, fall back to structured format
        try:
            import json
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback to manual parsing if GPT didn't return valid JSON
            return {
                "questions": [
                    {
                        "type": clarification_type.value,
                        "question": "תוכל לפרט יותר על מה אתה מחפש?",
                        "suggestions": ["פרטים נוספים", "נושא ספציפי", "תקופת זמן"]
                    }
                ],
                "explanation": "נדרשים פרטים נוספים לחיפוש מדויק יותר"
            }
            
    except Exception as e:
        logger.error(f"GPT clarification generation failed: {e}")
        # Return fallback clarification
        return await generate_fallback_clarification(query, intent, entities, clarification_type)

async def generate_fallback_clarification(
    query: str,
    intent: str, 
    entities: Dict,
    clarification_type: ClarificationType
) -> Dict[str, Any]:
    """Generate fallback clarification questions using template-based approach."""
    
    questions = []
    templates = CLARIFICATION_TEMPLATES.get(clarification_type, [])
    
    if clarification_type == ClarificationType.MISSING_ENTITIES:
        missing_info = []
        if "government_number" not in entities:
            missing_info.append("government")
        if "topic" not in entities and "ministries" not in entities:
            missing_info.append("topic")
        if intent == "search" and "date_range" not in entities:
            missing_info.append("time")
            
        for info_type in missing_info[:2]:  # Limit to 2 questions
            if info_type == "government":
                questions.append({
                    "type": "missing_government",
                    "question": "איזה ממשלה אתה מחפש?",
                    "suggestions": GOVERNMENT_SUGGESTIONS
                })
            elif info_type == "topic":
                questions.append({
                    "type": "missing_topic", 
                    "question": "איזה נושא או משרד מעניין אותך?",
                    "suggestions": TOPIC_SUGGESTIONS + MINISTRY_SUGGESTIONS[:4]
                })
            elif info_type == "time":
                questions.append({
                    "type": "missing_time",
                    "question": "איזה תקופת זמן אתה מחפש?", 
                    "suggestions": TIME_SUGGESTIONS
                })
    
    elif clarification_type == ClarificationType.AMBIGUOUS_TIME:
        questions.append({
            "type": "time_clarification",
            "question": "תוכל לפרט על התקופה שאתה מחפש?",
            "suggestions": TIME_SUGGESTIONS
        })
    
    elif clarification_type == ClarificationType.AMBIGUOUS_TOPIC:
        questions.append({
            "type": "topic_clarification", 
            "question": "איזה נושא ספציפי אתה מחפש?",
            "suggestions": TOPIC_SUGGESTIONS
        })
        
    elif clarification_type == ClarificationType.LOW_CONFIDENCE:
        if not entities:
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
        
    elif clarification_type == ClarificationType.VAGUE_INTENT:
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
        "explanation": f"נדרשים פרטים נוספים לחיפוש מדויק ({clarification_type.value})"
    }

async def generate_suggested_refinements(
    query: str,
    intent: str, 
    entities: Dict,
    clarification_type: ClarificationType
) -> List[str]:
    """Generate suggested query refinements."""
    
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CLARIFY_CLARIFY_BOT_2C"}

@app.post("/clarify", response_model=ClarificationResponse)
async def clarify_query(request: ClarificationRequest):
    """Generate clarification questions for ambiguous queries."""
    
    try:
        logger.info(f"Processing clarification request: {request.conv_id}")
        
        # Determine clarification type
        clarification_type = ClarificationType(request.clarification_type)
        
        # Generate clarification questions using GPT or fallback
        clarification_data = await generate_clarification_with_gpt(
            request.original_query,
            request.intent,
            request.entities,
            clarification_type,
            request.context_history or []
        )
        
        # Generate suggested refinements
        refinements = await generate_suggested_refinements(
            request.original_query,
            request.intent,
            request.entities, 
            clarification_type
        )
        
        # Calculate confidence based on number of questions and clarity
        confidence = 0.8
        if len(clarification_data.get("questions", [])) == 1:
            confidence = 0.9
        if request.confidence_score < 0.5:
            confidence = 0.7
            
        response = ClarificationResponse(
            success=True,
            conv_id=request.conv_id,
            clarification_questions=clarification_data.get("questions", []),
            suggested_refinements=refinements,
            explanation=clarification_data.get("explanation", "נדרשים פרטים נוספים"),
            confidence=confidence
        )
        
        logger.info(f"Generated {len(response.clarification_questions)} clarification questions")
        return response
        
    except Exception as e:
        logger.error(f"Error in clarify_query: {e}")
        raise HTTPException(status_code=500, detail=f"Clarification generation failed: {str(e)}")

@app.get("/templates")
async def get_clarification_templates():
    """Get available clarification question templates."""
    
    templates_info = {}
    for clarification_type, templates in CLARIFICATION_TEMPLATES.items():
        templates_info[clarification_type.value] = {
            "templates": templates,
            "count": len(templates)
        }
    
    return {
        "clarification_types": templates_info,
        "government_suggestions": GOVERNMENT_SUGGESTIONS,
        "ministry_suggestions": MINISTRY_SUGGESTIONS,
        "topic_suggestions": TOPIC_SUGGESTIONS,
        "time_suggestions": TIME_SUGGESTIONS,
        "total_templates": sum(len(t) for t in CLARIFICATION_TEMPLATES.values())
    }

if __name__ == "__main__":
    import uvicorn
    
    port = config.port
    logger.info(f"Starting CLARIFY_CLARIFY_BOT_2C on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        reload=True
    )