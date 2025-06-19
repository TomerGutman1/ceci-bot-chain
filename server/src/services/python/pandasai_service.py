"""
CECI-AI PandasAI Service
Python API that uses PandasAI for intelligent querying of Israeli government decisions
"""

import os
import sys
import json
import re
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from datetime import datetime, timedelta
import uvicorn
import logging

# Import session management
from session_manager import get_session_manager, QueryContext
from query_optimizer import QueryOptimizer
from validation import ResponseValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Request/Response Models ----
class QueryRequest(BaseModel):
    query: str
    intent_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None  # Add session support

class QueryResponse(BaseModel):
    success: bool
    answer: Any
    query_type: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: Optional[str] = None  # Return session ID
    query_id: Optional[str] = None    # Return query ID for reference

class DataUploadRequest(BaseModel):
    data: List[Dict[str, Any]]  # List of decision objects
    source: Optional[str] = "external"  # Where the data came from

# ---- Supabase Client ----
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials in environment variables")
    
    # Create client without proxy parameter - supabase 2.3.5 doesn't support it
    return create_client(url, key)

# ---- Dummy data for testing ----
def load_dummy_data() -> pd.DataFrame:
    """Load dummy data for testing when Supabase fails"""
    logger.info("Loading dummy data for testing...")
    data = {
        'decision_number': ['1234', '5678', '9012'],
        'decision_title': ['החלטה בנושא חינוך', 'החלטה בנושא בריאות', 'החלטה בנושא תחבורה'],
        'decision_date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01']),
        'government_number': [37, 37, 37],
        'prime_minister': ['בנימין נתניהו', 'בנימין נתניהו', 'בנימין נתניהו'],
        'tags_policy_area': ['חינוך', 'בריאות', 'תחבורה'],
        'tags_government_body': ['משרד החינוך', 'משרד הבריאות', 'משרד התחבורה'],
        'tags_location': ['ירושלים', 'תל אביב', 'חיפה'],
        'summary': ['תקציר החלטה על חינוך', 'תקציר החלטה על בריאות', 'תקציר החלטה על תחבורה'],
        'decision_url': ['http://example.com/1234', 'http://example.com/5678', 'http://example.com/9012']
    }
    df = pd.DataFrame(data)
    df['year'] = df['decision_date'].dt.year
    df['month'] = df['decision_date'].dt.month
    return df

# ---- Load Data ----
def load_decisions_data() -> pd.DataFrame:
    """Load Israeli government decisions from Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Load ALL records using pagination
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = supabase.table("israeli_government_decisions").select("*").range(offset, offset + page_size - 1).execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            logger.info(f"Loaded {len(all_data)} records so far...")
            
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        if not all_data:
            logger.warning("No data found in israeli_government_decisions table")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        # Convert date columns
        if 'decision_date' in df.columns:
            df['decision_date'] = pd.to_datetime(df['decision_date'], errors='coerce')
        
        # Handle government_number conversion
        if 'government_number' in df.columns:
            df['government_number'] = pd.to_numeric(df['government_number'], errors='coerce')
            df['government_number'] = df['government_number'].round().astype('Int64')
        
        # Add helper columns
        if 'decision_date' in df.columns:
            df['year'] = df['decision_date'].dt.year
            df['month'] = df['decision_date'].dt.month
        
        logger.info(f"Loaded total of {len(df)} records from Supabase")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data from Supabase: {str(e)}")
        logger.warning("Falling back to dummy data for testing")
        return load_dummy_data()

# ---- Utility Functions ----
def extract_number_from_hebrew(text: str) -> Optional[int]:
    """Extract number from Hebrew text, handles both digits and Hebrew words"""
    
    # Dictionary for Hebrew numbers
    hebrew_numbers = {
        'אחת': 1, 'אחד': 1, 'ראשון': 1, 'ראשונה': 1,
        'שתיים': 2, 'שניים': 2, 'שני': 2, 'שנייה': 2, 'שתי': 2,
        'שלוש': 3, 'שלושה': 3, 'שלישי': 3, 'שלישית': 3,
        'ארבע': 4, 'ארבעה': 4, 'רביעי': 4, 'רביעית': 4,
        'חמש': 5, 'חמישה': 5, 'חמישי': 5, 'חמישית': 5,
        'שש': 6, 'שישה': 6, 'שישי': 6, 'שישית': 6,
        'שבע': 7, 'שבעה': 7, 'שביעי': 7, 'שביעית': 7,
        'שמונה': 8, 'שמיני': 8, 'שמינית': 8,
        'תשע': 9, 'תשעה': 9, 'תשיעי': 9, 'תשיעית': 9,
        'עשר': 10, 'עשרה': 10, 'עשירי': 10, 'עשירית': 10,
        'עשרים': 20, 'שלושים': 30, 'ארבעים': 40, 'חמישים': 50,
        'מאה': 100, 'אלף': 1000
    }
    
    # First try to find digit numbers
    digit_match = re.search(r'\b(\d+)\b', text)
    if digit_match:
        return int(digit_match.group(1))
    
    # Then try Hebrew numbers
    for hebrew, value in hebrew_numbers.items():
        if hebrew in text:
            return value
    
    return None

def detect_quantity_request(query: str) -> Optional[int]:
    """Detect if user is asking for a specific number of decisions"""
    # Patterns that indicate quantity request
    quantity_patterns = [
        r'(הבא לי|תן לי|הראה לי|הצג)\s+(\S+)\s+החלטות',  # הבא לי X החלטות
        r'(הבא|תן|הראה)\s+(\S+)\s+החלטות',  # הבא X החלטות
        r'(\S+)\s+החלטות\s+(האחרונות|ראשונות|משמעותיות)',  # X החלטות האחרונות
        r'החלטות\s+(\S+)\s+(האחרונות|ראשונות)',  # החלטות X האחרונות
        r'(רשימה של|רשימת)\s+(\S+)\s+החלטות',  # רשימה של X החלטות
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, query)
        if match:
            # Extract the number part from the match
            for group in match.groups():
                if group:
                    number = extract_number_from_hebrew(group)
                    if number:
                        return number
    
    # Also check for TOP N patterns
    top_patterns = [
        r'(טופ|TOP|top)\s+(\d+)',  # טופ 5, TOP 10
        r'(הראשונות|האחרונות)\s+(\S+)',  # הראשונות X
    ]
    
    for pattern in top_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            number_text = match.group(2) if len(match.groups()) > 1 else match.group(1)
            number = extract_number_from_hebrew(number_text)
            if number:
                return number
    
    return None

# ---- Custom Instructions ----
CUSTOM_INSTRUCTIONS_FULL = """
You are analyzing Israeli government decisions. Always respond in Hebrew.

