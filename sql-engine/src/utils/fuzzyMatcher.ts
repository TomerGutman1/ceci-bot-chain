/**
 * Fuzzy Matcher for Hebrew Tags
 * Implements Levenshtein distance for tag matching with comprehensive synonyms
 */

// All available policy tags
export const POLICY_TAGS = [
  'ביטחון לאומי וצה״ל',
  'ביטחון פנים וחירום אזרחי',
  'דיפלומטיה ויחסים בינ״ל',
  'הגירה וקליטת עלייה',
  'תעסוקה ושוק העבודה',
  'כלכלה מאקרו ותקציב',
  'פיננסים, ביטוח ומסים',
  'פיתוח כלכלי ותחרות',
  'יוקר המחיה ושוק הצרכן',
  'תחבורה ציבורית ותשתיות דרך',
  'בטיחות בדרכים ורכב',
  'אנרגיה',
  'מים ותשתיות מים',
  'סביבה, אקלים ומגוון ביולוגי',
  'רשות הטבע והגנים ונוף',
  'חקלאות ופיתוח הכפר',
  'דיור, נדל״ן ותכנון',
  'שלטון מקומי ופיתוח פריפריה',
  'בריאות ורפואה',
  'רווחה ושירותים חברתיים',
  'אזרחים ותיקים',
  'שוויון חברתי וזכויות אדם',
  'מיעוטים ואוכלוסיות ייחודיות',
  'מילואים ותמיכה בלוחמים',
  'חינוך',
  'השכלה גבוהה ומחקר',
  'תרבות ואמנות',
  'ספורט ואורח חיים פעיל',
  'מורשת ולאום',
  'תיירות ופנאי',
  'דת ומוסדות דת',
  'טכנולוגיה, חדשנות ודיגיטל',
  'סייבר ואבטחת מידע',
  'תקשורת ומדיה',
  'משפט, חקיקה ורגולציה'
];

// Maximum Levenshtein distance for fuzzy matching
const MAX_LEVENSHTEIN_DISTANCE = 2;

