-- תיקון בעיות בפונקציות SQL
-- 1. תיקון get_government_statistics - השוואת government_number נכונה
-- 2. הסרת LIMIT מפונקציות ספירה וסטטיסטיקה

-- תיקון פונקציה לסטטיסטיקת ממשלה
DROP FUNCTION IF EXISTS get_government_statistics(INTEGER);

CREATE OR REPLACE FUNCTION get_government_statistics(gov_number INTEGER)
RETURNS TABLE(
    government_number TEXT,
    decision_count BIGINT,
    prime_minister TEXT,
    first_decision DATE,
    last_decision DATE,
    policy_areas_count INTEGER
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
        COUNT(DISTINCT CASE WHEN igd.tags_policy_area IS NOT NULL AND igd.tags_policy_area != '' THEN igd.tags_policy_area END)::INTEGER as policy_areas_count
    FROM israeli_government_decisions igd
    WHERE igd.government_number = gov_number::TEXT OR igd.government_number = gov_number::TEXT || '.0'
    GROUP BY igd.government_number;
END;
$$;

-- פונקציה חדשה לספירת החלטות של ממשלה
CREATE OR REPLACE FUNCTION count_decisions_by_government(gov_number INTEGER)
RETURNS TABLE(count BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)
    FROM israeli_government_decisions
    WHERE government_number = gov_number::TEXT OR government_number = gov_number::TEXT || '.0';
END;
$$;

-- פונקציה משופרת לספירת החלטות לפי ממשלה ונושא
CREATE OR REPLACE FUNCTION count_decisions_by_government_and_topic(gov_number INTEGER, topic_name TEXT)
RETURNS TABLE(
    count BIGINT,
    topic TEXT,
    government_number TEXT,
    prime_minister TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as count,
        topic_name as topic,
        MAX(igd.government_number) as government_number,
        MAX(igd.prime_minister) as prime_minister
    FROM israeli_government_decisions igd
    WHERE (igd.government_number = gov_number::TEXT OR igd.government_number = gov_number::TEXT || '.0')
      AND igd.tags_policy_area ILIKE '%' || topic_name || '%';
END;
$$;

-- בדיקות
SELECT 'Testing get_government_statistics for government 37:' as test;
SELECT * FROM get_government_statistics(37);

SELECT 'Testing count_decisions_by_government for government 37:' as test;
SELECT * FROM count_decisions_by_government(37);

SELECT 'Testing count_decisions_by_government_and_topic for government 37 and ביטחון:' as test;
SELECT * FROM count_decisions_by_government_and_topic(37, 'ביטחון');
