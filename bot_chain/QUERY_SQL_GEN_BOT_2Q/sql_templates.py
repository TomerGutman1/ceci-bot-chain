"""
SQL query templates for government decisions database.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class SQLTemplate:
    """SQL template with parameters and validation."""
    name: str
    description: str
    sql: str
    required_params: List[str]
    optional_params: List[str]
    example_params: Dict[str, Any]
    intent_match: List[str]  # Which intents this template supports


# SQL Templates for different query patterns
SQL_TEMPLATES = {
    "search_by_government_and_topic": SQLTemplate(
        name="search_by_government_and_topic",
        description="Search decisions by government number and topic",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE government_number = %(government_number)s
        AND %(topic)s = ANY(topics)
        ORDER BY decision_date DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["government_number", "topic"],
        optional_params=["limit"],
        example_params={
            "government_number": 37,
            "topic": "חינוך",
            "limit": 20
        },
        intent_match=["search"]
    ),
    
    "search_by_topic_only": SQLTemplate(
        name="search_by_topic_only",
        description="Search decisions by topic across all governments",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, 
            CASE 
                WHEN LENGTH(summary) > 500 THEN SUBSTRING(summary, 1, 497) || '...'
                ELSE summary
            END as summary,
            topics, ministries
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic"],
        optional_params=["limit"],
        example_params={
            "topic": "ביטחון",
            "limit": 10
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "specific_decision": SQLTemplate(
        name="specific_decision",
        description="Get a specific decision by government and decision number",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, content, summary, topics, ministries, decision_type
        FROM government_decisions 
        WHERE government_number = %(government_number)s
        AND decision_number = %(decision_number)s;
        """,
        required_params=["government_number", "decision_number"],
        optional_params=[],
        example_params={
            "government_number": 37,
            "decision_number": 660
        },
        intent_match=["specific_decision", "search"]
    ),
    
    "decision_by_number_only": SQLTemplate(
        name="decision_by_number_only",
        description="Search for a decision by number across all governments",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, content, summary, topics, ministries, decision_type
        FROM government_decisions 
        WHERE decision_number = %(decision_number)s
        ORDER BY government_number DESC;
        """,
        required_params=["decision_number"],
        optional_params=[],
        example_params={
            "decision_number": 2700
        },
        intent_match=["search"]
    ),
    
    "count_decisions_by_government": SQLTemplate(
        name="count_decisions_by_government",
        description="Count total decisions by government",
        sql="""
        SELECT 
            %(government_number)s as government_number,
            COUNT(*) as count
        FROM government_decisions 
        WHERE government_number = %(government_number)s;
        """,
        required_params=["government_number"],
        optional_params=[],
        example_params={
            "government_number": 37
        },
        intent_match=["count"]
    ),
    
    "count_decisions_by_topic": SQLTemplate(
        name="count_decisions_by_topic",
        description="Count decisions by topic and optionally government",
        sql="""
        SELECT 
            government_number,
            %(topic)s as topic,
            COUNT(*) as decision_count
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        {government_filter}
        GROUP BY government_number
        ORDER BY government_number DESC;
        """,
        required_params=["topic"],
        optional_params=["government_number"],
        example_params={
            "topic": "חינוך",
            "government_number": 37
        },
        intent_match=["count"]
    ),
    
    "count_by_topic_and_year": SQLTemplate(
        name="count_by_topic_and_year",
        description="Count decisions by topic and year",
        sql="""
        SELECT 
            COUNT(*) as count
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        AND EXTRACT(YEAR FROM decision_date) = %(year)s;
        """,
        required_params=["topic", "year"],
        optional_params=[],
        example_params={
            "topic": "חינוך",
            "year": 2023
        },
        intent_match=["count"]
    ),
    
    "count_by_topic_date_range": SQLTemplate(
        name="count_by_topic_date_range",
        description="Count decisions by topic within a date range",
        sql="""
        SELECT 
            COUNT(*) as count
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        AND decision_date >= %(start_date)s
        AND decision_date <= %(end_date)s;
        """,
        required_params=["topic", "start_date", "end_date"],
        optional_params=[],
        example_params={
            "topic": "בריאות",
            "start_date": "2010-01-01",
            "end_date": "2020-12-31"
        },
        intent_match=["count"]
    ),
    
    "count_by_year": SQLTemplate(
        name="count_by_year",
        description="Count all decisions in a specific year",
        sql="""
        SELECT 
            %(year)s as year,
            COUNT(*) as count
        FROM government_decisions 
        WHERE EXTRACT(YEAR FROM decision_date) = %(year)s;
        """,
        required_params=["year"],
        optional_params=[],
        example_params={
            "year": 2023
        },
        intent_match=["count"]
    ),
    
    "count_operational_by_topic": SQLTemplate(
        name="count_operational_by_topic",
        description="Count operational decisions by topic",
        sql="""
        SELECT 
            %(topic)s as topic,
            'אופרטיבית' as decision_type,
            COUNT(*) as count
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        AND decision_type = 'אופרטיבית';
        """,
        required_params=["topic"],
        optional_params=[],
        example_params={
            "topic": "חינוך"
        },
        intent_match=["count"]
    ),
    
    "search_by_date_range": SQLTemplate(
        name="search_by_date_range",
        description="Search decisions within a date range",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE decision_date >= %(start_date)s
        AND decision_date <= %(end_date)s
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["start_date", "end_date"],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "topic": "ביטחון",
            "limit": 30
        },
        intent_match=["search"]
    ),
    
    "search_by_ministry": SQLTemplate(
        name="search_by_ministry",
        description="Search decisions by ministry involvement",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE %(ministry)s = ANY(ministries)
        {government_filter}
        {topic_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["ministry"],
        optional_params=["government_number", "topic", "limit"],
        example_params={
            "ministry": "משרד החינוך",
            "government_number": 37,
            "limit": 25
        },
        intent_match=["search"]
    ),
    
    "full_text_search": SQLTemplate(
        name="full_text_search",
        description="Full-text search in decision content",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            ts_rank(to_tsvector('hebrew', content), to_tsquery('hebrew', %(search_term)s)) as relevance_score
        FROM government_decisions 
        WHERE to_tsvector('hebrew', content) @@ to_tsquery('hebrew', %(search_term)s)
        {government_filter}
        ORDER BY relevance_score DESC, decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=["search_term"],
        optional_params=["government_number", "limit"],
        example_params={
            "search_term": "חינוך & תקציב",
            "government_number": 37,
            "limit": 20
        },
        intent_match=["search"]
    ),
    
    "compare_governments": SQLTemplate(
        name="compare_governments",
        description="Compare decision counts between governments",
        sql="""
        SELECT 
            government_number,
            COUNT(*) as total_decisions,
            COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) as topic_decisions,
            ROUND(
                100.0 * COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) / COUNT(*), 
                2
            ) as topic_percentage
        FROM government_decisions 
        WHERE government_number IN %(government_list)s
        GROUP BY government_number
        ORDER BY government_number;
        """,
        required_params=["government_list", "topic"],
        optional_params=[],
        example_params={
            "government_list": [35, 36, 37],
            "topic": "ביטחון"
        },
        intent_match=["comparison"]
    ),
    
    "compare_governments_detailed": SQLTemplate(
        name="compare_governments_detailed",
        description="Compare specific decisions between governments on a topic",
        sql="""
        WITH gov_decisions AS (
            SELECT 
                government_number,
                decision_number,
                decision_date,
                title,
                summary,
                topics,
                ministries,
                decision_url,
                decision_type
            FROM government_decisions 
            WHERE government_number IN %(government_list)s
            AND %(topic)s = ANY(topics)
        )
        SELECT 
            government_number,
            json_agg(json_build_object(
                'decision_number', decision_number,
                'decision_date', decision_date,
                'title', title,
                'summary', summary,
                'topics', topics,
                'ministries', ministries,
                'decision_url', decision_url,
                'decision_type', decision_type
            ) ORDER BY decision_date DESC) as decisions,
            COUNT(*) as decision_count
        FROM gov_decisions
        GROUP BY government_number
        ORDER BY government_number;
        """,
        required_params=["government_list", "topic"],
        optional_params=[],
        example_params={
            "government_list": [35, 36],
            "topic": "דיור"
        },
        intent_match=["comparison", "DATA_QUERY"]
    ),
    
    "compare_policy_between_governments": SQLTemplate(
        name="compare_policy_between_governments",
        description="Compare policy decisions between two governments with details",
        sql="""
        SELECT 
            government_number,
            decision_number,
            decision_date,
            title,
            summary,
            topics,
            ministries,
            decision_url,
            CASE 
                WHEN government_number = %(gov1)s THEN 'ממשלה ' || %(gov1)s::text
                WHEN government_number = %(gov2)s THEN 'ממשלה ' || %(gov2)s::text
            END as government_label
        FROM government_decisions 
        WHERE government_number IN (%(gov1)s, %(gov2)s)
        AND %(topic)s = ANY(topics)
        ORDER BY government_number, decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=["gov1", "gov2", "topic"],
        optional_params=["limit"],
        example_params={
            "gov1": 35,
            "gov2": 36,
            "topic": "דיור",
            "limit": 20
        },
        intent_match=["comparison", "DATA_QUERY"]
    ),
    
    "recent_decisions": SQLTemplate(
        name="recent_decisions",
        description="Get most recent decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE 1=1
        AND decision_date IS NOT NULL
        AND decision_date >= '1990-01-01'
        {government_filter}
        {topic_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["government_number", "topic", "limit"],
        example_params={
            "limit": 10,
            "government_number": 37
        },
        intent_match=["search"]
    ),
    
    "search_by_year_and_topic": SQLTemplate(
        name="search_by_year_and_topic",
        description="Search decisions by year and topic, automatically finding relevant governments",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE EXTRACT(YEAR FROM decision_date) = %(year)s
        {topic_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["year"],
        optional_params=["topic", "limit"],
        example_params={
            "year": 2024,
            "topic": "חינוך",
            "limit": 20
        },
        intent_match=["search"]
    ),
    
    "trend_analysis": SQLTemplate(
        name="trend_analysis",
        description="Analyze trends in government decisions over multiple years",
        sql="""
        SELECT 
            EXTRACT(YEAR FROM decision_date) as year,
            government_number,
            COUNT(*) as decision_count,
            COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) as topic_count,
            ROUND(
                100.0 * COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) / COUNT(*),
                2
            ) as topic_percentage,
            STRING_AGG(DISTINCT 
                CASE WHEN %(topic)s = ANY(topics) THEN title END, 
                ' | ' ORDER BY decision_date DESC
            ) as sample_titles
        FROM government_decisions 
        WHERE decision_date >= %(start_date)s
        AND decision_date <= %(end_date)s
        {topic_filter}
        GROUP BY EXTRACT(YEAR FROM decision_date), government_number
        ORDER BY year DESC, government_number DESC;
        """,
        required_params=["topic"],
        optional_params=["start_date", "end_date", "limit"],
        example_params={
            "topic": "דיור",
            "start_date": "2020-01-01",
            "end_date": "2025-12-31",
            "limit": 50
        },
        intent_match=["search", "analysis"]
    ),
    
    "deep_analysis": SQLTemplate(
        name="deep_analysis",
        description="Deep analysis of decisions with obstacles and enablers identification",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, content, topics, ministries,
            CASE 
                WHEN content ILIKE '%חסם%' OR content ILIKE '%מניעה%' OR content ILIKE '%קושי%' 
                THEN 'מכיל חסמים אפשריים'
                ELSE 'ללא חסמים מזוהים'
            END as obstacle_indicators,
            CASE 
                WHEN content ILIKE '%מאפשר%' OR content ILIKE '%תמיכה%' OR content ILIKE '%עידוד%'
                THEN 'מכיל מאפשרים אפשריים'
                ELSE 'ללא מאפשרים מזוהים'
            END as enabler_indicators,
            LENGTH(content) as content_length
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        {government_filter}
        {date_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic"],
        optional_params=["government_number", "start_date", "end_date", "limit"],
        example_params={
            "topic": "תחבורה ציבורית",
            "limit": 20
        },
        intent_match=["analysis", "EVAL"]
    ),
    
    "historical_comparison": SQLTemplate(
        name="historical_comparison",
        description="Compare decisions between different time periods",
        sql="""
        WITH period_stats AS (
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM decision_date) BETWEEN %(start_year)s AND %(start_year)s + 1
                    THEN 'תקופה ראשונה'
                    WHEN EXTRACT(YEAR FROM decision_date) BETWEEN %(end_year)s - 1 AND %(end_year)s
                    THEN 'תקופה שנייה'
                END as period,
                COUNT(*) as total_decisions,
                COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) as topic_decisions,
                STRING_AGG(DISTINCT government_number::text, ', ') as governments,
                AVG(LENGTH(content)) as avg_content_length
            FROM government_decisions 
            WHERE (
                EXTRACT(YEAR FROM decision_date) BETWEEN %(start_year)s AND %(start_year)s + 1 OR
                EXTRACT(YEAR FROM decision_date) BETWEEN %(end_year)s - 1 AND %(end_year)s
            )
            {topic_filter}
            GROUP BY CASE 
                WHEN EXTRACT(YEAR FROM decision_date) BETWEEN %(start_year)s AND %(start_year)s + 1
                THEN 'תקופה ראשונה'
                WHEN EXTRACT(YEAR FROM decision_date) BETWEEN %(end_year)s - 1 AND %(end_year)s
                THEN 'תקופה שנייה'
            END
        )
        SELECT * FROM period_stats
        ORDER BY period;
        """,
        required_params=["start_year", "end_year", "topic"],
        optional_params=["limit"],
        example_params={
            "start_year": 2020,
            "end_year": 2024,
            "topic": "בריאות"
        },
        intent_match=["comparison", "analysis"]
    ),
    
    "ministry_breakdown": SQLTemplate(
        name="ministry_breakdown",
        description="Breakdown of decisions by ministry for specific topics",
        sql="""
        SELECT 
            unnest(ministries) as ministry,
            COUNT(*) as decision_count,
            COUNT(DISTINCT government_number) as government_span,
            MIN(decision_date) as earliest_decision,
            MAX(decision_date) as latest_decision,
            STRING_AGG(DISTINCT 
                CASE WHEN char_length(title) > 100 
                THEN substring(title, 1, 97) || '...'
                ELSE title END, 
                ' | ' ORDER BY decision_date DESC
            ) as sample_titles
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        {government_filter}
        {date_filter}
        GROUP BY unnest(ministries)
        HAVING COUNT(*) >= %(min_count)s
        ORDER BY decision_count DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic"],
        optional_params=["government_number", "start_date", "end_date", "min_count", "limit"],
        example_params={
            "topic": "חינוך",
            "min_count": 1,
            "limit": 15
        },
        intent_match=["search", "analysis"]
    ),
    
    "recommendations_analysis": SQLTemplate(
        name="recommendations_analysis", 
        description="Analyze successful decisions to generate operational recommendations",
        sql="""
        WITH successful_patterns AS (
            SELECT 
                id, government_number, decision_number, decision_date,
                title, summary, topics, ministries,
                CASE 
                    WHEN content ILIKE '%הצלחה%' OR content ILIKE '%יעיל%' OR content ILIKE '%חיובי%'
                    THEN 'הצלחה מזוהה'
                    WHEN content ILIKE '%יישום%' AND content ILIKE '%מלא%'
                    THEN 'יישום מלא'
                    WHEN content ILIKE '%תוצאות%' AND content ILIKE '%טוב%'
                    THEN 'תוצאות חיוביות'
                    ELSE 'רגיל'
                END as success_indicator,
                LENGTH(content) as detail_level
            FROM government_decisions 
            WHERE %(topic)s = ANY(topics)
            {government_filter}
            ORDER BY decision_date DESC
        )
        SELECT 
            government_number,
            COUNT(*) as total_decisions,
            COUNT(CASE WHEN success_indicator != 'רגיל' THEN 1 END) as successful_decisions,
            STRING_AGG(DISTINCT unnest(ministries), ', ') as involved_ministries,
            STRING_AGG(DISTINCT 
                CASE WHEN success_indicator != 'רגיל' THEN title END,
                ' | '
            ) as successful_examples
        FROM successful_patterns
        GROUP BY government_number
        ORDER BY successful_decisions DESC, government_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic"],
        optional_params=["government_number", "limit"],
        example_params={
            "topic": "איכות הסביבה",
            "limit": 10
        },
        intent_match=["analysis", "search"]
    ),
    
    "topic_summary": SQLTemplate(
        name="topic_summary",
        description="Summarize decisions by topic across governments",
        sql="""
        SELECT 
            unnest(topics) as topic,
            COUNT(*) as decision_count,
            COUNT(DISTINCT government_number) as government_count,
            MIN(decision_date) as first_decision,
            MAX(decision_date) as last_decision
        FROM government_decisions 
        WHERE 1=1
        {government_filter}
        GROUP BY unnest(topics)
        HAVING COUNT(*) >= %(min_count)s
        ORDER BY decision_count DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["government_number", "min_count", "limit"],
        example_params={
            "min_count": 5,
            "limit": 20
        },
        intent_match=["search", "count"]
    ),
    
    "joint_ministries_decisions": SQLTemplate(
        name="joint_ministries_decisions",
        description="Find decisions involving ALL specified ministries",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE ministries @> %(ministry_list)s::text[]
        {government_filter}
        {date_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["ministry_list"],
        optional_params=["government_number", "start_date", "end_date", "limit"],
        example_params={
            "ministry_list": ["משרד הבריאות", "משרד האוצר"],
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "decisions_by_multiple_topics": SQLTemplate(
        name="decisions_by_multiple_topics",
        description="Find decisions covering multiple topics",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            array_length(topics, 1) as topic_count
        FROM government_decisions 
        WHERE topics && %(topic_list)s::text[]
        {government_filter}
        ORDER BY array_length(topics && %(topic_list)s::text[], 1) DESC, decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic_list"],
        optional_params=["government_number", "limit"],
        example_params={
            "topic_list": ["חינוך", "תקציב"],
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "budget_decisions": SQLTemplate(
        name="budget_decisions",
        description="Find decisions with budget implications",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            CASE 
                WHEN content ~* 'מיליון|מיליארד|תקציב|הקצאה|מימון' THEN true
                ELSE false
            END as has_budget_mention
        FROM government_decisions 
        WHERE content ~* 'ש"ח|₪|מיליון|מיליארד|תקציב'
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "topic": "חינוך",
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "urgent_decisions": SQLTemplate(
        name="urgent_decisions",
        description="Find urgent or immediate decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE (title ~* 'דחוף|מיידי|חירום' OR content ~* 'דחוף|מיידי|חירום|בהול')
        {topic_filter}
        {government_filter}
        {date_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["topic", "government_number", "start_date", "end_date", "limit"],
        example_params={
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "canceled_decisions": SQLTemplate(
        name="canceled_decisions",
        description="Find canceled or revoked decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            decision_type
        FROM government_decisions 
        WHERE decision_type = 'בוטלה' OR title ~* 'ביטול|בטל'
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "committee_decisions": SQLTemplate(
        name="committee_decisions",
        description="Find decisions by specific committee",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            goverment_secretary_name as committee
        FROM government_decisions 
        WHERE goverment_secretary_name ILIKE '%' || %(committee_name)s || '%'
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=["committee_name"],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "committee_name": "ועדת שרים",
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "implementation_decisions": SQLTemplate(
        name="implementation_decisions",
        description="Find decisions about implementing previous decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE (title ~* 'יישום|ביצוע|הוצאה לפועל' OR content ~* 'ליישום החלטה|לביצוע החלטה')
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
    "extension_decisions": SQLTemplate(
        name="extension_decisions", 
        description="Find decisions extending or updating previous decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE title ~* 'הארכ|עדכון|תיקון החלטה|שינוי'
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "limit": 20
        },
        intent_match=["search", "DATA_QUERY"]
    ),
    
}


def extract_year_from_entities(entities: Dict[str, Any]) -> Optional[int]:
    """Extract year from entities - from date_range or topic text."""
    # DO NOT extract year from date_range if it has both start and end
    # This is to prevent date range queries from being converted to year queries
    if entities.get("date_range"):
        date_range = entities["date_range"]
        if isinstance(date_range, dict) and date_range.get("start") and date_range.get("end"):
            # If we have a full date range, don't extract year
            return None
        elif isinstance(date_range, dict) and date_range.get("start"):
            try:
                # Extract year from start date only if no end date (format: "2024-01-01")
                year_str = str(date_range["start"]).split("-")[0]
                return int(year_str)
            except (ValueError, IndexError):
                pass
    
    # Check topic text for year patterns like "מ2024", "ב-2024", "2024"
    topic = entities.get("topic", "")
    if topic:
        # Look for 4-digit years in topic
        year_match = re.search(r'\b(20\d{2})\b', topic)
        if year_match:
            year = int(year_match.group(1))
            # Clean the topic by removing the year pattern
            cleaned_topic = re.sub(r'\s*מ(20\d{2})\s*', ' ', topic)
            cleaned_topic = re.sub(r'\s*ב[-\s]?(20\d{2})\s*', ' ', cleaned_topic)
            cleaned_topic = re.sub(r'\s*(20\d{2})\s*', ' ', cleaned_topic)
            entities["topic"] = cleaned_topic.strip()
            return year
        
        # Look for Hebrew year patterns like "מ2024", "ב2024"
        year_match = re.search(r'מ(20\d{2})|ב[-\s]?(20\d{2})', topic)
        if year_match:
            year = int(year_match.group(1) or year_match.group(2))
            # Clean the topic by removing the year pattern
            cleaned_topic = re.sub(r'\s*מ(20\d{2})\s*', ' ', topic)
            cleaned_topic = re.sub(r'\s*ב[-\s]?(20\d{2})\s*', ' ', cleaned_topic)
            entities["topic"] = cleaned_topic.strip()
            return year
    
    return None


def extract_comparison_years(text: str) -> Optional[tuple]:
    """Extract two years for comparison from text like 'בין 2020 ל-2024'."""
    # Look for patterns like "בין 2020 ל-2024", "מ-2020 עד 2024"
    year_pattern = r'בין\s*(20\d{2})\s*ל?[-\s]*(20\d{2})|מ[-\s]*(20\d{2})\s*עד\s*(20\d{2})'
    match = re.search(year_pattern, text)
    if match:
        year1 = match.group(1) or match.group(3)
        year2 = match.group(2) or match.group(4)
        if year1 and year2:
            return (int(year1), int(year2))
    return None


def get_template_by_intent(intent: str, entities: Dict[str, Any]) -> Optional[SQLTemplate]:
    """Select the best template based on intent and available entities."""
    
    # For EVAL or ANALYSIS intent - always look for specific decision
    if intent == "EVAL" or intent == "ANALYSIS":
        if entities.get("decision_number"):
            # For EVAL/ANALYSIS, we need a specific decision
            if not entities.get("government_number"):
                entities["government_number"] = 37
            return SQL_TEMPLATES["specific_decision"]
        # If no decision number, can't do evaluation - fall through to search
    
    # For specific decisions - check both intent and operation
    if (intent == "specific_decision" or entities.get("operation") == "specific_decision"):
        if entities.get("government_number") and entities.get("decision_number"):
            return SQL_TEMPLATES["specific_decision"]
        elif entities.get("decision_number") and not entities.get("government_number"):
            # Default to current government (37) when only decision number specified
            entities["government_number"] = 37
            return SQL_TEMPLATES["specific_decision"]
    
    # For count queries - check intent, operation, or count_only flag
    if intent == "count" or entities.get("operation") == "count" or entities.get("count_only"):
        # Extract year from entities if present
        year = extract_year_from_entities(entities)
        
        # Count by topic and year
        if entities.get("topic") and year:
            entities["year"] = year
            return SQL_TEMPLATES["count_by_topic_and_year"]
        
        # Count by topic and date range
        elif entities.get("topic") and entities.get("date_range"):
            date_range = entities["date_range"]
            if date_range.get("start") and date_range.get("end"):
                entities["start_date"] = date_range["start"]
                entities["end_date"] = date_range["end"]
                return SQL_TEMPLATES["count_by_topic_date_range"]
        
        # Count by year only
        elif year and not entities.get("topic"):
            entities["year"] = year
            return SQL_TEMPLATES["count_by_year"]
        
        # Count operational decisions by topic
        elif entities.get("topic") and entities.get("decision_type") == "אופרטיבית":
            return SQL_TEMPLATES["count_operational_by_topic"]
        
        # Count by government only
        elif entities.get("government_number") and not entities.get("topic"):
            return SQL_TEMPLATES["count_decisions_by_government"]
        
        # Count by topic only
        elif entities.get("topic"):
            return SQL_TEMPLATES["count_decisions_by_topic"]
    
    # For search queries (handle "search", "QUERY", and "DATA_QUERY" intents)
    if intent == "search" or intent == "QUERY" or intent == "DATA_QUERY":
        print(f"DEBUG: Entered DATA_QUERY block with entities: {entities}")
        # Check if this is actually a count operation within a QUERY intent
        if entities.get("operation") == "count" or entities.get("count_only"):
            print(f"DEBUG: Count operation detected, entities: {entities}")
            # Count by topic and date range (check this BEFORE extracting year)
            if entities.get("topic") and entities.get("date_range"):
                date_range = entities["date_range"]
                print(f"DEBUG: Has topic and date_range, date_range type: {type(date_range)}, value: {date_range}")
                if isinstance(date_range, dict) and date_range.get("start") and date_range.get("end"):
                    entities["start_date"] = date_range["start"]
                    entities["end_date"] = date_range["end"]
                    print(f"DEBUG: Selecting count_by_topic_date_range template")
                    return SQL_TEMPLATES["count_by_topic_date_range"]
            
            # Extract year from entities if present
            year = extract_year_from_entities(entities)
            
            # Count by topic and year
            if entities.get("topic") and year:
                entities["year"] = year
                return SQL_TEMPLATES["count_by_topic_and_year"]
            
            # Count by year only
            elif year and not entities.get("topic"):
                entities["year"] = year
                return SQL_TEMPLATES["count_by_year"]
            
            # Count operational decisions by topic
            elif entities.get("topic") and entities.get("decision_type") == "אופרטיבית":
                return SQL_TEMPLATES["count_operational_by_topic"]
            
            # Count by government only
            elif entities.get("government_number") and not entities.get("topic"):
                return SQL_TEMPLATES["count_decisions_by_government"]
            
            # Count by topic only
            elif entities.get("topic"):
                return SQL_TEMPLATES["count_decisions_by_topic"]
        # Decision number search - with or without government number
        if entities.get("decision_number"):
            print(f"DEBUG: Found decision_number: {entities.get('decision_number')}, choosing specific_decision template")
            # Default to current government (37) if not specified
            if not entities.get("government_number"):
                entities["government_number"] = 37
            return SQL_TEMPLATES["specific_decision"]
            
        # Date range search
        if entities.get("date_range"):
            return SQL_TEMPLATES["search_by_date_range"]
        
        # Ministry search
        if entities.get("ministries"):
            # Check if we need joint ministries (ALL ministries must be involved)
            if len(entities.get("ministries", [])) > 1:
                entities["ministry_list"] = entities["ministries"]
                return SQL_TEMPLATES["joint_ministries_decisions"]
            else:
                # Single ministry search
                return SQL_TEMPLATES["search_by_ministry"]
        
        # Government + topic search
        if entities.get("government_number") and entities.get("topic"):
            return SQL_TEMPLATES["search_by_government_and_topic"]
        
        # Check for analysis-type queries based on operation or keywords
        operation = entities.get("operation", "")
        topic = entities.get("topic", "")
        
        # Trend analysis queries
        if ("מגמות" in topic or "טרנד" in topic or operation == "trend" or
            "השנים האחרונות" in topic or "ב-5 השנים" in topic):
            # Clean trend-specific phrases from topic
            cleaned_topic = re.sub(r'\s*ב[-\s]?\d+\s*השנים\s*האחרונות\s*', ' ', topic)
            cleaned_topic = re.sub(r'\s*המגמות\s*ב\s*', ' ', cleaned_topic)
            cleaned_topic = re.sub(r'\s*הראה\s*לי\s*את\s*', '', cleaned_topic)
            entities["topic"] = cleaned_topic.strip()
            return SQL_TEMPLATES["trend_analysis"]
        
        # Deep analysis queries  
        if ("נתח" in topic or "ניתוח" in topic or "חסמים" in topic or "מאפשרים" in topic or
            operation == "analyze" or entities.get("intent") == "EVAL"):
            # Clean analysis-specific phrases from topic
            cleaned_topic = re.sub(r'\s*נתח\s*את\s*ה?', '', topic)
            cleaned_topic = re.sub(r'\s*וזהה\s*חסמים\s*ומאפשרים\s*', '', cleaned_topic)
            cleaned_topic = re.sub(r'\s*החלטות\s*', 'החלטות ', cleaned_topic)
            entities["topic"] = cleaned_topic.strip()
            return SQL_TEMPLATES["deep_analysis"]
        
        # Historical comparison queries
        if ("השווה" in topic or "השוואה" in topic or "בין" in topic or 
            operation == "compare" or entities.get("comparison_target")):
            # Extract years for comparison if available
            years = extract_comparison_years(topic)
            if years:
                entities["start_year"] = years[0]
                entities["end_year"] = years[1]
                return SQL_TEMPLATES["historical_comparison"]
        
        # Recommendations queries
        if ("המלצות" in topic or "המלצה" in topic or "לקדם" in topic or
            operation == "recommend"):
            return SQL_TEMPLATES["recommendations_analysis"]
        
        # Ministry breakdown for detailed searches
        if ("משרד" in topic or "משרדים" in topic or entities.get("ministries")):
            return SQL_TEMPLATES["ministry_breakdown"]
        
        # Year + topic search - extract year from date_range or topic
        year = extract_year_from_entities(entities)
        if year and entities.get("topic"):
            # Add year parameter for the template
            entities["year"] = year
            return SQL_TEMPLATES["search_by_year_and_topic"]
        
        # Topic only search
        if entities.get("topic"):
            return SQL_TEMPLATES["search_by_topic_only"]
        
        # Recent decisions
        return SQL_TEMPLATES["recent_decisions"]
    
    # For comparison queries
    if intent == "comparison" or entities.get("comparison_target"):
        # Check if we have two specific governments to compare
        if entities.get("government_numbers") and len(entities["government_numbers"]) == 2:
            entities["gov1"] = entities["government_numbers"][0]
            entities["gov2"] = entities["government_numbers"][1]
            if entities.get("topic"):
                return SQL_TEMPLATES["compare_policy_between_governments"]
        
        # Check for comparison keywords in topic
        elif entities.get("topic") and ("השווה" in entities["topic"] or "השוואה" in entities["topic"]):
            # Extract government numbers from topic if available
            import re
            gov_pattern = r'ממשלה\s*(\d+)'
            gov_matches = re.findall(gov_pattern, entities["topic"])
            if len(gov_matches) >= 2:
                entities["gov1"] = int(gov_matches[0])
                entities["gov2"] = int(gov_matches[1])
                # Clean the topic to remove comparison words
                clean_topic = re.sub(r'השווה\s+את\s+מדיניות\s+ה?', '', entities["topic"])
                clean_topic = re.sub(r'בין\s+ממשלה\s+\d+\s+ל?ממשלה\s+\d+', '', clean_topic).strip()
                entities["topic"] = clean_topic
                return SQL_TEMPLATES["compare_policy_between_governments"]
        
        # Default comparison with aggregated counts
        elif entities.get("government_list") and entities.get("topic"):
            return SQL_TEMPLATES["compare_governments_detailed"]
        
        return SQL_TEMPLATES["compare_governments"]
    
    # Default fallback
    return SQL_TEMPLATES["recent_decisions"]


def build_dynamic_filters(template: SQLTemplate, entities: Dict[str, Any]) -> str:
    """Build dynamic filter clauses for templates with optional parameters."""
    sql = template.sql
    
    # Government filter
    if "{government_filter}" in sql:
        if entities.get("government_number"):
            government_filter = "AND government_number = %(government_number)s"
        else:
            government_filter = ""
        sql = sql.replace("{government_filter}", government_filter)
    
    # Topic filter
    if "{topic_filter}" in sql:
        if entities.get("topic"):
            topic_filter = "AND %(topic)s = ANY(topics)"
        else:
            topic_filter = ""
        sql = sql.replace("{topic_filter}", topic_filter)
    
    # Date filter
    if "{date_filter}" in sql:
        date_conditions = []
        if entities.get("start_date"):
            date_conditions.append("decision_date >= %(start_date)s")
        if entities.get("end_date"):
            date_conditions.append("decision_date <= %(end_date)s")
        
        if date_conditions:
            date_filter = "AND " + " AND ".join(date_conditions)
        else:
            date_filter = ""
        sql = sql.replace("{date_filter}", date_filter)
    
    return sql


def validate_parameters(template: SQLTemplate, params: Dict[str, Any]) -> List[str]:
    """Validate that all required parameters are present."""
    errors = []
    
    for required_param in template.required_params:
        if required_param not in params or params[required_param] is None:
            errors.append(f"Missing required parameter: {required_param}")
    
    return errors


def sanitize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize parameters to prevent SQL injection."""
    sanitized = {}
    
    for key, value in params.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            value = re.sub(r'[;\'\"\\]', '', value)
            # Limit length
            value = value[:200]
        elif isinstance(value, (int, float)):
            # Ensure reasonable bounds
            if key in ["government_number"]:
                value = max(1, min(50, int(value)))  # Cap at 50 for actual government numbers
            elif key in ["decision_number"]:
                value = max(1, min(9999, int(value)))
            elif key in ["limit"]:
                value = max(1, min(1000, int(value)))
        elif isinstance(value, list):
            # Sanitize list items
            value = [sanitize_parameters({key: item})[key] for item in value[:10]]
        
        sanitized[key] = value
    
    return sanitized


def get_template_coverage() -> Dict[str, Any]:
    """Get coverage statistics for SQL templates."""
    intent_coverage = {}
    total_templates = len(SQL_TEMPLATES)
    
    for template in SQL_TEMPLATES.values():
        for intent in template.intent_match:
            if intent not in intent_coverage:
                intent_coverage[intent] = 0
            intent_coverage[intent] += 1
    
    return {
        "total_templates": total_templates,
        "intent_coverage": intent_coverage,
        "template_names": list(SQL_TEMPLATES.keys()),
        "coverage_percentage": {
            intent: (count / total_templates) * 100 
            for intent, count in intent_coverage.items()
        }
    }


# Default parameters for common cases
DEFAULT_PARAMS = {
    "limit": 5,  # Reduced from 20 to prevent token overflow for large topics like environment
    "min_count": 1,
    "start_date": "2020-01-01",
    "end_date": "2025-12-31"
}