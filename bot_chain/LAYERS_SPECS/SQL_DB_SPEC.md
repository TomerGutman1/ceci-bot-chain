## מפרט מפורט – SQL DB (Supabase API Layer)

("Online Postgres via Supabase" — רכיב תשתיתי בין 2Q ↔ 3Q/4)

| קטגוריה                    | פרטים                                                                                                                                                                                                                                 |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ייעוד עסקי**            | מאגר החלטות ממשלה (כ־24,000 שורות) עם גישה קריאה-בלבד דרך Supabase בענן, לצורך שליפות מאובטחות ומהירות עבור שכבות LLM |
| **סכימה עיקרית**          | טבלה עיקרית: `israeli_government_decisions`  
                             **לקובץ הסכמה המלא:** ראה `israeli_government_decisions_DB_SCHEME.md` (באותה תיקייה) |
| **קלט נכנס**              | **מקור:** `2Q_SQL_GEN_BOT`  
                             **פורמט:** JSON  
                             ```json
                             {
                               "sql": "SELECT … WHERE decision_date BETWEEN $1 AND $2 LIMIT 50",
                               "params": ["1995-01-01", "2010-12-31"]
                             }
                             ``` |
| **פלט יוצא**              | **יעד:**  
                             - `3Q_RANKER_BOT` (שורות מרובות)  
                             - `4_FORMATTER` (תוכן מלא או החלטה בודדת)  
                             **פורמט:** מערך JSON של אובייקטי שורות — רק השדות שנכללו ב־SELECT |
| **גישה / Endpoint**       | `POST https://<project>.supabase.co/rest/v1/rpc/run_sql`  
                             Headers:  
                             - `apikey: service_role`  
                             - `Prefer: return=minimal`  
                             Body:  
                             ```json
                             { "sql": "...", "params": [] }
                             ``` |
| **כללי אבטחה**            | - Row-level security מופעל (קריאה בלבד)  
                             - רק מפתח מסוג Service Role  
                             - חסימת מילים מסוכנות (DML) דרך `2Q_SQL_GEN_BOT` |
| **Rate / Latency**        | - p95 latency ≤ 120ms לשאילתת LIMIT 50  
                             - קצב קריאה מומלץ: עד 150 בקשות לדקה |
| **שדות מותרים ל־SELECT**  | `id, decision_date, decision_number, government_number, decision_title, summary, decision_content, tags_policy_area, tags_government_body, operativity, decision_url` |
| **דוגמה שליפה – תוכן מלא** | ```sql
                             SELECT id, decision_title, summary, decision_content, decision_url
                             FROM israeli_government_decisions
                             WHERE decision_number=$1 AND government_number=$2
                             LIMIT 1;
                             ``` |
| **שגיאות נפוצות**         | - `42501 insufficient_privilege` — ניסיון להריץ DML  
                             - `57014 cancelled` — שאילתה איטית (מעל 2 שניות) |
| **טלמטריה**              | `db_query_ms`, `rows_returned`, `error_code`, `rate_per_min` |
| **שמירת נתונים**         | - Snapshot יומי ל־S3  
                             - רפליקה read-only  
                             - נתוני ציבור, אין PII |
| **בדיקות אוטומטיות**     | - שאילתה עם `LIMIT` תמיד מצליחה  
                             - `COUNT(*)` מתחת ל־10ms  
                             - `decision_content` מוחזר רק אם נדרש במפורש |
| **תלות**                 | Supabase Postgres 15  
                             pgvector (לשימוש עתידי בהטמעות) |
| **בעלים**                | Data-Platform Lead  
                             DevOps  
                             DBA — CECI-AI |

---

### זרימת QUERY טיפוסית:
`2Q_SQL_GEN_BOT`  
→ Supabase API (`run_sql`)  
→ JSON rows  
→ `3Q_RANKER_BOT`  
→ `4_FORMATTER`



