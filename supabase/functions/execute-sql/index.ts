import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { query, params = [] } = await req.json()

    // Validate input
    if (!query || typeof query !== 'string') {
      throw new Error('Query must be a non-empty string')
    }

    // Security: Only allow SELECT queries
    const normalizedQuery = query.trim().toUpperCase()
    if (!normalizedQuery.startsWith('SELECT')) {
      throw new Error('Only SELECT queries are allowed')
    }

    // Security: Check for dangerous patterns
    const dangerousPatterns = [
      'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
      'GRANT', 'REVOKE', '--', '/*', '*/', 'EXEC', 'EXECUTE'
    ]
    
    for (const pattern of dangerousPatterns) {
      if (normalizedQuery.includes(pattern)) {
        throw new Error(`Query contains forbidden pattern: ${pattern}`)
      }
    }

    // Create Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Execute the query
    // Note: Supabase doesn't support parameterized raw SQL queries directly
    // We'll need to use the query builder or implement our own parameterization
    
    // For now, we'll use a simple approach
    // In production, you should use proper parameterization
    let finalQuery = query
    params.forEach((param: any, index: number) => {
      const placeholder = `$${index + 1}`
      if (typeof param === 'string') {
        finalQuery = finalQuery.replace(placeholder, `'${param.replace(/'/g, "''")}'`)
      } else if (param === null) {
        finalQuery = finalQuery.replace(placeholder, 'NULL')
      } else {
        finalQuery = finalQuery.replace(placeholder, param.toString())
      }
    })

    console.log('Executing query:', finalQuery)

    // Execute using Supabase's rpc if we create a database function
    // For now, we'll return an error indicating this needs to be implemented
    throw new Error('Direct SQL execution not yet implemented. Please use Supabase query builder.')

    // Example of what we'd return on success:
    // return new Response(
    //   JSON.stringify({ data: results, error: null }),
    //   { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    // )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ data: null, error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400
      }
    )
  }
})
