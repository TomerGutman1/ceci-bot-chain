## מפרט מפורט – 2X_CTX_ROUTER_BOT

("Context Router" — שלב 2X במסלול MAIN, תומך ב־QUERY ו־EVAL)

| קטגוריה                  | פרטים                                                                                                                                                                                                                                                                                                                                                      |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ייעוד עסקי**           | לתרגם בקשות מסוג “הראשונה”, “שלישית”, “החלטה 2081” למזהי החלטות (IDs) מוחשיים מתוך ההיסטוריה, כדי שהמערכת תדע אילו רשומות לשלוף או לנתח בהמשך. השכבה אוספת הקשר, שומרת על רצף שיח, ומונעת בלבול. |
| **קלט נכנס**             | **מקור:** `1_INTENT_BOT` כאשר `intent` הוא `RESULT_REF` או `ANALYSIS`  
                           **פורמט:**  
                           `{"intent":"RESULT_REF", "params":{"index_in_previous":3, "request_full_content":true}, "confidence":0.92}`  
                           או  
                           `{"intent":"ANALYSIS", "params":{"decision_number":2081}, "confidence":0.95}` |
| **פלט יוצא**             | **יעד:**  
                           - `2Q_SQL_GEN_BOT` (במקרה של שליפה)  
                           - `2E_EVALUATOR_BOT` (אם התוכן כבר קיים בזיכרון)  
                           - `2C_CLARIFY_BOT` (אם לא נמצא הקשר)  
                           **פורמט:**  
                           `{"resolved":true, "decision_ids":[345,267], "next_action":"SQL"}` |
| **תחומי אחריות (Do)**   | - שימוש ב־`session_cache` (רשימת decision_ids מפניות קודמות)  
                           - המרה של אינדקסים ("השלישית") ל־ID אמיתי  
                           - זיהוי ישיר של `decision_number` או `decision_key`  
                           - החלטה אם להמשיך ל־SQL או ישירות ל־EVALUATOR  
                           - במידה ואין התאמה, שליחה ל־`2C_CLARIFY_BOT` |
| **גבולות (Don’t)**      | - לא כותב ל־DB  
                           - לא מנתח טקסט (שייך ל־`2E_EVALUATOR_BOT`)  
                           - לא משנה את פרמטרי השאלה המקורית |
| **מודל GPT מומלץ**       | `gpt-3.5-turbo` — מהיר, יעיל להבנת הקשרים קצרים (עד כ־600 טוקנים) |
| **Prompt בסיסי**         | `SYSTEM: You receive a JSON with intent=RESULT_REF or ANALYSIS and params. You also receive session_cache array of decision_ids. Map indices/keywords to IDs. Return JSON {resolved, decision_ids, next_action}.` |
| **Few-shot חיוניים**     | - "הראשונה" → `[id1]`  
                           - "האחרונה" → `[id_last]`  
                           - "החלטה 2081" → `[id_of_2081]`  
                           - ללא הקשר → `{"resolved":false}` |
| **ביצועים**             | p95 latency ≤ 250ms  
                           קלט עד 120 טוקנים  
                           פלט עד 60 טוקנים |
| **שגיאות**              | - אין סט תואם → `resolved:false`, שליחה ל־Clarify  
                           - פלט JSON לא תקין → לוג שגיאה + שליחה ל־Clarify |
| **טלמטריה**             | - `ctx_hits`  
                           - `ctx_miss`  
                           - `router_latency_ms`  
                           - `clarify_rate` |
| **אבטחה**               | - אין כתיבה ל־DB  
                           - `session_cache` מוצפן ב־Redis  
                           - תאימות GDPR (TTL = 15 דקות) |
| **בדיקות אוטומטיות**    | - "הראשונה" מחזירה את ה־ID הראשון  
                           - אינדקס מחוץ לטווח גורם לשליחה ל־Clarify  
                           - זיהוי `decision_number` מתבצע במדויק |
| **תלויות**              | OpenAI SDK ≥ 1.5  
                           Redis session store |
| **בעלים**               | Chat Memory Lead  
                           Backend Engineer  
                           Product PM – CECI-AI |

---

### זרימת דוגמה:
1. משתמש: “הראה לי את התוכן של השלישית”  
2. `1_INTENT_BOT` מזהה `RESULT_REF` עם `index=3`  
3. `2X_CTX_ROUTER_BOT` ממיר ל־`decision_id=267`  
4. מפנה ל־`2Q_SQL_GEN_BOT` לשליפה מלאה  
5. ממשיך הלאה בפייפליין
