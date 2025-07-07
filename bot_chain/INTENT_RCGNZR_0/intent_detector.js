/**
 * Intent Detection Engine v2.0
 * Deterministic, rule-based intent classification for Hebrew queries
 * Zero AI tokens, sub-millisecond response time
 */

class IntentDetector {
  constructor() {
    this.initializePatterns();
    this.initializeMappings();
  }

  initializePatterns() {
    // QUERY Detection Patterns
    this.queryPatterns = {
      search_triggers: {
        prefixes: [
          "החלטה", "החלטות", "כל החלטות", "רשימת החלטות", "הצג", "הראה",
          "תן לי", "מצא", "חפש"
        ],
        patterns: [
          /^(\d+)\s+החלטות/,
          /החלטה\s+(\d+)/,  // זיהוי "החלטה 2983"
          /החלטות\s+(ה)?אחרונות/,
          /ממשלה\s+(\d+)/,
          /החלטות\s+משרד/,
          /החלטות\s+ב(נושא|תחום)/,
          /החלטות\s+מ(תאריך|יום|-)/,
          /החלטות\s+בין.*ל/
        ]
      },
      statistical_triggers: {
        keywords: ["כמה", "מספר", "כמות", "סה\"כ", "סה״כ", "בסך הכל", "סכום"],
        patterns: [
          /כמה\s+החלטות/,
          /מספר\s+(ה)?החלטות/,
          /מה\s+(ה)?כמות/,
          /כמה\s+פעמים/
        ]
      },
      comparison_triggers: {
        keywords: ["השווה", "השוואה", "ההבדל", "לעומת", "מול"],
        patterns: [
          /השווה\s+בין.*ל/,
          /ההבדל\s+בין/,
          /מה\s+ההבדל/,
          /(ממשלה|תקופה|שנה)\s+(\d+)\s+לעומת\s+(\d+)/
        ]
      }
    };

    // EVAL Detection Patterns
    this.evalPatterns = {
      strict_triggers: {
        verbs: ["נתח", "ניתח", "ניתוח", "נתח לעומק", "הסבר לעומק", "פרט באופן מעמיק", "בחן לעומק", "ניתוח יסודי", "ענה על"],
        patterns: [
          /נתח\s+(את\s+)?החלטה\s+(\d+)/,
          /ניתח\s+(את\s+)?החלטה\s+(\d+)/,
          /נתח\s+לעומק\s+(את\s+)?החלטה\s+(\d+)/,
          /ניתוח\s+מעמיק\s+של\s+החלטה/,
          /אני\s+רוצה\s+ניתוח\s+(מעמיק\s+)?של/,
          /הסבר\s+את\s+ההשלכות\s+של\s+החלטה/,
          /מה\s+המשמעות\s+המעמיקה\s+של/,
          /בחן\s+לעומק\s+את\s+החלטה/,
          /ניתוח\s+יסודי\s+של\s+החלטה/,
          /פרט\s+באופן\s+מעמיק\s+על\s+החלטה/
        ]
      }
    };

    // REFERENCE Detection Patterns
    this.referencePatterns = {
      sent_references: ["ששלחת", "שהצגת", "שהראית", "שנתת", "שהבאת"],
      positional: ["האחרונה", "הקודמת", "הראשונה", "השנייה", "השלישית", "הרביעית"],
      continuity: ["כמו ששאלתי", "כמו שביקשתי", "כפי שאמרתי", "בהמשך ל", "עוד כמו", "תוכן מלא", "התוכן המלא", "את התוכן המלא", "התוכן", "את התוכן"],
      temporal: ["קודם", "לפני", "מקודם", "זה עתה", "הרגע"],
      patterns: [
        /(ה)?החלטה\s+ששלחת(\s+לי)?/,
        /מה\s+ש(אמרתי|שאלתי|ביקשתי)\s+קודם/,
        /עוד\s+(החלטות\s+)?כמו/,
        /(ה)?(אחרונה|קודמת)\s+ש/
      ]
    };

    // CLARIFICATION Detection Patterns
    this.clarificationPatterns = {
      vague_patterns: [
        /^מה\s*\??$/,
        /^איך\s*\??$/,
        /^למה\s*\??$/,
        /^מה\s+עם/,
        /^מה\s+לגבי/,
        /^(כן|לא|אוקיי|טוב)\s*\??$/
      ],
      incomplete_patterns: [
        /^החלטות$/,
        /^ממשלה$/,
        /^משרד$/,
        /^(ה)?(אחרונה|ראשונה|שנייה)$/,
        /^תן החלטות על/
      ],
      ambiguous: ["זה", "זו", "זאת", "אלה", "אלו", "הדבר", "העניין", "הנושא"]
    };
  }

