import axios from 'axios';
import logger from '../utils/logger';
import { supabase } from '../dal/supabaseClient';
// DISABLED: import crypto from 'crypto';

interface BotChainConfig {
  timeout: number;
  evaluatorTimeout: number;
  enabled: boolean;
  urls: {
    rewrite: string;
    intent: string;
    sqlGen: string;
    contextRouter: string;
    evaluator: string;
    clarify: string;
    ranker: string;
    formatter: string;
  };
}

interface BotChainRequest {
  message: string;
  sessionId: string;
  outputFormat?: string;
  presentationStyle?: string;
  includeMetadata?: boolean;
  includeScores?: boolean;
}

interface BotChainResponse {
  success: boolean;
  response: string;
  metadata?: {
    intent: string;
    entities: Record<string, any>;
    confidence: number;
    evaluation?: {
      overall_score: number;
      relevance_level: string;
      quality_metrics?: any[];
      content_analysis?: any;
      recommendations?: any[];
      confidence?: number;
      explanation?: string;
      processing_time_ms?: number;
      token_usage?: any;
    };
    processing_time_ms: number;
    service: string;
    token_usage?: {
      total_tokens: number;
      prompt_tokens: number;
      completion_tokens: number;
      estimated_cost_usd: number;
      route_type?: string;
      bot_breakdown: Record<string, {
        tokens: number;
        cost_usd: number;
      }>;
    };
    cache_hit?: boolean;
    sessionId?: string;
    session_id?: string;
    engine?: string;
  };
  error?: string;
}

// Context detection interfaces
interface ContextDetectionResult {
  needs_context: boolean;
  context_type: 'follow_up' | 'reference' | 'analysis' | 'none';
  confidence: number;
}

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
  route_flags: RouteFlags;
}

// Token tracking interface
interface TokenUsage {
  bot_name: string;
  tokens: number;
  model: string;
  cost_usd: number;
}

// Cache interfaces
interface CacheEntry {
  response: BotChainResponse;
  timestamp: number;
  hits: number;
}

interface SqlTemplateCache {
  intent: string;
  entities_pattern: string;
  sql_template: string;
  parameters: any[];
  last_used: number;
  usage_count: number;
}

interface IntentPatternCache {
  query_pattern: string;
  intent: string;
  confidence: number;
  last_used: number;
  usage_count: number;
}

class BotChainService {
  private config: BotChainConfig;
  private responseCache: Map<string, CacheEntry> = new Map();
  private sqlTemplateCache: Map<string, SqlTemplateCache> = new Map();
  private intentPatternCache: Map<string, IntentPatternCache> = new Map();
  private tokenUsageHistory: TokenUsage[] = [];
  private sessionEntities: Map<string, any> = new Map(); // Track entities per session
  private readonly CACHE_TTL = 14400000; // 4 hours in milliseconds
  private readonly SQL_CACHE_TTL = 86400000; // 24 hours in milliseconds
  private readonly INTENT_CACHE_TTL = 86400000; // 24 hours in milliseconds
  private readonly MAX_CACHE_SIZE = 100;
  private readonly useUnifiedIntent: boolean;
  private readonly useLLMFormatter: boolean;
  private readonly MODEL_COSTS = {
    'gpt-4o': { prompt: 0.005, completion: 0.015 },         // $5/$15 per 1M tokens
    'gpt-4o-mini': { prompt: 0.00015, completion: 0.0006 }, // $0.15/$0.60 per 1M tokens
    'gpt-4-turbo': { prompt: 0.01, completion: 0.03 },      // per 1K tokens
    'gpt-4': { prompt: 0.03, completion: 0.06 },
    'gpt-3.5-turbo': { prompt: 0.0005, completion: 0.0015 },
    'gpt-3.5-turbo-16k': { prompt: 0.003, completion: 0.004 }
  };

  constructor() {
    // Feature flags for unified architecture
    this.useUnifiedIntent = process.env.USE_UNIFIED_INTENT === 'true';
    this.useLLMFormatter = process.env.USE_LLM_FORMATTER === 'true';
    
    this.config = {
      timeout: parseInt(process.env.BOT_CHAIN_TIMEOUT || '30000'),
      evaluatorTimeout: parseInt(process.env.EVALUATOR_TIMEOUT || '120000'), // 120 seconds for EVALUATOR
      enabled: true, // Always enabled
      urls: {
        rewrite: process.env.REWRITE_BOT_URL || 'http://localhost:8010',
        intent: this.useUnifiedIntent 
          ? (process.env.UNIFIED_INTENT_BOT_URL || 'http://localhost:8011')
          : (process.env.INTENT_BOT_URL || 'http://localhost:8011'),
        sqlGen: process.env.SQL_GEN_BOT_URL || 'http://localhost:8012',
        contextRouter: process.env.CONTEXT_ROUTER_BOT_URL || 'http://localhost:8013',
        evaluator: process.env.EVALUATOR_BOT_URL || 'http://localhost:8014',
        clarify: process.env.CLARIFY_BOT_URL || 'http://localhost:8015',
        ranker: process.env.RANKER_BOT_URL || 'http://localhost:8016',
        formatter: this.useLLMFormatter
          ? (process.env.LLM_FORMATTER_BOT_URL || 'http://localhost:8017')
          : (process.env.FORMATTER_BOT_URL || 'http://localhost:8017')
      }
    };
    
    // Log feature flag status
    logger.info('Bot Chain Feature Flags', {
      useUnifiedIntent: this.useUnifiedIntent,
      useLLMFormatter: this.useLLMFormatter,
      intentUrl: this.config.urls.intent,
      formatterUrl: this.config.urls.formatter
    });

    logger.info('BotChainService initialized', { 
      urls: this.config.urls,
      enabled: this.config.enabled 
    });

    // Start cache cleanup interval
    setInterval(() => this.cleanupCache(), 300000); // Cleanup every 5 minutes
    
    // Start session cleanup interval
    setInterval(() => this.cleanupSessions(), 3600000); // Cleanup every hour
    
    // Start daily spend monitoring
    setInterval(() => this.checkDailySpendLimits(), 600000); // Check every 10 minutes
  }

  // DISABLED: Generate cache key from query
  // private generateCacheKey(message: string): string {
  //   return crypto.createHash('md5').update(message.toLowerCase().trim()).digest('hex');
  // }

