# 🎯 Intent Detection Engine - Technical Specification v2.0

## 📌 Overview

A deterministic, rule-based intent detection system that classifies Hebrew queries into **exactly 4 intent types** without using any AI/GPT tokens. The system must achieve 100% accuracy on known patterns with sub-millisecond response times.

## 🗂️ Intent Types (Exactly 4)

### 1. **QUERY** - General Search (includes Statistical & Comparison)
Any request to retrieve, count, compare, or analyze government decisions from the database.

### 2. **EVAL** - Deep Analysis Request
Specific requests for in-depth analysis of particular decisions (very selective, expensive operation).

### 3. **CLARIFICATION** - Needs Clarification
Queries that are too vague, incomplete, or ambiguous to process.

### 4. **REFERENCE** - Refers to Previous Interaction
Queries referencing previous responses that need context before routing to QUERY or EVAL.

---

## 📋 Output Format Specification

```typescript
interface IntentDetectionResult {
  intent_type: "QUERY" | "EVAL" | "CLARIFICATION" | "REFERENCE";
  
  entities: {
    // Numeric entities
    government_number?: number;      // 20-38
    decision_number?: number;        // Any positive integer
    limit?: number;                  // How many results to return
    
    // Text entities
    topic?: string;                  // Normalized topic
    ministries?: string[];           // Array of normalized ministry names
    
    // Date entities
    date_range?: {
      start: string;                 // ISO format: YYYY-MM-DD
      end: string;                    // ISO format: YYYY-MM-DD
    };
    
    // Query modifiers
    operation?: "search" | "count" | "compare" | "list";
    comparison_target?: string;      // For comparisons
    sort_order?: "asc" | "desc";
    
    // Reference markers
    reference_type?: "last" | "previous" | "specific" | "context";
    reference_position?: number;     // 1 = last, 2 = second to last, etc.
  };
  
  confidence: number;               // 0.0 to 1.0
  
  route_flags: {
    needs_context: boolean;         // True only for REFERENCE
    is_statistical: boolean;        // True for count operations
    is_comparison: boolean;         // True for comparison operations
  };
  
  explanation: string;              // Human-readable explanation
}
```

---

## 🔍 Detection Rules by Intent Type

### **1. QUERY Intent Detection**

```javascript
const QUERY_DETECTION = {
  // SEARCH OPERATIONS
  search_triggers: {
    prefixes: [
      "החלטות",
      "כל החלטות",
      "רשימת החלטות",
      "הצג",
      "הראה",
      "תן לי",
      "מצא",
      "חפש"
    ],
    
    patterns: [
      /^(\d+)\s+החלטות/,                    // "5 החלטות"
      /החלטות\s+(ה)?אחרונות/,              // "החלטות אחרונות"
      /ממשלה\s+(\d+)/,                      // "ממשלה 37"
      /החלטות\s+משרד/,                     // "החלטות משרד"
      /החלטות\s+ב(נושא|תחום)/,           // "החלטות בנושא"
      /החלטות\s+מ(תאריך|יום|-)/,         // "החלטות מתאריך"
      /החלטות\s+בין.*ל/                   // "החלטות בין X ל-Y"
    ]
  },
  
  // STATISTICAL OPERATIONS (still QUERY)
  statistical_triggers: {
    keywords: [
      "כמה",
      "מספר",
      "כמות",
      "סה\"כ",
      "בסך הכל",
      "סכום"
    ],
    
    patterns: [
      /כמה\s+החלטות/,
      /מספר\s+(ה)?החלטות/,
      /מה\s+(ה)?כמות/,
      /כמה\s+פעמים/
    ],
    
    // Sets operation: "count"
    sets_operation: "count"
  },
  
  // COMPARISON OPERATIONS (still QUERY)
  comparison_triggers: {
    keywords: [
      "השווה",
      "השוואה",
      "ההבדל",
      "לעומת",
      "מול"
    ],
    
    patterns: [
      /השווה\s+בין.*ל/,
      /ההבדל\s+בין/,
      /מה\s+ההבדל/,
      /(ממשלה|תקופה|שנה)\s+(\d+)\s+לעומת\s+(\d+)/
    ],
    
    // Sets operation: "compare"
    sets_operation: "compare"
  }
};
```

