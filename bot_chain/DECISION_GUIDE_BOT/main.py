from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import sys
from datetime import datetime
import logging
from openai import OpenAI
import json
import re
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Decision Guide Bot")

# Simple in-memory cache for validation results
validation_cache = {}
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

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
        
        # Log the request with hash
        logger.info(f"Analyzing decision draft - text_length: {len(request.text)}, request_id: {request.requestId}, doc_hash: {doc_hash}")
        
        # Check cache for previous validation result
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
        
        # Call OpenAI API
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
            max_tokens=3000
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
        return perform_analysis_with_retries(response_json, model, doc_hash, request.requestId)
        
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
    """Clear the validation cache - useful for testing"""
    global validation_cache
    cache_size = len(validation_cache)
    validation_cache.clear()
    logger.info(f"Cleared validation cache - removed {cache_size} entries")
    return {"status": "cache cleared", "entries_removed": cache_size}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8018"))
    uvicorn.run(app, host="0.0.0.0", port=port)