# 📑 PROJECT SUMMARY – CECI AI BOT CHAIN

> **Purpose (EN)** – Lightweight, always‑loaded overview for Claude: explains what the project does, where the critical instructions live, and how to read them *only when needed* to save tokens.
>
> **מטרה (עברית)** – תקציר קומפקטי ש‑Claude טוען בתחילת כל שיחה, עם מפות קבצים והנחיות קריאה ממוקדת לחיסכון בטוקנים.

---

## 1 · What the System Does ⏩

*Answer complex Hebrew queries about Israeli government decisions.*

1. **Frontend** sends `POST /api/process-query` with free‑text Hebrew.
2. **Backend** proxies the payload to a single **BOT CHAIN** container (port 8002).
3. **BOT CHAIN** runs **7 GPT bots** in sequence:
   `0_REWRITE → 1_INTENT → 2X_ROUTER → 2C_CLARIFY? → 2Q_SQL → 2E_EVAL → 3Q_RANK`.
4. A **Formatter code module** (non‑GPT) formats the ranked rows into Markdown / JSON and returns the answer.
5. Data source is **Supabase PostgreSQL** (`israeli_government_decisions_*` tables).

👉 *No SQL engine any more – BOT CHAIN replaced it transparently.*

---

## 2 · Directory Landmarks 📂

| Path                                        | What lives here                                        | When to read                                                                                        |
| ------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| `bot_chain/ARCHITECTURE.md`                 | Full system architecture (mermaid, ports, flows)       | **Overview only** – skim for context.                                                               |
| `bot_chain/LAYERS_SPECS/`                   | **7 individual bot specs** (prompt, examples, weights) | **Load *only* the spec of the layer in focus**.<br>e.g. handling rewrite → read `0_REWRITE_BOT.md`. |
| `bot_chain/MICRO_LEVEL_GUIDE.md`                      | Cross‑layer principles (naming, scoring, security)     | Reference for *any* layer deep dive.                                                                |
| `bot_chain/LAYERS_SPECS/SQL_DB_SPEC.md`                            | Whitelisted tables/columns & RLS notes                 | Read when crafting / debugging SQL.                                                                 |
| `bot_chain/LAYERS_SPECS/end2End_scenarios.md`                      | Sample user journeys & expected outputs                | Use for regression tests.                                                                           |
| `bot_chain/LAYERS_SPECS/israeli_government_decisions_DB_SCHEME.md` | PostgreSQL schema diagram                              | Needed only for new SQL joins.                                                                      |

> 🔖 **Rule of Thumb** – *If you are interacting with or modifying a single bot layer, read:*<br>  1. That layer's spec (one file).<br>  2. The `MICRO_LEVEL_GUIDE` for common rules.<br>  3. Skip everything else unless explicitly required.

---

## 3 · Token‑Saving Guidelines 🪙

1. **Minimal Context Loading** – Never ingest the entire repo. Pick the smallest relevant doc(s).
2. **Layer Isolation** – Each bot spec is self‑contained; do not preload specs for other layers.
3. **Debug Info** – Use `debug_info.token_usage` returned from BOT CHAIN to monitor consumption.
4. **Formatter** uses **no GPT tokens** – keep heavy post‑processing logic in code.

---

## 4 · Quick Reference ✏️

| Need                    | Open this                                            |
| ----------------------- | ---------------------------------------------------- |
| Understand overall flow | `ARCHITECTURE_BOT_CHAIN.md` (Section 2 Runtime Flow) |
| Check REST contract     | `ARCHITECTURE_BOT_CHAIN.md` (Section 4)              |
| Tune a prompt           | `bot_chain/LAYERS_SPECS/<layer>.md`                  |
| Validate DB columns     | `SQL_DB_SPEC.md` + `*_DB_SCHEME.md`                  |
| Estimate cost           | Token budget table (Architecture §8)                 |

---

## 5 · Contact

*Maintainer*: **Tomer** – [tomer@example.com](mailto:tomer@example.com)

---

*Loaded at conversation start – keep it short & actionable.*

---

## 🔌 פורטים מעודכנים של השירותים (30 ביוני 2025)

### Backend Service
- **Backend**: פורט 5001 (היה 5000) - מחובר ל-5173 בתוך הקונטיינר
  - פורט נוסף: 5174 גם מחובר ל-5173

### Bot Chain Services (כולם פועלים ב-healthy)
- **Rewrite Bot**: פורט 8010
- **Intent Bot**: פורט 8011
- **SQL Gen Bot**: פורט 8012
- **Context Router Bot**: פורט 8013
- **Evaluator Bot**: פורט 8014
- **Clarify Bot**: פורט 8015
- **Ranker Bot**: פורט 8016
- **Formatter Bot**: פורט 8017

