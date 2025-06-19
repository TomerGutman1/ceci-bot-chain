import './config/env'
import express from 'express'
import cors from 'cors'
import { errorHandler } from './middleware/errorHandler'
import apiRouter from './routes/index'
import { getDataProviderService } from './services/dataProviderService'

const port = process.env.PORT || 5173
const app = express()

// CORS configuration
const corsOptions = {
  origin: process.env.NODE_ENV === 'production' 
    ? process.env.FRONTEND_URL 
    : ['http://localhost:8080', 'http://localhost:5174', 'http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-client-info', 'apikey'],
}

// Request logging middleware
app.use((req, _res, next) => {
  const logMessage = `[Server] ${new Date().toISOString()} ${req.method} ${req.url}`;
  console.log(logMessage);
  
  // Also write to a log file
  const fs = require('fs');
  fs.appendFileSync('server.log', logMessage + '\n');
  
  next();
});

app.use(cors(corsOptions))
app.use(express.json())

// Health check endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'govainaTG Backend' })
})

// API health check endpoint
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', service: 'CECI-AI Backend API' })
})

// Direct test endpoint for data provider service
app.get('/test-data-provider', async (_req, res) => {
  try {
    const service = getDataProviderService();
    const status = service.getStatus();
    res.json({
      test: 'Data Provider Status',
      ...status
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed' });
  }
})

app.use('/api', apiRouter)
app.use(errorHandler)

// Initialize services on startup
async function initializeServices() {
  try {
    console.log('[Main] Initializing data provider service...');
    const startTime = Date.now();
    
    const dataProvider = getDataProviderService();
    await dataProvider.getAllDecisions(); // This will trigger loading if not already loaded
    
    const loadTime = (Date.now() - startTime) / 1000;
    const status = dataProvider.getStatus();
    console.log(`[Main] Data provider service initialized successfully`);
    console.log(`[Main] Loaded ${status.decisionCount} decisions in ${loadTime}s from ${status.source}`);
  } catch (error) {
    console.error('[Main] Failed to initialize data provider service:', error);
    console.error('[Main] PandasAI will need to load its own data');
  }
}

// Start http server
app.listen(port, async () => {
    console.log(`Server is running on port ${port}`)
    console.log(`CORS enabled for: ${corsOptions.origin}`)
    
    // Initialize services in background (don't await to not block server start)
    initializeServices().catch(error => {
        console.error('[Main] Service initialization error:', error);
    });
})
