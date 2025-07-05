# SPEC: Reference Resolution in Context Router (2X\_CTX\_ROUTER\_BOT)

## 1. Purpose

* **Objective**: Automatically detect and resolve user references to previous turns (e.g., decision numbers, government numbers, date ranges) before intent parsing.
* **Benefit**: Enhance user experience by filling missing parameters without unnecessary clarifications, while retaining fallback for ambiguity.

## 2. Scope

* Module: **2X\_CTX\_ROUTER\_BOT**
* Languages: JavaScript/TypeScript (within existing codebase)
* Dependencies: Redis memory store, fuzzy-matching library (e.g., `levenshtein` or `fuse.js`)

## 3. High-Level Flow

1. **Receive** `conv_id`, `userText`, existing `slots` (may be empty or partial).
2. **Detect** reference patterns in `userText` (decision\_number, government\_number, date\_range).
3. **Fetch** history (up to `historyTurns` previous turns) from Redis.
4. **Partial/Fuzzy Match** missing slots against history in **recency order** (most recent first).
5. **Determine** missing slot list.
6. **If** any required slots still missing **and** `clarifyOnFail===true`, **generate** dynamic clarify prompt and route to 2C\_CLARIFY\_BOT.
7. **Else**, **construct** enriched input string and pass to `1_INTENT_BOT`.

## 4. Data Models & Storage

### 4.1 Memory Store (Redis)

* Key: `chat:{conv_id}:history`
* Value: List of NDJSON lines, each:

  ```json
  { "turn_id": number, "speaker": "user"|"bot", "clean_text": string, "timestamp": ISOString }
  ```
* TTL: `ttlHours` (e.g., 2h), reset on each append.

### 4.2 Config File (`memory.config.js`)

```js
module.exports = {
  referenceResolver: {
    enabled: true,
    historyTurns: 20,
    ttlHours: 2,
    fuzzyThreshold: 0.6,
    patterns: [
      '^(?:החלטה)\\s*(\\d+)',
      '^(?:של|עבור)\\s*(?:ממשלה\\s*)?(\\d+)',
      '^(?:בין)\\s*(\\d{1,2}\\/\\d{1,2}\\/\\d{2,4})\\s*[-–—]\\s*(\\d{1,2}\\/\\d{1,2}\\/\\d{2,4})'
    ],
    clarifyOnFail: true
  }
};
```

## 5. Reference Resolution Algorithm

### 5.1 Pattern Matching

* Iterate over `patterns` (in order):

  * If `userText.match(pattern)`, extract group(s) into `matches` object:

    * `decision_number`, `government_number`, `date_range`.

### 5.2 History-Based Partial Match

* **⚠️ Recency Emphasis**: הסבירות שהמשתמש מתייחס לפניה מעבר ל־3 הודעות אחורה נמוכה משמעותית; יש להתמקד בשלוש ההודעות האחרונות.
* Order: **most recent turn → oldest**, up to `historyTurns`.
* Order: **most recent turn → oldest**, up to `historyTurns`.
* For each missing slot:

  1. Iterate history turns in recency order.
  2. Apply slot-specific regex on `clean_text`.
  3. If match & `fuzzy(clean_text, matchedText) >= fuzzyThreshold`, assign slot value.
  4. Break on first match.

### 5.3 Recency Weighting

* Implicit: iterating in order ensures more recent turns override older ones.
* **Note**: No explicit weighting score needed unless future extension.

## 6. Clarify Handling

* Identify `missingSlots = requiredSlots.filter(s => !matches[s])`.
* If `missingSlots.length > 0` **and** `clarifyOnFail`:

  1. Build `knownParts` summary from `matches`.
  2. Map each `missingSlot` to human label (e.g., `"מספר החלטה"`, `"ממשלה"`, `"טווח תאריכים"`).
  3. Draft prompt:

     > "לא ברור לי אם התכוונת ל־\${knownParts || 'הקשר כלשהו'} או ל־\${missingLabels}. תוכל בבקשה לציין למה אתה מתכוון ולהרחיב קצת?"
  4. Route to **2C\_CLARIFY\_BOT** with this prompt.

## 7. Enrichment & Forwarding

