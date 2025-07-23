from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import sys
from datetime import datetime
import logging
from openai import OpenAI
import json
import re
import hashlib
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Decision Guide Bot")

# Simple in-memory cache for validation results
validation_cache = {}
analysis_cache = {}  # Cache for analysis results
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

# Document size limits
WARN_CHAR_LIMIT = 50000  # ~20 pages
MAX_CHAR_LIMIT = 500000  # ~200 pages (increased from 100K)
CHUNK_SIZE = 30000  # Size for each chunk when splitting (safe for Hebrew)
CHUNK_OVERLAP = 2000  # Overlap between chunks to maintain context

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Request/Response models
class DocumentInfo(BaseModel):
    type: str  # 'text' or 'file'
    originalName: str
    size: int

class AnalyzeRequest(BaseModel):
    text: str
    documentInfo: DocumentInfo
    requestId: str

class CriteriaScore(BaseModel):
    criterion: str
    score: int  # 0-5 scale (will be converted to 1-10 in service)
    explanation: str
    reference_from_document: Optional[str] = None  # ציטוט מהמסמך
    specific_improvement: Optional[str] = None  # הצעה ספציפית לשיפור

class AnalyzeResponse(BaseModel):
    criteria_scores: List[CriteriaScore]
    recommendations: List[str]
    model_used: str
    misuse_detected: bool = False
    misuse_message: Optional[str] = None
    retry_status: Optional[str] = None
    progress_status: Optional[str] = None  # For reporting progress on large documents
    chunk_info: Optional[Dict[str, Any]] = None  # Information about chunk processing

# Criteria definitions
CRITERIA = [
    "לוח זמנים מחייב",
    "צוות מתכלל",
    "גורם מתכלל יחיד",
    "מנגנון דיווח/בקרה",
    "מנגנון מדידה והערכה",
    "מנגנון ביקורת חיצונית",
    "משאבים נדרשים",
    "מעורבות של מספר דרגים בתהליך",
    "מבנה סעיפים וחלוקת עבודה ברורה",
    "מנגנון יישום בשטח",
    "גורם מכריע",
    "שותפות בין מגזרית",
    "מדדי תוצאה ומרכיבי הצלחה"
]

