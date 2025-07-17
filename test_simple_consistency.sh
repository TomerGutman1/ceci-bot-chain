#!/bin/bash

# Simple test script to check Decision Guide Bot consistency
# Tests the bot 3 times with the same input

echo "Testing Decision Guide Bot consistency..."
echo "========================================="

TEST_TEXT="החלטת ממשלה מס 1234 בנושא חינוך

1. להקים צוות בראשות מנכ\"ל משרד החינוך
2. להקצות 10 מיליון שקל לתוכנית
3. לדווח לממשלה תוך 6 חודשים
4. משרד החינוך יפעל בשיתוף משרד הכלכלה"

# Function to make a request and extract scores
test_once() {
    local test_num=$1
    echo -e "\nTest $test_num:"
    
    # Call the bot directly on port 8018
    response=$(ssh root@178.62.39.248 "curl -s -X POST http://localhost:8018/analyze \
      -H 'Content-Type: application/json' \
      -d '{
        \"text\": \"$TEST_TEXT\",
        \"documentInfo\": {\"type\": \"text\", \"originalName\": \"test.txt\", \"size\": 200},
        \"requestId\": \"test-$test_num\"
      }'")
    
    if [ $? -eq 0 ]; then
        # Extract scores for key criteria
        echo "$response" | jq -r '.criteria_scores[] | select(.criterion == "לוח זמנים מחייב" or .criterion == "משאבים נדרשים" or .criterion == "מנגנון דיווח/בקרה") | "\(.criterion): \(.score)"'
    else
        echo "Error calling bot"
    fi
}

# Run 3 tests
for i in 1 2 3; do
    test_once $i
    sleep 2
done

echo -e "\n========================================="
echo "If all scores are identical, the fix is working!"