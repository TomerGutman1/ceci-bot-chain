#!/usr/bin/env bash
# Bot Chain Quick Tests
# Tests the individual bot services and basic functionality
# Based on the existing CECI-AI test framework but adapted for bot chain

set -Eeuo pipefail
trap 'print_summary' EXIT

###############################
#  ✶  DIRECTORY CONTEXT  ✶   #
###############################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

###################################
#  ✶  CONFIG & DEFAULTS  ✶        #
###################################
BOT_CHAIN_URL="http://localhost:8002"
REWRITE_URL="http://localhost:8010"
INTENT_URL="http://localhost:8011"
SQL_GEN_URL="http://localhost:8012"
CONTEXT_ROUTER_URL="http://localhost:8013"
EVALUATOR_URL="http://localhost:8014"
CLARIFY_URL="http://localhost:8015"
RANKER_URL="http://localhost:8016"
FORMATTER_URL="http://localhost:8017"

MODE="quick"        # quick | comprehensive
VERBOSITY="summary" # quiet | summary | debug
JOBS=1               # parallelism; 1 = serial
RESULTS_FILE="bot_chain_results.ndjson"
:> "$RESULTS_FILE"   # truncate

################################
#  ✶  ANSI COLORS INLINE  ✶     #
################################
RED='\e[31m'; GREEN='\e[32m'; YELLOW='\e[33m'; BLUE='\e[34m'; CYAN='\e[36m'; NC='\e[0m'; BOLD='\e[1m'
paint() { printf "%b%s%b" "$1" "$2" "$NC"; }

###############################
#  ✶  LOGGING HELPERS  ✶      #
###############################
log_debug()   { [[ "$VERBOSITY" == "debug" ]]   && echo -e "$(paint "$CYAN" "[DBG]") $*"; }
log_summary() { [[ "$VERBOSITY" != "quiet"  ]]   && echo -e "$*"; }

################################
#  ✶  PRE‑RUN NOTES  ✶         #
################################
print_notes() {
  cat <<'NOTE'
🤖 **Bot Chain Test Suite**
  • Tests individual bot services (rewrite, intent, sql-gen)
  • Validates API contracts and basic functionality
  • Use --mode comprehensive for full integration tests
  • Ensure docker compose is running: cd bot_chain && docker compose up -d
NOTE
}
[[ "$VERBOSITY" != "quiet" ]] && print_notes

###################################
#  ✶  USAGE / ARG PARSING  ✶      #
###################################
usage() {
  cat <<EOF
Usage: ./tests/run_bot_chain_tests.sh [options]
  -m, --mode MODE           quick|comprehensive (default: quick)
  -v, --verbosity LEVEL     quiet|summary|debug (default: summary)
  -j, --jobs N              parallel jobs (default: 1)
  -h, --help                show this help

Bot Chain Test Suite - Tests individual bot services and orchestration
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do case "$1" in
  -m|--mode) MODE="$2"; shift 2;;
  -v|--verbosity) VERBOSITY="$2"; shift 2;;
  -j|--jobs) JOBS="$2"; shift 2;;
  -h|--help) usage;;
  *) echo "Unknown option: $1" >&2; usage;;
esac; done

