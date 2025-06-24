# 🚀 SQL Query Engine - Setup and Usage Guide

## 📋 סקירה
SQL Query Engine הוא מערכת Text-to-SQL שמחליפה את PandasAI. במקום לטעון את כל הנתונים לזיכרון (24,716 רשומות), המערכת מתרגמת שאילתות בשפה טבעית ל-SQL ומריצה אותן ישירות ב-Supabase.

## 🏗️ ארכיטקטורה
```
User Query → Intent Detection → SQL Query Engine → Supabase → Formatted Response
                                    ↓
                            [NL-to-SQL Converter]
                                    ↓
                            [Query Executor]
                                    ↓
                            [Response Formatter]
```

## 📦 קבצים חדשים שנוצרו
```
server/src/services/sqlQueryEngine/
├── index.ts              # Main service
├── schema.ts             # Database schema definition
├── queryTemplates.ts     # Common query patterns
├── nlToSql.ts           # Natural language to SQL converter
├── executor.ts          # Query executor
├── formatter.ts         # Response formatter
├── types.ts            # TypeScript types
└── (test files TBD)

server/src/services/
└── sqlQueryEngineService.ts  # Wrapper for compatibility

supabase/migrations/
└── 20250622_create_execute_sql_function.sql  # RPC function
```

## 🔧 התקנה והגדרה

### 1. יצירת RPC Function ב-Supabase
הרץ את הקוד הבא ב-SQL Editor של Supabase:

```sql
-- Copy content from: supabase/migrations/20250622_create_execute_sql_function.sql
```

### 2. עדכון Environment Variables
הוסף ל-.env.prod:
```env
# SQL Query Engine Configuration
USE_SQL_ENGINE=true          # Enable SQL engine
SQL_ENGINE_PERCENTAGE=0      # A/B testing percentage (0-100)
USE_SUPABASE_RPC=true       # Use RPC function (recommended)
```

### 3. הרצת המערכת
```bash
# Build and run with Docker
docker compose up -d --build

# Or run locally
npm run dev
```

## 🧪 בדיקות

### בדיקה מהירה דרך API
```bash
# Make executable
chmod +x test-sql-engine.sh

# Run tests
./test-sql-engine.sh
```

### בדיקה ידנית
```bash
# Test specific query
curl -X POST http://localhost:5173/api/chat/test-sql \
  -H "Content-Type: application/json" \
  -d '{"query": "החלטה 660 של ממשלה 35"}'

# Check health
curl http://localhost:5173/api/chat/health
```

## 📊 דוגמאות לשאילתות

### שאילתות פשוטות (Template-based)
- "החלטה 660 של ממשלה 35"
- "כמה החלטות יש משנת 2023?"
- "הבא לי החלטה בנושא תחבורה"
- "סטטיסטיקה של ממשלה 37"

### שאילתות מורכבות (GPT-powered)
- "כל ההחלטות בנושא חינוך מהשנה האחרונה"
- "השווה את מספר ההחלטות בין ממשלה 36 ל-37"
- "מה ההחלטות החשובות ביותר בנושא כלכלה?"

## 🔄 מעבר מ-PandasAI

### שלב 1: A/B Testing (מומלץ)
```env
USE_SQL_ENGINE=false         # Keep PandasAI as default
SQL_ENGINE_PERCENTAGE=10     # Test on 10% of users
```

### שלב 2: Gradual Rollout
```env
SQL_ENGINE_PERCENTAGE=25     # 25%
SQL_ENGINE_PERCENTAGE=50     # 50%
SQL_ENGINE_PERCENTAGE=75     # 75%
```

### שלב 3: Full Migration
```env
USE_SQL_ENGINE=true          # SQL Engine for all
SQL_ENGINE_PERCENTAGE=0      # Ignored when USE_SQL_ENGINE=true
```

## 🚨 טיפול בבעיות

### SQL Engine לא זמין
1. בדוק שה-Supabase credentials נכונים
2. בדוק שה-RPC function נוצרה
3. בדוק לוגים: `docker compose logs backend`

### שגיאות בתרגום לSQL
1. GPT API key תקף?
2. נסה להוריד temperature ב-nlToSql.ts

### ביצועים איטיים
1. הוסף indexes ב-Supabase:
```sql
CREATE INDEX idx_decision_date ON israeli_government_decisions(decision_date);
CREATE INDEX idx_government_number ON israeli_government_decisions(government_number);
CREATE INDEX idx_year ON israeli_government_decisions(year);
```

## 📈 יתרונות על PandasAI

| תכונה | PandasAI | SQL Engine |
|--------|----------|------------|
| זיכרון | 24,716 רשומות בזיכרון | 0 - queries בלבד |
| מהירות | איטי בהתחלה | מהיר תמיד |
| דיוק | תלוי ב-GPT code generation | SQL מדויק |
| סקיילביליות | מוגבל לגודל DataFrame | ללא הגבלה |
| עלות | יקר (הרבה tokens) | זול (פחות tokens) |

## 🔮 פיתוחים עתידיים

1. **Query Caching** - Redis cache לתוצאות
2. **Query Analytics** - מעקב אחר שאילתות פופולריות
3. **Smart Suggestions** - הצעות אוטומטיות
4. **Multi-table Queries** - שאילתות מורכבות
5. **Export to Excel/CSV** - יצוא תוצאות

## 📝 הערות חשובות

1. **Security**: כל ה-queries עוברות validation
2. **Limits**: מוגבל ל-SELECT queries בלבד
3. **Performance**: השתמש ב-indexes לשיפור ביצועים
4. **Monitoring**: בדוק לוגים באופן קבוע

## 🤝 צוות פיתוח
פותח כחלק מפרויקט CECI-AI להחלפת PandasAI במערכת יעילה יותר.

---
עדכון אחרון: 22 ביוני 2025
