#!/bin/bash
# Script to monitor token usage in real-time

echo "📊 Token Usage Monitor for CECI Bot Chain"
echo "========================================="

# Function to format JSON output
format_json() {
    if command -v jq &> /dev/null; then
        jq '.'
    else
        cat
    fi
}

# Function to send a test query and show token usage
test_query() {
    local query="$1"
    local session_id="${2:-test-$(date +%s)}"
    
    echo -e "\n🔍 Testing: \"$query\""
    echo "Session ID: $session_id"
    echo "-----------------------------------------"
    
    response=$(curl -s -X POST http://localhost:5001/api/chat/test-bot-chain \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"$session_id\"}")
    
    # Extract token usage
    if command -v jq &> /dev/null; then
        token_usage=$(echo "$response" | jq -r '.metadata.token_usage // empty')
        
        if [ ! -z "$token_usage" ]; then
            echo "✅ Success!"
            echo ""
            echo "📊 Token Usage:"
            echo "$token_usage" | jq '.'
            
            # Extract key metrics
            total_tokens=$(echo "$token_usage" | jq -r '.total_tokens // 0')
            total_cost=$(echo "$token_usage" | jq -r '.estimated_cost_usd // 0')
            
            echo ""
            echo "📈 Summary:"
            echo "   Total Tokens: $total_tokens"
            echo "   Estimated Cost: \$$total_cost USD"
            
            # Bot breakdown
            echo ""
            echo "🤖 Bot Breakdown:"
            echo "$token_usage" | jq -r '.bot_breakdown // {} | to_entries[] | "   \(.key): \(.value.tokens) tokens (\(.value.cost_usd) USD)"'
        else
            echo "❌ No token usage data in response"
            echo "Response: $response" | format_json
        fi
    else
        echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
    fi
}

# Function to check backend logs for token usage
check_logs() {
    echo -e "\n📜 Recent Token Usage from Logs (last 20 entries):"
    echo "-----------------------------------------"
    docker logs backend 2>&1 | grep -i "token" | tail -20
}

# Function to get usage statistics
get_stats() {
    echo -e "\n📊 Usage Statistics:"
    echo "-----------------------------------------"
    
    response=$(curl -s http://localhost:5001/api/bot-chain/stats 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$response" ]; then
        echo "$response" | format_json
    else
        echo "Stats endpoint not available or no data"
    fi
}

# Main menu
while true; do
    echo -e "\n\n🎯 Token Usage Monitor Menu:"
    echo "1. Test a query and show token usage"
    echo "2. View recent logs"
    echo "3. Get usage statistics"
    echo "4. Run predefined test queries"
    echo "5. Exit"
    echo ""
    read -p "Select option (1-5): " choice
    
    case $choice in
        1)
            read -p "Enter your query: " custom_query
            test_query "$custom_query"
            ;;
        2)
            check_logs
            ;;
        3)
            get_stats
            ;;
        4)
            echo -e "\n🧪 Running Predefined Tests..."
            
            # Simple query
            test_query "3 החלטות בנושא חינוך" "test-simple"
            sleep 2
            
            # Query with ministries
            test_query "החלטות משרד הביטחון השנה" "test-ministry"
            sleep 2
            
            # Statistical query
            test_query "כמה החלטות יש בנושא בריאות?" "test-stats"
            sleep 2
            
            # EVAL query (expensive!)
            test_query "נתח את החלטה 2983" "test-eval"
            
            echo -e "\n✅ All tests completed!"
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done
