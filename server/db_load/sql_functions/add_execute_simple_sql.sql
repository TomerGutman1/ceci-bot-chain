-- Add the missing execute_simple_sql function
DROP FUNCTION IF EXISTS execute_simple_sql(TEXT);

CREATE OR REPLACE FUNCTION execute_simple_sql(query_text TEXT)
RETURNS TABLE(result JSONB)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Security check - only allow SELECT
    IF UPPER(query_text) NOT LIKE 'SELECT%' THEN
        RAISE EXCEPTION 'Only SELECT queries are allowed';
    END IF;
    
    -- Execute the query
    RETURN QUERY EXECUTE 'SELECT to_jsonb(t) FROM (' || query_text || ') t';
END;
$$;

-- Test the function
SELECT * FROM execute_simple_sql('SELECT COUNT(*) FROM israeli_government_decisions') LIMIT 1;