def create_evaluation_prompt(text: str) -> str:
    """Create the evaluation prompt based on the eval_prompt.md specifications"""
    prompt = f"""
אתה מומחה בניתוח החלטות ממשלה בישראל. המטרה שלך היא לעזור למשתמשים לשפר את ניסוח החלטות הממשלה שלהם.

**הנחיה חשובה**: רוב המשתמשים משתמשים במערכת בתום לב ומעלים טיוטות של החלטות ממשלה או מסמכי מדיניות. 
**היה נדיב ומקל בהגדרה** - אם המסמך נראה כמו טיוטה, הצעה, או מסמך מדיניות כלשהו, קבל אותו לניתוח.

**קבל לניתוח**:
- כל מסמך שעוסק במדיניות ציבורית
- טיוטות והצעות (גם אם לא מושלמות)
- מסמכי עבודה ממשלתיים
- הצעות חוק או תקנות
- תוכניות עבודה של משרדי ממשלה
- כל מסמך שנראה קשור לעבודה ממשלתית

**דחה רק במקרים ברורים**:
- כרטיסי טיסה
- קורות חיים אישיים
- חשבוניות וקבלות
- מסמכים רפואיים אישיים
- ספאם או טקסט אקראי

**ברירת מחדל**: אם יש ספק, קבל את המסמך לניתוח (is_government_decision: true).

אם זו כן החלטת ממשלה, נתח אותה לפי 13 הקריטריונים הבאים. לכל קריטריון:
1. תן ציון מ-0 עד 5 (היה עקבי בציונים - השתמש באותם סטנדרטים לכל הערכה)
2. כתוב הסבר קצר (2-3 משפטים)
3. צטט את החלק הרלוונטי מהמסמך (אם קיים) - הכנס את הציטוט בשדה "reference_from_document"
4. תן הצעה ספציפית איך לשפר את הנושא - הכנס את ההצעה בשדה "specific_improvement"

**חשוב**: הקריטריונים החשובים ביותר הם:
- משאבים נדרשים (הכי חשוב)
- לוח זמנים מחייב (חשוב מאוד)
- מנגנון דיווח/בקרה, מבנה סעיפים, ומנגנון יישום בשטח (חשובים)
- שאר הקריטריונים פחות קריטיים אך עדיין חשובים

**חשוב מאוד**: השתמש בדיוק בשמות הקריטריונים כפי שהם מופיעים למטה, כולל המילים "בתהליך" ו"ברורה" במקום הרלוונטי.

הטקסט לניתוח:
{text}

הקריטריונים לניתוח:

1. לוח זמנים מחייב (0-5):
   - 0: אין שום אזכור של זמן ביצוע
   - 1: אמירה כללית כמו "בהקדם"
   - 2: תאריך אחד לסעיף שולי
   - 3: זמנים לרוב הסעיפים אך לא מחייבים
   - 4: תאריכים ברורים לכל משימה עיקרית
   - 5: תאריכים מחייבים עם הגדרת השלכות לאי-עמידה

2. צוות מתכלל (0-5):
   - 0: אין צוות מתכלל
   - 1: אזכור מעורפל לצוות עתידי
   - 2: צוות מוזכר ללא פירוט
   - 3: צוות מוגדר אך ללא סמכויות ברורות
   - 4: צוות מוגדר עם משתתפים ואחריות
   - 5: צוות מפורט עם סמכויות, תדירות ישיבות, וכללי החלטה

3. גורם מתכלל יחיד (0-5):
   - 0: אין גורם יחיד
   - 1: שר אחראי ללא הגדרת תפקיד
   - 2: ממונה מוזכר ללא בהירות
   - 3: יו"ר ועדה ללא סמכות מלאה
   - 4: ראש פרויקט עם אחריות לתכלול
   - 5: גורם מוגדר עם סמכויות מלאות והגדרת תפקיד

4. מנגנון דיווח/בקרה (0-5):
   - 0: אין דיווח
   - 1: "יהיה צורך לעדכן"
   - 2: דיווח למישהו ללא תדירות
   - 3: דיווח תקופתי בסיסי
   - 4: מנגנון מפורט עם תדירות ואחראים
   - 5: מנגנון מובנה עם פורמט, תדירות, וטיפול בחריגות

5. מנגנון מדידה והערכה (0-5):
   - 0: אין מדידה
   - 1: "נבחן את ההשפעה"
   - 2: כוונה למחקר ללא פירוט
   - 3: תכנית בסיסית למדידה
   - 4: מנגנון מסודר עם תדירות ומדדים
   - 5: מתווה מלא עם מדדים, לו"ז, וגוף מבצע

6. מנגנון ביקורת חיצונית (0-5):
   - 0: אין ביקורת חיצונית
   - 1: "נשקול מומחים חיצוניים"
   - 2: גוף חיצוני מוזכר ללא פירוט
   - 3: גוף ביקורת מוגדר ללא תהליך
   - 4: גוף חיצוני עם מועד הערכה
   - 5: ביקורת מפורטת עם תדירות ופרסום

7. משאבים נדרשים (0-5):
   - 0: אין אזכור משאבים
   - 1: "יידרש תקציב"
   - 2: סכום מוזכר ללא מקור
   - 3: סכום עם מקור לא ברור
   - 4: תקציב עם מקור ושימוש עיקרי
   - 5: פירוט מלא של תקציב, כ"א, ומקורות

8. מעורבות של מספר דרגים בתהליך (0-5):
   - 0: רק דרג אחד
   - 1: גוף נוסף להתייעצות
   - 2: רשימת דרגים ללא תיאום
   - 3: דרגים עם פירוט עקרוני
   - 4: מעורבות מוגדרת של כמה דרגים
   - 5: תיאור מלא של דרגים ונהלי תיאום

9. מבנה סעיפים וחלוקת עבודה ברורה (0-5):
   - 0: טקסט מבולגן ללא סעיפים
   - 1: סעיפים עמומים
   - 2: חלק מהסעיפים עם אחריות
   - 3: רוב הסעיפים עם אחריות
   - 4: סעיפים מסודרים עם אחריות
   - 5: מבנה ברור עם סעיפים, אחריות, ואבני דרך

10. מנגנון יישום בשטח (0-5):
    - 0: אין אזכור ליישום
    - 1: "ניישם דרך רשויות"
    - 2: מנגנון כללי ללא פירוט
    - 3: מנגנון בסיסי עם גוף מבצע
    - 4: מנגנון קונקרטי עם יחידות ליווי
    - 5: תיאור שלם של אופן הביצוע

11. גורם מכריע (0-5):
    - 0: אין גורם מכריע
    - 1: "השר רשאי להחליט"
    - 2: "ועדת שרים תדון"
    - 3: גורם מכריע ללא תהליך
    - 4: גורם מכריע ברור
    - 5: גורם מכריע עם תהליך מפורט

12. שותפות בין מגזרית (0-5):
    - 0: אין שותפות
    - 1: "נשקול לשתף"
    - 2: ארגון מוזכר ללא תפקיד
    - 3: מגזרים שותפים ללא מנדט
    - 4: פירוט על שותפים ואופן עבודה
    - 5: שיתוף מפורט עם תפקידים ומימון

13. מדדי תוצאה ומרכיבי הצלחה (0-5):
    - 0: רק פעולות ללא יעדים
    - 1: "נשאף לשיפור"
    - 2: יעד כללי ללא מספרים
    - 3: יעד מספרי ללא זמן
    - 4: יעד כמותי עם זמן
    - 5: יעדים מספריים עם מתודולוגיה

**חשוב**: אם המסמך אינו החלטת ממשלה או טיוטה של החלטת ממשלה, אל תנתח אותו לפי הקריטריונים. במקום זאת, החזר:
{{
    "is_government_decision": false,
    "criteria_scores": [],
    "recommendations": [],
    "misuse_message": "מצטער, אני מיועד אך ורק לניתוח טיוטות של החלטות ממשלה. המסמך שהעלית נראה כמו [סוג המסמך]. אם ברצונך לנתח טיוטת החלטת ממשלה, אנא העלה או הדבק את הטקסט המלא של הטיוטה."
}}

אם זו כן החלטת ממשלה, החזר את התשובה בפורמט JSON הבא:
{{
    "is_government_decision": true,
    "criteria_scores": [
        {{
            "criterion": "שם הקריטריון",
            "score": 0-5,
            "explanation": "הסבר קצר",
            "reference_from_document": "ציטוט רלוונטי מהמסמך (אם קיים)",
            "specific_improvement": "הצעה ספציפית לשיפור"
        }}
    ],
    "recommendations": ["המלצה 1", "המלצה 2", ...],
    "misuse_message": null
}}
"""
    return prompt

