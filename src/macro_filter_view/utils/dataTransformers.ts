/**
 * Data transformation utilities for converting database schema to dashboard format
 * Handles parsing, formatting, and normalizing government decisions data
 */

import type { GovernmentDecision, DashboardDecision, DashboardFilters } from '../types/decision';

/**
 * Transform raw database decision to dashboard-friendly format
 */
export function transformDecision(raw: GovernmentDecision): DashboardDecision {
  return {
    id: raw.id,
    title: raw.decision_title,
    number: raw.decision_number,
    date: new Date(raw.decision_date),
    government: parseInt(raw.government_number),
    primeMinister: raw.prime_minister,
    committee: raw.committee,
    summary: raw.summary,
    content: raw.decision_content,
    type: raw.operativity,
    policyAreas: parseTags(raw.tags_policy_area),
    governmentBodies: parseTags(raw.tags_government_body),
    locations: parseTags(raw.tags_location),
    url: raw.decision_url,
    key: raw.decision_key,
  };
}

/**
 * Parse comma-separated tag strings into arrays
 */
export function parseTags(tagString: string | null): string[] {
  if (!tagString || tagString.trim() === '') {
    return [];
  }
  
  return tagString
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0)
    .map(tag => normalizeTag(tag));
}

/**
 * Normalize tag text (trim, remove extra spaces, handle Hebrew)
 */
export function normalizeTag(tag: string): string {
  return tag
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .trim()
    .replace(/^["']|["']$/g, ''); // Remove surrounding quotes
}

/**
 * Extract unique values from decision arrays for filter options
 */
export function extractFilterOptions(decisions: DashboardDecision[]) {
  const governments = new Set<number>();
  const committees = new Set<string>();
  const policyAreas = new Set<string>();
  const primeMinister = new Set<string>();
  const locations = new Set<string>();

  decisions.forEach(decision => {
    governments.add(decision.government);
    
    if (decision.committee) {
      committees.add(decision.committee);
    }
    
    decision.policyAreas.forEach(area => policyAreas.add(area));
    decision.governmentBodies.forEach(body => committees.add(body));
    decision.locations.forEach(location => locations.add(location));
    
    primeMinister.add(decision.primeMinister);
  });

  return {
    governments: Array.from(governments).sort((a, b) => b - a), // Most recent first
    committees: Array.from(committees).sort(),
    policyAreas: Array.from(policyAreas).sort(),
    primeMinister: Array.from(primeMinister).sort(),
    locations: Array.from(locations).sort(),
  };
}

/**
 * Generate default filter state
 */
export function getDefaultFilters(): DashboardFilters {
  return {
    governments: [],
    committees: [],
    policyAreas: [],
    primeMinister: null,
    dateRange: {
      start: null,
      end: null,
    },
    locations: [],
    decisionType: 'all',
    searchText: '',
  };
}

/**
 * Check if filters are in default/empty state
 */
export function isFiltersEmpty(filters: DashboardFilters): boolean {
  return (
    filters.governments.length === 0 &&
    filters.committees.length === 0 &&
    filters.policyAreas.length === 0 &&
    !filters.primeMinister &&
    !filters.dateRange.start &&
    !filters.dateRange.end &&
    filters.locations.length === 0 &&
    filters.decisionType === 'all' &&
    filters.searchText.trim() === ''
  );
}

/**
 * Count active filters for display
 */
export function countActiveFilters(filters: DashboardFilters): number {
  let count = 0;
  
  if (filters.governments.length > 0) count++;
  if (filters.committees.length > 0) count++;
  if (filters.policyAreas.length > 0) count++;
  if (filters.primeMinister) count++;
  if (filters.dateRange.start || filters.dateRange.end) count++;
  if (filters.locations.length > 0) count++;
  if (filters.decisionType !== 'all') count++;
  if (filters.searchText.trim()) count++;
  
  return count;
}

/**
 * Format Hebrew dates for display
 */
export function formatHebrewDate(date: Date): string {
  const hebrewMonths = [
    'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
    'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
  ];
  
  const day = date.getDate();
  const month = hebrewMonths[date.getMonth()];
  const year = date.getFullYear();
  
  return `${day} ב${month} ${year}`;
}

/**
 * Format relative time in Hebrew
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return 'היום';
  } else if (diffDays === 1) {
    return 'אתמול';
  } else if (diffDays < 7) {
    return `לפני ${diffDays} ימים`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return weeks === 1 ? 'לפני שבוע' : `לפני ${weeks} שבועות`;
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return months === 1 ? 'לפני חודש' : `לפני ${months} חודשים`;
  } else {
    const years = Math.floor(diffDays / 365);
    return years === 1 ? 'לפני שנה' : `לפני ${years} שנים`;
  }
}

/**
 * Format numbers with Hebrew separators
 */
export function formatHebrewNumber(num: number): string {
  return num.toLocaleString('he-IL');
}

/**
 * Generate color for policy areas consistently
 */
export function getPolicyAreaColor(area: string): string {
  const colors = [
    '#3b82f6', // Blue
    '#ef4444', // Red  
    '#10b981', // Green
    '#f59e0b', // Amber
    '#8b5cf6', // Purple
    '#06b6d4', // Cyan
    '#f97316', // Orange
    '#84cc16', // Lime
    '#ec4899', // Pink
    '#6b7280', // Gray
  ];
  
  // Simple hash function for consistent color assignment
  let hash = 0;
  for (let i = 0; i < area.length; i++) {
    hash = area.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}

/**
 * Sort decisions by various criteria
 */
export function sortDecisions(
  decisions: DashboardDecision[],
  sortBy: 'date' | 'title' | 'government' | 'type',
  direction: 'asc' | 'desc' = 'desc'
): DashboardDecision[] {
  const sorted = [...decisions].sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'date':
        comparison = a.date.getTime() - b.date.getTime();
        break;
      case 'title':
        comparison = a.title.localeCompare(b.title, 'he');
        break;
      case 'government':
        comparison = a.government - b.government;
        break;
      case 'type':
        comparison = a.type.localeCompare(b.type, 'he');
        break;
    }
    
    return direction === 'asc' ? comparison : -comparison;
  });
  
  return sorted;
}

