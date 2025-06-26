/**
 * Natural Language to SQL Converter
 * Converts Hebrew natural language queries to SQL
 */

import OpenAI from 'openai';
import { DECISIONS_SCHEMA, getHebrewColumnNames } from './schema';
import { findMatchingTemplate } from './queryTemplates';

export interface SQLConversion {
  sql: string;
  params: any[];
  expectedType: 'single' | 'multiple' | 'count' | 'aggregate';
  explanation: string;
  templateUsed?: string;
  confidence: number;
}

export class NLToSQLConverter {
  private openai: OpenAI;
  
  constructor() {
    this.openai = new OpenAI({ 
      apiKey: process.env.OPENAI_API_KEY 
    });
  }

  async convertToSQL(naturalQuery: string): Promise<SQLConversion> {
    console.log('[NLToSQL] Converting query:', naturalQuery);
    
    // Step 1: Normalize the query for better matching
    const normalizedQuery = this.normalizeQuery(naturalQuery);
    console.log('[NLToSQL] Normalized query:', normalizedQuery);
    
    // Step 2: Try pattern matching for common queries
    const templateResult = this.tryTemplateMatch(normalizedQuery);
    if (templateResult) {
      console.log('[NLToSQL] Matched template:', templateResult.templateUsed);
      return templateResult;
    }

    // Step 3: Try fuzzy template matching
    const fuzzyTemplateResult = this.tryFuzzyTemplateMatch(normalizedQuery);
    if (fuzzyTemplateResult) {
      console.log('[NLToSQL] Fuzzy matched template:', fuzzyTemplateResult.templateUsed);
      return fuzzyTemplateResult;
    }

    // Step 4: If no template matches, use GPT for conversion
    console.log('[NLToSQL] No template match, using GPT');
    return await this.convertWithGPT(normalizedQuery);
  }

  private normalizeQuery(query: string): string {
    // Normalize common variations
    let normalized = query
      .replace(/\s+/g, ' ') // Multiple spaces to single
      .trim()
      // Normalize variations of "החלטה אחת"
      .replace(/^(תן\s+לי\s+|הבא\s+לי\s+|הבא\s+|תן\s+)?החלטה\s+בנושא/, 'החלטה אחת בנושא')
      .replace(/^החלטה\s+מ/, 'החלטה אחת מ')
      // Normalize year patterns
      .replace(/משנת\s+(\d{4})/, 'מ$1')
      .replace(/בשנת\s+(\d{4})/, 'מ$1')
      // Normalize "הצג" variations
      .replace(/^(תציג|הצג\s+לי|הראה\s+לי)\s+/, 'הבא ')
      // Fix edge case: "1 החלטות" -> "החלטה אחת"
      .replace(/^1\s+החלטות/, 'החלטה אחת')
      // Don't normalize topics - let SQL handle partial matching
      // But add smart mapping for common mismatches
      .replace(/איכות\s+הסביבה/, 'סביבה')
      .replace(/מדע/, 'מחקר')
      .replace(/פנסיה/, 'ותיקים')
      .replace(/קורונה/, 'בריאות')
      ;
      
    return normalized;
  }

  private tryFuzzyTemplateMatch(query: string): SQLConversion | null {
    // Try to match "החלטה אחת בנושא X מYYYY" pattern more flexibly
    const singleDecisionPattern = /(?:החלטה\s+אחת|החלטה)\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+מ(\d{4})/;
    const match = query.match(singleDecisionPattern);
    
    if (match) {
      const [, topic, year] = match;
      return {
        sql: `
          SELECT * FROM israeli_government_decisions 
          WHERE tags_policy_area ILIKE $1
          AND EXTRACT(YEAR FROM decision_date) = $2
          ORDER BY decision_date DESC
          LIMIT 1
        `,
        params: [`%${topic.trim()}%`, parseInt(year)],
        expectedType: 'single',
        explanation: `מחפש החלטה אחת בנושא ${topic} משנת ${year}`,
        templateUsed: 'FUZZY_SINGLE_DECISION_BY_TOPIC_AND_YEAR',
        confidence: 0.9
      };
    }
    
    return null;
  }

  private tryTemplateMatch(query: string): SQLConversion | null {
    const matchResult = findMatchingTemplate(query);
    
    if (matchResult) {
      const { template, matches } = matchResult;
      
      return {
        sql: template.sql(...matches),
        params: template.params(...matches),
        expectedType: template.expectedType,
        explanation: `שאילתה מסוג: ${template.name}`,
        templateUsed: template.name,
        confidence: 0.95
      };
    }
    
    return null;
  }

