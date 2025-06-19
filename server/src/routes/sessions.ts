import { Router } from 'express';
import axios from 'axios';

const router = Router();

const PANDASAI_URL = process.env.PANDASAI_SERVICE_URL || 'http://localhost:8001';

// GET /api/session/:sessionId
router.get('/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    console.log('[SessionRoute] GET /api/session/', sessionId);
    
    const response = await axios.get(`${PANDASAI_URL}/session/${sessionId}`);
    res.json(response.data);
  } catch (error: any) {
    console.error('[SessionRoute] Error getting session info:', error);
    
    if (error.response?.status === 404) {
      res.status(404).json({ error: 'Session not found or expired' });
    } else {
      res.status(500).json({ 
        error: 'Failed to get session info',
        details: error.message 
      });
    }
  }
});

// GET /api/sessions/stats
router.get('/stats', async (_req, res) => {
  try {
    console.log('[SessionRoute] GET /api/sessions/stats');
    
    const response = await axios.get(`${PANDASAI_URL}/sessions/stats`);
    res.json(response.data);
  } catch (error: any) {
    console.error('[SessionRoute] Error getting sessions stats:', error);
    res.status(500).json({ 
      error: 'Failed to get sessions statistics',
      details: error.message 
    });
  }
});

// POST /api/sessions/cleanup
router.post('/cleanup', async (_req, res) => {
  try {
    console.log('[SessionRoute] POST /api/sessions/cleanup');
    
    const response = await axios.post(`${PANDASAI_URL}/sessions/cleanup`);
    res.json(response.data);
  } catch (error: any) {
    console.error('[SessionRoute] Error cleaning up sessions:', error);
    res.status(500).json({ 
      error: 'Failed to cleanup sessions',
      details: error.message 
    });
  }
});

export default router;
