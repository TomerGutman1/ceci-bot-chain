/**
 * API Service for Hebrew Government Decisions Dashboard
 * Connects to existing CECI backend at localhost:5001
 */

import axios from 'axios';
import type {
  GovernmentDecision,
  DashboardFilters,
  DecisionsResponse,
  StatsResponse,
  FilterOptions,
  DashboardStats,
  TimelineStat,
  PolicyAreaStat,
  CommitteeStat
} from '../types/decision';

// Base API configuration
// Use relative URL so nginx can proxy to backend
const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error);
    if (error.response?.status === 404) {
      throw new Error('המשאב המבוקש לא נמצא');
    } else if (error.response?.status >= 500) {
      throw new Error('שגיאה בשרת. אנא נסה שוב מאוחר יותר');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('הבקשה לקחה יותר מדי זמן. אנא נסה שוב');
    }
    throw error;
  }
);

/**
 * Convert dashboard filters to API query parameters
 */
function filtersToParams(filters: DashboardFilters): Record<string, any> {
  const params: Record<string, any> = {};

  if (filters.governments.length > 0) {
    params.government = filters.governments[0]; // Backend expects single government
  }

  if (filters.committees.length > 0) {
    params.committee = filters.committees[0]; // Backend expects single committee
  }

  if (filters.policyAreas.length > 0) {
    params.policyArea = filters.policyAreas[0]; // Backend expects single policy area
  }

  if (filters.primeMinister) {
    params.primeMinister = filters.primeMinister;
  }

  if (filters.dateRange.start) {
    params.startDate = filters.dateRange.start.toISOString().split('T')[0];
  }

  if (filters.dateRange.end) {
    params.endDate = filters.dateRange.end.toISOString().split('T')[0];
  }

  if (filters.decisionType !== 'all') {
    params.operativity = filters.decisionType === 'operative' ? 'אופרטיבית' : 'דקלרטיבית';
  }

  return params;
}

/**
 * Fetch paginated decisions with filters
 */
export async function fetchDecisions(
  filters: DashboardFilters,
  page: number = 1,
  limit: number = 50
): Promise<DecisionsResponse> {
  try {
    const params = {
      ...filtersToParams(filters),
      page,
      limit,
    };

    const response = await apiClient.get('/statistics/decisions', { params });
    
    return {
      decisions: response.data.decisions || [],
      total: response.data.pagination?.total || 0,
      page: response.data.pagination?.page || page,
      limit: response.data.pagination?.limit || limit,
      hasMore: (response.data.pagination?.page || page) < (response.data.pagination?.totalPages || 1),
    };
  } catch (error) {
    console.error('Error fetching decisions:', error);
    throw error;
  }
}

/**
 * Fetch dashboard statistics based on current filters
 */
export async function fetchStatistics(filters: DashboardFilters): Promise<StatsResponse> {
  try {
    const params = filtersToParams(filters);
    const response = await apiClient.get('/statistics/overview', { params });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    throw error;
  }
}

/**
 * Fetch available filter options (for dropdowns and autocomplete)
 */
export async function fetchFilterOptions(): Promise<FilterOptions> {
  try {
    const response = await apiClient.get('/statistics/filter-options');
    
    // Transform the response to match frontend expectations
    return {
      governments: response.data.governments.map((gov: any) => ({
        number: parseInt(gov.value),
        primeMinister: gov.label || `ממשלה ${gov.value}`,
        period: '' // Backend doesn't provide this yet
      })),
      committees: response.data.committees.map((c: any) => c.value || c),
      policyAreas: response.data.policyAreas.map((p: any) => p.value || p),
      primeMinister: response.data.primeMinisters.map((pm: any) => pm.value || pm),
      locations: [] // Not provided by backend yet
    };
  } catch (error) {
    console.error('Error fetching filter options:', error);
    throw error;
  }
}

/**
 * Fetch overview statistics (for KPI cards)
 */
