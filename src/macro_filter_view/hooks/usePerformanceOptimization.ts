/**
 * Performance Optimization Hooks
 * Handles large data volumes with pagination, virtualization, and caching
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useQuery, useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { useDebounce } from './useDebounce';
import { usePerformanceMonitoring } from './useAnalytics';
import type { DashboardFilters, DashboardDecision, DashboardStats } from '../types/decision';

// Performance configuration
const PERFORMANCE_CONFIG = {
  // Pagination
  PAGE_SIZE: 50,
  LARGE_PAGE_SIZE: 100,
  MAX_PAGES_IN_MEMORY: 10,
  
  // Virtualization
  VIRTUAL_ITEM_HEIGHT: 120,
  VIRTUAL_OVERSCAN: 5,
  VIRTUAL_THRESHOLD: 100,
  
  // Caching
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  STALE_TIME: 2 * 60 * 1000, // 2 minutes
  
  // Debouncing
  SEARCH_DEBOUNCE_MS: 300,
  FILTER_DEBOUNCE_MS: 150,
  
  // Memory management
  MAX_CACHED_ITEMS: 1000,
  CLEANUP_INTERVAL: 30 * 1000, // 30 seconds
};

interface PaginatedResponse<T> {
  items: T[];
  totalCount: number;
  hasNextPage: boolean;
  nextCursor?: string;
}

interface VirtualizedListProps {
  items: any[];
  height: number;
  itemHeight: number;
  overscan?: number;
  renderItem: (item: any, index: number) => React.ReactNode;
}

/**
 * Optimized decisions hook with pagination and caching
 */
export function useOptimizedDecisions(
  filters: DashboardFilters,
  options: {
    pageSize?: number;
    enabled?: boolean;
    cacheTime?: number;
  } = {}
) {
  const {
    pageSize = PERFORMANCE_CONFIG.PAGE_SIZE,
    enabled = true,
    cacheTime = PERFORMANCE_CONFIG.CACHE_DURATION,
  } = options;

  const { measureAsyncTime } = usePerformanceMonitoring();
  const debouncedFilters = useDebounce(filters, PERFORMANCE_CONFIG.FILTER_DEBOUNCE_MS);

  // Infinite query for large datasets
  const query = useInfiniteQuery({
    queryKey: ['decisions', 'optimized', debouncedFilters, pageSize],
    queryFn: measureAsyncTime(async ({ pageParam = 0 }) => {
      // Simulate API call with pagination
      const response = await fetch('/api/decisions/paginated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filters: debouncedFilters,
          page: pageParam,
          limit: pageSize,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch decisions');
      }

      return response.json() as Promise<PaginatedResponse<DashboardDecision>>;
    }, 'fetch_decisions_paginated'),
    initialPageParam: 0,
    getNextPageParam: (lastPage: any, allPages) => {
      return lastPage?.hasNextPage ? allPages.length : undefined;
    },
    staleTime: PERFORMANCE_CONFIG.STALE_TIME,
    gcTime: cacheTime,
    enabled,
    maxPages: PERFORMANCE_CONFIG.MAX_PAGES_IN_MEMORY,
  });

  // Flatten all pages into a single array
  const allDecisions = useMemo(() => {
    return query.data?.pages.flatMap((page: any) => page?.items || []) || [];
  }, [query.data]);

  // Total count from first page
  const totalCount = query.data?.pages?.[0]?.totalCount || 0;

  return {
    ...query,
    decisions: allDecisions,
    totalCount,
    hasNextPage: query.hasNextPage,
    fetchNextPage: query.fetchNextPage,
    isFetchingNextPage: query.isFetchingNextPage,
  };
}

/**
 * Virtual scrolling hook for large lists
 */
export function useVirtualizedList<T>(
  items: T[],
  containerHeight: number,
  itemHeight: number = PERFORMANCE_CONFIG.VIRTUAL_ITEM_HEIGHT,
  overscan: number = PERFORMANCE_CONFIG.VIRTUAL_OVERSCAN
) {
  const [scrollTop, setScrollTop] = useState(0);
  const { recordMetric } = usePerformanceMonitoring();

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = start + visibleCount;

    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.length, end + overscan),
    };
  }, [scrollTop, containerHeight, itemHeight, overscan, items.length]);

  // Get visible items
  const visibleItems = useMemo(() => {
    const result = [];
    for (let i = visibleRange.start; i < visibleRange.end; i++) {
      result.push({
        index: i,
        item: items[i],
        top: i * itemHeight,
      });
    }
    return result;
  }, [items, visibleRange, itemHeight]);

  // Scroll handler with performance monitoring
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = event.currentTarget.scrollTop;
    setScrollTop(newScrollTop);
    recordMetric('scroll_performance', performance.now());
  }, [recordMetric]);

  // Total height for scrollbar
  const totalHeight = items.length * itemHeight;

  return {
    visibleItems,
    totalHeight,
    handleScroll,
    visibleRange,
  };
}

/**
 * Optimized search hook with debouncing
 */
