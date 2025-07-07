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
const API_BASE_URL = 'http://localhost:5001/api';

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
    params.governments = filters.governments.join(',');
  }

  if (filters.committees.length > 0) {
    params.committees = filters.committees.join(',');
  }

  if (filters.policyAreas.length > 0) {
    params.policy_areas = filters.policyAreas.join(',');
  }

  if (filters.primeMinister) {
    params.prime_minister = filters.primeMinister;
  }

  if (filters.dateRange.start) {
    params.date_start = filters.dateRange.start.toISOString().split('T')[0];
  }

  if (filters.dateRange.end) {
    params.date_end = filters.dateRange.end.toISOString().split('T')[0];
  }

  if (filters.locations.length > 0) {
    params.locations = filters.locations.join(',');
  }

  if (filters.decisionType !== 'all') {
    params.operativity = filters.decisionType;
  }

  if (filters.searchText.trim()) {
    params.search = filters.searchText.trim();
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

    const response = await apiClient.get('/decisions', { params });
    
    return {
      decisions: response.data.decisions || [],
      total: response.data.total || 0,
      page: response.data.page || page,
      limit: response.data.limit || limit,
      hasMore: response.data.hasMore || false,
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
    const response = await apiClient.get('/statistics', { params });
    
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
    const response = await apiClient.get('/filter-options');
    return response.data;
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
    return response.data;
  } catch (error) {
    console.error('Error fetching overview stats:', error);
    throw error;
  }
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
      ...item,
      date: new Date(item.date),
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
    return response.data;
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
    return response.data;
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
    const params = {
      ...filtersToParams(filters),
      format,
    };
    
    const response = await apiClient.get('/decisions/export', {
      params,
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