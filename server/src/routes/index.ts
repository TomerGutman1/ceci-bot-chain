import { Router } from 'express';
import chatRouter from './chat';
import evaluationsRouter from './evaluations';
import statisticsRouter from './statistics';
import decisionsRouter from './decisions';
import { getDataProviderService } from '../services/dataProviderService';

const router = Router();

router.use('/chat', chatRouter);
router.use('/evaluations', evaluationsRouter);
router.use('/statistics', statisticsRouter);
router.use('/decisions', decisionsRouter);

// Debug endpoint for data provider service
router.get('/data-provider/status', (_req, res) => {
  try {
    const service = getDataProviderService();
    const status = service.getStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({ 
      error: 'Failed to get service status',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
