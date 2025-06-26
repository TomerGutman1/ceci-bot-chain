#!/bin/bash

# Debug script to understand parameter extraction structure

API_URL="http://localhost:8002/api/process-query"

echo "=== Parameter Extraction Debug ==="
echo ""

# Test a simple query
query="החלטות מאז 15/03/2023"
echo "Testing query: $query"
echo ""

response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\"}" 2>/dev/null)

# Extract the full metadata
metadata=$(echo "$response" | jq '.metadata' 2>/dev/null)

echo "Full metadata structure:"
echo "$metadata" | jq '.' 2>/dev/null | head -50

echo ""
echo "Extracted params structure:"
echo "$metadata" | jq '.extracted_params' 2>/dev/null | head -30

echo ""
echo "Trying to access date_from directly:"
echo "$metadata" | jq '.extracted_params.date_from' 2>/dev/null

echo ""
echo "Trying to access via TIME PARAMETERS:"
echo "$metadata" | jq '.extracted_params["TIME PARAMETERS"].date_from' 2>/dev/null

echo ""
echo "SQL Query generated:"
echo "$metadata" | jq '.sql_query' 2>/dev/null | head -5

echo ""
echo "Parameters used:"
echo "$response" | jq '.params' 2>/dev/null
