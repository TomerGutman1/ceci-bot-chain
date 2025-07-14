"""
Date interpretation utilities for Hebrew queries.
Handles various date expressions and converts them to SQL-compatible formats.
"""
from datetime import datetime, timedelta, date
from typing import Dict, Optional, Tuple, Any
import re
from calendar import monthrange

# Hebrew month names
HEBREW_MONTHS = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "מרס": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12
}

# Hebrew day names
HEBREW_DAYS = {
    "ראשון": 0, "שני": 1, "שלישי": 2, "רביעי": 3,
    "חמישי": 4, "שישי": 5, "שבת": 6
}

# Hebrew relative time expressions
HEBREW_RELATIVE_TIME = {
    "היום": 0,
    "אתמול": -1,
    "שלשום": -2,
    "מחר": 1,
    "מחרתיים": 2
}


def get_current_date() -> date:
    """Get current date (mockable for tests)."""
    return datetime.now().date()


def interpret_hebrew_date(text: str) -> Optional[Dict[str, str]]:
    """
    Interpret Hebrew date expressions and return date range.
    
    Args:
        text: Hebrew text containing date expression
        
    Returns:
        Dict with 'start' and 'end' dates in YYYY-MM-DD format, or None
    """
    today = get_current_date()
    current_year = today.year
    
    # Handle "השנה" (this year)
    if "השנה" in text:
        return {
            "start": f"{current_year}-01-01",
            "end": f"{current_year}-12-31"
        }
    
    # Handle "השנה שעברה" (last year)
    if "השנה שעברה" in text or "שנה שעברה" in text:
        last_year = current_year - 1
        return {
            "start": f"{last_year}-01-01",
            "end": f"{last_year}-12-31"
        }
    
    # Handle "החודש" (this month)
    if "החודש" in text:
        start = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end = today.replace(day=last_day)
        return {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d")
        }
    
    # Handle "החודש שעבר" (last month)
    if "החודש שעבר" in text or "חודש שעבר" in text:
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return {
            "start": last_month_start.strftime("%Y-%m-%d"),
            "end": last_month_end.strftime("%Y-%m-%d")
        }
    
    # Handle "X השנים האחרונות" (last X years)
    match = re.search(r'(\d+)\s*השנים\s*האחרונות', text)
    if match:
        years = int(match.group(1))
        start_year = current_year - years + 1
        return {
            "start": f"{start_year}-01-01",
            "end": today.strftime("%Y-%m-%d")
        }
    
    # Handle "X החודשים האחרונים" (last X months)
    match = re.search(r'(\d+)\s*החודשים\s*האחרונים', text)
    if match:
        months = int(match.group(1))
        start_date = today - timedelta(days=months * 30)  # Approximate
        return {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d")
        }
    
    # Handle "בין X ל-Y" (between X and Y)
    match = re.search(r'בין\s*(\d{4})\s*ל[-\s]*(\d{4})', text)
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        return {
            "start": f"{start_year}-01-01",
            "end": f"{end_year}-12-31"
        }
    
    # Handle "מ-X עד Y" (from X to Y)
    match = re.search(r'מ[-\s]*(\d{4})\s*עד\s*(\d{4})', text)
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        return {
            "start": f"{start_year}-01-01",
            "end": f"{end_year}-12-31"
        }
    
    # Handle single year "ב-YYYY" or "בשנת YYYY"
    match = re.search(r'ב[-\s]*(\d{4})|בשנת\s*(\d{4})', text)
    if match:
        year = int(match.group(1) or match.group(2))
        return {
            "start": f"{year}-01-01",
            "end": f"{year}-12-31"
        }
    
    # Handle month + year (e.g., "ינואר 2024")
    for month_name, month_num in HEBREW_MONTHS.items():
        pattern = rf'{month_name}\s*(\d{{4}})'
        match = re.search(pattern, text)
        if match:
            year = int(match.group(1))
            _, last_day = monthrange(year, month_num)
            return {
                "start": f"{year}-{month_num:02d}-01",
                "end": f"{year}-{month_num:02d}-{last_day:02d}"
            }
    
    # Handle relative days
    for hebrew_day, days_offset in HEBREW_RELATIVE_TIME.items():
        if hebrew_day in text:
            target_date = today + timedelta(days=days_offset)
            return {
                "start": target_date.strftime("%Y-%m-%d"),
                "end": target_date.strftime("%Y-%m-%d")
            }
    
    # Handle "השבוע" (this week)
    if "השבוע" in text:
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return {
            "start": start_of_week.strftime("%Y-%m-%d"),
            "end": end_of_week.strftime("%Y-%m-%d")
        }
    
    # Handle "השבוע שעבר" (last week)
    if "השבוע שעבר" in text or "שבוע שעבר" in text:
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)
        return {
            "start": start_of_week.strftime("%Y-%m-%d"),
            "end": end_of_week.strftime("%Y-%m-%d")
        }
    
    # Handle date range already in entities
    if "date_range" in text:
        return None  # Let the caller handle existing date_range
    
    return None


