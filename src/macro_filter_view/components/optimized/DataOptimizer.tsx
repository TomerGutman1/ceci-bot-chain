/**
 * Data Optimizer Component
 * Manages large datasets with intelligent caching and lazy loading
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { 
  Database, 
  Zap, 
  Clock, 
  Activity, 
  BarChart3, 
  Settings,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { 
  useOptimizedDecisions, 
  useOptimizedStats, 
  useDataCache,
  useBatchProcessor,
  useComponentPerformance
} from '../../hooks/usePerformanceOptimization';
import { useAnalytics } from '../../hooks/useAnalytics';
import VirtualizedList, { DecisionListItem } from './VirtualizedList';
import type { DashboardFilters, DashboardDecision } from '../../types/decision';

interface DataOptimizerProps {
  filters: DashboardFilters;
  onDecisionSelect?: (decision: DashboardDecision) => void;
  onSettingsChange?: (settings: OptimizationSettings) => void;
  className?: string;
}

interface OptimizationSettings {
  enableVirtualization: boolean;
  enableInfiniteScroll: boolean;
  enableCaching: boolean;
  enableBatchProcessing: boolean;
  pageSize: number;
  cacheSize: number;
}

export default function DataOptimizer({
  filters,
  onDecisionSelect,
  onSettingsChange,
  className,
}: DataOptimizerProps) {
  const [settings, setSettings] = useState<OptimizationSettings>({
    enableVirtualization: true,
    enableInfiniteScroll: true,
    enableCaching: true,
    enableBatchProcessing: true,
    pageSize: 50,
    cacheSize: 1000,
  });

  const [selectedDecisions, setSelectedDecisions] = useState<Set<string>>(new Set());
  const [showSettings, setShowSettings] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>({});

  const { trackChartInteraction } = useAnalytics();
  const { recordMetric } = useComponentPerformance('DataOptimizer');

  // Optimized data fetching
  const {
    decisions,
    totalCount,
    isLoading,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
    error,
  } = useOptimizedDecisions(filters, {
    pageSize: settings.pageSize,
    enabled: true,
  });

  // Optimized statistics
  const { 
    data: stats, 
    isLoading: isLoadingStats 
  } = useOptimizedStats(filters, {
    enabled: true,
  });

  // Data cache
  const cache = useDataCache('decisions', settings.cacheSize);

  // Batch processor for bulk operations
  const {
    processBatch,
    isProcessing,
    progress,
    results: batchResults,
  } = useBatchProcessor(
    async (batch: DashboardDecision[]) => {
      // Example batch processing (could be export, analysis, etc.)
      return batch.map(decision => ({
        ...decision,
        processed: true,
        timestamp: Date.now(),
      }));
    },
    settings.pageSize,
    10 // 10ms delay between batches
  );

  // Handle decision selection
  const handleDecisionSelect = useCallback((decision: DashboardDecision) => {
    setSelectedDecisions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(decision.id.toString())) {
        newSet.delete(decision.id.toString());
      } else {
        newSet.add(decision.id.toString());
      }
      return newSet;
    });
    
    onDecisionSelect?.(decision);
    trackChartInteraction('decision_list', 'select', { decisionId: decision.id });
    recordMetric('decision_selected', 1);
  }, [onDecisionSelect, trackChartInteraction, recordMetric]);

  // Handle settings change
  const handleSettingsChange = useCallback((newSettings: OptimizationSettings) => {
    setSettings(newSettings);
    onSettingsChange?.(newSettings);
    recordMetric('settings_changed', 1);
  }, [onSettingsChange, recordMetric]);

  // Load more data
  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
      recordMetric('load_more', 1);
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage, recordMetric]);

  // Process selected decisions
  const processSelected = useCallback(() => {
    const selectedItems = decisions.filter(d => selectedDecisions.has(d.id.toString()));
    if (selectedItems.length > 0) {
      processBatch(selectedItems);
      recordMetric('batch_process_started', selectedItems.length);
    }
  }, [decisions, selectedDecisions, processBatch, recordMetric]);

  // Performance monitoring
  useEffect(() => {
    const metrics = {
      totalItems: totalCount,
      loadedItems: decisions.length,
      selectedItems: selectedDecisions.size,
      cacheSize: cache.size,
      isVirtualized: settings.enableVirtualization,
      infiniteScroll: settings.enableInfiniteScroll,
    };
    
    setPerformanceMetrics(metrics);
    recordMetric('performance_snapshot', JSON.stringify(metrics).length);
  }, [totalCount, decisions.length, selectedDecisions.size, cache.size, settings, recordMetric]);

  // Render decision item
  const renderDecisionItem = useCallback((decision: DashboardDecision, index: number) => {
    return (
      <DecisionListItem
        key={decision.id}
        decision={decision}
        index={index}
        isSelected={selectedDecisions.has(decision.id.toString())}
        onSelect={handleDecisionSelect}
        onFavorite={(d) => {
          // Handle favorite logic
          trackChartInteraction('decision_list', 'favorite', { decisionId: d.id });
        }}
      />
    );
  }, [selectedDecisions, handleDecisionSelect, trackChartInteraction]);

  // Memoized list component
  const ListComponent = useMemo(() => {
    if (settings.enableVirtualization) {
      return (
        <VirtualizedList
          items={decisions}
          height={600}
          itemHeight={120}
          renderItem={renderDecisionItem}
          loadMore={settings.enableInfiniteScroll ? loadMore : undefined}
          hasMore={hasNextPage}
          isLoading={isFetchingNextPage}
          emptyMessage="אין החלטות תואמות למסננים"
        />
      );
    } else {
      return (
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {decisions.map((decision, index) => renderDecisionItem(decision, index))}
          {settings.enableInfiniteScroll && hasNextPage && (
            <div className="flex justify-center p-4">
              <Button
                variant="outline"
                onClick={loadMore}
                disabled={isFetchingNextPage}
              >
                {isFetchingNextPage ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                טען עוד
              </Button>
            </div>
          )}
        </div>
      );
    }
  }, [
    settings.enableVirtualization,
    settings.enableInfiniteScroll,
    decisions,
    renderDecisionItem,
    loadMore,
    hasNextPage,
    isFetchingNextPage
  ]);

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center p-8">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="font-medium text-gray-900 mb-2">שגיאה בטעינת נתונים</h3>
            <p className="text-sm text-gray-500">{error.message}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                מיטוב נתונים
              </CardTitle>
              <CardDescription>
                ניהול יעיל של מערכי נתונים גדולים
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4 mr-2" />
              הגדרות
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <div>
                <div className="text-sm font-medium text-blue-900">
                  {totalCount.toLocaleString()}
                </div>
                <div className="text-xs text-blue-700">סה״כ פריטים</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="text-sm font-medium text-green-900">
                  {decisions.length.toLocaleString()}
                </div>
                <div className="text-xs text-green-700">נטענו</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
              <Activity className="h-5 w-5 text-purple-600" />
              <div>
                <div className="text-sm font-medium text-purple-900">
                  {selectedDecisions.size}
                </div>
                <div className="text-xs text-purple-700">נבחרו</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <div className="text-sm font-medium text-orange-900">
                  {cache.size}
                </div>
                <div className="text-xs text-orange-700">במטמון</div>
              </div>
            </div>
          </div>

          {/* Optimization Settings */}
          {showSettings && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">הגדרות מיטוב</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="virtualization">רשימה וירטואלית</Label>
                    <Switch
                      id="virtualization"
                      checked={settings.enableVirtualization}
                      onCheckedChange={(checked) =>
                        handleSettingsChange({
                          ...settings,
                          enableVirtualization: checked,
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="infinite-scroll">גלילה אינסופית</Label>
                    <Switch
                      id="infinite-scroll"
                      checked={settings.enableInfiniteScroll}
                      onCheckedChange={(checked) =>
                        handleSettingsChange({
                          ...settings,
                          enableInfiniteScroll: checked,
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="caching">מטמון נתונים</Label>
                    <Switch
                      id="caching"
                      checked={settings.enableCaching}
                      onCheckedChange={(checked) =>
                        handleSettingsChange({
                          ...settings,
                          enableCaching: checked,
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="batch-processing">עיבוד באצוות</Label>
                    <Switch
                      id="batch-processing"
                      checked={settings.enableBatchProcessing}
                      onCheckedChange={(checked) =>
                        handleSettingsChange({
                          ...settings,
                          enableBatchProcessing: checked,
                        })
                      }
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    גודל עמוד: {settings.pageSize}
                  </Badge>
                  <Badge variant="outline">
                    גודל מטמון: {settings.cacheSize}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Bar */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {selectedDecisions.size} פריטים נבחרו
              </span>
              {selectedDecisions.size > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={processSelected}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Zap className="h-4 w-4 mr-2" />
                  )}
                  עבד נבחרים
                </Button>
              )}
            </div>

            <div className="flex items-center gap-2">
              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  טוען...
                </div>
              )}
              {isProcessing && (
                <div className="flex items-center gap-2 text-sm text-blue-600">
                  <div className="w-16 bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  {Math.round(progress)}%
                </div>
              )}
            </div>
          </div>

          {/* Data List */}
          <div className="border rounded-lg">
            {ListComponent}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}