CRITICAL RULES:
1. You MUST work with a SINGLE DataFrame called 'df' - there is NO 'dfs' list!
2. NEVER write code like 'for df in dfs' - this will fail!
3. The dataset contains 24,716 records in ONE dataframe called 'df'
4. To filter by year, use: df[df['year'] == 1999] NOT df['decision_date'].str.contains('1999')
5. decision_date is a datetime column, NOT a string - use df['year'] for year filtering

IMPORTANT: 
1. You are working with a SINGLE DataFrame called 'df', NOT a list of dataframes.
2. The dataset contains 24,716 records. Be EFFICIENT with your queries.
3. ALWAYS limit results: use .head(10) for exploratory queries
4. For year-based queries, ALWAYS filter by year column first: df[df['year'] == YYYY]
5. When searching topics, be specific: df[df['tags_policy_area'].str.contains('term', na=False)]
6. NEVER return more than 100 rows without aggregation

EFFICIENCY RULES:
- Filter early: Apply filters before any other operations
- Use indexes: decision_number, year, government_number are indexed
- Limit results: Always use .head() unless specifically asked for all
- For counts: Use .shape[0] or len() instead of returning all rows

CORRECT CODE EXAMPLES:
- Get 3 decisions: df.head(3)
- Get 3 decisions from 1999: df[df['year'] == 1999].head(3)
- Get education decisions: df[df['tags_policy_area'].str.contains('חינוך', na=False)]
- Combine filters: df[(df['year'] == 1999) & (df['tags_policy_area'].str.contains('חינוך', na=False))].head(3)
- Get full content safely: 
  row = df.iloc[0]
  content = row.get('decision_content', row.get('summary', 'אין תוכן זמין'))
  if pd.notna(content):
      result = {'type': 'string', 'value': content}
  else:
      result = {'type': 'string', 'value': 'לא נמצא תוכן'}

WRONG CODE (NEVER USE):
- for df in dfs: (NO dfs exists!)
- df['decision_date'].str.contains('1999') (decision_date is datetime, not string!)
- decisions_1999 = [df for df in dfs...] (NO list comprehension with dfs!)

QUERY HANDLING INSTRUCTIONS:

1. SINGLE DECISION REQUESTS ("הבא לי החלטה", "תן לי החלטה", "הראה החלטה"): 
   - ALWAYS return only ONE decision, not multiple
   - If multiple match criteria, return the most recent one

2. SPECIFIC DECISION BY NUMBER:
   - When asked for decision number X, filter by decision_number == 'X'
   - Example: "החלטה מספר 1234" → decision_number == '1234'

3. DATE FILTERS:
   - Single date: df[df['decision_date'] == '2022-01-01']
   - Year only: df[df['year'] == 2022]
   - Year from query "מ2005" or "משנת 2005": df[df['year'] == 2005]
   - For "החלטה בנושא X מ-YYYY": df[(df['tags_policy_area'].str.contains('X', na=False)) & (df['year'] == YYYY)]
   - Date range: df[df['decision_date'].between('2020-01-01', '2020-12-31')]
   - Month/day: df[(df['decision_date'].dt.month == 3) & (df['decision_date'].dt.day == 15)]

