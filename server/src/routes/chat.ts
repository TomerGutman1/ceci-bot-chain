import { Router } from 'express';

import { postChatSchema } from '../schemas/chatSchemas'
import { chatController, getChatHealth, testSQLEngine } from '../controllers/chat';
import { validateData } from '../middleware/validationMiddleware';

const router = Router();

// POST /api/chat
router.post('/', (req, _res, next) => {
  console.log('[ChatRoute] POST /api/chat received');
  console.log('[ChatRoute] Body:', req.body);
  next();
}, validateData(postChatSchema), chatController);

// GET /api/chat/health
router.get('/health', getChatHealth);

// POST /api/chat/test-sql - Test SQL engine directly
router.post('/test-sql', async (req, res) => {
  await testSQLEngine(req, res);
});

export default router;