def extract_date_from_entities(entities: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Extract and normalize date information from entities.
    
    Args:
        entities: Entity dictionary from intent detection
        
    Returns:
        Dict with 'start' and 'end' dates, or None
    """
    # Check if date_range already exists
    if "date_range" in entities and isinstance(entities["date_range"], dict):
        date_range = entities["date_range"]
        if "start" in date_range and "end" in date_range:
            return {
                "start": normalize_date_format(date_range["start"]),
                "end": normalize_date_format(date_range["end"])
            }
    
    # Check for year entity
    if "year" in entities:
        year = int(entities["year"])
        return {
            "start": f"{year}-01-01",
            "end": f"{year}-12-31"
        }
    
    # Check for start_date and end_date
    if "start_date" in entities and "end_date" in entities:
        return {
            "start": normalize_date_format(entities["start_date"]),
            "end": normalize_date_format(entities["end_date"])
        }
    
    # Check topic for embedded dates
    if "topic" in entities:
        date_range = interpret_hebrew_date(entities["topic"])
        if date_range:
            # Clean the date expression from topic
            cleaned_topic = clean_date_from_text(entities["topic"])
            entities["topic"] = cleaned_topic
            return date_range
    
    return None


def normalize_date_format(date_str: str) -> str:
    """
    Normalize various date formats to YYYY-MM-DD.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date in YYYY-MM-DD format
    """
    # Already in correct format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # Handle DD/MM/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # Handle DD-MM-YYYY
    match = re.match(r'^(\d{1,2})-(\d{1,2})-(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # Handle YYYY/MM/DD
    match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # Default - return as is
    return date_str


def clean_date_from_text(text: str) -> str:
    """
    Remove date expressions from text.
    
    Args:
        text: Text containing date expressions
        
    Returns:
        Cleaned text without date expressions
    """
    # Patterns to remove
    patterns = [
        r'\b\d{4}\b',  # Years
        r'השנה\s*שעברה',
        r'השנה',
        r'החודש\s*שעבר',
        r'החודש',
        r'\d+\s*השנים\s*האחרונות',
        r'\d+\s*החודשים\s*האחרונים',
        r'בין\s*\d{4}\s*ל[-\s]*\d{4}',
        r'מ[-\s]*\d{4}\s*עד\s*\d{4}',
        r'ב[-\s]*\d{4}',
        r'בשנת\s*\d{4}',
        r'השבוע\s*שעבר',
        r'השבוע',
    ]
    
    # Add month patterns
    for month in HEBREW_MONTHS:
        patterns.append(rf'{month}\s*\d{{4}}')
    
    # Add relative day patterns
    for day in HEBREW_RELATIVE_TIME:
        patterns.append(rf'\b{day}\b')
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def validate_date_range(start: str, end: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that date range is logical.
    
    Args:
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        
        # Check if end is after start
        if end_date < start_date:
            return False, "תאריך סיום לפני תאריך התחלה"
        
        # Check if dates are not too far in the future
        today = get_current_date()
        if start_date > today + timedelta(days=365):
            return False, "תאריך בעתיד הרחוק מדי"
        
        # Check if dates are reasonable (not before 1948)
        if start_date.year < 1948:
            return False, "תאריך לפני הקמת המדינה"
        
        return True, None
        
    except ValueError as e:
        return False, f"פורמט תאריך לא תקין: {str(e)}"