4. TOPIC/SUBJECT FILTERS:
   - Use tags_policy_area.str.contains('נושא', na=False)
   - For multiple keywords, use OR: contains('דיור') | contains('בנייה')

5. GOVERNMENT FILTERS:
   - Government number: government_number == 36
   - Handle variations: "ממשלה 36", "הממשלה ה-36", "ממשלה מספר 36"

6. MINISTRY/BODY FILTERS:
   - Use tags_government_body.str.contains('משרד', na=False)

7. COMBINED FILTERS:
   - Apply multiple conditions with & (AND) or | (OR)
   - Example: (year == 2023) & (tags_policy_area.str.contains('חינוך'))

8. STATISTICAL QUERIES:
   - "כמה": return count()
   - "איזה משרד הכי הרבה": groupby and count
   - "מגמה": groupby year and count

9. RANKING/TOP N:
   - "חמש החלטות משמעותיות": sort by relevance and take head(5)
   - "דרג": order by criteria and number results
   - When user asks for N decisions, ALWAYS use .head(N)
   - Hebrew numbers: אחת=1, שתיים/שניים=2, שלוש=3, ארבע=4, חמש=5, etc.

10. SPECIAL CASES:
   - Leap year Feb 29: (decision_date.dt.month == 2) & (decision_date.dt.day == 29)
   - Decision > 10000: decision_number.astype(int) > 10000
   - Unanimous decisions: check if exists a field for votes
   - Unapproved: operativity != 'אופרטיבית'

11. SUMMARY REQUESTS:
   - "סכם בקצרה": return only summary field
   - "תקציר של": focus on summary
   - ALWAYS check if fields are not None before accessing
   - If decision_content is None, use summary instead

12. MULTI-STEP QUERIES:
   - For "הצג קודם... ואז...": handle as two separate queries
   - Return results step by step

FORMATTING:
- For single decision: full details with all fields
- For multiple: list with number, title, date
- For statistics: clear numbers with context
- For empty results: "לא נמצאו החלטות בנושא X"

Format responses clearly in Hebrew.
"""

# Compact version of instructions to save tokens
CUSTOM_INSTRUCTIONS = """
You're analyzing Israeli government decisions. Respond in Hebrew.

CRITICAL: Work with ONE DataFrame 'df', NOT 'dfs'!

IMPORTANT - NO HALLUCINATION:
- ONLY return data that EXISTS in the dataframe
- If no results match the query, return empty DataFrame
- NEVER create fake decision numbers or content
- If df[condition] is empty, return the empty result

RESULT FORMAT - ALWAYS return result as dictionary:
- For text/content: result = {'type': 'string', 'value': 'the_content'}
- For dataframe: result = {'type': 'dataframe', 'value': df_result}
- For number: result = {'type': 'number', 'value': numeric_value}

KEY RULES:
1. Filter by year: df[df['year'] == YYYY]
2. Filter by topic: df[df['tags_policy_area'].str.contains('X', na=False)]
3. Limit results: always use .head(N)
4. For single decision: use .head(1)
5. Check None before accessing fields

COMMON PATTERNS:
- Decision by number: df[df['decision_number'] == 'X']
- Decisions from year: df[df['year'] == YYYY].head(N)
- Topic filter: df[df['tags_policy_area'].str.contains('topic', na=False)]
- Combined: df[(condition1) & (condition2)].head(N)
- Get content: 
  content = df.iloc[0]['decision_content']
  result = {'type': 'string', 'value': content if pd.notna(content) else 'לא נמצא תוכן'}

For counts: use .shape[0] or len()
For content: check decision_content is not None

