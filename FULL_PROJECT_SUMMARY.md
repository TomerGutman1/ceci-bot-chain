### 24 ביוני 2025 - גרסה 2.3.7 🔧 **תיקון templates ל-SQL Engine**
- 🆕 **תיקונים ושיפורים ב-Query Templates**:
  - הוספת template חדש `COUNT_BY_GOVERNMENT` עם priority 15 לזיהוי "כמה החלטות קיבלה ממשלה X"
  - הוספת `X_DECISIONS_BY_TOPIC` ו-`X_RECENT_DECISIONS` למספר מדויק של תוצאות
  - תיקון `COUNT_BY_GOVERNMENT_AND_TOPIC` עם priority 10 לזיהוי טוב יותר
  - הוספת `CONTEXTUAL_TOPIC` לשאילתות המשך כמו "ובנושא רפואה?"
- 🔧 **יצירת סקריפטי debug ממוקדים**:
  - `debug-government-37.sh` - בדיקה ממוקדת לבעיית ממשלה 37
  - `debug-complex-queries.sh` - בדיקת שאילתות מורכבות
  - `apply-fixes.sh` - החלת התיקונים
- 🚀 **תוצאות צפויות**:
  - "כמה החלטות קיבלה ממשלה 37?" יחזיר 2,358 החלטות
  - שאילתות מורכבות יחזירו תוצאות מדויקות
  - "הבא 20 החלטות" יחזיר בדיוק 20
- 📝 **קבצים שנוצרו/עודכנו**:
  - sql-engine/src/services/queryTemplates_fixed.ts
  - server/db_load/sql_functions/fix_government_functions.sql
  - TESTS/debug/ - תיקייה חדשה עם סקריפטי אבחון

### 24 ביוני 2025 - גרסה 2.3.6 🔴 **הסרת PandasAI והעברה מלאה ל-SQL Engine**
- ✅ **הסרת PandasAI מהמערכת**:
  - מחיקת כל ההפניות ל-PandasAI מקבצי Backend
  - הסרת קונטיינר pandasai מ-docker-compose.yml
  - כל השאילתות עוברות דרך SQL Engine בלבד
  - Backend מנהל את Intent Detection עם GPT-3.5
- 🔴 **בעיות קריטיות שנותרו**:
  - **ממשלה 37** - מחזיר רק 1 החלטה במקום 2,358
  - **שאילתות מורכבות** - "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?" מחזיר 2,878 (יותר מסך כל ההחלטות!)
  - **שאילתות המשך** - "ובנושא רפואה?" עובד אבל מחזיר רק 10 תוצאות
- ⚠️ **צעדים הבאים**:
  - תיקון template לזיהוי "כמה החלטות קיבלה ממשלה X"
  - תיקון שאילתות מורכבות (ממשלה + נושא)
  - בדיקה אם ה-10 תוצאות זו מגבלת תצוגה או בעיה בשאילתה
- 📝 **קבצים שעודכנו**:
  - server/src/controllers/chat.ts (הסרת PandasAI)
  - server/src/api/openai.ts (עדכון הודעות)
  - server/src/main.ts (עדכון הערות)
  - docker-compose.yml (החלפה עם גרסה בלי PandasAI)

### 24 ביוני 2025 - גרסה 2.3.5 🎯 **SQL Engine עובד מלא + תיקון Routing**
- ✅ **SQL Engine פעיל ב-100%**:
  - כל הקונטיינרים healthy ופעילים
  - 9/9 שאילתות חדשות עובדות דרך ה-API
  - תקשורת SSE (Server-Sent Events) עובדת מצוין
- 🔧 **תיקון בעיות Routing**:
  - הבעיה: endpoint היה `/api/chat/message` במקום `/api/chat`
  - תיקון בסקריפטי הבדיקה לשימוש ב-endpoint הנכון
  - יצירת `quick-test-sse.sh` לטיפול נכון ב-SSE responses
- 🚀 **תוצאות בדיקה מרשימות**:
  - ✅ החלטות לפי ועדה - עובד
  - ✅ ספירת אופרטיביות - עובד 
  - ✅ חיפוש לפי מיקום - עובד (30 תוצאות לתל אביב)
  - ✅ מגמה חודשית - עובד (12 חודשים)
  - ✅ ראש ממשלה + נושא - עובד
  - ✅ חיפוש טקסט "קורונה" - עובד (50 תוצאות)
- ⚠️ **בעיות קטנות שנותרו**:
  - זיהוי template לא מדויק ("החלטות של ועדת הכספים" → "החלטות לפי ראש ממשלה")
  - חיפוש מיקום בשדה לא נכון (tags_policy_area במקום tags_location)
  - פרמטרים חלקיים בחלק מהשאילתות
- 📝 **קבצים שעודכנו/נוצרו**:
  - TESTS/quick-test-sse.sh (סקריפט חדש)
  - TESTS/quick-test-new-types.sh (תיקון endpoint)

### 24 ביוני 2025 - גרסה 2.3.4 🔧 **תיקון TypeScript Error ב-SQL Engine**
- 🐛 **תיקון בעיית import חסר**:
  - הבעיה: `Module './queryTemplates' has no exported member 'findMatchingTemplate'`
  - הסיבה: הפונקציה `findMatchingTemplate` הייתה חסרה מ-sql-engine/queryTemplates.ts
  - הפתרון: סנכרון קובץ queryTemplates.ts עם הגרסה המלאה מ-server
- ✅ **עדכון queryTemplates.ts**:
  - הוספת הפונקציה החסרה findMatchingTemplate
  - הוספת כל ה-templates החסרים מהגרסה המלאה
  - SQL Engine אמור לעבוד עם כל סוגי השאילתות
- 📝 **קבצים שעודכנו**:
  - sql-engine/src/services/queryTemplates.ts (החלפה מלאה)

### 24 ביוני 2025 - גרסה 2.3.3 🔧 **תיקון בעיות LIMIT וניתוב NGINX**
- 🐛 **זיהוי וניתוח בעיית ה-LIMIT 50**:
  - גילוי: כל השאילתות מסוג PM_AND_TOPIC מחזירות בדיוק 50 תוצאות
  - גילוי: שאילתות CONTENT_SEARCH_DATE_RANGE מחזירות בדיוק 50 תוצאות
  - גילוי: שאילתות DECISIONS_BY_LOCATION מחזירות בדיוק 100 תוצאות
  - הסיבה: LIMIT קשיח בטמפלייטים במקום החזרת כל התוצאות
- 🔧 **תיקון בעיית LIMIT בטמפלייטים**:
  - הסרת LIMIT 50 מ-DECISIONS_BY_COMMITTEE
  - הסרת LIMIT 50 מ-PM_AND_TOPIC
  - הסרת LIMIT 50 מ-CONTENT_SEARCH_DATE_RANGE
  - הסרת LIMIT 100 מ-DECISIONS_BY_LOCATION
  - הוספת טמפלייט PM_TOPIC_COUNT לספירה מדויקת
- 🌐 **תיקון בעיית ניתוב NGINX**:
  - הבעיה: proxy_pass http://backend/api/ גרם לכפילות נתיב
  - הפתרון: שינוי ל-proxy_pass http://backend (בלי /api/)
  - תיקון גם ב-HTTP (port 80) וגם ב-HTTPS (port 443)
- 📝 **קבצים שנוצרו/עודכנו**:
  - sql-engine/src/services/queryTemplates_fixed.ts (תיקון LIMIT)
  - deploy/nginx/nginx_fixed.conf (תיקון ניתוב)
  - TESTS/test-limit-fix.sh (סקריפט בדיקה)
- 🎯 **תוצאה צפויה**:
  - שאילתות סטטיסטיות יחזירו את כל התוצאות, לא רק 50
  - API endpoints יהיו נגישים דרך NGINX
  - מספרים מדויקים ואמינים בתשובות

