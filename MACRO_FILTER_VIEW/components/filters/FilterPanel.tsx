/**
 * Main Filter Panel Component
 * Combines all filter components with smart features like URL state and presets
 */

import React, { useState, useEffect } from 'react';
import { Filter, X, RotateCcw, Bookmark, Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';

import GovernmentFilter from './GovernmentFilter';
import PolicyAreaFilter from './PolicyAreaFilter';
import DateRangeFilter from './DateRangeFilter';
import CommitteeFilter from './CommitteeFilter';
import DecisionTypeFilter from './DecisionTypeFilter';
import SearchFilter from './SearchFilter';

import { 
  getDefaultFilters, 
  isFiltersEmpty, 
  countActiveFilters,
  validateFilters 
} from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface FilterPanelProps {
  filters: DashboardFilters;
  onChange: (filters: DashboardFilters) => void;
  className?: string;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
}

export default function FilterPanel({
  filters,
  onChange,
  className,
  collapsed = false,
  onCollapsedChange,
}: FilterPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  
  // Sync with prop
  useEffect(() => {
    setIsCollapsed(collapsed);
  }, [collapsed]);

  const handleCollapsedChange = (newCollapsed: boolean) => {
    setIsCollapsed(newCollapsed);
    onCollapsedChange?.(newCollapsed);
  };

  const handleFilterChange = (key: keyof DashboardFilters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    
    // Validate filters before applying
    const errors = validateFilters(newFilters);
    if (errors.length === 0) {
      onChange(newFilters);
    } else {
      console.warn('Filter validation errors:', errors);
    }
  };

  const handleClearAll = () => {
    onChange(getDefaultFilters());
  };

  const handleShareFilters = async () => {
    try {
      const url = new URL(window.location.href);
      
      // Encode filters in URL
      if (filters.governments.length > 0) {
        url.searchParams.set('gov', filters.governments.join(','));
      }
      if (filters.committees.length > 0) {
        url.searchParams.set('committees', filters.committees.join(','));
      }
      if (filters.policyAreas.length > 0) {
        url.searchParams.set('policy', filters.policyAreas.join(','));
      }
      if (filters.primeMinister) {
        url.searchParams.set('pm', filters.primeMinister);
      }
      if (filters.dateRange.start) {
        url.searchParams.set('start', filters.dateRange.start.toISOString().split('T')[0]);
      }
      if (filters.dateRange.end) {
        url.searchParams.set('end', filters.dateRange.end.toISOString().split('T')[0]);
      }
      if (filters.decisionType !== 'all') {
        url.searchParams.set('type', filters.decisionType);
      }
      if (filters.searchText) {
        url.searchParams.set('search', filters.searchText);
      }

      await navigator.clipboard.writeText(url.toString());
      
      // Show success feedback (you might want to add a toast here)
      console.log('Filter URL copied to clipboard');
    } catch (error) {
      console.error('Failed to share filters:', error);
    }
  };

  const activeFilterCount = countActiveFilters(filters);
  const isEmpty = isFiltersEmpty(filters);

  return (
    <Card className={cn('w-full', className)}>
      <Collapsible open={!isCollapsed} onOpenChange={handleCollapsedChange}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                <span>מסנני חיפוש</span>
                {activeFilterCount > 0 && (
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    {activeFilterCount}
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                {!isEmpty && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleShareFilters();
                      }}
                      className="h-8 w-8 p-0"
                    >
                      <Share2 className="h-4 w-4" />
                      <span className="sr-only">שתף מסננים</span>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleClearAll();
                      }}
                      className="h-8 w-8 p-0"
                    >
                      <RotateCcw className="h-4 w-4" />
                      <span className="sr-only">נקה הכל</span>
                    </Button>
                  </>
                )}
              </div>
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="space-y-6">
            {/* Search Filter */}
            <SearchFilter
              searchText={filters.searchText}
              onChange={(text) => handleFilterChange('searchText', text)}
            />

            {/* Government Filter */}
            <GovernmentFilter
              selectedGovernments={filters.governments}
              onChange={(governments) => handleFilterChange('governments', governments)}
            />

            {/* Policy Areas Filter */}
            <PolicyAreaFilter
              selectedAreas={filters.policyAreas}
              onChange={(areas) => handleFilterChange('policyAreas', areas)}
              currentFilters={filters}
            />

            {/* Date Range Filter */}
            <DateRangeFilter
              dateRange={filters.dateRange}
              onChange={(range) => handleFilterChange('dateRange', range)}
            />

            {/* Committee Filter */}
            <CommitteeFilter
              selectedCommittees={filters.committees}
              onChange={(committees) => handleFilterChange('committees', committees)}
              currentFilters={filters}
            />

            {/* Decision Type Filter */}
            <DecisionTypeFilter
              selectedType={filters.decisionType}
              onChange={(type) => handleFilterChange('decisionType', type)}
              currentFilters={filters}
            />

            {/* Clear All Button */}
            {!isEmpty && (
              <div className="pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={handleClearAll}
                  className="w-full"
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  נקה את כל המסננים
                </Button>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}