def detect_misuse(response_json: dict) -> tuple[bool, Optional[str]]:
    """Detect if the user is trying to misuse the bot"""
    if not response_json.get("is_government_decision", True):
        # Get the GPT's explanation if available
        gpt_message = response_json.get("misuse_message", "")
        
        # Extract what type of document GPT detected
        doc_type_match = re.search(r'נראה כמו\s*([^\.]+)', gpt_message)
        detected_type = doc_type_match.group(1) if doc_type_match else "מסמך לא מזוהה"
        
        # Create a more informative error message
        enhanced_message = f"""⚠️ **שימוש לא תקין**

מצטער, אני מיועד אך ורק לניתוח טיוטות של החלטות ממשלה.

המסמך שהעלית נראה כמו **{detected_type}** ולא מובנה כהחלטת ממשלה.

אם ברצונך לנתח טיוטת החלטת ממשלה, אנא העלה או הדבק את הטקסט המלא של הטיוטה.

💡 **טיפ**: החלטת ממשלה צריכה לכלול:
• כותרת עם נושא מדיניות
• אזכור של משרדי ממשלה או שרים
• סעיפים המתארים פעולות ממשלתיות
• שפה פורמלית של מסמך ממשלתי"""
        
        return True, enhanced_message
    return False, None

def split_document(text: str) -> List[Dict[str, Any]]:
    """Split a large document into chunks with overlap."""
    chunks = []
    text_length = len(text)
    
    # If document is small enough, return as single chunk
    if text_length <= CHUNK_SIZE:
        return [{"text": text, "start": 0, "end": text_length, "index": 0}]
    
    # Find natural break points (paragraphs/sections)
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    current_start = 0
    chunk_index = 0
    
    for i, paragraph in enumerate(paragraphs):
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(paragraph) + 2 > CHUNK_SIZE and current_chunk:
            # Save current chunk
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
                "end": current_start + len(current_chunk),
                "index": chunk_index
            })
            
            # Start new chunk with overlap from previous chunk
            overlap_start = max(0, len(current_chunk) - CHUNK_OVERLAP)
            current_chunk = current_chunk[overlap_start:] + "\n\n" + paragraph
            current_start = current_start + overlap_start
            chunk_index += 1
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start,
            "end": current_start + len(current_chunk),
            "index": chunk_index
        })
    
    logger.info(f"Split document into {len(chunks)} chunks")
    return chunks