### **2. EVAL Intent Detection**

```javascript
const EVAL_DETECTION = {
  // VERY STRICT - Only explicit analysis requests
  strict_triggers: {
    verbs: [
      "נתח",
      "ניתוח",
      "הסבר לעומק",
      "פרט באופן מעמיק"
    ],
    
    patterns: [
      /נתח\s+(את\s+)?החלטה\s+(\d+)/,              // "נתח את החלטה 123"
      /ניתוח\s+מעמיק\s+של\s+החלטה/,              // "ניתוח מעמיק של החלטה"
      /אני\s+רוצה\s+ניתוח\s+(מעמיק\s+)?של/,      // "אני רוצה ניתוח של"
      /הסבר\s+את\s+ההשלכות\s+של\s+החלטה/,       // "הסבר את ההשלכות של החלטה"
      /מה\s+המשמעות\s+המעמיקה\s+של/              // "מה המשמעות המעמיקה של"
    ],
    
    required_context: [
      "החלטה ספציפית",   // Must reference specific decision
      "מספר החלטה",      // Must have decision number
      "ניתוח מעמיק"      // Must explicitly ask for deep analysis
    ]
  },
  
  // If detected, must have decision_number or be REFERENCE
  validation: (entities) => {
    return entities.decision_number || 
           entities.reference_type === "last" ||
           entities.reference_type === "specific";
  }
};
```

### **3. CLARIFICATION Intent Detection**

```javascript
const CLARIFICATION_DETECTION = {
  // Automatic triggers
  triggers: {
    // Too short (less than 3 words)
    length_check: (query) => query.trim().split(/\s+/).length < 3,
    
    // Too vague
    vague_patterns: [
      /^מה\s*\??$/,                    // "מה?"
      /^איך\s*\??$/,                   // "איך?"
      /^למה\s*\??$/,                   // "למה?"
      /^מה\s+עם/,                     // "מה עם..."
      /^מה\s+לגבי/,                   // "מה לגבי..."
      /^(כן|לא|אוקיי|טוב)\s*\??$/     // "כן?" "לא?"
    ],
    
    // Missing critical information
    incomplete_patterns: [
      /^החלטות$/,                     // Just "החלטות"
      /^ממשלה$/,                      // Just "ממשלה"
      /^משרד$/,                        // Just "משרד"
      /^(ה)?(אחרונה|ראשונה|שנייה)$/  // Just "האחרונה"
    ],
    
    // Ambiguous without context
    ambiguous: [
      "זה", "זו", "זאת", "אלה", "אלו",
      "הדבר", "העניין", "הנושא"
    ]
  },
  
  // If none of the other intents match with high confidence
  fallback_threshold: 0.6
};
```

### **4. REFERENCE Intent Detection**

```javascript
const REFERENCE_DETECTION = {
  // References to previous interactions
  triggers: {
    // Direct references to sent content
    sent_references: [
      "ששלחת",
      "שהצגת", 
      "שהראית",
      "שנתת",
      "שהבאת"
    ],
    
    // Positional references
    positional: [
      "האחרונה",
      "הקודמת",
      "הראשונה",
      "השנייה",
      "השלישית",
      "הרביעית"
    ],
    
    // Conversation continuity
    continuity: [
      "כמו ששאלתי",
      "כמו שביקשתי",
      "כפי שאמרתי",
      "בהמשך ל",
      "עוד כמו"
    ],
    
    // Time-based references
    temporal: [
      "קודם",
      "לפני",
      "מקודם",
      "זה עתה",
      "הרגע"
    ]
  },
  
  patterns: [
    /(ה)?החלטה\s+ששלחת(\s+לי)?/,              // "ההחלטה ששלחת"
    /מה\s+ש(אמרתי|שאלתי|ביקשתי)\s+קודם/,      // "מה ששאלתי קודם"
    /עוד\s+(החלטות\s+)?כמו/,                  // "עוד כמו..."
    /(ה)?(אחרונה|קודמת)\s+ש/                  // "האחרונה ש..."
  ],
  
  // Determines if this leads to QUERY or EVAL
  route_determination: (query) => {
    const evalKeywords = ["נתח", "ניתוח", "הסבר", "השלכות"];
    return evalKeywords.some(keyword => query.includes(keyword)) ? "EVAL" : "QUERY";
  }
};
```