### 26 ביוני 2025 - גרסה 2.3.2 🚀 **הוספת סוגי שאילתות חדשות ל-SQL Engine**
- 🆕 **סוגי שאילתות חדשות שנוספו**:
  - ✅ חיפוש לפי ועדה (committee) עם/בלי שנה
  - ✅ ספירת החלטות לפי אופרטיביות (דקלרטיבית/אופרטיבית)
  - ✅ חיפוש לפי מיקום (tags_location) מתאריך מסוים
  - ✅ מגמה חודשית - כמה החלטות בכל חודש בשנה
  - ✅ ראש ממשלה + נושא ("מה עשה נתניהו בנושא חינוך?")
  - ✅ החלטות מימים אחרונים (טווחי תאריכים יחסיים)
  - ✅ השוואה בין שני נושאים ("חינוך לעומת בריאות ב-2024")
  - ✅ הוועדות המובילות (Top-N committees)
  - ✅ חיפוש טקסט בתוכן עם טווח תאריכים
- 🔍 **שאילתות שעדיין צריך להוסיף**:
  - ⏳ Fuzzy Search לטיפול בשגיאות כתיב
  - ⏳ טיפול משופר בתוצאות ריקות עם הצעות חלופיות
- 📝 **קבצים שעודכנו**: 
  - sql-engine/src/services/queryTemplates.ts (הוספת 9 templates חדשים)

### 23 ביוני 2025 - גרסה 2.3.1 🎯 **תיקונים משמעותיים ב-SQL Engine**
- ✅ **תיקון בעיית government_number**:
  - הבעיה: השוואת government_number כ-integer במקום text גרמה לשגיאות
  - הפתרון: עדכון nlToSQL.ts עם הנחיות ברורות שgovernment_number הוא TEXT
  - תוצאה: כל השאילתות עובדות נכון עם government_number = '37' או '37.0'
- ✅ **תמיכה במספר מדויק של תוצאות**:
  - הוספת טמפלייט X_DECISIONS ב-queryTemplates.ts
  - דוגמאות: "הבא 20 החלטות", "תן לי 50 החלטות אחרונות"
  - עדכון system prompt לכבד את המספר המבוקש
- ✅ **ספירה לפי נושא ושנה**:
  - הוספת טמפלייטים: COUNT_BY_TOPIC_AND_YEAR, YEAR_ONLY
  - תמיכה בשאילתות כמו "כמה החלטות בנושא רפואה היו ב2022?"
  - תמיכה בשאילתות הקשריות כמו "וב2021?"
- ✅ **ספירה לפי נושא וטווח תאריכים**:
  - הוספת טמפלייט COUNT_BY_TOPIC_AND_DATE_RANGE
  - הוספת פונקציה convertHebrewMonthToEnglish לתרגום חודשים
  - תמיכה בשאילתות כמו "כמה החלטות בנושא רפואה היו מפברואר 2000 עד מרץ 2010?"
- ✅ **שיפור תשובות הפורמטר**:
  - עדכון formatCount ב-formatter.ts להציג תשובות ספציפיות
  - התשובות עכשיו מתייחסות לנושא, תאריכים וכמות בצורה ברורה
  - דוגמה: "נמצאו 335 החלטות בנושא רפואה בתקופה: פברואר 2000 עד מרץ 2010"
- 📝 **קבצים שעודכנו**: 
  - sql-engine/src/services/nlToSQL.ts
  - sql-engine/src/services/queryTemplates.ts
  - sql-engine/src/services/formatter.ts

### 23 ביוני 2025 - גרסה 2.3.0 🎯 **שיפורי SQL Engine - תמיכה מלאה במספרי תוצאות ותשובות ספציפיות**
- ✅ **תיקון מספר התוצאות המבוקש**:
  - הוספת טמפלייט `X_DECISIONS` - "הבא 20 החלטות" מחזיר בדיוק 20
  - עדכון system prompt לכבד את המספר המבוקש ב-LIMIT
  - המערכת מזהה "תן לי 50 החלטות" ומחזירה בדיוק 50
- ✅ **תמיכה בשאילתות נושא + שנה**:
  - הוספת טמפלייט `COUNT_BY_TOPIC_AND_YEAR`
  - "כמה החלטות בנושא רפואה היו ב2022?" עובד מצוין
  - הוספת טמפלייט `YEAR_ONLY` לשאילתות הקשריות כמו "וב2021?"
- ✅ **תמיכה בשאילתות נושא + טווח תאריכים**:
  - הוספת טמפלייט `COUNT_BY_TOPIC_AND_DATE_RANGE`
  - תמיכה בחודשים בעברית: "מפברואר 2000 עד מרץ 2010"
  - הוספת פונקציית תרגום חודשים מעברית לאנגלית
- ✅ **שיפור משמעותי בתשובות**:
  - התשובות מתייחסות לפרטי השאילתה הספציפיים
  - "נמצאו 335 החלטות בנושא רפואה בתקופה: פברואר 2000 עד מרץ 2010"
  - הוספת תאריכי החלטה ראשונה ואחרונה בטווח
- 🔧 **תיקונים טכניים**:
  - תיקון בעיית government_number כ-TEXT (השוואה ל-'37' לא 37)
  - תיקון SQL parameters בתוך SELECT statements
  - עדכון system prompt עם הנחיות מפורטות
- 📝 **קבצים שהשתנו**: 
  - sql-engine/src/services/queryTemplates.ts (טמפלייטים חדשים)
  - sql-engine/src/services/nlToSQL.ts (system prompt משופר)
  - sql-engine/src/services/formatter.ts (formatCount משופר)
  - tests/test-new-features.sh (סקריפט בדיקות חדש)

### 23 ביוני 2025 - גרסה 2.2.9 🚀 **תיקון execute_simple_sql וטעינת הנתונים**
- 🔧 **תיקון הפרמטר ב-execute_simple_sql**:
  - שינוי מ-`query_text` ל-`query` בהתאם לפונקציה ב-Supabase
  - עכשיו כל הפונקציות מתחברות נכון ל-RPC
- ✅ **אימות טעינת נתונים**:
  - 24,716 רשומות נטענו בהצלחה ל-Supabase
  - כל השאילתות מחזירות תוצאות אמיתיות
- 📊 **סטטוס עדכני**:
  - 30/34 שאילתות עובדות (88.2%)
  - רק 4 שאילתות עם Invalid response format
  - 2 שאילתות עובדות אבל עם תוצאות לא מדויקות
- 📝 **קבצים שהשתנו**: sql-engine/src/services/executor.ts

### 23 ביוני 2025 - גרסה 2.2.8 🎆 **פריצת דרך ב-SQL Engine - 88% מהשאילתות עובדות!**
- 🔍 **אבחון ותיקון הבעיה האמיתית**:
  - הפונקציות עבדו ב-Supabase אבל SQL Engine לא קרא להן
  - גילוי שני קבצי queryTemplates.ts - אחד ב-server ואחד ב-sql-engine
  - SQL Engine השתמש בגרסה הישנה של ה-templates
- ✅ **תיקון בעיות RPC Execution**:
  - עדכון executor.ts לטיפול נכון בתגובות execute_simple_sql
  - תיקון בעיות formatting ב-count ו-aggregate responses
  - הוספת פונקציה `execute_simple_sql` ל-Supabase
- 🚀 **תוצאות מרשימות**:
  - 30/34 שאילתות עובדות (88.2%) - שיפור מ-76.5%
  - 7 שאילתות שנכשלו עובדות עכשיו
  - רק 4 שאילתות עדיין נכשלות (טווחי תאריכים + ממשלה אחרונה)
- 📦 **עדכון SQL Engine לקונטיינר נפרד**:
  - הפרדה מוצלחת לקונטיינר עצמאי על פורט 8002
  - עדכון כל ה-templates לשימוש בפונקציות RPC
  - הוספת templates חדשים לשאילתות שהיו חסרות
- 📦 **קבצים שהשתנו**: 
  - sql-engine/src/services/queryTemplates.ts (עדכון מלא)
  - sql-engine/src/services/executor.ts (תיקון RPC response handling)
  - sql-engine/src/services/formatter.ts (תיקון count/aggregate formatting)
  - server/db_load/sql_functions/fix_sql_functions.sql (כל הפונקציות)
  - server/db_load/sql_functions/add_execute_simple_sql.sql

