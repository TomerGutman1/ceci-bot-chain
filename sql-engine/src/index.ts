/**
 * SQL Engine Service
 * Standalone service for SQL query processing
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { SQLQueryEngineService } from './services/sqlQueryEngine';
import queryRoutes from './routes/query';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.SQL_ENGINE_PORT || 8002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'sql-engine',
    timestamp: new Date().toISOString()
  });
});

// Routes
app.use('/api', queryRoutes);

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('[SQL Engine Error]:', err);
  res.status(500).json({
    success: false,
    error: err.message || 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 SQL Engine service running on port ${PORT}`);
  console.log(`   Health check: http://localhost:${PORT}/health`);
  console.log(`   API endpoint: http://localhost:${PORT}/api/process-query`);
});
