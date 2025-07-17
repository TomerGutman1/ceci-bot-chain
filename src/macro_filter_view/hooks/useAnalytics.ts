/**
 * Analytics and Usage Tracking Hooks
 * Track user interactions, performance metrics, and system usage
 */

import { useEffect, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { DashboardFilters } from '../types/decision';

// Analytics event types
interface AnalyticsEvent {
  type: 'page_view' | 'filter_change' | 'chart_interaction' | 'export' | 'search' | 'error';
  properties: Record<string, any>;
  timestamp: Date;
  sessionId: string;
  userId?: string;
}

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: Date;
  additionalData?: Record<string, any>;
}

interface UsageStats {
  dailyActiveUsers: number;
  totalSessions: number;
  averageSessionDuration: number;
  mostUsedFilters: Array<{ filter: string; count: number }>;
  popularCharts: Array<{ chart: string; views: number }>;
  errorRate: number;
  performanceMetrics: {
    averageLoadTime: number;
    averageFilterTime: number;
    cacheHitRate: number;
  };
}

// Session management
let sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
const sessionStartTime = Date.now();

/**
 * Core analytics tracking hook
 */
export function useAnalytics() {
  const eventQueueRef = useRef<AnalyticsEvent[]>([]);
  const flushTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Track an analytics event
  const track = useCallback((
    type: AnalyticsEvent['type'],
    properties: Record<string, any> = {}
  ) => {
    const event: AnalyticsEvent = {
      type,
      properties: {
        ...properties,
        url: window.location.pathname,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
      },
      timestamp: new Date(),
      sessionId,
    };

    eventQueueRef.current.push(event);

    // Flush events periodically
    if (flushTimeoutRef.current) {
      clearTimeout(flushTimeoutRef.current);
    }

    flushTimeoutRef.current = setTimeout(() => {
      flushEvents();
    }, 1000);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[Analytics]', type, properties);
    }
  }, []);

  // Flush events to server
  const flushEvents = useCallback(async () => {
    if (eventQueueRef.current.length === 0) return;

    const events = [...eventQueueRef.current];
    eventQueueRef.current = [];

    try {
      // Send to analytics endpoint
      await fetch('/api/analytics/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ events }),
      });
    } catch (error) {
      console.error('[Analytics] Failed to send events:', error);
      // Re-queue events on failure
      eventQueueRef.current.unshift(...events);
    }
  }, []);

  // Track page views
  const trackPageView = useCallback((page: string) => {
    track('page_view', { page });
  }, [track]);

  // Track filter changes
  const trackFilterChange = useCallback((
    filterType: string,
    newValue: any,
    oldValue?: any
  ) => {
    track('filter_change', {
      filterType,
      newValue: JSON.stringify(newValue),
      oldValue: oldValue ? JSON.stringify(oldValue) : undefined,
    });
  }, [track]);

  // Track chart interactions
  const trackChartInteraction = useCallback((
    chartType: string,
    action: string,
    data?: any
  ) => {
    track('chart_interaction', {
      chartType,
      action,
      data: data ? JSON.stringify(data) : undefined,
    });
  }, [track]);

  // Track exports
  const trackExport = useCallback((
    format: string,
    filterCount: number,
    recordCount: number
  ) => {
    track('export', {
      format,
      filterCount,
      recordCount,
    });
  }, [track]);

  // Track search queries
  const trackSearch = useCallback((
    query: string,
    resultCount: number,
    searchTime: number
  ) => {
    track('search', {
      query: query.length > 50 ? query.substring(0, 50) + '...' : query,
      queryLength: query.length,
      resultCount,
      searchTime,
    });
  }, [track]);

  // Track errors
  const trackError = useCallback((
    errorType: string,
    errorMessage: string,
    errorStack?: string
  ) => {
    track('error', {
      errorType,
      errorMessage,
      errorStack,
    });
  }, [track]);

  // Flush events on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      flushEvents();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (flushTimeoutRef.current) {
        clearTimeout(flushTimeoutRef.current);
      }
      flushEvents();
    };
  }, [flushEvents]);

  return {
    track,
    trackPageView,
    trackFilterChange,
    trackChartInteraction,
    trackExport,
    trackSearch,
    trackError,
    sessionId,
  };
}

/**
 * Performance monitoring hook
 */
