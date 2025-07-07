/**
 * HTTP Server wrapper for Intent Detector
 * Provides FastAPI-compatible interface for the deterministic intent detection engine
 */

const express = require('express');
const cors = require('cors');
const IntentDetector = require('./intent_detector.js');

const app = express();
const PORT = process.env.PORT || 8011;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize detector
const detector = new IntentDetector();

// Track start time for health checks
const startTime = new Date();

/**
 * Transform detector output to API-compatible format
 */
function transformToApiFormat(detectorResult, conv_id) {
  // Map new intent types to legacy format for compatibility
  let intent_type = detectorResult.intent_type;
  
  // If it's REFERENCE, we need to map it back to QUERY with special flags
  if (intent_type === 'REFERENCE') {
    intent_type = 'QUERY';
  }
  
  // Build route flags for compatibility
  const route_flags = {
    // Legacy flags for backward compatibility
    needs_clarification: detectorResult.intent_type === 'CLARIFICATION',
    has_context: detectorResult.route_flags.needs_context,
    is_follow_up: detectorResult.route_flags.needs_context,
    // New flags from deterministic engine
    needs_context: detectorResult.route_flags.needs_context,
    is_statistical: detectorResult.route_flags.is_statistical,
    is_comparison: detectorResult.route_flags.is_comparison
  };
  
  // Ensure entities structure is complete
  const entities = {
    government_number: detectorResult.entities.government_number || null,
    decision_number: detectorResult.entities.decision_number || null,
    topic: detectorResult.entities.topic || null,
    date_range: detectorResult.entities.date_range || null,
    ministries: detectorResult.entities.ministries || null,
    count_target: detectorResult.route_flags.is_statistical ? "decisions" : null,
    comparison_target: detectorResult.entities.comparison_target || null,
    limit: detectorResult.entities.limit || null,
    operation: detectorResult.entities.operation || null,
    decision_type: detectorResult.entities.decision_type || null
  };
  
  // Normalize entities for legacy compatibility
  entities.ministries = normalizeMinistries(entities.ministries);
  entities.topic = normalizeTopic(entities.topic);
  
  return {
    conv_id,
    intent_type,
    entities,
    confidence: detectorResult.confidence,
    route_flags,
    timestamp: new Date().toISOString(),
    layer: "1_MAIN_INTENT_BOT",
    token_usage: {
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0,
      model: "deterministic"
    }, // No tokens used in deterministic approach
    explanation: detectorResult.explanation
  };
}

/**
 * Normalize ministries to full form
 */
function normalizeMinistries(ministries) {
  if (!ministries || !Array.isArray(ministries)) return ministries;
  
  return ministries.map(ministry => {
    // If it already starts with "משרד", keep it as is
    if (ministry.startsWith('משרד ')) {
      return ministry;
    }
    // Special cases that don't get "משרד" prefix
    if (ministry === 'ראש הממשלה' || ministry === 'מטה הביטחון הלאומי') {
      return ministry;
    }
    // Add "משרד" prefix
    return `משרד ${ministry}`;
  });
}

/**
 * Normalize topic by removing common prefixes
 */
function normalizeTopic(topic) {
  if (!topic) return topic;
  
  // Remove common prefixes
  const prefixes = ["בנושא", "על", "לגבי"];
  for (const prefix of prefixes) {
    if (topic.startsWith(prefix + " ")) {
      return topic.substring(prefix.length + 1).trim();
    }
  }
  
  return topic;
}

/**
 * Main intent detection endpoint
 */
app.post('/intent', (req, res) => {
  try {
    const { text, conv_id, trace_id, context } = req.body;
    
    if (!text) {
      return res.status(400).json({
        error: "BAD_REQUEST",
        message: "Text field is required",
        timestamp: new Date().toISOString()
      });
    }
    
    if (!conv_id) {
      return res.status(400).json({
        error: "BAD_REQUEST", 
        message: "conv_id field is required",
        timestamp: new Date().toISOString()
      });
    }
    
    // Log request
    console.log(`Intent detection request received`, {
      conv_id,
      trace_id,
      text_length: text.length,
      has_context: !!context
    });
    
    // Detect intent
    const result = detector.detect(text);
    
    // Transform to API format
    const response = transformToApiFormat(result, conv_id);
    
    // Log success
    console.log(`Intent detection completed`, {
      conv_id,
      intent_type: response.intent_type,
      confidence: response.confidence,
      needs_clarification: response.route_flags.needs_clarification
    });
    
    res.json(response);
    
  } catch (error) {
    console.error('Intent detection failed:', error);
    res.status(500).json({
      error: "INTERNAL_SERVER_ERROR",
      message: "Intent detection failed",
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  const uptime = Math.floor((new Date() - startTime) / 1000);
  
  res.json({
    status: "ok",
    layer: "1_MAIN_INTENT_BOT",
    version: "2.0.0",
    uptime_seconds: uptime,
    timestamp: new Date().toISOString()
  });
});

/**
 * Root endpoint
 */
app.get('/', (req, res) => {
  res.json({
    service: "Intent Detector",
    version: "2.0.0",
    status: "running",
    endpoints: ["/intent", "/health"]
  });
});

/**
 * 404 handler
 */
app.use((req, res) => {
  res.status(404).json({
    error: "NOT_FOUND",
    message: `Endpoint ${req.path} not found`,
    timestamp: new Date().toISOString()
  });
});

/**
 * Error handler
 */
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: "INTERNAL_SERVER_ERROR",
    message: "An unexpected error occurred",
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Intent Detector Server running on port ${PORT}`);
  console.log(`Health check available at http://localhost:${PORT}/health`);
  console.log(`Intent detection endpoint at http://localhost:${PORT}/intent`);
});
