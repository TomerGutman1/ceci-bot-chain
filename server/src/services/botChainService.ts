import axios from 'axios';
import logger from '../utils/logger';
import { supabase } from '../dal/supabaseClient';
import crypto from 'crypto';

interface BotChainConfig {
  timeout: number;
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
    };
    processing_time_ms: number;
    service: string;
    token_usage?: {
      total_tokens: number;
      prompt_tokens: number;
      completion_tokens: number;
      estimated_cost_usd: number;
      bot_breakdown: Record<string, {
        tokens: number;
        cost_usd: number;
      }>;
    };
    cache_hit?: boolean;
  };
  error?: string;
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

class BotChainService {
  private config: BotChainConfig;
  private responseCache: Map<string, CacheEntry> = new Map();
  private sqlTemplateCache: Map<string, SqlTemplateCache> = new Map();
  private tokenUsageHistory: TokenUsage[] = [];
  private readonly CACHE_TTL = 3600000; // 1 hour in milliseconds
  private readonly MAX_CACHE_SIZE = 100;
  private readonly MODEL_COSTS = {
    'gpt-4-turbo': { prompt: 0.01, completion: 0.03 }, // per 1K tokens
    'gpt-4': { prompt: 0.03, completion: 0.06 },
    'gpt-3.5-turbo': { prompt: 0.0005, completion: 0.0015 },
    'gpt-3.5-turbo-16k': { prompt: 0.003, completion: 0.004 }
  };

  constructor() {
    this.config = {
      timeout: parseInt(process.env.BOT_CHAIN_TIMEOUT || '30000'),
      enabled: true, // Always enabled
      urls: {
        rewrite: process.env.REWRITE_BOT_URL || 'http://localhost:8010',
        intent: process.env.INTENT_BOT_URL || 'http://localhost:8011',
        sqlGen: process.env.SQL_GEN_BOT_URL || 'http://localhost:8012',
        contextRouter: process.env.CONTEXT_ROUTER_BOT_URL || 'http://localhost:8013',
        evaluator: process.env.EVALUATOR_BOT_URL || 'http://localhost:8014',
        clarify: process.env.CLARIFY_BOT_URL || 'http://localhost:8015',
        ranker: process.env.RANKER_BOT_URL || 'http://localhost:8016',
        formatter: process.env.FORMATTER_BOT_URL || 'http://localhost:8017'
      }
    };

    logger.info('BotChainService initialized', { 
      urls: this.config.urls,
      enabled: this.config.enabled 
    });

    // Start cache cleanup interval
    setInterval(() => this.cleanupCache(), 300000); // Cleanup every 5 minutes
  }

