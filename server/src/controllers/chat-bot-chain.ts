import { Request, Response } from 'express';
import { getBotChainService } from '../services/botChainService';

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
    
    // Check if bot chain is enabled
    if (!botChainService.isEnabled()) {
      res.write(`data: ${JSON.stringify({ 
        type: 'error',
        content: 'שירות הבוט אינו זמין כרגע. אנא פנה למנהל המערכת.',
        error: 'Bot chain is disabled',
        metadata: { engine: 'bot-chain' }
      })}\n\n`);
      res.end();
      return;
    }
    
    // Check bot chain health
    const isBotChainHealthy = await botChainService.checkHealth();
    
    if (!isBotChainHealthy) {
      res.write(`data: ${JSON.stringify({ 
        type: 'error',
        content: 'שירות הבוט אינו זמין כרגע. אנא נסה שוב מאוחר יותר.',
        error: 'Bot chain service unavailable',
        metadata: { engine: 'bot-chain' }
      })}\n\n`);
      res.end();
      return;
    }
    
    console.log('[Chat] Using Bot Chain for processing');
    
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
      // Bot chain failed
      console.error('[Chat] Bot chain failed:', botChainResult.error);
      res.write(`data: ${JSON.stringify({ 
        type: 'error',
        content: 'אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.',
        error: botChainResult.error || 'Bot chain processing failed',
        metadata: { engine: 'bot-chain' }
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
      error: error instanceof Error ? error.message : 'Unknown error',
      metadata: { engine: 'bot-chain' }
    })}\n\n`);
    
    res.end();
  }
}

// Enhanced health check for bot chain
export async function getChatHealthWithBotChain(_req: Request, res: Response) {
  try {
    const botChainService = getBotChainService();
    
    // Check bot chain health
    const botChainHealth = await botChainService.checkHealth().catch(() => false);
    
    res.json({
      status: botChainHealth ? 'healthy' : 'unhealthy',
      activeEngine: 'bot-chain',
      services: {
        botChain: {
          available: botChainHealth,
          enabled: botChainService.isEnabled()
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