  initializeMappings() {
    // Hebrew Numbers
    this.hebrewNumbers = {
      "אחת": 1, "שתיים": 2, "שלוש": 3, "ארבע": 4, "חמש": 5,
      "שש": 6, "שבע": 7, "שמונה": 8, "תשע": 9, "עשר": 10,
      "אחת עשרה": 11, "שתים עשרה": 12, "שלוש עשרה": 13,
      "ארבע עשרה": 14, "חמש עשרה": 15, "שש עשרה": 16,
      "שבע עשרה": 17, "שמונה עשרה": 18, "תשע עשרה": 19,
      "עשרים": 20, "שלושים": 30, "ארבעים": 40,
      "עשרים ואחת": 21, "עשרים ושתיים": 22, "עשרים ושלוש": 23,
      "עשרים וארבע": 24, "עשרים וחמש": 25, "עשרים ושש": 26,
      "עשרים ושבע": 27, "עשרים ושמונה": 28, "עשרים ותשע": 29,
      "שלושים ואחת": 31, "שלושים ושתיים": 32, "שלושים ושלוש": 33,
      "שלושים וארבע": 34, "שלושים וחמש": 35, "שלושים ושש": 36,
      "שלושים ושבע": 37, "שלושים ושמונה": 38, "שלושים ותשע": 39,
      "ראשונה": 1, "שנייה": 2, "שלישית": 3, "רביעית": 4, "חמישית": 5
    };

    // Ministry Mapping
    this.ministryMapping = {
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
      "משה\"ב": "משרד הביטחון",
      "רה\"מ": "ראש הממשלה",
      "מה\"ט": "המטה לביטחון לאומי"
    };

    // Month Names
    this.monthNames = {
      "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
      "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
      "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12
    };

    // Hebrew Topic Mapping - normalize variations to standard forms
    this.topicMapping = {
      // Security variations
      "ביטחון": "ביטחון",
      "בטחון": "ביטחון", 
      "ביטחון לאומי": "ביטחון",
      "בטחון פנימי": "ביטחון",
      "ביטחון פנים": "ביטחון",
      
      // Education variations
      "חינוך": "חינוך",
      "השכלה": "חינוך", 
      "חינוך והשכלה": "חינוך",
      "חינוך וחברה": "חינוך",
      "מערכת החינוך": "חינוך",
      "חנוך": "חינוך", // common typo
      
      // Health variations
      "בריאות": "בריאות",
      "רפואה": "בריאות",
      "בריאות הציבור": "בריאות",
      "שירותי בריאות": "בריאות",
      "רפואה וחירום": "בריאות",
      "בראות": "בריאות", // common typo
      
      // Economy variations
      "כלכלה": "כלכלה",
      "כלכלה ותעשייה": "כלכלה",
      "כלכלי": "כלכלה",
      "התעשייה": "כלכלה",
      "מסחר": "כלכלה",
      "מסחר וכלכלה": "כלכלה",
      
      // Transportation variations
      "תחבורה": "תחבורה",
      "תחבורה ציבורית": "תחבורה",
      "תחבורה וכבישים": "תחבורה",
      "כבישים": "תחבורה",
      "תיחבורה": "תחבורה", // common typo
      
      // Agriculture variations
      "חקלאות": "חקלאות",
      "חקלאות וכפר": "חקלאות",
      "פיתוח הכפר": "חקלאות",
      "חקלאי": "חקלאות",
      
      // Housing variations
      "שיכון": "שיכון",
      "דיור": "שיכון",
      "בנייה ודיור": "שיכון",
      "שיכון ובינוי": "שיכון",
      
      // Environment variations
      "איכות הסביבה": "איכות הסביבה",
      "סביבה": "איכות הסביבה",
      "הגנת הסביבה": "איכות הסביבה",
      "איכות סביבה": "איכות הסביבה",
      
      // Justice variations
      "משפטים": "משפטים",
      "מערכת המשפט": "משפטים",
      "צדק": "משפטים",
      
      // Foreign affairs variations
      "חוץ": "חוץ",
      "יחסי חוץ": "חוץ",
      "מדיניות חוץ": "חוץ",
      "יחסים בינלאומיים": "חוץ",
      
      // Interior variations
      "פנים": "פנים",
      "הפנים": "פנים",
      "מדיניות פנים": "פנים",
      
      // Technology variations
      "טכנולוגיה": "טכנולוגיה",
      "מדע וטכנולוגיה": "מדע וטכנולוגיה",
      "מדע": "מדע וטכנולוגיה",
      "מחקר ופיתוח": "מדע וטכנולוגיה",
      "דיגיטל": "טכנולוגיה",
      
      // Social affairs variations
      "רווחה": "רווחה",
      "שירותים חברתיים": "רווחה",
      "רווחה וביטחון סוציאלי": "רווחה",
      "ביטחון סוציאלי": "רווחה",
      
      // Energy variations
      "אנרגיה": "אנרגיה",
      "משאבי אנרגיה": "אנרגיה",
      "תשתיות אנרגיה": "אנרגיה",
      "חשמל": "אנרגיה"
    };
  }