### 23 ביוני 2025 - גרסה 2.2.7 🎯 **אבחון בעיות SQL Engine והחלטה להחליף את PandasAI**
- 🔍 **אבחון בעיות בסקריפטי הבדיקה**:
  - תיקון URL מ-HTTP ל-HTTPS בסקריפטים המשניים
  - תיקון נתיב health check ל-`/api/chat/health`
  - התאמת פורמט הבקשה ל-test-sql endpoint
- 📊 **סטטוס מעודכן**:
  - 26/34 שאילתות עובדות (76.5%)
  - 3 שאילתות עובדות חלקית (תוצאות לא מדויקות)
  - 8 שאילתות נופלות ל-PandasAI כי חסרות פונקציות SQL
- 🆕 **יצירת 8 פונקציות SQL נוספות**:
  - קובץ `complete_sql_functions.sql` מוכן להרצה ב-Supabase
  - תיקון כל שמות העמודות בהתאם לטבלה הקיימת
  - החלפת `link` ב-`decision_url`, `prime_minister_name` ב-`prime_minister`
  - החלפת `subject` ב-`summary`, הסרת `executive_body_name`
- 🎯 **החלטה אסטרטגית**:
  - מיקוד בהשלמת SQL Engine במקום לתקן את PandasAI
  - לאחר הרצת הפונקציות החדשות - הסרת PandasAI לגמרי
- 📝 **קבצים שהשתנו**: 
  - complete_sql_functions.sql (נוצר מחדש עם העמודות הנכונות)
  - queryTemplates.ts (תוקן prime_minister_name)
- 🗓️ **מבנה טבלת israeli_government_decisions**:
  - `decision_date` (date)
  - `decision_number` (text)
  - `committee` (text)
  - `decision_title` (text)
  - `decision_content` (text)
  - `decision_url` (text) - לא link!
  - `summary` (text) - לא subject!
  - `operativity` (text)
  - `tags_policy_area` (text)
  - `tags_government_body` (text)
  - `tags_location` (text)
  - `all_tags` (text)
  - `government_number` (text)
  - `prime_minister` (text) - לא prime_minister_name!
  - `decision_key` (text)# 🚀 CECI-AI - מערכת חיפוש החלטות ממשלה חכמה

## 📋 גרסה ותאריך
**יוני 2025 — גרסה 2.3.2** 🚀 (SQL Engine עם 9 סוגי שאילתות חדשות!)

## 🚨 סטטוס נוכחי - SQL Query Engine בלבד, PandasAI הוסר!
**תאריך עדכון אחרון: 24 ביוני 2025, 13:00**

### ✅ מה עובד (מאומת ב-24/06/2025):
- **SQL Query Engine** - פעיל ב-100% בלי PandasAI
- **RPC Functions** - כל 11 הפונקציות עובדות ב-Supabase
- **נתונים** - 24,716 רשומות נטענו בהצלחה
- Docker Compose Infrastructure - כל 5 השירותים (בלי PandasAI)
- API Routing + Redis + SSL
- תשובות אנושיות לשיחה כללית (GPT Intent Detection)

### 🔴 בעיות קריטיות שנותרו:
- **ממשלה 37** - מחזיר רק 1 החלטה במקום 2,358
- **שאילתות מורכבות** - "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?" מחזיר 2,878
- **תצוגה מוגבלת** - שאילתות המשך מחזירות רק 10 תוצאות

#### ✅ שאילתות שעובדות באופן עקבי (39/43 עם העדכון החדש):
**💡 טיפ: לבדיקה מלאה הרץ `./TESTS/test-sql-engine.sh`**
- **ספירות בסיסיות** ✓
  - "כמה החלטות יש בסך הכל?" 
  - "כמה החלטות יש?" 
  - "כמה החלטות קיימות?"
- **ספירות לפי שנה** ✓
  - "כמה החלטות יש משנת 2023?"
  - "כמה החלטות התקבלו בשנת 2024?"
  - "כמה החלטות היו בשנת 2022?"
- **החלטות ספציפיות** ✓
  - "החלטה 660 של ממשלה 35"
  - "החלטה 100 של ממשלה 37"
  - "החלטה 1" (מחזיר רשימה)
- **חיפוש לפי נושא** ✓
  - "הבא לי החלטה בנושא תחבורה"
  - "הבא לי החלטה בנושא חינוך"
  - "הבא לי החלטה בנושא בריאות"
  - "הבא 5 החלטות בנושא ביטחון"
- **סטטיסטיקה לממשלה** ✓
  - "סטטיסטיקה של ממשלה 37" (2,358 החלטות)
  - "סטטיסטיקה של ממשלה 36" (1,447 החלטות)
  - "סטטיסטיקה על ממשלה 35" (944 החלטות)
- **ספירות לפי נושא** ✓
  - "כמה החלטות יש בנושא כלכלה?" (1,367 החלטות)
  - "כמה החלטות יש בנושא חינוך?" (1,488 החלטות)
- **החלטות לפי ראש ממשלה** ✓
  - "החלטות של נתניהו" (100 החלטות)
- **החלטות חשובות לפי שנה** ✓
  - "מה ההחלטות החשובות ביותר של 2024?" (20 החלטות)
- **סטטיסטיקה לכל ממשלה** ✓
  - "כמה החלטות קיבלה כל ממשלה?" (15 ממשלות)
- **החלטות אחרונות** ✓
  - "ההחלטות האחרונות"
  - "החלטות אחרונות"
  - "החלטות עדכניות"
- **החלטות לפי ועדה** ✓ 🆕
  - "החלטות ועדת השרים לענייני חקיקה ב-2023"
  - "החלטות של ועדת הכספים"
- **ספירה לפי אופרטיביות** ✓ 🆕
  - "כמה החלטות דקלרטיביות היו ב-2024?"
  - "כמה החלטות אופרטיביות?"
- **חיפוש לפי מיקום** ✓ 🆕
  - "החלטות על ירושלים שהתקבלו מאז 2020"
  - "החלטות לגבי תל אביב מ-2022"
- **מגמה חודשית** ✓ 🆕
  - "כמה החלטות היו בכל חודש ב-2023?"
- **ראש ממשלה + נושא** ✓ 🆕
  - "מה עשה נתניהו בנושא חינוך?"
  - "מה עשתה גולדה בנושא ביטחון?"
- **טווחי תאריכים יחסיים** ✓ 🆕
  - "החלטות מה-7 הימים האחרונים"
  - "החלטות מ-30 הימים האחרונים"
- **השוואה בין נושאים** ✓ 🆕
  - "כמה החלטות חינוך לעומת בריאות ב-2024?"
- **ועדות מובילות** ✓ 🆕
  - "3 הוועדות שהנפיקו הכי הרבה החלטות"
- **חיפוש טקסט עם תאריכים** ✓ 🆕
  - "'קורונה' בין 2020-2021"

### 🚀 יתרונות SQL Engine:
1. **ביצועים** - שאילתות רצות ישירות ב-DB
2. **דיוק** - תשובות מדויקות, לא מדגמים
3. **זיכרון** - לא צריך לטעון 24K רשומות
4. **סקיילביליות** - יכול לעבוד עם מיליוני רשומות
5. **עלות נמוכה** - פחות טוקנים ל-GPT

### ❌ שאילתות שלא עובדות (4/43):
- **הממשלה האחרונה + נושא** - "החלטות הממשלה האחרונה בנושא תחבורה"
  - ה-template לא מזהה "האחרונה" כמו "הנוכחית"
- **שאילתות מורכבות**:
  - "החלטות בנושא חינוך מהשנה האחרונה"
- **שגיאות כתיב (Fuzzy Search)** - "החלטות בנושא טכהבורה" (שגיאה במילה *תחבורה*)
  - צריך להוסיף יכולת fuzzy matching עם pg_trgm
- **תוצאות ריקות משופרות** - "ממשלה 50"
  - להחזיר הודעה ידידותית יותר עם הצעות

