import { Router } from 'express';

import { postChatSchema } from '../schemas/chatSchemas'
import { chatController, getChatHealthWithBotChain, testBotChain } from '../controllers/chat-bot-chain';
import { getBotChainService } from '../services/botChainService';
import { validateData } from '../middleware/validationMiddleware';

const router = Router();

// POST /api/chat - Main chat endpoint using bot chain
router.post('/', (req, _res, next) => {
  console.log('[ChatRoute] POST /api/chat received');
  console.log('[ChatRoute] Body:', req.body);
  next();
}, validateData(postChatSchema), chatController);

// GET /api/chat/health - Health check for bot chain
router.get('/health', getChatHealthWithBotChain);

// POST /api/chat/test-bot-chain - Test bot chain directly
router.post('/test-bot-chain', async (req, res) => {
  await testBotChain(req, res);
});

// GET /api/chat/usage-stats - Get bot chain usage statistics
router.get('/usage-stats', async (_req, res) => {
  try {
    const botChainService = getBotChainService();
    const stats = botChainService.getUsageStats();
    
    res.json({
      success: true,
      stats: {
        ...stats,
        cacheHitRatePercent: (stats.cacheHitRate * 100).toFixed(2) + '%',
        avgCostPerRequestFormatted: '$' + stats.avgCostPerRequest.toFixed(4),
        totalCostFormatted: '$' + stats.totalCostUSD.toFixed(2)
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get usage statistics'
    });
  }
});

// GET /api/chat/recent-usage - Get recent token usage history
router.get('/recent-usage', async (_req, res) => {
  try {
    const botChainService = getBotChainService();
    // Get the last 10 requests - need to implement this method
    const stats = botChainService.getUsageStats();
    
    res.json({
      success: true,
      message: 'Recent usage tracking available through logs and individual responses',
      current_stats: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get recent usage'
    });
  }
});

export default router;