import { Router } from 'express';

import { postChatSchema } from '../schemas/chatSchemas'
import { getChatHealth as originalGetChatHealth, testSQLEngine } from '../controllers/chat';
import { chatController, getChatHealthWithBotChain, testBotChain } from '../controllers/chat-bot-chain';
import { validateData } from '../middleware/validationMiddleware';

const router = Router();

// POST /api/chat
router.post('/', (req, _res, next) => {
  console.log('[ChatRoute] POST /api/chat received');
  console.log('[ChatRoute] Body:', req.body);
  next();
}, validateData(postChatSchema), chatController);

// GET /api/chat/health - Enhanced health check with bot chain status
router.get('/health', getChatHealthWithBotChain);

// GET /api/chat/health-original - Original health check
router.get('/health-original', originalGetChatHealth);

// POST /api/chat/test-sql - Test SQL engine directly
router.post('/test-sql', async (req, res) => {
  await testSQLEngine(req, res);
});

// POST /api/chat/test-bot-chain - Test bot chain directly
router.post('/test-bot-chain', async (req, res) => {
  await testBotChain(req, res);
});

export default router;