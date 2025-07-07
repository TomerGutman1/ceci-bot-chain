/**
 * Search Filter Component
 * Real-time search across decision titles, content, and tags
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Search, X, Clock } from 'lucide-react';
import { Input } from '@/components/ui/input';
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
import { useSearchDecisions } from '../../hooks/useDecisions';
import { useDebounce } from '../../hooks/useDebounce';

interface SearchFilterProps {
  searchText: string;
  onChange: (text: string) => void;
  className?: string;
}

// Recent searches storage key
const RECENT_SEARCHES_KEY = 'dashboard-recent-searches';
const MAX_RECENT_SEARCHES = 5;

// Popular search suggestions
const SEARCH_SUGGESTIONS = [
  'חינוך',
  'בריאות',
  'ביטחון',
  'כלכלה',
  'תחבורה',
  'דיור',
  'סביבה',
  'משפט',
  'רווחה',
  'תרבות',
];

export default function SearchFilter({
  searchText,
  onChange,
  className,
}: SearchFilterProps) {
  const [inputValue, setInputValue] = useState(searchText);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  
  // Debounce search input to avoid too many API calls
  const debouncedSearchText = useDebounce(inputValue, 300);
  
  // Search results for autocomplete
  const { 
    data: searchResults, 
    isLoading: searchLoading 
  } = useSearchDecisions(
    debouncedSearchText, 
    debouncedSearchText.length >= 2 && showSuggestions
  );

  // Load recent searches from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Error loading recent searches:', error);
    }
  }, []);

  // Update search text when debounced value changes
  useEffect(() => {
    if (debouncedSearchText !== searchText) {
      onChange(debouncedSearchText);
    }
  }, [debouncedSearchText, searchText, onChange]);

  // Save search to recent searches
  const saveToRecentSearches = useCallback((search: string) => {
    if (!search.trim() || search.length < 2) return;
    
    try {
      const updated = [
        search.trim(),
        ...recentSearches.filter(s => s !== search.trim())
      ].slice(0, MAX_RECENT_SEARCHES);
      
      setRecentSearches(updated);
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error('Error saving recent search:', error);
    }
  }, [recentSearches]);

  const handleInputChange = (value: string) => {
    setInputValue(value);
    if (value.length >= 2) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleSearch = (searchTerm: string) => {
    setInputValue(searchTerm);
    onChange(searchTerm);
    setShowSuggestions(false);
    saveToRecentSearches(searchTerm);
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
    setShowSuggestions(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      setShowSuggestions(false);
      saveToRecentSearches(inputValue);
    }
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem(RECENT_SEARCHES_KEY);
  };

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        חיפוש חופשי
      </label>

      <Popover open={showSuggestions} onOpenChange={setShowSuggestions}>
        <PopoverTrigger asChild>
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="חפש בכותרות, תוכן או תגיות..."
              value={inputValue}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyPress={handleKeyPress}
              onFocus={() => inputValue.length >= 2 && setShowSuggestions(true)}
              className={cn(
                'pr-10 text-right',
                inputValue && 'pl-10' // Add space for clear button
              )}
            />
            {inputValue && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="absolute left-1 top-1/2 h-6 w-6 -translate-y-1/2 p-0 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">נקה חיפוש</span>
              </Button>
            )}
          </div>
        </PopoverTrigger>

        <PopoverContent className="w-full p-0" align="start">
          <Command>
            <CommandList className="max-h-96">
              {/* Search results */}
              {searchResults && searchResults.length > 0 && (
                <CommandGroup heading="תוצאות חיפוש">
                  {searchResults.slice(0, 5).map((decision) => (
                    <CommandItem
                      key={decision.id}
                      value={decision.decision_title}
                      onSelect={() => handleSearch(decision.decision_title)}
                      className="cursor-pointer"
                    >
                      <div className="text-right w-full">
                        <div className="font-medium text-sm line-clamp-1">
                          {decision.decision_title}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          החלטה {decision.decision_number} • ממשלה {decision.government_number}
                        </div>
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}

              {/* Recent searches */}
              {recentSearches.length > 0 && (
                <CommandGroup>
                  <div className="flex items-center justify-between px-2 py-1">
                    <span className="text-xs font-medium text-gray-500">חיפושים אחרונים</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearRecentSearches}
                      className="h-4 px-1 text-xs text-gray-400 hover:text-gray-600"
                    >
                      נקה
                    </Button>
                  </div>
                  {recentSearches.map((search, index) => (
                    <CommandItem
                      key={index}
                      value={search}
                      onSelect={() => handleSearch(search)}
                      className="cursor-pointer"
                    >
                      <Clock className="mr-2 h-3 w-3 text-gray-400" />
                      <span className="text-right">{search}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}

              {/* Search suggestions */}
              {!searchResults?.length && inputValue.length < 2 && (
                <CommandGroup heading="הצעות חיפוש">
                  {SEARCH_SUGGESTIONS.map((suggestion) => (
                    <CommandItem
                      key={suggestion}
                      value={suggestion}
                      onSelect={() => handleSearch(suggestion)}
                      className="cursor-pointer"
                    >
                      <span className="text-right">{suggestion}</span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}

              {/* Loading state */}
              {searchLoading && (
                <div className="p-4 text-center text-sm text-gray-500">
                  מחפש...
                </div>
              )}

              {/* No results */}
              {inputValue.length >= 2 && searchResults?.length === 0 && !searchLoading && (
                <CommandEmpty>לא נמצאו תוצאות חיפוש</CommandEmpty>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Active search display */}
      {searchText && (
        <div className="flex items-center gap-2">
          <Badge
            variant="secondary"
            className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200"
          >
            <Search className="w-3 h-3 ml-1" />
            <span className="max-w-[200px] truncate">{searchText}</span>
            <button
              onClick={handleClear}
              className="mr-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <X className="h-3 w-3" />
              <span className="sr-only">נקה חיפוש</span>
            </button>
          </Badge>
        </div>
      )}
    </div>
  );
}