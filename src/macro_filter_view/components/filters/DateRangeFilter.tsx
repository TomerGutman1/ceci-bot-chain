/**
 * Hebrew Date Range Filter Component
 * Supports Hebrew calendar display and preset date ranges
 */

import React, { useState } from 'react';
import { Calendar, ChevronDown, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { formatHebrewDate } from '../../utils/dataTransformers';
import type { DateRange } from '../../types/decision';

interface DateRangeFilterProps {
  dateRange: DateRange;
  onChange: (range: DateRange) => void;
  className?: string;
}

// Hebrew date presets
const DATE_PRESETS = [
  {
    label: 'השנה הנוכחית',
    value: 'current-year',
    getRange: () => ({
      start: new Date(new Date().getFullYear(), 0, 1),
      end: new Date(new Date().getFullYear(), 11, 31),
    }),
  },
  {
    label: 'השנה שעברה',
    value: 'last-year',
    getRange: () => ({
      start: new Date(new Date().getFullYear() - 1, 0, 1),
      end: new Date(new Date().getFullYear() - 1, 11, 31),
    }),
  },
  {
    label: 'החודש הנוכחי',
    value: 'current-month',
    getRange: () => {
      const now = new Date();
      return {
        start: new Date(now.getFullYear(), now.getMonth(), 1),
        end: new Date(now.getFullYear(), now.getMonth() + 1, 0),
      };
    },
  },
  {
    label: 'החודש שעבר',
    value: 'last-month',
    getRange: () => {
      const now = new Date();
      return {
        start: new Date(now.getFullYear(), now.getMonth() - 1, 1),
        end: new Date(now.getFullYear(), now.getMonth(), 0),
      };
    },
  },
  {
    label: 'הרבעון הנוכחי',
    value: 'current-quarter',
    getRange: () => {
      const now = new Date();
      const quarter = Math.floor(now.getMonth() / 3);
      return {
        start: new Date(now.getFullYear(), quarter * 3, 1),
        end: new Date(now.getFullYear(), quarter * 3 + 3, 0),
      };
    },
  },
  {
    label: '6 החודשים האחרונים',
    value: 'last-6-months',
    getRange: () => {
      const now = new Date();
      return {
        start: new Date(now.getFullYear(), now.getMonth() - 5, 1),
        end: now,
      };
    },
  },
  {
    label: '12 החודשים האחרונים',
    value: 'last-12-months',
    getRange: () => {
      const now = new Date();
      return {
        start: new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()),
        end: now,
      };
    },
  },
];

export default function DateRangeFilter({
  dateRange,
  onChange,
  className,
}: DateRangeFilterProps) {
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();
  const [selectingStart, setSelectingStart] = useState(true);

  const handlePresetSelect = (presetValue: string) => {
    const preset = DATE_PRESETS.find(p => p.value === presetValue);
    if (preset) {
      onChange(preset.getRange());
    }
  };

  const handleCalendarSelect = (date: Date | undefined) => {
    if (!date) return;

    if (selectingStart) {
      onChange({ start: date, end: dateRange.end });
      setSelectingStart(false);
    } else {
      // Ensure end date is after start date
      if (dateRange.start && date < dateRange.start) {
        onChange({ start: date, end: dateRange.start });
      } else {
        onChange({ start: dateRange.start, end: date });
      }
      setSelectingStart(true);
      setCalendarOpen(false);
    }
  };

  const handleClear = () => {
    onChange({ start: null, end: null });
    setSelectingStart(true);
  };

  const getDisplayText = () => {
    if (!dateRange.start && !dateRange.end) {
      return 'בחר טווח תאריכים...';
    }

    if (dateRange.start && !dateRange.end) {
      return `מ-${formatHebrewDate(dateRange.start)}`;
    }

    if (!dateRange.start && dateRange.end) {
      return `עד ${formatHebrewDate(dateRange.end)}`;
    }

    if (dateRange.start && dateRange.end) {
      return `${formatHebrewDate(dateRange.start)} - ${formatHebrewDate(dateRange.end)}`;
    }

    return 'בחר טווח תאריכים...';
  };

  const hasDateRange = dateRange.start || dateRange.end;

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        טווח תאריכים
      </label>

      <div className="space-y-2">
        {/* Quick presets */}
        <Select onValueChange={handlePresetSelect}>
          <SelectTrigger className="w-full text-right">
            <SelectValue placeholder="בחר טווח מוכן..." />
          </SelectTrigger>
          <SelectContent>
            {DATE_PRESETS.map((preset) => (
              <SelectItem key={preset.value} value={preset.value}>
                {preset.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Custom date range picker */}
        <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                'w-full justify-between text-right',
                hasDateRange && 'bg-orange-50 border-orange-200'
              )}
            >
              <span className="truncate">{getDisplayText()}</span>
              <Calendar className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>

          <PopoverContent className="w-auto p-0" align="start">
            <div className="p-3 border-b">
              <p className="text-sm font-medium text-center">
                {selectingStart ? 'בחר תאריך התחלה' : 'בחר תאריך סיום'}
              </p>
              {dateRange.start && (
                <p className="text-xs text-gray-500 text-center mt-1">
                  התחלה: {formatHebrewDate(dateRange.start)}
                </p>
              )}
            </div>

            <CalendarComponent
              mode="single"
              selected={selectingStart ? dateRange.start || undefined : dateRange.end || undefined}
              onSelect={handleCalendarSelect}
              className="rounded-md border-0"
              // locale="he" // Remove locale prop as it needs proper Locale import
            />

            <div className="p-3 border-t flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectingStart(!selectingStart)}
                className="flex-1"
              >
                {selectingStart ? 'עבור לתאריך סיום' : 'עבור לתאריך התחלה'}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="flex-1"
              >
                נקה
              </Button>
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {/* Selected date range display */}
      {hasDateRange && (
        <div className="flex flex-wrap gap-1">
          {dateRange.start && (
            <Badge variant="secondary" className="bg-orange-100 text-orange-800">
              התחלה: {formatHebrewDate(dateRange.start)}
              <button
                onClick={() => onChange({ start: null, end: dateRange.end })}
                className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <X className="h-3 w-3" />
                <span className="sr-only">הסר תאריך התחלה</span>
              </button>
            </Badge>
          )}

          {dateRange.end && (
            <Badge variant="secondary" className="bg-orange-100 text-orange-800">
              סיום: {formatHebrewDate(dateRange.end)}
              <button
                onClick={() => onChange({ start: dateRange.start, end: null })}
                className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <X className="h-3 w-3" />
                <span className="sr-only">הסר תאריך סיום</span>
              </button>
            </Badge>
          )}

          {dateRange.start && dateRange.end && (
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