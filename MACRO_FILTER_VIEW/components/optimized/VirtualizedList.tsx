/**
 * Virtualized List Component
 * Efficiently renders large lists by only rendering visible items
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useVirtualizedList, useComponentPerformance } from '../../hooks/usePerformanceOptimization';
import { cn } from '@/lib/utils';

interface VirtualizedListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  overscan?: number;
  className?: string;
  onScroll?: (scrollTop: number) => void;
  loadMore?: () => void;
  hasMore?: boolean;
  isLoading?: boolean;
  emptyMessage?: string;
}

export default function VirtualizedList<T>({
  items,
  height,
  itemHeight,
  renderItem,
  overscan = 5,
  className,
  onScroll,
  loadMore,
  hasMore,
  isLoading,
  emptyMessage = 'אין פריטים להצגה',
}: VirtualizedListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { recordMetric } = useComponentPerformance('VirtualizedList');
  
  const {
    visibleItems,
    totalHeight,
    handleScroll: internalHandleScroll,
    visibleRange,
  } = useVirtualizedList(items, height, itemHeight, overscan);

  // Combined scroll handler
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = event.currentTarget.scrollTop;
    const scrollHeight = event.currentTarget.scrollHeight;
    const clientHeight = event.currentTarget.clientHeight;
    
    internalHandleScroll(event);
    onScroll?.(scrollTop);

    // Trigger load more when near bottom
    if (
      loadMore &&
      hasMore &&
      !isLoading &&
      scrollTop + clientHeight >= scrollHeight - itemHeight * 2
    ) {
      loadMore();
    }

    // Performance monitoring
    recordMetric('scroll_position', scrollTop);
    recordMetric('visible_items_count', visibleItems.length);
  }, [internalHandleScroll, onScroll, loadMore, hasMore, isLoading, itemHeight, recordMetric, visibleItems.length]);

  // Monitor performance
  useEffect(() => {
    recordMetric('total_items', items.length);
    recordMetric('visible_range_size', visibleRange.end - visibleRange.start);
  }, [items.length, visibleRange, recordMetric]);

  if (items.length === 0) {
    return (
      <div 
        className={cn("flex items-center justify-center text-gray-500", className)}
        style={{ height }}
      >
        {emptyMessage}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("overflow-auto", className)}
      style={{ height }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, top }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top,
              left: 0,
              right: 0,
              height: itemHeight,
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div
            style={{
              position: 'absolute',
              top: visibleItems.length > 0 ? visibleItems[visibleItems.length - 1].top + itemHeight : 0,
              left: 0,
              right: 0,
              height: itemHeight,
            }}
            className="flex items-center justify-center text-gray-500"
          >
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="mr-2">טוען...</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Optimized Decision List Item Component
 */
interface DecisionListItemProps {
  decision: any;
  index: number;
  isSelected?: boolean;
  onSelect?: (decision: any) => void;
  onFavorite?: (decision: any) => void;
  className?: string;
}

export function DecisionListItem({
  decision,
  index,
  isSelected,
  onSelect,
  onFavorite,
  className,
}: DecisionListItemProps) {
  const { recordMetric } = useComponentPerformance('DecisionListItem');

  const handleClick = useCallback(() => {
    onSelect?.(decision);
    recordMetric('item_click', 1);
  }, [decision, onSelect, recordMetric]);

  const handleFavorite = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onFavorite?.(decision);
    recordMetric('favorite_click', 1);
  }, [decision, onFavorite, recordMetric]);

  return (
    <div
      className={cn(
        "flex items-center gap-4 p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors",
        isSelected && "bg-blue-50 border-blue-200",
        className
      )}
      onClick={handleClick}
    >
      <div className="flex-1 min-w-0 text-right">
        <h3 className="font-medium text-gray-900 truncate">
          {decision.title}
        </h3>
        <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
          <span>החלטה {decision.number}</span>
          <span>•</span>
          <span>ממשלה {decision.government}</span>
          <span>•</span>
          <span>{decision.date}</span>
        </div>
        {decision.policyArea && (
          <div className="mt-2">
            <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
              {decision.policyArea}
            </span>
          </div>
        )}
      </div>
      
      <div className="flex-shrink-0 flex items-center gap-2">
        <button
          onClick={handleFavorite}
          className="p-1 hover:bg-gray-100 rounded-full transition-colors"
        >
          <svg className="h-4 w-4 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.682l-1.318-1.364a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Infinite Scroll List Component
 */
interface InfiniteScrollListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  className?: string;
  threshold?: number;
}

export function InfiniteScrollList<T>({
  items,
  renderItem,
  onLoadMore,
  hasMore,
  isLoading,
  className,
  threshold = 200,
}: InfiniteScrollListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { recordMetric } = useComponentPerformance('InfiniteScrollList');

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = event.currentTarget;
    
    if (
      hasMore &&
      !isLoading &&
      scrollHeight - scrollTop - clientHeight < threshold
    ) {
      onLoadMore();
      recordMetric('load_more_triggered', 1);
    }
  }, [hasMore, isLoading, threshold, onLoadMore, recordMetric]);

  useEffect(() => {
    recordMetric('total_items', items.length);
  }, [items.length, recordMetric]);

  return (
    <div
      ref={containerRef}
      className={cn("overflow-auto", className)}
      onScroll={handleScroll}
    >
      <div className="space-y-1">
        {items.map((item, index) => (
          <div key={index}>
            {renderItem(item, index)}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-center justify-center p-4 text-gray-500">
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="mr-2">טוען עוד...</span>
          </div>
        )}
        
        {!hasMore && items.length > 0 && (
          <div className="text-center p-4 text-gray-500 text-sm">
            הצגת כל התוצאות ({items.length} פריטים)
          </div>
        )}
      </div>
    </div>
  );
}