### Other Services
- **Frontend**: פורט 3001
- **Nginx**: פורטים 80, 443, 8080
- **PostgreSQL**: פורט 5433 (מחובר ל-5432 בקונטיינר)
- **Redis**: פורט 6380 (מחובר ל-6379 בקונטיינר)

### API Endpoints
- **Health Check**: `http://localhost:5001/api/chat/health`
- **Chat API**: `http://localhost:5001/api/chat`
- **Test Bot Chain**: `http://localhost:5001/api/chat/test-bot-chain`

---

## 🚨 בעיות קריטיות שזוהו (30 ביוני 2025) 

### 1. **בעיית זרימה - Evaluator Bot נקרא בכל שאילתא**
**הבעיה**: ה-Evaluator Bot (2E) אמור להיקרא רק במסלול EVAL לניתוח מעמיק של החלטה ספציפית.
**מה קורה בפועל**: הוא נקרא בכל שאילתת QUERY רגילה, מה שגורם ל:
- צריכת טוקנים מיותרת (GPT-4-turbo יקר)
- האטה משמעותית בתגובות
- חריגה מתקציב ה-API

**הפתרון**: הוסרה הקריאה ל-Evaluator ממסלול QUERY. הוא יישאר רק למסלול EVAL.

### 2. **Ranker Bot - מושבת זמנית**
**הבעיה**: ה-Ranker Bot (3Q) גורם לעיכובים ארוכים וצורך טוקנים רבים.
**הפתרון הזמני**: דילוג על שלב הדירוג (SKIP_RANKER = true בקוד).
**השפעה**: התוצאות מוחזרות בסדר ברירת המחדל (תאריך יורד).

### 3. **חריגה ממכסת OpenAI**
**הבעיה**: "You exceeded your current quota" - נגמר התקציב של ה-API Key.
**הסיבה**: שימוש לא יעיל בבוטים (בעיקר Evaluator שלא לצורך).
**השפעה**: רוב השאילתות נכשלות עם שגיאת 500.

### 4. **עלויות לא כצפוי**
**התכנון המקורי**: עד $0.05 לשאילתא
**מה קרה בפועל**: עלויות גבוהות בהרבה בגלל:
- קריאות מיותרות ל-Evaluator בכל שאילתא
- שימוש ב-GPT-4-turbo במקומות שלא נדרש
- חוסר אופטימיזציה בגודל הבקשות

---

## 7 · יכולות המערכת - סוגי שאלות נתמכות 🎯

### המערכת יודעת לטפל במגוון רחב של שאילתות:

#### 1. **חיפושים פשוטים**
- "החלטות בנושא חינוך" → מחזירה את כל ההחלטות בנושא חינוך
- "החלטות ממשלה 37" → מחזירה את כל החלטות ממשלה 37
- "3 החלטות אחרונות" → מחזירה בדיוק 3 החלטות אחרונות

#### 2. **חיפושים עם טווחי תאריכים**
- "החלטות מינואר 2024" → מחזירה החלטות מינואר 2024
- "החלטות בין 01/01/2024 ל-31/03/2024" → מחזירה החלטות בטווח המבוקש
- "החלטות מ-2024" → מחזירה את כל החלטות 2024

#### 3. **שאלות סטטיסטיות**
- "כמה החלטות יש בנושא בריאות?" → סופרת ומחזירה מספר
- "כמה החלטות קיבלה ממשלה 37?" → סופרת החלטות לפי ממשלה

#### 4. **טיפול בשגיאות כתיב**
- "החלטות בנושא חנוך" → מתקנת ל"חינוך" ומחזירה תוצאות
- "ממשלה שלושים ושבע" → מזהה כממשלה 37

#### 5. **הבנת כוונות מורכבות**
- "תן לי 5 החלטות בנושא בריאות" → מבינה שזה limit ולא ממשלה
- "37 החלטות של הממשלה" → מזהה ש-37 זה כמות, לא מספר ממשלה

#### 6. **חיפושים משולבים**
- "החלטות ממשלה 37 בנושא חינוך מ-2024" → משלבת ממשלה, נושא ותאריך
- "5 החלטות אחרונות בנושא תחבורה" → משלבת limit, נושא וסדר

### דוגמאות לתשובות:

**שאילתא:** "3 החלטות בנושא חינוך"  
**תשובה:** (2.2 שניות)
```
# תוצאות חיפוש: 3 החלטות בנושא חינוך

**נמצאו 3 תוצאות**

## 1. ישראל ריאלית: תוכנית רב-שנתית למתן מענה למצב החירום הלאומי במקצועות ה-STEM
**מידע כללי:** ממשלה 37 | החלטה 2983 | 27 באפריל 2025
**תחומים:** נושא: חינוך | משרד: משרד החינוך, משרד האוצר...

## 2. הצעת חוק זכויות הסטודנט (תיקון - מסלולי לימוד נפרדים)
**מידע כללי:** ממשלה 37 | החלטה 2948 | 3 באפריל 2025
**תחומים:** נושא: חינוך | משרד: ועדת החינוך...

## 3. [החלטה נוספת בנושא חינוך]
...
```

