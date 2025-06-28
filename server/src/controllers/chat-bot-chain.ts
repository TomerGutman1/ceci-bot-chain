import { Request, Response } from 'express';
import { getBotChainService } from '../services/botChainService';
import { getSQLQueryEngineServiceWrapper } from '../services/sqlQueryEngineService';
import { getDataProviderService } from '../services/dataProviderService';
import { detectIntentWithGPT, generateSystemResponse } from '../services/intentDetectionService';

export async function handleChatRequestWithBotChain(req: Request, res: Response) {
  const { message, sessionId, preferences = {} } = req.body;

  // Set up SSE headers
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
  });

  try {
    console.log('[Chat] Processing user message with bot chain:', message);
    
    const botChainService = getBotChainService();
    const useBotChain = botChainService.isEnabled();
    
    if (useBotChain) {
      // Check bot chain health
      const isBotChainHealthy = await botChainService.checkHealth();
      
      if (isBotChainHealthy) {
        console.log('[Chat] Using Bot Chain for processing');
        
        try {
          // Process with bot chain
          const botChainResult = await botChainService.processQuery({
            message,
            sessionId,
            outputFormat: preferences.outputFormat || 'markdown',
            presentationStyle: preferences.presentationStyle || 'detailed',
            includeMetadata: preferences.includeMetadata !== false,
            includeScores: preferences.includeScores !== false
          });

          if (botChainResult.success) {
            // Send successful bot chain response
            res.write(`data: ${JSON.stringify({ 
              type: 'response',
              content: botChainResult.response,
              metadata: {
                ...botChainResult.metadata,
                session_id: sessionId,
                engine: 'bot-chain'
              }
            })}\n\n`);
          } else {
            // Bot chain failed, fall back to SQL engine
            console.warn('[Chat] Bot chain failed, falling back to SQL engine:', botChainResult.error);
            await handleFallbackToSQLEngine(message, sessionId, res, botChainResult.error);
          }
        } catch (botChainError) {
          console.error('[Chat] Bot chain error:', botChainError);
          await handleFallbackToSQLEngine(message, sessionId, res, botChainError instanceof Error ? botChainError.message : String(botChainError));
        }
      } else {
        console.warn('[Chat] Bot chain unhealthy, falling back to SQL engine');
        await handleFallbackToSQLEngine(message, sessionId, res, 'Bot chain service unavailable');
      }
    } else {
      console.log('[Chat] Bot chain disabled, using SQL engine');
      await handleFallbackToSQLEngine(message, sessionId, res);
    }
    
    // Send done signal
    res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);
    res.end();
    
  } catch (error) {
    console.error('[Chat] Error:', error);
    
    // Send error message
    res.write(`data: ${JSON.stringify({ 
      type: 'error',
      content: 'מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.',
      error: error instanceof Error ? error.message : 'Unknown error',
      metadata: { engine: 'error' }
    })}\n\n`);
    
    res.end();
  }
}

