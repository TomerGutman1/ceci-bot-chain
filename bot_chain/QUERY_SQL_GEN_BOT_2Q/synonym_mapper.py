"""
Hebrew synonym mapping for SQL query generation.
Maps user terms to database values and expands search coverage.
"""
from typing import Dict, List, Set, Optional
import re

# Core topic synonym mappings
TOPIC_SYNONYMS: Dict[str, List[str]] = {
    # Education
    "חינוך": ["חינוך", "השכלה", "חנוך", "מערכת החינוך", "חינוך פורמלי", "חינוך בלתי פורמלי"],
    "השכלה": ["חינוך", "השכלה", "לימודים", "אקדמיה"],
    "השכלה גבוהה": ["השכלה גבוהה", "אוניברסיטאות", "מכללות", "אקדמיה"],
    
    # Security
    "ביטחון": ["ביטחון", "בטחון", "ביטחון לאומי", "הגנה", "צבא", "ביטחון פנים"],
    "צבא": ["צבא", "צה\"ל", "כוחות הביטחון", "ביטחון"],
    "ביטחון פנים": ["ביטחון פנים", "משטרה", "כבאות", "ביטחון"],
    
    # Health
    "בריאות": ["בריאות", "רפואה", "בראות", "שירותי בריאות", "בריאות הציבור"],
    "רפואה": ["רפואה", "בריאות", "רופאים", "בתי חולים"],
    "קורונה": ["קורונה", "COVID-19", "מגפה", "בריאות"],
    
    # Economy
    "כלכלה": ["כלכלה", "כלכלי", "מסחר", "תעשייה", "עסקים", "משק"],
    "תקציב": ["תקציב", "תקציבי", "כספים", "מימון", "הקצאה"],
    "מיסים": ["מיסים", "מס", "מיסוי", "רשות המיסים"],
    
    # Transportation
    "תחבורה": ["תחבורה", "תיחבורה", "כבישים", "תחבורה ציבורית", "דרכים"],
    "תחבורה ציבורית": ["תחבורה ציבורית", "אוטובוסים", "רכבת", "תחבורה"],
    
    # Housing
    "דיור": ["דיור", "שיכון", "נדל\"ן", "בנייה", "דירות"],
    "בנייה": ["בנייה", "בניה", "תכנון ובנייה", "דיור"],
    
    # Environment
    "סביבה": ["סביבה", "איכות הסביבה", "איכות סביבה", "ירוק", "קיימות"],
    "אקלים": ["אקלים", "שינוי אקלים", "התחממות גלובלית", "סביבה"],
    
    # Welfare
    "רווחה": ["רווחה", "סעד", "שירותים חברתיים", "חברה"],
    "קשישים": ["קשישים", "גמלאים", "זקנה", "הגיל השלישי", "רווחה"],
    
    # Technology
    "טכנולוגיה": ["טכנולוגיה", "היי-טק", "חדשנות", "דיגיטל"],
    "דיגיטל": ["דיגיטל", "דיגיטלי", "מחשוב", "טכנולוגיה"],
    
    # Agriculture
    "חקלאות": ["חקלאות", "חקלאי", "משרד החקלאות", "חקלאים"],
    
    # Culture
    "תרבות": ["תרבות", "אמנות", "ספורט", "מורשת"],
    "ספורט": ["ספורט", "ספורטאים", "תרבות"],
    
    # Justice
    "משפט": ["משפט", "משפטי", "צדק", "בתי משפט", "חוק"],
    "חקיקה": ["חקיקה", "חוקים", "חוק", "משפט"],
    
    # Energy
    "אנרגיה": ["אנרגיה", "חשמל", "גז", "אנרגיה מתחדשת"],
    
    # Tourism
    "תיירות": ["תיירות", "תיירים", "תייר", "משרד התיירות"],
    
    # Immigration
    "עלייה": ["עלייה", "הגירה", "עולים", "קליטה"],
    
    # Religion
    "דת": ["דת", "דתות", "מועצות דתיות", "שירותי דת"]
}

# Ministry name variations
MINISTRY_SYNONYMS: Dict[str, List[str]] = {
    "משרד החינוך": ["משרד החינוך", "החינוך", "חינוך"],
    "משרד הביטחון": ["משרד הביטחון", "הביטחון", "ביטחון", "משרד הבטחון"],
    "משרד הבריאות": ["משרד הבריאות", "הבריאות", "בריאות"],
    "משרד האוצר": ["משרד האוצר", "האוצר", "אוצר"],
    "משרד התחבורה": ["משרד התחבורה", "התחבורה", "תחבורה", "משרד התחבורה והבטיחות בדרכים"],
    "משרד הרווחה": ["משרד הרווחה", "הרווחה", "רווחה", "משרד הרווחה והשירותים החברתיים"],
    "משרד המשפטים": ["משרד המשפטים", "המשפטים", "משפטים"],
    "משרד החקלאות": ["משרד החקלאות", "החקלאות", "חקלאות", "משרד החקלאות ופיתוח הכפר"],
    "משרד הכלכלה": ["משרד הכלכלה", "הכלכלה", "כלכלה", "משרד הכלכלה והתעשייה"],
    "משרד הפנים": ["משרד הפנים", "הפנים", "פנים"],
    "משרד החוץ": ["משרד החוץ", "החוץ", "חוץ", "משרד החוץ"],
    "משרד התרבות": ["משרד התרבות", "התרבות", "תרבות", "משרד התרבות והספורט"],
    "משרד השיכון": ["משרד השיכון", "השיכון", "שיכון", "משרד הבינוי והשיכון"],
    "משרד התיירות": ["משרד התיירות", "התיירות", "תיירות"],
    "משרד האנרגיה": ["משרד האנרגיה", "האנרגיה", "אנרגיה", "משרד האנרגיה והמים"],
    "משרד העלייה": ["משרד העלייה", "העלייה", "עלייה", "משרד העלייה והקליטה"],
    "המשרד להגנת הסביבה": ["המשרד להגנת הסביבה", "הגנת הסביבה", "סביבה", "משרד הסביבה"]
}