/**
 * Group decisions by date periods
 */
export function groupDecisionsByPeriod(
  decisions: DashboardDecision[],
  period: 'day' | 'month' | 'year'
): Map<string, DashboardDecision[]> {
  const groups = new Map<string, DashboardDecision[]>();
  
  decisions.forEach(decision => {
    let key: string;
    
    switch (period) {
      case 'day':
        key = decision.date.toISOString().split('T')[0];
        break;
      case 'month':
        key = `${decision.date.getFullYear()}-${String(decision.date.getMonth() + 1).padStart(2, '0')}`;
        break;
      case 'year':
        key = String(decision.date.getFullYear());
        break;
    }
    
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key)!.push(decision);
  });
  
  return groups;
}

/**
 * Calculate statistics from decision array
 */
export function calculateStatistics(decisions: DashboardDecision[]) {
  const total = decisions.length;
  const operational = decisions.filter(d => d.type === 'אופרטיבית').length;
  const declarative = decisions.filter(d => d.type === 'דקלרטיבית').length;
  
  // Group by policy areas
  const policyAreaCounts = new Map<string, number>();
  decisions.forEach(decision => {
    decision.policyAreas.forEach(area => {
      policyAreaCounts.set(area, (policyAreaCounts.get(area) || 0) + 1);
    });
  });
  
  // Group by committees
  const committeeCounts = new Map<string, number>();
  decisions.forEach(decision => {
    if (decision.committee) {
      committeeCounts.set(decision.committee, (committeeCounts.get(decision.committee) || 0) + 1);
    }
  });
  
  return {
    total,
    operational,
    declarative,
    operationalPercentage: total > 0 ? (operational / total) * 100 : 0,
    declarativePercentage: total > 0 ? (declarative / total) * 100 : 0,
    policyAreaCounts: Array.from(policyAreaCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10), // Top 10
    committeeCounts: Array.from(committeeCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10), // Top 10
  };
}

/**
 * Validate filter values
 */
export function validateFilters(filters: DashboardFilters): string[] {
  const errors: string[] = [];
  
  if (filters.dateRange.start && filters.dateRange.end) {
    if (filters.dateRange.start > filters.dateRange.end) {
      errors.push('תאריך ההתחלה חייב להיות לפני תאריך הסיום');
    }
  }
  
  if (filters.searchText.length > 100) {
    errors.push('טקסט החיפוש לא יכול להיות ארוך מ-100 תווים');
  }
  
  return errors;
}