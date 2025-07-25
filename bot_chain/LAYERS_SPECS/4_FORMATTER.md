## מפרט מפורט – 4_FORMATTER

("Answer Formatter" — שלב 4 במסלולים MAIN, QUERY, EVAL)

| קטגוריה                  | פרטים                                                                                                                                                                                                                                                                                         |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ייעוד עסקי**           | לעצב ולהחזיר הודעת צ'אט סופית, קריאה וברורה, בהתאם לסוג הבקשה של המשתמש:  
                           - **תצוגה רגילה** — הצגת החלטות ככרטיסים קצרים (כותרת, פרטים עיקריים, תקציר)  
                           - **תוכן מלא** — מוסיף את שדה `decision_content`  
                           - **תשובת ניתוח** — מעבד פלט JSON מה־`EVALUATOR` לטבלת תובנות או Bullet points |
| **קלט נכנס**             | **מקורות:**  
                           - `3Q_RANKER_BOT` → רשימת IDs  
                           - `SQL DB` (במקרה של החלטה בודדת או תוכן מלא)  
                           - `2E_EVALUATOR_BOT` → JSON עם `analysis`  
                           **פורמטים נפוצים:**  
                           1. `{"ranked_ids":[345,292,267]}`  
                           2. `{"raw_rows":[{…}], "full_content":true}`  
                           3. `{"analysis":[{ "id":345, … }]}` |
| **פלט יוצא**             | **יעד:** המשתמש  
                           **פורמט:** Markdown בעברית  
                           - תצוגה רגילה — כרטיסי החלטות בפורמט:  
                             ```
                             🏛️ החלטת ממשלה מס' 345  
                             🔢 מספר החלטה: ...  
                             📅 תאריך: ...  
                             🏷️ תחום מדיניות: ...  
                             📝 תקציר: ...
                             ```
                           - תצוגת תוכן מלא: מוסיף  
                             ```
                             **תוכן מלא של ההחלטה:**  
                             <decision_content>
                             ```
                           - ניתוח: טבלה או רשימה תמציתית לפי שדות `analysis` |
| **תחומי אחריות (Do)**   | - ביצוע קריאת DB נוספת לפי ID אם חסרים שדות  
                           - בניית Markdown עקבי  
                           - הדגשת מילות מפתח בשאלה (`<mark>`)  
                           - חיתוך תקצירים באורך 200 תווים  
                           - הוספת כותרות והפרדות בין כרטיסים |
| **גבולות (Don’t)**      | - אינו מפעיל GPT  
                           - אינו משנה סדר החלטות  
                           - אינו עורך או מחליף תוכן מה־DB |
| **טכנולוגיה**           | Node.js / TypeScript  
                           תבניות תצוגה באמצעות Handlebars או EJS |
| **ביצועים**             | השהיית p95 ≤ 80ms  
                           תומך עד 15 החלטות בתצוגה אחת |
| **שגיאות**              | - שדה חסר → יוצג כ־"לא צוין"  
                           - פלט ניתוח שגוי → טקסט קבוע: "שגיאה בניתוח, נסה שוב" |
| **טלמטריה**             | - `fmt_type` (regular / full / analysis)  
                           - `cards_rendered`  
                           - `fmt_latency_ms` |
| **אבטחה**               | - מנקה Markdown / HTML  
                           - קוצץ את `decision_content` לאורך מקסימלי של 4000 תווים כדי למנוע הצפת צ'אט |
| **בדיקות אוטומטיות**    | - מספר כרטיסים תואם למספר IDs  
                           - תוכן מלא מוצג רק אם `full_content=true`  
                           - עבור `analysis`: קיימת טבלת strengths ו־weaknesses |
| **תלויות**              | DB read-only pool  
                           ספריית Markdown Utility |
| **בעלים**               | Front-End Lead  
                           UX Writer  
                           Product PM — CECI-AI |

---

