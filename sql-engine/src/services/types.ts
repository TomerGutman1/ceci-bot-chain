/**
 * TypeScript type definitions for SQL Query Engine
 */

export interface Decision {
  decision_number: string;
  decision_title?: string;
  decision_date: string;
  government_number: number;
  prime_minister?: string;
  tags_policy_area?: string;
  tags_government_body?: string;
  summary?: string;
  decision_content?: string;
  decision_url?: string;
  year?: number;
  month?: number;
  decision_key?: string;
  operativity?: string;
}

export interface QueryRequest {
  query: string;
  sessionId?: string;
  parameters?: Record<string, any>;
}

export interface QueryResponse {
  success: boolean;
  type: 'single' | 'multiple' | 'count' | 'aggregate' | 'error';
  data: Decision | Decision[] | CountResult | AggregateResult | null;
  formatted: string;
  metadata?: QueryMetadata;
  error?: string;
}

export interface QueryMetadata {
  sql_query?: string;
  execution_time?: number;
  row_count?: number;
  session_id?: string;
  query_id?: string;
  confidence?: number;
  template_used?: string;
}

export interface CountResult {
  count: number;
  year?: number;
  topic?: string;
  governments_count?: number;
  topics_count?: number;
  first_decision?: string;
  last_decision?: string;
}

export interface AggregateResult {
  government_number: number;
  prime_minister?: string;
  total_decisions: number;
  first_decision?: string;
  last_decision?: string;
  policy_areas?: string[];
  unique_policy_combinations?: number;
}

export interface HealthCheckResult {
  healthy: boolean;
  database_connected: boolean;
  converter_working: boolean;
  statistics?: {
    total_decisions: number;
    most_recent_decision: string;
  };
}

export interface SchemaInfo {
  table: string;
  columns: ColumnInfo[];
  total_columns: number;
  searchable_columns: string[];
  indexes: string[];
}

export interface ColumnInfo {
  name: string;
  type: string;
  hebrew_name: string;
  description: string;
}