* If all `requiredSlots` filled:

  ```js
  let enriched = `הבא לי את החלטה ${matches.decision_number}`;
  if (matches.government_number) enriched += ` של ממשלה ${matches.government_number}`;
  if (matches.date_range) enriched += ` בין ${matches.date_range[0]} ל־${matches.date_range[1]}`;
  return { nextInput: enriched, route: '1_INTENT_BOT' };
  ```

## 8. Integration Points

* **Module**: `2X_CTX_ROUTER_BOT.js`
* **Invoke**: At start of routing, before intent parsing.
* **Dependencies**: Import `memory` API, `config`, and `similarity` function.

## 9. Performance & Reliability

* **p95 latency** for fetch+resolve ≤ 100ms.
* On Redis failure: fallback to no-op (pass `userText` unchanged to intent layer).
* Ensure non-blocking behavior.

## 10. Optional Metrics

* `ref_resolution_attempts_total`
* `ref_resolved_total`
* `ref_failed_total`

## 11. Testing Scenarios

| Scenario                                | Input                       | History Snippet                                                   | Expected Outcome                                                                                |
| --------------------------------------- | --------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1. Direct government+decision           | "החלטה 276"                 | "ממשלה 36" (1 turn behind)                                        | Enriched: "הבא לי את החלטה 276 של ממשלה 36"                                                     |
| 2. Missing government from input        | "החלטה 100"                 | "ממשלה 35" (3 turns behind)                                       | Enriched: "הבא לי את החלטה 100 של ממשלה 35"                                                     |
| 3. Date-range only                      | "בין 1/5/2022-30/6/2022"    | —                                                                 | Clarify prompt: missing decision\_number & government\_number                                   |
| 4. Decision only, date in history       | "החלטה 50"                  | "בין 1/1/2023 - 31/1/2023"                                        | Enriched: "הבא לי את החלטה 50 בין 1/1/2023 ל־31/1/2023"                                         |
| 5. Government only, decision in history | "ממשלה 34"                  | "החלטה 88" (2 turns behind)                                       | Enriched: "הבא לי את החלטה 88 של ממשלה 34"                                                      |
| 6. Multiple candidates in history       | "החלטה 12"                  | Turn 1: "החלטה 12"; Turn 2: "החלטה 12 של ממשלה 30"                | Use most recent: "הבא לי את החלטה 12 של ממשלה 30"                                               |
| 7. Fuzzy match threshold                | "החלטה תשעים"               | "החלטה 90" (1 turn behind, spelled numeric)                       | Enriched via fuzzy: "הבא לי את החלטה 90"                                                        |
| 8. Near-limit history                   | "החלטה 200"                 | 21 turns back: "ממשלה 40"; within 20 turns: "ממשלה 41" (19 turns) | Enriched: "הבא לי את החלטה 200 של ממשלה 41"                                                     |
| 9. Ambiguous after fuzzy attempt        | "החלטה X"                   | No matching patterns or history                                   | Clarify prompt: reference resolution failed – request specifics                                 |
| 10. User refers to two slots            | "X בין 10/2/2024-15/2/2024" | "החלטה 15 של ממשלה 39"                                            | Enriched: "הבא לי את החלטה 15 של ממשלה 39 בין 10/2/2024 ל־15/2/2024"                            |
| 11. Redis unavailable                   | "החלטה 300"                 | \[Redis error simulated]                                          | Pass through original input to INTENT: "החלטה 300" (no enrichment)                              |
| 12. Clarify enriched context            | "ממשלה 37"                  | "החלטה 120" (5 turns behind)                                      | Clarify prompt: "לא ברור לי אם התכוונת ל־החלטה 120 של ממשלה 37 או לממשלה 37 בלבד. תוכל להבהיר?" |

\---------------------------|-----------------------|---------------------------------------|------------------------------------------------|
\| Direct gov+decision       | "החלטה 276"         | "ממשלה 36" (1 turn behind)          | Enriched: "הבא לי את החלטה 276 של ממשלה 36" |
\| Missing gov, partial hist | "החלטה 100"         | "בין 1/1/2023 - 31/1/2023"           | Enriched: include date\_range                  |
\| Ambiguous                 | "ממשלה 35"          | no prior decisions                    | Clarify prompt (gov missing or unclear)       |
\| Date range only           | "בין 1/5/2022-30/6/2022" | no gov/decision                       | Clarify prompt with missing both slots        |

---

*End of Reference Resolution Specification*