async def analyze_chunk(chunk: Dict[str, Any], doc_hash: str, total_chunks: int) -> Dict[str, Any]:
    """Analyze a single chunk of a document."""
    chunk_index = chunk["index"]
    logger.info(f"Analyzing chunk {chunk_index + 1}/{total_chunks} for doc_hash: {doc_hash}")
    
    try:
        # Create evaluation prompt for this chunk
        prompt = create_evaluation_prompt(chunk["text"])
        
        # Call OpenAI API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """אתה מומחה בניתוח החלטות ממשלה בישראל. 
זהו חלק ממסמך גדול יותר. נתח את החלק הזה לפי הקריטריונים, תוך הבנה שאולי חסר הקשר מלא.
אם קריטריון מסוים לא מופיע בחלק זה, תן ציון 0 וציין שהמידע לא נמצא בחלק זה.
תמיד החזר תשובות בפורמט JSON תקין."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=3000,
            seed=42
        )
        
        # Parse response
        response_text = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())
        else:
            raise ValueError(f"Failed to extract JSON from chunk {chunk_index}")
        
        # Log token usage
        if hasattr(response, 'usage'):
            logger.info(f"Chunk {chunk_index} token usage - Total: {response.usage.total_tokens}")
        
        return {
            "chunk_index": chunk_index,
            "response_json": response_json,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error analyzing chunk {chunk_index}: {str(e)}")
        return {
            "chunk_index": chunk_index,
            "response_json": None,
            "success": False,
            "error": str(e)
        }

def aggregate_chunk_results(chunk_results: List[Dict[str, Any]], total_text_length: int) -> Dict[str, Any]:
    """Aggregate analysis results from multiple chunks."""
    # Initialize aggregated scores for each criterion
    criteria_aggregated = {}
    all_recommendations = []
    all_references = {}
    
    # Process each successful chunk
    successful_chunks = [r for r in chunk_results if r["success"]]
    
    if not successful_chunks:
        raise ValueError("No chunks were successfully analyzed")
    
    for result in successful_chunks:
        response_json = result["response_json"]
        chunk_index = result["chunk_index"]
        
        # Skip if not a government decision
        if not response_json.get("is_government_decision", True):
            continue
        
        # Process criteria scores
        for score_data in response_json.get("criteria_scores", []):
            criterion = score_data["criterion"]
            
            if criterion not in criteria_aggregated:
                criteria_aggregated[criterion] = {
                    "scores": [],
                    "explanations": [],
                    "references": [],
                    "improvements": []
                }
            
            # Only count non-zero scores (criterion was found in this chunk)
            if score_data["score"] > 0:
                criteria_aggregated[criterion]["scores"].append(score_data["score"])
                criteria_aggregated[criterion]["explanations"].append(
                    f"חלק {chunk_index + 1}: {score_data['explanation']}"
                )
                
                if score_data.get("reference_from_document"):
                    criteria_aggregated[criterion]["references"].append(
                        score_data["reference_from_document"]
                    )
                
                if score_data.get("specific_improvement"):
                    criteria_aggregated[criterion]["improvements"].append(
                        score_data["specific_improvement"]
                    )
        
        # Collect recommendations
        all_recommendations.extend(response_json.get("recommendations", []))
    
    # Calculate final scores and build response
    final_criteria_scores = []
    
    for criterion in CRITERIA:
        if criterion in criteria_aggregated and criteria_aggregated[criterion]["scores"]:
            # Average the scores where the criterion was found
            avg_score = sum(criteria_aggregated[criterion]["scores"]) / len(criteria_aggregated[criterion]["scores"])
            
            # Combine explanations
            combined_explanation = " | ".join(criteria_aggregated[criterion]["explanations"][:2])  # Limit to 2
            
            # Get first reference and improvement
            reference = criteria_aggregated[criterion]["references"][0] if criteria_aggregated[criterion]["references"] else None
            improvement = criteria_aggregated[criterion]["improvements"][0] if criteria_aggregated[criterion]["improvements"] else None
            
            final_criteria_scores.append({
                "criterion": criterion,
                "score": round(avg_score),  # Round to nearest integer
                "explanation": combined_explanation,
                "reference_from_document": reference,
                "specific_improvement": improvement
            })
        else:
            # Criterion not found in any chunk
            final_criteria_scores.append({
                "criterion": criterion,
                "score": 0,
                "explanation": "הקריטריון לא נמצא במסמך",
                "reference_from_document": None,
                "specific_improvement": f"יש להוסיף התייחסות ל{criterion} בהחלטה"
            })
    
    # Deduplicate recommendations
    unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]  # Limit to 10
    
    # Add chunk processing note
    chunk_note = f"המסמך נותח ב-{len(successful_chunks)} חלקים עקב אורכו ({total_text_length:,} תווים)"
    unique_recommendations.insert(0, chunk_note)
    
    return {
        "criteria_scores": final_criteria_scores,
        "recommendations": unique_recommendations,
        "chunk_info": {
            "total_chunks": len(chunk_results),
            "successful_chunks": len(successful_chunks),
            "total_length": total_text_length
        }
    }

