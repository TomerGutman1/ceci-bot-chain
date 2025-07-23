# Summary: How "נתח את החלטה" Requests are Handled

## Overview
When a user submits a request like "נתח את החלטה 2989" (analyze decision 2989), the system follows a specific flow through multiple bot services to perform a feasibility analysis of the government decision.

## Complete Flow

### 1. **Frontend (chat.ts)**
- User submits: "נתח את החלטה 2989"
- The chat service sends this to the bot chain

### 2. **Bot Chain Service (botChainService.ts)**
- Receives the request and starts the processing pipeline
- First sends to the Unified Intent Bot

### 3. **Unified Intent Bot (UNIFIED_INTENT_BOT_1)**
- Detects keywords: "נתח", "ניתוח", "הסבר לעומק"
- Classifies intent as: **"ANALYSIS"**
- Extracts entities:
  - decision_number: 2989
  - government_number: (defaults to 37 if not specified)
- Returns clean query: "החלטה 2989 של ממשלה 37 - ניתוח מעמיק"

### 4. **Context Router Bot (MAIN_CTX_ROUTER_BOT_2X)**
- Receives ANALYSIS intent
- Checks routing rules
- For ANALYSIS intent with decision_number → routes to SQL Gen Bot

### 5. **SQL Gen Bot (QUERY_SQL_GEN_BOT_2Q)**
- Generates SQL query to fetch the specific decision
- Executes query against database
- Returns decision content

### 6. **Bot Chain Service - Evaluator Decision**
```typescript
// Key logic in botChainService.ts
private shouldRunEvaluator(intent: string, entities: any, results: any[]): boolean {
    // Must be EVAL or ANALYSIS intent
    if (intent !== 'EVAL' && intent !== 'ANALYSIS') {
        return false;
    }
    
    // Case 1: Specific decision requested
    if (entities.decision_number && results.length === 1) {
        return true;
    }
    
    // Case 2: Single result without specific decision
    if (!entities.decision_number && results.length === 1) {
        return true;
    }
    
    // Case 3: Multiple results - DON'T analyze
    if (results.length > 1) {
        return false;
    }
}
```

### 7. **Evaluator Bot (EVAL_EVALUATOR_BOT_2E)**
When activated for analysis:

1. **Fetches Full Decision Content**
   - Uses backend API to get complete decision text
   - Validates if decision is suitable for analysis

2. **Validation Checks**
   - Checks if decision is "דקלרטיבית" (declarative) → rejects with explanation
   - Checks content length → adds note if too short (<500 chars)

3. **Performs 13-Criteria Analysis**
   The bot analyzes the decision against these criteria:
   - לוח זמנים מחייב (17%) - Mandatory timeline
   - צוות מתכלל (7%) - Coordinating team
   - גורם מתכלל יחיד (5%) - Single coordinator
   - מנגנון דיווח/בקרה (9%) - Reporting/control mechanism
   - מנגנון מדידה והערכה (6%) - Measurement and evaluation
   - מנגנון ביקורת חיצונית (4%) - External audit
   - משאבים נדרשים (19%) - Required resources
   - מעורבות של מספר דרגים (7%) - Multi-level involvement
   - מבנה סעיפים וחלוקת עבודה (9%) - Clear structure
   - מנגנון יישום בשטח (9%) - Implementation mechanism
   - גורם מכריע (3%) - Decision maker
   - שותפות בין מגזרית (3%) - Cross-sector partnership
   - מדדי תוצאה (2%) - Success metrics

4. **Returns Structured Analysis**
   ```json
   {
     "criteria": [...],
     "final_score": 65,
     "summary": "סיכום הניתוח",
     "recommendations": [...]
   }
   ```

### 8. **Formatter Bot (LLM_FORMATTER_BOT_4)**
Receives the analysis results and formats them into a user-friendly response:

```python
def format_analysis_results(content: Dict[str, Any]) -> str:
    # Creates formatted output with:
    # - Decision header with title and number
    # - Criteria table with scores
    # - Overall feasibility score (X/100)
    # - Feasibility level (High/Medium/Low)
    # - Key findings summary
    # - Recommendations for improvement
    # - Citations from the decision text
```

### 9. **Final Output to User**
Example formatted response:

```markdown
## 🔍 ניתוח החלטת ממשלה 2989

**כותרת ההחלטה:** [Decision Title]

### 📊 ניתוח מפורט לפי קריטריונים

| קריטריון | משקל | ציון |
|----------|-------|------|
| לוח זמנים מחייב | 17% | 3/5 |
| צוות מתכלל | 7% | 2/5 |
| ... | ... | ... |

### 🎯 ציון ישימות כולל: 65/100

⚠️ **רמת ישימות: בינונית**

### 📝 מסקנות מרכזיות
[Summary of the analysis]

### 💡 המלצות לשיפור היישום
• הוספת לוח זמנים מפורט עם אבני דרך
• מינוי צוות מתכלל עם סמכויות ברורות
• ...
```

## Key Configuration Points

1. **Intent Detection**: The keyword "נתח" triggers ANALYSIS intent in the Unified Intent Bot
2. **Route Mapping**: ANALYSIS intent maps to EVAL route in botChainService.ts
3. **Evaluator Activation**: Only runs for single decisions, not multiple results
4. **Model Selection**: Uses GPT-4o for complex analysis (evaluator bot)
5. **Timeout**: Extended timeout of 120 seconds for evaluator operations
6. **Validation**: Declarative decisions are rejected with appropriate user message

## Error Handling

- If decision is declarative: Returns explanation why analysis isn't suitable
- If decision is too short: Performs analysis but notes limited content
- If no decision found: Returns appropriate error message
- If analysis fails: Falls back to basic formatting

## Token Usage
The evaluator bot tracks token usage for the GPT-4o calls and includes this in the response for monitoring purposes.