#############################
#  ✶  TEST COLLECTION  ✶    #
#############################
# Format: NAME|URL|PAYLOAD|EXPECT_REGEX|METHOD
declare -a TESTS=(
  # Health checks
  "rewrite_health|$REWRITE_URL/health||status.*ok|GET"
  "intent_health|$INTENT_URL/health||status.*ok|GET"
  "sql_gen_health|$SQL_GEN_URL/health||status.*ok|GET"
  "context_router_health|$CONTEXT_ROUTER_URL/health||status.*ok|GET"
  "evaluator_health|$EVALUATOR_URL/health||status.*ok|GET"
  "clarify_health|$CLARIFY_URL/health||status.*ok|GET"
  "ranker_health|$RANKER_URL/health||status.*ok|GET"
  "formatter_health|$FORMATTER_URL/health||status.*ok|GET"
  "bot_chain_health|$BOT_CHAIN_URL/health||status.*ok|GET"
  
  # Rewrite bot tests
  "rewrite_basic|$REWRITE_URL/rewrite|{\"text\":\"תביא לי החלטות ממשלה שלושים ושבע\",\"conv_id\":\"$(uuidgen)\"}|clean_text|POST"
  "rewrite_normalization|$REWRITE_URL/rewrite|{\"text\":\"החלטה מספר 660 ממשלה 37\",\"conv_id\":\"$(uuidgen)\"}|clean_text|POST"
  
  # Intent bot tests  
  "intent_search|$INTENT_URL/intent|{\"text\":\"החלטות ממשלה 37 בנושא חינוך\",\"conv_id\":\"$(uuidgen)\"}|search|POST"
  "intent_count|$INTENT_URL/intent|{\"text\":\"כמה החלטות קיבלה ממשלה 37\",\"conv_id\":\"$(uuidgen)\"}|count|POST"
  "intent_specific|$INTENT_URL/intent|{\"text\":\"החלטה 660 של ממשלה 37\",\"conv_id\":\"$(uuidgen)\"}|specific_decision|POST"
  
  # SQL generation tests
  "sql_gen_search|$SQL_GEN_URL/sqlgen|{\"intent\":\"search\",\"entities\":{\"government_number\":37,\"topic\":\"חינוך\"},\"conv_id\":\"$(uuidgen)\"}|SELECT|POST"
  "sql_gen_count|$SQL_GEN_URL/sqlgen|{\"intent\":\"count\",\"entities\":{\"government_number\":37},\"conv_id\":\"$(uuidgen)\"}|COUNT|POST"
  "sql_gen_specific|$SQL_GEN_URL/sqlgen|{\"intent\":\"specific_decision\",\"entities\":{\"government_number\":37,\"decision_number\":660},\"conv_id\":\"$(uuidgen)\"}|WHERE.*government_number|POST"
  
  # Context Router tests
  "context_route_direct|$CONTEXT_ROUTER_URL/route|{\"conv_id\":\"$(uuidgen)\",\"current_query\":\"החלטות ממשלה 37 בנושא חינוך\",\"intent\":\"search\",\"entities\":{\"government_number\":37,\"topic\":\"חינוך\"},\"confidence_score\":0.9}|route|POST"
  "context_route_clarify|$CONTEXT_ROUTER_URL/route|{\"conv_id\":\"$(uuidgen)\",\"current_query\":\"מה קורה?\",\"intent\":\"search\",\"entities\":{},\"confidence_score\":0.5}|clarify|POST"
  
  # Evaluator tests
  "evaluator_excellent|$EVALUATOR_URL/evaluate|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"החלטה 660 של ממשלה 37\",\"intent\":\"specific_decision\",\"entities\":{\"government_number\":37,\"decision_number\":660},\"sql_query\":\"SELECT * FROM decisions WHERE gov=37 AND num=660\",\"results\":[{\"id\":1,\"government_number\":37,\"decision_number\":660,\"title\":\"החלטה טסט\",\"content\":\"תוכן החלטה\"}],\"result_count\":1,\"execution_time_ms\":85}|overall_score|POST"
  "evaluator_metrics|$EVALUATOR_URL/metrics||evaluation_weights|GET"
  
  # Clarification tests
  "clarify_missing_gov|$CLARIFY_URL/clarify|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"החלטות בנושא חינוך\",\"intent\":\"search\",\"entities\":{\"topic\":\"חינוך\"},\"confidence_score\":0.6,\"clarification_type\":\"missing_entities\"}|clarification_questions|POST"
  "clarify_vague_query|$CLARIFY_URL/clarify|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"מה קורה?\",\"intent\":\"search\",\"entities\":{},\"confidence_score\":0.3,\"clarification_type\":\"vague_intent\"}|clarification_questions|POST"
  "clarify_templates|$CLARIFY_URL/templates||clarification_types|GET"
  
  # Ranking tests
  "ranker_hybrid|$RANKER_URL/rank|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"החלטות בנושא חינוך\",\"intent\":\"search\",\"entities\":{\"topic\":\"חינוך\"},\"results\":[{\"id\":1,\"title\":\"החלטה על חינוך\",\"content\":\"תוכן החלטה\",\"topics\":[\"חינוך\"],\"decision_date\":\"2023-01-01\"}],\"strategy\":\"hybrid\"}|ranked_results|POST"
  "ranker_strategies|$RANKER_URL/strategies||available_strategies|GET"
  "ranker_stats|$RANKER_URL/stats||ranking_weights|GET"
  
  # Formatting tests
  "formatter_markdown|$FORMATTER_URL/format|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"החלטות בנושא חינוך\",\"intent\":\"search\",\"entities\":{\"topic\":\"חינוך\"},\"ranked_results\":[{\"id\":1,\"title\":\"החלטה על חינוך\",\"content\":\"תוכן החלטה\",\"topics\":[\"חינוך\"],\"decision_date\":\"2023-01-01\"}],\"output_format\":\"markdown\",\"presentation_style\":\"detailed\"}|formatted_response|POST"
  "formatter_json|$FORMATTER_URL/format|{\"conv_id\":\"$(uuidgen)\",\"original_query\":\"החלטות ממשלה 37\",\"intent\":\"search\",\"entities\":{\"government_number\":37},\"ranked_results\":[{\"id\":1,\"title\":\"החלטה\",\"government_number\":37}],\"output_format\":\"json\"}|formatted_response|POST"
  "formatter_formats|$FORMATTER_URL/formats||available_formats|GET"
)

