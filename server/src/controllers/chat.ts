import { Request, Response } from 'express';
import { getSQLQueryEngineServiceWrapper } from '../services/sqlQueryEngineService';
import { getDataProviderService } from '../services/dataProviderService';
import { detectIntentWithGPT, generateSystemResponse } from '../services/intentDetectionService';

export async function handleChatRequest(req: Request, res: Response) {
  const { message, sessionId } = req.body;

  // Set up SSE headers
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
  });

  try {
    console.log('[Chat] Processing user message:', message);
    
    // Use GPT to detect intent
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
          
          console.log('[Chat] Using SQL Query Engine for data query');
          const result = await sqlEngine.processNaturalQuery(queryToUse, sessionId);
          
          // Send the formatted response with session info
          res.write(`data: ${JSON.stringify({ 
            type: 'response',
            content: result.formatted,
            metadata: {
              query_type: result.type,
              service: 'sql-engine',
              data_count: Array.isArray(result.data) ? result.data.length : 1,
              session_id: sessionId,
              query_id: result.metadata?.query_id,
              intent_confidence: intentResult.confidence,
              sql_query: result.metadata?.sql_query
            }
          })}\n\n`);
        } catch (sqlError) {
          console.error('[Chat] SQL Engine error:', sqlError);
          
          res.write(`data: ${JSON.stringify({ 
            type: 'error',
            content: 'שירות הניתוח אינו זמין כרגע. אנא נסה שוב מאוחר יותר.',
            metadata: { service: 'sql-engine', error: sqlError instanceof Error ? sqlError.message : 'Unknown error' }
          })}\n\n`);
        }
        break;
        
      case 'GENERAL_QUESTION':
        console.log('[Chat] Handling general question about the system');
        
        // Generate appropriate response based on the question
        const systemResponse = await generateSystemResponse(intentResult.metadata?.questionType || 'general');
        
        res.write(`data: ${JSON.stringify({ 
          type: 'response',
          content: systemResponse,
          metadata: {
            query_type: 'general_question',
            service: 'system',
            session_id: sessionId,
            intent_confidence: intentResult.confidence
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
            session_id: sessionId,
            intent_confidence: intentResult.confidence
          }
        })}\n\n`);
        break;
        
      default:
        // Fallback - should not happen
        console.error('[Chat] Unknown intent:', intentResult.intent);
        
        res.write(`data: ${JSON.stringify({ 
          type: 'error',
          content: 'אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.',
          metadata: {
            query_type: 'error',
            service: 'system',
            error: 'unknown_intent'
          }
        })}\n\n`);
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
      error: error instanceof Error ? error.message : 'Unknown error'
    })}\n\n`);
    
    res.end();
  }
}

// Health check endpoint for the chat service
export async function getChatHealth(_req: Request, res: Response) {
  try {
    const sqlEngine = getSQLQueryEngineServiceWrapper();
    const dataProvider = getDataProviderService();
    
    const sqlEngineHealth = await sqlEngine.checkHealth().catch(() => false);
    const dataProviderStatus = dataProvider.getStatus();
    
    res.json({
      status: 'healthy',
      activeEngine: 'sql',
      services: {
        sqlEngine: {
          available: sqlEngineHealth,
          stats: sqlEngineHealth ? await sqlEngine.getStatistics() : null
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

// Endpoint for SQL engine testing
export async function testSQLEngine(req: Request, res: Response) {
  try {
    const { query } = req.body;
    
    if (!query) {
      return res.status(400).json({
        error: 'Query is required'
      });
    }
    
    const sqlEngine = getSQLQueryEngineServiceWrapper();
    const result = await sqlEngine.processNaturalQuery(query);
    
    res.json({
      success: result.success,
      type: result.type,
      formatted: result.formatted,
      metadata: result.metadata,
      data_preview: Array.isArray(result.data) 
        ? result.data.slice(0, 3) 
        : result.data
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// Compatibility with existing structure
export const chatController = handleChatRequest;
