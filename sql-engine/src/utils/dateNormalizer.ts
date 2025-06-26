/**
 * Date Normalizer for Hebrew Dates
 * Converts various Hebrew date formats to standard YYYY-MM-DD
 */

// Hebrew month names
const HEBREW_MONTHS: Record<string, number> = {
  'ינואר': 1, 'ינו': 1,
  'פברואר': 2, 'פבר': 2,
  'מרץ': 3, 'מרס': 3, 'מארס': 3,
  'אפריל': 4, 'אפר': 4,
  'מאי': 5,
  'יוני': 6,
  'יולי': 7,
  'אוגוסט': 8, 'אוג': 8,
  'ספטמבר': 9, 'ספט': 9,
  'אוקטובר': 10, 'אוק': 10,
  'נובמבר': 11, 'נוב': 11,
  'דצמבר': 12, 'דצמ': 12
};

// Current year for relative dates
const CURRENT_YEAR = new Date().getFullYear();

/**
 * Normalize various date formats to YYYY-MM-DD
 */
export function normalizeDateString(dateStr: string): string | null {
  const trimmed = dateStr.trim();
  console.log('[DateNormalizer] Processing:', dateStr);
  
  // Pattern 1: DD/MM/YYYY
  const slashPattern = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
  const slashMatch = trimmed.match(slashPattern);
  if (slashMatch) {
    const [, day, month, year] = slashMatch;
    const result = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    console.log('[DateNormalizer] Matched slash pattern:', result);
    return result;
  }
  
  // Pattern 2: DD.MM.YYYY or D.M.YYYY
  const dotPattern = /^(\d{1,2})\.(\d{1,2})\.(\d{4})$/;
  const dotMatch = trimmed.match(dotPattern);
  if (dotMatch) {
    const [, day, month, year] = dotMatch;
    const result = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    console.log('[DateNormalizer] Matched dot pattern:', result);
    return result;
  }
  
  // Pattern 3: DD-MM-YYYY
  const dashPattern = /^(\d{1,2})-(\d{1,2})-(\d{4})$/;
  const dashMatch = trimmed.match(dashPattern);
  if (dashMatch) {
    const [, day, month, year] = dashMatch;
    const result = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    console.log('[DateNormalizer] Matched dash pattern:', result);
    return result;
  }
  
  // Pattern 4: Hebrew month + year (e.g., "מרץ 21", "ינואר 2023", "מרץ 2023")
  const hebrewMonthPattern = new RegExp(`(${Object.keys(HEBREW_MONTHS).join('|')})\\s+(\\d{2,4})`, 'i');
  const hebrewMonthMatch = trimmed.match(hebrewMonthPattern);
  if (hebrewMonthMatch) {
    const [, monthName, year] = hebrewMonthMatch;
    const monthNum = HEBREW_MONTHS[monthName] || HEBREW_MONTHS[monthName.toLowerCase()];
    if (!monthNum) {
      console.warn('[DateNormalizer] Unknown Hebrew month:', monthName);
      return null;
    }
    const fullYear = year.length === 2 ? `20${year}` : year;
    // Return full date format YYYY-MM-01
    const result = `${fullYear}-${monthNum.toString().padStart(2, '0')}-01`;
    console.log('[DateNormalizer] Matched Hebrew month pattern:', result);
    return result;
  }
  
  // Pattern 5: Just year (e.g., "2023")
  const yearOnlyPattern = /^(\d{4})$/;
  const yearOnlyMatch = trimmed.match(yearOnlyPattern);
  if (yearOnlyMatch) {
    const result = `${yearOnlyMatch[1]}-01-01`;
    console.log('[DateNormalizer] Matched year only pattern:', result);
    return result;
  }
  
  // Pattern 6: Relative dates
  if (trimmed === 'היום') {
    const today = new Date();
    const result = formatDate(today);
    console.log('[DateNormalizer] Matched relative date "היום":', result);
    return result;
  }
  
  if (trimmed === 'אתמול') {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const result = formatDate(yesterday);
    console.log('[DateNormalizer] Matched relative date "אתמול":', result);
    return result;
  }
  
  // Pattern 7: "לפני X ימים/חודשים/שנים"
  const relativePattern = /לפני\s+(\d+)\s+(ימים|יום|חודשים|חודש|שנים|שנה)/;
  const relativeMatch = trimmed.match(relativePattern);
  if (relativeMatch) {
    const [, amount, unit] = relativeMatch;
    const date = new Date();
    const num = parseInt(amount);
    
    switch (unit) {
      case 'יום':
      case 'ימים':
        date.setDate(date.getDate() - num);
        break;
      case 'חודש':
      case 'חודשים':
        date.setMonth(date.getMonth() - num);
        break;
      case 'שנה':
      case 'שנים':
        date.setFullYear(date.getFullYear() - num);
        break;
    }
    
    const result = formatDate(date);
    console.log('[DateNormalizer] Matched relative pattern:', result);
    return result;
  }
  
  console.log('[DateNormalizer] No pattern matched for:', dateStr);
  return null; // Keep returning null for non-date strings
}