  detect(query) {
    try {
      // 1. Normalize query
      const normalized = this.normalize(query);
      
      // 2. Quick length check for CLARIFICATION - but allow specific patterns
      const words = normalized.split(/\s+/);
      if (words.length < 3) {
        // Check if it's a valid short pattern like "החלטה 2983", "ממשלה 37", or contains dates
        const hasValidPattern = /החלטה\s+\d+/.test(normalized) || 
                              /ממשלה\s+\d+/.test(normalized) ||
                              /ב[־-]?\d{4}/.test(normalized) || // Year patterns like "ב-2020"
                              normalized.includes("השנה") ||
                              normalized.includes("החודש") ||
                              /משנת\s+\d{4}/.test(normalized);
        
        if (!hasValidPattern) {
          return this.clarificationResult("Query too short");
        }
        // If it matches the pattern, continue processing
      }

      // 3. Check for REFERENCE markers FIRST (highest priority)
      const referenceCheck = this.checkReference(normalized);
      if (referenceCheck.isReference) {
        // BUT: If this is also an EVAL pattern, prefer EVAL over REFERENCE
        const evalCheck = this.checkEval(normalized);
        if (evalCheck.isEval && evalCheck.confidence > 0.7) {
          return {
            intent_type: "EVAL",
            entities: this.extractEntities(normalized),
            confidence: evalCheck.confidence,
            route_flags: {
              needs_context: true,
              is_statistical: false,
              is_comparison: false
            },
            explanation: "Analysis request with context reference"
          };
        }
        
        return {
          intent_type: "REFERENCE",
          entities: {
            ...this.extractEntities(normalized),
            reference_type: referenceCheck.referenceType,
            reference_position: referenceCheck.referencePosition
          },
          confidence: referenceCheck.confidence,
          route_flags: {
            needs_context: true,
            is_statistical: false,
            is_comparison: false
          },
          explanation: `Reference to ${referenceCheck.referenceType}`
        };
      }

      // 4. Check for EVAL (very strict, second priority)
      const evalCheck = this.checkEval(normalized);
      if (evalCheck.isEval && evalCheck.confidence > 0.7) {
        const entities = this.extractEntities(normalized);
        if (entities.decision_number) {
          // Explicit decision number - direct EVAL
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
        } else {
          // EVAL patterns with context references (like "נתח לי את התוכן")
          const referenceCheck = this.checkReference(normalized);
          if (referenceCheck.isReference) {
            return {
              intent_type: "EVAL",
              entities,
              confidence: evalCheck.confidence,
              route_flags: {
                needs_context: true,
                is_statistical: false,
                is_comparison: false
              },
              explanation: "Analysis request with context reference"
            };
          }
        }
      }

      // 5. Check for explicit CLARIFICATION patterns BEFORE QUERY
      const clarificationCheck = this.checkClarification(normalized);
      if (clarificationCheck.needsClarification && clarificationCheck.priority) {
        return this.clarificationResult(clarificationCheck.reason);
      }

      // 6. Check for QUERY (third priority - most common)
      const queryCheck = this.checkQuery(normalized);
      if (queryCheck.isQuery) {
        // Special case: If EVAL patterns are present but didn't meet threshold, still prefer EVAL over QUERY
        const entities = this.extractEntities(normalized);
        if (evalCheck.confidence > 0.5 && entities.decision_number) {
          return {
            intent_type: "EVAL",
            entities,
            confidence: Math.max(evalCheck.confidence, 0.75), // Boost confidence slightly
            route_flags: {
              needs_context: false,
              is_statistical: false,
              is_comparison: false
            },
            explanation: "Analysis request (boosted from QUERY context)"
          };
        }
        
        // If both QUERY and CLARIFICATION are detected with low confidence, prefer CLARIFICATION
        if (clarificationCheck.needsClarification && queryCheck.confidence <= 0.6) {
          return this.clarificationResult(clarificationCheck.reason);
        }
        
        const queryEntities = this.extractEntities(normalized);
        console.log("DEBUG: queryEntities from extractEntities:", JSON.stringify(queryEntities));
        
        // Check for ambiguous number references
        if (queryEntities._ambiguity_type === "government_or_decision") {
          return this.clarificationResult("Ambiguous number reference", queryEntities);
        }
        
        // Check if this is a specific decision query
        if (queryEntities.decision_number) {
          // Default to current government (37) if no government specified
          if (!queryEntities.government_number) {
            queryEntities.government_number = 37;
          }
          
          return {
            intent_type: "QUERY",
            entities: {
              ...queryEntities,
              operation: "specific_decision"
            },
            confidence: Math.max(queryCheck.confidence, 0.85), // High confidence for specific decisions
            route_flags: {
              needs_context: false,
              is_statistical: false,
              is_comparison: false
            },
            explanation: queryEntities.government_number 
              ? "Specific decision lookup" 
              : "Decision lookup across all governments"
          };
        }
        
        const result = {
          intent_type: "QUERY",
          entities: {
            ...queryEntities,
            operation: queryCheck.operation
          },
          confidence: queryCheck.confidence,
          route_flags: {
            needs_context: false,
            is_statistical: queryCheck.operation === "count",
            is_comparison: queryCheck.operation === "compare"
          },
          explanation: `${queryCheck.operation} operation`
        };
        console.log("DEBUG: QUERY result entities:", JSON.stringify(result.entities));
        return result;
      }

      // 7. Check for remaining CLARIFICATION patterns
      if (clarificationCheck.needsClarification) {
        return this.clarificationResult(clarificationCheck.reason);
      }

      // 7. Default to CLARIFICATION
      return this.clarificationResult("Could not determine clear intent");

    } catch (error) {
      return this.clarificationResult(`Error in detection: ${error.message}`);
    }
  }

  normalize(query) {
    let normalized = query
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[.,!?;:]+$/, '');
    
    // Apply typo correction for common Hebrew mistakes
    normalized = this.correctCommonTypos(normalized);
    
