## 🧩 BOT-CHAIN · Micro-Level Implementation Guide

<small>Version 0.9 · June 27 2025</small>

> **תכלית** – מסמך מעשי שמרכז את כל השלבים, החוזים, מבנה התיקיות וה-DevOps הנחוצים להקמת רכיב `bot-chain`
> (ה־Core החדש שמחליף את `sql-engine`) – עם שמות השכבות המלאים.

---

### 1 · High-Level Architecture

```mermaid
flowchart LR
  subgraph BOT_CHAIN
    R0(0_MAIN_REWRITE_BOT)
    I1(1_MAIN_INTENT_BOT)
    SQL2Q(2Q_QUERY_SQL_GEN_BOT)
    CTX2X(2X_MAIN_CTX_ROUTER_BOT)
    CL2C(2C_CLARIFY_CLARIFY_BOT)
    EV2E(2E_EVAL_EVALUATOR_BOT)
    R3Q(3Q_QUERY_RANKER_BOT)
    F4(4_MAIN_FORMATTER)
    DB[(SQL DB)]

    R0 --> I1
    I1 -->|main| SQL2Q
    I1 -->|ctx| CTX2X
    I1 -->|clarify| CL2C

    CTX2X --> SQL2Q
    CTX2X --> EV2E
    CTX2X --> CL2C

    SQL2Q --> DB
    DB --> R3Q
    R3Q --> F4
    EV2E --> F4
    F4 --> FE[(Frontend)]
    FE --> R0
  end
```

---

### 2 · Updated Folder Tree

```text
bot-chain/
├── common/
│   ├── models.py
│   ├── logging.yaml
│   └── utils.py
├── 0_MAIN_REWRITE_BOT/
│   ├── main.py
│   └── Dockerfile
├── 1_MAIN_INTENT_BOT/
│   ├── main.py
│   └── Dockerfile
├── 2Q_QUERY_SQL_GEN_BOT/
│   ├── main.py
│   └── Dockerfile
├── 2X_MAIN_CTX_ROUTER_BOT/
│   ├── main.py
│   └── Dockerfile
├── 2E_EVAL_EVALUATOR_BOT/
│   ├── main.py
│   └── Dockerfile
├── 2C_CLARIFY_CLARIFY_BOT/
│   ├── main.py
│   └── Dockerfile
├── 3Q_QUERY_RANKER_BOT/
│   ├── main.py
│   └── Dockerfile
├── 4_MAIN_FORMATTER/
│   ├── main.py
│   └── Dockerfile
├── docker-compose.yml
├── tests/
│   ├── test_0_main_rewrite_bot.py
│   ├── test_1_main_intent_bot.py
│   ├── test_2q_query_sql_gen_bot.py
│   ├── test_2x_main_ctx_router_bot.py
│   ├── test_2e_eval_evaluator_bot.py
│   ├── test_2c_clarify_clarify_bot.py
│   ├── test_3q_query_ranker_bot.py
│   └── test_4_main_formatter.py
└── README.md
```

---

### 3 · Global Conventions

| Key                  | Value                                                                  |
| -------------------- | ---------------------------------------------------------------------- |
| **Message envelope** | NDJSON – every line = `{conv_id, trace_id, timestamp, layer, payload}` |
| **Trace header**     | `x-conversation-id`                                                    |
| **Event bus**        | Redis Streams `ceci_events`                                            |
| **OpenAI timeout**   | `30 s` per call, 3 retries (expo back-off)                             |
| **Health URL**       | `GET /health` → `{"status":"ok","layer":"<name>"}`                     |
| **Prometheus**       | `/metrics` with labels `layer`, `model`                                |

---

### 4 · Layer-by-Layer Specs

