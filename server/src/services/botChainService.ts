import axios from 'axios';
import logger from '../utils/logger';

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
  };
  error?: string;
}

class BotChainService {
  private config: BotChainConfig;

  constructor() {
    this.config = {
      timeout: parseInt(process.env.BOT_CHAIN_TIMEOUT || '30000'),
      enabled: process.env.BOT_CHAIN_ENABLED === 'true',
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
      const response = await axios.post(fullUrl, data, {
        timeout: this.config.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      logger.error(`Bot call failed: ${fullUrl}`, { error: error instanceof Error ? error.message : String(error), data });
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

      // Step 1: Text Rewrite
      const rewriteResponse = await this.callBot(this.config.urls.rewrite, '/rewrite', {
        text: request.message,
        conv_id: request.sessionId
      });

      if (!rewriteResponse.success) {
        throw new Error('Rewrite step failed');
      }

      const cleanText = rewriteResponse.clean_text;
      logger.debug('Text rewrite completed', { original: request.message, clean: cleanText });

      // Step 2: Intent Detection
      const intentResponse = await this.callBot(this.config.urls.intent, '/intent', {
        text: cleanText,
        conv_id: request.sessionId
      });

      if (!intentResponse.success) {
        throw new Error('Intent detection failed');
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

      if (!routingResponse.success) {
        throw new Error('Context routing failed');
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

        if (!clarifyResponse.success) {
          throw new Error('Clarification generation failed');
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

      // Step 4: SQL Generation
      const sqlResponse = await this.callBot(this.config.urls.sqlGen, '/sqlgen', {
        intent,
        entities,
        conv_id: request.sessionId
      });

      if (!sqlResponse.success) {
        throw new Error('SQL generation failed');
      }

      const { results, sql, template_used } = sqlResponse;
      logger.debug('SQL generation completed', { 
        resultCount: results?.length || 0, 
        template: template_used 
      });

      // Step 5: Result Evaluation
      const evaluationResponse = await this.callBot(this.config.urls.evaluator, '/evaluate', {
        conv_id: request.sessionId,
        original_query: request.message,
        intent,
        entities,
        sql_query: sql,
        results,
        result_count: results?.length || 0,
        execution_time_ms: sqlResponse.execution_time_ms || 0
      });

      let evaluation: { overall_score: number; relevance_level: string; } | undefined = undefined;
      if (evaluationResponse.success) {
        evaluation = {
          overall_score: evaluationResponse.overall_score,
          relevance_level: evaluationResponse.relevance_level
        };
        logger.debug('Result evaluation completed', evaluation);
      }

      // Step 6: Result Ranking (if results exist)
      let rankedResults = results;
      let rankingExplanation = '';
      
      if (results && results.length > 0) {
        const rankingResponse = await this.callBot(this.config.urls.ranker, '/rank', {
          conv_id: request.sessionId,
          original_query: request.message,
          intent,
          entities,
          results,
          strategy: 'hybrid'
        });

        if (rankingResponse.success) {
          rankedResults = rankingResponse.ranked_results;
          rankingExplanation = rankingResponse.ranking_explanation;
          logger.debug('Result ranking completed', { 
            rankedCount: rankedResults.length,
            strategy: rankingResponse.strategy_used 
          });
        }
      }

      // Step 7: Response Formatting
      const formatResponse = await this.callBot(this.config.urls.formatter, '/format', {
        conv_id: request.sessionId,
        original_query: request.message,
        intent,
        entities,
        ranked_results: rankedResults,
        evaluation_summary: evaluation,
        ranking_explanation: rankingExplanation,
        output_format: request.outputFormat || 'markdown',
        presentation_style: request.presentationStyle || 'detailed',
        include_metadata: request.includeMetadata !== false,
        include_scores: request.includeScores !== false
      });

      if (!formatResponse.success) {
        throw new Error('Response formatting failed');
      }

      const formattedResponse = formatResponse.formatted_response;
      const processingTime = Date.now() - startTime;

      logger.info('Bot chain processing completed', {
        sessionId: request.sessionId,
        intent,
        resultCount: rankedResults?.length || 0,
        processingTimeMs: processingTime,
        evaluationScore: evaluation?.overall_score
      });

      return {
        success: true,
        response: formattedResponse,
        metadata: {
          intent,
          entities,
          confidence,
          evaluation,
          processing_time_ms: processingTime,
          service: 'bot-chain-full-pipeline'
        }
      };

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