export async function fetchOverviewStats(filters: DashboardFilters): Promise<DashboardStats> {
  try {
    const params = filtersToParams(filters);
    const response = await apiClient.get('/statistics/overview', { params });
    
    // Transform backend response to match frontend expectations
    const data = response.data;
    return {
      total: data.totalDecisions || 0,
      operational: data.operativeDecisions || 0,
      declarative: data.nonOperativeDecisions || 0,
      avgPerMonth: data.averageDecisionsPerMonth || 0,
      mostActiveCommittee: '', // Not provided by backend
      policyCoverageScore: 0, // Not provided by backend
      periodComparison: {
        current: data.recentDecisions || 0,
        previous: 0, // Not provided by backend
        changePercent: 0 // Not provided by backend
      }
    };
  } catch (error) {
    console.error('Error fetching overview stats:', error);
    throw error;
  }
}

/**
 * Helper function to convert Hebrew month names to month indices
 */
function getMonthIndex(hebrewMonth: string): number {
  const monthMap: { [key: string]: number } = {
    'ינואר': 0,
    'פברואר': 1,
    'מרץ': 2,
    'אפריל': 3,
    'מאי': 4,
    'יוני': 5,
    'יולי': 6,
    'אוגוסט': 7,
    'ספטמבר': 8,
    'אוקטובר': 9,
    'נובמבר': 10,
    'דצמבר': 11,
  };
  return monthMap[hebrewMonth] ?? 0;
}

/**
 * Fetch timeline data for charts
 */
export async function fetchTimelineData(
  filters: DashboardFilters,
  granularity: 'day' | 'month' | 'year' = 'month'
): Promise<TimelineStat[]> {
  try {
    const params = {
      ...filtersToParams(filters),
      granularity,
    };
    const response = await apiClient.get('/statistics/timeline', { params });
    return response.data.map((item: any) => ({
      // Construct date from month and year
      date: new Date(item.year, getMonthIndex(item.month), 1),
      count: item.count,
      // Map field names to match frontend expectations
      operationalCount: item.operativeCount,
      declarativeCount: item.nonOperativeCount,
    }));
  } catch (error) {
    console.error('Error fetching timeline data:', error);
    throw error;
  }
}

/**
 * Fetch policy area distribution for pie charts
 */
export async function fetchPolicyAreaStats(filters: DashboardFilters): Promise<PolicyAreaStat[]> {
  try {
    const params = filtersToParams(filters);
    const response = await apiClient.get('/statistics/policy-areas', { params });
    
    // Transform backend response to match frontend expectations
    return response.data.map((item: any) => ({
      area: item.name,
      count: item.count,
      percentage: item.percentage
    }));
  } catch (error) {
    console.error('Error fetching policy area stats:', error);
    throw error;
  }
}

/**
 * Fetch committee activity statistics
 */
export async function fetchCommitteeStats(filters: DashboardFilters): Promise<CommitteeStat[]> {
  try {
    const params = filtersToParams(filters);
    const response = await apiClient.get('/statistics/committees', { params });
    
    // Transform backend response to match frontend expectations
    return response.data.map((item: any) => ({
      committee: item.name,
      count: item.count,
      percentage: item.percentage,
      recentActivity: 0 // Not provided by backend
    }));
  } catch (error) {
    console.error('Error fetching committee stats:', error);
    throw error;
  }
}

/**
 * Search for specific decisions (autocomplete/search functionality)
 */
export async function searchDecisions(
  query: string,
  limit: number = 10
): Promise<GovernmentDecision[]> {
  try {
    const response = await apiClient.get('/decisions/search', {
      params: { q: query, limit },
    });
    return response.data.decisions || [];
  } catch (error) {
    console.error('Error searching decisions:', error);
    throw error;
  }
}

/**
 * Export decisions data in various formats
 */
export async function exportDecisions(
  filters: DashboardFilters,
  format: 'csv' | 'excel' = 'csv'
): Promise<Blob> {
  try {
    const body = {
      filters: filtersToParams(filters),
      format,
    };
    
    const response = await apiClient.post('/statistics/export', body, {
      responseType: 'blob',
    });
    
    return response.data;
  } catch (error) {
    console.error('Error exporting decisions:', error);
    throw error;
  }
}

/**
 * Health check for API connectivity
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
}

/**
 * Get aggregated statistics for specific government(s)
 */
export async function fetchGovernmentComparison(
  governmentNumbers: number[]
): Promise<any> {
  try {
    const response = await apiClient.get('/statistics/governments', {
      params: { governments: governmentNumbers.join(',') },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching government comparison:', error);
    throw error;
  }
}

// Default export for the API client
export default apiClient;