### ⚠️ שאילתות שעובדות חלקית (2/34):
- **"כמה החלטות בנושא חינוך החליטה ממשלה מס 37"** ✅❌
  - עובד אבל מחזיר את כל החלטות החינוך (1488) במקום רק של ממשלה 37
- **"כמה החלטות בנושא חינוך עברו בין 2020 ל2022?"** ✅❌
  - עובד אבל מחזיר את כל החלטות החינוך במקום רק 2020-2022

### 🎯 השלב הבא: הסרת PandasAI וניקוי הפרויקט

**מה צריך לעשות:**
1. **הסרת PandasAI לגמרי** - SQL Engine מחליף אותו ב-100%
   - מחיקת כל קבצי Python ב-server/src/services/python/
   - הסרת pandasai container מ-docker-compose.yml
   - הסרת כל הקוד הקשור ל-PandasAI מ-backend
   - עדכון או הסרת pandasAIService.ts

2. **ניקוי קבצים מיותרים**
   - הסרת test scripts ישנים
   - ניקוי קבצי גיבוי וטמפורריים
   - הסרת תלויות Python לא רלוונטיות

3. **הכנה ל-Production**
   - הגדרת SSL certificates אמיתיים
   - עדכון nginx.conf לדומיין אמיתי
   - הגדרת environment variables ל-production
   - הסרת פורטים מיותרים (8001, 8002 לא אמורים להיות חשופים)

4. **העלאה ל-GitHub**
   - יצירת .gitignore מעודכן
   - וידוא שאין קבצי .env ב-commit
   - יצירת README.md חדש וברור
   - תיעוד הוראות התקנה

### ⚠️ בעיות פתוחות שנותרו:
1. **בעיות קטנות ב-SQL Engine**:
   - זיהוי template לא מדויק לועדות
   - חיפוש מיקום בשדה לא נכון
   - פרמטרים חלקיים
2. **שאילתות שעדיין נכשלות (4/43)**:
   - הממשלה האחרונה + נושא
   - שאילתות מורכבות
   - Fuzzy Search לשגיאות כתיב
   - תוצאות ריקות משופרות
3. **שיפורי UX** - שגיאות כתיב, פוקוס בשדה קלט, זיהוי הקשר

### 🎆 הבעיה שנפתרה זה עתה:
**חיפוש החלטות ספציפיות** - לדוגמה "החלטה 660 של ממשלה 35"
- נפתר על ידי טיפול ישיר בקוד Python
- שימוש בעמודת decision_key
- מחזיר הודעה מפורטת אם ההחלטה קיימת בממשלות אחרות

## 📂 מיפוי קבצים חשובים - קיצור דרך למפתחים

### 🔧 קבצי הגדרות ראשיים
- **`.env.prod`** - משתני סביבה ל-production (תיקייה ראשית)
- **`docker-compose.yml`** - הגדרות Docker Compose (תיקייה ראשית)
- **`docker-compose.prod.yml`** - override ל-production
- **`nginx.conf`** - nginx פשוט (תיקייה ראשית)
- **`deploy/nginx/nginx.conf`** - nginx מלא ל-production

### 🐍 PandasAI Service
- **`server/src/services/python/pandasai_service.py`** - השירות הראשי
- **`server/src/services/python/session_manager.py`** - ניהול sessions
- **`server/src/services/python/redis_session_store.py`** - Redis integration
- **`server/src/services/python/query_optimizer.py`** - אופטימיזציית שאילתות
- **`server/src/services/python/validation/response_validator.py`** - בדיקת תשובות
- **`server/src/services/python/Dockerfile`** - Docker config ל-PandasAI
- **`server/src/services/python/requirements_pandasai.txt`** - תלויות Python

### 🖥️ Backend (Node.js)
- **`server/src/main.ts`** - נקודת כניסה ראשית
- **`server/src/controllers/chat.ts`** - טיפול בשיחות
- **`server/src/services/pandasAIService.ts`** - תקשורת עם PandasAI
- **`server/src/services/intentDetectionService.ts`** - זיהוי כוונות (חדש!)
- **`server/src/api/openai.ts`** - חיבור ל-OpenAI
- **`server/src/routes/`** - הגדרת נתיבי API
- **`server/Dockerfile`** - Docker config ל-backend

### ⚛️ Frontend (React)
- **`src/App.tsx`** - קומפוננטה ראשית
- **`src/services/chat.service.ts`** - תקשורת עם backend
- **`src/components/Chat/`** - קומפוננטות צ'אט
- **`src/pages/`** - דפי האפליקציה
- **`Dockerfile`** - Docker config ל-frontend (תיקייה ראשית)
- **`vite.config.ts`** - הגדרות Vite

### 🗄️ Database & Data
- **`server/db_load/decisions.xlsx`** - קובץ נתונים מקורי
- **`server/db_load/db_load.js`** - סקריפט טעינה ל-Supabase

### 🛠️ סקריפטים ועזרים
- **`TESTS/`** - כל סקריפטי הבדיקה (תיקייה מרוכזת)
  - `test-sql-engine.sh` - בדיקה מקיפה של SQL Engine
  - `test-limit-fix.sh` - בדיקת תיקון בעיית LIMIT
  - `test-new-features.sh` - בדיקת פיצ'רים חדשים
  - `test-comprehensive-stability.sh` - בדיקת יציבות
  - `run-all-tests.sh` - הרצת כל הבדיקות
- **`start-all-services.sh`** - הרצת כל השירותים
- **`build-production.sh`** - בנייה ל-production
- **`run-local.sh`** - הרצה לוקלית
- **`check-system.sh`** - בדיקת מערכת

### 📚 תיעוד
- **`FULL_PROJECT_SUMMARY.md`** - המסמך הזה
- **`DEPLOYMENT.md`** - הוראות פריסה מפורטות
- **`README.md`** - תיעוד כללי
- **`SYSTEM_INSTRUCTIONS.md`** - הוראות מערכת
- **`UBUNTU_SETUP.md`** - הגדרת Ubuntu/WSL

### 🔐 Supabase
- **`supabase/functions/get-decisions/`** - Edge Function לטעינת נתונים
- **`supabase/migrations/`** - שינויי DB

## 🆕 שינויים מרכזיים בגרסה 2.0

### 🏗️ שינויי ארכיטקטורה מהותיים
- 🐳 **מעבר ל-Docker Compose** - המערכת כולה רצה ב-containers
- 🔴 **הוספת Redis** - לניהול sessions עם persistence
- 🌐 **Nginx Reverse Proxy** - לניתוב וSSL termination
- 📦 **Response Validator** - מניעת hallucination של PandasAI

### 🚀 פיצ'רים חדשים
- Docker Support מלא עם health checks
- Redis Session Store עם TTL אוטומטי
- Response Validation (מושבת כרגע)
- Production Ready + SSL Support + Rate Limiting

### 🔧 תיקוני באגים
- ✅ **תיקון בעיית Hallucination** - הוספת ResponseValidator שמוודא שכל החלטה קיימת
- ✅ **שיפור Reference Resolution** - קוד מפורש יותר למניעת החזרת החלטות שגויות
- ✅ **תיקון בעיות CORS** - עדכון FRONTEND_URL ל-localhost:8080
- ✅ **תיקון בעיות Docker** - הסרת hardcoded paths, שימוש ב-.env.prod מקומי

### 📦 עדכון תלויות
- ➕ **redis==5.0.1** - נוסף ל-requirements_pandasai.txt
- 🔄 **Docker images** - redis:7-alpine, nginx:alpine, python:3.11-slim, node:18-alpine

## 📋 סקירה כללית
מערכת CECI-AI היא פלטפורמה מתקדמת לחיפוש וניתוח החלטות ממשלת ישראל באמצעות AI. המערכת משלבת ממשק משתמש מודרני (React), שרת Backend (Node.js), ושירות AI חכם (PandasAI + GPT) שמאפשר שאילתות בשפה טבעית בעברית.