export function usePerformanceMonitoring() {
  const metricsRef = useRef<PerformanceMetric[]>([]);

  // Record a performance metric
  const recordMetric = useCallback((
    name: string,
    value: number,
    additionalData?: Record<string, any>
  ) => {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: new Date(),
      additionalData,
    };

    metricsRef.current.push(metric);

    // Keep only last 100 metrics in memory
    if (metricsRef.current.length > 100) {
      metricsRef.current = metricsRef.current.slice(-100);
    }

    // Log performance issues
    if (name === 'filter_response_time' && value > 300) {
      console.warn(`[Performance] Slow filter response: ${value}ms`);
    }

    if (name === 'chart_render_time' && value > 1000) {
      console.warn(`[Performance] Slow chart render: ${value}ms`);
    }
  }, []);

  // Measure function execution time
  const measureTime = useCallback(<T extends any[], R>(
    fn: (...args: T) => R,
    metricName: string
  ) => {
    return (...args: T): R => {
      const start = performance.now();
      const result = fn(...args);
      const duration = performance.now() - start;
      
      recordMetric(metricName, duration);
      return result;
    };
  }, [recordMetric]);

  // Measure async function execution time
  const measureAsyncTime = useCallback(<T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    metricName: string
  ) => {
    return async (...args: T): Promise<R> => {
      const start = performance.now();
      const result = await fn(...args);
      const duration = performance.now() - start;
      
      recordMetric(metricName, duration);
      return result;
    };
  }, [recordMetric]);

  // Get performance summary
  const getPerformanceSummary = useCallback(() => {
    const metrics = metricsRef.current;
    const summary: Record<string, { avg: number; min: number; max: number; count: number }> = {};

    metrics.forEach(metric => {
      if (!summary[metric.name]) {
        summary[metric.name] = { avg: 0, min: Infinity, max: -Infinity, count: 0 };
      }

      const s = summary[metric.name];
      s.count++;
      s.min = Math.min(s.min, metric.value);
      s.max = Math.max(s.max, metric.value);
      s.avg = ((s.avg * (s.count - 1)) + metric.value) / s.count;
    });

    return summary;
  }, []);

  // Monitor Core Web Vitals
  useEffect(() => {
    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          recordMetric('lcp', entry.startTime);
        }
      });
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

      // First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          recordMetric('fid', (entry as any).processingStart - entry.startTime);
        }
      });
      fidObserver.observe({ type: 'first-input', buffered: true });

      return () => {
        lcpObserver.disconnect();
        fidObserver.disconnect();
      };
    }
  }, [recordMetric]);

  return {
    recordMetric,
    measureTime,
    measureAsyncTime,
    getPerformanceSummary,
    metrics: metricsRef.current,
  };
}

/**
 * Filter usage analytics hook
 */
export function useFilterAnalytics(filters: DashboardFilters) {
  const { trackFilterChange } = useAnalytics();
  const previousFiltersRef = useRef<DashboardFilters>(filters);

  useEffect(() => {
    const previous = previousFiltersRef.current;
    const current = filters;

    // Track changes in each filter type
    if (JSON.stringify(previous.governments) !== JSON.stringify(current.governments)) {
      trackFilterChange('governments', current.governments, previous.governments);
    }

    if (JSON.stringify(previous.policyAreas) !== JSON.stringify(current.policyAreas)) {
      trackFilterChange('policyAreas', current.policyAreas, previous.policyAreas);
    }

    if (JSON.stringify(previous.committees) !== JSON.stringify(current.committees)) {
      trackFilterChange('committees', current.committees, previous.committees);
    }

    if (JSON.stringify(previous.dateRange) !== JSON.stringify(current.dateRange)) {
      trackFilterChange('dateRange', current.dateRange, previous.dateRange);
    }

    if (previous.decisionType !== current.decisionType) {
      trackFilterChange('decisionType', current.decisionType, previous.decisionType);
    }

    if (previous.searchText !== current.searchText) {
      trackFilterChange('searchText', current.searchText, previous.searchText);
    }

    previousFiltersRef.current = current;
  }, [filters, trackFilterChange]);
}

/**
 * Usage statistics hook
 */
export function useUsageStats() {
  return useQuery({
    queryKey: ['usage-stats'],
    queryFn: async (): Promise<UsageStats> => {
      const response = await fetch('/api/analytics/usage-stats');
      if (!response.ok) {
        throw new Error('Failed to fetch usage stats');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Error tracking hook
 */
export function useErrorTracking() {
  const { trackError } = useAnalytics();

  useEffect(() => {
    // Global error handler
    const handleError = (event: ErrorEvent) => {
      trackError(
        'javascript_error',
        event.message,
        event.error?.stack
      );
    };

    // Unhandled promise rejection handler
    const handleRejection = (event: PromiseRejectionEvent) => {
      trackError(
        'unhandled_promise_rejection',
        event.reason?.toString() || 'Unknown promise rejection',
        event.reason?.stack
      );
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  }, [trackError]);

  return { trackError };
}

/**
 * A/B testing hook (for future experiments)
 */
export function useABTesting() {
  const getVariant = useCallback((experimentName: string, defaultVariant: string = 'control') => {
    // Simple hash-based variant assignment
    const userId = sessionId;
    const hash = Array.from(userId + experimentName).reduce((acc, char) => {
      return ((acc << 5) - acc + char.charCodeAt(0)) >>> 0;
    }, 0);
    
    // For now, always return control variant
    // In production, this would check active experiments and user assignments
    return defaultVariant;
  }, []);

  const trackExperiment = useCallback((experimentName: string, variant: string, metric: string, value: number) => {
    const { track } = useAnalytics();
    track('chart_interaction', {
      experimentName,
      variant,
      metric,
      value,
    });
  }, []);

  return {
    getVariant,
    trackExperiment,
  };
}