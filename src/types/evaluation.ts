// Additional type definitions for evaluation.ts

export interface Decision {
  num: string;
  date: string;
  pathname: string;
  title: string | null;
  content: string | null;
  summary: string | null;
  gov_num: number;
  prime_minister: string | null;
  committee: string | null;
  operativity: boolean;
  field: string | null;
  offices: string | null;
  created_at: string;
  updated_at: string;
  evaluation?: EvaluationResult;
}

export interface EvaluationResult {
  id?: string;
  decisionNumber?: string;
  decisionDate?: string;
  governmentNumber?: number;
  parameters: EvaluationParameter[];
  totalScore: number;
  evaluationText: string;
  createdAt: Date;
  updatedAt?: Date;
}

export interface EvaluationParameter {
  name: string;
  hebrewName: string;
  score: number; // 0-5
  weight: number; // percentage
  description: string;
}

export interface DecisionEvaluation {
  id: string;
  decision_num: string;
  decision_date: string;
  eval: string;
  created_at: string;
  updated_at: string;
}

// Evaluation parameters based on EVALUATION_PROMPT
export const EVALUATION_PARAMETERS = [
  { key: 'timeline', hebrewName: 'לוח זמנים מחייב', weight: 17 },
  { key: 'coordinating_team', hebrewName: 'צוות מתכלל', weight: 7 },
  { key: 'single_coordinator', hebrewName: 'גורם מתכלל יחיד', weight: 5 },
  { key: 'reporting_mechanism', hebrewName: 'מנגנון דיווח/בקרה', weight: 9 },
  { key: 'measurement_mechanism', hebrewName: 'מנגנון מדידה והערכה', weight: 6 },
  { key: 'external_audit', hebrewName: 'מנגנון ביקורת חיצונית', weight: 4 },
  { key: 'required_resources', hebrewName: 'משאבים נדרשים', weight: 19 },
  { key: 'multi_level_involvement', hebrewName: 'מעורבות של מספר דרגים', weight: 7 },
  { key: 'clear_structure', hebrewName: 'מבנה סעיפים וחלוקת עבודה', weight: 9 },
  { key: 'implementation_mechanism', hebrewName: 'מנגנון יישום בשטח', weight: 9 },
  { key: 'decision_maker', hebrewName: 'גורם מכריע', weight: 3 },
  { key: 'cross_sector_partnership', hebrewName: 'שותפות בין מגזרית', weight: 3 },
  { key: 'success_metrics', hebrewName: 'מדדי תוצאה ומרכיבי הצלחה', weight: 2 },
];