  private async convertWithGPT(naturalQuery: string): Promise<SQLConversion> {
    const systemPrompt = this.buildSystemPrompt();
    const userPrompt = this.buildUserPrompt(naturalQuery);
    
    try {
      const response = await this.openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        temperature: 0.1,
        max_tokens: 500,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0].message.content;
      if (!content) {
        throw new Error('No response from GPT');
      }

      const result = JSON.parse(content);
      return {
        sql: result.sql,
        params: result.params || [],
        expectedType: result.expected_type || 'multiple',
        explanation: result.explanation || 'שאילתה מותאמת אישית',
        confidence: result.confidence || 0.8
      };
    } catch (error) {
      console.error('[NLToSQL] GPT conversion error:', error);
      throw new Error(`Failed to convert query: ${(error as Error).message}`);
    }
  }

  private buildSystemPrompt(): string {
    return `You are a SQL query generator for Israeli government decisions database.
    
Schema:
Table: israeli_government_decisions

Columns:
${DECISIONS_SCHEMA.columns.map(col => 
  `- ${col.name} (${col.type}): ${col.description}${col.current_value ? ` [Current: ${col.current_value}]` : ''}`
).join('\n')}

AVAILABLE POLICY TAGS (tags_policy_area):
ביטחון לאומי וצה״ל
ביטחון פנים וחירום אזרחי
דיפלומטיה ויחסים בינ״ל
הגירה וקליטת עלייה
תעסוקה ושוק העבודה
כלכלה מאקרו ותקציב
פיננסים, ביטוח ומסים
פיתוח כלכלי ותחרות
יוקר המחיה ושוק הצרכן
תחבורה ציבורית ותשתיות דרך
בטיחות בדרכים ורכב
אנרגיה
מים ותשתיות מים
סביבה, אקלים ומגוון ביולוגי
רשות הטבע והגנים ונוף
חקלאות ופיתוח הכפר
דיור, נדל״ן ותכנון
שלטון מקומי ופיתוח פריפריה
בריאות ורפואה
רווחה ושירותים חברתיים
אזרחים ותיקים
שוויון חברתי וזכויות אדם
מיעוטים ואוכלוסיות ייחודיות
מילואים ותמיכה בלוחמים
חינוך
השכלה גבוהה ומחקר
תרבות ואמנות
ספורט ואורח חיים פעיל
מורשת ולאום
תיירות ופנאי
דת ומוסדות דת
טכנולוגיה, חדשנות ודיגיטל
סייבר ואבטחת מידע
תקשורת ומדיה
משפט, חקיקה ורגולציה

IMPORTANT RULES FOR TOPIC SEARCH:
1. User queries often don't match tags exactly. Use smart partial matching:
   - "איכות הסביבה" → search for "%סביבה%"
   - "מדע" → search for "%מחקר%" or "%טכנולוגיה%"
   - "פנסיה" → search for "%ותיקים%" or "%רווחה%"
   - "קורונה" → search for "%בריאות%" or "%חירום%"
   - "בריאות הציבור" → search for "%בריאות%"
   - "חינוך מיוחד" → search for "%חינוך%"
   - "ביטחון פנים" → search for "%ביטחון פנים%"

2. For broader matches, search for the most significant word:
   - Don't search for full phrases if partial match is better
   - Focus on the main topic word

Important Rules:
1. ALWAYS use parameterized queries with $1, $2, etc.
2. For Hebrew text search use ILIKE with % wildcards
3. decision_number is TEXT, not INTEGER - use string comparison
4. government_number is TEXT (e.g., "37.0") - ALWAYS compare as TEXT: government_number = '37' OR government_number = '37.0'
5. Current government is 37 (stored as "37" or "37.0")
6. Decision numbers reset each government - ALWAYS filter by government_number
7. Always limit results unless counting (default LIMIT 10, but respect specific numbers requested by user)
8. Order by decision_date DESC for recent results
9. Use valid PostgreSQL syntax
10. For single decision requests, use LIMIT 1
11. Tags are separated by semicolon (;)
12. NEVER use government_number = 37 (integer), ALWAYS use government_number = '37' (string)

Common Patterns:
- Single decision: WHERE decision_number = $1 AND (government_number = $2 OR government_number = $2 || '.0')
- Topic search: WHERE tags_policy_area ILIKE $1
- Count: SELECT COUNT(*) as count
- Date range: WHERE decision_date BETWEEN $1 AND $2
- Recent: ORDER BY decision_date DESC LIMIT 10
- Government filter: WHERE (government_number = '37' OR government_number = '37.0')
- IMPORTANT: When adding government_number = 37, use string '37' not integer 37

Response format (JSON):
{
  "sql": "SELECT ... FROM ... WHERE ...",
  "params": ["param1", "param2"],
  "expected_type": "single|multiple|count|aggregate",
  "explanation": "Hebrew explanation of what the query does",
  "confidence": 0.0-1.0
}`;
  }

  private buildUserPrompt(query: string): string {
    // Add context about Hebrew column mappings
    const hebrewMappings = getHebrewColumnNames();
    
    return `Convert this Hebrew query to SQL: "${query}"

Hebrew to English column mappings:
${Object.entries(hebrewMappings)
  .filter(([hebrew, _]) => /[\u0590-\u05FF]/.test(hebrew))
  .map(([hebrew, english]) => `- ${hebrew} → ${english}`)
  .join('\n')}

Remember:
- If asking for one decision ("החלטה" or "החלטה אחת"), use LIMIT 1
- If asking for multiple ("החלטות"), use appropriate LIMIT
- If asking for specific number (e.g., "20 החלטות"), use LIMIT 20
- If counting ("כמה"), use COUNT(*)
- If no government specified, use current (37)
- Decision numbers need government context
- For year-based queries, use EXTRACT(YEAR FROM decision_date) = year_number
- When searching by topic AND year, combine both conditions
- Contextual queries like "וב2021?" refer to previous context
- For partial topic matches, use ILIKE with wildcards (e.g., "%בריאות%" will match "בריאות ורפואה")
- For compound topics like "חינוך מיוחד", search for the full phrase
- Use broader search when exact topic doesn't exist (e.g., "מדע" → search in "השכלה גבוהה ומחקר")
- Topic mapping hints:
  * "איכות הסביבה" → "סביבה, אקלים ומגוון ביולוגי"
  * "מדע" → "השכלה גבוהה ומחקר" or "טכנולוגיה, חדשנות ודיגיטל"
  * "פנסיה" → "אזרחים ותיקים" or "רווחה ושירותים חברתיים"
  * "קורונה" → "בריאות ורפואה" or "חירום אזרחי"
  * "בריאות הציבור" → "בריאות ורפואה"
  * "חינוך מיוחד" → "חינוך"
  * "ביטחון פנים" → "ביטחון פנים וחירום אזרחי"
- Always use ILIKE with % wildcards for flexible matching
- Normalize query variations: "תן לי החלטה" = "החלטה אחת" = "הבא החלטה"`;
  }

  // Validation method
  validateSQL(sql: string): boolean {
    // Basic SQL injection prevention
    const dangerousPatterns = [
      /;\s*DROP/i,
      /;\s*DELETE/i,
      /;\s*UPDATE/i,
      /;\s*INSERT/i,
      /;\s*ALTER/i,
      /;\s*CREATE/i,
      /--/,
      /\/\*/
    ];
    
    return !dangerousPatterns.some(pattern => pattern.test(sql));
  }

  // Helper to extract entities from query
  extractEntities(query: string): {
    decisionNumber?: string;
    governmentNumber?: number;
    year?: number;
    topic?: string;
  } {
    const entities: any = {};
    
    // Extract decision number
    const decisionMatch = query.match(/החלטה\s*(?:מספר\s*)?(\d+)/);
    if (decisionMatch) {
      entities.decisionNumber = decisionMatch[1];
    }
    
    // Extract government number
    const govMatch = query.match(/ממשלה\s*(\d+)/);
    if (govMatch) {
      entities.governmentNumber = parseInt(govMatch[1]);
    }
    
    // Extract year
    const yearMatch = query.match(/(?:משנת|בשנת)\s*(\d{4})/);
    if (yearMatch) {
      entities.year = parseInt(yearMatch[1]);
    }
    
    // Extract topic
    const topicMatch = query.match(/בנושא\s+([\u0590-\u05FF\s]+?)(?:\s*מ\d{4}|\s*משנת|\s*של|\s*$)/);
    if (topicMatch) {
      entities.topic = topicMatch[1].trim();
    }
    
    return entities;
  }
}
