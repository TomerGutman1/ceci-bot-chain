# LLM Formatter Bot (GPT-4o-mini)

## Overview

The LLM Formatter Bot is an AI-powered response formatter that transforms raw SQL query results into natural, conversational Hebrew text. This bot replaces the previous deterministic code-based formatter with a more flexible and linguistically sophisticated approach.

## Key Features

- **Natural Language Generation**: Produces fluent, grammatically correct Hebrew responses
- **Gender/Number Agreement**: Handles complex Hebrew plural and gender rules correctly
- **Statistical Formatting**: Presents counts and statistics in a clear, readable format
- **Flexible Formatting**: Adapts to different types of queries and result structures
- **Context Awareness**: Maintains consistency with the user's original question style

## Architecture Benefits

1. **Quality**: Superior Hebrew language handling compared to rule-based formatting
2. **Flexibility**: Handles edge cases and complex formatting scenarios
3. **Maintainability**: No need to update code for new formatting rules
4. **Cost Efficiency**: Uses GPT-4o-mini for optimal cost/quality balance

## Input Structure

```json
{
  "conv_id": "unique-conversation-id",
  "results": [...],
  "query": "Original user query",
  "service": "query/evaluation/etc",
  "metadata": {
    "intent": "DATA_QUERY",
    "is_statistical": false,
    "count_only": false
  }
}
```

## Response Types

### 1. List Results
- Formats multiple decisions with bullets or numbering
- Includes decision number, date, and topic
- Provides URL links when available

### 2. Statistical Results
- Presents counts in natural language
- Handles zero results gracefully
- Provides context for the numbers

### 3. Analysis Results
- Formats evaluation scores clearly
- Structures multi-aspect analysis
- Maintains readability for long content

### 4. Single Results
- Provides detailed information
- Includes all relevant fields
- Natural paragraph structure

## API Endpoint

```
POST /format
{
  "conv_id": "uuid",
  "results": [...],
  "query": "כמה החלטות בנושא חינוך",
  "service": "query",
  "metadata": {...}
}
```

## Response Structure

```json
{
  "conv_id": "uuid",
  "formatted_response": "נמצאו 156 החלטות בנושא חינוך...",
  "formatting_metadata": {
    "response_type": "statistical",
    "result_count": 156,
    "formatting_rules_applied": ["number_formatting", "hebrew_grammar"]
  },
  "token_usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200,
    "estimated_cost": 0.0003
  }
}
```

## Special Handling

### Hebrew Grammar Rules
- Correct plural forms: "2 החלטות" not "2 החלטה"
- Gender agreement: "נמצאו" vs "נמצאה"
- Number formatting: "156" presented naturally

### Zero Results
- Polite, helpful response
- Suggests alternatives when appropriate
- Clear indication that no results were found

### Large Result Sets
- Summarizes key information
- Groups by relevant criteria
- Maintains readability

## Prompt Engineering

The bot uses a carefully crafted prompt that:
1. Emphasizes Hebrew language correctness
2. Provides clear formatting examples
3. Handles different result types
4. Maintains consistent tone

## Testing

Run formatter-specific tests:
```bash
python test_llm_formatter.py
```

## Environment Variables

- `OPENAI_API_KEY`: Required for GPT-4o-mini access
- `LOG_LEVEL`: Default INFO
- `PORT`: Default 8017
- `MAX_TOKENS`: Default 500

## Model Configuration

- **Model**: gpt-4o-mini-2024-07-18
- **Temperature**: 0.3 (balanced creativity/consistency)
- **Max Tokens**: 500
- **Cost**: ~$0.0003 per format operation

## Common Formatting Patterns

### Statistical Response
```
נמצאו 45 החלטות בנושא תחבורה מתוך סך של 1,234 החלטות ממשלה.
```

### List Response
```
הנה 3 ההחלטות האחרונות בנושא חינוך:

• החלטה 2989 (15/01/2024) - רפורמה במערכת החינוך
• החלטה 2876 (03/01/2024) - תקציב מיוחד לחינוך מיוחד
• החלטה 2765 (22/12/2023) - שיפוץ בתי ספר
```

### No Results
```
לא נמצאו החלטות התואמות את החיפוש שלך. 
אולי תרצה לנסות חיפוש רחב יותר או לבדוק את האיות?
```

## Performance Considerations

- Caches common formatting patterns
- Reuses examples for similar queries
- Optimizes token usage through concise prompts
- Handles streaming responses efficiently