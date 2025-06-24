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
    
    // Step 1: Try pattern matching for common queries
    const templateResult = this.tryTemplateMatch(naturalQuery);
    if (templateResult) {
      console.log('[NLToSQL] Matched template:', templateResult.templateUsed);
      return templateResult;
    }

    // Step 2: If no template matches, use GPT for conversion
    console.log('[NLToSQL] No template match, using GPT');
    return await this.convertWithGPT(naturalQuery);
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

Important Rules:
1. ALWAYS use parameterized queries with $1, $2, etc.
2. For Hebrew text search use ILIKE with % wildcards
3. decision_number is TEXT, not INTEGER - use string comparison
4. Current government is 37
5. Decision numbers reset each government - ALWAYS filter by government_number
6. Always limit results unless counting (default LIMIT 10)
7. Order by decision_date DESC for recent results
8. Use valid PostgreSQL syntax
9. For single decision requests, use LIMIT 1
10. Tags are separated by semicolon (;)

Common Patterns:
- Single decision: WHERE decision_number = $1 AND government_number = $2
- Topic search: WHERE tags_policy_area ILIKE $1
- Count: SELECT COUNT(*) as count
- Date range: WHERE decision_date BETWEEN $1 AND $2
- Recent: ORDER BY decision_date DESC LIMIT 10

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
- If asking for one decision ("החלטה"), use LIMIT 1
- If asking for multiple ("החלטות"), use appropriate LIMIT
- If counting ("כמה"), use COUNT(*)
- If no government specified, use current (37)
- Decision numbers need government context`;
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
