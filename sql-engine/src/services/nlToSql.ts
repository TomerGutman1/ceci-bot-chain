/**
 * Natural Language to SQL Converter
 * Converts Hebrew natural language queries to SQL
 */

import OpenAI from 'openai';
import { DECISIONS_SCHEMA, getHebrewColumnNames } from './schema';
import { findMatchingTemplate } from './queryTemplates';
import { findBestMatchingTag, getTopicSearchCondition, POLICY_TAGS } from '../utils/fuzzyMatcher';
import { normalizeDateString, extractDateRange } from '../utils/dateNormalizer';
import { ExtractedEntities } from './types';

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
    
    // Step 0: Check for unclear/vague queries
    if (this.isUnclearQuery(naturalQuery)) {
      console.log('[NLToSQL] Query is unclear/vague, returning guidance');
      return {
        sql: 'SELECT decision_number, decision_title, decision_date FROM israeli_government_decisions LIMIT 0',
        params: [],
        expectedType: 'multiple',
        explanation: '❏ לא הבנתי את השאלה. נסה למשל:\n   • החלטות בנושא חינוך משנת 2022\n   • החלטה 660 של ממשלה 35\n   • כמה החלטות יש בנושא בריאות?',
        templateUsed: 'UNCLEAR_QUERY',
        confidence: 0.2
      };
    }
    
    // Step 1: Use GPT to extract and normalize parameters FIRST
    const extractedParams = await this.extractParametersWithGPT(naturalQuery);
    console.log('[NLToSQL] Extracted parameters:', extractedParams);
    
    // Step 2: Create normalized query based on extracted parameters
    const normalizedQuery = this.buildNormalizedQuery(naturalQuery, extractedParams);
    console.log('[NLToSQL] Normalized query:', normalizedQuery);
    
    // Step 3: Try pattern matching for common queries
    const templateResult = this.tryTemplateMatch(normalizedQuery, extractedParams);
    if (templateResult) {
      console.log('[NLToSQL] Matched template:', templateResult.templateUsed);
      return templateResult;
    }

    // Step 4: Try fuzzy template matching
    const fuzzyTemplateResult = this.tryFuzzyTemplateMatch(normalizedQuery, extractedParams);
    if (fuzzyTemplateResult) {
      console.log('[NLToSQL] Fuzzy matched template:', fuzzyTemplateResult.templateUsed);
      return fuzzyTemplateResult;
    }

    // Step 5: If no template matches, use GPT for conversion
    console.log('[NLToSQL] No template match, using GPT with extracted params');
    return await this.convertWithGPT(naturalQuery, extractedParams);
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
      // Normalize date patterns for "since" queries
      .replace(/מאז\s+ה-?(\d)/, 'מאז ה-$1')
      .replace(/החל\s+מ-?(\d)/, 'החל מ-$1');
      
    // Enhanced topic normalization using fuzzy matcher
    const topicMatch = normalized.match(/בנושא\s+([\u0590-\u05FF\s]+?)(?:\s*מ\d{4}|\s*משנת|\s*של|\s*$)/);
    if (topicMatch) {
      const topic = topicMatch[1].trim();
      const bestTag = findBestMatchingTag(topic);
      if (bestTag && bestTag !== topic) {
        console.log(`[NLToSQL] Fuzzy matched topic: "${topic}" → "${bestTag}"`);
        normalized = normalized.replace(topic, bestTag);
      }
    }
    
    // Normalize dates using date normalizer - ENHANCED
    // Look for date patterns and normalize them
    const datePatterns = [
      /(\d{1,2}\/\d{1,2}\/\d{4})/g,  // DD/MM/YYYY
      /(\d{1,2}\.\d{1,2}\.\d{4})/g,  // DD.MM.YYYY
      /(\d{1,2}-\d{1,2}-\d{4})/g,     // DD-MM-YYYY
      // Add patterns for dates with context
      /(?:מאז|החל מ-?|מ-)\s*(?:ה-)?(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})/g
    ];
    
    // First normalize standalone dates
    for (const pattern of datePatterns.slice(0, 3)) {
      normalized = normalized.replace(pattern, (match) => {
        const normalizedDate = normalizeDateString(match);
        if (normalizedDate) {
          console.log(`[NLToSQL] Normalized date: ${match} → ${normalizedDate}`);
          return normalizedDate;
        }
        return match;
      });
    }
    
    // Then normalize dates with context (מאז, החל מ-, etc.)
    normalized = normalized.replace(/(?:מאז|החל מ-?|מ-)\s*(?:ה-)?(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})/g, (match, dateStr) => {
      const normalizedDate = normalizeDateString(dateStr);
      if (normalizedDate) {
        console.log(`[NLToSQL] Normalized date in context: ${match} → מאז ${normalizedDate}`);
        return match.replace(dateStr, normalizedDate);
      }
      return match;
    })
    
    // Extract date range for logging
    const dateRange = extractDateRange(normalized);
    if (dateRange.startDate) {
      console.log(`[NLToSQL] Extracted date range:`, dateRange);
    }
      
    return normalized;
  }

  private tryFuzzyTemplateMatch(query: string, extractedParams?: any): SQLConversion | null {
    // Try to match "החלטה אחת בנושא X מYYYY" pattern more flexibly
    const singleDecisionPattern = /(?:החלטה\s+אחת|החלטה)\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+מ(\d{4})/;
    const match = query.match(singleDecisionPattern);
    
    if (match) {
      const [, topic, year] = match;
      // Use fuzzy matcher to get the best SQL condition
      const topicCondition = getTopicSearchCondition(topic.trim(), 1);
      
      return {
        sql: `
          SELECT * FROM israeli_government_decisions 
          WHERE ${topicCondition.sql}
          AND EXTRACT(YEAR FROM decision_date) = $2
          ORDER BY decision_date DESC
          LIMIT 1
        `,
        params: [topicCondition.param, parseInt(year)],
        expectedType: 'single',
        explanation: `מחפש החלטה אחת בנושא ${topic} משנת ${year}`,
        templateUsed: 'FUZZY_SINGLE_DECISION_BY_TOPIC_AND_YEAR',
        confidence: 0.9
      };
    }
    
    return null;
  }

  private tryTemplateMatch(query: string, extractedParams?: any): SQLConversion | null {
    const matchResult = findMatchingTemplate(query);
    
    if (matchResult) {
      const { template, matches } = matchResult;
      
      // Special handling for date-based templates
      if (template.name.includes('SINCE_DATE') && extractedParams?.date_from) {
        // For templates expecting date + topic, we need to inject the normalized date
        if (template.name === 'DECISIONS_SINCE_DATE_BY_TOPIC') {
          // Extract topic from the query
          const topicMatch = query.match(/(?:שעוסקות|שקשורות|בנושא)\s+(?:ב|ל)?([֐-׿\s]+)/);
          if (topicMatch) {
            const topic = topicMatch[1].trim();
            return {
              sql: `
                SELECT * FROM israeli_government_decisions 
                WHERE decision_date >= $1
                AND (tags_policy_area ILIKE $2 
                     OR summary ILIKE $3 
                     OR decision_content ILIKE $4
                     OR decision_title ILIKE $5)
                ORDER BY decision_date DESC
              `,
              params: [
                extractedParams.date_from,
                `%${topic}%`,
                `%${topic}%`,
                `%${topic}%`,
                `%${topic}%`
              ],
              expectedType: 'multiple',
              explanation: `מחפש החלטות מאז ${extractedParams.date_from} בנושא ${topic}`,
              templateUsed: template.name,
              confidence: 0.95
            };
          }
        }
      }
      
      // Default template handling
      const result = {
        sql: template.sql(...matches),
        params: template.params(...matches),
        expectedType: template.expectedType,
        explanation: `שאילתה מסוג: ${template.name}`,
        templateUsed: template.name,
        confidence: 0.95
      };
      
      return result;
    }
    
    return null;
  }

  // New method to extract parameters using GPT - ENHANCED WITH FULL PARAMETER MAP
  private async extractParametersWithGPT(query: string): Promise<any> {
    const prompt = `Extract parameters from this Hebrew query. Return a FLAT JSON object with these exact keys:

Query: "${query}"

PARAMETER EXTRACTION RULES:

1. TIME:
   - date_from: "מאז X", "החל מ-X", "מ-X" → "YYYY-MM-DD"
   - date_to: "עד X", "לפני X" → "YYYY-MM-DD"
   - year_exact: "בשנת X", "משנת X" → number
   - relative_period: "בחצי השנה האחרונה", "בחודשיים האחרונים" → string

2. TOPIC:
   - tags_policy_area: Official tag if matches (e.g., "חינוך", "בריאות")
   - topic_free: Any topic not in official tags
   - topic: General topic extracted - EXTRACT ONLY THE KEY TOPIC, not the full query
     Examples: 
     * "החלטות על מיעוטים" → topic: "מיעוטים"
     * "החלטות בנושא החברה הערבית" → topic: "החברה הערבית"

3. GOVERNMENT:
   - government_number: "ממשלה X" → string "X"
   - prime_minister: "של X", "בתקופת X" → name
   - committee: "ועדת X" → committee name

4. LOCATION:
   - tags_location: "בירושלים", "בגליל" → location
   - region_type: "בצפון", "בדרום" → region

5. QUANTITY:
   - count_only: "כמה" → true
   - limit: "X החלטות", "הבא X" → number
   - single_result: "החלטה אחת" → true

6. CONTENT:
   - full_text_query: "שמכילות X" → search term
   - operativity_filter: "אופרטיביות" → "אופרטיבי"
   - decision_number: "החלטה X" → string "X"
   - urgency_level: "דחופות" → "דחוף"

7. DISPLAY:
   - fields_subset: "רק כותרות" → "כותרות"
   - order_by: "הכי חדשות" → "decision_date DESC"

8. CONTEXT:
   - clarification_needed: Very short query → true
   - follow_up_ref: "וב-2021?" → true

EXAMPLES:
- "החלטות מאז 15/03/2023" → {"date_from": "2023-03-15"}
- "כמה החלטות בנושא חינוך" → {"count_only": true, "tags_policy_area": "חינוך"}
- "5 החלטות של ממשלה 36" → {"limit": 5, "government_number": "36"}
- "החלטות דחופות בירושלים" → {"urgency_level": "דחוף", "tags_location": "ירושלים"}

RETURN FORMAT:
{
  "date_from": "YYYY-MM-DD or null",
  "date_to": "YYYY-MM-DD or null",
  "year_exact": number or null,
  "tags_policy_area": "tag or null",
  "topic": "topic or null",
  "government_number": "string or null",
  "limit": number or null,
  "count_only": boolean or null,
  // ... other params as needed
}

IMPORTANT: Return ONLY the parameters found. Use null for missing params. Normalize dates to YYYY-MM-DD.`;

    try {
      const response = await this.openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          { 
            role: "system", 
            content: "You are an expert parameter extractor. Return a FLAT JSON object with extracted parameters. Use exact key names provided." 
          },
          { role: "user", content: prompt }
        ],
        temperature: 0.1,
        max_tokens: 300,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0].message.content;
      if (!content) {
        console.error('[NLToSQL] No response from GPT for parameter extraction');
        return {};
      }

      const extracted = JSON.parse(content);
      console.log('[NLToSQL] Extracted parameters:', extracted);
      return extracted;
    } catch (error) {
      console.error('[NLToSQL] Error extracting parameters with GPT:', error);
      return {};
    }
  }

  // Build normalized query with extracted parameters
  private buildNormalizedQuery(originalQuery: string, params: any): string {
    let normalized = originalQuery;
    
    // Replace dates with normalized versions
    if (params.date_from) {
      // Try to replace various date patterns with normalized date
      normalized = normalized.replace(/\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}/g, params.date_from);
    }
    
    // Apply other normalizations
    normalized = normalized
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/^(תן\s+לי\s+|הבא\s+לי\s+|הבא\s+|תן\s+)?החלטה\s+בנושא/, 'החלטה אחת בנושא')
      .replace(/^החלטה\s+מ/, 'החלטה אחת מ')
      .replace(/משנת\s+(\d{4})/, 'מ$1')
      .replace(/בשנת\s+(\d{4})/, 'מ$1')
      .replace(/^(תציג|הצג\s+לי|הראה\s+לי)\s+/, 'הבא ')
      .replace(/^1\s+החלטות/, 'החלטה אחת');
      
    // Topic normalization - only for exact tag matches
    if (params.topic) {
      const bestTag = findBestMatchingTag(params.topic);
      // Only update if it's an EXACT match to one of the 36 official tags
      if (bestTag && POLICY_TAGS.includes(bestTag)) {
        console.log(`[NLToSQL] Found exact tag match: "${params.topic}" → "${bestTag}"`);
        params.tags_policy_area = bestTag;
        // Keep the original topic for search
      } else {
        console.log(`[NLToSQL] No exact tag match for: "${params.topic}" - will search in content`);
      }
    }
    
    return normalized;
  }

  private async convertWithGPT(naturalQuery: string, extractedParams?: any): Promise<SQLConversion> {
    // If we have both date and topic from extracted params, build SQL directly
    if (extractedParams?.date_from && extractedParams?.topic) {
      const topic = extractedParams.topic;
      const searchTerm = `%${topic.trim()}%`;
      
      return {
        sql: `
          SELECT * FROM israeli_government_decisions 
          WHERE decision_date >= $1
          AND (tags_policy_area ILIKE $2 
               OR summary ILIKE $3 
               OR decision_content ILIKE $4
               OR decision_title ILIKE $5)
          ORDER BY decision_date DESC
        `,
        params: [
          extractedParams.date_from,
          searchTerm,
          searchTerm,
          searchTerm,
          searchTerm
        ],
        expectedType: 'multiple',
        explanation: `מחפש החלטות מאז ${extractedParams.date_from} בנושא ${topic}`,
        confidence: 0.95
      };
    }
    
    // For topic-only searches, prefer specific content search over broad tag matching
    if (extractedParams?.topic && !extractedParams?.date_from) {
      const topic = extractedParams.topic;
      const searchTerm = `%${topic.trim()}%`;
      
      // Check if it's an exact policy tag match
      const isExactTag = topic === extractedParams.tags_policy_area;
      
      if (isExactTag) {
        // Only use tag search for exact matches
        return {
          sql: `SELECT * FROM israeli_government_decisions WHERE tags_policy_area ILIKE $1 ORDER BY decision_date DESC`,
          params: [searchTerm],
          expectedType: 'multiple',
          explanation: `מחפש החלטות בתחום ${topic}`,
          confidence: 0.95
        };
      } else {
        // For non-exact matches, search in content for more relevant results
        return {
          sql: `
            SELECT * FROM israeli_government_decisions 
            WHERE decision_title ILIKE $1
               OR summary ILIKE $2
               OR decision_content ILIKE $3
            ORDER BY decision_date DESC
          `,
          params: [searchTerm, searchTerm, searchTerm],
          expectedType: 'multiple',
          explanation: `מחפש החלטות שמכילות את המונח "${topic}"`,
          confidence: 0.9
        };
      }
    }
    
    const systemPrompt = this.buildSystemPrompt();
    const userPrompt = this.buildUserPrompt(naturalQuery, extractedParams);
    
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
      const confidence = result.confidence || 0.8;
      
      // If we have extracted params, ensure they're used in the SQL
      if (extractedParams?.date_from && result.sql.includes('$1')) {
        // Make sure the date param is properly placed
        if (!result.params || result.params.length === 0) {
          result.params = [extractedParams.date_from];
        } else if (typeof result.params[0] === 'string' && result.params[0].match(/\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}/)) {
          // Replace non-normalized date with normalized one
          result.params[0] = extractedParams.date_from;
        }
      }
      
      // Validate params match SQL parameters
      const sqlParamCount = (result.sql.match(/\$\d+/g) || []).length;
      const providedParamCount = (result.params || []).length;
      
      if (sqlParamCount > 0 && providedParamCount === 0) {
        console.error('[NLToSQL] SQL has parameters but no params provided!');
        console.error('[NLToSQL] SQL:', result.sql);
        throw new Error('SQL parameters mismatch: SQL expects parameters but none provided');
      }
      
      if (sqlParamCount !== providedParamCount) {
        console.warn('[NLToSQL] Parameter count mismatch:', {
          sqlParams: sqlParamCount,
          providedParams: providedParamCount,
          sql: result.sql,
          params: result.params
        });
      }
      
      // Confidence gate - if too low, provide guidance instead
      if (confidence < 0.7 || !result.sql || result.sql.trim() === '') {
        console.log('[NLToSQL] Low confidence or invalid SQL, returning guidance');
        return {
          sql: 'SELECT decision_number, decision_title, decision_date FROM israeli_government_decisions LIMIT 0',
          params: [],
          expectedType: 'multiple',
          explanation: '❓ לא הבנתי בדיוק את הנושא / התאריך. נסה למשל:\n   • החלטות בנושא חינוך משנת 2022\n   • החלטות של ממשלה 37 בין 2021-2022',
          confidence: confidence
        };
      }
      
      return {
        sql: result.sql,
        params: result.params || [],
        expectedType: result.expected_type || 'multiple',
        explanation: result.explanation || 'שאילתה מותאמת אישית',
        confidence: confidence
      };
    } catch (error) {
      console.error('[NLToSQL] GPT conversion error:', error);
      throw new Error(`Failed to convert query: ${(error as Error).message}`);
    }
  }

  private buildSystemPrompt(): string {
    return `You are a SQL query generator for Israeli government decisions database.

=== CRITICAL RULES ===
1. **NEVER** add government_number filter unless the user explicitly mentions a government number
2. **NEVER** default to government 37 - search across ALL governments unless specified
3. Only filter by government when user says "ממשלה X" or similar explicit reference

=== CRITICAL: PARAMETER EXTRACTION ===

You MUST extract ALL relevant parameters from the Hebrew query following this comprehensive map:

1. **TIME PARAMETERS** (זמן):
   - date_from: "מאז X", "החל מ-X", "מ-X", "אחרי X" → decision_date >= 'YYYY-MM-DD'
   - date_to: "עד X", "לפני X" → decision_date <= 'YYYY-MM-DD'
   - date_range: "בין X ל-Y", "בשנים X-Y" → BETWEEN dates
   - year_exact: "בשנת X", "ב-X" → EXTRACT(YEAR FROM decision_date) = X
   - month_year: "בחודש X שנת Y" → EXTRACT(MONTH FROM date) = X AND EXTRACT(YEAR FROM date) = Y
   - relative_period: "בחצי השנה האחרונה", "ב-X הימים האחרונים" → dynamic calculation
   
2. **TOPIC PARAMETERS** (נושא):
   - tags_policy_area: Match against 36 official tags (see list below)
   - topic_free: Free text not in tags → search in summary, content, title
   - topic_fuzzy: "איכות הסביבה" → "סביבה", "פנסיה" → "אזרחים ותיקים"
   
3. **GOVERNMENT/POLITICAL** (ממשלה):
   - government_number: "ממשלה X" → government_number = 'X' OR 'X.0' (TEXT!)
   - prime_minister: "של X", "בתקופת X" → prime_minister ILIKE '%X%'
   - committee: "ועדת X" → committee ILIKE '%X%'
   - current_government: "הממשלה הנוכחית" → 37
   - **CRITICAL RULE**: ONLY add government filter if user explicitly mentions government number!
   
4. **GEOGRAPHY** (גיאוגרפיה):
   - tags_location: "בירושלים", "באזור הגליל" → tags_location ILIKE '%X%'
   - tags_government_body: "משרד החינוך", "משרד הבריאות"
   
5. **QUANTITY/AGGREGATION** (כמות):
   - count_only: "כמה", "מספר" → SELECT COUNT(*)
   - limit: "X החלטות", "הבא X" → LIMIT X (default: 10)
   - single_result: "החלטה אחת", "החלטה" → LIMIT 1
   - aggregation_type: "ממוצע", "סה״כ", "מקסימום"
   
6. **CONTENT FILTERS** (סינון תוכן):
   - full_text_query: "שמכילות 'X'", "עם המילה X" → ILIKE '%X%'
   - operativity_filter: "אופרטיביות", "דקלרטיביות" → operativity column
   - decision_number: "החלטה מספר X" → decision_number = 'X' (TEXT!)
   
7. **DISPLAY TYPE** (הצגה):
   - expected_type: single/multiple/count/aggregate
   - order_by: "הכי חדשות", "לפי תאריך" → ORDER BY decision_date DESC
   - fields_subset: "רק קישורים", "כותרות בלבד" → SELECT specific columns
   
8. **CONTEXT/CLARITY** (הקשר):
   - unclear_query: Very short (<3 chars) or gibberish → return guidance
   - follow_up_ref: "וב-2021?", "כמה כאלה?" → needs previous context
   - confidence: 0.0-1.0 based on clarity and parameter extraction success
    
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
1. **PREFER SPECIFIC CONTENT SEARCH**: When user searches for a topic that is NOT an exact official tag,
   search in decision_title, summary, and decision_content for more relevant results.
   Example: "החברה הערבית" → search for "%החברה הערבית%" in content, NOT in tags

2. Only use tags_policy_area search when:
   - The user query exactly matches one of the 36 official tags
   - The user explicitly asks for decisions "in the field/area of X" (בתחום)

3. For better relevance, prioritize searching in this order:
   - decision_title (most specific)
   - summary (good overview)
   - decision_content (comprehensive but may be less focused)

4. Examples of content search (NOT tag search):
   - "החברה הערבית" → WHERE decision_title ILIKE '%החברה הערבית%' OR ...
   - "ערבים" → WHERE decision_title ILIKE '%ערבים%' OR ...
   - "דרוזים" → WHERE decision_title ILIKE '%דרוזים%' OR ...
   - "קורונה" → WHERE decision_title ILIKE '%קורונה%' OR ...

2. For broader matches, search for the most significant word:
   - Don't search for full phrases if partial match is better
   - Focus on the main topic word

3. If topic not in tags, search comprehensively:
   WHERE (tags_policy_area ILIKE $1 
      OR summary ILIKE $1 
      OR decision_content ILIKE $1
      OR decision_title ILIKE $1)

Important Rules:
1. ALWAYS use parameterized queries with $1, $2, etc.
2. For Hebrew text search use ILIKE with % wildcards
3. decision_number is TEXT, not INTEGER - use string comparison
4. government_number is TEXT (e.g., "37.0") - ALWAYS compare as TEXT: government_number = '37' OR government_number = '37.0'
5. Current government is 37 (stored as "37" or "37.0") - but DO NOT filter by government unless explicitly requested
   - **CRITICAL**: NEVER add government filter automatically! Only filter by government if user explicitly mentions it
6. Decision numbers reset each government - ALWAYS filter by government_number
7. Always limit results unless counting (default LIMIT 10, but respect specific numbers requested by user)
8. Order by decision_date DESC for recent results
9. Use valid PostgreSQL syntax
10. For single decision requests, use LIMIT 1
11. Tags are separated by semicolon (;)
12. NEVER use government_number = 37 (integer), ALWAYS use government_number = '37' (string)
13. DATES: decision_date is in YYYY-MM-DD format. ALWAYS convert dates to this format:
    - "1/1/2023" or "1.1.2023" → "2023-01-01"
    - "15/06/23" → "2023-06-15"
    - Always pad month and day with zeros: "2023-1-5" → "2023-01-05"
14. **CRITICAL**: When creating params array:
    - Date parameters MUST be in YYYY-MM-DD format
    - Example: Query "מאז 15/03/2023" → params: ["2023-03-15", ...]
    - Example: Query "מאז 1.1.2023" → params: ["2023-01-01", ...]

Common Query Patterns:
- "מאז תאריך X בנושא Y": 
  SQL: WHERE decision_date >= $1 AND (tags_policy_area ILIKE $2)
  params: ["2023-03-15", "%חינוך%"]  // DATE MUST BE NORMALIZED!
  
- "החלטות משנת X בנושא Y": 
  SQL: WHERE EXTRACT(YEAR FROM decision_date) = $1 AND (tags_policy_area ILIKE $2)
  params: [2023, "%בריאות%"]
  
- "בין תאריך X ל-Y": 
  SQL: WHERE decision_date BETWEEN $1 AND $2
  params: ["2023-01-01", "2023-12-31"]  // BOTH DATES NORMALIZED!
  
- "החלטות של ממשלה X": 
  SQL: WHERE government_number = $1 OR government_number = $2
  params: ["37", "37.0"]
  
- "מה עשה ראש הממשלה X": 
  SQL: WHERE prime_minister ILIKE $1
  params: ["%נתניהו%"]

Response format (JSON):
{
  "sql": "SELECT ... FROM ... WHERE ...",
  "params": ["param1", "param2"],  // MUST match $1, $2 in SQL!
  "expected_type": "single|multiple|count|aggregate",
  "explanation": "Hebrew explanation of what the query does",
  "confidence": 0.0-1.0,
  "extracted_params": {
    "date_from": "YYYY-MM-DD or null",
    "date_to": "YYYY-MM-DD or null", 
    "year_exact": "number or null",
    "month_year": {"month": number, "year": number} or null,
    "relative_period": "string description or null",
    "tags_policy_area": "matched tag or null",
    "topic_free": "free text topic or null",
    "tags_location": "location or null",
    "tags_government_body": "ministry/body or null",
    "government_number": "number string or null",
    "prime_minister": "PM name or null",
    "committee": "committee name or null",
    "limit": "number or null",
    "count_only": "boolean",
    "single_result": "boolean",
    "full_text_query": "search term or null",
    "operativity_filter": "אופרטיבי/דקלרטיבי or null",
    "decision_number": "number string or null",
    "order_by": "field and direction or null",
    "confidence_reason": "reason for confidence score"
  }
}

EXAMPLES OF PARAMETER EXTRACTION:

1. "כמה החלטות בנושא חינוך היו בשנת 2023?"
   → count_only: true, tags_policy_area: "חינוך", year_exact: 2023

2. "הבא 5 החלטות של נתניהו בנושא ביטחון מאז 2022"
   → limit: 5, prime_minister: "נתניהו", tags_policy_area: "ביטחון לאומי וצה״ל", date_from: "2022-01-01"

3. "החלטות בירושלים מהחודשיים האחרונים"
   → tags_location: "ירושלים", relative_period: "2 months"

4. "החלטה 660 של ממשלה 35"
   → decision_number: "660", government_number: "35", single_result: true

5. "החלטות מאז 15/03/2023 בנושא חינוך"
   → SQL: WHERE decision_date >= $1 AND tags_policy_area ILIKE $2
   → params: ["2023-03-15", "%חינוך%"]
   → date_from: "2023-03-15", tags_policy_area: "חינוך"

6. "החלטות מאז 1.1.2023"
   → SQL: WHERE decision_date >= $1
   → params: ["2023-01-01"]  // NOT "1.1.2023"!`;
  }

  private buildUserPrompt(query: string, extractedParams?: any): string {
    // Add context about Hebrew column mappings
    const hebrewMappings = getHebrewColumnNames();
    
    let prompt = `Convert this Hebrew query to SQL: "${query}"

Extracted parameters from the query:
${JSON.stringify(extractedParams || {}, null, 2)}

IMPORTANT: Use the extracted parameters above, especially the normalized dates!`;
    
    return prompt + `

Hebrew to English column mappings:
${Object.entries(hebrewMappings)
  .filter(([hebrew, _]) => /[\u0590-\u05FF]/.test(hebrew))
  .map(([hebrew, english]) => `- ${hebrew} → ${english}`)
  .join('\n')}

Remember:
- **CRITICAL**: ALWAYS include a "params" array in your response!
- If SQL uses $1, $2, etc., the params array MUST contain the corresponding values
- Example: SQL with "WHERE decision_date >= $1 AND tags_policy_area ILIKE $2"
  Must have params: ["2023-03-15", "%חינוך%"]
- NEVER return empty params if SQL contains parameters!
- Date parameters MUST be normalized to YYYY-MM-DD format
  * "15/03/2023" → "2023-03-15" in params
  * "1.1.2023" → "2023-01-01" in params
- If asking for one decision ("החלטה" or "החלטה אחת"), use LIMIT 1
- If asking for multiple ("החלטות"), use appropriate LIMIT
- If asking for specific number (e.g., "20 החלטות"), use LIMIT 20
- If counting ("כמה"), use COUNT(*)
- **IMPORTANT**: DO NOT add government filter unless explicitly mentioned by user
- Decision numbers need government context
- For year-based queries, use EXTRACT(YEAR FROM decision_date) = year_number
- When searching by topic AND year, combine both conditions
- Contextual queries like "וב2021?" refer to previous context
- **CRITICAL DATE HANDLING**:
  * ALWAYS normalize dates to YYYY-MM-DD format before putting in params
  * "15/03/2023" or "15.03.2023" → param should be "2023-03-15"
  * "1.1.2023" → param should be "2023-01-01" (with zero padding)
  * When user says "מאז X" - use decision_date >= with normalized date
  * When user says "משנת X" - use EXTRACT(YEAR FROM decision_date) = X
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
- Normalize query variations: "תן לי החלטה" = "החלטה אחת" = "הבא החלטה"
- For comprehensive topic search: Search in tags_policy_area, summary, decision_content AND decision_title
- For "since date" queries: Use decision_date >= date_value
- When user asks for decisions "שעוסקות ב" or "שקשורות ל", search in all relevant fields, not just tags`;
  }

  // Check if query is unclear/vague
  private isUnclearQuery(query: string): boolean {
    // Check for gibberish - non-Hebrew and non-ASCII
    const hebrewPattern = /[֐-׿]/;
    const asciiPattern = /[a-zA-Z0-9]/;
    if (!hebrewPattern.test(query) && !asciiPattern.test(query)) {
      return true;
    }
    
    // Check for very short queries
    const trimmed = query.trim();
    if (trimmed.length < 3) {
      return true;
    }
    
    // Check for common unclear patterns
    const unclearPatterns = [
      /^משהו\s*לא\s*ברור/,  // "משהו לא ברור"
      /^לא\s*ברור/,                    // "לא ברור"
      /^אה$/,                           // "אה"
      /^מה$/,                           // "מה"
      /^xyz/i,                         // gibberish starting with xyz
      /^[^\u0590-\u05FF\w\s]{3,}$/   // only special characters
    ];
    
    return unclearPatterns.some(pattern => pattern.test(trimmed));
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
  extractEntities(query: string): ExtractedEntities {
    const entities: ExtractedEntities = {};
    
    // Extract decision number
    const decisionMatch = query.match(/החלטה\s*(?:מספר\s*)?(\d+)/);
    if (decisionMatch) {
      entities.decision_number = decisionMatch[1];
    }
    
    // Extract government number
    const govMatch = query.match(/ממשלה\s*(\d+)/);
    if (govMatch) {
      entities.government_number = parseInt(govMatch[1]);
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
    
    // Extract limit
    const limitMatch = query.match(/(\d+)\s+החלטות?/);
    if (limitMatch) {
      entities.limit = parseInt(limitMatch[1]);
    }
    
    // Extract prime minister
    const pmMatch = query.match(/(?:של|מאת)\s+([\u0590-\u05FF\s]+?)\s+(?:בנושא|החלטות)/);
    if (pmMatch) {
      entities.prime_minister = pmMatch[1].trim();
    }
    
    // Extract date range
    const dateRange = extractDateRange(query);
    if (dateRange.startDate) {
      entities.date_from = dateRange.startDate;
    }
    if (dateRange.endDate) {
      entities.date_to = dateRange.endDate;
    }
    
    return entities;
  }
}