| 🏷️ Layer                      | Endpoint(s)      | Core Logic                                                                           | GPT Model       |
| ------------------------------ | ---------------- | ------------------------------------------------------------------------------------ | --------------- |
| **0\_MAIN\_REWRITE\_BOT**      | `POST /rewrite`  | Prompt-template “Improve Hebrew phrasing + normalize entities”, returns `clean_text` | `gpt-3.5-turbo` |
| **1\_MAIN\_INTENT\_BOT**       | `POST /intent`   | Extract `intent`, `entities`, route flags                                            | `gpt-4-turbo`   |
| **2Q\_QUERY\_SQL\_GEN\_BOT**   | `POST /sqlgen`   | Generate parameterized SQL, verify with `sqlparse`, fallback to templated query      | `gpt-4-turbo`   |
| **2X\_MAIN\_CTX\_ROUTER\_BOT** | `POST /context`  | Fetch last N turns from Redis, decide reuse / merge                                  | `gpt-3.5-turbo` |
| **2E\_EVAL\_EVALUATOR\_BOT**   | `POST /evaluate` | Weight scoring, SHAP explanation, anomaly flags                                      | `gpt-4-turbo`   |
| **2C\_CLARIFY\_CLARIFY\_BOT**  | `POST /clarify`  | Craft follow-up Q ≤ 200-chars                                                        | `gpt-3.5-turbo` |
| **3Q\_QUERY\_RANKER\_BOT**     | `POST /rank`     | BM25 + GPT rerank top 10 rows → `ranked`                                             | `gpt-3.5-turbo` |
| **4\_MAIN\_FORMATTER**         | `POST /format`   | Jinja2 template to final markdown / JSON, add “Full Decision Content” when requested | —               |

---

### 5 · API Contract (Excerpt)

```yaml
# openapi/bot-chain.yml
paths:
  /rewrite:
    post:
      summary: Clean & rewrite user text
      responses:
        "200":
          content:
            application/json:
              schema: { $ref: "#/components/schemas/ReWriteResponse" }

components:
  schemas:
    ReWriteResponse:
      type: object
      properties:
        conv_id: { type: string, format: uuid }
        clean_text: { type: string }
```

(חוזים דומים לכל שכבה - בקבצי YAML נפרדים או מקטעים שונים באותו קובץ.)

---

### 6 · Development Workflow

1. **Contracts-first**
   *Generate pydantic models from OpenAPI → `common/models.py`.*

2. **Layer implementation order**
   `0_MAIN_REWRITE_BOT` → `1_MAIN_INTENT_BOT` → `2Q_QUERY_SQL_GEN_BOT` … → `4_MAIN_FORMATTER`.

3. **Local run**

   ```bash
   docker compose -f docker-compose.yml up -d --build
   curl -X POST http://localhost:8002/rewrite -d '{"text":"..."}'
   ```

4. **Unit tests**

   ```bash
   pytest -q --cov=. tests/
   ```

5. **CI (GitHub Actions)**
   *On PR:* Build all images → `docker compose -f docker-compose.test.yml up` → fail fast.

6. **Blue-green deploy**

   ```bash
   docker compose --profile new-core up -d \
     && ./scripts/smoke.sh \
     || ./scripts/rollback_core.sh
   ```

---

### 7 · Observability & Ops

| Metric                | Source     | Alert Rule            |
| --------------------- | ---------- | --------------------- |
| p95 latency per layer | Prometheus | > 2 s for 5 m         |
| OpenAI error rate     | Prometheus | > 5 %                 |
| Redis stream lag      | Grafana    | > 1 s                 |
| Healthcheck fail      | Watchtower | immediate email/Slack |

---

### 8 · Edge-Case Test Matrix

| Case                    | Expected Behaviour                                  | Critical Layer           |
| ----------------------- | --------------------------------------------------- | ------------------------ |
| Ambiguous question      | Trigger 2C\_CLARIFY\_CLARIFY\_BOT                   | `1_MAIN_INTENT_BOT`      |
| No DB results           | `4_MAIN_FORMATTER` returns “לא נמצאו תוצאות”        | `3Q_QUERY_RANKER_BOT`    |
| Follow-up with pronouns | Context router resolves entities                    | `2X_MAIN_CTX_ROUTER_BOT` |
| Request full content    | Formatter appends **Full Decision Content** section | `2Q_QUERY_SQL_GEN_BOT`   |

---


