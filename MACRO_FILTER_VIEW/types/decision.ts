/**
 * TypeScript interfaces for Israeli Government Decisions Dashboard
 * Based on israeli_government_decisions database schema
 */

// Core decision data structure from database
export interface GovernmentDecision {
  id: number;
  decision_date: string; // ISO-8601 date format
  decision_number: string;
  government_number: string;
  prime_minister: string;
  committee: string | null;
  decision_title: string;
  summary: string;
  decision_content: string;
  operativity: 'אופרטיבית' | 'דקלרטיבית';
  tags_policy_area: string | null; // Comma-separated values
  tags_government_body: string | null; // Comma-separated values
  tags_location: string | null; // Comma-separated values
  all_tags: string;
  decision_url: string;
  decision_key: string; // Format: "<government_number>_<decision_number>"
  embedding: number[] | null; // Vector for future RAG
  created_at: string;
  updated_at: string;
}

// Parsed and processed decision for dashboard use
export interface DashboardDecision {
  id: number;
  title: string;
  number: string;
  date: Date;
  government: number;
  primeMinister: string;
  committee: string | null;
  summary: string;
  content: string;
  type: 'אופרטיבית' | 'דקלרטיבית';
  policyAreas: string[];
  governmentBodies: string[];
  locations: string[];
  url: string;
  key: string;
}

// Filter interfaces
export interface DateRange {
  start: Date | null;
  end: Date | null;
}

export interface DashboardFilters {
  governments: number[];
  committees: string[];
  policyAreas: string[];
  primeMinister: string | null;
  dateRange: DateRange;
  locations: string[];
  decisionType: 'אופרטיבית' | 'דקלרטיבית' | 'all';
  searchText: string;
}

// Statistics interfaces
export interface PolicyAreaStat {
  area: string;
  count: number;
  percentage: number;
}

export interface GovernmentStat {
  governmentNumber: number;
  primeMinister: string;
  totalDecisions: number;
  operationalCount: number;
  declarativeCount: number;
  dateRange: {
    start: Date;
    end: Date;
  };
}

export interface CommitteeStat {
  committee: string;
  count: number;
  percentage: number;
  recentActivity: number; // Last 30 days
}

export interface TimelineStat {
  date: Date;
  count: number;
  operationalCount: number;
  declarativeCount: number;
}

export interface DashboardStats {
  total: number;
  operational: number;
  declarative: number;
  avgPerMonth: number;
  mostActiveCommittee: string;
  policyCoverageScore: number;
  periodComparison: {
    current: number;
    previous: number;
    changePercent: number;
  };
}

// Chart data interfaces
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TimelineChartData {
  date: string;
  total: number;
  operational: number;
  declarative: number;
}

export interface PolicyDistributionData {
  name: string;
  value: number;
  count: number;
  color: string;
}

// API Response types
export interface DecisionsResponse {
  decisions: GovernmentDecision[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface StatsResponse {
  overview: DashboardStats;
  timeline: TimelineStat[];
  policyAreas: PolicyAreaStat[];
  committees: CommitteeStat[];
  governments: GovernmentStat[];
}

// Filter options for dropdowns
export interface FilterOptions {
  governments: Array<{
    number: number;
    primeMinister: string;
    period: string;
  }>;
  committees: string[];
  policyAreas: string[];
  primeMinister: string[];
  locations: string[];
}

// User preferences
export interface UserPreferences {
  defaultView: 'cards' | 'table' | 'list';
  chartsConfiguration: {
    [key: string]: {
      visible: boolean;
      position: number;
      size: 'small' | 'medium' | 'large';
    };
  };
  filterPresets: Array<{
    name: string;
    filters: DashboardFilters;
    isDefault: boolean;
  }>;
  theme: 'light' | 'dark' | 'auto';
}

// Export/sharing types
export interface ExportConfig {
  format: 'csv' | 'excel' | 'pdf';
  includeCharts: boolean;
  dateRange: DateRange;
  filters: DashboardFilters;
  selectedFields: string[];
}

export interface ShareableReport {
  id: string;
  title: string;
  description: string;
  filters: DashboardFilters;
  chartConfig: UserPreferences['chartsConfiguration'];
  isPublic: boolean;
  expiresAt: Date | null;
  createdAt: Date;
}