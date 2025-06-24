-- Fix SQL Functions for SQL Query Engine
-- These functions work with the existing query templates
-- Drop existing functions first to avoid conflicts

-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS count_decisions_by_topic(TEXT);
DROP FUNCTION IF EXISTS get_decisions_by_government_and_topic(TEXT, TEXT);
DROP FUNCTION IF EXISTS get_decisions_by_date_range(DATE, DATE);
DROP FUNCTION IF EXISTS count_decisions_per_government();
DROP FUNCTION IF EXISTS get_decisions_by_prime_minister(TEXT);
DROP FUNCTION IF EXISTS get_important_decisions_by_year(INTEGER);
DROP FUNCTION IF EXISTS search_decisions_hebrew(TEXT);
DROP FUNCTION IF EXISTS count_all_decisions();
DROP FUNCTION IF EXISTS count_decisions_by_year(INTEGER);
DROP FUNCTION IF EXISTS get_government_statistics(INTEGER);
DROP FUNCTION IF EXISTS execute_simple_sql(TEXT);

-- 1. Count decisions by topic
CREATE OR REPLACE FUNCTION count_decisions_by_topic(topic_name TEXT)
RETURNS TABLE(count BIGINT) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM israeli_government_decisions
    WHERE tags_policy_area ILIKE '%' || topic_name || '%';
END;
$$;

-- 2. Get decisions by government and topic  
CREATE OR REPLACE FUNCTION get_decisions_by_government_and_topic(gov_number TEXT, topic_name TEXT)
RETURNS SETOF israeli_government_decisions
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM israeli_government_decisions
    WHERE (government_number = gov_number OR government_number = gov_number || '.0')
      AND tags_policy_area ILIKE '%' || topic_name || '%'
    ORDER BY decision_date DESC
    LIMIT 100;
END;
$$;

-- 3. Get decisions by date range
CREATE OR REPLACE FUNCTION get_decisions_by_date_range(start_date DATE, end_date DATE)
RETURNS SETOF israeli_government_decisions
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM israeli_government_decisions
    WHERE decision_date BETWEEN start_date AND end_date
    ORDER BY decision_date DESC
    LIMIT 100;
END;
$$;

-- 4. Count decisions per government  
CREATE OR REPLACE FUNCTION count_decisions_per_government()
RETURNS TABLE(
    government_number TEXT,
    prime_minister TEXT, 
    count BIGINT,
    first_decision DATE,
    last_decision DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        igd.government_number,
        MAX(igd.prime_minister) as prime_minister,
        COUNT(*) as count,
        MIN(igd.decision_date) as first_decision,
        MAX(igd.decision_date) as last_decision
    FROM israeli_government_decisions igd
    GROUP BY igd.government_number
    ORDER BY COUNT(*) DESC;
END;
$$;

-- 5. Get decisions by prime minister
CREATE OR REPLACE FUNCTION get_decisions_by_prime_minister(pm_name TEXT)
RETURNS SETOF israeli_government_decisions
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM israeli_government_decisions
    WHERE prime_minister ILIKE '%' || pm_name || '%'
    ORDER BY decision_date DESC
    LIMIT 100;
END;
$$;

-- 6. Get important decisions by year
CREATE OR REPLACE FUNCTION get_important_decisions_by_year(target_year INTEGER)
RETURNS SETOF israeli_government_decisions
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM israeli_government_decisions
    WHERE EXTRACT(YEAR FROM decision_date) = target_year
      AND (
        decision_title ILIKE '%חשוב%' OR
        decision_title ILIKE '%תכנית%' OR
        decision_title ILIKE '%רפורמה%' OR
        decision_title ILIKE '%תקציב%' OR
        decision_title ILIKE '%חוק%' OR
        decision_title ILIKE '%מדיניות%'
      )
    ORDER BY decision_date DESC
    LIMIT 20;
END;
$$;

-- 7. Search decisions in Hebrew (enhanced)  
CREATE OR REPLACE FUNCTION search_decisions_hebrew(search_term TEXT)
RETURNS SETOF israeli_government_decisions
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM israeli_government_decisions
    WHERE 
        decision_title ILIKE '%' || search_term || '%' OR
        decision_content ILIKE '%' || search_term || '%' OR
        summary ILIKE '%' || search_term || '%' OR
        tags_policy_area ILIKE '%' || search_term || '%' OR
        all_tags ILIKE '%' || search_term || '%'
    ORDER BY decision_date DESC
    LIMIT 100;
END;
$$;

-- 8. Count all decisions
CREATE OR REPLACE FUNCTION count_all_decisions()
RETURNS TABLE(count BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*) FROM israeli_government_decisions;
END;
$$;

-- 9. Count decisions by year
CREATE OR REPLACE FUNCTION count_decisions_by_year(target_year INTEGER)
RETURNS TABLE(count BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM israeli_government_decisions
    WHERE EXTRACT(YEAR FROM decision_date) = target_year;
END;
$$;

-- 10. Get government statistics
CREATE OR REPLACE FUNCTION get_government_statistics(gov_number INTEGER)
RETURNS TABLE(
    government_number TEXT,
    decision_count BIGINT,
    prime_minister TEXT,
    first_decision DATE,
    last_decision DATE,
    policy_areas TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        igd.government_number,
        COUNT(*) as decision_count,
        MAX(igd.prime_minister) as prime_minister,
        MIN(igd.decision_date) as first_decision,
        MAX(igd.decision_date) as last_decision,
        STRING_AGG(DISTINCT igd.tags_policy_area, ', ') as policy_areas
    FROM israeli_government_decisions igd
    WHERE igd.government_number = gov_number::TEXT OR igd.government_number = gov_number || '.0'
    GROUP BY igd.government_number;
END;
$$;

-- 11. Simple SQL executor for testing
CREATE OR REPLACE FUNCTION execute_simple_sql(query_text TEXT)
RETURNS TABLE(result JSONB)
LANGUAGE plpgsql
AS $
BEGIN
    -- Security check - only allow SELECT
    IF UPPER(query_text) NOT LIKE 'SELECT%' THEN
        RAISE EXCEPTION 'Only SELECT queries are allowed';
    END IF;
    
    -- Execute the query
    RETURN QUERY EXECUTE 'SELECT to_jsonb(t) FROM (' || query_text || ') t';
END;
$;

-- Test that functions are working
SELECT 'Testing count_decisions_by_topic:' as test;
SELECT * FROM count_decisions_by_topic('חינוך');

SELECT 'Testing count_all_decisions:' as test;
SELECT * FROM count_all_decisions();

SELECT 'Testing search_decisions_hebrew:' as test;
SELECT COUNT(*) FROM search_decisions_hebrew('קורונה');
