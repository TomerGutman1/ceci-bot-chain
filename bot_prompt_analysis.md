# Bot Chain Prompt Analysis Report

## Summary of Findings

I analyzed all the bot_chain main.py files and found several prompts that need token optimization. Here's a comprehensive breakdown:

## 1. CLARIFY_CLARIFY_BOT_2C/main.py

### Large Prompt Found (Lines 164-186):
```python
system_prompt = f"""אתה עוזר בעברית שמתמחה ביצירת שאלות הבהרה למערכת חיפוש החלטות ממשלה.

המטרה: לעזור למשתמשים לנסח שאילתות מדויקות יותר כשהשאילתא המקורית מעורפלת או חסרה מידע.

טיפוס הבהרה נדרש: {clarification_type.value}

הוראות:
1. צור 2-3 שאלות הבהרה קצרות ומדויקות
2. הצע 3-4 תשובות אפשריות לכל שאלה
3. התמקד במידע החסר החשוב ביותר לחיפוש
4. השתמש בעברית פשוטה וברורה
5. תן עדיפות לשאלות שיכולות לשפר את דיוק החיפוש

דוגמאות לסוגי שאלות:
- זמן: "איזה תקופה אתה מחפש?"
- נושא: "איזה תחום מעניין אותך?"
- ממשלה: "איזה ממשלה מתכוון?"
- משרד: "איזה משרד רלוונטי?"

החזר תשובה בפורמט JSON עם המפתחות:
- questions: רשימה של שאלות עם type, question, suggestions
- explanation: הסבר קצר למה צריך את ההבהרה
"""
```

**Current Token Count: ~370 tokens**
**Target: 150 tokens**

### Optimized Version:
```python
system_prompt = f"""עוזר עברית - שאלות הבהרה למערכת חיפוש החלטות ממשלה.

מטרה: שיפור שאילתות מעורפלות.
סוג: {clarification_type.value}

הוראות:
1. צור 2-3 שאלות הבהרה קצרות
2. הצע 3-4 תשובות לכל שאלה
3. התמקד במידע החסר החשוב
4. עברית פשוטה וברורה

דוגמאות:
- זמן: "איזה תקופה?"
- נושא: "איזה תחום?"
- ממשלה: "איזה ממשלה?"

JSON: {{"questions": [שאלות], "explanation": "הסבר"}}
"""
```

**Optimized Token Count: ~145 tokens**

## 2. MAIN_INTENT_BOT_1/prompts.py

### Multiple Large Prompts Found:

#### INTENT_SYSTEM_PROMPT (Lines 5-39):
**Current Token Count: ~340 tokens**
**Target: 150 tokens**

#### FEW_SHOT_PROMPT (Lines 243-333):
**Current Token Count: ~820 tokens**
**Target: 150 tokens**

### Optimized INTENT_SYSTEM_PROMPT:
```python
INTENT_SYSTEM_PROMPT = """Hebrew intent extraction for Israeli government decisions.

Return JSON:
{
    "intent": "search|count|specific_decision|comparison|clarification_needed",
    "confidence": 0.0-1.0,
    "entities": {
        "government_number": int|null,
        "decision_number": int|null,
        "topic": "string"|null,
        "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}|null,
        "ministries": ["array"]|null,
        "count_target": "decisions|meetings|topics|ministries"|null,
        "comparison_target": "string"|null,
        "limit": int|null
    },
    "route_flags": {
        "needs_clarification": bool,
        "has_context": bool,
        "is_follow_up": bool
    },
    "explanation": "Brief explanation"
}

Rules:
1. Hebrew numbers to digits (שלושים ושבע -> 37)
2. Numbers before "החלטות" = COUNT, not government_number
3. Government format: "ממשלה X"
4. Set confidence by query clarity
"""
```

**Optimized Token Count: ~148 tokens**

## 3. MAIN_REWRITE_BOT_0/main.py

### REWRITE_PROMPT (Lines 79-99):
**Current Token Count: ~180 tokens**
**Target: 150 tokens**

### Optimized Version:
```python
REWRITE_PROMPT = """Hebrew text improvement assistant.

Tasks:
1. Fix spelling/grammar
2. Normalize entities (ממשלה 37 not שלושים ושבע)
3. Remove unnecessary words
4. Keep concise and clear

Text: {text}

Return JSON:
- "clean_text": improved text
- "corrections": array with type/original/corrected

Rules: preserve meaning, keep Hebrew RTL, don't translate
"""
```

