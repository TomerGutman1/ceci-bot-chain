#!/bin/bash

# Quick test for parameter extraction enhancement
# Summary version - minimal output

API_URL="http://localhost:8002/api/process-query"
declare -A results
declare -A first_errors

# Silent test function
silent_test() {
    local category="$1"
    local query="$2"
    local check_param="$3"
    local expected="$4"
    local test_name="$5"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "false" ]; then
        if [ -z "${first_errors[$category]}" ]; then
            error=$(echo "$response" | jq -r '.error' 2>/dev/null | cut -c1-40)
            first_errors[$category]="$test_name: $error..."
        fi
        return 1
    fi
    
    extracted=$(echo "$response" | jq -r ".metadata.extracted_params.$check_param" 2>/dev/null)
    
    if [[ "$extracted" == *"$expected"* ]] && [ "$extracted" != "null" ]; then
        return 0
    else
        if [ -z "${first_errors[$category]}" ]; then
            first_errors[$category]="$test_name: Expected $check_param=$expected, got $extracted"
        fi
        return 1
    fi
}

echo "======================================"
echo "Parameter Extraction Test Summary"
echo "======================================"
echo -n "Running tests"

# Time parameters
category="Time"
silent_test "$category" "מאז 15/03/2023" "date_from" "2023-03-15" "Date normalize" && ((results[$category]++))
echo -n "."
silent_test "$category" "בחודשיים האחרונים" "relative_period" "חודשיים" "Relative period" && ((results[$category]++))
echo -n "."
silent_test "$category" "בין 2021 ל-2023" "date_range" "2021" "Date range" && ((results[$category]++))
echo -n "."

# Topic parameters
category="Topic"
silent_test "$category" "בנושא איכות הסביבה" "topic_fuzzy" "סביבה" "Fuzzy match" && ((results[$category]++))
echo -n "."
silent_test "$category" "רובוטיקה בחינוך" "topic_free" "רובוטיקה" "Free text" && ((results[$category]++))
echo -n "."

# Government
category="Government"
silent_test "$category" "ממשלה 36" "government_number" "36" "Gov number" && ((results[$category]++))
echo -n "."
silent_test "$category" "בתקופת נתניהו" "prime_minister" "נתניהו" "PM name" && ((results[$category]++))
echo -n "."

# Quantity
category="Quantity"
silent_test "$category" "כמה החלטות" "count_only" "true" "Count query" && ((results[$category]++))
echo -n "."
silent_test "$category" "5 החלטות" "limit" "5" "Limit extract" && ((results[$category]++))
echo -n "."

# Content
category="Content"
silent_test "$category" "שמכילות תקציב" "full_text_query" "תקציב" "Text search" && ((results[$category]++))
echo -n "."
silent_test "$category" "החלטות דחופות" "urgency_level" "דחופ" "Urgency" && ((results[$category]++))
echo -n "."

echo " Done!"
echo ""
echo "Test Results:"
echo "============="
printf "%-15s %s\n" "Category" "Passed"
echo "------------------------------"

total_passed=0
total_tests=0
for category in "Time" "Topic" "Government" "Quantity" "Content"; do
    passed="${results[$category]:-0}"
    case $category in
        "Time") total=3 ;;
        "Topic") total=2 ;;
        "Government") total=2 ;;
        "Quantity") total=2 ;;
        "Content") total=2 ;;
    esac
    printf "%-15s %d/%d\n" "$category" "$passed" "$total"
    ((total_passed += passed))
    ((total_tests += total))
done
echo "------------------------------"
printf "%-15s %d/%d\n" "TOTAL" "$total_passed" "$total_tests"

echo ""
if [ ${#first_errors[@]} -gt 0 ]; then
    echo "First error in each category:"
    echo "=============================="
    for category in "${!first_errors[@]}"; do
        echo "$category: ${first_errors[$category]}"
    done
    echo ""
fi

if [ $total_passed -eq $total_tests ]; then
    echo "✅ All parameter extraction tests passed!"
    exit 0
else
    echo "⚠️  Some parameter extraction tests need attention."
    exit 1
fi
