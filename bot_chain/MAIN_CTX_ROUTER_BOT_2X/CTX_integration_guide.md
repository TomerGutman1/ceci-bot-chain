 🧠 CECI Bot Chain Memory Service Integration Guide

  📋 Table of Contents

  1. #system-architecture--integration-points
  2. #critical-linking-points
  3. #required-changes-by-component
  4. #data-flow--handoff-protocols
  5. #api-contracts--interfaces
  6. #implementation-checklist
  7. #testing-integration-points

  ---
  🏗️ System Architecture & Integration Points

  graph TB
      subgraph "Frontend Layer"
          User[👤 User Input]
          Frontend[🌐 Frontend :3001]
          User --> Frontend
      end

      subgraph "Server Layer"
          Backend[🖥️ Backend :5001]
          BotChain[🤖 BotChainService]
          Frontend --> Backend
          Backend --> BotChain
      end

      subgraph "Memory Integration Hub"
          RouterBot[🎯 Context Router Bot :8013]
          MemoryService[🧠 Memory Service]
          RouterBot --> MemoryService
      end

      subgraph "Storage Layer"
          Redis[💾 Redis :6380]
          MemoryService --> Redis
      end

      subgraph "Bot Chain Services"
          IntentBot[🎭 Intent Bot :8011]
          SQLBot[🗄️ SQL Gen Bot :8012]
          ClarifyBot[❓ Clarify Bot :8015]
          FormatterBot[📝 Formatter Bot :8017]
      end

      BotChain -.->|"🔗 LINK 1\nDetect Context Needs"| RouterBot
      RouterBot -.->|"🔗 LINK 2\nIntent Analysis"| IntentBot
      RouterBot -.->|"🔗 LINK 3\nContext-Enhanced Routing"| SQLBot
      RouterBot -.->|"🔗 LINK 4\nHistory-Aware Clarification"| ClarifyBot
      SQLBot -.->|"🔗 LINK 5\nMemory-Enhanced Responses"| FormatterBot

      style MemoryService fill:#e1f5fe,stroke:#0277bd,stroke-width:3px
      style RouterBot fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
      style BotChain fill:#fff3e0,stroke:#ef6c00,stroke-width:3px

  ---
  🔗 Critical Linking Points

  🔗 LINK 1: BotChainService → Context Router Bot

  Location: server/src/services/botChainService.ts
  Status: ❌ MISSING - NEEDS IMPLEMENTATION

  What's Missing:
  // Current botChainService.ts (missing context detection)
  const contextResponse = await axios.post(`${CONTEXT_ROUTER_BOT_URL}/route`, {
    conv_id: convId,
    current_query: query,
    intent: intentResponse.intent,
    entities: intentResponse.entities,
    confidence_score: intentResponse.confidence
    // ❌ Missing: route_flags with needs_context detection
  });

  What Needs to be Added:
  // server/src/services/botChainService.ts - ADD THIS
  interface ContextDetectionResult {
    needs_context: boolean;
    context_type: 'follow_up' | 'reference' | 'analysis' | 'none';
    confidence: number;
  }

  function detectContextNeeds(query: string, intent: string, entities: any): ContextDetectionResult {
    // 1. Follow-up query detection
    const followUpKeywords = ['גם', 'עוד', 'נוסף', 'תוכן מלא', 'פרטים', 'המשך'];
    const hasFollowUp = followUpKeywords.some(keyword => query.includes(keyword));

    // 2. Reference pattern detection
    const referencePatterns = ['זה', 'זו', 'האחרון', 'הקודם', 'הנ"ל', 'שאמרת'];
    const hasReference = referencePatterns.some(pattern => query.includes(pattern));

    // 3. Intent-based context needs
    const memoryIntents = ['RESULT_REF', 'ANALYSIS', 'COMPARISON'];
    const isMemoryIntent = memoryIntents.includes(intent);

    // 4. Entity-based context needs
    const needsEntityContext = !entities.decision_number && !entities.government_number;

    if (isMemoryIntent) return { needs_context: true, context_type: 'analysis', confidence: 0.95 };
    if (hasReference) return { needs_context: true, context_type: 'reference', confidence: 0.9 };
    if (hasFollowUp) return { needs_context: true, context_type: 'follow_up', confidence: 0.8 };
    if (needsEntityContext) return { needs_context: true, context_type: 'reference', confidence: 0.7 };

    return { needs_context: false, context_type: 'none', confidence: 0.1 };
  }

  // Modified routing call - ADD THIS
  async function routeWithMemoryContext(
    convId: string,
    query: string,
    intentResponse: any
  ): Promise<any> {
    const contextDetection = detectContextNeeds(query, intentResponse.intent, intentResponse.entities);

    const routingRequest = {
      conv_id: convId,
      current_query: query,
      intent: intentResponse.intent,
      entities: intentResponse.entities,
      confidence_score: intentResponse.confidence,
      route_flags: {
        needs_context: contextDetection.needs_context,
        context_type: contextDetection.context_type,
        context_confidence: contextDetection.confidence
      }
    };

    const response = await axios.post(`${CONTEXT_ROUTER_BOT_URL}/route`, routingRequest);
    return response.data;
  }

  🔗 LINK 2: Context Router Bot → Intent Bot

  Location: bot_chain/MAIN_CTX_ROUTER_BOT_2X/main.py
  Status: ✅ ALREADY IMPLEMENTED

  Current Flow:
  # This is already working - no changes needed
  context = await get_conversation_context(request.conv_id)
  # Intent analysis happens before routing to Context Router

  🔗 LINK 3: Context Router Bot → SQL Gen Bot

  Location: bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py
  Status: ❌ MISSING - NEEDS IMPLEMENTATION

  What's Missing:
  # Current SQL Gen Bot request (missing conversation context)
  class SQLGenerationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      intent: str
      # ❌ Missing: conversation_history field

  What Needs to be Added:
  # bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py - ADD THIS
  from typing import List, Dict, Any, Optional

  class ConversationTurn(BaseModel):
      turn_id: str
      speaker: str  # "user" or "bot"
      clean_text: str
      timestamp: str

  class SQLGenerationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      intent: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD THIS
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD THIS

  def enhance_sql_with_context(
      base_query: str,
      entities: Dict[str, Any],
      conversation_history: List[ConversationTurn]
  ) -> Dict[str, Any]:
      """Enhance SQL generation with conversation context."""

      # 1. Extract missing entities from conversation history
      for turn in reversed(conversation_history):
          if turn.speaker == "user":
              # Parse previous queries for entities
              if "החלטה" in turn.clean_text and not entities.get("decision_number"):
                  decision_match = re.search(r'(\d+)', turn.clean_text)
                  if decision_match:
                      entities["decision_number"] = decision_match.group(1)

      # 2. Detect follow-up patterns
      if any("תוכן מלא" in turn.clean_text for turn in conversation_history[-2:]):
          entities["request_full_content"] = True

      # 3. Context-aware SQL template selection
      if len(conversation_history) > 2:
          # User has context, can use more complex queries
          return {"entities": entities, "context_aware": True}

      return {"entities": entities, "context_aware": False}

  @app.post("/generate-sql")
  async def generate_sql_with_context(request: SQLGenerationRequest):
      """Generate SQL with conversation context awareness."""

      # Enhance entities with conversation context
      enhanced_data = enhance_sql_with_context(
          request.query,
          request.entities,
          request.conversation_history
      )

      # Use enhanced entities for SQL generation
      sql_result = await generate_sql(
          request.query,
          enhanced_data["entities"],
          context_aware=enhanced_data["context_aware"]
      )

      return sql_result

  🔗 LINK 4: Context Router Bot → Clarify Bot

  Location: bot_chain/CLARIFY_CLARIFY_BOT_2C/main.py
  Status: ❌ MISSING - NEEDS IMPLEMENTATION

  What's Missing:
  # Current Clarify Bot (missing conversation context)
  class ClarificationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      ambiguity_type: str
      # ❌ Missing: conversation_history for context-aware clarification

  What Needs to be Added:
  # bot_chain/CLARIFY_CLARIFY_BOT_2C/main.py - ADD THIS
  class ClarificationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      ambiguity_type: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD THIS
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD THIS

  def generate_context_aware_clarification(
      query: str,
      entities: Dict[str, Any],
      ambiguity_type: str,
      conversation_history: List[ConversationTurn]
  ) -> str:
      """Generate clarification questions with conversation context."""

      # Extract context from conversation history
      previous_topics = []
      previous_decisions = []

      for turn in conversation_history:
          if turn.speaker == "user":
              # Extract topics and decisions from previous queries
              if "החלטה" in turn.clean_text:
                  decision_match = re.search(r'(\d+)', turn.clean_text)
                  if decision_match:
                      previous_decisions.append(decision_match.group(1))

      # Generate context-aware clarification
      if ambiguity_type == "missing_entities" and previous_decisions:
          return f"האם אתה מתכוון להחלטה {previous_decisions[-1]} שעליה שאלת קודם?"

      elif ambiguity_type == "vague_reference" and "זה" in query:
          if previous_topics:
              return f"האם אתה מתכוון לנושא {previous_topics[-1]} שדיברנו עליו?"

      # Default clarification without context
      return generate_standard_clarification(query, entities, ambiguity_type)

  @app.post("/clarify")
  async def clarify_with_context(request: ClarificationRequest):
      """Generate clarification with conversation context."""

      clarification = generate_context_aware_clarification(
          request.query,
          request.entities,
          request.ambiguity_type,
          request.conversation_history
      )

      return {"clarification": clarification, "context_used": len(request.conversation_history) > 0}

  🔗 LINK 5: SQL Gen Bot → Formatter Bot

  Location: bot_chain/MAIN_FORMATTER_4/main.py
  Status: ❌ MISSING - NEEDS IMPLEMENTATION

  What's Missing:
  # Current Formatter Bot (missing conversation context)
  class FormatterRequest(BaseModel):
      query: str
      sql_result: Dict[str, Any]
      # ❌ Missing: conversation_history for context-aware formatting

  What Needs to be Added:
  # bot_chain/MAIN_FORMATTER_4/main.py - ADD THIS
  class FormatterRequest(BaseModel):
      query: str
      sql_result: Dict[str, Any]
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD THIS
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD THIS

  def format_response_with_context(
      query: str,
      sql_result: Dict[str, Any],
      conversation_history: List[ConversationTurn]
  ) -> str:
      """Format response with conversation context awareness."""

      # Detect follow-up patterns
      is_follow_up = any(
          keyword in turn.clean_text
          for turn in conversation_history[-2:]
          for keyword in ['גם', 'עוד', 'נוסף']
      )

      # Detect full content request
      wants_full_content = any(
          "תוכן מלא" in turn.clean_text
          for turn in conversation_history[-2:]
      )

      # Context-aware formatting
      if is_follow_up:
          prefix = "בנוסף למה שמצאנו קודם, "
      elif wants_full_content:
          prefix = "הנה התוכן המלא: "
      else:
          prefix = ""

      # Format with context
      formatted_response = f"{prefix}{format_standard_response(sql_result)}"

      return formatted_response

  @app.post("/format")
  async def format_with_context(request: FormatterRequest):
      """Format response with conversation context."""

      formatted_response = format_response_with_context(
          request.query,
          request.sql_result,
          request.conversation_history
      )

      return {"formatted_response": formatted_response}

  ---
  🔧 Required Changes by Component

  1. Server/BotChainService (server/src/services/botChainService.ts)

  Priority: 🔴 CRITICAL - MUST IMPLEMENT

  // ADD these interfaces
  interface RouteFlags {
    needs_context: boolean;
    context_type: 'follow_up' | 'reference' | 'analysis' | 'none';
    context_confidence: number;
  }

  interface ContextRequest {
    conv_id: string;
    current_query: string;
    intent: string;
    entities: any;
    confidence_score: number;
    route_flags: RouteFlags;  // ADD THIS
  }

  // ADD this function
  function detectContextNeeds(query: string, intent: string, entities: any): RouteFlags {
    // Implementation from LINK 1 above
  }

  // MODIFY existing routing function
  async function processQuery(convId: string, query: string) {
    // ... existing intent detection code ...

    // ADD context detection
    const contextDetection = detectContextNeeds(query, intentResponse.intent, intentResponse.entities);

    // MODIFY routing request
    const routingRequest: ContextRequest = {
      conv_id: convId,
      current_query: query,
      intent: intentResponse.intent,
      entities: intentResponse.entities,
      confidence_score: intentResponse.confidence,
      route_flags: contextDetection  // ADD THIS
    };

    const contextResponse = await axios.post(`${CONTEXT_ROUTER_BOT_URL}/route`, routingRequest);

    // ... rest of existing code ...
  }

  2. Context Router Bot (bot_chain/MAIN_CTX_ROUTER_BOT_2X/main.py)

  Priority: 🟡 MINOR UPDATE - ALREADY MOSTLY IMPLEMENTED

  # UPDATE ContextRequest model
  class ContextRequest(BaseModel):
      conv_id: str = Field(..., description="Conversation ID")
      current_query: str = Field(..., description="Current user query")
      intent: str = Field(..., description="Detected intent")
      entities: Dict[str, Any] = Field(..., description="Extracted entities")
      confidence_score: float = Field(..., ge=0.0, le=1.0)
      route_flags: Dict[str, Any] = Field(default_factory=dict)  # ADD THIS

  # UPDATE routing logic to pass context to downstream bots
  async def route_to_downstream_bot(route: str, request: ContextRequest, conversation_history: List[Dict]):
      """Route to downstream bot with conversation context."""

      base_request = {
          "query": request.current_query,
          "entities": request.entities,
          "intent": request.intent
      }

      # ADD conversation history if available
      if conversation_history:
          base_request["conversation_history"] = conversation_history
          base_request["context_summary"] = {
              "total_turns": len(conversation_history),
              "last_query": conversation_history[-1].get("clean_text", ""),
              "context_type": request.route_flags.get("context_type", "none")
          }

      # Route to appropriate bot
      if route == "direct_sql":
          response = await axios.post(f"{SQL_GEN_BOT_URL}/generate-sql", base_request)
      elif route == "clarify":
          response = await axios.post(f"{CLARIFY_BOT_URL}/clarify", base_request)

      return response.data

  3. SQL Gen Bot (bot_chain/QUERY_SQL_GEN_BOT_2Q/main.py)

  Priority: 🟠 MODERATE - NEEDS IMPLEMENTATION

  # ADD these to existing models
  class ConversationTurn(BaseModel):
      turn_id: str
      speaker: str
      clean_text: str
      timestamp: str

  # UPDATE existing SQLGenerationRequest
  class SQLGenerationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      intent: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD

  # ADD context enhancement function
  def enhance_entities_with_context(
      entities: Dict[str, Any],
      conversation_history: List[ConversationTurn]
  ) -> Dict[str, Any]:
      """Extract missing entities from conversation history."""

      enhanced_entities = entities.copy()

      # Look for missing decision numbers in previous queries
      if not enhanced_entities.get("decision_number"):
          for turn in reversed(conversation_history):
              if turn.speaker == "user":
                  decision_match = re.search(r'החלטה\s*(\d+)', turn.clean_text)
                  if decision_match:
                      enhanced_entities["decision_number"] = decision_match.group(1)
                      break

      # Look for missing government numbers
      if not enhanced_entities.get("government_number"):
          for turn in reversed(conversation_history):
              if turn.speaker == "user":
                  gov_match = re.search(r'ממשלה\s*(\d+)', turn.clean_text)
                  if gov_match:
                      enhanced_entities["government_number"] = gov_match.group(1)
                      break

      return enhanced_entities

  # UPDATE main SQL generation endpoint
  @app.post("/generate-sql")
  async def generate_sql_with_context(request: SQLGenerationRequest):
      """Generate SQL with conversation context."""

      # Enhance entities with conversation context
      enhanced_entities = enhance_entities_with_context(
          request.entities,
          request.conversation_history
      )

      # Use existing SQL generation logic with enhanced entities
      sql_result = await generate_sql_query(
          request.query,
          enhanced_entities,
          request.intent
      )

      return {
          "sql_query": sql_result,
          "context_used": len(request.conversation_history) > 0,
          "enhanced_entities": enhanced_entities
      }

  4. Clarify Bot (bot_chain/CLARIFY_CLARIFY_BOT_2C/main.py)

  Priority: 🟠 MODERATE - NEEDS IMPLEMENTATION

  # UPDATE existing ClarificationRequest
  class ClarificationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      ambiguity_type: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD

  # ADD context-aware clarification
  def generate_context_aware_clarification(
      query: str,
      entities: Dict[str, Any],
      ambiguity_type: str,
      conversation_history: List[ConversationTurn]
  ) -> str:
      """Generate clarification using conversation context."""

      if not conversation_history:
          return generate_standard_clarification(query, entities, ambiguity_type)

      # Extract context from recent conversation
      recent_decisions = []
      recent_topics = []

      for turn in conversation_history[-5:]:  # Last 5 turns
          if turn.speaker == "user":
              # Extract decision numbers
              decision_matches = re.findall(r'(\d+)', turn.clean_text)
              recent_decisions.extend(decision_matches)

              # Extract topics
              if "החלטה" in turn.clean_text:
                  recent_topics.append("החלטות ממשלה")

      # Context-aware clarification based on ambiguity type
      if ambiguity_type == "missing_entities":
          if recent_decisions and not entities.get("decision_number"):
              return f"האם אתה מתכוון להחלטה {recent_decisions[-1]} שעליה שאלת קודם?"

      elif ambiguity_type == "vague_reference":
          if "זה" in query or "זו" in query:
              if recent_topics:
                  return f"האם אתה מתכוון ל{recent_topics[-1]} שדיברנו עליו?"

      return generate_standard_clarification(query, entities, ambiguity_type)

  5. Formatter Bot (bot_chain/MAIN_FORMATTER_4/main.py)

  Priority: 🟢 LOW - OPTIONAL ENHANCEMENT

  # UPDATE existing FormatterRequest
  class FormatterRequest(BaseModel):
      query: str
      sql_result: Dict[str, Any]
      conversation_history: List[ConversationTurn] = Field(default_factory=list)  # ADD
      context_summary: Dict[str, Any] = Field(default_factory=dict)  # ADD

  # ADD context-aware formatting
  def format_with_conversation_context(
      query: str,
      sql_result: Dict[str, Any],
      conversation_history: List[ConversationTurn]
  ) -> str:
      """Format response with conversation awareness."""

      # Detect conversation patterns
      is_follow_up = any(
          keyword in turn.clean_text
          for turn in conversation_history[-2:]
          for keyword in ['גם', 'עוד', 'נוסף', 'המשך']
      )

      wants_full_content = any(
          "תוכן מלא" in turn.clean_text
          for turn in conversation_history[-2:]
      )

      # Context-aware response formatting
      if is_follow_up:
          prefix = "בנוסף למה שמצאנו קודם:\n\n"
      elif wants_full_content:
          prefix = "הנה התוכן המלא של החלטה:\n\n"
      else:
          prefix = ""

      # Use existing formatting logic
      formatted_response = format_standard_response(sql_result)

      return f"{prefix}{formatted_response}"

  ---
  🔄 Data Flow & Handoff Protocols

  Request Flow with Memory Integration

  sequenceDiagram
      participant U as User
      participant F as Frontend
      participant B as Backend/BotChain
      participant R as Context Router
      participant M as Memory Service
      participant S as SQL Gen Bot
      participant FORMAT as Formatter Bot

      U->>F: "מה התוכן המלא של החלטה 2989?"
      F->>B: POST /api/chat

      Note over B: 🔗 LINK 1: Context Detection
      B->>B: detectContextNeeds()<br/>needs_context: true<br/>context_type: 'follow_up'

      B->>R: POST /route + route_flags

      Note over R: 🔗 Memory Access
      R->>M: fetch(conv_id)
      M-->>R: conversation_history[]

      Note over R: 🔗 LINK 3: Context Enhancement
      R->>S: POST /generate-sql + conversation_history
      S->>S: enhance_entities_with_context()
      S-->>R: sql_result + enhanced_entities

      Note over R: 🔗 LINK 5: Context-Aware Formatting
      R->>FORMAT: POST /format + conversation_history
      FORMAT-->>R: formatted_response

      R->>M: append(user_query + bot_response)
      R-->>B: routing_result + formatted_response
      B-->>F: response
      F-->>U: "הנה התוכן המלא של החלטה 2989..."

  Memory Storage Protocol

  # When and what to store
  def should_store_in_memory(route: str, request: ContextRequest) -> bool:
      """Determine if interaction should be stored in memory."""

      # Don't store clarification requests (incomplete interactions)
      if route == "clarify":
          return False

      # Don't store failed requests
      if request.confidence_score < 0.5:
          return False

      # Store successful interactions
      return True

  def prepare_memory_entry(speaker: str, content: str, metadata: Dict = None) -> Dict:
      """Prepare conversation turn for memory storage."""

      return {
          'turn_id': str(uuid4()),
          'speaker': speaker,  # 'user' or 'bot'
          'clean_text': content,
          'timestamp': datetime.utcnow().isoformat(),
          'metadata': metadata or {}
      }

  ---
  📡 API Contracts & Interfaces

  1. BotChainService → Context Router Contract

  // REQUEST
  interface ContextRoutingRequest {
    conv_id: string;
    current_query: string;
    intent: string;
    entities: Record<string, any>;
    confidence_score: number;
    route_flags: {
      needs_context: boolean;
      context_type: 'follow_up' | 'reference' | 'analysis' | 'none';
      context_confidence: number;
    };
  }

  // RESPONSE
  interface ContextRoutingResponse {
    route: 'direct_sql' | 'clarify' | 'next_bot';
    needs_clarification: boolean;
    clarification_type?: string;
    context_summary: {
      conv_id: string;
      query_count: number;
      entities_count: number;
      context_score: number;
      conversation_history_count: number;
    };
    reasoning: string;
  }

  2. Context Router → SQL Gen Bot Contract

  # REQUEST
  class SQLGenerationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      intent: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)
      context_summary: Dict[str, Any] = Field(default_factory=dict)

  # RESPONSE
  class SQLGenerationResponse(BaseModel):
      sql_query: str
      parameters: Dict[str, Any]
      context_used: bool
      enhanced_entities: Dict[str, Any]
      confidence: float

  3. Context Router → Clarify Bot Contract

  # REQUEST
  class ClarificationRequest(BaseModel):
      query: str
      entities: Dict[str, Any]
      ambiguity_type: str
      conversation_history: List[ConversationTurn] = Field(default_factory=list)
      context_summary: Dict[str, Any] = Field(default_factory=dict)

  # RESPONSE
  class ClarificationResponse(BaseModel):
      clarification: str
      context_used: bool
      suggested_entities: Dict[str, Any]
      confidence: float

  ---
  ✅ Implementation Checklist

  Phase 1: Core Integration (Week 1)

  - 🔴 CRITICAL: Implement detectContextNeeds() in BotChainService
  - 🔴 CRITICAL: Update Context Router to accept route_flags
  - 🔴 CRITICAL: Test memory storage and retrieval
  - 🟡 MODERATE: Update SQL Gen Bot to accept conversation history
  - 🟡 MODERATE: Implement entity enhancement with context

  Phase 2: Context Enhancement (Week 2)

  - 🟠 MODERATE: Implement context-aware clarification
  - 🟠 MODERATE: Add conversation context to formatter
  - 🟠 MODERATE: Test end-to-end context flow
  - 🟢 LOW: Add context-aware response formatting

  Phase 3: Testing & Monitoring (Week 3)

  - 🔴 CRITICAL: Integration tests for all linking points
  - 🔴 CRITICAL: Performance testing of memory operations
  - 🟡 MODERATE: Monitoring and metrics implementation
  - 🟢 LOW: Documentation and troubleshooting guides

  ---
  🧪 Testing Integration Points

  Test LINK 1: Context Detection

  // server/src/tests/botChainService.test.ts
  describe('Context Detection', () => {
    test('detects follow-up queries', () => {
      const result = detectContextNeeds('תן לי גם תוכן מלא', 'specific_decision', {});
      expect(result.needs_context).toBe(true);
      expect(result.context_type).toBe('follow_up');
    });

    test('detects reference queries', () => {
      const result = detectContextNeeds('מה זה אומר?', 'clarification', {});
      expect(result.needs_context).toBe(true);
      expect(result.context_type).toBe('reference');
    });
  });

  Test LINK 3: SQL Enhancement

  # bot_chain/QUERY_SQL_GEN_BOT_2Q/test_context_enhancement.py
  def test_entity_enhancement_with_context():
      conversation_history = [
          ConversationTurn(
              turn_id="1",
              speaker="user",
              clean_text="מה החלטת הממשלה 2989?",
              timestamp="2025-07-03T10:00:00"
          )
      ]

      entities = {}  # No entities in current query
      enhanced = enhance_entities_with_context(entities, conversation_history)

      assert enhanced["decision_number"] == "2989"

  Test Memory Storage

  # test_memory_integration.py
  def test_memory_storage_integration():
      # Test conversation flow
      response1 = client.post("/route", json={
          "conv_id": "test-conv",
          "current_query": "מה החלטת הממשלה 2989?",
          "intent": "specific_decision",
          "entities": {"decision_number": "2989"},
          "confidence_score": 0.95
      })

      # Check memory storage
      memory_response = client.get("/memory/test-conv")
      assert len(memory_response.json()["history"]) == 2  # User + Bot turn

  ---
  🚨 Critical Implementation Notes

  1. Error Handling at Link Points

  # All bots must handle missing conversation_history gracefully
  def safe_context_access(conversation_history: List[ConversationTurn]) -> Dict:
      """Safely access conversation context with fallback."""
      try:
          if not conversation_history:
              return {"context_available": False}

          # Process context
          return process_conversation_context(conversation_history)
      except Exception as e:
          logger.warning(f"Context processing failed: {e}")
          return {"context_available": False, "error": str(e)}

  2. Backward Compatibility

  # All bot endpoints must remain backward compatible
  @app.post("/generate-sql")
  async def generate_sql(request: SQLGenerationRequest):
      """Generate SQL with optional conversation context."""

      # New requests have conversation_history
      if hasattr(request, 'conversation_history') and request.conversation_history:
          return generate_sql_with_context(request)

      # Legacy requests without conversation context
      return generate_sql_legacy(request)

  3. Performance Considerations

  # Limit conversation history size passed to bots
  def trim_conversation_for_bot(history: List[ConversationTurn], max_turns: int = 5) -> List[ConversationTurn]:
      """Trim conversation history to prevent large payloads."""
      return history[-max_turns:] if len(history) > max_turns else history