  // Clean up expired cache entries
  private cleanupCache(): void {
    const now = Date.now();
    let cleaned = 0;
    
    // Clean response cache
    for (const [key, entry] of this.responseCache.entries()) {
      if (now - entry.timestamp > this.CACHE_TTL) {
        this.responseCache.delete(key);
        cleaned++;
      }
    }
    
    // Clean SQL template cache
    for (const [key, template] of this.sqlTemplateCache.entries()) {
      if (now - template.last_used > this.SQL_CACHE_TTL) { // 24 hours for SQL templates
        this.sqlTemplateCache.delete(key);
        cleaned++;
      }
    }
    
    // Clean intent pattern cache
    for (const [key, pattern] of this.intentPatternCache.entries()) {
      if (now - pattern.last_used > this.INTENT_CACHE_TTL) { // 24 hours for intent patterns
        this.intentPatternCache.delete(key);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      logger.info(`Cache cleanup: removed ${cleaned} expired entries`);
    }
  }

  // Clean up old session entity tracking data
  private cleanupSessions(): void {
    const now = Date.now();
    const SESSION_TTL = 7200000; // 2 hours
    let cleaned = 0;
    
    // Note: This is a simple implementation. In production, you'd want to track
    // last access time for each session
    for (const [sessionId, _entities] of this.sessionEntities.entries()) {
      // For now, we'll clean up sessions that have no recent cache entries
      let hasRecentActivity = false;
      
      for (const [_key, entry] of this.responseCache.entries()) {
        if (entry.response.metadata?.sessionId === sessionId && 
            now - entry.timestamp < SESSION_TTL) {
          hasRecentActivity = true;
          break;
        }
      }
      
      if (!hasRecentActivity) {
        this.sessionEntities.delete(sessionId);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      logger.info(`Session cleanup: removed ${cleaned} inactive sessions`);
    }
  }

  // Response cache SAFELY RESTORED with entity safety checks
  private checkResponseCache(message: string): CacheEntry | null {
    // SAFETY CHECK: Never cache responses for queries with specific entity numbers
    if (this.containsSpecificEntities(message)) {
      logger.info('Skipping response cache for specific entities', { message });
      return null;
    }
    
    const key = this.generateCacheKey(message);
    const cached = this.responseCache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      cached.hits++;
      logger.info('Cache hit', { message, hits: cached.hits });
      return cached;
    }
    
    return null;
  }

  // Store in response cache SAFELY RESTORED with entity safety checks
  private storeInCache(message: string, response: BotChainResponse): void {
    // SAFETY CHECK: Never cache responses for queries with specific entity numbers
    if (this.containsSpecificEntities(message)) {
      logger.info('Skipping response storage for specific entities', { message });
      return;
    }
    
    const key = this.generateCacheKey(message);
    
    // Limit cache size
    if (this.responseCache.size >= this.MAX_CACHE_SIZE) {
      const oldestKey = Array.from(this.responseCache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp)[0][0];
      this.responseCache.delete(oldestKey);
    }
    
    this.responseCache.set(key, {
      response,
      timestamp: Date.now(),
      hits: 0
    });
  }

  // Cache invalidation for conversation context changes
  private invalidateConversationCache(sessionId: string): void {
    // Invalidate all cached responses for this conversation
    let invalidated = 0;
    
    for (const [key, entry] of this.responseCache.entries()) {
      // Check if the cached response belongs to this session
      if (entry.response.metadata?.sessionId === sessionId) {
        this.responseCache.delete(key);
        invalidated++;
      }
    }
    
    if (invalidated > 0) {
      logger.info(`Invalidated ${invalidated} cache entries for session ${sessionId}`);
    }
  }

  // Invalidate cache when entities significantly change
  private checkEntityChangesAndInvalidate(
    sessionId: string,
    previousEntities: any,
    currentEntities: any
  ): void {
    // Check if critical entities have changed
    const criticalEntityKeys = ['decision_number', 'government_number', 'topic'];
    
    for (const key of criticalEntityKeys) {
      if (previousEntities[key] !== currentEntities[key]) {
        logger.info('Critical entity change detected, invalidating cache', {
          sessionId,
          entityKey: key,
          oldValue: previousEntities[key],
          newValue: currentEntities[key]
        });
        this.invalidateConversationCache(sessionId);
        return;
      }
    }
  }

  // Track token usage
  private trackTokenUsage(botName: string, tokens: number, model: string): void {
    const costs = this.MODEL_COSTS[model as keyof typeof this.MODEL_COSTS] || this.MODEL_COSTS['gpt-3.5-turbo'];
    const cost = (tokens / 1000) * ((costs.prompt + costs.completion) / 2); // Average of prompt and completion
    
    const usage: TokenUsage = {
      bot_name: botName,
      tokens,
      model,
      cost_usd: cost
    };
    
    this.tokenUsageHistory.push(usage);
    
    // Keep only last 1000 entries
    if (this.tokenUsageHistory.length > 1000) {
      this.tokenUsageHistory = this.tokenUsageHistory.slice(-1000);
    }
    
    logger.info('Token usage tracked', usage);
  }

  // Get token usage summary for all history
  private getTokenUsageSummary(): NonNullable<BotChainResponse['metadata']>['token_usage'] {
    const botBreakdown: Record<string, { tokens: number; cost_usd: number }> = {};
    let totalTokens = 0;
    let totalCost = 0;
    
    // Aggregate by bot
    for (const usage of this.tokenUsageHistory) {
      if (!botBreakdown[usage.bot_name]) {
        botBreakdown[usage.bot_name] = { tokens: 0, cost_usd: 0 };
      }
      botBreakdown[usage.bot_name].tokens += usage.tokens;
      botBreakdown[usage.bot_name].cost_usd += usage.cost_usd;
      totalTokens += usage.tokens;
      totalCost += usage.cost_usd;
    }
    
    return {
      total_tokens: totalTokens,
      prompt_tokens: Math.floor(totalTokens * 0.4), // Estimate
      completion_tokens: Math.floor(totalTokens * 0.6), // Estimate
      estimated_cost_usd: totalCost,
      bot_breakdown: botBreakdown
    };
  }

  // Determine route type based on intent and flow
  private getRouteType(intent: string, needs_clarification: boolean): string {
    if (needs_clarification) {
      return 'CLARIFY';
    }
    if (intent === 'ANALYSIS' || intent === 'analysis' || intent.includes('EVAL')) {
      return 'EVAL';
    }
    if (intent === 'RESULT_REF' || intent.includes('reference')) {
      return 'QUERY_CONTEXT';
    }
    if (intent === 'DECISION_GUIDE') {
      return 'DECISION_GUIDE';
    }
    return 'QUERY';
  }

  // Get token usage summary for current request only
  private getCurrentRequestTokenSummary(currentRequestTokens: TokenUsage[], routeType?: string): NonNullable<BotChainResponse['metadata']>['token_usage'] {
    const botBreakdown: Record<string, { tokens: number; cost_usd: number }> = {};
    let totalTokens = 0;
    let totalCost = 0;
    let promptTokens = 0;
    let completionTokens = 0;
    
    // Aggregate by bot for current request
    for (const usage of currentRequestTokens) {
      if (!botBreakdown[usage.bot_name]) {
        botBreakdown[usage.bot_name] = { tokens: 0, cost_usd: 0 };
      }
      botBreakdown[usage.bot_name].tokens += usage.tokens;
      botBreakdown[usage.bot_name].cost_usd += usage.cost_usd;
      totalTokens += usage.tokens;
      totalCost += usage.cost_usd;
    }
    
    // Better estimation based on typical GPT usage
    promptTokens = Math.floor(totalTokens * 0.4);
    completionTokens = totalTokens - promptTokens;
    
    const result: any = {
      total_tokens: totalTokens,
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      estimated_cost_usd: totalCost,
      bot_breakdown: botBreakdown
    };
    
    if (routeType) {
      result.route_type = routeType;
    }
    
    return result;
  }

  // Check daily spend and alert if approaching limits
  private checkDailySpendLimits(): void {
    const now = Date.now();
    const dayStart = now - (now % 86400000); // Start of current day
    
    let dailyCost = 0;
    let dailyTokens = 0;
    
    for (const usage of this.tokenUsageHistory) {
      // Estimate timestamp if not available (using current time - index)
      const estimatedTimestamp = now - (this.tokenUsageHistory.length - this.tokenUsageHistory.indexOf(usage)) * 60000;
      if (estimatedTimestamp >= dayStart) {
        dailyCost += usage.cost_usd;
        dailyTokens += usage.tokens;
      }
    }
    
    const DAILY_BUDGET = 10; // $10 daily budget
    
    // Alert at 80% of daily budget
    if (dailyCost >= DAILY_BUDGET * 0.8) {
      logger.warn('Daily spend approaching limit', { 
        daily_cost: dailyCost,
        daily_budget: DAILY_BUDGET,
        percentage_used: (dailyCost / DAILY_BUDGET) * 100,
        daily_tokens: dailyTokens
      });
    }
    
    // Alert if exceeded daily budget
    if (dailyCost >= DAILY_BUDGET) {
      logger.error('Daily spend limit exceeded', { 
        daily_cost: dailyCost,
        daily_budget: DAILY_BUDGET,
        daily_tokens: dailyTokens
      });
    }
    
    logger.info('Daily spend check', { 
      daily_cost: dailyCost,
      daily_budget: DAILY_BUDGET,
      percentage_used: (dailyCost / DAILY_BUDGET) * 100,
      daily_tokens: dailyTokens
    });
  }

  // Normalize query for pattern matching - SAFELY RESTORED
  private normalizeQueryPattern(query: string): string {
    return query
      .toLowerCase()
      .replace(/\d+/g, '#') // Replace numbers with # for safe pattern matching
      .replace(/[\u0590-\u05FF]+/g, 'HEB') // Replace Hebrew with HEB
      .replace(/[^\w\s#]/g, '') // Remove punctuation
      .trim();
  }

  // Intent pattern cache SAFELY RESTORED - only caches patterns, not specific entities
  private checkIntentPatternCache(query: string): IntentPatternCache | null {
    const pattern = this.normalizeQueryPattern(query);
    
    // SAFETY CHECK: Skip caching if query contains specific entity numbers
    if (this.containsSpecificEntities(query)) {
      logger.info('Skipping pattern cache for specific entities', { query });
      return null;
    }
    
    const cached = this.intentPatternCache.get(pattern);
    
    if (cached && Date.now() - cached.last_used < this.INTENT_CACHE_TTL) {
      cached.usage_count++;
      cached.last_used = Date.now();
      logger.info('Intent pattern cache hit', { pattern, usage_count: cached.usage_count });
      return cached;
    }
    
    return null;
  }

  // Store in intent pattern cache SAFELY RESTORED - only caches patterns, not specific entities
  private storeIntentPattern(query: string, intent: string, confidence: number): void {
    const pattern = this.normalizeQueryPattern(query);
    
    // SAFETY CHECK: Never cache queries with specific entity numbers
    if (this.containsSpecificEntities(query)) {
      logger.info('Skipping pattern storage for specific entities', { query });
      return;
    }
    
    // Limit cache size
    if (this.intentPatternCache.size >= this.MAX_CACHE_SIZE) {
      const oldestKey = Array.from(this.intentPatternCache.entries())
        .sort((a, b) => a[1].last_used - b[1].last_used)[0][0];
      this.intentPatternCache.delete(oldestKey);
    }
    
    this.intentPatternCache.set(pattern, {
      query_pattern: pattern,
      intent,
      confidence,
      last_used: Date.now(),
      usage_count: 1
    });
    
    logger.info('Intent pattern cached', { pattern, intent });
  }

  // Generate cache key for response cache - SAFELY RESTORED
  private generateCacheKey(message: string): string {
    return Buffer.from(message.toLowerCase().trim()).toString('base64');
  }

  // SAFETY CHECK: Detect if query contains specific entity numbers that should not be cached
  private containsSpecificEntities(query: string): boolean {
    // Check for government numbers (e.g., "ממשלה 37", "ממשלה 276")
    if (/ממשלה\s*\d+/.test(query)) {
      return true;
    }
    
    // Check for decision numbers (e.g., "החלטה 2989", "הח' 1234")
    if (/החלטה\s*\d+|הח['"]?\s*\d+/.test(query)) {
      return true;
    }
    
    // Check for specific years or dates that might be sensitive
    if (/20\d{2}|19\d{2}/.test(query)) {
      return true;
    }
    
    // Check for count queries (e.g., "כמה החלטות")
    if (/כמה/.test(query)) {
      return true;
    }
    
    // Check for direct numeric entity patterns
    if (/\d{3,}/.test(query)) { // Any number with 3+ digits
      return true;
    }
    
    // Check for reference words that depend on context
    if (/זה|זו|זאת|האחרון|הקודם|הנ"ל|שאמרת|ההחלטה|אותה/.test(query)) {
      return true;
    }
    
    // Check for ordinal references (e.g., "השני", "הראשון")
    if (/הראשון|השני|השלישי|הרביעי|החמישי/.test(query)) {
      return true;
    }
    
    // Check for "full content" requests which often relate to previous queries
    if (/תוכן\s*מלא|התוכן\s*המלא|פרטים\s*נוספים/.test(query)) {
      return true;
    }
    
    return false;
  }

  // Step 2.2: Smart Context Router activation logic
  private shouldCallContextRouter(query: string, intent: string, entities: any, contextDetection: ContextDetectionResult): boolean {
    // Always call for clarification intents
    if (intent === 'CLARIFICATION' || intent === 'UNCLEAR') {
      return true;
    }
    
    // Always call for RESULT_REF intent (requires conversation history)
    if (intent === 'RESULT_REF') {
      return true;
    }
    
    // Always call if context is detected
    if (contextDetection.needs_context) {
      return true;
    }
    
    // Skip for direct queries with complete entity sets
    // Example: "החלטה 2766" - has decision number, no context needed
    if (entities.decision_number && entities.government_number) {
      return false;
    }
    
    // Skip for simple direct searches with clear intent
    // Example: "החלטות ממשלה 37" - clear government search
    if (intent === 'QUERY' && entities.government_number && !entities.decision_number) {
      return false;
    }
    
    // Skip for topic-only searches
    // Example: "החלטות על חינוך" - clear topic search
    if (intent === 'QUERY' && entities.topic && !this.hasReferenceWords(query)) {
      return false;
    }
    
    // Skip for ministry-only searches
    // Example: "החלטות משרד הבריאות"
    if (intent === 'QUERY' && entities.ministries && entities.ministries.length > 0 && !this.hasReferenceWords(query)) {
      return false;
    }
    
    // Default: call Context Router for ambiguous cases
    return true;
  }
  
  // Helper function to detect reference words
  private hasReferenceWords(query: string): boolean {
    const referencePatterns = ['זה', 'זו', 'זאת', 'האחרון', 'הקודם', 'הנ"ל', 'שאמרת', 'ההחלטה', 'אותה'];
    return referencePatterns.some(pattern => query.includes(pattern));
  }

  // Step 2.1: Smart EVALUATOR activation logic
  private shouldRunEvaluator(intent: string, entities: any, results: any[]): boolean {
    // Must be EVAL or ANALYSIS intent (unified intent bot returns ANALYSIS)
    if (intent !== 'EVAL' && intent !== 'ANALYSIS') {
      return false;
    }
    
    // Must have results to analyze
    if (!results || results.length === 0) {
      return false;
    }
    
    // Case 1: User specified exact decision number - always run
    if (entities.decision_number) {
      return true;
    }
    
    // Case 2: Single result from search - can analyze
    if (results.length === 1) {
      return true;
    }
    
    // Case 3: Multiple results without specific decision - DON'T analyze
    // Examples: "נתח החלטות חינוך", "נתח החלטות ממשלה 37"
    if (results.length > 1) {
      logger.info('Multiple results without specific decision - skipping EVALUATOR', {
        result_count: results.length,
        entities
      });
      return false;
    }
    
    return false;
  }

  // Step 3.1: Multi-tier model selection for EVALUATOR
  private selectEvaluatorModel(contentLength: number): { model: string; maxTokens: number; tier: string } {
    if (contentLength < 800) {
      return {
        model: 'skip', // Too short for analysis
        maxTokens: 0,
        tier: 'too_short'
      };
    } else if (contentLength < 1400) {
      return {
        model: 'gpt-3.5-turbo',
        maxTokens: 2000,
        tier: 'short_content'
      };
    } else if (contentLength < 4000) {
      return {
        model: 'gpt-3.5-turbo',
        maxTokens: 4000,
        tier: 'medium_content'
      };
    } else if (contentLength < 6000) {
      return {
        model: 'gpt-3.5-turbo',
        maxTokens: 4000,
        tier: 'long_content'
      };
    } else {
      return {
        model: 'gpt-4-turbo',
        maxTokens: 8000,
        tier: 'complex_content'
      };
    }
  }

  // Content validation for EVALUATOR - Step 1.3 implementation  
  private validateContentForEvaluation(result: any): { suitable: boolean; reason: string; details: string; contentLength: number } {
    const content = result.decision_content || result.summary || '';
    const title = result.decision_title || '';
    
    // Check 1: Minimum content length (800 characters for multi-tier analysis)
    if (content.length < 800) {
      return {
        suitable: false,
        reason: 'תוכן קצר מדי',
        details: `תוכן בן ${content.length} תווים, נדרש מינימום 800 תווים לניתוח מעמיק`,
        contentLength: content.length
      };
    }
    
    // Check 2: Basic Hebrew text validation
    const hebrewRegex = /[\u0590-\u05FF]/;
    if (!hebrewRegex.test(content) && !hebrewRegex.test(title)) {
      return {
        suitable: false,
        reason: 'אין תוכן בעברית',
        details: 'הניתוח מותאם לתוכן בעברית בלבד',
        contentLength: content.length
      };
    }
    
    // Check 3: Very long content handling - ALLOW long content since these are prime candidates for analysis
    // Long decisions are exactly what users want to analyze deeply
    // The extended 120s timeout should handle most long content cases
    
    // Check 4: Check for empty or placeholder content
    const placeholderPatterns = [
      /^ללא תוכן/i,
      /^לא זמין/i,
      /^N\/A$/i,
      /^-$/,
      /^\s*$/
    ];
    
    if (placeholderPatterns.some(pattern => pattern.test(content.trim()))) {
      return {
        suitable: false,
        reason: 'תוכן ריק או זמין',
        details: 'התוכן אינו מכיל מידע מספק לניתוח',
        contentLength: content.length
      };
    }
    
    // Content is suitable for evaluation
    return {
      suitable: true,
      reason: 'מתאים לניתוח',
      details: `תוכן בן ${content.length} תווים עובר את כל בדיקות האיכות`,
      contentLength: content.length
    };
  }

  // Context detection function (LINK 1 implementation)
  private detectContextNeeds(query: string, intent: string, entities: any): ContextDetectionResult {
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

  // Determine if query is simple enough to skip expensive bots
  private isSimpleQuery(intent: string, entities: any, confidence: number): boolean {
    // High confidence queries with specific patterns are simple
    if (confidence > 0.8) {
      // Simple search patterns
      if (intent === 'QUERY' && entities.topic && !entities.date_range && !entities.ministries) {
        return true;
      }
      
      // Direct government number queries
      if (intent === 'QUERY' && entities.government_number && !entities.complex_filters) {
        return true;
      }
      
      // Specific decision lookups
      if (intent === 'QUERY' && entities.government_number && entities.decision_number) {
        return true;
      }
      
      // Count queries
      if (intent === 'STATISTICAL') {
        return true;
      }
    }
    
    // Recent decisions queries
    if (intent === 'QUERY' && (!entities.topic || entities.recent)) {
      return true;
    }
    
    // EVAL is never simple - always needs full processing
    if (intent === 'EVAL') {
      return false;
    }
    
    return false;
  }

  async checkHealth(): Promise<boolean> {
    try {
      // Check intent bot as a representative health check
      const intentUrl = this.useUnifiedIntent ? this.config.urls.intent : this.config.urls.sqlGen;
      const response = await axios.get(`${intentUrl}/health`, {
        timeout: 5000
      });
      return response.status === 200 && response.data?.status === 'ok';
    } catch (error) {
      logger.error('Bot chain health check failed', { error: error instanceof Error ? error.message : String(error) });
      return false;
    }
  }

  // תיקון לפונקציה callBot בקובץ botChainService.ts
// מחליף את החלק שבודק token_usage

  private async callBot(url: string, endpoint: string, data: any, currentRequestTokens?: TokenUsage[], customTimeout?: number): Promise<any> {
    const fullUrl = `${url}${endpoint}`;
    try {
      logger.info(`Calling bot: ${fullUrl}`, { data });
      const response = await axios.post(fullUrl, data, {
        timeout: customTimeout || this.config.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      logger.info(`Bot response from ${fullUrl}`, { 
        status: response.status,
        data: response.data 
      });
      
      // Track token usage if available in response
      // תיקון: בדיקה של token_usage בכמה מקומות אפשריים
      let tokenUsageData = null;
      let model = 'gpt-3.5-turbo'; // ברירת מחדל
      
      // Option 1: token_usage at top level (REWRITE, INTENT, SQL_GEN)
      if (response.data.token_usage) {
        tokenUsageData = response.data.token_usage;
        model = tokenUsageData.model || response.data.model || model;
      }
      // Option 2: token_usage inside evaluation (EVALUATOR)
      else if (response.data.evaluation && response.data.evaluation.token_usage) {
        tokenUsageData = response.data.evaluation.token_usage;
        model = tokenUsageData.model || model;
      }
      // Option 3: Check for usage field (some bots might use this)
      else if (response.data.usage) {
        tokenUsageData = response.data.usage;
        model = response.data.model || model;
      }
      
      // If token usage found, track it
      if (tokenUsageData && tokenUsageData.total_tokens) {
        const botName = endpoint.replace('/', '').toUpperCase();
        const tokens = tokenUsageData.total_tokens || 0;
        
        // Use bot-provided cost if available, otherwise calculate
        let cost = tokenUsageData.cost_usd;
        if (!cost && cost !== 0) {
          const costs = this.MODEL_COSTS[model as keyof typeof this.MODEL_COSTS] || this.MODEL_COSTS['gpt-3.5-turbo'];
          cost = (tokens / 1000) * ((costs.prompt + costs.completion) / 2);
        }
        
        // Track globally for history
        this.trackTokenUsage(botName, tokens, model);
        
        // Track for current request if array provided
        if (currentRequestTokens) {
          currentRequestTokens.push({
            bot_name: botName,
            tokens,
            model,
            cost_usd: cost
          });
        }
        
        logger.debug('Token usage found in response', {
          bot: botName,
          tokens,
          model,
          tokenUsageData: tokenUsageData,
          source: tokenUsageData === response.data.token_usage ? 'top-level' : 
                  tokenUsageData === response.data.evaluation?.token_usage ? 'evaluation' : 
                  'usage'
        });
      } else {
        // Log when no token usage found
        logger.debug('No token usage found in response', {
          bot: endpoint.replace('/', '').toUpperCase(),
          responseKeys: Object.keys(response.data),
          hasEvaluation: !!response.data.evaluation,
          evaluationKeys: response.data.evaluation ? Object.keys(response.data.evaluation) : []
        });
      }
      
      return response.data;
    } catch (error) {
      logger.error(`Bot call failed: ${fullUrl}`, { 
        error: error instanceof Error ? error.message : String(error), 
        data,
        response: (error as any).response?.data,
        status: (error as any).response?.status
      });
      throw error;
    }
  }

  async processQuery(request: BotChainRequest): Promise<BotChainResponse> {
    const startTime = Date.now();
    const currentRequestTokens: TokenUsage[] = []; // Track tokens for current request only
    
    // Use consistent conversation ID throughout the entire bot chain
    const conversationId = request.sessionId || `temp_${Date.now()}`;
    
    try {
      logger.info('Processing query with bot chain', { 
        sessionId: request.sessionId,
        conversationId: conversationId,
        messageLength: request.message.length 
      });
      
      // Check response cache first (with safety checks for specific entities)
      const cachedResponse = this.checkResponseCache(request.message);
      if (cachedResponse) {
        logger.info('Returning cached response', { 
          sessionId: request.sessionId,
          cache_hits: cachedResponse.hits 
        });
        return cachedResponse.response;
      }

      // NEW UNIFIED FLOW: Use the unified intent bot if enabled
      
      let cleanText: string;
      let intent: string, entities: any, confidence: number;
      let routeFlags: any = {};
      
      if (this.useUnifiedIntent) {
        // NEW FLOW: Single call to unified intent bot
        logger.info('Using unified intent bot (GPT-4o-turbo)', { 
          conversationId,
          messageLength: request.message.length 
        });
        
        const unifiedResponse = await this.callBot(this.config.urls.intent, '/intent', {
          raw_user_text: request.message,
          chat_history: [], // TODO: Add conversation history
          conv_id: conversationId
        }, currentRequestTokens);
        
        logger.info('Unified intent response received', { 
          response: unifiedResponse,
          hasCleanQuery: !!unifiedResponse.clean_query,
          intent: unifiedResponse.intent
        });
        
        // Extract fields from unified response
        cleanText = unifiedResponse.clean_query;
        intent = unifiedResponse.intent || unifiedResponse.intent_type;
        entities = unifiedResponse.params || unifiedResponse.entities || {};
        confidence = unifiedResponse.confidence;
        routeFlags = unifiedResponse.route_flags || {};
        
        // Log clean query for telemetry
        logger.info('Query normalized by unified bot', { 
          original: request.message, 
          clean: cleanText,
          corrections: unifiedResponse.corrections?.length || 0
        });
        
      } else {
        // OLD FLOW: Separate rewrite and intent detection
        // Step 1: Text Rewrite
        const rewriteResponse = await this.callBot(this.config.urls.rewrite, '/rewrite', {
          text: request.message,
          conv_id: conversationId
        }, currentRequestTokens);

        logger.info('Rewrite response received', { 
          response: rewriteResponse,
          hasCleanText: !!rewriteResponse.clean_text 
        });

        // Check if we got a valid response with clean_text
        if (!rewriteResponse.clean_text) {
          throw new Error('Rewrite step failed - no clean text returned');
        }

        cleanText = rewriteResponse.clean_text;
        logger.debug('Text rewrite completed', { original: request.message, clean: cleanText });

        // Step 2: Intent Detection with safe pattern caching
      
        // Check intent pattern cache first (safe for non-specific entity queries)
        const cachedIntent = this.checkIntentPatternCache(cleanText);
        if (cachedIntent) {
          intent = cachedIntent.intent;
          confidence = cachedIntent.confidence;
          entities = {}; // Safe: Use empty entities for cached patterns
          logger.info('Using cached intent pattern', { intent, confidence });
        } else {
          // Call intent bot for fresh detection
          const intentResponse = await this.callBot(this.config.urls.intent, '/intent', {
            text: cleanText,
            conv_id: conversationId
          }, currentRequestTokens);

          // Check if we got a valid intent response
          if ((!intentResponse.intent_type && !intentResponse.intent) || !intentResponse.entities) {
            throw new Error('Intent detection failed - invalid response');
          }

          intent = intentResponse.intent_type || intentResponse.intent;
          entities = intentResponse.entities;
          confidence = intentResponse.confidence;
          
          // TEMPORARY WORKAROUND: Extract date range if intent detector missed it
          if (!entities.date_range && cleanText.includes('בין') && cleanText.includes('ל־')) {
            const dateRangeMatch = cleanText.match(/בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/);
            if (dateRangeMatch) {
              entities.date_range = {
                start: `${dateRangeMatch[1]}-01-01`,
                end: `${dateRangeMatch[2]}-12-31`
              };
              logger.info('Date range extracted via workaround', { date_range: entities.date_range });
            }
          }
          
          // Store in intent pattern cache (with safety checks)
          this.storeIntentPattern(cleanText, intent, confidence);
        }
      }
      
      // NOTE: Government 37 defaulting for decision-number-only queries is handled in SQL templates

      logger.debug('Intent detection completed', { intent, entities, confidence });

      // Track entity changes for cache invalidation
      const previousEntities = this.sessionEntities.get(conversationId) || {};
      this.checkEntityChangesAndInvalidate(conversationId, previousEntities, entities);
      this.sessionEntities.set(conversationId, { ...entities }); // Store copy of entities

      // Intelligent bot activation based on query complexity
      const isSimpleQuery = this.isSimpleQuery(intent, entities, confidence);
      const shouldSkipExpensiveBots = isSimpleQuery && process.env.SMART_ROUTING !== 'false';
      
      if (shouldSkipExpensiveBots) {
        logger.info('Simple query detected - using fast track processing', { 
          intent, confidence, entities 
        });
      }

      // Step 3: Context Routing with Memory Integration (LINK 1)
      const contextDetection = this.detectContextNeeds(cleanText, intent, entities);
      
      let route = 'direct';
      let needs_clarification = false;
      let clarification_type = null;
      let routingResponse: any = null;

      // Step 2.2: Smart Context Router usage - only call when needed
      const shouldCallContextRouter = this.shouldCallContextRouter(cleanText, intent, entities, contextDetection);
      
      if (shouldCallContextRouter) {
        logger.info('Context Router needed - calling for conversation management', { 
          context_type: contextDetection.context_type,
          confidence: contextDetection.confidence,
          needs_context: contextDetection.needs_context
        });
        
        const routingRequest: ContextRequest = {
          conv_id: conversationId,
          current_query: cleanText,
          intent,
          entities,
          confidence_score: confidence,
          route_flags: routeFlags.needs_context ? routeFlags : {
            needs_context: contextDetection.needs_context,
            context_type: contextDetection.context_type,
            context_confidence: contextDetection.confidence
          }
        };

        routingResponse = await this.callBot(this.config.urls.contextRouter, '/route', routingRequest, currentRequestTokens);

        // Check if routing response is valid
        if (!routingResponse || !routingResponse.route) {
          throw new Error('Context routing failed - invalid response');
        }

        route = routingResponse.route;
        needs_clarification = routingResponse.needs_clarification;
        clarification_type = routingResponse.clarification_type;
        
        // Use resolved entities if reference resolution occurred
        if (routingResponse.resolved_entities) {
          logger.info('Using resolved entities from context router', {
            originalEntities: entities,
            resolvedEntities: routingResponse.resolved_entities,
            enrichedQuery: routingResponse.enriched_query
          });
          entities = routingResponse.resolved_entities;
        }
        
        // Use enriched query if available
        if (routingResponse.enriched_query && routingResponse.enriched_query !== cleanText) {
          logger.info('Using enriched query from reference resolution', {
            originalQuery: cleanText,
            enrichedQuery: routingResponse.enriched_query
          });
          cleanText = routingResponse.enriched_query;
        }
      } else {
        logger.info('Skipping Context Router - direct query with complete entities', {
          intent,
          has_all_entities: true,
          is_contextual: false
        });
        
        // Default routing for non-contextual queries
        route = 'direct';
        needs_clarification = false;
        clarification_type = null;
      }

      logger.debug('Context routing completed', { route, needs_clarification });

      // Check if intent itself is CLARIFICATION or UNCLEAR
      if (intent === 'CLARIFICATION' || intent === 'UNCLEAR') {
        needs_clarification = true;
        clarification_type = intent === 'UNCLEAR' ? 'unclear_query' : 'low_confidence';
        logger.info(`${intent} intent detected - triggering clarify bot`);
      }

      // Handle clarification needed
      if (needs_clarification) {
        const clarifyResponse = await this.callBot(this.config.urls.clarify, '/clarify', {
          conv_id: conversationId,
          original_query: request.message,
          intent,
          entities,
          confidence_score: confidence,
          clarification_type
        }, currentRequestTokens);

        // Check if clarify response is valid
        if (!clarifyResponse || !clarifyResponse.clarification_questions) {
          throw new Error('Clarification generation failed - invalid response');
        }

        const questions = clarifyResponse.clarification_questions;
        const suggestions = clarifyResponse.suggested_refinements;

        // Format clarification response
        let clarificationText = "אני זקוק לפרטים נוספים כדי לעזור לך:\n\n";
        
        questions.forEach((q: any, index: number) => {
          clarificationText += `${index + 1}. ${q.question}\n`;
          if (q.suggestions && q.suggestions.length > 0) {
            clarificationText += `   אפשרויות: ${q.suggestions.join(', ')}\n`;
          }
        });

        if (suggestions.length > 0) {
          clarificationText += "\nהצעות לשיפור השאילתא:\n";
          suggestions.forEach((suggestion: string) => {
            clarificationText += `• ${suggestion}\n`;
          });
        }

        const processingTime = Date.now() - startTime;
        return {
          success: true,
          response: clarificationText,
          metadata: {
            intent,
            entities,
            confidence,
            processing_time_ms: processingTime,
            service: 'bot-chain-clarification',
            token_usage: this.getCurrentRequestTokenSummary(currentRequestTokens)
          }
        };
      }

      // Handle Decision Guide intent
      if (intent === 'DECISION_GUIDE') {
        logger.info('DECISION_GUIDE intent detected - returning guidance response');
        
        const guidanceText = `ברוך הבא למדריך ניסוח החלטות הממשלה! 🎯

אני כאן כדי לעזור לך לנסח החלטת ממשלה איכותית וישימה.

כדי להתחיל, לחץ על הכפתור "צריך עזרה בניסוח החלטה" שמופיע בממשק הראשי.

שם תוכל:
📄 להעלות קובץ PDF של טיוטת ההחלטה
✏️ או להדביק את הטקסט ישירות

אני אנתח את הטיוטה שלך על פי 13 קריטריונים חשובים:
• לוחות זמנים מחייבים
• צוות מתכלל וגורם אחראי
• מנגנוני דיווח ובקרה
• משאבים נדרשים
• ועוד...

תקבל ציון מפורט לכל קריטריון (1-10) יחד עם המלצות ספציפיות לשיפור.

💡 טיפ: ההחלטות הטובות ביותר כוללות יעדים ברורים, לוחות זמנים מוגדרים, ותקציב מפורט.`;

        const processingTime = Date.now() - startTime;
        return {
          success: true,
          response: guidanceText,
          metadata: {
            intent,
            entities,
            confidence,
            processing_time_ms: processingTime,
            service: 'bot-chain-decision-guide',
            token_usage: this.getCurrentRequestTokenSummary(currentRequestTokens, 'DECISION_GUIDE')
          }
        };
      }

      // Step 4: SQL Generation with Context Support (LINK 3)
      let sqlResponse;
      
      // Prepare SQL generation request with context if available
      const sqlGenRequest: any = {
        intent,
        entities,
        conv_id: conversationId
      };
      
      // Add conversation history if context was detected
      if (contextDetection.needs_context && routingResponse && routingResponse.conversation_history) {
        sqlGenRequest.conversation_history = routingResponse.conversation_history;
        sqlGenRequest.context_summary = {
          total_turns: routingResponse.conversation_history.length,
          last_query: cleanText,
          context_type: contextDetection.context_type
        };
        logger.info('Adding conversation history to SQL request', {
          conversationId,
          historyLength: routingResponse.conversation_history.length,
          contextType: contextDetection.context_type
        });
      } else if (contextDetection.needs_context && !routingResponse) {
        // This shouldn't happen now that RESULT_REF always goes through context router
        logger.warn('Context needed but no routing response available', {
          conversationId,
          intent,
          contextType: contextDetection.context_type
        });
      }
      
      // Call SQL generation bot
      sqlResponse = await this.callBot(this.config.urls.sqlGen, '/sqlgen', sqlGenRequest, currentRequestTokens);

      // Log the SQL response for debugging
      logger.info('SQL bot response details', { 
        hasResponse: !!sqlResponse,
        hasSqlQuery: !!sqlResponse?.sql_query,
        responseKeys: sqlResponse ? Object.keys(sqlResponse) : [],
        sqlResponse
      });
      
      // DEBUG: Log the exact parameters from SQL bot
      logger.error('DEBUG SQL bot parameters analysis', {
        parameters: sqlResponse.parameters,
        parameterTypes: sqlResponse.parameters ? sqlResponse.parameters.map((p: any) => ({name: p.name, value: p.value, type: typeof p.value})) : [],
        originalEntities: entities
      });

      // Check if SQL response is valid
      if (!sqlResponse || !sqlResponse.sql_query) {
        throw new Error('SQL generation failed - invalid response');
      }
      
      // FORCE ERROR TO TEST IF CODE IS RUNNING
      console.log('🔥🔥🔥 CODE IS RUNNING - ABOUT TO PROCESS SQL RESPONSE 🔥🔥🔥');

      // const sql = sqlResponse.sql_query; // Not used after removing evaluator
      const template_used = sqlResponse.template_used;
      const parameters = sqlResponse.parameters || [];
      
      // Execute the SQL query
      let results: any[] = [];
      // Check for requested limit in entities
      const requestedLimit = entities.limit || 10;
      try {
        console.log('🚨 ENTERING SQL EXECUTION BLOCK - THIS SHOULD ALWAYS SHOW!');
        // Convert parameters from array to object for easier access
        const sqlParams: Record<string, any> = {};
        parameters.forEach((param: any) => {
          sqlParams[param.name] = param.value;
        });
        
        // NOTE: government_number is set correctly by SQL bot templates when needed
        
        // DEBUG: Log the conversion and filtering
        logger.error('🔧 DEBUG sqlParams conversion', {
          originalParameters: parameters,
          convertedSqlParams: sqlParams,
          governmentNumberValue: sqlParams.government_number,
          governmentNumberType: typeof sqlParams.government_number,
          hasGovernmentNumber: !!sqlParams.government_number,
          template_used: template_used,
          intent: intent
        });
        
        // EXPLICIT DEBUG FOR GOVERNMENT PARAMETER
        console.log('🔥 SQLPARAMS DETAILED DEBUG:');
        console.log('  - sqlParams =', JSON.stringify(sqlParams, null, 2));
        console.log('  - sqlParams.government_number =', sqlParams.government_number);
        console.log('  - typeof sqlParams.government_number =', typeof sqlParams.government_number);
        console.log('  - Boolean(sqlParams.government_number) =', Boolean(sqlParams.government_number));
        console.log('  - Original parameters array =', JSON.stringify(parameters, null, 2));
        console.log('  - Template used =', template_used);
        console.log('  - Intent =', intent);
        
        // SPECIAL HANDLING FOR COUNT QUERIES
        console.log('🔴 COUNT QUERY DETECTION DEBUG:');
        console.log('  - template_used:', template_used);
        console.log('  - template_used includes count_:', template_used && template_used.includes('count_'));
        console.log('  - entities.operation:', entities.operation);
        console.log('  - intent:', intent);
        
        const isCountQuery = template_used && (
          template_used.includes('count_') ||
          template_used === 'compare_governments'
        ) || (entities.operation === 'count' || intent === 'count');
        
        console.log('  - isCountQuery result:', isCountQuery);
        
        if (isCountQuery) {
          logger.info('Processing COUNT query with special handling', { template_used, intent });
          console.log('✅ ENTERING COUNT QUERY HANDLING BLOCK');
          
          // For count queries, we need to execute actual counting logic
          if (template_used === 'count_decisions_by_topic') {
            // Execute count by topic
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            // Add topic filter if available
            if (sqlParams.topic) {
              countQuery = countQuery.ilike('tags_policy_area', `%${sqlParams.topic}%`);
            }
            
            // Add government filter if available
            if (sqlParams.government_number) {
              countQuery = countQuery.eq('government_number', sqlParams.government_number.toString());
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count query error', { error, sqlParams });
              results = [];
            } else {
              // Return count result in the format expected by formatter
              results = [{
                government_number: sqlParams.government_number,
                topic: sqlParams.topic,
                decision_count: count || 0,
                count: count || 0  // Formatter expects 'count' field
              }];
              logger.info('Count query completed', { count, sqlParams });
            }
          } else if (template_used === 'count_decisions_by_government') {
            // Execute count by government
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            if (sqlParams.government_number) {
              countQuery = countQuery.eq('government_number', sqlParams.government_number.toString());
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count query error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                government_number: sqlParams.government_number,
                decision_count: count || 0,
                count: count || 0  // Formatter expects 'count' field
              }];
              logger.info('Count query completed', { count, sqlParams });
            }
          } else if (template_used === 'count_by_topic_and_year') {
            // Count by topic and year
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            if (sqlParams.topic) {
              countQuery = countQuery.ilike('tags_policy_area', `%${sqlParams.topic}%`);
            }
            if (sqlParams.year) {
              const yearStart = `${sqlParams.year}-01-01`;
              const yearEnd = `${sqlParams.year}-12-31`;
              countQuery = countQuery.gte('decision_date', yearStart).lte('decision_date', yearEnd);
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count by topic and year error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                count: count || 0,
                topic: sqlParams.topic,
                year: sqlParams.year
              }];
              logger.info('Count by topic and year completed', { count, sqlParams });
            }
          } else if (template_used === 'count_by_topic_date_range') {
            // Count by topic and date range
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            if (sqlParams.topic) {
              countQuery = countQuery.ilike('tags_policy_area', `%${sqlParams.topic}%`);
            }
            if (sqlParams.start_date && sqlParams.end_date) {
              countQuery = countQuery.gte('decision_date', sqlParams.start_date).lte('decision_date', sqlParams.end_date);
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count by topic date range error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                count: count || 0,
                topic: sqlParams.topic,
                start_date: sqlParams.start_date,
                end_date: sqlParams.end_date
              }];
              logger.info('Count by topic date range completed', { count, sqlParams });
            }
          } else if (template_used === 'count_by_year') {
            // Count all decisions in a year
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            if (sqlParams.year) {
              const yearStart = `${sqlParams.year}-01-01`;
              const yearEnd = `${sqlParams.year}-12-31`;
              countQuery = countQuery.gte('decision_date', yearStart).lte('decision_date', yearEnd);
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count by year error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                count: count || 0,
                year: sqlParams.year
              }];
              logger.info('Count by year completed', { count, sqlParams });
            }
          } else if (template_used === 'count_operational_by_topic') {
            // Count operational decisions by topic
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            if (sqlParams.topic) {
              countQuery = countQuery.ilike('tags_policy_area', `%${sqlParams.topic}%`);
            }
            // Add operational filter
            countQuery = countQuery.eq('operativity', 'אופרטיבית');
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count operational by topic error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                count: count || 0,
                topic: sqlParams.topic,
                decision_type: 'אופרטיבית'
              }];
              logger.info('Count operational by topic completed', { count, sqlParams });
            }
          } else {
            // Generic count handling
            let countQuery = supabase
              .from('israeli_government_decisions')
              .select('*', { count: 'exact', head: true });
            
            // Apply filters from parameters
            if (sqlParams.government_number) {
              countQuery = countQuery.eq('government_number', sqlParams.government_number.toString());
            }
            if (sqlParams.topic) {
              countQuery = countQuery.ilike('tags_policy_area', `%${sqlParams.topic}%`);
            }
            
            const { count, error } = await countQuery;
            
            if (error) {
              logger.error('Count query error', { error, sqlParams });
              results = [];
            } else {
              results = [{
                count: count || 0,
                decision_count: count || 0
              }];
              logger.info('Generic count query completed', { count, sqlParams });
            }
          }
        } else {
          // REGULAR SEARCH QUERIES - existing logic
          console.log('❌ NOT A COUNT QUERY - ENTERING REGULAR SEARCH BLOCK');
          logger.info('Processing regular search query');
          
          // Build Supabase query based on SQL parameters (not entities)
          let query = supabase
            .from('israeli_government_decisions')
            .select('*');
        
        // Government number filter: ALWAYS use SQL params when available (SQL bot handles government 37 default)
        if (sqlParams.government_number) {
          query = query.eq('government_number', sqlParams.government_number.toString());
          logger.debug('Added government filter from SQL params', { government_number: sqlParams.government_number });
        } else if (entities.government_number) {
          query = query.eq('government_number', entities.government_number.toString());
          logger.debug('Added government filter from entities', { government_number: entities.government_number });
        }
        
        // Decision number filter
        if (sqlParams.decision_number) {
          query = query.eq('decision_number', sqlParams.decision_number.toString());
          logger.debug('Added decision number filter', { decision_number: sqlParams.decision_number });
        }
        
        // Date range filter
        if (entities.date_range && typeof entities.date_range === 'object' && 
            entities.date_range.start && entities.date_range.end) {
          query = query
            .gte('decision_date', entities.date_range.start)
            .lte('decision_date', entities.date_range.end);
          logger.debug('Added date range filter', entities.date_range);
        } else if (entities.date_range && typeof entities.date_range === 'string') {
          // Log warning if date_range is a string instead of an object
          logger.warn('Date range received as string instead of object', { 
            date_range: entities.date_range,
            type: typeof entities.date_range 
          });
        }
        
        // Ministry filter - search in tags_government_body
        if (entities.ministries && entities.ministries.length > 0) {
          // For multiple ministries, use OR logic
          const ministryFilters = entities.ministries
            .map((ministry: string) => `tags_government_body.ilike.%${ministry}%`)
            .join(',');
          query = query.or(ministryFilters);
          logger.debug('Added ministry filter', { ministries: entities.ministries });
        }
        
        // Topic filter - search in tags_policy_area
        if (entities.topic && entities.topic !== 'אחרונות') {
          query = query.ilike('tags_policy_area', `%${entities.topic}%`);
          logger.debug('Added topic filter', { topic: entities.topic });
        }
        
        // For "latest" queries, ensure we only get decisions with valid dates
        if (entities.order === 'latest' || entities.topic === 'אחרונות') {
          query = query
            .not('decision_date', 'is', null)
            .gte('decision_date', '1990-01-01'); // Exclude very old or invalid dates
          logger.debug('Added date validity filter for latest decisions');
        }
        
        // Order and limit
        query = query
          .order('decision_date', { ascending: false })
          .order('government_number', { ascending: false })
          .order('decision_number', { ascending: false })
          .limit(requestedLimit);
        
          // Execute query
          const { data, error } = await query;
          
          if (error) {
            logger.error('Supabase query error', { error, entities });
            results = [];
          } else {
            results = data || [];
            
            // NO POST-QUERY FILTERING NEEDED - SQL params handle government filtering correctly
            
            logger.info(`${entities.topic || entities.ministries ? 'Filtered' : 'General'} search completed`, { 
              resultCount: results.length,
              entities,
              requestedLimit
            });
          }
        } // End of else block for regular search queries
        
        // Special handling for decision number not found
        if (results.length === 0 && entities.decision_number) {
          logger.info(`Decision number ${entities.decision_number} not found in government ${entities.government_number || 'any'}`, { 
            decision_number: entities.decision_number,
            government_number: entities.government_number 
          });
          // Return empty results for specific decision that doesn't exist
          results = [];
        }
        // If no results and we have a topic, try searching in title and summary
        else if (results.length === 0 && entities.topic && entities.topic !== 'אחרונות') {
          logger.debug('No results in tags, searching in title and summary');
          
          const { data: titleSummaryData, error: titleSummaryError } = await supabase
            .from('israeli_government_decisions')
            .select('*')
            .or(`decision_title.ilike.%${entities.topic}%,summary.ilike.%${entities.topic}%`)
            .order('decision_date', { ascending: false })
            .limit(requestedLimit);
            
          if (titleSummaryError) {
            logger.error('Supabase query error (title/summary search)', { titleSummaryError });
          } else if (titleSummaryData && titleSummaryData.length > 0) {
            results = titleSummaryData;
            logger.debug('Title/summary search found results', { 
              resultCount: results.length
            });
          }
        }
      } catch (error) {
        logger.error('SQL execution failed', { error });
        // Continue with empty results
      }
      logger.debug('SQL generation completed', { 
        resultCount: results?.length || 0, 
        template: template_used 
      });

      // Step 5: Result Evaluation - ONLY FOR EVAL INTENT
      // The evaluator should only run for deep analysis of specific decisions
      let evaluation: { 
        overall_score: number; 
        relevance_level: string;
        quality_metrics?: any[];
        content_analysis?: any;
        recommendations?: any[];
        confidence?: number;
        explanation?: string;
        processing_time_ms?: number;
        token_usage?: any;
      } | undefined = undefined;
      
      // Step 2.1: Smart conditional EVALUATOR activation
      // Only run evaluator for specific analysis requests, not generic searches
      const shouldRunEvaluator = this.shouldRunEvaluator(intent, entities, results);
      
      if (shouldRunEvaluator) {
        logger.info('EVALUATOR conditions met - proceeding with analysis', {
          intent,
          has_decision_number: !!entities.decision_number,
          result_count: results?.length || 0
        });
        // Step 1.3: Content validation for EVALUATOR
        const contentSuitabilityCheck = this.validateContentForEvaluation(results[0]);
        if (!contentSuitabilityCheck.suitable) {
          logger.info('Skipping EVALUATOR due to content validation', { 
            reason: contentSuitabilityCheck.reason,
            decision_number: results[0].decision_number 
          });
          
          // Return standard "content not suitable" evaluation
          evaluation = {
            overall_score: 0.5,
            relevance_level: 'not_suitable_for_analysis',
            content_analysis: {
              analysis_type: 'content_validation_skip',
              reason: contentSuitabilityCheck.reason,
              details: contentSuitabilityCheck.details
            },
            explanation: `תוכן לא מתאים לניתוח מעמיק: ${contentSuitabilityCheck.reason}`,
            processing_time_ms: 0,
            confidence: 1.0
          };
        } else {
          // Step 3.1: Multi-tier model selection based on content length
          const modelSelection = this.selectEvaluatorModel(contentSuitabilityCheck.contentLength);
          
          logger.info('EVAL intent detected - using multi-tier model selection', {
            content_length: contentSuitabilityCheck.contentLength,
            selected_model: modelSelection.model,
            max_tokens: modelSelection.maxTokens,
            tier: modelSelection.tier
          });
          
          // Extract decision_number from entities (what user requested) for EVALUATOR bot
          const decision_number = entities.decision_number || (results[0] && results[0].decision_number);
          
          const evalResponse = await this.callBot(this.config.urls.evaluator, '/evaluate', {
            conv_id: conversationId,
            original_query: request.message,  // Changed from 'query' to 'original_query'
            decision_number: decision_number, // Added required decision_number field
            government_number: entities.government_number || (results[0] && results[0].government_number), // Pass government number from entities
            results: results.slice(0, 1), // For EVAL, typically analyze just one decision
            intent,
            entities,
            // Step 3.1: Pass model selection to EVALUATOR bot
            model_config: {
              model: modelSelection.model,
              max_tokens: modelSelection.maxTokens,
              tier: modelSelection.tier
            }
          }, currentRequestTokens, this.config.evaluatorTimeout); // Use extended timeout for EVALUATOR
          
          if (evalResponse) {
            // EVALUATOR bot returns data directly, not under 'evaluation' field
            evaluation = {
              overall_score: evalResponse.overall_score,
              relevance_level: evalResponse.relevance_level,
              quality_metrics: evalResponse.quality_metrics,
              content_analysis: evalResponse.content_analysis,
              recommendations: evalResponse.recommendations,
              confidence: evalResponse.confidence,
              explanation: evalResponse.explanation,
              processing_time_ms: evalResponse.processing_time_ms,
              token_usage: evalResponse.token_usage
            };
            logger.info('Deep evaluation completed', evaluation);
          } else {
            logger.warn('EVALUATOR bot returned no response - creating empty evaluation');
            evaluation = {
              overall_score: 0,
              relevance_level: 'unknown',
              quality_metrics: [],
              content_analysis: { error: 'EVALUATOR failed to process' },
              recommendations: [],
              confidence: 0,
              explanation: 'שגיאה בעיבוד הניתוח',
              processing_time_ms: 0,
              token_usage: null
            };
          }
        }
      } else if (intent === 'EVAL' || intent === 'ANALYSIS') {
        // EVAL/ANALYSIS intent but conditions not met for running evaluator
        logger.info('EVAL/ANALYSIS intent but skipping EVALUATOR', {
          intent,
          reason: !results || results.length === 0 ? 'no_results' : 
                  results.length > 1 && !entities.decision_number ? 'multiple_results_no_specific_decision' :
                  'incomplete_entity_set',
          result_count: results?.length || 0,
          has_decision_number: !!entities.decision_number
        });
      }

      // Step 6: Result Ranking (if results exist)
      let rankedResults = results;
      let rankingExplanation = '';
      
      // RANKER DISABLED - inherently expensive due to processing all results
      // Even with optimizations, it needs to analyze full result sets making it costly
      const SKIP_RANKER = true; // Always skip ranker until a more efficient solution is found
      
      if (results && results.length > 0 && !SKIP_RANKER) {
        // Filter out heavy fields before sending to ranker
        const lightweightResults = results.map((result: any) => ({
          id: result.id,
          decision_number: result.decision_number,
          government_number: result.government_number,
          decision_date: result.decision_date,
          decision_title: result.decision_title,
          summary: result.summary,
          tags_policy_area: result.tags_policy_area,
          operativity: result.operativity,
          // Exclude: decision_content, embedding, all_tags, decision_url, etc.
        }));
        
        logger.debug('Sending lightweight results to ranker', {
          originalResultSize: JSON.stringify(results).length,
          lightweightResultSize: JSON.stringify(lightweightResults).length,
          resultCount: lightweightResults.length
        });
        
        const rankingResponse = await this.callBot(this.config.urls.ranker, '/rank', {
          conv_id: conversationId,
          original_query: request.message,
          intent,
          entities,
          results: lightweightResults,
          strategy: 'hybrid'
        }, currentRequestTokens);

        if (rankingResponse && rankingResponse.ranked_results) {
          // Map the ranked IDs back to full results
          const rankedIds = rankingResponse.ranked_results.map((r: any) => r.id);
          rankedResults = rankedIds.map((id: number) => 
            results.find((r: any) => r.id === id)
          ).filter(Boolean);
          
          rankingExplanation = rankingResponse.ranking_explanation;
          logger.debug('Result ranking completed', { 
            rankedCount: rankedResults.length,
            strategy: rankingResponse.strategy_used 
          });
        }
      } else if (SKIP_RANKER && results.length > 0) {
        logger.debug('Skipping ranker (temporary bypass)', { 
          resultCount: results.length 
        });
        rankingExplanation = 'Ranking skipped - using default order';
      }

      // Step 7: Response Formatting
      // Check if this is a count query (based on template or operation)
      const isCountQuery = template_used && (
        template_used.includes('count_') ||
        template_used === 'compare_governments'
      ) || (entities.operation === 'count');
      
      // For count queries, pass the results as-is (they contain count information)
      // For regular queries, map database fields to formatter expected fields
      const mappedResults = isCountQuery ? rankedResults : rankedResults.map((result: any) => ({
        ...result,
        title: result.decision_title || 'ללא כותרת',
        content: result.summary || result.decision_content?.substring(0, 500) || '',
        decision_content: result.decision_content || result.content || '', // Ensure full content is available
        summary: result.summary || '', // Ensure summary is available separately
        topics: result.tags_policy_area ? result.tags_policy_area.split(';').map((t: string) => t.trim()) : [],
        ministries: result.tags_government_body ? result.tags_government_body.split(';').map((m: string) => m.trim()) : []
      }));
      
      // NEW LLM FORMATTER: Use the LLM formatter if enabled
      
      let formatResponse: any;
      
      if (this.useLLMFormatter) {
        // NEW FLOW: Use LLM-based formatter
        logger.info('Using LLM formatter (GPT-4o-mini)', { 
          conversationId,
          resultCount: mappedResults.length 
        });
        
        // Determine data type for formatter
        let dataType = 'ranked_rows';
        let content: any = { results: mappedResults };
        
        if (isCountQuery) {
          dataType = 'count';
          content = mappedResults[0] || { count: 0 };
        } else if (intent === 'EVAL' || intent === 'ANALYSIS') {
          dataType = 'analysis';
          content = {
            evaluation: evaluation,
            decision: mappedResults[0],
            explanation: evaluation?.explanation || ''
          };
        } else if (entities.comparison_target) {
          dataType = 'comparison';
          content = { results: mappedResults, comparison_type: entities.comparison_target };
        }
        
        formatResponse = await this.callBot(this.config.urls.formatter, '/format', {
          data_type: dataType,
          content: content,
          original_query: request.message,
          presentation_style: request.presentationStyle || 'card',
          locale: 'he',
          conv_id: conversationId,
          include_metadata: request.includeMetadata !== false,
          include_scores: request.includeScores !== false,
          max_results: 10
        }, currentRequestTokens);
        
      } else {
        // OLD FLOW: Use code-based formatter
        formatResponse = await this.callBot(this.config.urls.formatter, '/format', {
          conv_id: conversationId,
          original_query: request.message,
          intent,
          entities,
          ranked_results: mappedResults,
          evaluation_summary: evaluation,
          ranking_explanation: rankingExplanation,
          output_format: request.outputFormat || 'markdown',
          presentation_style: request.presentationStyle || 'detailed',
          include_metadata: request.includeMetadata !== false,
          include_scores: request.includeScores !== false
        }, currentRequestTokens);
      }

      // Check if format response is valid
      if (!formatResponse || !formatResponse.formatted_response) {
        throw new Error('Response formatting failed - invalid response');
      }

      const formattedResponse = formatResponse.formatted_response;
      const processingTime = Date.now() - startTime;

      logger.info('Bot chain processing completed', {
        sessionId: request.sessionId,
        intent,
        resultCount: rankedResults?.length || 0,
        processingTimeMs: processingTime
      });

      const response: BotChainResponse = {
        success: true,
        response: formattedResponse,
        metadata: {
          intent,
          entities,
          confidence,
          evaluation,
          processing_time_ms: processingTime,
          service: 'bot-chain-full-pipeline',
          token_usage: this.getCurrentRequestTokenSummary(currentRequestTokens, this.getRouteType(intent, needs_clarification)),
          sessionId: request.sessionId
        }
      };
      
      // Store response in cache (with safety checks for specific entities)
      this.storeInCache(request.message, response);
      
      return response;

    } catch (error) {
      const processingTime = Date.now() - startTime;
      logger.error('Bot chain processing failed', {
        sessionId: request.sessionId,
        error: error instanceof Error ? error.message : String(error),
        processingTimeMs: processingTime
      });

      return {
        success: false,
        response: 'מצטער, אירעה שגיאה בעיבוד השאילתא. אנא נסה שוב.',
        error: error instanceof Error ? error.message : String(error),
        metadata: {
          intent: 'error',
          entities: {},
          confidence: 0,
          processing_time_ms: processingTime,
          service: 'bot-chain-error'
        }
      };
    }
  }

  isEnabled(): boolean {
    return this.config.enabled;
  }
  
  // Get usage statistics
  getUsageStats(): {
    totalRequests: number;
    cacheHitRate: number;
    totalTokensUsed: number;
    totalCostUSD: number;
    avgTokensPerRequest: number;
    avgCostPerRequest: number;
    sqlTemplateCacheSize: number;
    responseCacheSize: number;
    intentPatternCacheSize: number;
  } {
    const tokenSummary = this.getTokenUsageSummary();
    const totalRequests = this.tokenUsageHistory.length;
    
    // Calculate cache hit rate
    let cacheHits = 0;
    for (const entry of this.responseCache.values()) {
      cacheHits += entry.hits;
    }
    const cacheHitRate = totalRequests > 0 ? cacheHits / (totalRequests + cacheHits) : 0;
    
    return {
      totalRequests,
      cacheHitRate,
      totalTokensUsed: tokenSummary?.total_tokens || 0,
      totalCostUSD: tokenSummary?.estimated_cost_usd || 0,
      avgTokensPerRequest: totalRequests > 0 ? (tokenSummary?.total_tokens || 0) / totalRequests : 0,
      avgCostPerRequest: totalRequests > 0 ? (tokenSummary?.estimated_cost_usd || 0) / totalRequests : 0,
      sqlTemplateCacheSize: this.sqlTemplateCache.size,
      responseCacheSize: this.responseCache.size,
      intentPatternCacheSize: this.intentPatternCache.size
    };
  }
}

// Singleton instance
let botChainServiceInstance: BotChainService | null = null;

export function getBotChainService(): BotChainService {
  if (!botChainServiceInstance) {
    botChainServiceInstance = new BotChainService();
  }
  return botChainServiceInstance;
}

export { BotChainService, BotChainRequest, BotChainResponse };