---

## 🔢 Entity Extraction Rules

### **Hebrew Number Conversion**
```javascript
const HEBREW_NUMBERS = {
  // Units
  "אחת": 1, "שתיים": 2, "שלוש": 3, "ארבע": 4, "חמש": 5,
  "שש": 6, "שבע": 7, "שמונה": 8, "תשע": 9, "עשר": 10,
  
  // Teens
  "אחת עשרה": 11, "שתים עשרה": 12, "שלוש עשרה": 13,
  
  // Tens
  "עשרים": 20, "שלושים": 30, "ארבעים": 40,
  
  // Composites
  "עשרים ואחת": 21, "עשרים ושתיים": 22,
  "שלושים ושבע": 37, "שלושים ושמונה": 38,
  
  // Ordinals
  "ראשונה": 1, "שנייה": 2, "שלישית": 3, "רביעית": 4
};
```

### **Ministry Normalization**
```javascript
const MINISTRY_MAPPING = {
  // Short forms to full names
  "החינוך": "משרד החינוך",
  "הביטחון": "משרד הביטחון",
  "האוצר": "משרד האוצר",
  "הבריאות": "משרד הבריאות",
  "התחבורה": "משרד התחבורה",
  "המשפטים": "משרד המשפטים",
  "החוץ": "משרד החוץ",
  "הפנים": "משרד הפנים",
  "הכלכלה": "משרד הכלכלה והתעשייה",
  "החקלאות": "משרד החקלאות ופיתוח הכפר",
  
  // Abbreviations
  "משה\"ב": "משרד הביטחון",
  "רה\"מ": "ראש הממשלה",
  "מה\"ט": "המטה לביטחון לאומי"
};
```

### **Date Extraction**
```javascript
const DATE_EXTRACTION = {
  // Relative dates
  relative: {
    "היום": () => new Date().toISOString().split('T')[0],
    "אתמול": () => {
      const d = new Date();
      d.setDate(d.getDate() - 1);
      return d.toISOString().split('T')[0];
    },
    "השבוע": () => getCurrentWeekRange(),
    "החודש": () => getCurrentMonthRange(),
    "השנה": () => getCurrentYearRange()
  },
  
  // Month names
  months: {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12
  },
  
  // Patterns
  patterns: {
    full_date: /(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})/,
    month_year: /(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s+(\d{4})/,
    year_only: /\b(20\d{2})\b/,
    range: /בין\s+(.+?)\s+ל[בין]*\s*(.+)/
  }
};
```

---

## 🏗️ Implementation Algorithm

```javascript
class IntentDetector {
  detect(query) {
    // 1. Normalize
    const normalized = this.normalize(query);
    
    // 2. Quick length check for CLARIFICATION
    if (normalized.split(/\s+/).length < 3) {
      return this.clarificationResult("Query too short");
    }
    
    // 3. Check for REFERENCE markers FIRST
    const referenceCheck = this.checkReference(normalized);
    if (referenceCheck.isReference) {
      return {
        intent_type: "REFERENCE",
        entities: this.extractEntities(normalized),
        confidence: referenceCheck.confidence,
        route_flags: {
          needs_context: true,
          is_statistical: false,
          is_comparison: false
        },
        explanation: `Reference to ${referenceCheck.referenceType}`
      };
    }
    
    // 4. Check for EVAL (very strict)
    const evalCheck = this.checkEval(normalized);
    if (evalCheck.isEval && evalCheck.confidence > 0.8) {
      const entities = this.extractEntities(normalized);
      // Validate EVAL requirements
      if (entities.decision_number || referenceCheck.couldBeEval) {
        return {
          intent_type: "EVAL",
          entities,
          confidence: evalCheck.confidence,
          route_flags: {
            needs_context: false,
            is_statistical: false,
            is_comparison: false
          },
          explanation: "Deep analysis request"
        };
      }
    }
    
    // 5. Check for QUERY (including statistical and comparison)
    const queryCheck = this.checkQuery(normalized);
    if (queryCheck.isQuery) {
      const entities = this.extractEntities(normalized);
      return {
        intent_type: "QUERY",
        entities: {
          ...entities,
          operation: queryCheck.operation // "search", "count", "compare"
        },
        confidence: queryCheck.confidence,
        route_flags: {
          needs_context: false,
          is_statistical: queryCheck.operation === "count",
          is_comparison: queryCheck.operation === "compare"
        },
        explanation: `${queryCheck.operation} operation`
      };
    }
    
    // 6. Default to CLARIFICATION
    return this.clarificationResult("Could not determine clear intent");
  }
  
  normalize(query) {
    return query
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[.,!?;:]+$/, '');
  }
  
  extractEntities(query) {
    // Parallel extraction for performance
    return {
      government_number: this.extractGovernment(query),
      decision_number: this.extractDecision(query),
      limit: this.extractLimit(query),
      topic: this.extractTopic(query),
      ministries: this.extractMinistries(query),
      date_range: this.extractDateRange(query),
      reference_type: this.extractReferenceType(query),
      reference_position: this.extractReferencePosition(query)
    };
  }
}
```