async def analyze_large_document(text: str, doc_hash: str, request_id: str, 
                                progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """Analyze a large document by splitting it into chunks."""
    logger.info(f"Starting large document analysis for doc_hash: {doc_hash}, length: {len(text)}")
    
    # Split document into chunks
    chunks = split_document(text)
    total_chunks = len(chunks)
    
    if progress_callback:
        await progress_callback(f"מפצל מסמך ארוך ל-{total_chunks} חלקים...")
    
    # Analyze chunks concurrently (but limit concurrency to avoid rate limits)
    chunk_results = []
    batch_size = 3  # Process 3 chunks at a time
    
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i + batch_size]
        
        if progress_callback:
            await progress_callback(f"מנתח חלקים {i+1}-{min(i+batch_size, total_chunks)} מתוך {total_chunks}...")
        
        # Analyze batch concurrently
        batch_tasks = [analyze_chunk(chunk, doc_hash, total_chunks) for chunk in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Handle results
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Chunk analysis failed: {str(result)}")
                chunk_results.append({
                    "success": False,
                    "error": str(result)
                })
            else:
                chunk_results.append(result)
    
    if progress_callback:
        await progress_callback("מאחד תוצאות הניתוח...")
    
    # Aggregate results
    try:
        aggregated = aggregate_chunk_results(chunk_results, len(text))
        return aggregated
    except Exception as e:
        logger.error(f"Failed to aggregate results for doc_hash {doc_hash}: {str(e)}")
        raise

def perform_analysis(response_json: dict, model: str, doc_hash: str) -> AnalyzeResponse:
    """Perform the actual analysis of the document after validation"""
    try:
        # Extract criteria scores
        criteria_scores = []
        for score_data in response_json.get("criteria_scores", []):
            criteria_scores.append(CriteriaScore(
                criterion=score_data["criterion"],
                score=score_data["score"],
                explanation=score_data["explanation"],
                reference_from_document=score_data.get("reference_from_document"),
                specific_improvement=score_data.get("specific_improvement")
            ))
        
        # Extract recommendations
        recommendations = response_json.get("recommendations", [])
        
        # Generate additional recommendations based on low scores
        for score in criteria_scores:
            if score.score <= 2:
                if score.criterion == "לוח זמנים מחייב":
                    recommendations.append("יש להוסיף תאריכי יעד מחייבים לכל משימה עיקרית בהחלטה")
                elif score.criterion == "מנגנון ביקורת חיצונית":
                    recommendations.append("מומלץ להוסיף מנגנון ביקורת חיצונית לוודא יישום אפקטיבי")
                elif score.criterion == "מדדי תוצאה ומרכיבי הצלחה":
                    recommendations.append("יש להגדיר מדדי הצלחה כמותיים וברורים עם יעדים מספריים")
        
        return AnalyzeResponse(
            criteria_scores=criteria_scores,
            recommendations=recommendations[:5],  # Limit to top 5 recommendations
            model_used=model,
            misuse_detected=False
        )
    except KeyError as e:
        logger.error(f"Missing required field in analysis for doc_hash {doc_hash}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during analysis for doc_hash {doc_hash}: {str(e)}")
        raise

def perform_analysis_with_retries(response_json: dict, model: str, doc_hash: str, request_id: str) -> AnalyzeResponse:
    """Perform analysis with retry logic"""
    MAX_RETRIES = 3
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Analysis attempt {attempt} for doc_hash {doc_hash}, request_id {request_id}")
            result = perform_analysis(response_json, model, doc_hash)
            
            if attempt > 1:
                result.retry_status = f"הניתוח הצליח בניסיון {attempt}"
                logger.info(f"Analysis succeeded on attempt {attempt} for doc_hash {doc_hash}")
            
            return result
            
        except Exception as e:
            logger.warning(f"Analysis attempt {attempt} failed for doc_hash {doc_hash}: {str(e)}")
            
            if attempt < MAX_RETRIES:
                # Calculate wait time with exponential backoff
                wait_time = attempt * 1.5  # 1.5s, 3s
                logger.info(f"Waiting {wait_time}s before retry {attempt + 1} for doc_hash {doc_hash}")
                time.sleep(wait_time)
                continue
            else:
                # All retries exhausted
                logger.error(f"All {MAX_RETRIES} analysis attempts failed for doc_hash {doc_hash}")
                return AnalyzeResponse(
                    criteria_scores=[],
                    recommendations=[f"הניתוח נכשל לאחר {MAX_RETRIES} ניסיונות. אנא נסה שוב מאוחר יותר."],
                    model_used=model,
                    misuse_detected=False,
                    retry_status=f"נכשל לאחר {MAX_RETRIES} ניסיונות"
                )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_decision(request: AnalyzeRequest):
    """Analyze a government decision draft against 13 criteria"""
    try:
        # Calculate document hash for tracking
        doc_hash = hashlib.md5(request.text.encode()).hexdigest()
        
        # Check document size
        doc_length = len(request.text)
        logger.info(f"Analyzing decision draft - text_length: {doc_length}, request_id: {request.requestId}, doc_hash: {doc_hash}")
        
        # Check if document exceeds maximum size limit
        if doc_length > MAX_CHAR_LIMIT:
            logger.warning(f"Document exceeds maximum size limit - doc_hash: {doc_hash}, length: {doc_length}, max: {MAX_CHAR_LIMIT}")
            return AnalyzeResponse(
                criteria_scores=[],
                recommendations=[f"המסמך גדול מאוד ({doc_length:,} תווים). המערכת תומכת עד {MAX_CHAR_LIMIT:,} תווים (כ-200 עמודים). אנא פנה לתמיכה לקבלת סיוע."],
                model_used="none",
                misuse_detected=False,
                retry_status="מסמך גדול מאוד"
            )
        
        if doc_length > WARN_CHAR_LIMIT:
            logger.info(f"Document exceeds warning limit - doc_hash: {doc_hash}, length: {doc_length}")
            # Continue with analysis but add warning
            size_warning = f"שים לב: המסמך ארוך ({doc_length:,} תווים, כ-{doc_length//2500} עמודים). זה עלול להשפיע על איכות הניתוח."
        
        # Check analysis cache first
        analysis_cache_key = f"analysis_{doc_hash}"
        cached_analysis = analysis_cache.get(analysis_cache_key)
        if cached_analysis:
            cache_timestamp, cached_response = cached_analysis
            if (datetime.utcnow() - cache_timestamp).total_seconds() < CACHE_EXPIRY_SECONDS:
                logger.info(f"Using cached analysis result - doc_hash: {doc_hash}")
                # Add size warning if applicable
                if doc_length > WARN_CHAR_LIMIT:
                    size_warning = f"שים לב: המסמך ארוך ({doc_length:,} תווים, כ-{doc_length//2500} עמודים). זה עלול להשפיע על איכות הניתוח."
                    cached_response.recommendations.insert(0, size_warning)
                return cached_response
        
        # For large documents, use chunking approach
        if doc_length > CHUNK_SIZE:
            logger.info(f"Document requires chunking - length: {doc_length}, chunk_size: {CHUNK_SIZE}")
            
            # Define progress callback
            progress_messages = []
            async def progress_callback(message: str):
                progress_messages.append(message)
                logger.info(f"Progress update for doc_hash {doc_hash}: {message}")
            
            try:
                # Analyze large document
                large_doc_result = await analyze_large_document(
                    request.text, 
                    doc_hash, 
                    request.requestId,
                    progress_callback
                )
                
                # Build response
                result = AnalyzeResponse(
                    criteria_scores=[CriteriaScore(**cs) for cs in large_doc_result["criteria_scores"]],
                    recommendations=large_doc_result["recommendations"],
                    model_used="gpt-4o",
                    misuse_detected=False,
                    progress_status=" | ".join(progress_messages),
                    chunk_info=large_doc_result.get("chunk_info")
                )
                
                # Cache successful results
                if result.criteria_scores:
                    analysis_cache[analysis_cache_key] = (datetime.utcnow(), result)
                    logger.info(f"Cached large document analysis for doc_hash: {doc_hash}")
                
                return result
                
            except Exception as e:
                logger.error(f"Large document analysis failed for doc_hash {doc_hash}: {str(e)}")
                return AnalyzeResponse(
                    criteria_scores=[],
                    recommendations=[f"ניתוח המסמך הארוך נכשל: {str(e)}"],
                    model_used="gpt-4o",
                    misuse_detected=False,
                    retry_status="נכשל בניתוח מסמך גדול"
                )
        
        # Check cache for previous validation result (for normal-sized documents)
        cache_key = f"validation_{doc_hash}"
        cached_result = validation_cache.get(cache_key)
        if cached_result:
            cache_timestamp, is_valid, rejection_reason = cached_result
            if (datetime.utcnow() - cache_timestamp).total_seconds() < CACHE_EXPIRY_SECONDS:
                logger.info(f"Using cached validation result - doc_hash: {doc_hash}, is_valid: {is_valid}")
                if not is_valid:
                    return AnalyzeResponse(
                        criteria_scores=[],
                        recommendations=[],
                        model_used="cached",
                        misuse_detected=True,
                        misuse_message=rejection_reason
                    )
        
        # Always use GPT-4 for better accuracy in document classification
        model = "gpt-4o"
        
        # Create the evaluation prompt
        prompt = create_evaluation_prompt(request.text)
        
        # Call OpenAI API with seed for consistency
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": """אתה מומחה בניתוח החלטות ממשלה בישראל. 
הנחיה חשובה: רוב המשתמשים מעלים מסמכים לגיטימיים. היה נדיב ומקל בקבלת מסמכים לניתוח.
קבל כל מסמך שנראה קשור למדיניות ציבורית, טיוטות, הצעות, או עבודה ממשלתית.
דחה רק מסמכים ברורים כמו כרטיסי טיסה, קורות חיים אישיים, או חשבוניות.
ברירת מחדל: אם יש ספק - קבל את המסמך (is_government_decision: true).
תמיד החזר תשובות בפורמט JSON תקין."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Set to 0 for consistent scoring
            max_tokens=3000,
            seed=42  # Fixed seed for deterministic results
        )
        
        # Parse the response
        response_text = response.choices[0].message.content
        
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())
        else:
            logger.error(f"Failed to extract JSON from GPT response for doc_hash: {doc_hash}")
            raise ValueError("Failed to extract JSON from response")
        
        # Log the validation result
        is_gov_decision = response_json.get("is_government_decision", True)
        logger.info(f"Document validation - doc_hash: {doc_hash}, is_government_decision: {is_gov_decision}")
        
        # Check for misuse
        misuse_detected, misuse_message = detect_misuse(response_json)
        
        # Cache the validation result
        validation_cache[cache_key] = (datetime.utcnow(), not misuse_detected, misuse_message)
        
        if misuse_detected:
            logger.warning(f"Document rejected - doc_hash: {doc_hash}, reason: {misuse_message}")
            return AnalyzeResponse(
                criteria_scores=[],
                recommendations=[],
                model_used=model,
                misuse_detected=True,
                misuse_message=misuse_message
            )
        
        # Log token usage
        if hasattr(response, 'usage'):
            logger.info(f"Token usage - Model: {model}, Prompt: {response.usage.prompt_tokens}, "
                       f"Completion: {response.usage.completion_tokens}, "
                       f"Total: {response.usage.total_tokens}")
        
        # Document passed validation - now perform analysis with retries
        logger.info(f"Document passed validation, starting analysis for doc_hash: {doc_hash}")
        result = perform_analysis_with_retries(response_json, model, doc_hash, request.requestId)
        
        # Cache successful analysis results
        if result and not result.misuse_detected and result.criteria_scores:
            analysis_cache[analysis_cache_key] = (datetime.utcnow(), result)
            logger.info(f"Cached analysis result for doc_hash: {doc_hash}")
        
        # Add size warning if applicable
        if doc_length > WARN_CHAR_LIMIT and 'size_warning' in locals():
            result.recommendations.insert(0, size_warning)
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for doc_hash {doc_hash}: {str(e)}")
        # Try to be more resilient - assume it's a valid government document if parsing failed
        return AnalyzeResponse(
            criteria_scores=[],
            recommendations=["לא ניתן לפענח את תגובת המערכת. אנא נסה שוב."],
            model_used=model,
            misuse_detected=False
        )
    except Exception as e:
        logger.error(f"Error analyzing decision for doc_hash {doc_hash}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Decision Guide Bot",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/clear-cache")
async def clear_cache():
    """Clear both validation and analysis caches - useful for testing"""
    global validation_cache, analysis_cache
    validation_size = len(validation_cache)
    analysis_size = len(analysis_cache)
    validation_cache.clear()
    analysis_cache.clear()
    total_removed = validation_size + analysis_size
    logger.info(f"Cleared caches - validation: {validation_size}, analysis: {analysis_size}, total: {total_removed}")
    return {
        "status": "caches cleared", 
        "validation_entries_removed": validation_size,
        "analysis_entries_removed": analysis_size,
        "total_entries_removed": total_removed
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8018"))
    uvicorn.run(app, host="0.0.0.0", port=port)