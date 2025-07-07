/**
 * Multi-select Government Filter Component
 * Allows filtering by multiple Israeli governments with Hebrew RTL support
 */

import React, { useState } from 'react';
import { Check, ChevronDown, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import { useFilterOptions } from '../../hooks/useDecisions';

interface GovernmentFilterProps {
  selectedGovernments: number[];
  onChange: (governments: number[]) => void;
  className?: string;
}

// Default government data with Hebrew names and periods
const DEFAULT_GOVERNMENTS = [
  { number: 37, primeMinister: 'בנימין נתניהו', period: '2022-2025' },
  { number: 36, primeMinister: 'נפתלי בנט / יאיר לפיד', period: '2021-2022' },
  { number: 35, primeMinister: 'בנימין נתניהו', period: '2020-2021' },
  { number: 34, primeMinister: 'בנימין נתניהו', period: '2015-2020' },
  { number: 33, primeMinister: 'בנימין נתניהו', period: '2013-2015' },
  { number: 32, primeMinister: 'בנימין נתניהו', period: '2009-2013' },
];

export default function GovernmentFilter({
  selectedGovernments,
  onChange,
  className,
}: GovernmentFilterProps) {
  const [open, setOpen] = useState(false);
  const { data: filterOptions } = useFilterOptions();
  
  // Use API data if available, fallback to default
  const governments = filterOptions?.governments || DEFAULT_GOVERNMENTS;

  const handleSelect = (governmentNumber: number) => {
    const isSelected = selectedGovernments.includes(governmentNumber);
    
    if (isSelected) {
      onChange(selectedGovernments.filter(g => g !== governmentNumber));
    } else {
      onChange([...selectedGovernments, governmentNumber]);
    }
  };

  const handleRemove = (governmentNumber: number) => {
    onChange(selectedGovernments.filter(g => g !== governmentNumber));
  };

  const handleClear = () => {
    onChange([]);
  };

  const getDisplayText = () => {
    if (selectedGovernments.length === 0) {
      return 'בחר ממשלות...';
    }
    
    if (selectedGovernments.length === 1) {
      const gov = governments.find(g => g.number === selectedGovernments[0]);
      return gov ? `ממשלה ${gov.number}` : `ממשלה ${selectedGovernments[0]}`;
    }
    
    return `${selectedGovernments.length} ממשלות נבחרו`;
  };

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        ממשלות
      </label>
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={cn(
              'w-full justify-between text-right',
              selectedGovernments.length > 0 && 'bg-blue-50 border-blue-200'
            )}
          >
            <span className="truncate">{getDisplayText()}</span>
            <ChevronDown className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-full p-0" align="start">
          <Command className="max-h-96">
            <CommandInput 
              placeholder="חפש ממשלה..." 
              className="text-right"
            />
            
            <CommandList>
              <CommandEmpty>לא נמצאו ממשלות</CommandEmpty>
              
              <CommandGroup>
                {governments.map((government) => (
                  <CommandItem
                    key={government.number}
                    value={government.number.toString()}
                    onSelect={() => handleSelect(government.number)}
                    className="cursor-pointer"
                  >
                    <Check
                      className={cn(
                        'mr-2 h-4 w-4',
                        selectedGovernments.includes(government.number)
                          ? 'opacity-100'
                          : 'opacity-0'
                      )}
                    />
                    
                    <div className="flex-1 text-right">
                      <div className="font-medium">
                        ממשלה {government.number}
                      </div>
                      <div className="text-xs text-gray-500">
                        {government.primeMinister} • {government.period}
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Selected governments display */}
      {selectedGovernments.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedGovernments.map((govNumber) => {
            const gov = governments.find(g => g.number === govNumber);
            return (
              <Badge
                key={govNumber}
                variant="secondary"
                className="bg-blue-100 text-blue-800 hover:bg-blue-200"
              >
                ממשלה {govNumber}
                <button
                  onClick={() => handleRemove(govNumber)}
                  className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  <X className="h-3 w-3" />
                  <span className="sr-only">הסר ממשלה {govNumber}</span>
                </button>
              </Badge>
            );
          })}
          
          {selectedGovernments.length > 1 && (
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