## 🏗️ ארכיטקטורת המערכת - עדכון נוכחי (גרסה 2.3.5)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Nginx         │────▶│    Backend       │────▶│   SQL Engine    │     │   PandasAI      │
│  (Reverse Proxy)│◀────│   (Node.js)      │◀────│   (Node.js)     │     │   (Python)      │
│   Port 80/443   │     │   Port 5173      │     │   Port 8002     │     │   Port 8001     │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                          │                          │
         ▼                      ▼                          ▼                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │     │     Redis        │     │  Supabase DB    │
│  (React+Nginx)  │     │  (Session Store) │     │  (24,716 rows)  │
│   Internal      │     │   Port 6379      │     │   External      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### 🔗 קישוריות ו-Routing (מעודכן)

#### 🌐 External Access:
- **Frontend**: http://localhost:80 → Nginx → Frontend container
- **API**: http://localhost/api/chat → Nginx → Backend:5173 → SQL Engine:8002
- **Direct SQL Engine**: http://localhost:8002 (רק לפיתוח)
- **Direct PandasAI**: http://localhost:8001 (רק לפיתוח)

#### 🔄 Internal Docker Network (ceci-network):
- **Backend → SQL Engine**: http://sql-engine:8002/api/process-query
- **Backend → PandasAI**: http://pandasai:8001 (כרגע מושבת)
- **Backend → Redis**: redis://redis:6379
- **Backend → Supabase**: https://[project].supabase.co (חיצוני)

#### 🔧 API Endpoints:
- **Chat**: POST `/api/chat` - מקבל message ו-sessionId, מחזיר SSE stream
- **Health**: GET `/api/health` - בדיקת בריאות
- **Test SQL**: POST `/api/chat/test-sql` - בדיקה ישירה של SQL Engine

## 🐳 Docker Compose Services

```yaml
services:
  redis:        # Session storage & caching
  sql-engine:   # SQL Query Engine  
  backend:      # Node.js API
  frontend:     # React app with nginx
  nginx:        # Main reverse proxy + SSL
  certbot:      # SSL certificate renewal
```

## ⚠️ חשוב: המערכת קוראת מ-Supabase, לא מקובץ CSV!
המערכת טוענת 24,716 החלטות ישירות מ-Supabase דרך Edge Function.

## 📁 מבנה הפרויקט המעודכן

```
ceci-ai-testing-main/
│
├── 📁 src/                          # Frontend React Application
│   ├── 📁 components/               
│   ├── 📁 services/                
│   └── 📁 pages/
│
├── 📁 server/                       # Backend Node.js Application
│   ├── 📁 src/
│   │   ├── 📁 services/
│   │   │   └── 📁 python/          # PandasAI Service
│   │   │       ├── pandasai_service.py
│   │   │       ├── session_manager.py
│   │   │       ├── redis_session_store.py  # חדש!
│   │   │       ├── validation/             # חדש!
│   │   │       │   └── response_validator.py
│   │   │       ├── Dockerfile              # חדש!
│   │   │       └── requirements_pandasai.txt
│   │   └── 📁 controllers/
│   ├── Dockerfile                   # חדש!
│   └── .dockerignore               # חדש!
│
├── 📁 deploy/                       # חדש! Deployment files
│   └── 📁 nginx/
│       ├── Dockerfile
│       ├── nginx.conf
│       └── frontend.nginx.conf
│
├── docker-compose.yml               # חדש!
├── Dockerfile                       # Frontend Dockerfile
├── .dockerignore
├── .env.prod                       # Production environment
└── FULL_PROJECT_SUMMARY.md         # המסמך הזה
```

## 🛠️ הגדרות וקונפיגורציה - Production

### 🔑 משתני סביבה ב-.env.prod
```env
# Frontend
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbG...
VITE_API_URL=/api  # נתיב יחסי ל-production

# Backend
NODE_ENV=production
PORT=5173
OPENAI_API_KEY=sk-proj-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...
FRONTEND_URL=http://localhost:8080
PANDASAI_SERVICE_URL=http://pandasai:8001

# Redis - חדש!
REDIS_URL=redis://redis:6379
```

### 🐳 Docker Configuration
```yaml
# Health checks לכל שירות
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:port/health"]
  interval: 30s
  timeout: 10s
  retries: 3

# Networks
networks:
  ceci-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🆕 Response Validator - מניעת Hallucination ⚠️ **מומלץ להשבית**

### בעיות שהתגלו ופתרונות:
1. ✅ **Context Length Exceeded** - תוקן! QueryOptimizer מגביל את הנתונים
2. ⚠️ **Validator חוסם תוצאות אמיתיות** - עדיין בעייתי, מומלץ להשבית
3. ✅ **שליחת DataFrame מלא** - תוקן! שולחים רק נתונים רלוונטיים

### המלצה לפני פריסה:
**השבת את ה-Validator זמנית** עד שיתוקן האלגוריתם שלו

### ResponseValidator
ResponseValidator היא מחלקה שבודקת שכל החלטה שמוחזרת קיימת במסד הנתונים, מסירה החלטות לא תקפות ומחזירה warnings.

**פרטי יישום**: ראה `server/src/services/python/validation/response_validator.py`

⚠️ **בעיה: ה-Validator חוסם גם תוצאות אמיתיות ומחזיר "לא נמצאו החלטות" למרות שיש תוצאות!**

## 🔴 Redis Session Store - חדש!

### ארכיטקטורת Redis Store
RedisSessionStore מנהל session storage עם TTL אוטומטי, fallback ל-memory והסתרת סיסמאות בלוגים.

**פרטי יישום**: ראה `server/src/services/python/redis_session_store.py`

### תכונות Redis Integration
- ✅ חיבור דרך `REDIS_URL` בלבד
- ✅ TTL אוטומטי (30 דקות default)
- ✅ Fallback ל-memory אם Redis לא זמין
- ✅ הסתרת סיסמאות בלוגים
- ✅ Health check endpoint: `/redis/status`

## 🚀 הרצת המערכת ב-Docker

### דרישות מקדימות
1. **Docker** & **Docker Compose**
2. **קובץ .env.prod** עם כל המשתנים
3. **OpenAI API Key** עם קרדיט

### הרצה
```bash
# בניה והרצה
docker compose up -d --build

# צפייה בלוגים
docker compose logs -f

# בדיקת סטטוס
docker compose ps

# עצירה
docker compose down
```

### בדיקות
- Frontend: `https://localhost/` (צריך לאשר self-signed certificate)
- Backend Health: `http://localhost:5173/health` (לא `/api/health`)
- PandasAI: `http://localhost:8001/`
- Redis Status: `http://localhost:8001/redis/status` (כרגע מחזיר 404)

## 🎯 הנחיות קריטיות לפני פריסה

### 1️⃣ **בדיקת Environment Variables**
```bash
# ודא שכל המשתנים קיימים ב-.env.prod:
- OPENAI_API_KEY (חובה! עם קרדיט)
- SUPABASE_URL & SUPABASE_SERVICE_KEY
- VITE_SUPABASE_URL & VITE_SUPABASE_ANON_KEY
- REDIS_URL=redis://redis:6379
```

### 2️⃣ **השבתת Response Validator (זמנית)**
ב-`server/src/services/python/pandasai_service.py` שורה 846:
```python
# response_validator = ResponseValidator(df)
response_validator = None  # DISABLED - too aggressive
```

### 3️⃣ **הגדרת SSL ל-Production**
1. עדכן את `nginx.conf` עם הדומיין האמיתי
2. הפעל certbot לקבלת SSL:
```bash
docker compose run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d your-domain.com
```

### 4️⃣ **בדיקות לפני פריסה**
**ראה DEPLOYMENT.md לרשימת בדיקות מלאה**
- בדיקת health של כל השירותים
- בדיקת API endpoints
- בדיקת Redis ולוגים

### 5️⃣ **אופטימיזציות מומלצות ל-Production**
1. **הגדל את ה-rate limits** ב-nginx.conf אם צריך
2. **הוסף monitoring** - Prometheus/Grafana
3. **הגדר log aggregation** - ELK Stack
4. **Backup strategy** ל-Redis data
5. **הגדר health check alerts**