**שאילתא:** "החלטות בנושא בולים"  
**תשובה:** מוצאת החלטות על הנפקת בולים (לא מבלבלת עם "ביטחון")

**שאילתא:** "כמה החלטות קיבלה ממשלה 37?"  
**תשובה:** מזהה כוונה לספירה ומחזירה מספר כולל של החלטות

### יכולות מתקדמות בפיתוח:
- השוואות בין ממשלות
- הקשר ורצף שיחה
- שאלות הבהרה אינטליגנטיות
- אגרגציות מורכבות

### 29 בדצמבר 2024 - תיקון בעיות זיהוי ב-Intent Bot, שיפור חיפושים ואופטימיזציה של ביצועים

**🐛 בעיות שתוקנו:**
1. **זיהוי מספרים** - המערכת מזהה נכון ש"3 החלטות" = limit של 3 תוצאות (לא ממשלה 3)
   - עדכון: `bot_chain/MAIN_INTENT_BOT_1/prompts.py` - הוספת כללים לזיהוי מספרים לפני מילים כמו "החלטות"
   - הוספת שדה `limit` ל-IntentEntities

2. **חיפוש נושאים** - תוקן באג שהמיר "בולים" ל"ביטחון"
   - עדכון: `server/src/services/botChainService.ts` - שמירה על הנושא המקורי בחיפוש משני

3. **תמיכה ב-limit דינמי** - המערכת מכבדת את מספר התוצאות המבוקש
   - עדכון: הבקאנד קורא `entities.limit` במקום `entities.count_target`

**📁 קבצים שעודכנו:**
- `bot_chain/MAIN_INTENT_BOT_1/prompts.py`
- `bot_chain/MAIN_INTENT_BOT_1/main.py`


4. **אופטימיזציה של ביצועים** - הסרת evaluator ממסלול QUERY
   - עדכון: הסרת קריאה ל-evaluator bot ממסלול חיפוש רגיל (לפי MICRO_LEVEL_GUIDE)
   - שיפור: זמן תגובה ירד מ-8-17 שניות ל-**2.2 שניות** (שיפור של 75%!)
   - ה-evaluator נשאר רק למסלול EVAL (ניתוח מעמיק של החלטה ספציפית)

**📁 קבצים שעודכנו:**
- `bot_chain/MAIN_INTENT_BOT_1/prompts.py`
- `bot_chain/MAIN_INTENT_BOT_1/main.py`
- `server/src/services/botChainService.ts`

**✅ תוצאות בדיקות:**
- "3 החלטות בנושא חינוך" → מחזיר בדיוק 3 תוצאות (2.2 שניות)
- "החלטות בנושא בולים" → מוצא החלטות על בולים (לא ביטחון)
- "החלטות בנושא חינוך מינואר 2024" → מחזיר תוצאות מהתאריך הנכון
- "37 החלטות של הממשלה" → מזוהה נכון כ-limit=37 (לא כממשלה)
- כל 14 הבדיקות האוטומטיות עברו בהצלחה

---

**📊 מעקב בדיקות (30 ביוני 2025)**

**בדיקות שעברו בהצלחה ✅**
- test_runner.sh - Limit Recognition 1: "3 החלטות" מזוהה נכון כ-limit=3
  - Path: `/mnt/c/Users/tomer/Downloads/ceci-w-bots/tests/bot_chain_tests/test_runner.sh`

**בדיקות שנכשלו ❌**
- רוב הבדיקות נכשלות בגלל חריגה ממכסת OpenAI
- נדרש לחדש את ה-API Key או להמתין לאיפוס המכסה

**המלצות דחופות 🚨**
1. החלפת API Key או המתנה לאיפוס מכסה
2. אופטימיזציה נוספת:
   - להחליף GPT-4-turbo ל-GPT-3.5-turbo איפה שאפשר
   - להקטין את גודל הפרומפטים
   - להוסיף caching לתשובות חוזרות
3. ניטור עלויות: להוסיף מנגנון tracking לכל קריאת API
4. Rate limiting: להגביל מספר קריאות לדקה

---

## 📄 מסמכים חדשים

### 🚀 **OPTIMIZATION_PLAN.md** - תוכנית אופטימיזציה מפורטת
- **מיקום**: `/mnt/c/Users/tomer/Downloads/ceci-w-bots/OPTIMIZATION_PLAN.md`
- **תוכן**: תוכנית 4 שלבים להורדת עלויות ב-75% ושיפור ביצועים ב-60%
- **כולל**:
  - Quick Wins (שבוע 1)
  - Smart Routing (שבוע 2-3)
  - Advanced Optimization (שבוע 4-6)
  - Intelligence Preservation
  - ניתוח עלויות מפורט