# Common typos and corrections
TYPO_CORRECTIONS: Dict[str, str] = {
    # Common typos
    "חנוך": "חינוך",
    "בראות": "בריאות",
    "תיחבורה": "תחבורה",
    "כלכללה": "כלכלה",
    "בטחון": "ביטחון",
    "החלתה": "החלטה",
    "ממשלת": "ממשלה",
    "משרהד": "משרד",
    "הכלכללה": "הכלכלה",
    
    # Alternative spellings
    "קוביד": "קורונה",
    "COVID": "קורונה",
    "היי טק": "היי-טק",
    "הייטק": "היי-טק",
    "נדלן": "נדל\"ן",
    "צהל": "צה\"ל"
}


def expand_topic_synonyms(topic: str) -> List[str]:
    """
    Expand a topic to include all its synonyms.
    
    Args:
        topic: The topic to expand
        
    Returns:
        List of synonyms including the original topic
    """
    # First check if it's a direct key
    if topic in TOPIC_SYNONYMS:
        return TOPIC_SYNONYMS[topic]
    
    # Check if it appears in any synonym list
    for key, synonyms in TOPIC_SYNONYMS.items():
        if topic in synonyms:
            return synonyms
    
    # Return just the original if no synonyms found
    return [topic]


def expand_ministry_synonyms(ministry: str) -> List[str]:
    """
    Expand a ministry name to include all its variations.
    
    Args:
        ministry: The ministry name to expand
        
    Returns:
        List of ministry name variations
    """
    # First check if it's a direct key
    if ministry in MINISTRY_SYNONYMS:
        return MINISTRY_SYNONYMS[ministry]
    
    # Check if it appears in any synonym list
    for key, synonyms in MINISTRY_SYNONYMS.items():
        if ministry in synonyms:
            return synonyms
    
    # Return just the original if no synonyms found
    return [ministry]


def correct_typos(text: str) -> str:
    """
    Correct common typos in Hebrew text.
    
    Args:
        text: Text to correct
        
    Returns:
        Corrected text
    """
    corrected = text
    
    # Apply direct corrections
    for typo, correction in TYPO_CORRECTIONS.items():
        corrected = corrected.replace(typo, correction)
    
    return corrected


def get_all_synonyms_for_topic(topic: str) -> Set[str]:
    """
    Get all possible synonyms for a topic including typo corrections.
    
    Args:
        topic: The topic to get synonyms for
        
    Returns:
        Set of all possible synonyms
    """
    # Correct typos first
    corrected_topic = correct_typos(topic)
    
    # Get synonyms
    synonyms = set(expand_topic_synonyms(corrected_topic))
    
    # Also check the original (uncorrected) topic
    if topic != corrected_topic:
        synonyms.update(expand_topic_synonyms(topic))
    
    return synonyms


def normalize_topic_for_db(topic: str) -> str:
    """
    Normalize a topic to its canonical database form.
    
    Args:
        topic: Topic to normalize
        
    Returns:
        Normalized topic string
    """
    # Correct typos
    corrected = correct_typos(topic)
    
    # Find canonical form (first item in synonym list)
    for canonical, synonyms in TOPIC_SYNONYMS.items():
        if corrected in synonyms:
            return canonical
    
    return corrected


def build_topic_sql_condition(topic: str, field: str = "tags_policy_area") -> str:
    """
    Build SQL condition for topic search with synonym expansion.
    
    Args:
        topic: Topic to search for
        field: Database field to search in
        
    Returns:
        SQL condition string
    """
    synonyms = get_all_synonyms_for_topic(topic)
    
    if len(synonyms) == 1:
        return f"{field} ILIKE '%%{list(synonyms)[0]}%%'"
    
    conditions = [f"{field} ILIKE '%%{syn}%%'" for syn in synonyms]
    return f"({' OR '.join(conditions)})"


def build_ministry_sql_condition(ministry: str, field: str = "tags_government_body") -> str:
    """
    Build SQL condition for ministry search with synonym expansion.
    
    Args:
        ministry: Ministry to search for
        field: Database field to search in
        
    Returns:
        SQL condition string
    """
    synonyms = expand_ministry_synonyms(ministry)
    
    if len(synonyms) == 1:
        return f"{field} ILIKE '%%{synonyms[0]}%%'"
    
    conditions = [f"{field} ILIKE '%%{syn}%%'" for syn in synonyms]
    return f"({' OR '.join(conditions)})"