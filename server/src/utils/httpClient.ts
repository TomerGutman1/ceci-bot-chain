import axios, { AxiosInstance } from 'axios';
import http from 'http';
import https from 'https';
import logger from './logger';

// Create HTTP agent with connection pooling
const httpAgent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 1000,
  maxSockets: 100,              // Total max sockets
  maxFreeSockets: 10,           // Max idle sockets
  timeout: 30000,               // Socket timeout
  scheduling: 'lifo'            // Last-in-first-out scheduling
});

// Create HTTPS agent with connection pooling
const httpsAgent = new https.Agent({
  keepAlive: true,
  keepAliveMsecs: 1000,
  maxSockets: 100,
  maxFreeSockets: 10,
  timeout: 30000,
  scheduling: 'lifo'
});

// Create axios instance with optimized settings
const httpClient: AxiosInstance = axios.create({
  timeout: 30000,               // 30 second timeout per request
  httpAgent: httpAgent,
  httpsAgent: httpsAgent,
  maxRedirects: 5,
  validateStatus: (status) => status < 500,  // Don't throw on 4xx
  
  // Connection pooling headers
  headers: {
    'Connection': 'keep-alive',
    'Keep-Alive': 'timeout=120'
  }
});

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

// Add request interceptor for logging
httpClient.interceptors.request.use(
  (config) => {
    const startTime = Date.now();
    config.metadata = { startTime };
    
    logger.debug('HTTP Request', {
      method: config.method,
      url: config.url,
      timeout: config.timeout
    });
    
    return config;
  },
  (error) => {
    logger.error('HTTP Request Error', { error: error.message });
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
httpClient.interceptors.response.use(
  (response) => {
    const endTime = Date.now();
    const duration = endTime - (response.config.metadata?.startTime || endTime);
    
    logger.debug('HTTP Response', {
      method: response.config.method,
      url: response.config.url,
      status: response.status,
      duration: duration
    });
    
    return response;
  },
  (error) => {
    const endTime = Date.now();
    const duration = endTime - (error.config?.metadata?.startTime || endTime);
    
    logger.error('HTTP Response Error', {
      method: error.config?.method,
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
      code: error.code,
      duration: duration
    });
    
    return Promise.reject(error);
  }
);

// Helper function to check connection pool stats
export function getConnectionStats() {
  const httpSockets = (httpAgent as any).sockets || {};
  const httpFreeSockets = (httpAgent as any).freeSockets || {};
  const httpRequests = (httpAgent as any).requests || {};
  
  const httpsSockets = (httpsAgent as any).sockets || {};
  const httpsFreeSockets = (httpsAgent as any).freeSockets || {};
  const httpsRequests = (httpsAgent as any).requests || {};
  
  return {
    http: {
      totalSockets: Object.keys(httpSockets).reduce((sum, key) => sum + (httpSockets[key]?.length || 0), 0),
      freeSockets: Object.keys(httpFreeSockets).reduce((sum, key) => sum + (httpFreeSockets[key]?.length || 0), 0),
      requests: Object.keys(httpRequests).reduce((sum, key) => sum + (httpRequests[key]?.length || 0), 0)
    },
    https: {
      totalSockets: Object.keys(httpsSockets).reduce((sum, key) => sum + (httpsSockets[key]?.length || 0), 0),
      freeSockets: Object.keys(httpsFreeSockets).reduce((sum, key) => sum + (httpsFreeSockets[key]?.length || 0), 0),
      requests: Object.keys(httpsRequests).reduce((sum, key) => sum + (httpsRequests[key]?.length || 0), 0)
    }
  };
}

// Export both the instance and a factory function
export default httpClient;

export function createHttpClient(config?: any): AxiosInstance {
  return axios.create({
    ...httpClient.defaults,
    ...config,
    httpAgent: httpAgent,
    httpsAgent: httpsAgent
  });
}