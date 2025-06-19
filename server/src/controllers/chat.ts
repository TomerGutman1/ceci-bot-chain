import { Request, Response } from 'express';
import { getPandasAIService } from '../services/pandasAIService';
import { getDataProviderService } from '../services/dataProviderService';

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
    
    // Check if PandasAI service is available
    const pandasAI = getPandasAIService();
    const isPandasAIAvailable = await pandasAI.checkHealth().catch(() => false);
    
    if (isPandasAIAvailable) {
      console.log('[Chat] Using PandasAI service for query processing');
      
      // Process query with PandasAI with session support
      const result = await pandasAI.processNaturalQuery(message, sessionId);
      
      // Send the formatted response with session info
      res.write(`data: ${JSON.stringify({ 
        type: 'response',
        content: result.formatted,
        metadata: {
          query_type: result.type,
          service: 'pandasai',
          data_count: Array.isArray(result.data) ? result.data.length : 1,
          session_id: result.session_id,
          query_id: result.query_id
        }
      })}\n\n`);
      
    } else {
      console.log('[Chat] PandasAI service not available');
      
      // Send error message
      res.write(`data: ${JSON.stringify({ 
        type: 'error',
        content: 'שירות הניתוח אינו זמין כרגע. אנא וודא ש-PandasAI רץ.',
        metadata: {
          service: 'pandasai',
          available: false
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
    const pandasAI = getPandasAIService();
    const dataProvider = getDataProviderService();
    
    const pandasAIHealth = await pandasAI.checkHealth().catch(() => false);
    const dataProviderStatus = dataProvider.getStatus();
    
    res.json({
      status: 'healthy',
      services: {
        pandasai: {
          available: pandasAIHealth,
          url: process.env.PANDASAI_SERVICE_URL || 'http://localhost:8001'
        },
        dataProvider: {
          available: true,
          loaded: dataProviderStatus.isLoaded,
          loading: dataProviderStatus.isLoading,
          decisions: dataProviderStatus.decisionCount,
          source: dataProviderStatus.source
        }
      },
      requiredService: 'pandasai'
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

// Compatibility with existing structure
export const chatController = handleChatRequest;
