/**
 * Committee Filter Component with Autocomplete
 * Filters by government committees and bodies
 */

import React, { useState, useMemo } from 'react';
import { Check, ChevronDown, X, Users } from 'lucide-react';
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
import { useFilterOptions, useCommitteeStats } from '../../hooks/useDecisions';
import { formatHebrewNumber } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface CommitteeFilterProps {
  selectedCommittees: string[];
  onChange: (committees: string[]) => void;
  currentFilters: DashboardFilters;
  className?: string;
}

// Default committees in Hebrew
const DEFAULT_COMMITTEES = [
  'הממשלה',
  'ועדת השרים לענייני חקיקה',
  'ועדת השרים לענייני ביטחון לאומי',
  'ועדת השרים לענייני כלכלה',
  'ועדת השרים לענייני חברה ורווחה',
  'ועדת השרים לתכנון ובנייה',
  'ועדת השרים לענייני סביבה',
  'ועדת השרים לענייני חינוך',
  'ועדת השרים לענייני תרבות וספורט',
  'ועדת השרים לענייני מדע וטכנולוגיה',
  'ועדת השרים לענייני מיעוטים',
  'ועדת השרים לענייני ירושלים',
];

export default function CommitteeFilter({
  selectedCommittees,
  onChange,
  currentFilters,
  className,
}: CommitteeFilterProps) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { data: filterOptions } = useFilterOptions();
  const { data: committeeStats } = useCommitteeStats(currentFilters);
  
  // Combine API data with defaults
  const allCommittees = useMemo(() => {
    const apiCommittees = filterOptions?.committees || [];
    const combined = [...new Set([...apiCommittees, ...DEFAULT_COMMITTEES])];
    return combined.sort((a, b) => a.localeCompare(b, 'he'));
  }, [filterOptions]);

  // Filter committees based on search term
  const filteredCommittees = useMemo(() => {
    if (!searchTerm.trim()) return allCommittees;
    
    return allCommittees.filter(committee =>
      committee.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [allCommittees, searchTerm]);

  // Get count for each committee from statistics
  const getCommitteeCount = (committee: string): number => {
    if (!committeeStats) return 0;
    const stat = committeeStats.find(s => s.committee === committee);
    return stat?.count || 0;
  };

  // Get recent activity indicator
  const getRecentActivity = (committee: string): number => {
    if (!committeeStats) return 0;
    const stat = committeeStats.find(s => s.committee === committee);
    return stat?.recentActivity || 0;
  };

  const handleSelect = (committee: string) => {
    const isSelected = selectedCommittees.includes(committee);
    
    if (isSelected) {
      onChange(selectedCommittees.filter(c => c !== committee));
    } else {
      onChange([...selectedCommittees, committee]);
    }
  };

  const handleRemove = (committee: string) => {
    onChange(selectedCommittees.filter(c => c !== committee));
  };

  const handleClear = () => {
    onChange([]);
  };

  const getDisplayText = () => {
    if (selectedCommittees.length === 0) {
      return 'בחר ועדות...';
    }
    
    if (selectedCommittees.length === 1) {
      return selectedCommittees[0];
    }
    
    return `${selectedCommittees.length} ועדות נבחרו`;
  };

  // Sort committees by activity (most active first)
  const sortedCommittees = useMemo(() => {
    return [...filteredCommittees].sort((a, b) => {
      const countA = getCommitteeCount(a);
      const countB = getCommitteeCount(b);
      
      if (countA !== countB) {
        return countB - countA; // Higher count first
      }
      
      return a.localeCompare(b, 'he'); // Alphabetical if counts are equal
    });
  }, [filteredCommittees, committeeStats]);

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        ועדות וגופים
      </label>
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={cn(
              'w-full justify-between text-right',
              selectedCommittees.length > 0 && 'bg-purple-50 border-purple-200'
            )}
          >
            <span className="truncate">{getDisplayText()}</span>
            <ChevronDown className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-full p-0" align="start">
          <Command className="max-h-96">
            <div className="flex items-center border-b px-3">
              <Users className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <Input
                placeholder="חפש ועדה או גוף..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border-0 px-0 py-2 focus-visible:ring-0 text-right"
              />
            </div>
            
            <CommandList>
              <CommandEmpty>לא נמצאו ועדות</CommandEmpty>
              
              <CommandGroup>
                {sortedCommittees.map((committee) => {
                  const count = getCommitteeCount(committee);
                  const recentActivity = getRecentActivity(committee);
                  
                  return (
                    <CommandItem
                      key={committee}
                      value={committee}
                      onSelect={() => handleSelect(committee)}
                      className="cursor-pointer"
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          selectedCommittees.includes(committee)
                            ? 'opacity-100'
                            : 'opacity-0'
                        )}
                      />
                      
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center gap-2">
                          <span className="text-right">{committee}</span>
                          {recentActivity > 0 && (
                            <div className="w-2 h-2 bg-green-500 rounded-full" title="פעילות אחרונה" />
                          )}
                        </div>
                        
                        <div className="flex items-center gap-1">
                          {count > 0 && (
                            <Badge
                              variant="secondary"
                              className="text-xs bg-gray-100 text-gray-600"
                            >
                              {formatHebrewNumber(count)}
                            </Badge>
                          )}
                          {recentActivity > 0 && (
                            <Badge
                              variant="secondary"
                              className="text-xs bg-green-100 text-green-600"
                            >
                              +{formatHebrewNumber(recentActivity)}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Selected committees display */}
      {selectedCommittees.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedCommittees.map((committee) => {
            const count = getCommitteeCount(committee);
            
            return (
              <Badge
                key={committee}
                variant="secondary"
                className="bg-purple-100 text-purple-800 hover:bg-purple-200 max-w-[250px]"
              >
                <Users className="w-3 h-3 ml-1" />
                <span className="truncate">{committee}</span>
                {count > 0 && (
                  <span className="text-xs opacity-75 mr-1">
                    ({formatHebrewNumber(count)})
                  </span>
                )}
                <button
                  onClick={() => handleRemove(committee)}
                  className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  <X className="h-3 w-3" />
                  <span className="sr-only">הסר {committee}</span>
                </button>
              </Badge>
            );
          })}
          
          {selectedCommittees.length > 1 && (
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