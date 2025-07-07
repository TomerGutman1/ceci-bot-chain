/**
 * Mobile Filter Drawer Component
 * Slide-out panel for mobile filter interface
 */

import React from 'react';
import { Filter, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { cn } from '@/lib/utils';

import GovernmentFilter from '../filters/GovernmentFilter';
import PolicyAreaFilter from '../filters/PolicyAreaFilter';
import DateRangeFilter from '../filters/DateRangeFilter';
import CommitteeFilter from '../filters/CommitteeFilter';
import DecisionTypeFilter from '../filters/DecisionTypeFilter';
import SearchFilter from '../filters/SearchFilter';

import { countActiveFilters, getDefaultFilters } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface MobileFilterDrawerProps {
  filters: DashboardFilters;
  onChange: (filters: DashboardFilters) => void;
  children?: React.ReactNode;
  className?: string;
}

export default function MobileFilterDrawer({
  filters,
  onChange,
  children,
  className,
}: MobileFilterDrawerProps) {
  const activeFilterCount = countActiveFilters(filters);

  const handleFilterChange = (key: keyof DashboardFilters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    onChange(newFilters);
  };

  const handleClearAll = () => {
    onChange(getDefaultFilters());
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        {children || (
          <Button variant="outline" className={cn('relative', className)}>
            <Filter className="h-4 w-4 mr-2" />
            מסננים
            {activeFilterCount > 0 && (
              <Badge
                variant="secondary"
                className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center bg-blue-500 text-white text-xs"
              >
                {activeFilterCount}
              </Badge>
            )}
          </Button>
        )}
      </SheetTrigger>

      <SheetContent side="right" className="w-full sm:w-96 overflow-y-auto">
        <SheetHeader className="space-y-4">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              מסנני חיפוש
            </SheetTitle>
            
            {activeFilterCount > 0 && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {activeFilterCount} פעילים
              </Badge>
            )}
          </div>
          
          <SheetDescription>
            השתמש במסננים למציאת החלטות הרלוונטיות עבורך
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 mt-6">
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
          {activeFilterCount > 0 && (
            <div className="pt-4 border-t">
              <Button
                variant="outline"
                onClick={handleClearAll}
                className="w-full"
              >
                <X className="mr-2 h-4 w-4" />
                נקה את כל המסננים
              </Button>
            </div>
          )}
        </div>

        {/* Filter Summary */}
        {activeFilterCount > 0 && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 mb-2">
              מסננים פעילים
            </h4>
            <div className="space-y-2 text-sm text-blue-800">
              {filters.governments.length > 0 && (
                <div>ממשלות: {filters.governments.join(', ')}</div>
              )}
              {filters.policyAreas.length > 0 && (
                <div>תחומי מדיניות: {filters.policyAreas.length} נבחרו</div>
              )}
              {filters.committees.length > 0 && (
                <div>ועדות: {filters.committees.length} נבחרו</div>
              )}
              {(filters.dateRange.start || filters.dateRange.end) && (
                <div>טווח תאריכים: מוגדר</div>
              )}
              {filters.decisionType !== 'all' && (
                <div>סוג החלטה: {filters.decisionType}</div>
              )}
              {filters.searchText && (
                <div>חיפוש: "{filters.searchText}"</div>
              )}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}