// Common synonyms and mappings - COMPREHENSIVE VERSION
export const TAG_SYNONYMS: Record<string, string> = {
  // Environment variations
  'איכות הסביבה': 'סביבה, אקלים ומגוון ביולוגי',
  'איכות סביבה': 'סביבה, אקלים ומגוון ביולוגי',
  'סביבה': 'סביבה, אקלים ומגוון ביולוגי',
  'אקלים': 'סביבה, אקלים ומגוון ביולוגי',
  'איכות-הסביבה': 'סביבה, אקלים ומגוון ביולוגי',
  'הסביבה': 'סביבה, אקלים ומגוון ביולוגי',
  
  // Science and research
  'מדע': 'השכלה גבוהה ומחקר',
  'מחקר': 'השכלה גבוהה ומחקר',
  'אקדמיה': 'השכלה גבוהה ומחקר',
  'מדעים': 'השכלה גבוהה ומחקר',
  'אוניברסיטה': 'השכלה גבוהה ומחקר',
  'אוניברסיטאות': 'השכלה גבוהה ומחקר',
  
  // Elderly and pensions
  'פנסיה': 'אזרחים ותיקים',
  'פנסיות': 'אזרחים ותיקים',
  'גמלאים': 'אזרחים ותיקים',
  'קשישים': 'אזרחים ותיקים',
  'זקנה': 'אזרחים ותיקים',
  'גיל הזהב': 'אזרחים ותיקים',
  'ותיקים': 'אזרחים ותיקים',
  
  // Health variations
  'קורונה': 'בריאות ורפואה',
  'בריאות הציבור': 'בריאות ורפואה',
  'רפואה': 'בריאות ורפואה',
  'בריאות': 'בריאות ורפואה',
  'מערכת הבריאות': 'בריאות ורפואה',
  'בתי חולים': 'בריאות ורפואה',
  'בראות': 'בריאות ורפואה', // Common typo
  'בריאת': 'בריאות ורפואה', // Common typo
  
  // Education variations
  'חינוך מיוחד': 'חינוך',
  'בתי ספר': 'חינוך',
  'חנוך': 'חינוך', // Common typo
  'השכלה': 'חינוך',
  'מערכת החינוך': 'חינוך',
  'חינוך': 'חינוך', // Direct match
  
  // Security variations
  'ביטחון': 'ביטחון לאומי וצה״ל',
  'צבא': 'ביטחון לאומי וצה״ל',
  'צהל': 'ביטחון לאומי וצה״ל',
  'צה״ל': 'ביטחון לאומי וצה״ל',
  'ביטחון המדינה': 'ביטחון לאומי וצה״ל',
  'בטחון': 'ביטחון לאומי וצה״ל', // Common typo
  
  // Technology variations
  'היי טק': 'טכנולוגיה, חדשנות ודיגיטל',
  'הייטק': 'טכנולוגיה, חדשנות ודיגיטל',
  'טכנולוגיה': 'טכנולוגיה, חדשנות ודיגיטל',
  'חדשנות': 'טכנולוגיה, חדשנות ודיגיטל',
  'דיגיטל': 'טכנולוגיה, חדשנות ודיגיטל',
  
  // Transportation
  'תחבורה': 'תחבורה ציבורית ותשתיות דרך',
  'כבישים': 'תחבורה ציבורית ותשתיות דרך',
  'רכבות': 'תחבורה ציבורית ותשתיות דרך',
  'תחבורה ציבורית': 'תחבורה ציבורית ותשתיות דרך',
  'דרכים': 'תחבורה ציבורית ותשתיות דרך',
  
  // Real estate
  'נדלן': 'דיור, נדל״ן ותכנון',
  'נדל״ן': 'דיור, נדל״ן ותכנון',
  'דיור': 'דיור, נדל״ן ותכנון',
  'שיכון': 'דיור, נדל״ן ותכנון',
  
  // Minorities and Arab society
  'החברה הערבית': 'מיעוטים ואוכלוסיות ייחודיות',
  'ערבים': 'מיעוטים ואוכלוסיות ייחודיות',
  'מיעוטים': 'מיעוטים ואוכלוסיות ייחודיות',
  'מגזר ערבי': 'מיעוטים ואוכלוסיות ייחודיות',
  'אוכלוסייה ערבית': 'מיעוטים ואוכלוסיות ייחודיות',
  'דרוזים': 'מיעוטים ואוכלוסיות ייחודיות',
  'בדואים': 'מיעוטים ואוכלוסיות ייחודיות',
  'צרקסים': 'מיעוטים ואוכלוסיות ייחודיות',
  
  // Additional common mappings
  'כלכלה': 'כלכלה מאקרו ותקציב',
  'תקציב': 'כלכלה מאקרו ותקציב',
  'מיסים': 'פיננסים, ביטוח ומסים',
  'מס': 'פיננסים, ביטוח ומסים',
  'ביטוח': 'פיננסים, ביטוח ומסים'
};

/**
 * Calculate Levenshtein distance between two strings
 */
export function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];
  
  // Handle edge cases
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  
  // Initialize matrix
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }
  
  // Calculate distances
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1      // deletion
        );
      }
    }
  }
  
  return matrix[b.length][a.length];
}

/**
 * Find the best matching tag for a given input
 * @param input - User input to match
 * @param maxDistance - Maximum Levenshtein distance to consider (default: MAX_LEVENSHTEIN_DISTANCE)
 * @returns Best matching tag or null if no good match
 */