**Optimized Token Count: ~95 tokens**

## 4. QUERY_SQL_GEN_BOT_2Q/main.py

### SQL_GENERATION_PROMPT (Lines 84-115):
**Current Token Count: ~320 tokens**
**Target: 150 tokens**

### Optimized Version:
```python
SQL_GENERATION_PROMPT = """PostgreSQL query generator for Israeli government decisions.

Schema: government_decisions (id, government_number, decision_number, decision_date, title, content, summary, topics[], ministries[], status)

Intent: {intent}
Entities: {entities}

Requirements:
1. Parameterized queries: %(param)s
2. Always: AND status = 'active'
3. ORDER BY + LIMIT for search (default 20)
4. Array ops: 'value' = ANY(topics)
5. Full-text: to_tsvector('hebrew', content) @@ to_tsquery('hebrew', 'term')

Return JSON: {{"sql": "query", "parameters": {{}}, "explanation": "logic"}}
"""
```

**Optimized Token Count: ~138 tokens**

## 5. EVAL_EVALUATOR_BOT_2E/main.py

### Large Prompt (Lines 460-482):
**Current Token Count: ~280 tokens**
**Target: 150 tokens**

### Optimized Version:
```python
prompt = f"""העריך איכות תוצאות חיפוש החלטות ממשלה.

שאילתא: "{query}"
כוונה: {intent}
ישויות: {json.dumps(entities, ensure_ascii=False)}

תוצאות:
{results_text}

הערך 0-1:
1. רלוונטיות סמנטית
2. איכות תוכן
3. איכות שפה

JSON: {{"semantic_relevance": 0.85, "content_quality": 0.75, "language_quality": 0.90, "explanation": "הסבר"}}
"""
```

**Optimized Token Count: ~145 tokens**

## 6. QUERY_RANKER_BOT_3Q/main.py

### Large Prompt (Lines 247-261):
**Current Token Count: ~210 tokens**
**Target: 150 tokens**

### Optimized Version:
```python
system_prompt = f"""מומחה ניתוח רלוונטיות החלטות ממשלה.

החזר ציון 0.0-1.0 + הסבר עברית.
כוונה: {intent}

סקלה:
0.0-0.3: לא רלוונטי
0.4-0.6: חלקי
0.7-0.8: רלוונטי מאוד
0.9-1.0: מושלם

JSON: {{"score": 0.x, "explanation": "הסבר"}}
"""
```

**Optimized Token Count: ~85 tokens**

## Summary Table

| Bot | Original Tokens | Optimized Tokens | Reduction |
|-----|----------------|------------------|-----------|
| CLARIFY_CLARIFY_BOT_2C | ~370 | ~145 | 61% |
| MAIN_INTENT_BOT_1 (system) | ~340 | ~148 | 56% |
| MAIN_INTENT_BOT_1 (few-shot) | ~820 | Split/reduce | 82% |
| MAIN_REWRITE_BOT_0 | ~180 | ~95 | 47% |
| QUERY_SQL_GEN_BOT_2Q | ~320 | ~138 | 57% |
| EVAL_EVALUATOR_BOT_2E | ~280 | ~145 | 48% |
| QUERY_RANKER_BOT_3Q | ~210 | ~85 | 60% |

## Key Optimization Strategies Used:

1. **Remove redundant explanations** - Keep only essential instructions
2. **Use abbreviations and concise language** - "עוזר עברית" instead of full descriptions
3. **Simplify examples** - Shorter, more focused examples
4. **Consolidate similar instructions** - Group related rules together
5. **Remove verbose JSON structure explanations** - Show format once, concisely
6. **Use bullet points instead of numbered lists** - More compact
7. **Hebrew text optimization** - Shorter Hebrew phrases where possible

## Files to Edit:

1. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/CLARIFY_CLARIFY_BOT_2C/main.py` (lines 164-186)
2. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/MAIN_INTENT_BOT_1/prompts.py` (multiple sections)
3. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/MAIN_REWRITE_BOT_0/main.py` (lines 79-99)
4. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py` (lines 84-115)
5. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/EVAL_EVALUATOR_BOT_2E/main.py` (lines 460-482)
6. `/mnt/c/Users/tomer/Downloads/ceci-w-bots/bot_chain/QUERY_RANKER_BOT_3Q/main.py` (lines 247-261)

## Next Steps:

1. Apply the optimized prompts to each file
2. Test functionality to ensure optimization doesn't break behavior
3. Monitor token usage in production
4. Further optimize if needed while maintaining quality