    return normalized;
  }

  correctCommonTypos(text) {
    // Common Hebrew typos and corrections - only include actual mistakes
    const typoCorrections = {
      'החלתה': 'החלטה',
      'החלתות': 'החלטות',
      'ממשלת': 'ממשלה',
      'נותח': 'נתח',
      'צביא': 'הביא',
      'חנוך': 'חינוך',
      'בראות': 'בריאות',
      'תביא': 'הביא',
      'החלתה': 'החלטה'
    };

    // Apply corrections - check longer strings first to avoid partial replacements
    const corrections = Object.entries(typoCorrections)
      .sort((a, b) => b[0].length - a[0].length);

    for (const [typo, correction] of corrections) {
      // Replace all occurrences of the typo
      text = text.replace(new RegExp(typo, 'g'), correction);
    }

    return text;
  }

  checkReference(query) {
    let confidence = 0;
    let referenceType = null;
    let referencePosition = null;

    // Check for sent references
    for (const ref of this.referencePatterns.sent_references) {
      if (query.includes(ref)) {
        confidence += 0.5;
        referenceType = "last";
        referencePosition = 1;
      }
    }

    // Check for positional references
    for (const pos of this.referencePatterns.positional) {
      if (query.includes(pos)) {
        confidence += 0.4;
        if (pos === "האחרונה") {
          referenceType = "last";
          referencePosition = 1;
        } else if (pos === "הקודמת") {
          referenceType = "previous";
          referencePosition = 1;
        } else if (pos === "הראשונה") {
          referenceType = "specific";
          referencePosition = 1;
        } else if (pos === "השנייה") {
          referenceType = "specific";
          referencePosition = 2;
        } else if (pos === "השלישית") {
          referenceType = "specific";
          referencePosition = 3;
        } else if (pos === "הרביעית") {
          referenceType = "specific";
          referencePosition = 4;
        }
      }
    }

    // Check for continuity references
    for (const cont of this.referencePatterns.continuity) {
      if (query.includes(cont)) {
        // Higher confidence for content references like "התוכן", "את התוכן"
        // BUT only if there's no specific decision number in the query
        if (cont.includes("תוכן") && !/החלטה\s+\d+/.test(query)) {
          confidence += 0.6;  // Boost confidence to ensure detection
        } else {
          confidence += 0.3;
        }
        referenceType = referenceType || "context";
      }
    }

    // Check for temporal references
    for (const temp of this.referencePatterns.temporal) {
      if (query.includes(temp)) {
        confidence += 0.2;
        referenceType = referenceType || "context";
      }
    }

    // Check pattern matches
    for (const pattern of this.referencePatterns.patterns) {
      if (pattern.test(query)) {
        confidence += 0.4;
        referenceType = referenceType || "last";
        if (!referencePosition) referencePosition = 1;
      }
    }

    // Special case: "עוד" at start usually means reference
    if (query.startsWith("עוד ")) {
      confidence += 0.5;
      referenceType = referenceType || "context";
    }

    // Check for numbered references: "מספר X"
    const numberedRef = query.match(/מספר\s+(\d+)/);
    if (numberedRef && (query.includes("רשימה") || query.includes("ששלחת") || query.includes("שנתת"))) {
      confidence += 0.4;
      referenceType = "specific";
      referencePosition = parseInt(numberedRef[1]);
    }

    // Check for "בהמשך ל", "כמו שביקשתי", etc.
    if (query.includes("בהמשך ל") || query.includes("כמו שביקשתי") || query.includes("כפי שאמרתי")) {
      confidence += 0.4;
      referenceType = "context";
    }

    // Check for "מה ש" patterns
    if (query.includes("מה ששאלתי") || query.includes("מה שביקשתי")) {
      confidence += 0.4;
      referenceType = "context";
    }

    // Check for "חזור על" or "הצג שוב"
    if (query.includes("חזור על") || query.includes("הצג שוב")) {
      confidence += 0.4;
      referenceType = "last";
    }

    // Special handling for "השנייה ברשימה"
    if (query.includes("השנייה ברשימה")) {
      confidence += 0.5;
      referenceType = "specific";
      referencePosition = 2;
    }

    // Special handling for "התוצאות האחרונות"
    if (query.includes("התוצאות האחרונות")) {
      confidence += 0.4;
      referenceType = "last";
    }

    // Special handling for "עוד פרטים על ההחלטה הקודמת"
    if (query.includes("עוד פרטים על") && query.includes("הקודמת")) {
      confidence += 0.6;
      referenceType = "previous";
      referencePosition = 1;
    }

    // Check for standalone government number - likely clarification response
    if (/^ממשלה\s+\d+$/.test(query.trim()) || /^\d+$/.test(query.trim())) {
      confidence += 0.8;
      referenceType = "clarification";
      referencePosition = 1;
    }

    return {
      isReference: confidence >= 0.5,
      confidence: Math.min(confidence, 1.0),
      referenceType: referenceType || "context",
      referencePosition
    };
  }

  checkEval(query) {
    let confidence = 0;
    let hasDecisionNumber = false;

    // Check strict triggers
    for (const verb of this.evalPatterns.strict_triggers.verbs) {
      if (query.includes(verb)) {
        // Higher confidence if it's an analysis verb with content reference
        if ((verb === "נתח" || verb === "ניתוח") && 
            (query.includes("התוכן") || query.includes("את התוכן"))) {
          confidence += 0.8;  // High confidence for analysis + content reference
        } else {
          confidence += 0.4;
        }
      }
    }

    // Check patterns
    for (const pattern of this.evalPatterns.strict_triggers.patterns) {
      if (pattern.test(query)) {
        confidence += 0.5;
        hasDecisionNumber = true;
      }
    }

    // Check for decision number - multiple patterns
    let decisionMatch = /החלטה\s+(\d+)/.exec(query);
    if (!decisionMatch) {
      decisionMatch = /החלטה\s+מספר\s+(\d+)/.exec(query);
    }
    if (!decisionMatch) {
      decisionMatch = /החלטת\s+ממשלה\s+(\d+)/.exec(query);
    }
    if (!decisionMatch) {
      decisionMatch = /החלטת\s+הממשלה\s+(\d+)/.exec(query);
    }
    if (decisionMatch) {
      hasDecisionNumber = true;
      confidence += 0.4;
    }

    // Additional EVAL indicators
    if (query.includes("ניתוח מפורט") || query.includes("ניתוח מעמיק")) {
      confidence += 0.3;
    }

    if (query.includes("הסבר לעומק")) {
      confidence += 0.3;
      // Check if there's a decision number after this phrase
      const deepExplainMatch = /הסבר\s+לעומק\s+את\s+החלטה\s+(\d+)/.exec(query);
      if (deepExplainMatch) {
        hasDecisionNumber = true;
        confidence += 0.4;
      }
    }

    // Special case: "נתח את כל" should be QUERY, not EVAL
    if (query.includes("נתח את כל") || query.includes("ניתוח של כל")) {
      confidence = 0;
    }

    // If it starts with "תן לי ניתוח" and has decision number, it's EVAL
    if (query.includes("תן לי ניתוח") && hasDecisionNumber) {
      confidence += 0.3;
    }

    // Special handling for "ניתוח החלטת הממשלה X" - should be EVAL
    if (query.includes("ניתוח החלטת הממשלה") && hasDecisionNumber) {
      confidence += 0.4;
    }

    // Special handling for "נתח לי את" with decision number
    if (query.includes("נתח לי את") && hasDecisionNumber) {
      confidence += 0.3;
    }

    // Special handling for "נתח לעומק את" patterns
    if (query.includes("נתח לעומק את") && hasDecisionNumber) {
      confidence += 0.4;
    }

    // Special handling for simple "נתח את החלטה" patterns  
    if (query.includes("נתח את החלטה") && hasDecisionNumber) {
      confidence += 0.5; // High confidence for direct analysis requests
    }
    
    // Handle simple "נתח" commands that don't have decision numbers
    if (query.includes("נתח") && !query.includes("נתח את כל")) {
      confidence += 0.4; // Add confidence for analysis intent
    }

    // Allow EVAL for simple "נתח" without decision number
    const isSimpleAnalysis = query.includes("נתח") && !query.includes("נתח את כל") && confidence >= 0.4;
    
    return {
      isEval: (confidence >= 0.7 && hasDecisionNumber) || isSimpleAnalysis,
      confidence: Math.min(confidence, 1.0)
    };
  }

  checkQuery(query) {
    let confidence = 0;
    let operation = "search";

    // Check search triggers
    for (const prefix of this.queryPatterns.search_triggers.prefixes) {
      if (query.includes(prefix)) {
        confidence += 0.3;
      }
    }

    for (const pattern of this.queryPatterns.search_triggers.patterns) {
      if (pattern.test(query)) {
        confidence += 0.4;
      }
    }

    // Check statistical triggers
    for (const keyword of this.queryPatterns.statistical_triggers.keywords) {
      if (query.includes(keyword)) {
        confidence += 0.4;
        operation = "count";
      }
    }

    for (const pattern of this.queryPatterns.statistical_triggers.patterns) {
      if (pattern.test(query)) {
        confidence += 0.5;
        operation = "count";
      }
    }

    // Check comparison triggers
    for (const keyword of this.queryPatterns.comparison_triggers.keywords) {
      if (query.includes(keyword)) {
        confidence += 0.4;
        operation = "compare";
      }
    }

    for (const pattern of this.queryPatterns.comparison_triggers.patterns) {
      if (pattern.test(query)) {
        confidence += 0.5;
        operation = "compare";
      }
    }

    // General decision-related terms
    if (query.includes("החלטות") || query.includes("החלטה")) {
      confidence += 0.2;
    }

    if (query.includes("ממשלה")) {
      confidence += 0.2;
    }

    return {
      isQuery: confidence >= 0.5,
      confidence: Math.min(confidence, 1.0),
      operation
    };
  }

  checkClarification(query) {
    // Too short - but allow specific patterns
    const words = query.split(/\s+/);
    if (words.length < 3) {
      // Check if it's a valid short pattern like "החלטה 2983", "ממשלה 37", or contains dates
      const hasValidPattern = /החלטה\s+\d+/.test(query) || 
                            /ממשלה\s+\d+/.test(query) ||
                            /ב[־-]?\d{4}/.test(query) || // Year patterns like "ב-2020"
                            query.includes("השנה") ||
                            query.includes("החודש") ||
                            /משנת\s+\d{4}/.test(query);
      
      if (hasValidPattern) {
        return { needsClarification: false };
      }
      return { needsClarification: true, reason: "Query too short", priority: true };
    }

    // Vague patterns
    for (const pattern of this.clarificationPatterns.vague_patterns) {
      if (pattern.test(query)) {
        return { needsClarification: true, reason: "Too vague", priority: true };
      }
    }

    // Incomplete patterns - these have high priority
    for (const pattern of this.clarificationPatterns.incomplete_patterns) {
      if (pattern.test(query)) {
        return { needsClarification: true, reason: "Incomplete information", priority: true };
      }
    }

    // Check for ambiguous terms without context
    for (const ambiguous of this.clarificationPatterns.ambiguous) {
      if (query.includes(ambiguous) && query.split(/\s+/).length <= 3) {
        return { needsClarification: true, reason: "Ambiguous reference", priority: false };
      }
    }

    return { needsClarification: false };
  }

  extractEntities(query) {
    const entities = {};

    // Extract government number - but skip if it's part of "החלטת ממשלה X" pattern
    const govMatch = query.match(/ממשלה\s+(\d+)/);
    if (govMatch && !query.match(/החלטת\s+(ה)?ממשלה\s+(\d+)/)) {
      entities.government_number = parseInt(govMatch[1]);
    }
    
    // Check for "current government" references
    if (query.includes("הממשלה הנוכחית") || 
        query.includes("ממשלה נוכחית") || 
        query.includes("הממשלה הנוכחת") ||
        query.includes("ממשלה נוכחת")) {
      entities.government_number = 37; // Current government is 37
    }

    // Convert Hebrew numbers for government - check longer phrases first
    const hebrewNumbersSorted = Object.entries(this.hebrewNumbers)
      .sort((a, b) => b[0].length - a[0].length);
    
    for (const [hebrew, number] of hebrewNumbersSorted) {
      if (query.includes(`ממשלה ${hebrew}`)) {
        entities.government_number = number;
        break;
      }
    }

    // Extract decision number - multiple patterns
    let decisionMatch = query.match(/החלטה\s+(\d+)/);
    if (!decisionMatch) {
      decisionMatch = query.match(/החלטה\s+מספר\s+(\d+)/);
    }
    
    // Special handling for "החלטת ממשלה X" pattern
    let govDecisionMatch = query.match(/החלטת\s+ממשלה\s+(\d+)/);
    if (!govDecisionMatch) {
      govDecisionMatch = query.match(/החלטת\s+הממשלה\s+(\d+)/);
    }
    
    if (govDecisionMatch) {
      const number = parseInt(govDecisionMatch[1]);
      // Debug logging
      console.log(`[DEBUG] govDecisionMatch found: "${govDecisionMatch[0]}", number: ${number}`);
      
      // If number > 37, it's likely a decision number, not government number
      // Since current government is 37 and we don't have government 2767
      if (number > 37) {
        console.log(`[DEBUG] Number ${number} > 37, treating as decision number`);
        entities.decision_number = number;
        // Default to current government if not specified
        if (!entities.government_number) {
          entities.government_number = 37;
        }
      } else {
        // Number <= 37 could be either government or decision
        // Check if there's additional context
        const hasDecisionContext = query.includes("מספר") || 
                                 query.match(/החלטה\s+\d+\s+של\s+ממשלה/) ||
                                 query.includes("נתח") || query.includes("ניתח");
        
        if (hasDecisionContext) {
          // More likely to be a decision number
          entities.decision_number = number;
          if (!entities.government_number) {
            entities.government_number = 37;
          }
        } else {
          // Ambiguous case - flag it for clarification
          entities.ambiguous_number = number;
          entities._ambiguity_type = "government_or_decision";
        }
      }
    } else if (decisionMatch) {
      entities.decision_number = parseInt(decisionMatch[1]);
      
      // Only set government 37 if explicitly mentioned as "current government"
      // Otherwise let the query search across all governments
    }

    // Extract limit - various patterns
    let limitMatch = query.match(/^(\d+)\s+החלטות/);
    if (limitMatch) {
      entities.limit = parseInt(limitMatch[1]);
    }
    
    // "תראה לי X החלטות" pattern
    if (!entities.limit) {
      limitMatch = query.match(/תראה\s+לי\s+(\d+)\s+החלטות/);
      if (limitMatch) {
        entities.limit = parseInt(limitMatch[1]);
      }
    }
    
    // "תן לי X החלטות" pattern
    if (!entities.limit) {
      limitMatch = query.match(/תן\s+לי\s+(\d+)\s+החלטות/);
      if (limitMatch) {
        entities.limit = parseInt(limitMatch[1]);
      }
    }

    // Extract Hebrew limit numbers - check for standalone digits too
    const hebrewLimitsSorted = Object.entries(this.hebrewNumbers)
      .sort((a, b) => b[0].length - a[0].length);
    
    for (const [hebrew, number] of hebrewLimitsSorted) {
      if (query.match(new RegExp(`^${hebrew}\\s+החלטות`))) {
        entities.limit = number;
        break;
      }
      // Also check for "X החלטות" in middle of sentence
      if (query.match(new RegExp(`\\s${hebrew}\\s+החלטות`))) {
        entities.limit = number;
        break;
      }
    }

    // Extract standalone digit limits in middle of text
    if (!entities.limit) {
      const digitalLimitMatch = query.match(/(\d+)\s+ההחלטות/);
      if (digitalLimitMatch) {
        entities.limit = parseInt(digitalLimitMatch[1]);
      }
    }

    // Extract topic - simplified patterns that properly stop at Hebrew verbs and government references
    // Pattern 1: "בנושא [topic]" stopping at verbs or government references
    let topicMatch = query.match(/בנושא\s+(.+?)\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?|ממשלה\s+\d+|של\s+ממשלה)/);
    if (!topicMatch) {
      topicMatch = query.match(/בנושא\s+([א-ת\s]+?)(?:\s+מ[שאז]|\s+ב[יש]ן|\s+ש[אמעה]|\s+ב\d{4}|\s*$)/);
    }
    
    // Pattern 2: "על [topic]" stopping at verbs or government references  
    if (!topicMatch) {
      topicMatch = query.match(/על\s+(.+?)\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?|ממשלה\s+\d+|של\s+ממשלה)/);
    }
    if (!topicMatch) {
      topicMatch = query.match(/על\s+([א-ת\s]+?)(?:\s+מ[שאז]|\s+ב[יש]ן|\s+ש[אמעה]|\s+ב\d{4}|\s*$)/);
    }
    
    // Pattern 3: "בתחום [topic]" stopping at verbs or government references
    if (!topicMatch) {
      topicMatch = query.match(/בתחום\s+(.+?)\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?|ממשלה\s+\d+|של\s+ממשלה)/);
    }
    if (!topicMatch) {
      topicMatch = query.match(/בתחום\s+([א-ת\s]+?)(?:\s+מ[שאז]|\s+ב[יש]ן|\s+ש[אמעה]|\s+ב\d{4}|\s*$)/);
    }
    
    // Pattern 4: "החלטות [topic]" stopping at verbs or government references
    if (!topicMatch) {
      topicMatch = query.match(/החלטות\s+(.+?)\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?|ממשלה\s+\d+|של\s+ממשלה)/);
    }
    if (!topicMatch) {
      topicMatch = query.match(/החלטות\s+([א-ת]+)(?:\s+מ[שאז]|\s+ב[יש]ן|\s+ש[אמעה]|\s+ב\d{4}|\s*$)/);
    }
    
    // Topic in comparison patterns
    if (!topicMatch) {
      topicMatch = query.match(/החלטות\s+(.+?)\s+בין\s+\d+/);
    }
    if (!topicMatch) {
      topicMatch = query.match(/החלטות\s+(.+?)\s+ב[־-]\d+/);
    }
    if (!topicMatch) {
      topicMatch = query.match(/השווה\s+החלטות\s+(.+?)\s+בין/);
    }
    
    if (topicMatch) {
      const extractedTopic = this.cleanTopicFromGovernmentReferences(topicMatch[1].trim());
      // Special case: "האחרונות" should not be treated as a topic but as "most recent"
      if (extractedTopic !== "האחרונות" && extractedTopic !== "אחרונות") {
        entities.topic = extractedTopic;
      }
    }
    
    // Special case: extract topic from "החלטות X" pattern - but stop at government references
    if (!entities.topic) {
      const simpleTopicMatch = query.match(/החלטות\s+(.+?)(?:\s+ממשלה|\s+בממשל|\s+קיבלה?|\s+ב[יש]ן|\s+מ[שאז]|\s*$)/);
      if (simpleTopicMatch && 
          !simpleTopicMatch[1].match(/^(ממשלה|של|משרד|על|בנושא|היו|היה|יש|בשנת)$/) &&
          !simpleTopicMatch[1].match(/^ממשלה\s+\d+$/) &&
          !simpleTopicMatch[1].match(/^ממשלה\s+היו/) &&
          !simpleTopicMatch[1].match(/היו\s+בממשל/)) {  // Don't treat "היו בממשלה" as topic
        const extractedTopic = this.cleanTopicFromGovernmentReferences(simpleTopicMatch[1].trim());
        // Special case: "האחרונות" should not be treated as a topic but as "most recent"
        if (extractedTopic !== "האחרונות" && extractedTopic !== "אחרונות") {
          entities.topic = extractedTopic;
        }
      }
    }

    // Extract ministries - avoid duplicates
    const ministries = new Set();
    for (const [short, full] of Object.entries(this.ministryMapping)) {
      if (query.includes(short)) {
        ministries.add(full);
      } else if (query.includes(full)) {
        ministries.add(full);
      }
    }
    if (ministries.size > 0) {
      entities.ministries = Array.from(ministries);
    }

    // Extract date ranges
    const dateRange = this.extractDateRange(query);
    console.log(`[DEBUG] extractDateRange for query "${query}" returned:`, dateRange);
    if (dateRange) {
      entities.date_range = dateRange;
    }

    // Extract comparison targets - improved patterns
    if (query.includes("השווה") || query.includes("השוואה") || query.includes("ההבדל")) {
      let compMatch = query.match(/ממשלה\s+(\d+)\s+לעומת\s+(\d+)/);
      if (!compMatch) {
        compMatch = query.match(/ממשלה\s+(\d+)\s+לממשלה\s+(\d+)/);
      }
      if (!compMatch) {
        compMatch = query.match(/בין\s+ממשלה\s+(\d+)\s+ל(?:ממשלה\s+)?(\d+)/);
      }
      if (!compMatch) {
        // Check for "ממשלה X ו-Y" pattern
        compMatch = query.match(/ממשלה\s+(\d+)\s+ו[־-]?(\d+)/);
      }
      if (!compMatch) {
        // Check for "ממשלות X ו-Y" pattern
        compMatch = query.match(/ממשלות\s+(\d+)\s+ו[־-]?(\d+)/);
      }
      
      // Check for Hebrew numbers in comparison
      if (!compMatch) {
        // Check for Hebrew numbers with digital numbers: "ממשלה שלושים לממשלה ארבעים"
        const hebrewCompMatch = query.match(/ממשלה\s+([א-ת\s]+?)\s+ל(?:ממשלה\s+)?([א-ת\s]+)/);
        if (hebrewCompMatch) {
          const num1 = this.parseHebrewNumber(hebrewCompMatch[1].trim());
          const num2 = this.parseHebrewNumber(hebrewCompMatch[2].trim());
          if (num1 && num2) {
            entities.comparison_target = `governments:${num1},${num2}`;
          }
        }
      }
      
      // Check for "בין ממשלה Hebrew ו-Hebrew" pattern
      if (!compMatch && !entities.comparison_target) {
        const betweenHebrewMatch = query.match(/בין\s+ממשלה\s+([א-ת\s]+?)\s+ו[־-]?([א-ת\s]+)/);
        if (betweenHebrewMatch) {
          const num1 = this.parseHebrewNumber(betweenHebrewMatch[1].trim());
          const num2 = this.parseHebrewNumber(betweenHebrewMatch[2].trim());
          if (num1 && num2) {
            entities.comparison_target = `governments:${num1},${num2}`;
          }
        }
      }
      
      if (compMatch && !entities.comparison_target) {
        entities.comparison_target = `governments:${compMatch[1]},${compMatch[2]}`;
      }
    }

    // Check for operational decisions
    if (query.includes("אופרטיביות") || query.includes("אופרטיבי") || 
        query.includes("אופרטיביים") || query.includes("אופרטיבית")) {
      entities.decision_type = "אופרטיבית";
      console.log("DEBUG: Operational decision detected, added decision_type:", entities.decision_type);
    }

    return entities;
  }

  extractDateRange(query) {
    const currentYear = new Date().getFullYear();
    
    // Relative dates
    if (query.includes("השנה")) {
      return {
        start: `${currentYear}-01-01`,
        end: `${currentYear}-12-31`
      };
    }

    if (query.includes("החודש")) {
      const now = new Date();
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      return {
        start: start.toISOString().split('T')[0],
        end: end.toISOString().split('T')[0]
      };
    }

    // "משנת X והלאה" pattern
    const fromYearMatch = query.match(/משנת\s+(\d{4})\s+והלאה/);
    if (fromYearMatch) {
      return {
        start: `${fromYearMatch[1]}-01-01`,
        end: `${currentYear + 5}-12-31` // 5 years into future as reasonable limit
      };
    }

    // "מאז X" pattern
    const sinceMatch = query.match(/מאז\s+(\d{4})/);
    if (sinceMatch) {
      return {
        start: `${sinceMatch[1]}-01-01`,
        end: `${currentYear}-12-31`
      };
    }

    // "בשנת YYYY" pattern
    const inYearMatch2 = query.match(/בשנת\s+(\d{4})/);
    if (inYearMatch2) {
      return {
        start: `${inYearMatch2[1]}-01-01`,
        end: `${inYearMatch2[1]}-12-31`
      };
    }
    
    // "ב-YYYY" pattern
    const inYearMatch = query.match(/ב[־-]?(\d{4})/);
    if (inYearMatch) {
      return {
        start: `${inYearMatch[1]}-01-01`,
        end: `${inYearMatch[1]}-12-31`
      };
    }
    
    // "הוחלטו ב-YYYY" or similar patterns
    const decisionYearMatch = query.match(/הוחלטו\s+ב[־-]?(\d{4})/);
    if (decisionYearMatch) {
      return {
        start: `${decisionYearMatch[1]}-01-01`,
        end: `${decisionYearMatch[1]}-12-31`
      };
    }

    // "בין YYYY-YYYY" pattern (years only)
    const yearRangeMatch = query.match(/בין\s+(\d{4})[־-](\d{4})/);
    if (yearRangeMatch) {
      return {
        start: `${yearRangeMatch[1]}-01-01`,
        end: `${yearRangeMatch[2]}-12-31`
      };
    }
    
    // "בין YYYY ל-YYYY" pattern - handle Hebrew maqaf (־), hyphen (-), and en-dash (–)
    const yearRangeMatch2 = query.match(/בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/);
    console.log(`[DEBUG] Testing pattern /בין\\s+(\\d{4})\\s+ל[־\\-–]?\\s*(\\d{4})/ against "${query}":`, yearRangeMatch2);
    if (yearRangeMatch2) {
      return {
        start: `${yearRangeMatch2[1]}-01-01`,
        end: `${yearRangeMatch2[2]}-12-31`
      };
    }
    
    // "בין YYYY ל YYYY" pattern - without any hyphen
    const yearRangeMatch3 = query.match(/בין\s+(\d{4})\s+ל\s+(\d{4})/);
    if (yearRangeMatch3) {
      return {
        start: `${yearRangeMatch3[1]}-01-01`,
        end: `${yearRangeMatch3[2]}-12-31`
      };
    }
    
    // "משנת YYYY" pattern
    const fromYearSimple = query.match(/משנת\s+(\d{4})(?!\s+והלאה)/);
    if (fromYearSimple) {
      return {
        start: `${fromYearSimple[1]}-01-01`,
        end: `${fromYearSimple[1]}-12-31`
      };
    }

    // Month-year patterns
    for (const [monthName, monthNum] of Object.entries(this.monthNames)) {
      const monthYearPattern = new RegExp(`${monthName}\\s+(\\d{4})`);
      const match = query.match(monthYearPattern);
      if (match) {
        const year = parseInt(match[1]);
        const lastDay = new Date(year, monthNum, 0).getDate();
        return {
          start: `${year}-${monthNum.toString().padStart(2, '0')}-01`,
          end: `${year}-${monthNum.toString().padStart(2, '0')}-${lastDay}`
        };
      }
    }

    // Date range patterns - multiple formats
    let rangeMatch = query.match(/(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\s+ל[בין]*\s*(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})/);
    if (!rangeMatch) {
      // Try "בין X ל-Y" format
      rangeMatch = query.match(/בין\s+(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\s+ל-?(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})/);
    }
    if (rangeMatch) {
      const startYear = rangeMatch[3].length === 2 ? 2000 + parseInt(rangeMatch[3]) : parseInt(rangeMatch[3]);
      const endYear = rangeMatch[6].length === 2 ? 2000 + parseInt(rangeMatch[6]) : parseInt(rangeMatch[6]);
      
      return {
        start: `${startYear}-${rangeMatch[2].padStart(2, '0')}-${rangeMatch[1].padStart(2, '0')}`,
        end: `${endYear}-${rangeMatch[5].padStart(2, '0')}-${rangeMatch[4].padStart(2, '0')}`
      };
    }

    return null;
  }

  parseHebrewNumber(hebrewText) {
    // Check if the text contains Hebrew numbers
    const words = hebrewText.split(/\s+/);
    for (const word of words) {
      if (this.hebrewNumbers[word]) {
        return this.hebrewNumbers[word];
      }
    }
    
    // Check for compound numbers like "שלושים ושלוש"
    const hebrewNumbersSorted = Object.entries(this.hebrewNumbers)
      .sort((a, b) => b[0].length - a[0].length);
    
    for (const [hebrew, number] of hebrewNumbersSorted) {
      if (hebrewText.includes(hebrew)) {
        return number;
      }
    }
    
    return null;
  }

  clarificationResult(reason, entities = {}) {
    // Provide more informative clarification messages based on the ambiguity
    let clarificationMessage = reason;
    
    // Check if this is an ambiguous government/decision number case
    if (reason === "Ambiguous number reference") {
      if (entities.ambiguous_number) {
        const num = entities.ambiguous_number;
        if (num <= 37) {
          clarificationMessage = `המספר ${num} יכול להתייחס למספר ממשלה או למספר החלטה. אנא הבהר:\n` +
            `- "החלטה ${num} של ממשלה 37" - אם התכוונת להחלטה מספר ${num}\n` +
            `- "החלטות ממשלה ${num}" - אם התכוונת לממשלה מספר ${num}`;
        }
      }
    }
    
    return {
      intent_type: "CLARIFICATION",
      entities: entities,
      confidence: 0.3,
      route_flags: {
        needs_context: false,
        is_statistical: false,
        is_comparison: false
      },
      explanation: clarificationMessage
    };
  }

  cleanTopicFromGovernmentReferences(topic) {
    if (!topic) return topic;
    
    // Remove government references and Hebrew verbs that indicate end of topic
    let cleaned = topic
      // Remove "ממשלה X" patterns
      .replace(/\s+ממשלה\s+\d+.*$/, '')
      .replace(/\s+של\s+ממשלה.*$/, '')
      // Remove Hebrew verbs that indicate end of topic
      .replace(/\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?).*$/, '')
      // Remove other stopping patterns
      .replace(/\s+(?:היו|ש?היה|נעשה|נעשו).*$/, '')
      .trim();
    
    // Remove common prefixes
    cleaned = cleaned
      .replace(/^בנושא\s+/, '')
      .replace(/^על\s+/, '')
      .replace(/^בתחום\s+/, '')
      .replace(/^לגבי\s+/, '')
      .trim();
    
    // Normalize using topic mapping if available
    if (this.topicMapping[cleaned]) {
      cleaned = this.topicMapping[cleaned];
    }
    
    // Additional cleanup - remove articles and prepositions at the end
    cleaned = cleaned
      .replace(/\s+(ה|את|של|על|ב|מ|ל)$/, '')
      .trim();
    
    return cleaned;
  }

  normalizeHebrewTopic(topic) {
    if (!topic) return topic;
    
    // Check direct mapping first
    if (this.topicMapping[topic]) {
      return this.topicMapping[topic];
    }
    
    // Try fuzzy matching for partial matches
    const topicLower = topic.toLowerCase();
    for (const [variation, normalized] of Object.entries(this.topicMapping)) {
      if (topicLower.includes(variation.toLowerCase()) || variation.toLowerCase().includes(topicLower)) {
        return normalized;
      }
    }
    
    return topic;
  }
}

// CommonJS export
module.exports = IntentDetector;
