/**
 * Fixed Query templates for common patterns
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
  priority?: number; // Added priority for pattern matching
}

export const QUERY_TEMPLATES: Record<string, QueryTemplate> = {
  // Count decisions by government - NEW HIGH PRIORITY TEMPLATE
  COUNT_BY_GOVERNMENT: {
    name: 'ספירת החלטות לפי ממשלה',
    description: 'כמה החלטות קיבלה ממשלה מסוימת',
    pattern: /כמה\s+החלטות\s+(?:קיבלה|החליטה|יש\s+ל)\s*ממשלה\s+(?:מס(?:פר)?\s*)?(\d+)/,
    sql: (gov: string) => `
      SELECT COUNT(*) as count 
      FROM israeli_government_decisions 
      WHERE government_number = $1 OR government_number = $1 || '.0'
    `,
    params: (gov: string) => [gov],
    expectedType: 'count',
    examples: ['כמה החלטות קיבלה ממשלה 37?', 'כמה החלטות יש לממשלה 36?'],
    priority: 15 // High priority
  },

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
    examples: ['החלטה 660 של ממשלה 35'],
    priority: 10
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
    examples: ['החלטה 660'],
    priority: 9
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
    examples: ['decision_key = "37_660"'],
    priority: 10
  },

  // Decisions by committee - HIGH PRIORITY
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
    examples: ['החלטות ועדת השרים לענייני חקיקה ב-2023', 'החלטות של ועדת הכספים'],
    priority: 20 // High priority to match before PM pattern
  },

  // Decisions by location - FIXED field name
  DECISIONS_BY_LOCATION: {
    name: 'החלטות לפי מיקום',
    description: 'החלטות הקשורות למיקום מסוים',
    pattern: /החלטות\s+(?:על|בנושא|לגבי)\s+([\u0590-\u05FF\s]+?)\s+(?:ש)?(?:התקבלו\s+)?(?:מאז|מ[-\s]?)(\d{4})/,
    sql: (location: string, year: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE (tags_location ILIKE $1 OR all_tags ILIKE $2)
      AND decision_date >= $3
      ORDER BY decision_date DESC
    `,
    params: (location: string, year: string) => [
      `%${location.trim()}%`,
      `%${location.trim()}%`,
      `${year}-01-01`
    ],
    expectedType: 'multiple',
    examples: ['החלטות על ירושלים שהתקבלו מאז 2020', 'החלטות לגבי תל אביב מ-2022'],
    priority: 15
  },

  // X decisions by topic - NEW
  X_DECISIONS_BY_TOPIC: {
    name: 'X החלטות בנושא',
    description: 'מספר מדויק של החלטות בנושא מסוים',
    pattern: /(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    sql: (count: string, topic: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
      ORDER BY decision_date DESC
      LIMIT ${parseInt(count)}
    `,
    params: (_count: string, topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['הבא 20 החלטות בנושא תחבורה', 'תן לי 5 החלטות בנושא חינוך'],
    priority: 8
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
    examples: ['הבא לי החלטה בנושא חינוך', 'הבא החלטה אחת בנושא בריאות'],
    priority: 5
  },

  MULTIPLE_DECISIONS_BY_TOPIC: {
    name: 'החלטות לפי נושא',
    description: 'מציאת מספר החלטות בנושא מסוים',
    pattern: /(?:הבא|תן|הצג)\s+(?:לי\s+)?(?:כמה|מספר)?\s*החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_topic: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
      ORDER BY decision_date DESC
      LIMIT 10
    `,
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['הבא כמה החלטות בנושא תחבורה', 'תן לי החלטות בנושא חינוך'],
    priority: 5
  },

  // Current government decisions
  CURRENT_GOVERNMENT_TOPIC: {
    name: 'החלטות הממשלה הנוכחית',
    description: 'החלטות של הממשלה הנוכחית בנושא מסוים',
    pattern: /החלט(?:ה|ות)\s+(?:(?:מה\s*ממשלה)|מהממשלה|ממשלה)\s+ה?(?:נוכחית|אחרונה|הנוכחית)\s+בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_topic: string) => `
      SELECT *
      FROM   current_gov_decisions_by_topic($1, 10)
    `,
    params: (topic: string) => ['37', `%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['החלטות מהממשלה הנוכחית בנושא תחבורה'],
    priority: 5
  },

  // Total count
  TOTAL_COUNT: {
    name: 'ספירת כל ההחלטות',
    description: 'כמה החלטות יש בסך הכל',
    pattern: /כמה\s+החלטות\s+(?:יש|קיימות)?\s*(?:בסך\s*הכל|סה"כ)?\s*\??$/,
    sql: () => `SELECT COUNT(*) as count FROM israeli_government_decisions`,
    params: () => [],
    expectedType: 'count',
    examples: ['כמה החלטות יש בסך הכל?', 'כמה החלטות יש?', 'כמה החלטות קיימות?'],
    priority: 5
  },

  // Count queries
  COUNT_BY_YEAR: {
    name: 'ספירת החלטות לפי שנה',
    description: 'כמה החלטות התקבלו בשנה מסוימת',
    pattern: /כמה\s+החלטות\s+(?:יש|התקבלו|היו)?\s*(?:ב|מ)?שנת\s+(\d{4})/,
    sql: (_year: string) => `SELECT * FROM count_decisions_by_year($1)`,
    params: (year: string) => [parseInt(year)],
    expectedType: 'count',
    examples: ['כמה החלטות יש משנת 2023?', 'כמה החלטות התקבלו בשנת 2024?'],
    priority: 5
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
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'count',
    examples: ['כמה החלטות יש בנושא חינוך?'],
    priority: 5
  },

  // Count operativity
  COUNT_BY_OPERATIVITY: {
    name: 'ספירת החלטות לפי אופרטיביות',
    description: 'כמה החלטות דקלרטיביות או אופרטיביות',
    pattern: /כמה\s+החלטות\s+(דקלרטיביות|אופרטיביות)(?:\s+היו)?(?:\s+ב[-\s]?(\d{4}))?/,
    sql: (type: string, year?: string) => {
      if (year) {
        return `
          SELECT COUNT(*) as count 
          FROM israeli_government_decisions 
          WHERE operativity ILIKE $1
          AND EXTRACT(YEAR FROM decision_date) = $2
        `;
      }
      return `
        SELECT COUNT(*) as count 
        FROM israeli_government_decisions 
        WHERE operativity ILIKE $1
      `;
    },
    params: (type: string, year?: string) => {
      const params: any[] = [`%${type}%`];
      if (year) params.push(parseInt(year));
      return params;
    },
    expectedType: 'count',
    examples: ['כמה החלטות דקלרטיביות היו ב-2024?', 'כמה החלטות אופרטיביות?'],
    priority: 8
  },

  // Monthly trend
  MONTHLY_TREND: {
    name: 'מגמה חודשית',
    description: 'כמה החלטות היו בכל חודש בשנה',
    pattern: /(?:כמה\s+החלטות\s+)?(?:היו\s+)?בכל\s+חודש\s+ב[-\s]?(\d{4})/,
    sql: (year: string) => `
      SELECT 
        EXTRACT(MONTH FROM decision_date)::int as month,
        COUNT(*) as count
      FROM israeli_government_decisions 
      WHERE EXTRACT(YEAR FROM decision_date) = $1
      GROUP BY EXTRACT(MONTH FROM decision_date)
      ORDER BY month
    `,
    params: (year: string) => [parseInt(year)],
    expectedType: 'aggregate',
    examples: ['כמה החלטות היו בכל חודש ב-2023?'],
    priority: 7
  },

  // PM and topic
  PM_AND_TOPIC: {
    name: 'ראש ממשלה ונושא',
    description: 'החלטות של ראש ממשלה בנושא מסוים',
    pattern: /(?:מה\s+)?(?:עשה|עשתה)\s+([\u0590-\u05FF\s]+?)\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    sql: (pm: string, topic: string) => `
      SELECT * FROM israeli_government_decisions
      WHERE prime_minister ILIKE $1
      AND (tags_policy_area ILIKE $2 OR all_tags ILIKE $3)
      ORDER BY decision_date DESC
    `,
    params: (pm: string, topic: string) => [
      `%${pm.trim()}%`,
      `%${topic.trim()}%`,
      `%${topic.trim()}%`
    ],
    expectedType: 'multiple',
    examples: ['מה עשה נתניהו בנושא חינוך?', 'מה עשתה גולדה בנושא ביטחון?'],
    priority: 6
  },

  // Recent days
  RECENT_DAYS: {
    name: 'החלטות מימים אחרונים',
    description: 'החלטות מימים אחרונים',
    pattern: /החלטות\s+מ[-\s]?(\d+)\s+הימים\s+האחרונים/,
    sql: (days: string) => `
      SELECT * FROM israeli_government_decisions
      WHERE decision_date >= CURRENT_DATE - INTERVAL '${parseInt(days)} days'
      ORDER BY decision_date DESC
    `,
    params: () => [],
    expectedType: 'multiple',
    examples: ['החלטות מ-7 הימים האחרונים', 'החלטות מ-30 הימים האחרונים'],
    priority: 8
  },

  // Topic comparison
  TOPIC_COMPARISON: {
    name: 'השוואה בין נושאים',
    description: 'השוואת מספר החלטות בין שני נושאים',
    pattern: /(?:כמה\s+החלטות\s+)?([\u0590-\u05FF\s]+?)\s+לעומת\s+([\u0590-\u05FF\s]+?)(?:\s+ב[-\s]?(\d{4}))?/,
    sql: (topic1: string, topic2: string, year?: string) => {
      const yearCondition = year ? ` AND EXTRACT(YEAR FROM decision_date) = ${parseInt(year)}` : '';
      return `
        SELECT 
          '${topic1.trim()}' as topic,
          COUNT(*) as count
        FROM israeli_government_decisions 
        WHERE tags_policy_area ILIKE '%${topic1.trim()}%'${yearCondition}
        UNION ALL
        SELECT 
          '${topic2.trim()}' as topic,
          COUNT(*) as count
        FROM israeli_government_decisions 
        WHERE tags_policy_area ILIKE '%${topic2.trim()}%'${yearCondition}
        ORDER BY count DESC
      `;
    },
    params: () => [],
    expectedType: 'aggregate',
    examples: ['כמה החלטות חינוך לעומת בריאות ב-2024?'],
    priority: 6
  },

  // Top committees
  TOP_COMMITTEES: {
    name: 'ועדות מובילות',
    description: 'הוועדות שהנפיקו הכי הרבה החלטות',
    pattern: /(\d+)\s+הוועדות\s+(?:ש)?(?:הנפיקו|שהוציאו|עם)\s+הכי\s+הרבה\s+החלטות/,
    sql: (limit: string) => `
      SELECT 
        committee,
        COUNT(*) as count
      FROM israeli_government_decisions 
      WHERE committee IS NOT NULL AND committee != ''
      GROUP BY committee
      ORDER BY count DESC
      LIMIT ${parseInt(limit)}
    `,
    params: () => [],
    expectedType: 'aggregate',
    examples: ['3 הוועדות שהנפיקו הכי הרבה החלטות'],
    priority: 7
  },

  // Content search with date range - FIXED
  CONTENT_SEARCH_DATE_RANGE: {
    name: 'חיפוש בתוכן עם טווח תאריכים',
    description: 'חיפוש מילה בתוכן בטווח תאריכים',
    pattern: /['"]([^'"]+)['"]\s+בין\s+(\d{4})[-\s]?(\d{4})?/,
    sql: (term: string, fromYear: string, toYear?: string) => {
      const endYear = toYear || fromYear;
      return `
        SELECT * FROM israeli_government_decisions
        WHERE (decision_content ILIKE $1 
           OR summary ILIKE $2 
           OR decision_title ILIKE $3)
        AND decision_date BETWEEN $4 AND $5
        ORDER BY decision_date DESC
      `;
    },
    params: (term: string, fromYear: string, toYear?: string) => {
      const searchTerm = `%${term}%`;
      const endYear = toYear || fromYear;
      return [
        searchTerm,
        searchTerm,
        searchTerm,
        `${fromYear}-01-01`,
        `${endYear}-12-31`
      ];
    },
    expectedType: 'multiple',
    examples: ["'קורונה' בין 2020-2021", "'תקציב' בין 2023-2024"],
    priority: 7
  },

  // Statistics by government
  GOVERNMENT_STATISTICS: {
    name: 'סטטיסטיקת ממשלה',
    description: 'סטטיסטיקה על ממשלה מסוימת',
    pattern: /סטטיסטיק(?:ה|ות)\s+(?:של\s+|על\s+)?ממשלה\s+(\d+)/,
    sql: (_gov: string) => `SELECT * FROM get_government_statistics($1)`,
    params: (gov: string) => [parseInt(gov)],
    expectedType: 'aggregate',
    examples: ['סטטיסטיקה של ממשלה 36', 'סטטיסטיקות על ממשלה 37'],
    priority: 5
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
    examples: ['ההחלטות האחרונות', 'החלטות מהשבוע האחרון'],
    priority: 5
  },

  // X recent decisions - NEW
  X_RECENT_DECISIONS: {
    name: 'X החלטות אחרונות',
    description: 'מספר מדויק של החלטות אחרונות',
    pattern: /(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות(?:\s+אחרונות)?$/,
    sql: (count: string) => `
      SELECT * FROM israeli_government_decisions 
      ORDER BY decision_date DESC
      LIMIT ${parseInt(count)}
    `,
    params: () => [],
    expectedType: 'multiple',
    examples: ['הבא 20 החלטות', 'תן לי 50 החלטות אחרונות'],
    priority: 8
  },

  // Search in content
  CONTENT_SEARCH: {
    name: 'חיפוש בתוכן',
    description: 'חיפוש טקסט חופשי בתוכן ההחלטות',
    pattern: /חפש\s+(?:את\s+)?(?:המילה\s+|הביטוי\s+)?["']([^"']+)["']/,
    sql: (_searchTerm: string) => `SELECT * FROM search_decisions_hebrew($1)`,
    params: (searchTerm: string) => [searchTerm],
    expectedType: 'multiple',
    examples: ['חפש "קורונה"', 'חפש את המילה "חינוך חינם"'],
    priority: 5
  },

  // Simple text search (new pattern)
  SIMPLE_TEXT_SEARCH: {
    name: 'חיפוש טקסט פשוט',
    description: 'חיפוש טקסט בתוכן ההחלטות',
    pattern: /^["']([^"']+)["']$/,
    sql: (searchTerm: string) => `
      SELECT * FROM israeli_government_decisions
      WHERE decision_content ILIKE $1 
         OR summary ILIKE $2 
         OR decision_title ILIKE $3
      ORDER BY decision_date DESC
    `,
    params: (searchTerm: string) => {
      const term = `%${searchTerm}%`;
      return [term, term, term];
    },
    expectedType: 'multiple',
    examples: ['"קורונה"', '"חינוך חינם"'],
    priority: 6
  },

  // Count per government
  COUNT_PER_GOVERNMENT: {
    name: 'ספירה לפי ממשלה',
    description: 'כמה החלטות קיבלה כל ממשלה',
    pattern: /כמה\s+החלטות\s+קיבלה\s+כל\s+ממשלה/,
    sql: () => `SELECT * FROM count_decisions_per_government()`,
    params: () => [],
    expectedType: 'aggregate',
    examples: ['כמה החלטות קיבלה כל ממשלה?'],
    priority: 5
  },

  // Decisions by prime minister - LOWER PRIORITY than committee
  DECISIONS_BY_PM: {
    name: 'החלטות לפי ראש ממשלה',
    description: 'החלטות של ראש ממשלה מסוים',
    pattern: /החלטות\s+של\s+([\u0590-\u05FF\s]+?)(?:\s|$)/,
    sql: (_pmName: string) => `SELECT * FROM get_decisions_by_prime_minister($1)`,
    params: (pmName: string) => [pmName.trim()],
    expectedType: 'multiple',
    examples: ['החלטות של נתניהו'],
    priority: 3 // Lower priority than committee pattern
  },

  // Important decisions by year
  IMPORTANT_BY_YEAR: {
    name: 'החלטות חשובות לפי שנה',
    description: 'ההחלטות החשובות ביותר של שנה מסוימת',
    pattern: /(?:מה\s+)?(?:הן\s+)?(?:ה)?החלטות\s+החשובות\s+(?:ביותר\s+)?(?:של\s+)?(?:ב?)?(\d{4})/,
    sql: (_year: string) => `SELECT * FROM get_important_decisions_by_year($1)`,
    params: (year: string) => [parseInt(year)],
    expectedType: 'multiple',
    examples: ['מה ההחלטות החשובות ביותר של 2024?'],
    priority: 5
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
    `,
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['החלטות בנושא חינוך מהשנה האחרונה'],
    priority: 5
  },

  

  // Count decisions by government and topic - FIXED
  COUNT_BY_GOVERNMENT_AND_TOPIC: {
    name: 'ספירת החלטות לפי ממשלה ונושא',
    description: 'כמה החלטות בנושא מסוים החליטה ממשלה מסוימת',
    pattern: /כמה\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+(?:החליטה|קיבלה|התקבלו(?:\s+ב)?)\s*ממשלה\s+(?:מס(?:פר)?\.?\s*)?(\d+)/i,
    sql: (_topic: string, _gov: string) => `
    SELECT
      COUNT(*)            AS count,
      $1                  AS topic,
      $2                  AS government_number,
      MIN(decision_date)  AS first_decision,
      MAX(decision_date)  AS last_decision,
      MAX(prime_minister) AS prime_minister
    FROM israeli_government_decisions
    WHERE tags_policy_area ILIKE $3
      AND (government_number = $2 OR government_number = $2 || '.0')
  `,

    // 1-topic | 2-gov | 3-LIKE-pattern
    params: (topic: string, gov: string) => [
      topic.trim(),                       // $1
      gov,                                // $2
      `%${topic.trim()}%`                 // $3
    ],
    expectedType: 'count',
    examples: ['כמה החלטות בנושא חינוך החליטה ממשלה מס 37', 'כמה החלטות בנושא ביטחון קיבלה ממשלה 37'],
    priority: 10 // Higher priority to match before COUNT_BY_TOPIC
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
    examples: ['כמה החלטות בנושא חינוך עברו בין 2020 ל2022'],
    priority: 5
  },

  // PM topic count
  PM_TOPIC_COUNT: {
    name: 'ספירת החלטות ראש ממשלה בנושא',
    description: 'כמה החלטות קיבל ראש ממשלה בנושא מסוים',
    pattern: /כמה\s+החלטות\s+(?:קיבל|החליט|עשה)\s+([\u0590-\u05FF\s]+?)\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    sql: (pm: string, topic: string) => `
      SELECT 
        COUNT(*) as count,
        $1 as prime_minister,
        $2 as topic
      FROM israeli_government_decisions
      WHERE prime_minister ILIKE $3
      AND (tags_policy_area ILIKE $4 OR all_tags ILIKE $5)
    `,
    params: (pm: string, topic: string) => [
      pm.trim(),
      topic.trim(),
      `%${pm.trim()}%`,
      `%${topic.trim()}%`,
      `%${topic.trim()}%`
    ],
    expectedType: 'count',
    examples: ['כמה החלטות קיבל נתניהו בנושא ביטחון?'],
    priority: 6
  },

  // Contextual follow-up queries
  CONTEXTUAL_TOPIC: {
    name: 'שאילתת המשך נושא',
    description: 'שאילתת המשך על נושא',
    pattern: /^ו?בנושא\s+([\u0590-\u05FF\s]+)\??$/,
    sql: (_topic: string) => `
      SELECT * FROM israeli_government_decisions 
      WHERE tags_policy_area ILIKE $1
      ORDER BY decision_date DESC
      LIMIT 20
    `,
    params: (topic: string) => [`%${topic.trim()}%`],
    expectedType: 'multiple',
    examples: ['ובנושא רפואה?', 'בנושא חינוך?'],
    priority: 12
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

// Find matching template with priority
export function findMatchingTemplate(query: string): {
  template: QueryTemplate;
  matches: string[];
} | null {
  // Sort templates by priority (higher first)
  const sortedTemplates = Object.entries(QUERY_TEMPLATES)
    .sort(([_a, templateA], [_b, templateB]) => 
      (templateB.priority || 0) - (templateA.priority || 0)
    );

  for (const [_key, template] of sortedTemplates) {
    const match = query.match(template.pattern);
    if (match) {
      console.log(`[QueryTemplates] Matched template: ${template.name} (priority: ${template.priority || 0})`);
      return {
        template,
        matches: match.slice(1) // Remove full match, keep capture groups
      };
    }
  }
  return null;
}
