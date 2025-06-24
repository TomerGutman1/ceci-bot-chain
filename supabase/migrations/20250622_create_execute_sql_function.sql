-- Supabase SQL Function for executing parameterized queries
-- This should be run in the Supabase SQL editor

-- Drop the function if it exists
DROP FUNCTION IF EXISTS execute_sql(text, jsonb);

-- Create the function
CREATE OR REPLACE FUNCTION execute_sql(
  query_text text,
  params jsonb DEFAULT '[]'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result jsonb;
  row_count integer;
  normalized_query text;
BEGIN
  -- Normalize query for validation
  normalized_query := upper(trim(query_text));
  
  -- Security: Only allow SELECT queries
  IF NOT (normalized_query LIKE 'SELECT%') THEN
    RAISE EXCEPTION 'Only SELECT queries are allowed';
  END IF;
  
  -- Security: Check for dangerous patterns
  IF normalized_query ~* '(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE|--|/\*|\*/|EXEC|EXECUTE)' THEN
    RAISE EXCEPTION 'Query contains forbidden patterns';
  END IF;
  
  -- Execute the query and return results as JSON
  BEGIN
    -- For parameterized queries, we need to use dynamic SQL
    -- This is a simplified version - in production, use proper parameterization
    EXECUTE format('
      SELECT jsonb_agg(row_to_json(t))
      FROM (%s) t
    ', query_text) INTO result;
    
    -- Get row count
    GET DIAGNOSTICS row_count = ROW_COUNT;
    
    -- Return result with metadata
    RETURN jsonb_build_object(
      'data', COALESCE(result, '[]'::jsonb),
      'row_count', COALESCE(jsonb_array_length(result), 0),
      'success', true
    );
    
  EXCEPTION WHEN OTHERS THEN
    -- Return error information
    RETURN jsonb_build_object(
      'data', null,
      'error', SQLERRM,
      'success', false
    );
  END;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION execute_sql(text, jsonb) TO authenticated;

-- Create a simpler version for basic queries without parameters
CREATE OR REPLACE FUNCTION execute_simple_sql(query_text text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN execute_sql(query_text, '[]'::jsonb);
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION execute_simple_sql(text) TO authenticated;

-- Test the function
-- SELECT execute_simple_sql('SELECT COUNT(*) as total FROM israeli_government_decisions');
