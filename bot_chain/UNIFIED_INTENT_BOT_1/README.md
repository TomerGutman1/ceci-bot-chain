# Unified Intent Bot (GPT-4o-turbo)

## Overview

The Unified Intent Bot combines the functionality of the previous Rewrite Bot and Intent Bot into a single, more efficient service. This bot serves as the entry point for all queries in the unified architecture.

## Key Features

- **Combined Processing**: Handles both text normalization and intent detection in one API call
- **Hebrew Optimization**: Specialized handling for Hebrew text, typos, and linguistic variations
- **Statistical Detection**: Recognizes queries asking for counts ("כמה") and sets appropriate flags
- **Context Awareness**: Identifies when queries reference previous conversation context

## Architecture Benefits

1. **Performance**: Saves 200-300ms by eliminating one network call
2. **Token Efficiency**: ~100 tokens saved per query
3. **Quality**: GPT-4o provides better Hebrew understanding than GPT-3.5
4. **Simplicity**: Single point of maintenance for query preprocessing

## Intent Types

- `DATA_QUERY`: Regular search queries for decisions
- `ANALYSIS`: Requests for deep analysis or evaluation
- `RESULT_REF`: References to previous results ("tell me more about this")
- `UNCLEAR`: Ambiguous queries requiring clarification

## API Endpoint

```
POST /intent
{
  "raw_user_text": "כמה החלטות בנושא חינוך קיבלה ממשלה 37",
  "chat_history": [...],
  "conv_id": "unique-conversation-id"
}
```

## Response Structure

```json
{
  "conv_id": "unique-conversation-id",
  "clean_query": "כמה החלטות בנושא חינוך קיבלה ממשלה 37",
  "intent": "DATA_QUERY",
  "params": {
    "topic": "חינוך",
    "government_number": 37,
    "count_only": true
  },
  "confidence": 0.95,
  "route_flags": {
    "needs_context": false,
    "is_statistical": true,
    "is_comparison": false
  },
  "corrections": [...],
  "token_usage": {...}
}
```

## Special Handling

### Statistical Queries
- Detects "כמה" (how many) and sets `count_only: true`
- Sets `is_statistical: true` in route flags
- Ensures SQL Gen Bot uses COUNT templates

### Context References
- Identifies pronouns like "זה", "זאת", "הקודם"
- Sets `needs_context: true` for Context Router
- Extracts ordinal references ("השני", "הראשון")

### Hebrew Normalization
- Fixes common typos: "חנוך" → "חינוך"
- Normalizes ministry names: "החינוך" → "משרד החינוך"
- Handles number variations: "שלושים ושבע" → 37

## Testing

Run tests with:
```bash
python test_unified_intent.py
```

## Environment Variables

- `OPENAI_API_KEY`: Required for GPT-4o access
- `LOG_LEVEL`: Default INFO
- `PORT`: Default 8011

## Model Configuration

- **Model**: gpt-4o-2024-08-06 (GPT-4o-turbo)
- **Temperature**: 0.1 (low for consistency)
- **Max Tokens**: 500
- **Cost**: ~$0.007 per query