export function findBestMatchingTag(input: string, maxDistance: number = MAX_LEVENSHTEIN_DISTANCE): string | null {
  const normalizedInput = input.trim().toLowerCase();
  
  console.log('[FuzzyMatcher] Looking for match for:', input);
  
  // Step 1: Check exact synonym match (highest priority)
  if (TAG_SYNONYMS[normalizedInput]) {
    console.log('[FuzzyMatcher] Found exact synonym match:', normalizedInput, '→', TAG_SYNONYMS[normalizedInput]);
    return TAG_SYNONYMS[normalizedInput];
  }
  
  // Also check original case
  if (TAG_SYNONYMS[input.trim()]) {
    console.log('[FuzzyMatcher] Found exact synonym match (original case):', input.trim(), '→', TAG_SYNONYMS[input.trim()]);
    return TAG_SYNONYMS[input.trim()];
  }
  
  // Step 2: Check if input is contained in any tag (partial match)
  for (const tag of POLICY_TAGS) {
    const normalizedTag = tag.toLowerCase();
    if (normalizedTag.includes(normalizedInput)) {
      console.log('[FuzzyMatcher] Found partial match:', normalizedInput, 'in', tag);
      return tag;
    }
  }
  
  // Step 3: Find tag with minimum Levenshtein distance
  let bestMatch: string | null = null;
  let minDistance = Infinity;
  
  // First check against synonyms keys for fuzzy matching
  for (const [synonym, tag] of Object.entries(TAG_SYNONYMS)) {
    const distance = levenshteinDistance(normalizedInput, synonym.toLowerCase());
    if (distance < minDistance && distance <= maxDistance) {
      minDistance = distance;
      bestMatch = tag;
      console.log('[FuzzyMatcher] Fuzzy synonym match:', normalizedInput, '→', synonym, '→', tag, `(distance: ${distance})`);
    }
  }
  
  // Then check against actual tags
  for (const tag of POLICY_TAGS) {
    const distance = levenshteinDistance(normalizedInput, tag.toLowerCase());
    
    if (distance < minDistance && distance <= maxDistance) {
      minDistance = distance;
      bestMatch = tag;
      console.log('[FuzzyMatcher] Fuzzy tag match:', normalizedInput, '→', tag, `(distance: ${distance})`);
    }
  }
  
  if (bestMatch) {
    console.log('[FuzzyMatcher] Final fuzzy match:', normalizedInput, '→', bestMatch, `(distance: ${minDistance})`);
  } else {
    console.log('[FuzzyMatcher] No match found for:', normalizedInput, '- will use fallback search');
  }
  
  return bestMatch;
}

/**
 * Check if a topic matches any tag (exact or fuzzy)
 */
export function isTopicInTags(topic: string): boolean {
  const normalizedTopic = topic.trim().toLowerCase();
  
  // Check synonyms
  if (TAG_SYNONYMS[normalizedTopic] || TAG_SYNONYMS[topic.trim()]) {
    return true;
  }
  
  // Check if contained in any tag
  for (const tag of POLICY_TAGS) {
    if (tag.toLowerCase().includes(normalizedTopic)) {
      return true;
    }
  }
  
  // Check fuzzy match
  const fuzzyMatch = findBestMatchingTag(topic, MAX_LEVENSHTEIN_DISTANCE);
  return fuzzyMatch !== null;
}

/**
 * Get SQL condition for topic search
 */
export function getTopicSearchCondition(topic: string, paramIndex: number): {
  sql: string;
  param: string;
} {
  const bestMatch = findBestMatchingTag(topic);
  
  if (bestMatch) {
    // Found a matching tag - search in tags_policy_area
    console.log('[FuzzyMatcher] Using tag search for:', topic, '→', bestMatch);
    return {
      sql: `tags_policy_area ILIKE $${paramIndex}`,
      param: `%${bestMatch}%`
    };
  }
  
  // No tag match - search in all text fields (fallback)
  console.log('[FuzzyMatcher] Using comprehensive search for:', topic);
  return {
    sql: `(tags_policy_area ILIKE $${paramIndex} 
        OR summary ILIKE $${paramIndex} 
        OR decision_content ILIKE $${paramIndex}
        OR decision_title ILIKE $${paramIndex})`,
    param: `%${topic}%`
  };
}
