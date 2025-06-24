-- ======================================
-- SQL Functions for Israeli Government Decisions - COMPLETE
-- Created: 23/06/2025
-- This file drops ALL existing functions and recreates them correctly
-- 
-- TABLE STRUCTURE:
-- decision_date (date)
-- decision_number (text)
-- committee (text)
-- decision_title (text)
-- decision_content (text)
-- decision_url (text) -- NOT 'link'!
-- summary (text)
-- operativity (text)
-- tags_policy_area (text)
-- tags_government_body (text)
-- tags_location (text)
-- all_tags (text)
-- government_number (text)
-- prime_minister (text) -- NOT 'prime_minister_name'!
-- decision_key (text)
-- ======================================

-- Step 1: Drop ALL existing functions (based on your output)
DROP FUNCTION IF EXISTS public.count_decisions_by_topic(topic_search text) CASCADE;
DROP FUNCTION IF EXISTS public.count_decisions_per_government() CASCADE;
DROP FUNCTION IF EXISTS public.get_decisions_by_date_range(start_date date, end_date date, result_limit integer) CASCADE;
DROP FUNCTION IF EXISTS public.get_decisions_by_government_and_topic(gov_number text, topic_search text, result_limit integer) CASCADE;
DROP FUNCTION IF EXISTS public.get_decisions_by_prime_minister(pm_name text, result_limit integer) CASCADE;
DROP FUNCTION IF EXISTS public.get_important_decisions_by_year(year_param integer, result_limit integer) CASCADE;
DROP FUNCTION IF EXISTS public.search_decisions_content(search_term text, result_limit integer) CASCADE;
DROP FUNCTION IF EXISTS public.search_decisions_hebrew(search_term text, result_limit integer) CASCADE;

-- Step 2: Create functions with correct signatures (matching what templates expect)

-- 1. Count decisions by topic
CREATE FUNCTION count_decisions_by_topic(topic_name TEXT)
RETURNS TABLE (
  count BIGINT,
  topic TEXT,
  governments_count BIGINT,
  first_decision DATE,
  last_decision DATE
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*)::BIGINT as count,
    topic_name as topic,
    COUNT(DISTINCT government_number)::BIGINT as governments_count,
    MIN(decision_date) as first_decision,
    MAX(decision_date) as last_decision
  FROM israeli_government_decisions
  WHERE tags_policy_area ILIKE '%' || topic_name || '%';
END;
$$ LANGUAGE plpgsql;

-- 2. Search decisions content (simple version without extra parameters)
CREATE FUNCTION search_decisions_content(search_term TEXT)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT,
  relevance REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url,
    (
      CASE 
        WHEN igd.decision_title ILIKE '%' || search_term || '%' THEN 10
        WHEN igd.decision_content ILIKE '%' || search_term || '%' THEN 5
        WHEN igd.summary ILIKE '%' || search_term || '%' THEN 3
        ELSE 1
      END
    )::REAL as relevance
  FROM israeli_government_decisions igd
  WHERE 
    igd.decision_title ILIKE '%' || search_term || '%' OR
    igd.decision_content ILIKE '%' || search_term || '%' OR
    igd.summary ILIKE '%' || search_term || '%' OR
    igd.tags_policy_area ILIKE '%' || search_term || '%'
  ORDER BY relevance DESC, igd.decision_date DESC
  LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 3. Get decisions by date range
CREATE FUNCTION get_decisions_by_date_range(start_date DATE, end_date DATE)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url
  FROM israeli_government_decisions igd
  WHERE igd.decision_date BETWEEN start_date AND end_date
  ORDER BY igd.decision_date DESC;
END;
$$ LANGUAGE plpgsql;

-- 4. Get decisions by government and topic
CREATE FUNCTION get_decisions_by_government_and_topic(gov_number TEXT, topic_name TEXT)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url
  FROM israeli_government_decisions igd
  WHERE (igd.government_number = gov_number OR igd.government_number = gov_number || '.0')
    AND igd.tags_policy_area ILIKE '%' || topic_name || '%'
  ORDER BY igd.decision_date DESC;
END;
$$ LANGUAGE plpgsql;

