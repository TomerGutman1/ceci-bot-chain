/**
 * Query templates for common patterns
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

export const QUERY_TEMPLATES: Record<string, QueryTemplate> = {
  // Single decision by number with government
  DECISION_BY_NUMBER: {
    name: 'החלטה לפי מספר וממשלה',
    description: 'מציאת החלטה ספציפית לפי מספר וממשלה',
    pattern: /החלטה\s*(?:מספר\s*)?(\d+)\s*של\s*ממשלה\s*(\d+)/,
    sql: (_decision: string, _gov?: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE decision_key = $1
      LIMIT 1
    `,
    params: (decision: string, gov?: string) => [`${gov || '37'}_${decision}`],
    expectedType: 'single',
    examples: ['החלטה 660 של ממשלה 35']
  },

  // Single decision by number (any government)
  DECISION_BY_NUMBER_ANY_GOV: {
    name: 'החלטה לפי מספר בכל הממשלות',
    description: 'מציאת החלטה ספציפית לפי מספר בכל הממשלות',
    pattern: /^החלטה\s*(?:מספר\s*)?(\d+)\s*$/,
    sql: (_decision: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE decision_number = $1
      ORDER BY government_number DESC
      LIMIT 10
    `,
    params: (decision: string) => [decision],
    expectedType: 'multiple',
    examples: ['החלטה 660']
  },

  // Decision by key (government_decision)
  DECISION_BY_KEY: {
    name: 'החלטה לפי מפתח',
    description: 'מציאת החלטה לפי מפתח משולב',
    pattern: /decision_key\s*=\s*['"](\d+_\d+)['"]/,
    sql: (_key: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE decision_key = $1
      LIMIT 1
    `,
    params: (key: string) => [key],
    expectedType: 'single',
    examples: ['decision_key = "37_660"']
  },

  // Decisions by topic
  SINGLE_DECISION_BY_TOPIC: {
    name: 'החלטה בודדת לפי נושא',
    description: 'מציאת החלטה אחת בנושא מסוים',
    pattern: /הבא\s+(?:לי\s+)?החלטה\s+(?:אחת\s+)?בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_topic: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
      ORDER BY decision_date DESC
      LIMIT 1
    `,
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'single',
    examples: ['הבא לי החלטה בנושא חינוך', 'הבא החלטה אחת בנושא בריאות']
  },

  MULTIPLE_DECISIONS_BY_TOPIC: {
    name: 'החלטות לפי נושא',
    description: 'מציאת מספר החלטות בנושא מסוים',
    pattern: /(?:הבא|תן|הצג)\s+(?:לי\s+)?(\d+|כמה|מספר)?\s*החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (count: string, _topic: string) => {
      const limit = count && !isNaN(parseInt(count)) ? parseInt(count) : 10;
      return `
        SELECT * FROM israeli_government_decisions 
        WHERE tags_policy_area ILIKE $1
        ORDER BY decision_date DESC
        LIMIT ${limit}
      `;
    },
    params: (_count: string, topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['הבא 5 החלטות בנושא תחבורה', 'תן לי כמה החלטות בנושא חינוך']
  },

  // Current government decisions
  CURRENT_GOVERNMENT_TOPIC: {
    name: 'החלטות הממשלה הנוכחית',
    description: 'החלטות של הממשלה הנוכחית בנושא מסוים',
    pattern: /החלט(?:ה|ות)\s+(?:מה)?ממשלה\s+ה?(?:נוכחית|אחרונה|הנוכחית)\s+בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_topic: string) => `
      SELECT * 
      FROM israeli_government_decisions 
      WHERE (government_number = $1 OR government_number = $1 || '.0')
        AND tags_policy_area ILIKE $2
      ORDER BY decision_date DESC
      LIMIT 100
    `,
    params: (topic: string) => ['37', topic.trim()],
    expectedType: 'multiple',
    examples: ['החלטות מהממשלה הנוכחית בנושא תחבורה']
  },

  // Total count
  TOTAL_COUNT: {
    name: 'ספירת כל ההחלטות',
    description: 'כמה החלטות יש בסך הכל',
    pattern: /כמה\s+החלטות\s+(?:יש|קיימות)?\s*(?:בסך\s*הכל|סה"כ)?\s*\??$/,
    sql: () => `SELECT COUNT(*) as count FROM israeli_government_decisions`,
    params: () => [],
    expectedType: 'count',
    examples: ['כמה החלטות יש בסך הכל?', 'כמה החלטות יש?', 'כמה החלטות קיימות?']
  },

  // Count queries
  COUNT_BY_YEAR: {
    name: 'ספירת החלטות לפי שנה',
    description: 'כמה החלטות התקבלו בשנה מסוימת',
    pattern: /כמה\s+החלטות\s+(?:יש|התקבלו|היו)?\s*(?:ב|מ)?שנת\s+(\d{4})/,
    sql: (_year: string) => `SELECT * FROM count_decisions_by_year($1)`,
    params: (year: string) => [parseInt(year)],
    expectedType: 'count',
    examples: ['כמה החלטות יש משנת 2023?', 'כמה החלטות התקבלו בשנת 2024?']
  },

  COUNT_BY_TOPIC: {
    name: 'ספירת החלטות לפי נושא',
    description: 'כמה החלטות יש בנושא מסוים',
    pattern: /כמה\s+החלטות\s+(?:יש|קיימות)?\s*בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|\?|$)/,
    sql: (_topic: string) => `
      SELECT COUNT(*) as count 
      FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
    `,
    params: (topic: string) => [topic.trim()],
    expectedType: 'count',
    examples: ['כמה החלטות יש בנושא חינוך?']
  },

  // Decisions by date range
  DECISIONS_BY_DATE_RANGE: {
    name: 'החלטות בטווח תאריכים',
    description: 'החלטות בין שני תאריכים',
    pattern: /החלטות\s+(?:מ|בין)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s+(?:עד|ל)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})/,
    sql: (_fromDate: string, _toDate: string) => `
      SELECT * 
      FROM israeli_government_decisions 
      WHERE decision_date BETWEEN $1 AND $2
      ORDER BY decision_date DESC
      LIMIT 100
    `,
    params: (fromDate: string, toDate: string) => [
      normalizeDate(fromDate),
      normalizeDate(toDate)
    ],
    expectedType: 'multiple',
    examples: ['החלטות מ-1.1.2023 עד 31.12.2023']
  },

  // Statistics by government
  GOVERNMENT_STATISTICS: {
    name: 'סטטיסטיקת ממשלה',
    description: 'סטטיסטיקה על ממשלה מסוימת',
    pattern: /סטטיסטיק(?:ה|ות)\s+(?:של\s+|על\s+)?ממשלה\s+(\d+)/,
    sql: (_gov: string) => `SELECT * FROM get_government_statistics($1)`,
    params: (gov: string) => [parseInt(gov)],
    expectedType: 'aggregate',
    examples: ['סטטיסטיקה של ממשלה 36', 'סטטיסטיקות על ממשלה 37']
  },

  // Recent decisions
  RECENT_DECISIONS: {
    name: 'החלטות אחרונות',
    description: 'ההחלטות האחרונות שהתקבלו',
    pattern: /(?:ה)?החלטות\s+(?:ה)?אחרונות|החלטות\s+מ?השבוע\s+האחרון|החלטות\s+עדכניות/,
    sql: () => `
      SELECT * FROM israeli_government_decisions 
      ORDER BY decision_date DESC
      LIMIT 10
    `,
    params: () => [],
    expectedType: 'multiple',
    examples: ['ההחלטות האחרונות', 'החלטות מהשבוע האחרון']
  },

  // Search in content
  CONTENT_SEARCH: {
    name: 'חיפוש בתוכן',
    description: 'חיפוש טקסט חופשי בתוכן ההחלטות',
    pattern: /חפש\s+(?:את\s+)?(?:המילה\s+|הביטוי\s+)?["']([^"']+)["']/,
    sql: (_searchTerm: string) => `SELECT * FROM search_decisions_hebrew($1)`,
    params: (searchTerm: string) => [searchTerm],
    expectedType: 'multiple',
    examples: ['חפש "קורונה"', 'חפש את המילה "חינוך חינם"']
  },

  // Count per government
  COUNT_PER_GOVERNMENT: {
    name: 'ספירה לפי ממשלה',
    description: 'כמה החלטות קיבלה כל ממשלה',
    pattern: /כמה\s+החלטות\s+קיבלה\s+כל\s+ממשלה/,
    sql: () => `SELECT * FROM count_decisions_per_government()`,
    params: () => [],
    expectedType: 'aggregate',
    examples: ['כמה החלטות קיבלה כל ממשלה?']
  },

  // Decisions by prime minister
  DECISIONS_BY_PM: {
    name: 'החלטות לפי ראש ממשלה',
    description: 'החלטות של ראש ממשלה מסוים',
    pattern: /החלטות\s+של\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_pmName: string) => `SELECT * FROM get_decisions_by_prime_minister($1)`,
    params: (pmName: string) => [pmName.trim()],
    expectedType: 'multiple',
    examples: ['החלטות של נתניהו']
  },

  // Important decisions by year
  IMPORTANT_BY_YEAR: {
    name: 'החלטות חשובות לפי שנה',
    description: 'ההחלטות החשובות ביותר של שנה מסוימת',
    pattern: /(?:מה\s+)?(?:הן\s+)?(?:ה)?החלטות\s+החשובות\s+(?:ביותר\s+)?(?:של\s+)?(?:ב?)?(\d{4})/,
    sql: (_year: string) => `SELECT * FROM get_important_decisions_by_year($1)`,
    params: (year: string) => [parseInt(year)],
    expectedType: 'multiple',
    examples: ['מה ההחלטות החשובות ביותר של 2024?']
  },

  // Decisions from last year with topic
  LAST_YEAR_TOPIC: {
    name: 'החלטות שנה אחרונה בנושא',
    description: 'החלטות בנושא מסוים מהשנה האחרונה',
    pattern: /החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+מהשנה\s+האחרונה/,
    sql: (_topic: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
        AND EXTRACT(YEAR FROM decision_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
      ORDER BY decision_date DESC
      LIMIT 20
    `,
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['החלטות בנושא חינוך מהשנה האחרונה']
  },

  // Count decisions by government and topic
  COUNT_BY_GOVERNMENT_AND_TOPIC: {
    name: 'ספירת החלטות לפי ממשלה ונושא',
    description: 'כמה החלטות בנושא מסוים החליטה ממשלה מסוימת',
    pattern: /כמה\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+(?:החליטה|קיבלה|התקבלו\s+ב)\s*ממשלה\s+(?:מס(?:פר)?\s*)?(\d+)/,
    sql: (_topic: string, _gov: string) => `
      SELECT 
        COUNT(*) as count,
        $1 as topic,
        $2 as government_number,
        MIN(decision_date) as first_decision,
        MAX(decision_date) as last_decision,
        MAX(prime_minister) as prime_minister
      FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $3
        AND government_number IN ($2, $2 || '.0')
    `,
    params: (topic: string, gov: string) => [topic.trim(), gov, `%${topic.trim()}%`],
    expectedType: 'count',
    examples: ['כמה החלטות בנושא חינוך החליטה ממשלה מס 37']
  },

  // Count decisions by topic and date range
  COUNT_BY_TOPIC_AND_DATE_RANGE: {
    name: 'ספירת החלטות לפי נושא וטווח תאריכים',
    description: 'כמה החלטות בנושא מסוים עברו בטווח תאריכים',
    pattern: /כמה\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+(?:עברו|התקבלו|היו)\s+(?:בין|מ)\s*(\d{4})\s+(?:ל|עד)\s*(\d{4})/,
    sql: (_topic: string, _startYear: string, _endYear: string) => `
      SELECT 
        COUNT(*) as count,
        $1 as topic,
        $2 as start_year,
        $3 as end_year,
        COUNT(DISTINCT government_number) as governments_count,
        MIN(decision_date) as first_decision,
        MAX(decision_date) as last_decision
      FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $4
        AND EXTRACT(YEAR FROM decision_date) BETWEEN $2 AND $3
    `,
    params: (topic: string, startYear: string, endYear: string) => [
      topic.trim(), 
      parseInt(startYear), 
      parseInt(endYear), 
      `%${topic.trim()}%`
    ],
    expectedType: 'count',
    examples: ['כמה החלטות בנושא חינוך עברו בין 2020 ל2022']
  }
};

// Helper functions
function normalizeDate(dateStr: string): string {
  // Convert various date formats to YYYY-MM-DD
  const parts = dateStr.split(/[\/\-\.]/);
  if (parts.length === 3) {
    const day = parts[0].padStart(2, '0');
    const month = parts[1].padStart(2, '0');
    const year = parts[2].length === 2 ? '20' + parts[2] : parts[2];
    return `${year}-${month}-${day}`;
  }
  return dateStr;
}

// Get all patterns for testing
export function getAllPatterns(): RegExp[] {
  return Object.values(QUERY_TEMPLATES).map(template => template.pattern);
}

// Find matching template
export function findMatchingTemplate(query: string): {
  template: QueryTemplate;
  matches: string[];
} | null {
  for (const [_key, template] of Object.entries(QUERY_TEMPLATES)) {
    const match = query.match(template.pattern);
    if (match) {
      return {
        template,
        matches: match.slice(1) // Remove full match, keep capture groups
      };
    }
  }
  return null;
}
