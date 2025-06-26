# CECI‑AI – Short Operational Summary *(updated 25‑Jun‑2025)*

> **הערה על תווים מוזרים:** בסיכום הקודם הופיעו סימנים כגון `filecite…`. אלה היו סימוני‑ציטוט פנימיים של ChatGPT ואינם נחוצים במסמך Markdown. בגרסה הזו הם סולקו לחלוטין.

---

## 1. Production Deployment

* **Domain:** [https://ceci-ai.ceci.org.il](https://ceci-ai.ceci.org.il) → `178.62.39.248`
* **Infrastructure:** DigitalOcean Droplet (Ubuntu 24.04) + **Docker Compose** with five containers: `nginx`, `frontend`, `backend`, `sql-engine`, `redis`.
* **Critical ports:** 443/80 (public HTTPS/HTTP) · `8002` (internal SQL) · Dev ports `3000`, `5173`, `8080` *closed in prod*.
* **Security:** Nginx + Let's Encrypt (valid to 22‑Sep‑2025), HSTS, Content‑Security‑Policy, basic rate‑limiting. All containers isolated on an internal Docker network.

## 2. High‑Level Architecture

| Layer             | Main Components                               | Notes                                      |
| ----------------- | --------------------------------------------- | ------------------------------------------ |
| **Edge**          | Nginx reverse‑proxy                           | TLS termination, static assets, rate‑limit |
| **App**           | Node.js backend                               | REST + GraphQL                             |
| **SQL Engine**    | PostgreSQL 16                                 | *SQL‑only* – no PandasAI                   |
| **Cache**         | Redis 7                                       | Intents & query results                    |
| **Frontend**      | React (Vite)                                  | Served via Nginx                           |
| **Observability** | Custom logging (`execution_time`, `query_id`) | Exported to Grafana/Prometheus *(planned)* |

## 3. CI / Test Status

* **Current pass rate:** **13 / 15** tests (שיפור מ-10/15!).
* **Fixed issues:** ✅
  1. *Date Normalizer* — תוקן! עכשיו מזהה DD/MM/YYYY, DD.MM.YYYY, DD-MM-YYYY
  2. *Government Filter* — תוקן! אין יותר ברירת מחדל של ממשלה 37
  3. *Parameter Extraction* — תוקן! 11/11 בדיקות עוברות 💯

* **Still failing:**
  1. *Confidence Gate* — threshold too high → some unclear queries reach SQL.
  2. *Limit Extraction* — regex misses phrases like "הבא N החלטות".
* **Test tiers:** `summary` → `quick` → `comprehensive`.

## 4. Open Tasks (Priority Order)

1. **Enhance Question Handling** – expand the bot's ability to understand & correctly answer diverse natural‑language question types (improve slot‑filling, templates & fall‑backs).
2. **Fix Mixed Content** – convert all remaining HTTP calls to HTTPS.
3. **Automate SSL Renewal** – cron job: `0 12 * * * /root/ceci-ai/certbot/renew.sh`.
4. **Embed in WordPress** – iframe at `/ceci-ai/` page.
5. **CI/CD Pipeline** – GitHub Actions, branch `deploy_droplet`, auto‑deploy to Droplet.
6. **Monitoring + Backups** – Grafana/Prometheus; daily full‑dump to S3.

## 5. GitHub Workflow

* **Repository:** `github.com/TomerGutman1/ceci-ai` (public) – main development repo.
* **Deployment branch:** `deploy_droplet` — automatically built & deployed to production via GitHub Actions.
* **Clone tip:** use `git clone -b deploy_droplet --single-branch git@github.com:TomerGutman1/ceci-ai.git` if you don't have admin rights.
* **Feature branches:** `feat/<topic>` — branch off `deploy_droplet`, open PR → `deploy_droplet`.
* **Hotfixes:** commit directly to `hotfix/<issue>` then PR → `deploy_droplet`.

```bash
# clone (directly into deploy_droplet)
git clone -b deploy_droplet --single-branch git@github.com:TomerGutman1/ceci-ai.git
cd ceci-ai

# start a feature
git checkout -b feat/some-improvement

# push
git push -u origin feat/some-improvement

# deploy (maintainers only)
git checkout deploy_droplet
# deploy commits directly from deploy_droplet (fast‑forward)
git pull --ff-only origin deploy_droplet
git push origin deploy_droplet   # triggers CI/CD
```

## 6. Notable Changes in 2.4.x

| Version            | Highlight                                                              |
| ------------------ | ---------------------------------------------------------------------- |
| **2.4.0**          | Full switch to HTTPS & dedicated SQL‑engine                            |
| **2.4.3 – 2.4.6**  | Improved Fuzzy Matcher, new Date Normalizer, Confidence Gate           |
| **2.4.7 – 2.4.10** | Fixed COUNT\_BY\_GOVERNMENT, added metrics logging, expanded templates |

## 7. Architecture & Code Flow

**Main Components:**
| Component | Path | Purpose | Talks to |
|-----------|------|---------|----------|
| Frontend | `/src/App.tsx` | React UI | → nginx → backend |
| Backend | `/server/src/main.ts` | Express API | → sql-engine, OpenAI |
| SQL Engine | `/sql-engine/src/index.ts` | NL→SQL | → PostgreSQL |
| Templates | `/sql-engine/src/services/queryTemplates.ts` | 40+ SQL patterns | Used by nlToSql |

**Query Processing Flow:**
1. User input → Frontend (`/src/components/ChatInterface.tsx`)
2. nginx:443 → Backend (`/server/src/routes/chat.routes.ts`)
3. Backend analyzes query type:
   - SQL queries → sql-engine:8002 (`/sql-engine/src/services/nlToSql.ts`)
   - General chat → OpenAI API
4. SQL Engine: Template matching → SQL execution → Format response
5. Response flows back through the chain

**Key Files:**
- Natural Language → SQL: `/sql-engine/src/services/nlToSql.ts`
- Query Templates: `/sql-engine/src/services/queryTemplates.ts`
- Response Formatting: `/sql-engine/src/services/formatter.ts`
- Fuzzy Topic Matching: `/sql-engine/src/utils/fuzzyMatcher.ts`

**CI/CD:** Push to `deploy_droplet` branch → GitHub Actions → Docker Hub → DigitalOcean

📄 **Full architecture details:** See `C:\Users\tomer\Downloads\INTEGRATION\FRONTEND_NEW\ceci-ai-testing-main\ARCHITECTURE.md`

## 8. Quick Maintenance Sheet

```bash
# connect
ssh root@178.62.39.248
cd /root/ceci-ai

# check container status
docker compose ps

# live logs
docker compose logs -f nginx

# update code & rebuild
git pull origin deploy_droplet
docker compose  build sql-engine
docker compose up -d --build

# manual SSL renewal if cron fails
docker compose run --rm certbot renew
```

---

## 9. Current Debug Status (25 ביוני 2025 - עדכון בשעה 23:00)

### שיפורים שהושלמו היום:
1. **Enhanced System Prompt** - הוספת Natural Language Parameter Map מלא ל-GPT prompt
   - כולל כל 8 הקטגוריות של פרמטרים (זמן, נושא, ממשלה, גיאוגרפיה, כמות, תוכן, הצגה, הקשר)
   - extracted_params מורחב עם 20+ שדות
   - דוגמאות מפורטות לכל סוג פרמטר

2. **✅ Date Normalizer - תוקן לחלוטין!** 
   - מעבר ל-GPT-based parameter extraction במקום regex
   - GPT מחלץ ומנרמל תאריכים בכל הפורמטים:
     * DD/MM/YYYY → YYYY-MM-DD ✅
     * DD.MM.YYYY → YYYY-MM-DD ✅
     * DD-MM-YYYY → YYYY-MM-DD ✅
   - זיהוי חכם של הקשר: "מאז", "החל מ-", "מ-"
   - תמיכה בשנה בלבד: "2023" → "2023-01-01"
   - שילוב מושלם עם נושאים

3. **TypeScript Fix** - תיקון שגיאת `originalIntent` ב-IntentResult interface

4. **Confidence Gate Handling** - טיפול משופר בשאילתות לא ברורות
   - החזרת תשובות ברורות יותר עבור UNCLEAR_QUERY ו-LOW_CONFIDENCE

5. **Government Filter Fix** ✅ - תיקון מושלם!
   - הסרת ברירת מחדל של ממשלה 37
   - הוספת טמפלייטים: DECISIONS_BY_GOVERNMENT, DECISIONS_BY_TOPIC_AND_GOVERNMENT
   - עובד מצוין עם פרמטרים

6. **Metadata Enhancement** - הוספת params ו-template_used ל-response metadata

### סטטוס בדיקות נוכחי:
- ✅ **Date Normalizer Tests** - 100% עוברים!
- ✅ **Government Filter Tests** - עובד מצוין
- ❌ **Template Matching** - עדיין יש בעיות עם טמפלייטים מורכבים
- ❌ **Confidence Gate** - עדיין צריך כיול
- ❌ **Limit Extraction** - regex לא תופס "הבא N החלטות"

### בעיות פתוחות:
1. **Template matching conflicts** - צריך לנקות טמפלייטים ישנים שמסתמכים על regex
2. **Unclear Query Handling** - עדיין מגיעות ל-SQL במקום הודעת הנחיה
3. **Mixed Content Warning** - עדיין יש קריאות HTTP במקום HTTPS

## 10. Database Schema (`government_decisions`)

```sql
id bigint,
decision_date date,
decision_number text,
committee text,
decision_title text,
decision_content text,
decision_url text,
summary text,
operativity text,
tags_policy_area text,
tags_government_body text,
tags_location text,
all_tags text,
government_number integer,
prime_minister text,
decision_key text,
created_at timestamptz,
updated_at timestamptz
```

---

## 11. Natural‑Language Parameter Map

להלן "מפת‑הפרמטרים" המלאה — כל ה‑*signals* שה‑GPT צריך (או עשוי) לחלץ ממשפט טבעי של משתמש כדי להרכיב שאילתת SQL או לוגיקה נכונה.

| קטגוריה             | פרמטר לוגי             | דוגמאות ניסוח משתמש                    | הערות / שיקולי GPT                  |
| ------------------- | ---------------------- | -------------------------------------- | ----------------------------------- |
| **זמן**             | `date_from`            | "החל מ‑ינואר 2022", "אחרי 1.3.2020"    | ≥ תאריך                             |
|                     | `date_to`              | "עד סוף 2023", "לפני מאי 2019"         | ≤ תאריך                             |
|                     | `date_range`           | "בין 2020 ל‑2022", "בשנים 2010‑2015"   | שני גבולות                          |
|                     | `year_exact`           | "בשנת 2021", "ב‑2023"                  | מומר לטווח שנה מלא                  |
|                     | `relative_period`      | "בחצי השנה האחרונה", "בעשור הקודם"     | חישוב דינמי                         |
| **גאוגרפיה / משרד** | `tags_location`        | "בגליל", "בתל אביב", "באשכול נגב"      | match בטבלת `tags_location`         |
|                     | `tags_government_body` | "משרד החינוך", "משרד התחבורה"          |                                     |
| **נושא / תגית**     | `tags_policy_area`     | "ביטחון לאומי", "אנרגיה", "יוקר המחיה" | התאמה לרשימת 36 תגיות, fallback FTS |
|                     | `topic_free`           | "רובוטיקה בחינוך", "סייבר אזרחי"       | full‑text search                    |
| **גוף מקבל**        | `committee`            | "קבינט ביטחוני", "ועדת שרים"           | התאמה בשדה `committee`              |
| **זהות פוליטית**    | `government_number`    | "ממשלה 36"                             | int                                 |
|                     | `prime_minister`       | "נפתלי בנט", "בנימין נתניהו"           | כולל מיפוי כינוי ("ביבי")           |
| **כמות / אגרגציה**  | `count_only`           | "כמה החלטות…"                          | `SELECT COUNT(*)`                   |
|                     | `limit`                | "הצג חמש החלטות…"                      | ברירת‑מחדל 10                       |
|                     | `aggregation_type`     | "ממוצע תקציב", "סה"כ החלטות"           | להמשך                               |
| **סינון תוכן**      | `full_text_query`      | "שמכילות את 'תקציב'"                   | `ILIKE`                             |
|                     | `operativity_filter`   | "אופרטיביות בלבד"                      | ערכים ב‑`operativity`               |
| **סוג הצגה**        | `expected_type`        | "רק קישורים", "טבלה מלאה"              | אילו עמודות להחזיר                  |
|                     | `order_by`             | "הכי חדשות קודם", "לפי מספר"           | דיפולט `decision_date DESC`         |
| **שיטת שאילתה**     | `clarification_needed` | שאלה קצרה מדי                          | מציף בקשת הבהרה                     |
| **טופס שפה**        | `spelling_correction`  | "החלתה" → "החלטה"                      | pre‑normalize                       |
| **קונטקסט**         | `follow_up_ref`        | "כמה היו כאלה?"                        | זקוק לשאלה קודמת                    |

### Usage Workflow

1. **Normalizer** – זיהוי תאריכים, מיפוי כינויים, תיקון כתיב.
2. **Intent ↦ Slot Filling** – מלא את השדות בטבלה לעיל; ריקים ⇒ ברירת מחדל או בקשת הבהרה.
3. **Template Match → GPT** – אם מולאו שדות מסוימים → השתמש בטמפלט ייעודי; אחרת GPT‑SQL.
4. **Prompt Enrichment** – ציין בבירור אילו שדות הנתיב צריך לאכלס.

---

**TL;DR**
Production is stable (5 containers, HTTPS). Key next steps: *Enhance Question Handling*, resolve Mixed Content, automate SSL, build CI/CD, and fix Date Normalizer & Confidence Gate.

---

## עדכון 26/06/2025 - Parameter Extraction Enhancement

### השיפור:
1. **שדרוג extractParametersWithGPT** - עבר ממבנה מקונן למבנה פשוט (flat JSON)
   - תיקון הבעיה שהפרמטרים הוחזרו במבנה מקונן מסובך
   - GPT מחזיר עכשיו פרמטרים ישירות: `{"date_from": "2023-03-15", "topic": "חינוך"}`
   - פרומפט פשוט וברור יותר עם דוגמאות

2. **תיקון הבדיקות** - עדכון test_parameter_extraction.sh לתמוך בשני הפורמטים
   - בדיקה ראשונה של מבנה פשוט
   - fallback למבנה מקונן אם נדרש

### הוראות הרצה:
```bash
# בדיקה מקיפה
cd /mnt/c/Users/tomer/Downloads/INTEGRATION/FRONTEND_NEW/ceci-ai-testing-main
./tests/test_parameter_extraction.sh

# בדיקה מהירה
./tests/test_param_extraction_quick.sh

# דיבאג
./tests/debug_param_extraction.sh
```

### הבעיה שנפתרה:
GPT החזיר פרמטרים במבנה מקונן (nested) שהבדיקות לא ידעו לקרוא. עכשיו הוא מחזיר flat JSON פשוט.

---

## עדכון 26/06/2025 בשעה 11:30 - Parameter Extraction Tests Fixed ✅

### מה הבעיה הייתה:
- הבדיקות הישנות חיפשו פרמטרים בשדות נפרדים במטאדאטה (כמו `metadata.date_from`)
- במציאות, הפרמטרים מוחזרים במערך `metadata.params`
- בנוסף, הבדיקות לא התחשבו בסדר הפרמטרים ב-SQL

### מה תוקן:
1. **בדיקות מעודכנות** - 3 קבצי בדיקה חדשים:
   - `test_param_extraction_v2.sh` - בדיקה של params array
   - `test_param_extraction_final.sh` - בדיקה מלאה עם תיקונים
   - `check_nltosql_response.sh` - בדיקת מבנה התגובה

2. **תוצאות נוכחיות: 11/11 בדיקות עוברות! ✅ 💯**
   - ✅ Date normalization (DD/MM/YYYY, DD.MM.YYYY)
   - ✅ Topic matching with fuzzy search
   - ✅ Government filtering
   - ✅ Count and limit queries
   - ✅ Full text search
   - ✅ Template matching

### כל הבדיקות עוברות בהצלחה!
- כל בדיקות התאריכים עוברות
- כל בדיקות הנושאים עוברות
- כל בדיקות הפרמטרים עוברות

### הרצת הבדיקות:
```bash
# בדיקה סופית מלאה
./tests/test_param_extraction_final.sh
```

---

## עדכון 26/06/2025 בשעה 12:00 - Improved Topic Search 🔍

### השיפור:
**שינוי גישה בחיפוש נושאים** - מעבר ממיפוי אוטומטי לתגיות רחבות לחיפוש ספציפי בתוכן

### הבעיה שנפתרה:
- חיפוש "החברה הערבית" החזיר את כל ההחלטות בנושא "מיעוטים" (157 תוצאות)
- זה יותר מדי רחב ולא רלוונטי למשתמש
- כולל גם החלטות על חרדים, אתיופים, עולים חדשים וכו'

### הפתרון:
1. **חיפוש בתוכן במקום בתגיות** - כשהנושא אינו תג רשמי מדויק
2. **חיפוש ב-3 שדות**:
   - decision_title (הכי ספציפי)
   - summary (סקירה טובה)
   - decision_content (מקיף אך פחות ממוקד)
3. **שמירה על תגיות רק למקרים מדויקים** - רק כשהמשתמש מבקש במפורש תג רשמי

### תוצאות החיפוש המשופר:
- "החברה הערבית" - 28 תוצאות ספציפיות ✅
- "ערבים" - 117 תוצאות רלוונטיות ✅
- "דרוזים" - 86 תוצאות ✅
- "בדואים" - 152 תוצאות ✅
- "מיעוטים" - 209 תוצאות (כולל כל המיעוטים) ✅

### הקוד שהשתנה:
- `nlToSql.ts` - שינוי בפונקציה `convertWithGPT` לטפל בנושאים בצורה ספציפית
- `nlToSql.ts` - עדכון `buildNormalizedQuery` לא לעשות מיפוי אוטומטי
- System prompt - הנחיות חדשות ל-GPT להעדיף חיפוש תוכן

### היתרון למשתמש:
מקבל תוצאות רלוונטיות ומדויקות הרבה יותר, במקום "להטביע" אותו במידע לא רלוונטי
