/**
 * Decision Type Filter Component
 * Toggle between אופרטיבית (Operational) and דקלרטיבית (Declarative) decisions
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { useOverviewStats } from '../../hooks/useDecisions';
import { formatHebrewNumber } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface DecisionTypeFilterProps {
  selectedType: 'אופרטיבית' | 'דקלרטיבית' | 'all';
  onChange: (type: 'אופרטיבית' | 'דקלרטיבית' | 'all') => void;
  currentFilters: DashboardFilters;
  className?: string;
}

export default function DecisionTypeFilter({
  selectedType,
  onChange,
  currentFilters,
  className,
}: DecisionTypeFilterProps) {
  const { data: stats } = useOverviewStats(currentFilters);

  const typeOptions = [
    {
      value: 'all' as const,
      label: 'כל ההחלטות',
      count: stats?.total || 0,
      description: 'כולל החלטות אופרטיביות ודקלרטיביות',
      color: 'bg-gray-100 text-gray-800',
    },
    {
      value: 'אופרטיבית' as const,
      label: 'החלטות אופרטיביות',
      count: stats?.operational || 0,
      description: 'החלטות הכוללות הוראות ביצוע ספציפיות',
      color: 'bg-green-100 text-green-800',
    },
    {
      value: 'דקלרטיבית' as const,
      label: 'החלטות דקלרטיביות',
      count: stats?.declarative || 0,
      description: 'החלטות המביעות עמדה או כוונה בלבד',
      color: 'bg-blue-100 text-blue-800',
    },
  ];

  return (
    <div className={cn('space-y-3', className)}>
      <label className="text-sm font-medium text-gray-700">
        סוג החלטה
      </label>

      <RadioGroup
        value={selectedType}
        onValueChange={onChange}
        className="space-y-2"
      >
        {typeOptions.map((option) => (
          <div
            key={option.value}
            className={cn(
              'flex items-center space-x-3 space-x-reverse p-3 rounded-lg border transition-colors',
              selectedType === option.value
                ? 'border-blue-200 bg-blue-50'
                : 'border-gray-200 bg-white hover:bg-gray-50'
            )}
          >
            <RadioGroupItem value={option.value} id={option.value} />
            
            <div className="flex-1 space-y-1">
              <Label
                htmlFor={option.value}
                className="flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{option.label}</span>
                  <Badge
                    variant="secondary"
                    className={cn('text-xs', option.color)}
                  >
                    {formatHebrewNumber(option.count)}
                  </Badge>
                </div>
              </Label>
              
              <p className="text-xs text-gray-500 pr-6">
                {option.description}
              </p>
            </div>
          </div>
        ))}
      </RadioGroup>

      {/* Statistics summary */}
      {stats && stats.total > 0 && (
        <div className="p-3 bg-gray-50 rounded-lg text-sm">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="font-medium text-green-600">
                {formatHebrewNumber(stats.operational)}
              </div>
              <div className="text-xs text-gray-500">אופרטיביות</div>
              <div className="text-xs text-gray-400">
                {stats.total > 0 ? Math.round((stats.operational / stats.total) * 100) : 0}%
              </div>
            </div>
            
            <div>
              <div className="font-medium text-blue-600">
                {formatHebrewNumber(stats.declarative)}
              </div>
              <div className="text-xs text-gray-500">דקלרטיביות</div>
              <div className="text-xs text-gray-400">
                {stats.total > 0 ? Math.round((stats.declarative / stats.total) * 100) : 0}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}