  // Generate cache key from query
  private generateCacheKey(message: string): string {
    return crypto.createHash('md5').update(message.toLowerCase().trim()).digest('hex');
  }

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
      if (now - template.last_used > this.CACHE_TTL * 2) { // Keep SQL templates longer
        this.sqlTemplateCache.delete(key);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      logger.info(`Cache cleanup: removed ${cleaned} expired entries`);
    }
  }

  // Check response cache
  private checkResponseCache(message: string): CacheEntry | null {
    const key = this.generateCacheKey(message);
    const cached = this.responseCache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      cached.hits++;
      logger.info('Cache hit', { message, hits: cached.hits });
      return cached;
    }
    
    return null;
  }

  // Store in response cache
  private storeInCache(message: string, response: BotChainResponse): void {
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

  // Get token usage summary
  private getTokenUsageSummary(): BotChainResponse['metadata']['token_usage'] {
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

  async checkHealth(): Promise<boolean> {
    try {
      // Check rewrite bot as a representative health check
      const response = await axios.get(`${this.config.urls.rewrite}/health`, {
        timeout: 5000
      });
      return response.status === 200 && response.data?.status === 'ok';
    } catch (error) {
      logger.error('Bot chain health check failed', { error: error instanceof Error ? error.message : String(error) });
      return false;
    }
  }

  private async callBot(url: string, endpoint: string, data: any): Promise<any> {
    const fullUrl = `${url}${endpoint}`;
    try {
      logger.info(`Calling bot: ${fullUrl}`, { data });
      const response = await axios.post(fullUrl, data, {
        timeout: this.config.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      logger.info(`Bot response from ${fullUrl}`, { 
        status: response.status,
        data: response.data 
      });
      
      // Track token usage if available in response
      if (response.data.token_usage) {
        const botName = endpoint.replace('/', '').toUpperCase();
        const model = response.data.model || 'gpt-3.5-turbo';
        const tokens = response.data.token_usage.total_tokens || 0;
        this.trackTokenUsage(botName, tokens, model);
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
    
    try {
      logger.info('Processing query with bot chain', { 
        sessionId: request.sessionId,
        messageLength: request.message.length 
      });
      
      // Check cache first
      const cachedEntry = this.checkResponseCache(request.message);
      if (cachedEntry) {
        const cachedResponse = { ...cachedEntry.response };
        cachedResponse.metadata = {
          ...cachedResponse.metadata!,
          cache_hit: true,
          processing_time_ms: Date.now() - startTime
        };
        return cachedResponse;
      }

      // Step 1: Text Rewrite
      const rewriteResponse = await this.callBot(this.config.urls.rewrite, '/rewrite', {
        text: request.message,
        conv_id: request.sessionId
      });

      logger.info('Rewrite response received', { 
        response: rewriteResponse,
        hasCleanText: !!rewriteResponse.clean_text 
      });

      // Check if we got a valid response with clean_text
      if (!rewriteResponse.clean_text) {
        throw new Error('Rewrite step failed - no clean text returned');
      }

      const cleanText = rewriteResponse.clean_text;
      logger.debug('Text rewrite completed', { original: request.message, clean: cleanText });

      // Step 2: Intent Detection
      const intentResponse = await this.callBot(this.config.urls.intent, '/intent', {
        text: cleanText,
        conv_id: request.sessionId
      });

      // Check if we got a valid intent response
      if (!intentResponse.intent || !intentResponse.entities) {
        throw new Error('Intent detection failed - invalid response');
      }

      const { intent, entities, confidence } = intentResponse;
      logger.debug('Intent detection completed', { intent, entities, confidence });

      // Step 3: Context Routing
      const routingResponse = await this.callBot(this.config.urls.contextRouter, '/route', {
        conv_id: request.sessionId,
        current_query: cleanText,
        intent,
        entities,
        confidence_score: confidence
      });

      // Check if routing response is valid
      if (!routingResponse || !routingResponse.route) {
        throw new Error('Context routing failed - invalid response');
      }

      const { route, needs_clarification, clarification_type } = routingResponse;
      logger.debug('Context routing completed', { route, needs_clarification });

      // Handle clarification needed
      if (needs_clarification) {
        const clarifyResponse = await this.callBot(this.config.urls.clarify, '/clarify', {
          conv_id: request.sessionId,
          original_query: request.message,
          intent,
          entities,
          confidence_score: confidence,
          clarification_type
        });

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
            service: 'bot-chain-clarification'
          }
        };
      }

      // Step 4: SQL Generation - Check template cache first
      const sqlCacheKey = `${intent}_${JSON.stringify(entities)}`;
      let sqlResponse;
      
      const cachedSqlTemplate = this.sqlTemplateCache.get(sqlCacheKey);
      if (cachedSqlTemplate) {
        logger.info('SQL template cache hit', { intent, entities });
        sqlResponse = {
          sql_query: cachedSqlTemplate.sql_template,
          template_used: 'cached',
          parameters: cachedSqlTemplate.parameters
        };
        cachedSqlTemplate.usage_count++;
        cachedSqlTemplate.last_used = Date.now();
      } else {
        // Call SQL generation bot
        sqlResponse = await this.callBot(this.config.urls.sqlGen, '/sqlgen', {
          intent,
          entities,
          conv_id: request.sessionId
        });
        
        // Cache the SQL template if successful
        if (sqlResponse && sqlResponse.sql_query) {
          this.sqlTemplateCache.set(sqlCacheKey, {
            intent,
            entities_pattern: JSON.stringify(entities),
            sql_template: sqlResponse.sql_query,
            parameters: sqlResponse.parameters || [],
            last_used: Date.now(),
            usage_count: 1
          });
          logger.info('SQL template cached', { intent, entities });
        }
      }

      // Log the SQL response for debugging
      logger.info('SQL bot response details', { 
        hasResponse: !!sqlResponse,
        hasSqlQuery: !!sqlResponse?.sql_query,
        responseKeys: sqlResponse ? Object.keys(sqlResponse) : [],
        sqlResponse
      });

      // Check if SQL response is valid
      if (!sqlResponse || !sqlResponse.sql_query) {
        throw new Error('SQL generation failed - invalid response');
      }

      // const sql = sqlResponse.sql_query; // Not used after removing evaluator
      const template_used = sqlResponse.template_used;
      const parameters = sqlResponse.parameters || [];
      
      // Execute the SQL query
      let results: any[] = [];
      try {
        // Convert parameters from array to object
        const paramObj: Record<string, any> = {};
        parameters.forEach((param: any) => {
          paramObj[param.name] = param.value;
        });
        
        // For now, let's try a simpler approach - direct query to the table
        // This is a temporary solution until we figure out the proper way
        logger.debug('Trying direct Supabase query');
        
        // Check for requested limit in entities
        const requestedLimit = entities.limit || 10;
        
        // Handle date range queries
        if (entities.date_range && entities.date_range.start && entities.date_range.end) {
          logger.debug('Applying date range filter', entities.date_range);
          
          let query = supabase
            .from('israeli_government_decisions')
            .select('*')
            .gte('decision_date', entities.date_range.start)
            .lte('decision_date', entities.date_range.end);
            
          // Add topic filter if provided
          if (paramObj.topic) {
            query = query.ilike('tags_policy_area', `%${paramObj.topic}%`);
          }
          
          const { data: dateRangeData, error: dateRangeError } = await query
            .order('decision_date', { ascending: false })
            .limit(requestedLimit);
            
          if (!dateRangeError && dateRangeData) {
            results = dateRangeData;
            logger.debug('Date range search completed', { 
              resultCount: results.length,
              dateRange: entities.date_range
            });
          }
        } else {
          // First try: search in tags_policy_area
          let { data, error } = await supabase
            .from('israeli_government_decisions')
            .select('*')
            .ilike('tags_policy_area', `%${paramObj.topic || 'חינוך'}%`)
            .order('decision_date', { ascending: false })
            .limit(requestedLimit);
        
          if (error) {
            logger.error('Supabase query error (tags search)', { error });
            results = [];
          } else {
            results = data || [];
            logger.debug('Tags search completed', { 
              resultCount: results.length,
              searchedIn: 'tags_policy_area'
            });
          }
          
          // If no results from tags, search in title and summary
          if (results.length === 0 && paramObj.topic) {
            logger.debug('No results in tags, searching in title and summary');
            
            const { data: titleSummaryData, error: titleSummaryError } = await supabase
              .from('israeli_government_decisions')
              .select('*')
              .or(`decision_title.ilike.%${paramObj.topic}%,summary.ilike.%${paramObj.topic}%`)
              .order('decision_date', { ascending: false })
              .limit(requestedLimit);
              
            if (titleSummaryError) {
              logger.error('Supabase query error (title/summary search)', { titleSummaryError });
              results = [];
            } else {
              results = titleSummaryData || [];
              logger.debug('Title/summary search completed', { 
                resultCount: results.length,
                searchedIn: 'decision_title,summary'
              });
            }
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

      // Step 5: Result Evaluation - REMOVED FROM QUERY FLOW
      // The evaluator should only run in EVAL flow for deep analysis of specific decisions
      let evaluation: { overall_score: number; relevance_level: string; } | undefined = undefined;
      
      // Only call evaluator for EVAL intent type
      if (intent === 'EVAL' && results && results.length > 0) {
        logger.debug('Calling evaluator for EVAL intent');
        const evalResponse = await this.callBot(this.config.urls.evaluator, '/evaluate', {
          conv_id: request.sessionId,
          query: request.message,
          results: results.slice(0, 5), // Limit to first 5 results
          intent,
          entities
        });
        
        if (evalResponse && evalResponse.evaluation) {
          evaluation = evalResponse.evaluation;
          logger.debug('Evaluation completed', evaluation);
        }
      }

      // Step 6: Result Ranking (if results exist)
      let rankedResults = results;
      let rankingExplanation = '';
      
      // TEMPORARY: Skip ranker to avoid timeout issues
      const SKIP_RANKER = true;
      
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
          conv_id: request.sessionId,
          original_query: request.message,
          intent,
          entities,
          results: lightweightResults,
          strategy: 'hybrid'
        });

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
      // Map database fields to formatter expected fields
      const mappedResults = rankedResults.map((result: any) => ({
        ...result,
        title: result.decision_title || 'ללא כותרת',
        content: result.summary || result.decision_content?.substring(0, 500) || '',
        topics: result.tags_policy_area ? result.tags_policy_area.split(';').map((t: string) => t.trim()) : [],
        ministries: result.tags_government_body ? result.tags_government_body.split(';').map((m: string) => m.trim()) : []
      }));
      
      const formatResponse = await this.callBot(this.config.urls.formatter, '/format', {
        conv_id: request.sessionId,
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
      });

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
          token_usage: this.getTokenUsageSummary()
        }
      };
      
      // Cache the successful response
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
      totalTokensUsed: tokenSummary.total_tokens,
      totalCostUSD: tokenSummary.estimated_cost_usd,
      avgTokensPerRequest: totalRequests > 0 ? tokenSummary.total_tokens / totalRequests : 0,
      avgCostPerRequest: totalRequests > 0 ? tokenSummary.estimated_cost_usd / totalRequests : 0,
      sqlTemplateCacheSize: this.sqlTemplateCache.size,
      responseCacheSize: this.responseCache.size
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