/**
 * Format Date object to YYYY-MM-DD
 */
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Extract date ranges from natural language
 */
export function extractDateRange(query: string): {
  startDate?: string;
  endDate?: string;
  year?: number;
} {
  const result: any = {};
  
  // Pattern: "משנת YYYY" or "מ-YYYY"
  const fromYearPattern = /(?:משנת|מ-)?\s*(\d{4})/;
  const fromYearMatch = query.match(fromYearPattern);
  if (fromYearMatch) {
    result.year = parseInt(fromYearMatch[1]);
    result.startDate = `${fromYearMatch[1]}-01-01`;
  }
  
  // Pattern: "מאז [date]" or "החל מ-[date]"
  const sincePattern = /(?:מאז|החל מ-?)\s*(?:ה-)?(.+?)(?:\s|$)/;
  const sinceMatch = query.match(sincePattern);
  if (sinceMatch) {
    const normalizedDate = normalizeDateString(sinceMatch[1]);
    if (normalizedDate) {
      result.startDate = normalizedDate;
    }
  }
  
  // Pattern: "עד [date]" or "לפני [date]"
  const untilPattern = /(?:עד|לפני)\s+(.+?)(?:\s|$)/;
  const untilMatch = query.match(untilPattern);
  if (untilMatch) {
    const normalizedDate = normalizeDateString(untilMatch[1]);
    if (normalizedDate) {
      result.endDate = normalizedDate;
    }
  }
  
  // Pattern: "בין [date1] ל-[date2]"
  const betweenPattern = /בין\s+(.+?)\s+(?:ל|לבין)-?\s*(.+?)(?:\s|$)/;
  const betweenMatch = query.match(betweenPattern);
  if (betweenMatch) {
    const date1 = normalizeDateString(betweenMatch[1]);
    const date2 = normalizeDateString(betweenMatch[2]);
    if (date1 && date2) {
      result.startDate = date1;
      result.endDate = date2;
    }
  }
  
  return result;
}

/**
 * Convert Hebrew ordinal numbers to regular numbers
 */
export function convertHebrewOrdinals(text: string): string {
  const ordinals: Record<string, string> = {
    'ראשון': '1',
    'ראשונה': '1',
    'שני': '2',
    'שניה': '2',
    'שלישי': '3',
    'שלישית': '3',
    'רביעי': '4',
    'רביעית': '4',
    'חמישי': '5',
    'חמישית': '5',
    'שישי': '6',
    'שישית': '6',
    'שביעי': '7',
    'שביעית': '7',
    'שמיני': '8',
    'שמינית': '8',
    'תשיעי': '9',
    'תשיעית': '9',
    'עשירי': '10',
    'עשירית': '10'
  };
  
  let result = text;
  for (const [hebrew, number] of Object.entries(ordinals)) {
    result = result.replace(new RegExp(`\\b${hebrew}\\b`, 'g'), number);
  }
  
  return result;
}