## 🔧 טיפול בבעיות נפוצות - Docker

### 🐛 בעיית הרשאות Docker
```bash
# הוסף משתמש לקבוצת docker
sudo usermod -aG docker $USER
newgrp docker

# או השתמש ב-sudo
sudo docker compose up -d --build
```

### 🐛 בעיה: env file not found
**פתרון:** ודא שקובץ `.env.prod` קיים בתיקייה הראשית

### 🐛 בעיית WSL Integration
**פתרון:** 
1. פתח Docker Desktop
2. Settings → Resources → WSL Integration
3. הפעל את ה-Ubuntu distro

## 📊 API Endpoints חדשים

### Decision Validation
```bash
# בדיקה אם החלטה קיימת
GET /validate-decision/{decision_number}

# קבלת פרטי החלטה
GET /decision/{decision_number}
```

### Redis Status
```bash
# בדיקת סטטוס Redis
GET /redis/status
```

## 🚧 פיתוחים עתידיים - עדכון

### 🎯 משימות לביצוע מיידי
1. ✅ **תיקון PandasAI Context Length** - הושלם! עובד מצוין
2. 🚨 **תיקון Response Validator** - עדיין חוסם, מומלץ להשבית
3. ✅ **ייעול שליחת נתונים ל-GPT** - הושלם עם query_optimizer משופר
4. ✅ **Redis Integration** - הושלם!
5. ✅ **Docker Support** - הושלם!
6. ✅ **תיקון Backend Routes** - הושלם!
7. ✅ **תיקון Health Checks** - הושלם (היה false positive)
8. ⏳ **Production Deployment** - מוכן עם הסתייגויות
9. ⏳ **GitHub Actions CI/CD** - הבא בתור
10. ⏳ **Monitoring & Logging** - ELK Stack
11. 🆕 **שיפורי UX דחופים**:
    - **תיקון אוטומטי לשגיאות כתיב** - הוספת fuzzy matching לזיהוי "הבא ליי" → "הבא לי"
    - **שמירת פוקוס בשדה הקלט** - אחרי Enter להישאר בשדה הכתיבה
    - **זיהוי הקשר משופר** - "תוכן ההחלטה" → להבין שמתכוונים להחלטה האחרונה
    - **הצעות אוטומטיות** - הצעת תיקונים בזמן אמת
    - **היסטוריית חיפושים** - גישה מהירה לחיפושים קודמים
12. 🆕 **תיקון חיפוש לפי מספר החלטה** - להבין ש-decision_number הוא string

### 🆕 שאילתות חדשות שנוספו:
1. **ספירה לפי ממשלה ונושא** - "כמה החלטות בנושא חינוך החליטה ממשלה מס 37"
   - Template: `COUNT_BY_GOVERNMENT_AND_TOPIC`
2. **ספירה לפי נושא וטווח תאריכים** - "כמה החלטות בנושא חינוך עברו בין 2020 ל2022?"
   - Template: `COUNT_BY_TOPIC_AND_DATE_RANGE`

### 🔮 פיצ'רים מתקדמים
1. **Kubernetes** - מעבר מ-Docker Compose
2. **GraphQL API** - במקום REST
3. **WebSocket Support** - Real-time updates
4. **Multi-tenant** - תמיכה בארגונים מרובים
5. **Analytics Dashboard** - Grafana integration

## 🔧 המלצות לתיקון בעיות PandasAI

### 🤖 בעיות בקוד שמייצר PandasAI
הבעיה: PandasAI לא עוקב אחרי ההוראות המפורשות ב-CUSTOM_INSTRUCTIONS ומייצר קוד שגוי.

**פתרונות אפשריים:**

1. **שדרוג ל-GPT-4** - יותר טוב במעקב אחר הוראות:
   ```python
   "llm": OpenAI(
       api_token=os.getenv("OPENAI_API_KEY"),
       model="gpt-4" או "gpt-4-turbo-preview"
   )
   ```

2. **הוספת Pre-processor** שמתקן קוד לפני הרצה:
   ```python
   class CodeFixer:
       def fix_common_errors(self, code):
           # תיקון concat ריק
           code = code.replace('pd.concat([])', 'pd.DataFrame()')
           # תיקון הפניות ל-dfs
           code = code.replace('for df in dfs:', '# SKIP')
           return code
   ```

3. **שימוש ב-LangChain** במקום PandasAI:
   - שליטה טובה יותר על ה-prompts
   - אפשרות ל-chain של פעולות

4. **כתיבת פונקציות מוגדרות מראש** לשאילתות נפוצות:
   ```python
   def get_decisions_by_topic(df, topic):
       return df[df['tags_policy_area'].str.contains(topic, na=False)]
   
   def get_decisions_by_year(df, year):
       return df[df['year'] == year]
   ```

5. **החלפת PandasAI ב-Direct Query** לשאילתות פשוטות:
   - זיהוי דפוסים ושימוש בקוד מוגדר מראש
   - PandasAI רק לשאילתות מורכבות

## 🔄 עדכונים אחרונים

### 22 ביוני 2025 - גרסה 2.2.6 🆕 **הוספת שאילתות מורכבות חדשות**
- 🆕 **הוספת 2 templates חדשים ל-queryTemplates.ts**:
  - `COUNT_BY_GOVERNMENT_AND_TOPIC` - ספירת החלטות לפי ממשלה ונושא
  - `COUNT_BY_TOPIC_AND_DATE_RANGE` - ספירת החלטות לפי נושא וטווח תאריכים
- 🔧 **תיקון בעית health check בסקריפטים**:
  - שינוי מ-`/health` ל-`/api/health` בסקריפטים החדשים
- 📋 **עדכון הסקריפטים**:
  - הוספת השאילתות החדשות לכל 3 סקריפטי הבדיקה
  - יצירת `test_content_search.py` לבדיקת חיפוש טקסט
- 📝 **קבצים שהשתנו**: queryTemplates.ts, test-sql-engine.sh, test-sql-engine-quick.sh, test-sql-engine-failed.sh

### 22 ביוני 2025 - גרסה 2.2.5 🚀 **תיקון כולל לבעיות SQL Engine**
- 🆕 **יצירת 8 פונקציות SQL חדשות ב-Supabase**:
  - `count_decisions_by_topic()` - ספירת החלטות לפי נושא
  - `search_decisions_content()` - חיפוש טקסט עם full-text search
  - `get_decisions_by_date_range()` - החלטות בטווח תאריכים
  - `get_decisions_by_government_and_topic()` - ממשלה + נושא
  - `count_decisions_per_government()` - סטטיסטיקה לכל הממשלות
  - `get_decisions_by_prime_minister()` - החלטות לפי ראש ממשלה
  - `get_important_decisions_by_year()` - החלטות חשובות לפי שנה
  - `search_decisions_hebrew()` - חיפוש משופר בעברית
- ✅ **עדכון queryTemplates.ts**:
  - מעבר לשימוש בפונקציות SQL במקום שאילתות ישירות
  - הוספת 5 templates חדשים לשאילתות מורכבות
  - תיקון כל בעיות אי-התאמת הטיפוסים
- 📝 **קבצים חדשים**:
  - `server/db_load/sql_functions/additional_functions.sql`
- ⚠️ **הבא בתור**: צריך להריץ את הפונקציות ב-Supabase ולבדוק מחדש

### 22 ביוני 2025 - גרסה 2.2.4 🎯 **תיקון התאמת טיפוסים ב-SQL Engine**
- ✅ **תיקון בעיית government_number**:
  - הנתונים מאוחסנים כ-"37.0" במקום "37"
  - עדכון לחיפוש בשתי הגרסאות: WHERE government_number IN ($1, $2)
  - סטטיסטיקת ממשלה 37 מחזירה עכשיו 2,358 החלטות (לא 1!)
- ✅ **שיפור טיפול בפרמטרים**:
  - כל הפרמטרים מטופלים כטקסט עם גרשיים
  - תמיכה בתאריכים ו-NULL