Respond with formatted Hebrew text.
"""

# ---- Initialize PandasAI ----
def initialize_pandasai(df: pd.DataFrame) -> SmartDataframe:
    """Initialize PandasAI with OpenAI LLM"""
    try:
        # Get fresh config
        config = get_llm_config()
        
        # Configure PandasAI with optimized settings for large datasets
        sdf = SmartDataframe(df, config=config)
        
        logger.info("PandasAI initialized successfully with optimized settings")
        return sdf
        
    except Exception as e:
        logger.error(f"Failed to initialize PandasAI: {str(e)}")
        raise

# ---- Process Query ----
def process_pandas_query(sdf: SmartDataframe, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a natural language query using PandasAI with session support"""
    try:
        # Get session manager
        session_manager = get_session_manager()
        session = session_manager.get_or_create_session(session_id)
        
        # Resolve references in query
        logger.info(f"Original query: {query}")
        resolved_query, referenced_ids = session_manager.reference_resolver.resolve_references(query, session)
        
        # Use resolved query if references were found
        if referenced_ids:
            logger.info(f"References found: {referenced_ids}")
            logger.info(f"Resolved query: {resolved_query}")
            query = resolved_query
        else:
            logger.info("No references found in query")
        
        # Optimize the dataframe based on the query
        global df
        optimized_df, modified_query = query_optimizer.optimize_dataframe(df, query)
        
        # Create a new SmartDataframe with the optimized data
        # Use fresh config to avoid recursion
        optimized_sdf = SmartDataframe(
            optimized_df,
            config=get_llm_config()
        )
        
        logger.info(f"Optimized dataset from {len(df)} to {len(optimized_df)} rows")
        logger.info(f"Modified query: {modified_query}")
        
        # Use the modified query with the optimized dataframe
        query = modified_query
        # Check if this is a follow-up query
        follow_up_keywords = ['עכשיו', 'כעת', 'בנוסף', 'גם', 'עוד', 'אותו דבר', 'כאלה', 'כמו']
        is_follow_up = any(keyword in query for keyword in follow_up_keywords)
        
        if is_follow_up and 'משנת' in query:
            # Extract year for follow-up queries
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', query)
            if year_match:
                year = year_match.group(1)
                # For follow-up queries, emphasize using the same filters but different year
                query = f"{query} - השתמש באותו סינון רק שנה ל-df[df['year'] == {year}]"
        
        # Check if user is asking for multiple decisions with specific count
        requested_count = detect_quantity_request(query)
        
        # Check if user is asking for a single decision
        single_decision_keywords = ['הבא לי', 'תן לי', 'הראה לי', 'תביא לי', 'החלטה אחת', 'החלטה בנושא']
        is_single_decision_request = any(keyword in query for keyword in single_decision_keywords) and requested_count is None
        
        # If specific count requested, modify query to include .head(N)
        if requested_count and requested_count > 1:
            logger.info(f"Detected request for {requested_count} decisions")
            # Add instruction to limit results
            if 'האחרונות' in query:
                query += f" - קח את df.sort_values('decision_date', ascending=False).head({requested_count})"
            elif 'ראשונות' in query:
                query += f" - קח את df.sort_values('decision_date', ascending=True).head({requested_count})"
            else:
                query += f" - הגבל ל-{requested_count} תוצאות בלבד עם .head({requested_count})"
        
        # Check for "all decisions" request
        all_decisions_keywords = ['כל ההחלטות', 'את כל', 'הכל', 'כולן']
        wants_all = any(keyword in query for keyword in all_decisions_keywords)
        
        if wants_all and not requested_count:
            # Default to showing top 20 for "all" requests
            logger.info("זוהה בקשה ל'כל ההחלטות', מגביל ל-20")
            query += " - הראה רק את ה20 הראשונות עם .head(20), וציין שיש עוד"
        
        # Check if user wants full content of a specific decision
        full_content_patterns = [
            r'תוכן מלא של ההחלטה (הראשונה|השנייה|השלישית)',
            r'תוכן מלא של החלטה מספר (\d+)',
            r'הטקסט המלא של',
            r'תן לי את התוכן',
        ]
        
        wants_specific_content = False
        for pattern in full_content_patterns:
            if re.search(pattern, query):
                wants_specific_content = True
                break
        
        # If asking for "the decision you sent", help PandasAI understand
        if 'ששלחת' in query or 'שהצגת' in query:
            # Add instruction to get the most recent result
            query += " - אם אין תוצאות קודמות, קח את ההחלטה האחרונה ברשימה. ודא ש-decision_content לא None לפני הצגה"
        
        # Check if user wants full content
        full_content_keywords = ['תוכן מלא', 'תוכן ההחלטה', 'הטקסט המלא', 'ההחלטה המלאה', 'נוסח מלא']
        wants_full_content = any(keyword in query for keyword in full_content_keywords)
        
        # For single decision requests with year filter, help PandasAI by being more specific
        year_patterns = [r'מ(\d{4})', r'משנת (\d{4})', r'\b(19\d{2}|20\d{2})\b']
        
        year_match = None
        for pattern in year_patterns:
            match = re.search(pattern, query)
            if match:
                year_match = match
                break
                
        if is_single_decision_request and year_match:
            year = year_match.group(1)
            
            # Extract topic if exists
            topic_match = re.search(r'בנושא ([\u0590-\u05FF\s]+)(?:מ\d{4}|משנת)', query)
            
            if topic_match:
                topic = topic_match.group(1).strip()
                modified_query = f"הבא לי את df[(df['tags_policy_area'].str.contains('{topic}', na=False)) & (df['year'] == {year})].sort_values('decision_date', ascending=False).head(1)"
            else:
                modified_query = f"{query.split(year_match.group(0))[0].strip()} עם df[df['year'] == {year}].sort_values('decision_date', ascending=False).head(1)"
            
            logger.info(f"Modified query for year filter: {modified_query}")
            query = modified_query
        
        # Use PandasAI with the optimized dataframe
        logger.info(f"Processing query with PandasAI: {query}")
        try:
            response = optimized_sdf.chat(query)
        except Exception as pandas_error:
            # Check if it's a context length error
            error_str = str(pandas_error)
            if "context_length_exceeded" in error_str or "maximum context length" in error_str:
                logger.warning(f"Context length exceeded, attempting with smaller dataset")
                
                # Try with even smaller dataset
                if len(optimized_df) > 100:
                    super_optimized_df = optimized_df.head(100)
                else:
                    # Sample 50 random rows
                    super_optimized_df = optimized_df.sample(n=min(50, len(optimized_df)), random_state=42)
                
                # Create super optimized SmartDataframe
                super_config = get_llm_config()
                # Adjust for super-optimized settings
                super_config["max_retries"] = 1
                super_config["use_error_correction_framework"] = False
                super_config["max_rows_to_analyze"] = 50
                super_config["sample_rows"] = 3
                
                super_optimized_sdf = SmartDataframe(
                    super_optimized_df,
                    config=super_config
                )
                
                # Retry with super optimized dataset
                try:
                    response = super_optimized_sdf.chat(query + " (מוגבל למדגם קטן יותר עקב מגבלות טכניות)")
                    logger.info("Successfully processed with super-optimized dataset")
                except Exception as e:
                    logger.error(f"Failed even with super-optimized dataset: {e}")
                    # Return a helpful error message
                    return {
                        "type": "error",
                        "data": None,
                        "formatted": "מצטער, השאילתה מורכבת מדי. אנא נסה שאילתה ממוקדת יותר, למשל:\n" +
                                    "- הגבל לשנה ספציפית\n" +
                                    "- הגבל לנושא ספציפי\n" +
                                    "- בקש מספר קטן יותר של תוצאות",
                        "error": "context_length_exceeded"
                    }
            else:
                # Re-raise if it's not a context length error
                raise pandas_error
        
        # Validate response before processing
        if response_validator:
            validation_result = response_validator.validate_response(response, query)
            
            if not validation_result["is_valid"]:
                logger.warning(f"Invalid response detected: {validation_result['warnings']}")
                if validation_result["removed_items"]:
                    logger.warning(f"Removed invalid items: {validation_result['removed_items']}")
            
            # Use the cleaned response
            response = validation_result["cleaned_response"]
            
            # If response is empty after validation, return appropriate message
            if isinstance(response, pd.DataFrame) and response.empty:
                logger.warning("All results were invalid, returning empty result")
                return {
                    "type": "text",
                    "data": None,
                    "formatted": "😔 לא נמצאו החלטות תקפות התואמות לבקשה. ייתכן שהמערכת ניסתה להציג החלטות שאינן קיימות במסד הנתונים.",
                    "error": "invalid_results",
                    "validation_warnings": validation_result.get("warnings", [])
                }
        
        # Determine response type and prepare result
        result = None
        if isinstance(response, pd.DataFrame):
            
            # If it's a request for a single decision and we got multiple, take only the first
            if is_single_decision_request and len(response) > 1:
                logger.info(f"Limiting response to 1 decision (got {len(response)})")
                response = response.head(1)
            
            formatted = format_decision_response(response, is_single_decision_request, wants_full_content)
            result = {
                "type": "dataframe",
                "data": response.to_dict('records'),
                "formatted": formatted,
                "results_df": response  # Keep DataFrame for session
            }
        elif isinstance(response, (int, float)):
            result = {
                "type": "number",
                "data": response,
                "formatted": str(response),
                "results_df": None
            }
        else:
            result = {
                "type": "text",
                "data": response,
                "formatted": str(response),
                "results_df": None
            }
        
        # Add query to session (always, even for new sessions)
        query_context = session_manager.add_query_to_session(
            session_id=session.id,
            query=query,
            results=result.get("results_df"),
            response_type=result["type"],
            formatted_response=result["formatted"],
            metadata={
                "referenced_queries": referenced_ids,
                "single_decision_request": is_single_decision_request,
                "wants_full_content": wants_full_content
            }
        )
        result["query_id"] = query_context.query_id
        result["session_id"] = session.id
        
        # Remove the DataFrame from result before returning
        if "results_df" in result:
            del result["results_df"]
        
        return result
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise

def format_decision_response(df: pd.DataFrame, single_decision: bool, full_content: bool = False) -> str:
    """Format decision dataframe into Hebrew text"""
    if len(df) == 0:
        return "😔 לא נמצאו החלטות התואמות לבקשה"
    
    if single_decision or len(df) == 1:
        # Format single decision
        row = df.iloc[0]
        
        # Get decision number and title
        decision_num = row.get('decision_number', 'לא צוין')
        decision_title = row.get('decision_title', None)
        
        # Start with decision number in header
        response = f"🏛️ החלטת ממשלה מס' {decision_num}\n\n"
        
        # Title on second line if exists
        if decision_title and str(decision_title).strip() and str(decision_title).lower() != 'none':
            response += f"📋 {decision_title}\n\n"
        else:
            response += ""  # No extra line if no title
        
        # Decision details - clean format
        response += f"🔢 מספר החלטה: {row.get('decision_number', 'לא צוין')}\n"
        response += f"📅 תאריך: {format_date(row.get('decision_date', ''))}\n"
        # Handle government_number - it might be float or NaN
        gov_num = row.get('government_number', 'לא צוין')
        if pd.notna(gov_num) and isinstance(gov_num, (int, float)):
            gov_num = int(gov_num)
        response += f"🏢 ממשלה מספר: {gov_num}\n"
        
        if row.get('prime_minister'):
            response += f"👤 ראש הממשלה: {row.get('prime_minister')}\n"
        
        # Tags if available
        if row.get('tags_policy_area'):
            response += f"\n🏷️ תחומים: {row.get('tags_policy_area')}\n"
        
        # Government bodies if available
        if row.get('tags_government_body'):
            response += f"🏦 גופים מעורבים: {row.get('tags_government_body')}\n"
        
        # Content section
        response += "\n"
        
        if full_content and row.get('decision_content') and str(row.get('decision_content')).strip():
            # Show FULL content when requested
            response += "📜 תוכן ההחלטה המלא:\n\n"
            content = str(row.get('decision_content')).strip()
            response += f"{content}\n"
        elif row.get('summary') and str(row.get('summary')).strip():
            # Show summary by default
            response += "📝 תקציר:\n\n"
            summary = str(row.get('summary')).strip()
            # Limit summary length if not requesting full content
            if not full_content and len(summary) > 500:
                summary = summary[:497] + "..."
            response += f"{summary}\n"
        elif row.get('decision_content') and str(row.get('decision_content')).strip():
            # Show partial content if no summary
            response += "📄 מתוך ההחלטה:\n\n"
            content = str(row.get('decision_content')).strip()
            if len(content) > 500:
                content = content[:497] + "..."
            response += f"{content}\n"
            if not full_content and len(str(row.get('decision_content')).strip()) > 500:
                response += "\n💡 טיפ: לקריאת הטקסט המלא, כתוב 'תוכן מלא'\n"
        
        # Operativity status if available
        if row.get('operativity'):
            op_emoji = "✅" if row.get('operativity') == 'אופרטיבי' else "📋"
            response += f"\n{op_emoji} סטטוס: {row.get('operativity')}\n"
        
        # Link at the bottom
        if row.get('decision_url'):
            response += f"\n🔗 קישור להחלטה: {row.get('decision_url')}"
        
        return response
    else:
        # Format multiple decisions list with rich format
        response = f"📊 נמצאו {len(df)} החלטות רלוונטיות:\n\n"
        
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            # Get decision number and title
            decision_num = row.get('decision_number', 'לא צוין')
            decision_title = row.get('decision_title', 'ללא כותרת')
            
            # Format each decision like a mini version of single decision
            response += f"**{i}. החלטת ממשלה מס' {decision_num}**\n"
            
            # Title if exists
            if decision_title and str(decision_title).strip() and str(decision_title).lower() != 'none':
                response += f"📋 {decision_title}\n"
            
            # Date
            response += f"📅 תאריך: {format_date(row.get('decision_date', ''))}\n"
            
            # Government number if available
            gov_num = row.get('government_number', '')
            if pd.notna(gov_num) and isinstance(gov_num, (int, float)):
                response += f"🏢 ממשלה מספר: {int(gov_num)}\n"
            
            # Tags if available
            if row.get('tags_policy_area'):
                response += f"🏷️ תחומים: {row.get('tags_policy_area')}\n"
            
            # Short summary if available
            if row.get('summary') and str(row.get('summary')).strip():
                summary = str(row.get('summary')).strip()
                if len(summary) > 150:
                    summary = summary[:147] + "..."
                response += f"📝 תקציר: {summary}\n"
            
            # Link if available
            if row.get('decision_url'):
                response += f"🔗 קישור: {row.get('decision_url')}\n"
            
            response += "\n" + "─" * 50 + "\n\n"  # Separator line between decisions
        
        if len(df) > 10:
            response += f"\n... ועוד {len(df) - 10} החלטות נוספות\n"
        
        response += "\n💡 טיפ: לחץ על קישור או בקש החלטה ספציפית לפרטים מלאים"
        
        return response