# Add comprehensive tests if requested
if [[ "$MODE" == "comprehensive" ]]; then
  TESTS+=(
    # Templates endpoint
    "sql_templates|$SQL_GEN_URL/templates||total_templates|GET"
    
    # Complex intent scenarios
    "intent_clarification|$INTENT_URL/intent|{\"text\":\"מה עם החינוך\",\"conv_id\":\"$(uuidgen)\"}|clarification_needed|POST"
    "intent_complex_search|$INTENT_URL/intent|{\"text\":\"החלטות משרד החינוך מ-2023\",\"conv_id\":\"$(uuidgen)\"}|ministries|POST"
    
    # Complex SQL generation
    "sql_gen_date_range|$SQL_GEN_URL/sqlgen|{\"intent\":\"search\",\"entities\":{\"topic\":\"ביטחון\",\"date_range\":{\"start\":\"2023-01-01\",\"end\":\"2023-12-31\"}},\"conv_id\":\"$(uuidgen)\"}|decision_date|POST"
    "sql_gen_ministry|$SQL_GEN_URL/sqlgen|{\"intent\":\"search\",\"entities\":{\"ministries\":[\"משרד החינוך\"]},\"conv_id\":\"$(uuidgen)\"}|ministries|POST"
    
    # Context Router comprehensive tests
    "context_stats|$CONTEXT_ROUTER_URL/stats||total_contexts|GET"
    "context_route_ambiguous_time|$CONTEXT_ROUTER_URL/route|{\"conv_id\":\"$(uuidgen)\",\"current_query\":\"החלטות בתקופה האחרונה\",\"intent\":\"search\",\"entities\":{},\"confidence_score\":0.8}|clarify|POST"
    "context_route_missing_entities|$CONTEXT_ROUTER_URL/route|{\"conv_id\":\"$(uuidgen)\",\"current_query\":\"כמה החלטות?\",\"intent\":\"count\",\"entities\":{},\"confidence_score\":0.8}|clarify|POST"
    
    # Error conditions
    "sql_gen_invalid_intent|$SQL_GEN_URL/sqlgen|{\"intent\":\"invalid\",\"entities\":{},\"conv_id\":\"$(uuidgen)\"}|error|POST"
    "intent_empty_text|$INTENT_URL/intent|{\"text\":\"\",\"conv_id\":\"$(uuidgen)\"}|422|POST"
  )
fi