- 🔧 **עדכון queryTemplates.ts**:
  - החלפת STRING_AGG ב-GROUP BY פשוט יותר
  - הוספת ORDER BY COUNT(*) DESC לקבלת התוצאה הנכונה
- 📊 **תוצאות בדיקות**:
  - ✅ ספירת החלטות: 24,716
  - ✅ החלטה ספציפית: עובד מצוין
  - ✅ חיפוש לפי נושא: עובד
  - ✅ סטטיסטיקה לממשלה: עובד עם המספרים הנכונים
  - ❌ שאילתות מורכבות: עדיין דורשות עבודה

### 22 ביוני 2025 - גרסה 2.2.3 🏗️ **הפרדת SQL Engine לשירות עצמאי**
- ✅ **תיקון באג קריטי ב-executor.ts**:
  - תיקון placeholder מ-`${index + 1}` ל-`${index + 1}`
  - עכשיו פרמטרים מועברים נכון ל-RPC function
- 🆕 **הפרדת SQL Engine לקונטיינר נפרד**:
  - יצירת פרויקט `sql-engine` עצמאי
  - Express server על פורט 8002
  - API endpoints: `/api/process-query`, `/api/execute-sql`, `/api/schema`
  - בניות מהירות יותר ופיתוח עצמאי
- 🔄 **עדכון Backend לתקשורת HTTP**:
  - שימוש ב-axios במקום import ישיר
  - תקשורת דרך `SQL_ENGINE_URL=http://sql-engine:8002`
- 📝 **קבצים חדשים**: 
  - `sql-engine/` - פרויקט חדש עם כל קבצי SQL Engine
  - עדכון docker-compose.yml עם שירות sql-engine
  - עדכון sqlQueryEngineService.ts לתקשורת HTTP

### 22 ביוני 2025 - גרסה 2.2.2 🚀 **SQL Engine עובד במלואו עם RPC Functions**
- ✅ **תיקון חיפוש החלטה ספציפית**:
  - שימוש ב-decision_key במקום decision_number + government_number
  - החלטה 660 של ממשלה 35 נמצאת עכשיו!
- ✅ **יצירת RPC Functions ב-Supabase**:
  - `count_all_decisions()` - ספירת כל ההחלטות
  - `count_decisions_by_year()` - ספירה לפי שנה
  - `get_government_statistics()` - סטטיסטיקה לממשלה
  - `execute_simple_sql()` - הרצת SQL בטוחה
- ✅ **עדכון Templates**:
  - מעבר לשימוש ב-RPC functions
  - הפעלת USE_SUPABASE_RPC=true
- 🎯 **תוצאות**:
  - כל סוגי השאילתות עובדים!
  - ביצועים משופרים
  - אבטחה טובה יותר
- 📝 **קבצים שהשתנו**: queryTemplates.ts, .env.prod + SQL functions ב-Supabase

### 22 ביוני 2025 - גרסה 2.2.1 🔧 **תיקוני SQL Engine והפעלה מלאה**
- 🔄 **הפעלת SQL Engine ב-100%**:
  - שינוי SQL_ENGINE_PERCENTAGE=100
  - כיבוי USE_SUPABASE_RPC=false (לא קיים RPC function)
  - בדיקות מקיפות עם test-sql-engine.sh
- 🔧 **תיקוני עמודות computed**:
  - החלפת year ב-EXTRACT(YEAR FROM decision_date)
  - פישוט שאילתות COUNT להתאמה ל-Query Builder
  - תיקון STRING_AGG במקום ARRAY_AGG
- 📊 **הבנת ה-Pipeline**:
  - Intent Detection (GPT-3.5) → תמיד
  - SQL Engine: NL→SQL (GPT-3.5) + Query Executor + Formatter
  - PandasAI: כבוי כרגע כש-SQL Engine פעיל
- ⚠️ **בעיות שנותרו**:
  - Query Builder לא מזהה שאילתות מורכבות
  - חלק מהשאילתות לא עובדות (סטטיסטיקה, חיפוש לפי ראש ממשלה)
- 📝 **קבצים שהשתנו**: queryTemplates.ts, formatter.ts, .env.prod

### 22 ביוני 2025 - גרסה 2.2.0 🚀 **מערכת SQL Query Engine חדשה**
- 🆕 **פיתוח מערכת Text-to-SQL מלאה**:
  - תרגום שאילתות טבעיות ל-SQL
  - ביצוע ישיר ב-Supabase ללא טעינת נתונים לזיכרון
  - תמיכה ב-A/B testing בין PandasAI ל-SQL Engine
  - Query templates לשאילתות נפוצות
  - Response formatting בעברית
- 📝 **קבצים חדשים**:
  - `server/src/services/sqlQueryEngine/` - כל המערכת החדשה
  - `SQL_ENGINE_GUIDE.md` - מדריך שימוש מלא
  - `test-sql-engine.sh` - סקריפט בדיקות
- ⚠️ **סטטוס**: המערכת מוכנה אך לא מופעלת (USE_SQL_ENGINE=false)
- 🔧 **הפעלה**: יש ליצור RPC function ב-Supabase ולהגדיר USE_SQL_ENGINE=true

### 22 ביוני 2025 - גרסה 2.1.1 🐛 **תיקון בעיית filters בשאילתות סטטיסטיות**
- 🐛 **אבחון הבעיה**:
  - שגיאה: "cannot access local variable 'filters' where it is not associated with a value"
  - הבעיה: המשתנה filters הוגדר רק בתוך בלוק else, אבל נעשה בו שימוש מחוץ לבלוק
- ✅ **הפתרון**:
  - העברת `filters = self.extract_filters(query)` לתחילת הפונקציה
  - עכשיו filters זמין בכל מקום בפונקציה
- 📝 **קבצים שהשתנו**: query_optimizer.py
- ⚠️ **בעיות שנותרו**:
  - תשובות סטטיסטיות מבוססות על מדגם (1000 מתוך 24,716)
  - עדיין יש בעיות concat בחיפושים מסוימים

### 22 ביוני 2025 - גרסה 2.1.0 🔍 **פתרון בעיית החלטות ספציפיות**
- 🔍 **אבחון הבעיה**:
  - PandasAI לא מוצא החלטה 660 של ממשלה 35 למרות שהיא קיימת
  - הקוד הנוצר: `df['decision_number'] == 660` (מספר) במקום `== '660'` (מחרוזת)
  - PandasAI לא עוקב אחרי ההוראות המפורשות ב-CUSTOM_INSTRUCTIONS
- 🛠️ **ניסיונות פתרון**:
  - עדכון הוראות מפורשות לשימוש ב-decision_key
  - הוספת דוגמאות ספציפיות
  - שינוי temperature
  - ניסיון עם GPT-4 (עבד אבל יקר)
- ✅ **הפתרון הסופי**:
  - Bypass ל-PandasAI עבור החלטות ספציפיות
  - טיפול ישיר בקוד Python ללא PandasAI
  - שימוש ב-decision_key (למשל: '35_660')
  - החזרת הודעות שגיאה מפורטות כשלא נמצא
- 📝 **קבצים שהשתנו**: pandasai_service.py
- ⚠️ **לקח חשוב**: לפעמים פתרון ישיר עדיף על AI מורכב

### 22 ביוני 2025 - גרסה 2.0.9 🎉 **התקדמות משמעותית ב-PandasAI**
- ✅ **תיקון בעיות TypeScript**:
  - הסרת import לא בשימוש ב-chat.ts
  - שימוש ב-underscore למשתנהים לא בשימוש
- ✅ **שיפורים ב-PandasAI**:
  - הוספת הוראות מפורשות נגד pd.concat על dfs
  - הורדת temperature ל-0.1 לקבלת תוצאות עקביות
  - הוספת דוגמאות ספציפיות לחיפוש תחבורה
- ✅ **תוצאות**:
  - חיפוש לפי נושא עובד!
  - חיפוש לפי ממשלה ונושא עובד!
  - חיפוש החלטה ספציפית עובד!
