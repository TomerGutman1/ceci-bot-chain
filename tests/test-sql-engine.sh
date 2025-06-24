#!/bin/bash

# Test script for SQL Query Engine
# Usage: ./test-sql-engine.sh

API_URL="https://localhost"

echo "=================================================="
echo "🧪 Testing SQL Query Engine - Comprehensive Test Suite"
echo "=================================================="

# Function to test a query
test_query() {
    local query="$1"
    local description="$2"
    local expected_type="$3"
    
    echo ""
    echo "📝 Test: $description"
    echo "Query: \"$query\""
    echo "Expected type: $expected_type"
    echo "---"
    
    # --- build safe JSON payload ---
    payload=$(jq -Rn --arg q "$query" '{query:$q}')

    response=$(curl -sk -X POST "${API_URL}/api/chat/test-sql" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if [ $? -eq 0 ]; then
        success=$(echo "$response" | jq -r '.success')
        if [ "$success" = "true" ]; then
            echo "✅ Success!"
            actual_type=$(echo "$response" | jq -r '.type')
            echo "Type: $actual_type"
            
            # Check if type matches expected
            if [ "$expected_type" != "" ] && [ "$actual_type" != "$expected_type" ]; then
                echo "⚠️  Warning: Expected type '$expected_type' but got '$actual_type'"
            fi
            
            echo "Formatted response:"
            echo "$response" | jq -r '.formatted' | head -30
            
            # Show data preview for certain types
            if [ "$actual_type" = "count" ] || [ "$actual_type" = "aggregate" ]; then
                echo ""
                echo "Data preview:"
                echo "$response" | jq 'if (.data|type)=="array" then .data[0] else .data end'
            fi
            
            # Show metadata
            if [ "$(echo "$response" | jq -r '.metadata')" != "null" ]; then
                echo ""
                echo "Metadata:"
                echo "- SQL: $(echo "$response" | jq -r '.metadata.sql_query' | head -1)"
                echo "- Rows: $(echo "$response" | jq -r '.metadata.row_count')"
                echo "- Time: $(echo "$response" | jq -r '.metadata.execution_time')ms"
                echo "- Confidence: $(echo "$response" | jq -r '.metadata.confidence')"
            fi
        else
            echo "❌ Failed!"
            echo "Error: $(echo "$response" | jq -r '.error')"
            echo "Full response: $(echo "$response" | jq '.')"
        fi
    else
        echo "❌ Request failed!"
    fi
    
    echo "=================================================="
}

# Check if server is running
echo "🔍 Checking if server is running..."
health_check=$(curl -sk "${API_URL}/api/chat/health")
if [ $? -ne 0 ]; then
    echo "❌ Server is not running! Please start the server first."
    exit 1
fi

# Check SQL Engine availability
sql_engine_available=$(echo "$health_check" | jq -r '.services.sqlEngine.available')
if [ "$sql_engine_available" != "true" ]; then
    echo "⚠️  Warning: SQL Engine is not fully available"
    echo "Stats: $(echo "$health_check" | jq -r '.services.sqlEngine.stats')"
fi

echo "✅ Server is running"
echo ""

# Basic count queries
echo "🔢 === BASIC COUNT QUERIES ==="
test_query "כמה החלטות יש בסך הכל?" "Count total decisions" "count"
test_query "כמה החלטות יש?" "Count total (short form)" "count"
test_query "כמה החלטות קיימות?" "Count total (alternative form)" "count"

# Year-based queries
echo ""
echo "📅 === YEAR-BASED QUERIES ==="
test_query "כמה החלטות יש משנת 2023?" "Count decisions by year 2023" "count"
test_query "כמה החלטות התקבלו בשנת 2024?" "Count decisions in year 2024" "count"
test_query "כמה החלטות היו בשנת 2022?" "Count decisions year 2022" "count"

# Specific decision queries
echo ""
echo "🎯 === SPECIFIC DECISION QUERIES ==="
test_query "החלטה 660 של ממשלה 35" "Find specific decision 660/35" "single"
test_query "החלטה 100 של ממשלה 37" "Find specific decision 100/37" "single"
test_query "החלטה 1" "Find decision 1 (any government)" "multiple"

# Topic-based queries
echo ""
echo "🏷️ === TOPIC-BASED QUERIES ==="
test_query "הבא לי החלטה בנושא תחבורה" "Single decision about transportation" "single"
test_query "הבא לי החלטה בנושא חינוך" "Single decision about education" "single"
test_query "הבא לי החלטה בנושא בריאות" "Single decision about health" "single"
test_query "הבא 5 החלטות בנושא ביטחון" "5 decisions about security" "multiple"
test_query "כמה החלטות יש בנושא כלכלה?" "Count decisions about economy" "count"

# Government statistics
echo ""
echo "🏛️ === GOVERNMENT STATISTICS ==="
test_query "סטטיסטיקה של ממשלה 37" "Statistics for government 37" "aggregate"
test_query "סטטיסטיקה של ממשלה 36" "Statistics for government 36" "aggregate"
test_query "סטטיסטיקה על ממשלה 35" "Statistics for government 35" "aggregate"

# Recent decisions
echo ""
echo "🕐 === RECENT DECISIONS ==="
test_query "ההחלטות האחרונות" "Most recent decisions" "multiple"
test_query "החלטות אחרונות" "Recent decisions (short)" "multiple"
test_query "החלטות עדכניות" "Current decisions" "multiple"

# Current government queries
echo ""
echo "👥 === CURRENT GOVERNMENT QUERIES ==="
test_query "החלטות מהממשלה הנוכחית בנושא חינוך" "Current government education decisions" "multiple"
test_query "החלטות הממשלה האחרונה בנושא תחבורה" "Current government transport decisions" "multiple"

# Date range queries
echo ""
echo "📆 === DATE RANGE QUERIES ==="
test_query "החלטות מ-1.1.2024 עד 31.12.2024" "Decisions in date range 2024" "multiple"
test_query "החלטות בין 1.1.2023 ל-31.12.2023" "Decisions between dates 2023" "multiple"

# New complex count queries
echo ""
echo "🆕 === NEW COMPLEX COUNT QUERIES ==="
test_query "כמה החלטות בנושא חינוך החליטה ממשלה מס 37" "Count decisions by government 37 and education topic" "count"
test_query "כמה החלטות בנושא חינוך עברו בין 2020 ל2022?" "Count education decisions between 2020-2022" "count"

# Complex queries (expected to fail for now)
echo ""
echo "🔧 === COMPLEX QUERIES (Testing Limits) ==="
test_query "החלטות בנושא חינוך מהשנה האחרונה" "Education decisions from last year" ""
test_query "החלטות של נתניהו" "Decisions by Netanyahu" ""
test_query "כמה החלטות קיבלה כל ממשלה?" "Decisions per government" ""
test_query "מה ההחלטות החשובות ביותר של 2024?" "Important decisions 2024" ""

# Search content queries
echo ""
echo "🔍 === CONTENT SEARCH QUERIES ==="
test_query 'חפש "קורונה"' "Search for Corona" "multiple"
test_query 'חפש את המילה "חינוך חינם"' "Search for free education" "multiple"

echo ""
echo "🎉 All tests completed!"

# Show test summary
echo ""
echo "📊 === TEST SUMMARY ==="
echo "Total tests run: $(grep -cE '^test_query ' "$0")"
echo ""

# Show configuration
echo "Current configuration:"
echo "- Active Engine: $(echo "$health_check" | jq -r '.activeEngine')"
echo "- SQL Engine %: $(echo "$health_check" | jq -r '.sqlEnginePercentage')"
echo "- PandasAI: $(echo "$health_check" | jq -r '.services.pandasai.available')"
echo "- SQL Engine: $(echo "$health_check" | jq -r '.services.sqlEngine.available')"

# Show database statistics if available
if [ "$sql_engine_available" = "true" ]; then
    echo ""
    echo "Database statistics:"
    echo "$health_check" | jq '.services.sqlEngine.stats'
fi
