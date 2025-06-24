/**
 * Fixed Query templates - removing hard-coded LIMIT for statistical queries
 * These are pre-defined SQL queries for common natural language patterns
 */

export interface QueryTemplate {
  name: string;
  description: string;
  pattern: RegExp;
  sql: (...args: string[]) => string;
  params: (...args: string[]) => any[];
  expectedType: 'single' | 'multiple' | 'count' | 'aggregate';
  examples: string[];
}

// Helper function to determine appropriate limit based on query type
function getAppropriateLimit(expectedType: string, userRequestedLimit?: number): string {
  if (userRequestedLimit) {
    return `LIMIT ${userRequestedLimit}`;
  }
  
  // For count/aggregate queries that need all data, don't limit
  if (expectedType === 'count' || expectedType === 'aggregate') {
    return ''; // No limit
  }
  
  // For display queries, use reasonable defaults
  return 'LIMIT 100'; // Default for multiple results
}

export const QUERY_TEMPLATES: Record<string, QueryTemplate> = {
  // ... (keeping all other templates as is)

  // Search by committee - FIXED: No hard limit
  DECISIONS_BY_COMMITTEE: {
    name: 'החלטות לפי ועדה',
    description: 'החלטות של ועדה מסוימת',
    pattern: /החלטות\s+(?:של\s+)?ועד(?:ה|ת)\s+([\u0590-\u05FF\s]+?)(?:\s+ב[-\s]?(\d{4}))?/,
    sql: (committee: string, year?: string) => {
      if (year) {
        return `
          SELECT * FROM israeli_government_decisions 
          WHERE committee ILIKE $1
          AND EXTRACT(YEAR FROM decision_date) = $2
          ORDER BY decision_date DESC
        `;
      }
      return `
        SELECT * FROM israeli_government_decisions 
        WHERE committee ILIKE $1
        ORDER BY decision_date DESC
      `;
    },
    params: (committee: string, year?: string) => {
      const params: any[] = [`%${committee.trim()}%`];
      if (year) params.push(parseInt(year));
      return params;
    },
    expectedType: 'multiple',
    examples: ['החלטות ועדת השרים לענייני חקיקה ב-2023', 'החלטות של ועדת הכספים']
  },

  // Search by location - FIXED: No hard limit
  DECISIONS_BY_LOCATION: {
    name: 'החלטות לפי מיקום',
    description: 'החלטות הקשורות למיקום מסוים',
    pattern: /החלטות\s+(?:על|בנושא|לגבי)\s+([\u0590-\u05FF\s]+?)\s+(?:ש)?(?:התקבלו\s+)?(?:מאז|מ[-\s]?)(\d{4})/,
    sql: (location: string, year: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE (tags_location ILIKE '%${location.trim()}%' OR all_tags ILIKE '%${location.trim()}%')
      AND decision_date >= '${year}-01-01'
      ORDER BY decision_date DESC
    `,
    params: () => [],
    expectedType: 'multiple',
    examples: ['החלטות על ירושלים שהתקבלו מאז 2020', 'החלטות לגבי תל אביב מ-2022']
  },

  // PM + Topic - FIXED: Return ALL results for accurate statistics
  PM_AND_TOPIC: {
    name: 'ראש ממשלה ונושא',
    description: 'החלטות של ראש ממשלה בנושא מסוים',
    pattern: /(?:מה\s+)?(?:עשה|עשתה)\s+([\u0590-\u05FF\s]+?)\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    sql: (pm: string, topic: string) => `
      SELECT * FROM israeli_government_decisions
      WHERE prime_minister ILIKE '%${pm.trim()}%'
      AND (tags_policy_area ILIKE '%${topic.trim()}%' OR all_tags ILIKE '%${topic.trim()}%')
      ORDER BY decision_date DESC
    `,
    params: () => [],
    expectedType: 'multiple',
    examples: ['מה עשה נתניהו בנושא חינוך?', 'מה עשתה גולדה בנושא ביטחון?']
  },

  // Content search with date range - FIXED: Return more comprehensive results
  CONTENT_SEARCH_DATE_RANGE: {
    name: 'חיפוש בתוכן עם טווח תאריכים',
    description: 'חיפוש מילה בתוכן בטווח תאריכים',
    pattern: /['"]([^'"]+)['"]\s+בין\s+(\d{4})[-\s]?(\d{4})?/,
    sql: (term: string, fromYear: string, toYear?: string) => {
      const endYear = toYear || fromYear;
      return `
        SELECT * FROM israeli_government_decisions
        WHERE (decision_content ILIKE '%${term}%' 
           OR summary ILIKE '%${term}%' 
           OR decision_title ILIKE '%${term}%')
        AND decision_date BETWEEN '${fromYear}-01-01' AND '${endYear}-12-31'
        ORDER BY decision_date DESC
      `;
    },
    params: () => [],
    expectedType: 'multiple',
    examples: ["'קורונה' בין 2020-2021", "'תקציב' בין 2023-2024"]
  },

  // Alternative: PM + Topic with COUNT - NEW
  PM_TOPIC_COUNT: {
    name: 'ספירת החלטות ראש ממשלה בנושא',
    description: 'כמה החלטות קיבל ראש ממשלה בנושא מסוים',
    pattern: /כמה\s+החלטות\s+(?:קיבל|החליט|עשה)\s+([\u0590-\u05FF\s]+?)\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    sql: (pm: string, topic: string) => `
      SELECT 
        COUNT(*) as count,
        '${pm.trim()}' as prime_minister,
        '${topic.trim()}' as topic
      FROM israeli_government_decisions
      WHERE prime_minister ILIKE '%${pm.trim()}%'
      AND (tags_policy_area ILIKE '%${topic.trim()}%' OR all_tags ILIKE '%${topic.trim()}%')
    `,
    params: () => [],
    expectedType: 'count',
    examples: ['כמה החלטות קיבל נתניהו בנושא ביטחון?']
  }
};

// ... rest of the helper functions remain the same
