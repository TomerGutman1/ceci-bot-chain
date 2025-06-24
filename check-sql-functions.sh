#!/bin/bash

echo "=================================================="
echo "🔍 Checking if SQL Functions exist in Supabase"
echo "=================================================="

# Get the service key from .env.prod
SUPABASE_SERVICE_KEY=$(grep "SUPABASE_SERVICE_KEY=" .env.prod | cut -d '=' -f2)
SUPABASE_URL=$(grep "SUPABASE_URL=" .env.prod | cut -d '=' -f2)

# Function to run SQL queries
run_sql() {
    local query="$1"
    echo -e "\n📝 Testing: $query"
    
    response=$(curl -s -X POST \
        "$SUPABASE_URL/rest/v1/rpc/execute_simple_sql" \
        -H "apikey: $SUPABASE_SERVICE_KEY" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    if [[ $response == *"error"* ]]; then
        echo "❌ Failed: $response"
    else
        echo "✅ Success"
    fi
}

# Check if functions exist by trying to call them
echo -e "\n🔧 Checking RPC Functions:"

# 1. count_all_decisions
echo -e "\n1️⃣ count_all_decisions:"
response=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/rpc/count_all_decisions" \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Content-Type: application/json")
    
if [[ $response == *"count"* ]]; then
    echo "✅ Function exists! Result: $response"
else
    echo "❌ Function missing or error: $response"
fi

# 2. count_decisions_by_topic
echo -e "\n2️⃣ count_decisions_by_topic:"
response=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/rpc/count_decisions_by_topic" \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"topic_name": "חינוך"}')
    
if [[ $response == *"count"* ]]; then
    echo "✅ Function exists! Result: $response"
else
    echo "❌ Function missing or error: $response"
fi

# 3. get_government_statistics
echo -e "\n3️⃣ get_government_statistics:"
response=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/rpc/get_government_statistics" \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"gov_number": 37}')
    
if [[ $response == *"decision_count"* ]]; then
    echo "✅ Function exists! Result: $response"
else
    echo "❌ Function missing or error: $response"
fi

# 4. count_decisions_by_year
echo -e "\n4️⃣ count_decisions_by_year:"
response=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/rpc/count_decisions_by_year" \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"target_year": 2024}')
    
if [[ $response == *"count"* ]]; then
    echo "✅ Function exists! Result: $response"
else
    echo "❌ Function missing or error: $response"
fi

# 5. search_decisions_hebrew
echo -e "\n5️⃣ search_decisions_hebrew:"
response=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/rpc/search_decisions_hebrew" \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Content-Type: application/json" \
    -d '{"search_term": "קורונה"}')
    
if [[ $response == *"decision"* ]] || [[ $response == "[]" ]]; then
    echo "✅ Function exists!"
else
    echo "❌ Function missing or error: $response"
fi

echo -e "\n=================================================="
echo "📊 Summary:"
echo "If functions are missing, you need to run:"
echo "server/db_load/sql_functions/fix_sql_functions.sql"
echo "in the Supabase SQL Editor"
echo "=================================================="