-- 5. Count decisions per government
CREATE FUNCTION count_decisions_per_government()
RETURNS TABLE (
  government_number TEXT,
  prime_minister TEXT,
  count BIGINT,
  first_decision DATE,
  last_decision DATE,
  topics_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.government_number,
    MAX(igd.prime_minister) as prime_minister,
    COUNT(*)::BIGINT as count,
    MIN(igd.decision_date) as first_decision,
    MAX(igd.decision_date) as last_decision,
    COUNT(DISTINCT igd.tags_policy_area)::BIGINT as topics_count
  FROM israeli_government_decisions igd
  GROUP BY igd.government_number
  ORDER BY igd.government_number DESC;
END;
$$ LANGUAGE plpgsql;

-- 6. Get decisions by prime minister
CREATE FUNCTION get_decisions_by_prime_minister(pm_name TEXT)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  prime_minister TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.prime_minister,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url
  FROM israeli_government_decisions igd
  WHERE igd.prime_minister ILIKE '%' || pm_name || '%'
  ORDER BY igd.decision_date DESC
  LIMIT 100;
END;
$$ LANGUAGE plpgsql;

-- 7. Get important decisions by year
CREATE FUNCTION get_important_decisions_by_year(target_year INTEGER)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  prime_minister TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT,
  importance_score REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.prime_minister,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url,
    (
      CASE 
        WHEN igd.decision_title ILIKE '%חירום%' THEN 10
        WHEN igd.decision_title ILIKE '%תקציב%' THEN 9
        WHEN igd.decision_title ILIKE '%חוק%' THEN 8
        WHEN igd.decision_title ILIKE '%ביטחון%' THEN 8
        WHEN igd.decision_title ILIKE '%כלכלה%' THEN 7
        WHEN igd.decision_title ILIKE '%חינוך%' THEN 6
        WHEN igd.decision_title ILIKE '%בריאות%' THEN 6
        ELSE 5
      END
    )::REAL as importance_score
  FROM israeli_government_decisions igd
  WHERE EXTRACT(YEAR FROM igd.decision_date) = target_year
  ORDER BY importance_score DESC, igd.decision_date DESC
  LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 8. Enhanced Hebrew search function
CREATE FUNCTION search_decisions_hebrew(search_term TEXT)
RETURNS TABLE (
  decision_key TEXT,
  decision_number TEXT,
  government_number TEXT,
  decision_title TEXT,
  prime_minister TEXT,
  decision_date DATE,
  tags_policy_area TEXT,
  decision_url TEXT,
  match_location TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    igd.decision_key,
    igd.decision_number,
    igd.government_number,
    igd.decision_title,
    igd.prime_minister,
    igd.decision_date,
    igd.tags_policy_area,
    igd.decision_url,
    CASE 
      WHEN igd.decision_title ILIKE '%' || search_term || '%' THEN 'title'
      WHEN igd.decision_content ILIKE '%' || search_term || '%' THEN 'content'
      WHEN igd.summary ILIKE '%' || search_term || '%' THEN 'summary'
      WHEN igd.tags_policy_area ILIKE '%' || search_term || '%' THEN 'tags'
      WHEN igd.tags_government_body ILIKE '%' || search_term || '%' THEN 'gov_body'
      WHEN igd.tags_location ILIKE '%' || search_term || '%' THEN 'location'
      ELSE 'other'
    END as match_location
  FROM israeli_government_decisions igd
  WHERE 
    igd.decision_title ILIKE '%' || search_term || '%' OR
    igd.decision_content ILIKE '%' || search_term || '%' OR
    igd.summary ILIKE '%' || search_term || '%' OR
    igd.tags_policy_area ILIKE '%' || search_term || '%' OR
    igd.tags_government_body ILIKE '%' || search_term || '%' OR
    igd.tags_location ILIKE '%' || search_term || '%' OR
    igd.all_tags ILIKE '%' || search_term || '%'
  ORDER BY 
    CASE 
      WHEN igd.decision_title ILIKE '%' || search_term || '%' THEN 1
      WHEN igd.summary ILIKE '%' || search_term || '%' THEN 2
      WHEN igd.tags_policy_area ILIKE '%' || search_term || '%' THEN 3
      WHEN igd.tags_government_body ILIKE '%' || search_term || '%' THEN 4
      ELSE 5
    END,
    igd.decision_date DESC
  LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Verify all functions were created correctly
SELECT 
    p.proname AS function_name,
    pg_get_function_identity_arguments(p.oid) AS arguments
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public' 
AND p.proname IN (
    'count_decisions_by_topic',
    'search_decisions_content',
    'get_decisions_by_date_range',
    'get_decisions_by_government_and_topic',
    'count_decisions_per_government',
    'get_decisions_by_prime_minister',
    'get_important_decisions_by_year',
    'search_decisions_hebrew'
)
ORDER BY p.proname;

-- Step 4: Test the functions
SELECT 'Testing count_decisions_by_topic:' as test;
SELECT * FROM count_decisions_by_topic('חינוך') LIMIT 1;

SELECT 'Testing search_decisions_content:' as test;
SELECT COUNT(*) as results_count FROM search_decisions_content('קורונה');

SELECT 'Testing get_decisions_by_date_range:' as test;
SELECT COUNT(*) as results_count FROM get_decisions_by_date_range('2023-01-01', '2023-12-31');

SELECT 'Testing get_decisions_by_government_and_topic:' as test;
SELECT COUNT(*) as results_count FROM get_decisions_by_government_and_topic('37', 'חינוך');

SELECT 'Testing count_decisions_per_government:' as test;
SELECT COUNT(*) as governments_count FROM count_decisions_per_government();

SELECT 'Testing get_decisions_by_prime_minister:' as test;
SELECT COUNT(*) as results_count FROM get_decisions_by_prime_minister('נתניהו');

SELECT 'Testing get_important_decisions_by_year:' as test;
SELECT COUNT(*) as results_count FROM get_important_decisions_by_year(2024);

SELECT 'Testing search_decisions_hebrew:' as test;
SELECT COUNT(*) as results_count FROM search_decisions_hebrew('חינוך חינם');

-- Expected output:
-- All functions should be created successfully
-- Tests should return meaningful results without errors