#################################
#  ✶  CORE TEST FUNCTION  ✶     #
#################################
run_one() {
  local name="$1" url="$2" payload="$3" expect="$4" method="$5"
  local status body passed err snippet="" success="false"

  # Prepare curl command
  if [[ "$method" == "GET" ]]; then
    body=$(curl --fail --silent --show-error \
                --write-out '%{http_code}' \
                "$url") || {
        status="${body: -3}"; err="HTTP $status"; passed=false; }
  else
    # POST request
    body=$(curl --fail --silent --show-error \
                --write-out '%{http_code}' \
                -H 'Content-Type: application/json' \
                -d "$payload" "$url") || {
        status="${body: -3}"; err="HTTP $status"; passed=false; }
  fi

  [[ -z "${status:-}" ]] && { status="${body: -3}"; body="${body::-3}"; }

  # Extract success field if JSON
  if echo "$body" | jq empty 2>/dev/null; then
    success=$(echo "$body" | jq -r '.status // .success // empty' 2>/dev/null)
  fi

  # Pass/fail logic
  if [[ "$status" == "200" && "$body" =~ $expect ]]; then
    passed=true
  elif [[ "$status" =~ ^[45] && "$expect" =~ (error|422) ]]; then
    # Expected error condition
    passed=true
  else
    passed=false
    if [[ -n "$success" && "$success" != "true" && "$success" != "ok" ]]; then
      err="Service reported: $success"
    elif [[ "$status" != "200" ]]; then
      err="HTTP $status"
    else
      err="Pattern '$expect' not found"
    fi
  fi

  # Snippet for debugging
  if ! $passed; then
    snippet="${body:0:200}"
  fi

  # NDJSON record
  jq -nc --arg n "$name" --argjson p $passed --arg e "$err" --arg s "$snippet" --arg u "$url" \
    '{name:$n, passed:$p, error:$e, snippet:$s, url:$u}' >> "$RESULTS_FILE"

  # Live output
  local icon="$( $passed && echo "${GREEN}✓${NC}" || echo "${RED}✗${NC}")"
  log_summary " $icon $name"
  if ! $passed; then
    log_summary "   $(paint "$YELLOW" "Expected: $expect")"
    [[ -n "$err" ]] && log_summary "   $(paint "$YELLOW" "Error: $err")"
    [[ -n "$snippet" ]] && log_summary "   $(paint "$YELLOW" "Response: $snippet")"
  fi
}

###################################
#  ✶  PARALLEL EXECUTION  ✶       #
###################################
export -f run_one paint log_summary
export VERBOSITY RESULTS_FILE RED GREEN YELLOW NC CYAN BLUE BOLD

printf "%s\n" "${TESTS[@]}" | xargs -n1 -P "$JOBS" -I{} bash -c '
  IFS="|" read -r n u p e m <<< "{}"; run_one "$n" "$u" "$p" "$e" "$m"'

###########################
#  ✶  SUMMARY PRINT  ✶    #
###########################
print_summary() {
  local pass fail total
  pass=$(grep -c '"passed":true' "$RESULTS_FILE" || true)
  fail=$(grep -c '"passed":false' "$RESULTS_FILE" || true)
  total=$((pass+fail))

  echo -e "\n${BLUE}${BOLD}=== BOT CHAIN TEST SUMMARY ===${NC}"
  echo -e "Total:   $total"
  echo -e "Passed:  $(paint "$GREEN" "$pass")"
  echo -e "Failed:  $(paint "$RED" "$fail")"

  if [[ $fail -eq 0 ]]; then
    echo -e "$(paint "$GREEN" "✔ All bot chain tests passed! 🤖")"
  else
    echo -e "$(paint "$RED" "⚠ Some tests failed – see $RESULTS_FILE")"
    echo -e "\nFailed tests:"
    jq -r 'select(.passed == false) | "  ❌ \(.name): \(.error)"' "$RESULTS_FILE" 2>/dev/null || true
  fi
  
  echo -e "\n$(paint "$CYAN" "💡 Tip: Use 'docker compose logs [service-name]' to debug failures")"
}

# Check if docker compose is running
if ! curl -s "$BOT_CHAIN_URL/health" >/dev/null 2>&1; then
  echo -e "$(paint "$YELLOW" "⚠️  Bot chain services may not be running")"
  echo -e "   Try: cd bot_chain && docker compose up -d"
  echo -e "   Then wait 30s for services to start"
fi