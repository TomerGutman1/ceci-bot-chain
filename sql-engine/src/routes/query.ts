/**
 * Query Routes
 * API routes for SQL query processing
 */

import { Router, Request, Response } from 'express';
import { getSQLQueryEngineService } from '../services/sqlQueryEngine';

const router = Router();
const sqlEngine = getSQLQueryEngineService();

// Process natural language query
router.post('/process-query', async (req: Request, res: Response) => {
  try {
    const { query, sessionId } = req.body;
    
    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Query is required'
      });
    }

    console.log(`[QueryRoute] Processing query: "${query}"`);
    
    const result = await sqlEngine.processNaturalQuery(query, sessionId);
    
    res.json(result);
  } catch (error: any) {
    console.error('[QueryRoute] Error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to process query'
    });
  }
});

// Execute direct SQL (for testing/debugging)
router.post('/execute-sql', async (req: Request, res: Response) => {
  try {
    const { sql, params } = req.body;
    
    if (!sql) {
      return res.status(400).json({
        success: false,
        error: 'SQL query is required'
      });
    }

    const result = await sqlEngine.executeSQL(sql, params || []);
    
    res.json(result);
  } catch (error: any) {
    console.error('[QueryRoute] SQL execution error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to execute SQL'
    });
  }
});

// Get schema information
router.get('/schema', (req: Request, res: Response) => {
  try {
    const schema = sqlEngine.getSchemaInfo();
    res.json({
      success: true,
      data: schema
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to get schema'
    });
  }
});

// Get service statistics
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await sqlEngine.getStatistics();
    res.json({
      success: true,
      data: stats
    });
  } catch (error: any) {
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to get statistics'
    });
  }
});

// Health check
router.get('/health', async (req: Request, res: Response) => {
  try {
    const isHealthy = await sqlEngine.checkHealth();
    res.json({
      success: true,
      healthy: isHealthy,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    res.status(503).json({
      success: false,
      healthy: false,
      error: error.message
    });
  }
});

export default router;