export function useOptimizedSearch(
  searchTerm: string,
  filters: DashboardFilters,
  options: {
    minLength?: number;
    debounceMs?: number;
    enabled?: boolean;
  } = {}
) {
  const {
    minLength = 2,
    debounceMs = PERFORMANCE_CONFIG.SEARCH_DEBOUNCE_MS,
    enabled = true,
  } = options;

  const debouncedSearchTerm = useDebounce(searchTerm, debounceMs);
  const { measureAsyncTime } = usePerformanceMonitoring();

  const query = useQuery({
    queryKey: ['search', debouncedSearchTerm, filters],
    queryFn: measureAsyncTime(async () => {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: debouncedSearchTerm,
          filters,
          limit: 50,
        }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      return response.json();
    }, 'search_decisions'),
    enabled: enabled && debouncedSearchTerm.length >= minLength,
    staleTime: PERFORMANCE_CONFIG.STALE_TIME,
  });

  return {
    ...query,
    searchTerm: debouncedSearchTerm,
    isSearching: query.isFetching,
    results: query.data?.results || [],
    totalResults: query.data?.totalCount || 0,
  };
}

/**
 * Memory-efficient data cache hook
 */
export function useDataCache<T>(
  key: string,
  maxSize: number = PERFORMANCE_CONFIG.MAX_CACHED_ITEMS
) {
  const cache = useRef(new Map<string, { data: T; timestamp: number }>());
  const queryClient = useQueryClient();

  const set = useCallback((subKey: string, data: T) => {
    const fullKey = `${key}:${subKey}`;
    
    // Remove oldest items if cache is full
    if (cache.current.size >= maxSize) {
      const oldestKey = Array.from(cache.current.keys())[0];
      cache.current.delete(oldestKey);
    }

    cache.current.set(fullKey, {
      data,
      timestamp: Date.now(),
    });
  }, [key, maxSize]);

  const get = useCallback((subKey: string): T | undefined => {
    const fullKey = `${key}:${subKey}`;
    const cached = cache.current.get(fullKey);
    
    if (!cached) return undefined;
    
    // Check if expired
    if (Date.now() - cached.timestamp > PERFORMANCE_CONFIG.CACHE_DURATION) {
      cache.current.delete(fullKey);
      return undefined;
    }
    
    return cached.data;
  }, [key]);

  const clear = useCallback(() => {
    cache.current.clear();
    queryClient.invalidateQueries({ queryKey: [key] });
  }, [key, queryClient]);

  const size = cache.current.size;

  // Cleanup expired entries
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      const keysToDelete: string[] = [];

      cache.current.forEach((value, key) => {
        if (now - value.timestamp > PERFORMANCE_CONFIG.CACHE_DURATION) {
          keysToDelete.push(key);
        }
      });

      keysToDelete.forEach(key => cache.current.delete(key));
    }, PERFORMANCE_CONFIG.CLEANUP_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  return { set, get, clear, size };
}

/**
 * Batch processing hook for large operations
 */
export function useBatchProcessor<T, R>(
  processor: (batch: T[]) => Promise<R[]>,
  batchSize: number = 50,
  delay: number = 10
) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<R[]>([]);
  const { measureAsyncTime } = usePerformanceMonitoring();

  const processBatch = useCallback(async (items: T[]): Promise<R[]> => {
    if (items.length === 0) return [];

    setIsProcessing(true);
    setProgress(0);
    setResults([]);

    const allResults: R[] = [];
    const batches = [];

    // Split items into batches
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }

    // Process each batch
    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      
      const batchResults = await measureAsyncTime(
        () => processor(batch),
        `batch_process_${i}`
      );

      allResults.push(...batchResults);
      setProgress(((i + 1) / batches.length) * 100);
      setResults([...allResults]);

      // Small delay to prevent UI blocking
      if (delay > 0 && i < batches.length - 1) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    setIsProcessing(false);
    return allResults;
  }, [processor, batchSize, delay, measureAsyncTime]);

  return {
    processBatch,
    isProcessing,
    progress,
    results,
  };
}

/**
 * Optimized statistics hook with caching
 */
export function useOptimizedStats(
  filters: DashboardFilters,
  options: {
    enabled?: boolean;
    refreshInterval?: number;
  } = {}
) {
  const { enabled = true, refreshInterval } = options;
  const debouncedFilters = useDebounce(filters, PERFORMANCE_CONFIG.FILTER_DEBOUNCE_MS);
  const { measureAsyncTime } = usePerformanceMonitoring();

  return useQuery({
    queryKey: ['statistics', 'optimized', debouncedFilters],
    queryFn: measureAsyncTime(async (): Promise<DashboardStats> => {
      const response = await fetch('/api/statistics/optimized', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters: debouncedFilters }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch statistics');
      }

      return response.json();
    }, 'fetch_optimized_stats'),
    enabled,
    staleTime: PERFORMANCE_CONFIG.STALE_TIME,
    gcTime: PERFORMANCE_CONFIG.CACHE_DURATION,
    refetchInterval: refreshInterval,
  });
}

// useDebounce is imported from './useDebounce' - no need to redefine it here

/**
 * Performance monitoring for components
 */
export function useComponentPerformance(componentName: string) {
  const { recordMetric } = usePerformanceMonitoring();
  const renderCount = useRef(0);
  const mountTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current++;
    recordMetric(`${componentName}_render_count`, renderCount.current);
  });

  useEffect(() => {
    const mountDuration = performance.now() - mountTime.current;
    recordMetric(`${componentName}_mount_time`, mountDuration);

    return () => {
      const totalLifetime = performance.now() - mountTime.current;
      recordMetric(`${componentName}_lifetime`, totalLifetime);
    };
  }, [componentName, recordMetric]);

  return {
    renderCount: renderCount.current,
    recordMetric: (name: string, value: number) => 
      recordMetric(`${componentName}_${name}`, value),
  };
}