/**
 * Hebrew PDF Helper
 * Functions to handle Hebrew text in PDF generation
 */

// Map Hebrew text to English equivalents for PDF headers
const hebrewToEnglishMap: { [key: string]: string } = {
  'דוח סטטיסטיקות החלטות ממשלה': 'Government Decisions Statistics Report',
  'מסננים פעילים': 'Active Filters',
  'ממשלות': 'Governments',
  'תחומי מדיניות': 'Policy Areas',
  'ועדות': 'Committees',
  'טווח תאריכים': 'Date Range',
  'ראש ממשלה': 'Prime Minister',
  'סוג החלטה': 'Decision Type',
  'אופרטיבית': 'Operative',
  'דקלרטיבית': 'Declarative',
  'כרטיסי מדדים': 'KPI Cards',
  'ציר זמן': 'Timeline',
  'התפלגות תחומי מדיניות': 'Policy Distribution',
  'פעילות ועדות': 'Committee Activity',
  'השוואת ממשלות': 'Government Comparison',
  'רשימת החלטות': 'Decisions List',
  'מספר': 'Number',
  'תאריך': 'Date',
  'כותרת': 'Title',
  'ממשלה': 'Government',
  'תחום': 'Area',
  'נוצר בתאריך': 'Created on',
  'מ-': 'From',
  'עד': 'To',
  ' נבחרו': ' selected',
};

/**
 * Convert Hebrew text to English for PDF compatibility
 */
export function hebrewToEnglish(text: string): string {
  // First check if we have a direct translation
  if (hebrewToEnglishMap[text]) {
    return hebrewToEnglishMap[text];
  }

  // Check for partial matches
  let translatedText = text;
  Object.entries(hebrewToEnglishMap).forEach(([hebrew, english]) => {
    translatedText = translatedText.replace(hebrew, english);
  });

  return translatedText;
}

/**
 * Reverse text for RTL display in PDF (if needed)
 */
export function reverseHebrewText(text: string): string {
  // Check if text contains Hebrew characters
  const hebrewRegex = /[\u0590-\u05FF]/;
  if (!hebrewRegex.test(text)) {
    return text;
  }

  // Reverse the text for RTL display
  return text.split('').reverse().join('');
}

/**
 * Format date for PDF display
 */
export function formatDateForPDF(date: Date): string {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}