/**
 * Main Entry Point for Macro Filter View Dashboard
 * Hebrew Government Decisions Statistics Dashboard
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import DashboardLayout from './components/layout/DashboardLayout';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
    },
    mutations: {
      retry: 1,
    },
  },
});

export default function MacroFilterViewDashboard() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50" dir="rtl">
        <DashboardLayout />
      </div>
      
      {/* Development tools - only in dev mode */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}

// Export components for external use
export { default as FilterPanel } from './components/filters/FilterPanel';
export { default as KPICards } from './components/charts/KPICards';
export { default as TimelineChart } from './components/charts/TimelineChart';
export { default as PolicyDistributionChart } from './components/charts/PolicyDistributionChart';
export { default as CommitteeActivityChart } from './components/charts/CommitteeActivityChart';
export { default as DataTable } from './components/shared/DataTable';
export { default as MobileFilterDrawer } from './components/shared/MobileFilterDrawer';

// Export types
export type {
  DashboardFilters,
  DashboardDecision,
  DashboardStats,
  FilterOptions,
} from './types/decision';

// Export utilities
export {
  getDefaultFilters,
  countActiveFilters,
  formatHebrewDate,
  formatHebrewNumber,
} from './utils/dataTransformers';