def format_date(date_str):
    """Format date to Hebrew format"""
    if not date_str:
        return 'לא צוין'
    try:
        # Try to parse the date
        from datetime import datetime
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        
        # Hebrew month names
        hebrew_months = {
            1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
            5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
            9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
        }
        
        return f"{date_obj.day} ב{hebrew_months.get(date_obj.month, '')} {date_obj.year}"
    except:
        return str(date_str)

# Rest of the code remains the same...

# ---- FastAPI App ----
app = FastAPI(
    title="CECI-AI PandasAI Service",
    description="Intelligent querying of Israeli government decisions using PandasAI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
df: Optional[pd.DataFrame] = None
sdf: Optional[SmartDataframe] = None
current_government: int = 37
query_optimizer = QueryOptimizer()
response_validator: Optional[ResponseValidator] = None
llm_config = None  # Will be initialized on startup

# Function to get LLM config
def get_llm_config():
    """Get LLM configuration for PandasAI"""
    return {
        "llm": OpenAI(
            api_token=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo-16k",
            temperature=0.2
        ),
        "verbose": True,
        "enable_cache": False,  # Disabled to prevent stale responses
        "cache_db_path": "./cache/cache.db",
        "custom_whitelisted_dependencies": ["pandasai"],
        "middlewares": [],
        "custom_instructions": CUSTOM_INSTRUCTIONS,
        "max_retries": 2,
        "use_error_correction_framework": True,
        "enforce_privacy": False,
        "max_rows_to_analyze": 100,
        "sample_rows": 5,
        "use_advanced_reasoning_framework": False,
        "save_logs": False,
        "open_charts": False,
        "conversational": False
    }

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    global df, sdf, current_government, response_validator
    try:
        logger.info("Loading government decisions data...")
        df = load_decisions_data()
        
        if not df.empty:
            # Initialize Response Validator
            response_validator = ResponseValidator(df)
            logger.info("Response validator initialized")
            
            # Initialize PandasAI
            try:
                sdf = initialize_pandasai(df)
                logger.info("PandasAI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PandasAI: {e}")
                logger.error("Cannot run without PandasAI - please fix OpenAI API key!")
                raise Exception("PandasAI is required but failed to initialize")
            
            current_government = 37  # Default
            logger.info(f"Successfully loaded {len(df)} decisions. Current government: {current_government}")
        else:
            logger.error("No data loaded!")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "CECI-AI PandasAI Service",
        "status": "healthy" if df is not None else "not ready",
        "records": len(df) if df is not None else 0,
        "current_government": current_government
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a query using PandasAI"""
    try:
        if df is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        if sdf is None:
            # Fallback mode - improved search
            logger.info(f"Fallback mode: searching for '{request.query}'")
            
            # Search in multiple columns
            mask = (
                df['decision_title'].str.contains(request.query, case=False, na=False) |
                df['summary'].str.contains(request.query, case=False, na=False) |
                df['tags_policy_area'].str.contains(request.query, case=False, na=False) |
                df['decision_content'].str.contains(request.query, case=False, na=False)
            )
            
            results = df[mask].head(10)  # Limit to 10 results
            
            if len(results) > 0:
                # Format the results nicely
                formatted_results = []
                for _, row in results.iterrows():
                    formatted_results.append({
                        'decision_number': row.get('decision_number', 'לא ידוע'),
                        'title': row.get('decision_title', 'ללא כותרת'),
                        'date': str(row.get('decision_date', 'לא ידוע')),
                        'summary': row.get('summary', 'אין תקציר'),
                        'url': row.get('decision_url', '')
                    })
                
                answer = f"נמצאו {len(results)} החלטות בנושא '{request.query}':\n\n"
                for i, res in enumerate(formatted_results[:5], 1):  # Show top 5
                    answer += f"{i}. החלטה מס' {res['decision_number']}\n"
                    answer += f"   כותרת: {res['title']}\n"
                    answer += f"   תאריך: {res['date']}\n"
                    if res['summary'] and res['summary'] != 'אין תקציר':
                        answer += f"   תקציר: {res['summary'][:200]}...\n"
                    answer += "\n"
                
                if len(results) > 5:
                    answer += f"\n(ועוד {len(results) - 5} תוצאות נוספות)"
            else:
                answer = f"לא נמצאו החלטות התואמות לחיפוש '{request.query}'"
            
            return QueryResponse(
                success=True,
                answer=answer,
                query_type="search",
                metadata={
                    "status": "fallback_mode",
                    "count": len(results),
                    "results": formatted_results if len(results) > 0 else None
                }
            )
        
        # Use PandasAI to process the query with session support
        logger.info(f"Processing query with PandasAI: {request.query}")
        result = process_pandas_query(sdf, request.query, request.session_id)
        
        return QueryResponse(
            success=True,
            answer=result["formatted"],
            query_type=result["type"],
            metadata={
                "status": "pandasai_mode",
                "data_type": result["type"],
                "raw_data": result.get("data") if result["type"] != "text" else None
            },
            session_id=result.get("session_id"),
            query_id=result.get("query_id")
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        return QueryResponse(
            success=False,
            answer=None,
            query_type="error",
            error=str(e)
        )

@app.get("/stats")
async def get_statistics():
    """Get basic statistics about the data"""
    if df is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {
        "total_decisions": len(df),
        "status": "running_with_dummy_data"
    }

@app.post("/upload-data")
async def upload_data(request: DataUploadRequest):
    """Upload external data to use instead of loading from Supabase"""
    global df, sdf, response_validator
    try:
        logger.info(f"Received {len(request.data)} decisions from {request.source}")
        
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Process dates and numbers like in load_decisions_data
        if 'decision_date' in df.columns:
            df['decision_date'] = pd.to_datetime(df['decision_date'], errors='coerce')
        
        if 'government_number' in df.columns:
            df['government_number'] = pd.to_numeric(df['government_number'], errors='coerce')
            df['government_number'] = df['government_number'].round().astype('Int64')
        
        # Add helper columns
        if 'decision_date' in df.columns:
            df['year'] = df['decision_date'].dt.year
            df['month'] = df['decision_date'].dt.month
        
        # Re-initialize Response Validator with new data
        response_validator = ResponseValidator(df)
        logger.info("Response validator re-initialized with new data")
        
        # Re-initialize PandasAI with new data
        sdf = initialize_pandasai(df)
        
        logger.info(f"Successfully loaded {len(df)} decisions from external source")
        
        return {
            "success": True,
            "records_loaded": len(df),
            "source": request.source,
            "message": "Data loaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/data-status")
async def get_data_status():
    """Get current data status"""
    return {
        "data_loaded": df is not None,
        "records": len(df) if df is not None else 0,
        "pandasai_ready": sdf is not None,
        "columns": list(df.columns) if df is not None else []
    }

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "state": session.state.value,
        "query_count": len(session.query_chain),
        "recent_queries": [
            {
                "query_id": q.query_id,
                "timestamp": q.timestamp.isoformat(),
                "original_query": q.original_query,
                "response_type": q.response_type,
                "has_results": q.results is not None
            }
            for q in session.get_recent_queries(5)
        ]
    }

@app.get("/sessions/stats")
async def get_sessions_statistics():
    """Get statistics about all sessions"""
    session_manager = get_session_manager()
    return session_manager.get_session_stats()

@app.get("/redis/status")
async def get_redis_status():
    """Get Redis connection status"""
    session_manager = get_session_manager()
    
    redis_info = {
        "redis_url_configured": bool(os.getenv("REDIS_URL")),
        "redis_connected": False,
        "redis_url": "Not configured",
        "storage_backend": "memory"
    }
    
    if session_manager.redis_store:
        redis_info["redis_connected"] = session_manager.redis_store.is_connected()
        redis_info["redis_url"] = session_manager.redis_store._safe_redis_url()
        if redis_info["redis_connected"]:
            redis_info["storage_backend"] = "redis"
            redis_info["redis_stats"] = session_manager.redis_store.get_session_stats()
    
    return redis_info

@app.post("/sessions/cleanup")
async def cleanup_expired_sessions():
    """Manually trigger cleanup of expired sessions"""
    session_manager = get_session_manager()
    removed_count = session_manager.cleanup_expired_sessions()
    
    return {
        "success": True,
        "removed_sessions": removed_count,
        "message": f"Removed {removed_count} expired sessions"
    }

@app.get("/decision/{decision_number}")
async def get_decision_by_number(decision_number: str):
    """Get a specific decision by its number (for debugging)"""
    if df is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Search for the decision
    decision_df = df[df['decision_number'] == decision_number]
    
    if decision_df.empty:
        # Try to find similar decision numbers
        similar = []
        try:
            decision_num_int = int(decision_number)
            similar_df = df[
                (df['decision_number'].astype(str).str.match(f"^{decision_number[:2]}")) |
                (df['decision_number'].astype(int).between(decision_num_int - 10, decision_num_int + 10))
            ].head(5)
            
            if not similar_df.empty:
                similar = similar_df['decision_number'].tolist()
        except:
            pass
        
        return {
            "found": False,
            "decision_number": decision_number,
            "message": f"Decision {decision_number} not found in database",
            "similar_decisions": similar,
            "total_decisions": len(df)
        }
    
    # Return the decision details
    decision = decision_df.iloc[0]
    return {
        "found": True,
        "decision_number": decision_number,
        "data": {
            "title": decision.get('decision_title'),
            "date": str(decision.get('decision_date')),
            "government_number": int(decision.get('government_number')) if pd.notna(decision.get('government_number')) else None,
            "prime_minister": decision.get('prime_minister'),
            "tags_policy_area": decision.get('tags_policy_area'),
            "tags_government_body": decision.get('tags_government_body'),
            "summary": decision.get('summary'),
            "has_content": bool(decision.get('decision_content') and str(decision.get('decision_content')).strip()),
            "url": decision.get('decision_url')
        }
    }

@app.get("/validate-decision/{decision_number}")
async def validate_decision_exists(decision_number: str):
    """Quick check if a decision exists (for validation)"""
    if df is None or response_validator is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    exists = decision_number in response_validator.valid_decision_numbers
    
    return {
        "decision_number": decision_number,
        "exists": exists,
        "total_valid_decisions": len(response_validator.valid_decision_numbers)
    }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
