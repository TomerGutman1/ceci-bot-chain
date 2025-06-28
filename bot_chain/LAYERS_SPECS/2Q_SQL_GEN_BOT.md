## מפרט מפורט – 2Q_SQL_GEN_BOT

("SQL Generator" — שלב 2 במסלול QUERY)

| קטגוריה                  | פרטים                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ייעוד עסקי**           | לייצר שאילתת SQL בטוחה, מדויקת ואופטימלית בהתאם ל־`params` שחולצו על ידי `1_INTENT_BOT` או `2X_CTX_ROUTER_BOT`. |
| **קלט נכנס**             | **מקור:** `1_INTENT_BOT` או `2X_CTX_ROUTER_BOT` (במקרה של RESULT_REF)  
                           **פורמט:** JSON מלא:  
                           `{"intent":"DATA_QUERY", "params":{ ... }}`  
                           **דוגמה 1 – חיפוש כללי:**  
                           `{"params":{"topic_free":"חינוך מיוחד","date_from":"1995-01-01","date_to":"2010-12-31","limit":50}}`  
                           **דוגמה 2 – חיפוש החלטה ספציפית בתוכן מלא:**  
                           `{"params":{"decision_number":2081,"government_number":37,"full_content":true}}` |
| **פלט יוצא**             | **יעד:** `SQL DB` (PostgreSQL)  
                           **פורמט:** JSON:  
                           `{"sql": "SELECT …", "params": [ … ]}`  
                           **דוגמה פלט:**  
                           `{"sql":"SELECT id, decision_date, decision_title, summary, decision_content, decision_url FROM israeli_government_decisions WHERE decision_number=$1 AND government_number=$2 LIMIT 1", "params":[2081, 37]}` |
| **תחומי אחריות (Do)**   | - בחירת עמודות מותרות בלבד (ללא `SELECT *`)  
                           - הוספת `LIMIT` תמידית (ברירת מחדל: 10)  
                           - טיפול בטווחי תאריכים ובחיפושים חופשיים (`ILIKE '%…%'`)  
                           - שימוש בדגל `full_content` לצורך הכללת `decision_content`  
                           - שימוש ב־placeholders (`$1`, `$2`…) ויצירת מערך `params` תואם |
| **גבולות (Don’t)**      | - לא מריץ SQL  
                           - לא מוחק / מעדכן נתונים  
                           - לא מחזיר תשובה למשתמש |
| **מודל GPT מומלץ**       | `gpt-4-turbo` — דיוק תחבירי גבוה והבנת הנחיות מורכבות |
| **Prompt בסיסי**         | 1. SYSTEM: "Generate a secure parameterised SQL for table `israeli_government_decisions` … Never use SELECT * … Always include LIMIT …"  
                           2. USER: JSON `params` + תיאור קצר של השאלה |
| **Few-shot חיוניים**     | - חיפוש נושא עם טווח תאריכים  
                           - חיפוש לפי מספר החלטה עם `full_content=true`  
                           - שאילתות מסוג `count_only` (מומר ל־`SELECT COUNT(*)`) |
| **אילוצי ביצועים**       | השהיית p95 ≤ 500ms  
                           קלט ≤ 200 טוקנים  
                           פלט ≤ 120 טוקנים |
| **שגיאות**              | - פלט JSON לא תקין → fallback: רישום ביומן + intent=`UNCLEAR`  
                           - זיהוי מילת SQL אסורה (`DROP`, `INSERT` וכו’) → סינון והחזרת שגיאת SECURITY |
| **טלמטריה**             | - `avg_selected_columns`  
                           - `has_limit_flag`  
                           - `sqlgen_latency_ms` |
| **אבטחה**               | - רשימת עמודות מותרות (whitelist)  
                           - חסימת פקודות DDL/DML  
                           - רישום שאילתות ביומן תוך השמטת ערכים (`placeholders` בלבד) |
| **בדיקות אוטומטיות**    | - שאילתה ללא `LIMIT` תיחשב כשגיאה  
                           - `decision_content` נכלל רק כאשר `full_content=true`  
                           - מספר ה־placeholder תואם לאורך מערך `params` |
| **תלויות / גרסאות**      | OpenAI SDK ≥ 1.5  
                           Prompt קבוע תחת `sqlgen_v1.md` ב־Git |
| **בעלים**               | Data Eng Lead  
                           SQL Subject Matter Expert  
                           Product PM — CECI-AI |

---

### זרימת QUERY טיפוסית:
משתמש → 0_REWRITE_BOT → 1_INTENT_BOT → 2Q_SQL_GEN_BOT → SQL DB → 3Q_RANKER_BOT → 4_FORMATTER → משתמש
