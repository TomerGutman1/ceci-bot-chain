/**
 * Schema definition for Israeli Government Decisions database
 * Used for SQL generation and validation
 */

export interface ColumnDefinition {
  name: string;
  type: 'text' | 'integer' | 'date' | 'timestamp' | 'boolean';
  description: string;
  hebrew_name: string;
  searchable?: boolean;
  examples?: string[];
  notes?: string;
  computed?: boolean;
  current_value?: any;
}

export interface SchemaDefinition {
  table_name: string;
  columns: ColumnDefinition[];
  indexes: string[];
  full_text_search: string[];
  constraints?: string[];
}

export const DECISIONS_SCHEMA: SchemaDefinition = {
  table_name: 'israeli_government_decisions',
  columns: [
    {
      name: 'decision_number',
      type: 'text',
      description: 'Decision number - unique per government',
      hebrew_name: 'מספר החלטה',
      examples: ['660', '1234', '100'],
      notes: 'Resets with each new government',
      searchable: true
    },
    {
      name: 'decision_title',
      type: 'text',
      description: 'Title of the decision',
      hebrew_name: 'כותרת ההחלטה',
      searchable: true
    },
    {
      name: 'decision_date',
      type: 'date',
      description: 'Date the decision was made',
      hebrew_name: 'תאריך ההחלטה',
      examples: ['2023-01-15', '2024-06-22']
    },
    {
      name: 'government_number',
      type: 'integer',
      description: 'Government number',
      hebrew_name: 'מספר ממשלה',
      current_value: 37,
      examples: ['35', '36', '37']
    },
    {
      name: 'prime_minister',
      type: 'text',
      description: 'Name of the Prime Minister',
      hebrew_name: 'ראש הממשלה',
      examples: ['בנימין נתניהו', 'נפתלי בנט', 'יאיר לפיד']
    },
    {
      name: 'tags_policy_area',
      type: 'text',
      description: 'Policy areas separated by semicolon',
      hebrew_name: 'תחומי מדיניות',
      searchable: true,
      examples: ['חינוך', 'בריאות', 'תחבורה', 'ביטחון'],
      notes: 'Multiple tags separated by ;'
    },
    {
      name: 'tags_government_body',
      type: 'text',
      description: 'Government bodies involved',
      hebrew_name: 'גופים ממשלתיים',
      searchable: true,
      examples: ['משרד החינוך', 'משרד הבריאות']
    },
    {
      name: 'summary',
      type: 'text',
      description: 'Summary of the decision',
      hebrew_name: 'תקציר',
      searchable: true
    },
    {
      name: 'decision_content',
      type: 'text',
      description: 'Full content of the decision',
      hebrew_name: 'תוכן ההחלטה',
      searchable: true,
      notes: 'May be very long'
    },
    {
      name: 'decision_url',
      type: 'text',
      description: 'URL to the decision',
      hebrew_name: 'קישור להחלטה'
    },
    {
      name: 'year',
      type: 'integer',
      description: 'Year extracted from decision_date',
      hebrew_name: 'שנה',
      computed: true,
      examples: ['2023', '2024']
    },
    {
      name: 'month',
      type: 'integer',
      description: 'Month extracted from decision_date',
      hebrew_name: 'חודש',
      computed: true,
      examples: ['1', '12']
    },
    {
      name: 'decision_key',
      type: 'text',
      description: 'Composite key: government_decision',
      hebrew_name: 'מפתח משולב',
      computed: true,
      examples: ['37_660', '35_1234']
    }
  ],
  indexes: [
    'decision_number',
    'government_number',
    'year',
    'decision_date',
    'decision_key'
  ],
  full_text_search: [
    'decision_title',
    'summary',
    'tags_policy_area',
    'decision_content'
  ],
  constraints: [
    'decision_key is unique',
    'government_number is not null',
    'decision_date is not null'
  ]
};

// Helper functions for schema
export function getSearchableColumns(): string[] {
  return DECISIONS_SCHEMA.columns
    .filter(col => col.searchable)
    .map(col => col.name);
}

export function getColumnByName(name: string): ColumnDefinition | undefined {
  return DECISIONS_SCHEMA.columns.find(col => col.name === name);
}

export function getHebrewColumnNames(): Record<string, string> {
  const mapping: Record<string, string> = {};
  DECISIONS_SCHEMA.columns.forEach(col => {
    mapping[col.hebrew_name] = col.name;
    mapping[col.name] = col.hebrew_name;
  });
  return mapping;
}
