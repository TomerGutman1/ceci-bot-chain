/**
 * React Query hooks for dashboard data fetching
 * Provides caching, loading states, and error handling
 */

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchDecisions,
  fetchStatistics,
  fetchFilterOptions,
  fetchOverviewStats,
  fetchTimelineData,
  fetchPolicyAreaStats,
  fetchCommitteeStats,
  searchDecisions,
  exportDecisions,
  checkApiHealth,
  fetchGovernmentComparison
} from '../services/api';
import type { DashboardFilters } from '../types/decision';

// Query keys for consistent caching
export const queryKeys = {
  decisions: (filters: DashboardFilters, page?: number) => 
    ['decisions', filters, page] as const,
  statistics: (filters: DashboardFilters) => 
    ['statistics', filters] as const,
  overview: (filters: DashboardFilters) => 
    ['overview', filters] as const,
  timeline: (filters: DashboardFilters, granularity: string) => 
    ['timeline', filters, granularity] as const,
  policyAreas: (filters: DashboardFilters) => 
    ['policyAreas', filters] as const,
  committees: (filters: DashboardFilters) => 
    ['committees', filters] as const,
  filterOptions: () => ['filterOptions'] as const,
  search: (query: string) => ['search', query] as const,
  health: () => ['health'] as const,
  governmentComparison: (governments: number[]) => 
    ['governmentComparison', governments] as const,
};

/**
 * Hook for fetching paginated decisions with infinite scroll support
 */
export function useDecisions(filters: DashboardFilters, limit: number = 50) {
  return useInfiniteQuery({
    queryKey: queryKeys.decisions(filters),
    queryFn: ({ pageParam = 1 }) => fetchDecisions(filters, pageParam, limit),
    getNextPageParam: (lastPage) => 
      lastPage.hasMore ? lastPage.page + 1 : undefined,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes cache
  });
}

/**
 * Hook for single page of decisions (for table view)
 */
export function useDecisionsPage(
  filters: DashboardFilters, 
  page: number = 1, 
  limit: number = 50
) {
  return useQuery({
    queryKey: queryKeys.decisions(filters, page),
    queryFn: () => fetchDecisions(filters, page, limit),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook for complete dashboard statistics
 */
export function useStatistics(filters: DashboardFilters) {
  return useQuery({
    queryKey: queryKeys.statistics(filters),
    queryFn: () => fetchStatistics(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes for statistics
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook for overview KPI statistics
 */
export function useOverviewStats(filters: DashboardFilters) {
  return useQuery({
    queryKey: queryKeys.overview(filters),
    queryFn: () => fetchOverviewStats(filters),
    staleTime: 1 * 60 * 1000, // 1 minute for overview
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook for timeline chart data
 */
export function useTimelineData(
  filters: DashboardFilters, 
  granularity: 'day' | 'month' | 'year' = 'month'
) {
  return useQuery({
    queryKey: queryKeys.timeline(filters, granularity),
    queryFn: () => fetchTimelineData(filters, granularity),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook for policy area distribution
 */
export function usePolicyAreaStats(filters: DashboardFilters) {
  return useQuery({
    queryKey: queryKeys.policyAreas(filters),
    queryFn: () => fetchPolicyAreaStats(filters),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook for committee activity statistics
 */
export function useCommitteeStats(filters: DashboardFilters) {
  return useQuery({
    queryKey: queryKeys.committees(filters),
    queryFn: () => fetchCommitteeStats(filters),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook for filter options (cached for long periods)
 */
export function useFilterOptions() {
  return useQuery({
    queryKey: queryKeys.filterOptions(),
    queryFn: fetchFilterOptions,
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Hook for search functionality with debouncing
 */
export function useSearchDecisions(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: queryKeys.search(query),
    queryFn: () => searchDecisions(query),
    enabled: enabled && query.length >= 2, // Only search if query is at least 2 characters
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook for API health monitoring
 */
export function useApiHealth() {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: checkApiHealth,
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 60 * 1000, // 1 minute
    refetchInterval: 30 * 1000, // Check every 30 seconds
  });
}

/**
 * Hook for government comparison data
 */
export function useGovernmentComparison(governments: number[]) {
  return useQuery({
    queryKey: queryKeys.governmentComparison(governments),
    queryFn: () => fetchGovernmentComparison(governments),
    enabled: governments.length > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 20 * 60 * 1000,
  });
}

/**
 * Mutation hook for exporting data
 */
export function useExportDecisions() {
  return useMutation({
    mutationFn: ({ filters, format }: { 
      filters: DashboardFilters; 
      format: 'csv' | 'excel' 
    }) => exportDecisions(filters, format),
    onSuccess: (blob, { format }) => {
      // Auto-download the exported file
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `government-decisions.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
  });
}

/**
 * Custom hook for invalidating cache when filters change
 */
export function useInvalidateCache() {
  const queryClient = useQueryClient();

  const invalidateDecisions = () => {
    queryClient.invalidateQueries({ queryKey: ['decisions'] });
  };

  const invalidateStatistics = () => {
    queryClient.invalidateQueries({ queryKey: ['statistics'] });
    queryClient.invalidateQueries({ queryKey: ['overview'] });
    queryClient.invalidateQueries({ queryKey: ['timeline'] });
    queryClient.invalidateQueries({ queryKey: ['policyAreas'] });
    queryClient.invalidateQueries({ queryKey: ['committees'] });
  };

  const invalidateAll = () => {
    queryClient.invalidateQueries();
  };

  return {
    invalidateDecisions,
    invalidateStatistics,
    invalidateAll,
  };
}

/**
 * Hook for managing loading states across multiple queries
 */
export function useDashboardLoading(filters: DashboardFilters) {
  const overviewQuery = useOverviewStats(filters);
  const timelineQuery = useTimelineData(filters);
  const policyQuery = usePolicyAreaStats(filters);
  const committeeQuery = useCommitteeStats(filters);

  const isLoading = [
    overviewQuery.isLoading,
    timelineQuery.isLoading,
    policyQuery.isLoading,
    committeeQuery.isLoading,
  ].some(Boolean);

  const hasError = [
    overviewQuery.error,
    timelineQuery.error,
    policyQuery.error,
    committeeQuery.error,
  ].some(Boolean);

  const isReady = [
    overviewQuery.data,
    timelineQuery.data,
    policyQuery.data,
    committeeQuery.data,
  ].every(Boolean);

  return {
    isLoading,
    hasError,
    isReady,
    errors: {
      overview: overviewQuery.error,
      timeline: timelineQuery.error,
      policy: policyQuery.error,
      committee: committeeQuery.error,
    },
  };
}