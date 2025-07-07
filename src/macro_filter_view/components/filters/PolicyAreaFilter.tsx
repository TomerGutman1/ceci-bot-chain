/**
 * Multi-select Policy Area Filter Component
 * Allows filtering by multiple policy areas with count indicators
 */

import React, { useState, useMemo } from 'react';
import { Check, ChevronDown, X, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { useFilterOptions, usePolicyAreaStats } from '../../hooks/useDecisions';
import { formatHebrewNumber, getPolicyAreaColor } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface PolicyAreaFilterProps {
  selectedAreas: string[];
  onChange: (areas: string[]) => void;
  currentFilters: DashboardFilters;
  className?: string;
}

// Default policy areas in Hebrew
const DEFAULT_POLICY_AREAS = [
  'ביטחון',
  'כלכלה',
  'חינוך',
  'בריאות',
  'משפט',
  'תחבורה',
  'איכות הסביבה',
  'דיור',
  'רווחה',
  'תרבות וספורט',
  'חקלאות',
  'תעשייה ומסחר',
  'תקשורת',
  'אנרגיה',
  'מדע וטכנולוגיה',
];

export default function PolicyAreaFilter({
  selectedAreas,
  onChange,
  currentFilters,
  className,
}: PolicyAreaFilterProps) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { data: filterOptions } = useFilterOptions();
  const { data: areaStats } = usePolicyAreaStats(currentFilters);
  
  // Combine API data with defaults
  const allAreas = useMemo(() => {
    const apiAreas = filterOptions?.policyAreas || [];
    const combined = [...new Set([...apiAreas, ...DEFAULT_POLICY_AREAS])];
    return combined.sort((a, b) => a.localeCompare(b, 'he'));
  }, [filterOptions]);

  // Filter areas based on search term
  const filteredAreas = useMemo(() => {
    if (!searchTerm.trim()) return allAreas;
    
    return allAreas.filter(area =>
      area.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [allAreas, searchTerm]);

  // Get count for each area from statistics
  const getAreaCount = (area: string): number => {
    if (!areaStats) return 0;
    const stat = areaStats.find(s => s.area === area);
    return stat?.count || 0;
  };

  const handleSelect = (area: string) => {
    const isSelected = selectedAreas.includes(area);
    
    if (isSelected) {
      onChange(selectedAreas.filter(a => a !== area));
    } else {
      onChange([...selectedAreas, area]);
    }
  };

  const handleRemove = (area: string) => {
    onChange(selectedAreas.filter(a => a !== area));
  };

  const handleClear = () => {
    onChange([]);
  };

  const getDisplayText = () => {
    if (selectedAreas.length === 0) {
      return 'בחר תחומי מדיניות...';
    }
    
    if (selectedAreas.length === 1) {
      return selectedAreas[0];
    }
    
    return `${selectedAreas.length} תחומים נבחרו`;
  };

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        תחומי מדיניות
      </label>
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={cn(
              'w-full justify-between text-right',
              selectedAreas.length > 0 && 'bg-green-50 border-green-200'
            )}
          >
            <span className="truncate">{getDisplayText()}</span>
            <ChevronDown className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-full p-0" align="start">
          <Command className="max-h-96">
            <div className="flex items-center border-b px-3">
              <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <Input
                placeholder="חפש תחום מדיניות..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border-0 px-0 py-2 focus-visible:ring-0 text-right"
              />
            </div>
            
            <CommandList>
              <CommandEmpty>לא נמצאו תחומי מדיניות</CommandEmpty>
              
              <CommandGroup>
                {filteredAreas.map((area) => {
                  const count = getAreaCount(area);
                  const color = getPolicyAreaColor(area);
                  
                  return (
                    <CommandItem
                      key={area}
                      value={area}
                      onSelect={() => handleSelect(area)}
                      className="cursor-pointer"
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          selectedAreas.includes(area)
                            ? 'opacity-100'
                            : 'opacity-0'
                        )}
                      />
                      
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                          <span className="text-right">{area}</span>
                        </div>
                        
                        {count > 0 && (
                          <Badge
                            variant="secondary"
                            className="text-xs bg-gray-100 text-gray-600"
                          >
                            {formatHebrewNumber(count)}
                          </Badge>
                        )}
                      </div>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Selected areas display */}
      {selectedAreas.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedAreas.map((area) => {
            const color = getPolicyAreaColor(area);
            const count = getAreaCount(area);
            
            return (
              <Badge
                key={area}
                variant="secondary"
                className="bg-green-100 text-green-800 hover:bg-green-200 max-w-[200px]"
              >
                <div
                  className="w-2 h-2 rounded-full ml-1"
                  style={{ backgroundColor: color }}
                />
                <span className="truncate">{area}</span>
                {count > 0 && (
                  <span className="text-xs opacity-75 mr-1">
                    ({formatHebrewNumber(count)})
                  </span>
                )}
                <button
                  onClick={() => handleRemove(area)}
                  className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  <X className="h-3 w-3" />
                  <span className="sr-only">הסר {area}</span>
                </button>
              </Badge>
            );
          })}
          
          {selectedAreas.length > 1 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="h-6 px-2 text-xs text-gray-500 hover:text-gray-700"
            >
              נקה הכל
            </Button>
          )}
        </div>
      )}
    </div>
  );
}