async function handleFallbackToSQLEngine(
  message: string, 
  sessionId: string, 
  res: Response, 
  fallbackReason?: string
) {
  try {
    console.log('[Chat] Using SQL Engine fallback', fallbackReason ? `(${fallbackReason})` : '');
    
    // Use original intent detection for SQL engine
    const intentResult = await detectIntentWithGPT(message, sessionId);
    console.log('[Chat] Intent detected by GPT:', intentResult);
    
    // Route based on GPT's decision
    switch (intentResult.intent) {
      case 'DATA_QUERY':
        const queryToUse = intentResult.correctedQuery || message;
        
        // Use SQL Query Engine
        try {
          const sqlEngine = getSQLQueryEngineServiceWrapper();
          const isAvailable = await sqlEngine.checkHealth();
          
          if (!isAvailable) {
            throw new Error('SQL Engine not available');
          }
          
          const result = await sqlEngine.processNaturalQuery(queryToUse, sessionId);
          
          // Send the formatted response with session info
          res.write(`data: ${JSON.stringify({ 
            type: 'response',
            content: result.formatted,
            metadata: {
              query_type: result.type,
              service: 'sql-engine',
              engine: 'sql-engine-fallback',
              data_count: Array.isArray(result.data) ? result.data.length : 1,
              session_id: sessionId,
              query_id: result.metadata?.query_id,
              intent_confidence: intentResult.confidence,
              sql_query: result.metadata?.sql_query,
              fallback_reason: fallbackReason
            }
          })}\n\n`);
        } catch (sqlError) {
          console.error('[Chat] SQL Engine error:', sqlError);
          
          res.write(`data: ${JSON.stringify({ 
            type: 'error',
            content: 'שירות הניתוח אינו זמין כרגע. אנא נסה שוב מאוחר יותר.',
            metadata: { 
              service: 'sql-engine', 
              engine: 'sql-engine-fallback',
              error: sqlError instanceof Error ? sqlError.message : 'Unknown error',
              fallback_reason: fallbackReason
            }
          })}\n\n`);
        }
        break;
        
      case 'GENERAL_QUESTION':
        console.log('[Chat] Handling general question about the system');
        
        const systemResponse = await generateSystemResponse(intentResult.metadata?.questionType || 'general');
        
        res.write(`data: ${JSON.stringify({ 
          type: 'response',
          content: systemResponse,
          metadata: {
            query_type: 'general_question',
            service: 'system',
            engine: 'system-fallback',
            session_id: sessionId,
            intent_confidence: intentResult.confidence,
            fallback_reason: fallbackReason
          }
        })}\n\n`);
        break;
        
      case 'UNCLEAR':
        console.log('[Chat] Query is unclear, providing guidance');
        
        res.write(`data: ${JSON.stringify({ 
          type: 'response',
          content: intentResult.guidance || 'מצטער, לא הבנתי את הבקשה. אני יכול לעזור לך למצוא החלטות ממשלה לפי נושא, תאריך, מספר החלטה ועוד. איך אוכל לעזור?',
          metadata: {
            query_type: 'unclear',
            service: 'system',
            engine: 'system-fallback',
            session_id: sessionId,
            intent_confidence: intentResult.confidence,
            fallback_reason: fallbackReason
          }
        })}\n\n`);
        break;
        
      default:
        console.error('[Chat] Unknown intent:', intentResult.intent);
        
        res.write(`data: ${JSON.stringify({ 
          type: 'error',
          content: 'אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.',
          metadata: {
            query_type: 'error',
            service: 'system',
            engine: 'system-fallback',
            error: 'unknown_intent',
            fallback_reason: fallbackReason
          }
        })}\n\n`);
    }
  } catch (fallbackError) {
    console.error('[Chat] Fallback error:', fallbackError);
    res.write(`data: ${JSON.stringify({ 
      type: 'error',
      content: 'שירותי הניתוח אינם זמינים כרגע. אנא נסה שוב מאוחר יותר.',
      metadata: { 
        service: 'fallback', 
        engine: 'error',
        error: fallbackError instanceof Error ? fallbackError.message : 'Unknown error',
        fallback_reason: fallbackReason
      }
    })}\n\n`);
  }
}

// Enhanced health check that includes bot chain status
export async function getChatHealthWithBotChain(_req: Request, res: Response) {
  try {
    const botChainService = getBotChainService();
    const sqlEngine = getSQLQueryEngineServiceWrapper();
    const dataProvider = getDataProviderService();
    
    // Check all services
    const [botChainHealth, sqlEngineHealth] = await Promise.all([
      botChainService.checkHealth().catch(() => false),
      sqlEngine.checkHealth().catch(() => false)
    ]);
    
    const dataProviderStatus = dataProvider.getStatus();
    const activeEngine = botChainService.isEnabled() && botChainHealth ? 'bot-chain' : 'sql-engine';
    
    res.json({
      status: 'healthy',
      activeEngine,
      services: {
        botChain: {
          available: botChainHealth,
          enabled: botChainService.isEnabled(),
          primary: activeEngine === 'bot-chain'
        },
        sqlEngine: {
          available: sqlEngineHealth,
          stats: sqlEngineHealth ? await sqlEngine.getStatistics() : null,
          fallback: activeEngine !== 'sql-engine'
        },
        dataProvider: {
          available: true,
          loaded: dataProviderStatus.isLoaded,
          loading: dataProviderStatus.isLoading,
          decisions: dataProviderStatus.decisionCount,
          source: dataProviderStatus.source
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// Test endpoint for bot chain
export async function testBotChain(req: Request, res: Response) {
  try {
    const { query, sessionId = 'test', preferences = {} } = req.body;
    
    if (!query) {
      return res.status(400).json({
        error: 'Query is required'
      });
    }
    
    const botChainService = getBotChainService();
    
    if (!botChainService.isEnabled()) {
      return res.status(503).json({
        error: 'Bot chain is disabled'
      });
    }
    
    const result = await botChainService.processQuery({
      message: query,
      sessionId,
      outputFormat: preferences.outputFormat,
      presentationStyle: preferences.presentationStyle,
      includeMetadata: preferences.includeMetadata,
      includeScores: preferences.includeScores
    });
    
    res.json({
      success: result.success,
      response: result.response,
      metadata: result.metadata,
      error: result.error
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// Compatibility exports
export const chatController = handleChatRequestWithBotChain;