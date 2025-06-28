# 📋 CECI‑AI Test Guide v3.3 — QUICK + SUMMARY by default

> **עדכוני v3.3** (Error‑rich output)
>
> * **Error details בהירים** – בכל כישלון יופיעו `Expected:` + **Error**
>   (אם `.error` קיים) או **Message** (אם `.formatted`) או **SQL** מקוצר.
> * `snippet/error` עד 200 תווים נשמר כקודם.
> * שאר המבנה נשמר (תקיית `tests/`, quick + summary כברירת מחדל).

---

## 📄 `tests/run_tests.sh` – סקריפט יחיד, קופי‑פייסט

```bash
#!/usr/bin/env bash
# tests/run_tests.sh – universal test runner for CECI‑AI (v3.3)
# Location: repository_root/tests/
# Default: quick mode + colored summary

set -Eeuo pipefail
trap 'print_summary' EXIT

###############################
#  ✶  DIRECTORY CONTEXT  ✶   #
###############################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"   # stay inside tests/

###################################
#  ✶  CONFIG & DEFAULTS  ✶        #
###################################
API_URL="http://localhost:8002/api/process-query"
MODE="quick"        # quick | comprehensive
VERBOSITY="summary" # quiet | summary | debug
JOBS=1               # parallelism; 1 = serial
FULL_CONTENT=false   # --full-content flag
RESULTS_FILE="results.ndjson"
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
⚠️  **הערות טרם הרצה**
  • קיימים תתי‑סוגי בדיקות (rewrite / date / healthcheck וכו').
  • ודא שאתה בוחר MODE מתאים (quick/comprehensive).
  • דגל --full-content מציג קטע תוכן רק במקרים שנכשלו.
  • ניתן להריץ במקביל עם -j N.
NOTE
}
[[ "$VERBOSITY" != "quiet" ]] && print_notes

###################################
#  ✶  USAGE / ARG PARSING  ✶      #
###################################
usage() {
  cat <<EOF
Usage: ./tests/run_tests.sh [options]
  -m, --mode MODE           quick|comprehensive (default: quick)
  -v, --verbosity LEVEL     quiet|summary|debug (default: summary)
  -j, --jobs N              parallel jobs (default: 1)
      --full-content        include 200‑char snippet on failures
  -h, --help                show this help
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do case "$1" in
  -m|--mode) MODE="$2"; shift 2;;
  -v|--verbosity) VERBOSITY="$2"; shift 2;;
  -j|--jobs) JOBS="$2"; shift 2;;
  --full-content) FULL_CONTENT=true; shift;;
  -h|--help) usage;;
  *) echo "Unknown option: $1" >&2; usage;;
esac; done

#############################
#  ✶  TEST COLLECTION  ✶    #
#############################
# Format: NAME|QUERY|EXPECT_REGEX
# (extend as needed)
declare -a TESTS=(
  "rewrite_basic|שפר ניסוח החלטה 660|success"
  "date_normalizer_since|החלטות מאז 2023|\\\"decision_number\\\""
)

#################################
#  ✶  CORE TEST FUNCTION  ✶     #
#################################
run_one() {
  local name="$1" query="$2" expect="$3"
  local status body passed err snippet="" sql="" error_msg="" formatted="" success="false"

  # API call
  body=$(curl --fail --silent --show-error \
              --write-out '%{http_code}' \
              -H 'Content-Type: application/json' \
              -d "{\"query\": \"$query\"}" "$API_URL") || {
      status="${body: -3}"; err="HTTP $status"; passed=false; }

  [[ -z "${status:-}" ]] && { status="${body: -3}"; body="${body::-3}"; }

  # Extract extra fields for rich error reporting
  success=$(echo "$body" | jq -r '.success // empty' 2>/dev/null)
  error_msg=$(echo "$body" | jq -r '.error // empty' 2>/dev/null)
  formatted=$(echo "$body" | jq -r '.formatted // empty' 2>/dev/null | head -1)
  sql=$(echo "$body" | jq -r '.metadata.sql_query // empty' 2>/dev/null | head -1)

  # pass/fail logic
  if [[ "$status" == "200" && "$success" == "true" && "$body" =~ $expect ]]; then
    passed=true
  else
    passed=false
    if [[ "$success" != "true" && -n "$error_msg" ]]; then
      err="$error_msg"
    elif [[ "$success" != "true" && -z "$error_msg" && -n "$formatted" ]]; then
      err="$formatted"
    elif [[ "$success" == "true" ]]; then
      err="Pattern '$expect' not found"
    fi
  fi

  # snippet (decision_content) only if user requested + failed
  if $FULL_CONTENT && ! $passed; then
    snippet=$(echo "$body" | jq -r '.decision_content' 2>/dev/null | cut -c1-200)
  fi
  # fallback snippet from whole body if still empty
  if ! $passed && [[ -z "$snippet" ]]; then
    snippet="${body:0:200}"
  fi

  # NDJSON record
  jq -nc --arg n "$name" --argjson p $passed --arg e "$err" --arg s "$snippet" --arg sql "$sql" \
    '{name:$n, passed:$p, error:$e, snippet:$s, sql:$sql}' >> "$RESULTS_FILE"

  # live output
  local icon="$( $passed && echo "${GREEN}✓${NC}" || echo "${RED}✗${NC}")"
  log_summary " $icon $name"
  if ! $passed; then
    log_summary "   $(paint "$YELLOW" "Expected: $expect")"
    if [[ -n "$err" ]]; then
      log_summary "   $(paint "$YELLOW" "Error: $err")"
    elif [[ -n "$formatted" ]]; then
      log_summary "   $(paint "$YELLOW" "Message: $formatted")"
    fi
    if [[ -n "$sql" ]]; then
      log_summary "   $(paint "$YELLOW" "SQL: $(echo "$sql" | cut -c1-80)…")"
    fi
    [[ -n "$snippet" && -z "$sql" ]] && log_summary "   $(paint "$YELLOW" "Response: $snippet…")"
  fi
}

###################################
#  ✶  PARALLEL EXECUTION  ✶       #
###################################
export -f run_one paint log_summary
export API_URL MODE VERBOSITY FULL_CONTENT RESULTS_FILE RED GREEN YELLOW NC CYAN BLUE BOLD

printf "%s\n" "${TESTS[@]}" | xargs -n1 -P "$JOBS" -I{} bash -c '\n  IFS="|" read -r n q e <<< "{}"; run_one "$n" "$q" "$e"'

###########################
#  ✶  SUMMARY PRINT  ✶    #
###########################
print_summary() {
  local pass fail total
  pass=$(grep -c '"passed":true' "$RESULTS_FILE" || true)
  fail=$(grep -c '"passed":false' "$RESULTS_FILE" || true)
  total=$((pass+fail))

  echo -e "\n${BLUE}${BOLD}=== SUMMARY ===${NC}"
  echo -e "Total:   $total"
  echo -e "Passed:  $(paint "$GREEN" "$pass")"
  echo -e "Failed:  $(paint "$RED" "$fail")"

  if [[ $fail -eq 0 ]]; then
    echo -e "$(paint "$GREEN" "✔ All tests passed! 🎉")"
  else
    echo -e "$(paint "$RED" "⚠ Some tests failed – see $RESULTS_FILE")"
  fi
}
```

### 🔧 הפעלה בסיסית

```bash
chmod +x ./tests/run_tests.sh
./tests/run_tests.sh                     # quick + summary (ברירת מחדל)
./tests/run_tests.sh -m comprehensive -v debug --full-content
./tests/run_tests.sh -j 4                # ריצה בארבעה תהליכים
```

### 🖨️ דוגמת פלט כשיש כשל (עכשיו עשיר יותר)

```
✗ COUNT_BY_TAG_AND_YEAR template
   Expected: COUNT.*חינוך.*2023
   SQL: SELECT COUNT(*) … חינוך … 2023 …

=== SUMMARY ===
Total:   1
Passed:  0
Failed:  1
⚠ Some tests failed – see results.ndjson
```
