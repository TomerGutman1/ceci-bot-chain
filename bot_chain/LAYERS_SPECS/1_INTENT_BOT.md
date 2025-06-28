## מפרט מפורט – 1_INTENT_BOT

("Intent Detector / Param Extractor" — שלב 1 במסלול MAIN)

| קטגוריה                  | פרטים                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ייעוד עסקי**           | לסווג כל שאילתה ל־`intent` מדויק (`DATA_QUERY`, `RESULT_REF`, `ANALYSIS`, `UNCLEAR`) ולחלץ ממנה את כל הפרמטרים הדרושים לשלבים הבאים. |
| **קלט נכנס**             | **מקור:** `0_REWRITE_BOT`  
                           **פורמט:** JSON – `{"clean_query":"<שאלה בעברית תקנית>"}`  
                           **דוגמאות:**  
                           1. `{"clean_query":"הבא לי החלטות בנושא חינוך מיוחד בין 1995 ל-2010"}`  
                           2. `{"clean_query":"הראה לי את ההחלטה הראשונה שהצגת לי"}` |
| **פלט יוצא**             | **יעד:** `2Q_SQL_GEN_BOT`, `2X_CTX_ROUTER_BOT`, `2C_CLARIFY_BOT`  
                           **פורמט:** JSON תקני:  
                           `json { "intent":"...", "params":{...}, "confidence":0-1 }`  
                           **דוגמאות:**  
                           - `{"intent":"DATA_QUERY", "params":{"topic_free":"חינוך מיוחד","date_from":"1995-01-01","date_to":"2010-12-31","limit":50}, "confidence":0.93}`  
                           - `{"intent":"RESULT_REF", "params":{"index_in_previous":1,"request_full_content":true}, "confidence":0.95}` |
| **תחומי אחריות (Do)**   | - סיווג intent עם confidence  
                           - חילוץ פרמטרים (נושא, טווח תאריכים, אינדקס החלטה, flags כמו `count_only` או `full_content`)  
                           - נרמול תאריכים "מ-95" → "1995-01-01"  
                           - זיהוי רפרנסים כמו "הראשונה", "זו שהצגת" |
| **גבולות (Don’t)**      | - לא מפיק SQL  
                           - לא מבצע ניתוח טקסטואלי מעמיק (שייך ל־`2E_EVALUATOR_BOT`)  
                           - לא פונה למסד נתונים |
| **מודל GPT מומלץ**       | `gpt-4-turbo` — הבנת הקשר עמוקה, פלט JSON אמין |
| **Prompt בסיסי**         | `text SYSTEM: Classify the question for the Israeli-Gov decision DB. Return ONLY JSON {intent, params, confidence}. …`  
                           כולל Appendix עם רשימת פרמטרים ודוגמאות few-shot |
| **Few-shot חיוניים**     | לפחות 8–10 דוגמאות הכוללות:  
                           - `DATA_QUERY` רגיל  
                           - טווח תאריכים  
                           - `RESULT_REF` עם "הראשונה"  
                           - `ANALYSIS`  
                           - `UNCLEAR` |
| **ביצועים**             | p95 latency ≤ 400ms  
                           קלט עד 300 טוקנים  
                           פלט עד 120 טוקנים |
| **שגיאות**              | אם JSON שגוי → fallback:  
                           intent = `UNCLEAR`,  
                           confidence = 0,  
                           + רישום שגיאה ביומן |
| **טלמטריה**             | - `intent_distribution`  
                           - `avg_confidence`  
                           - `param_missing_rate` |
| **אבטחה**               | הסתרת מידע אישי (PII) בלוגים  
                           הגבלת קצב: 30 בקשות לדקה לכל IP |
| **בדיקות**              | - זיהוי תקין של `DATA_QUERY` עם confidence ≥ 0.9  
                           - זיהוי `RESULT_REF` עם רפרנס כמו "הראשונה"  
                           - זיהוי `UNCLEAR` לשאלות ריקות או סימני שאלה בלבד |
| **תלויות**              | OpenAI SDK ≥ 1.5  
                           prompt שמור ב־Git תחת `intent_v1.md` |
| **קנה מידה עתידי**      | - Fine-tuning קטן לפרזינג ייחודי  
                           - הפרדת classification ו-extraction לשני מודלים נפרדים במקרה של דרישת latency נמוכה |
| **בעלים**               | NLP Lead  
                           Product PM  
                           QA Automation – CECI-AI |

---

### זרימה תמציתית:
משתמש → 0_REWRITE_BOT → 1_INTENT_BOT → אחד או יותר מהבאים: SQL_GEN, CTX_ROUTER, CLARIFY