- ⚠️ **עדיין בעיות**:
  - שגיאות כתיב מרובות
  - שאילתות סטטיסטיות
- 📝 **קבצים שהשתנו**: chat.ts, intentDetectionService.ts, pandasai_service.py

### 22 ביוני 2025 - גרסה 2.0.8 🤖 **Assistant כ-Smart Router עם LLM**
- ✅ **החלפת לוגיקת מילות מפתח ב-LLM**:
  - GPT-3.5 מנתח כל הודעה ומחליט לאן לנתב
  - זיהוי Intent: DATA_QUERY, GENERAL_QUESTION, UNCLEAR
  - תיקון אוטומטי של שגיאות כתיב בשקט
  - תשובות חכמות לשאלות על המערכת
- ✅ **שיפורי Query Optimizer**:
  - תמיכה ב"מהממשלה האחרונה/הנוכחית"
  - זיהוי משופר של נושאים עם ממשלה
  - תיקון TypeError בהמרת government_number
- 📝 **קבצים חדשים**: intentDetectionService.ts
- 📝 **קבצים שהשתנו**: chat.ts, query_optimizer.py, pandasai_service.py

### 21 ביוני 2025 - גרסה 2.0.7 🎯 **חיפוש החלטות לפי ממשלה**
- ✅ **תמיכה במספרי החלטה פר ממשלה**:
  - מספרי החלטות מתאפסים בכל ממשלה חדשה
  - חיפוש החלטה לפי מספר כולל תמיד סינון לפי ממשלה
  - ברירת מחדל: ממשלה נוכחית (37) אם לא צוין אחרת
  - הודעות שגיאה משופרות עם אינדיקציה לממשלות אחרות
- 📝 **קבצים שהשתנו**: pandasai_service.py, pandasAIService.ts

### 21 ביוני 2025 - גרסה 2.0.6 ✅ **שיפור חוויית משתמש**
- ✅ **הוספת תמיכה בשיחה כללית**:
  - הוספת לוגיקה ב-chat controller להבחין בין שאלות נתונים לשיחה כללית
  - שילוב GPT Assistant לתשובות אנושיות יותר
  - Fallback לתשובות פשוטות במקרה של כשל
- ✅ **השבתת Response Validator זמנית**:
  - Validator אגרסיבי מדי וחוסם תוצאות לגיטימיות
  - הושבת זמנית עד לשיפור האלגוריתם
- ✅ **שיפור חיפוש החלטות לפי מספר**:
  - תמיכה בחיפוש גם כמחרוזת וגם כמספר
  - חיפוש תמיד במסד המלא עבור החלטה ספציפית
  - דילוג על הגבלות גודל למספר החלטה ספציפי

### 21 ביוני 2025 - גרסה 2.0.5 ✅ **תיקונים ואימותים**
- ✅ **תיקון בעיית Docker Build Cache**:
  - פתרון בעיית credentials: `docker pull` ידני של ה-base images
  - בנייה מחדש עם `docker compose build --no-cache frontend`
  - וידוא שאין יותר אזכורים של `localhost:5173` ב-build
  - המערכת עובדת מצוין עם API calls ל-`/api`
- ✅ **אימות Backend Health Check**:
  - אובחן כ-false positive - השירות עובד מצוין
  - כל השירותים healthy כולל backend
  - אין צורך בתיקון

### 19 ביוני 2025 - גרסה 2.0.3 (נוכחית) ✅ **רוב הבעיות תוקנו!**
- ✅ **תיקון Context Length Error**:
  - הקטנת מגבלות ב-query_optimizer.py:
    - Statistical queries: 5000 → 1000 rows
    - Filtered results: 1000 → 100 rows  
    - No filters: 500 → 50 rows
    - הסרת עמודות מיותרות בדאטה גדול
  - המערכת עכשיו מטפלת בשגיאות context length בצורה חכמה
  
- ✅ **תיקון API Routing**:
  - nginx.conf: שינוי מ-`proxy_pass http://backend/` ל-`proxy_pass http://backend/api/`
  - הוספת health check ל-backend container
  - כל ה-API endpoints עובדים דרך nginx

- ✅ **שיפורי ביצועים**:
  - אופטימיזציה אגרסיבית של נתונים לפני שליחה ל-GPT
  - הגבלת עמודות בהתאם לגודל התוצאה
  - decision_content רק עבור 5 תוצאות או פחות

- ⚠️ **בעיות שנותרו**:
  - Response Validator חוסם יותר מדי - מומלץ להשבית
  - Backend health check מחזיר unhealthy (אבל השירות עובד)
  - צריך להגדיר production SSL certificates

### ינואר 2025 - גרסה 2.0.1
- ✅ **Validation System** - התחלת פיתוח
  - תכנון ResponseValidator
  - הוספת endpoints לבדיקה
  - debug tools

### 20 ביוני 2025 - גרסה 2.0.4 🔧 **בתהליך תיקון**
- 🔧 **תיקון בעיית Frontend Build**:
  - תוקן fallback ב-chat.service.ts ו-evaluation.service.ts מ-`localhost:5173` ל-`/api`
  - הוספת VITE_BASE_PATH support ב-vite.config.ts
  - עדכון React Router עם basename דינמי
  - יצירת docker-compose.prod.yml לפריסה ב-DO
  - בעיה: Docker build cache עדיין משתמש בקוד ישן
- 🐛 **בעיות Docker Build**:
  - שגיאת credentials בזמן pull של images
  - פתרון: `docker login` או `docker pull` ידני
- 📝 **קבצים חדשים שנוצרו**:
  - docker-compose.prod.yml - override לפריסה
  - .env.prod.do - משתני סביבה ל-DigitalOcean
  - DEPLOYMENT.md - הוראות פריסה מפורטות
  - run-local.sh - סקריפט הרצה לוקלית
  - build-production.sh - סקריפט בנייה ל-production

## 📄 רישיון
MIT License - ראה קובץ LICENSE

---

**נבנה עם ❤️ על ידי צוות CECI-AI**

_עודכן לאחרונה: 24 ביוני 2025 - גרסה 2.3.6_

---

## 📝 הערות חשובות למפתח/AI הבא

1. **המערכת עובדת!** - אל תיבהל מה-unhealthy status של backend, זה false positive
2. **Context Length** - אם חוזרת הבעיה, הקטן עוד את המגבלות ב-query_optimizer.py
3. **Response Validator** - כרגע מושבת, צריך לשכתב את הלוגיקה שלו
4. **SSL Certificates** - חובה להגדיר לפני production deployment
5. **Performance** - המערכת מוגבלת ל-50-100 רשומות per query, זה by design
6. **Supabase** - וודא שיש מספיק קריאות API נותרות
7. **OpenAI** - וודא שיש קרדיט מספיק ושה-API key תקף
8. **decision_number** - זה STRING במסד הנתונים, לא מספר!
9. **PandasAI עדיין משתמש ב-dfs[0]** - למרות ההוראות, צריך להיות יותר אגרסיביים

### 🔧 בעיות UX שדורשות תיקון דחוף:
1. **שגיאות כתיב** - "הבא ליי" צריך להיות מזוהה כ-"הבא לי"
2. **פוקוס בשדה קלט** - אחרי לחיצת Enter, הפוקוס נעלם וצריך ללחוץ שוב
3. **זיהוי הקשר** - "תוכן ההחלטה" לא מזהה את ההחלטה האחרונה שהוצגה
4. **חיפוש לפי מספר** - החלטה 660 לא נמצאת למרות שקיימת

**בהצלחה! 🚀**

---

## 🔴 בעיית 404 על Assets בפריסה

**בעיה זו תוקנה בגרסה 2.0.4** - ראה DEPLOYMENT.md לפרטים מלאים על הפתרון.

**בקצרה**: הבעיה נגרמה מכך ש-Vite נבנה עם `base: '/'` במקום עם sub-path. הפתרון כולל:
- הוספת VITE_BASE_PATH support
- עדכון React Router עם basename
- תיקון API URLs לשימוש בנתיבים יחסיים