---

## 🧪 Test Cases

```javascript
const TEST_CASES = [
  // QUERY - Search
  {
    input: "החלטות ממשלה 37 בנושא חינוך",
    expected: {
      intent_type: "QUERY",
      entities: {
        government_number: 37,
        topic: "חינוך",
        operation: "search"
      }
    }
  },
  
  // QUERY - Statistical
  {
    input: "כמה החלטות יש בנושא בריאות?",
    expected: {
      intent_type: "QUERY",
      entities: {
        topic: "בריאות",
        operation: "count"
      },
      route_flags: { is_statistical: true }
    }
  },
  
  // QUERY - Comparison
  {
    input: "השווה בין ממשלה 36 ל-37",
    expected: {
      intent_type: "QUERY",
      entities: {
        operation: "compare",
        comparison_target: "governments:36,37"
      },
      route_flags: { is_comparison: true }
    }
  },
  
  // EVAL
  {
    input: "נתח את החלטה 2983",
    expected: {
      intent_type: "EVAL",
      entities: {
        decision_number: 2983
      }
    }
  },
  
  // REFERENCE
  {
    input: "נתח את ההחלטה האחרונה ששלחת",
    expected: {
      intent_type: "REFERENCE",
      entities: {
        reference_type: "last",
        reference_position: 1
      },
      route_flags: { needs_context: true }
    }
  },
  
  // CLARIFICATION
  {
    input: "מה?",
    expected: {
      intent_type: "CLARIFICATION",
      confidence: 0.3
    }
  }
];
```

---

## ⚡ Performance Requirements

- **Response time**: < 1ms per query
- **Memory usage**: < 50MB for all patterns and rules
- **Accuracy**: 100% on defined patterns
- **Fallback**: Always returns valid intent (CLARIFICATION as default)

---

## 🔐 Error Handling

```javascript
try {
  const result = detector.detect(query);
  // Validate result structure
  if (!isValidIntentResult(result)) {
    throw new Error("Invalid detection result");
  }
  return result;
} catch (error) {
  // Always return CLARIFICATION on error
  return {
    intent_type: "CLARIFICATION",
    entities: {},
    confidence: 0.1,
    route_flags: {
      needs_context: false,
      is_statistical: false,
      is_comparison: false
    },
    explanation: `Error in detection: ${error.message}`
  };
}
```

---

## 📦 Integration Notes

1. **The Intent Bot receiving this output expects**:
   - `intent_type` field (not `intent`)
   - Normalized ministry names
   - Hebrew numbers converted to digits
   - Dates in ISO format

2. **Context Router activation**:
   - Only when `intent_type === "REFERENCE"`
   - Never for regular QUERY/EVAL/CLARIFICATION

3. **SQL Gen Bot handles**:
   - All QUERY operations (search, count, compare)
   - Uses `operation` field to determine query type

4. **Evaluator Bot**:
   - Only activated for `intent_type === "EVAL"`
   - Requires valid decision_number

This specification ensures 100% deterministic routing with zero AI token usage while maintaining full compatibility with the existing bot chain architecture.