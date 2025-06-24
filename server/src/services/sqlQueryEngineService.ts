/**
 * SQL Query Engine Service wrapper
 * Provides a compatible interface to communicate with external SQL Engine service
 */

import axios from 'axios';

export interface QueryResult {
  success: boolean;
  type: 'single' | 'multiple' | 'count' | 'aggregate' | 'error';
  data: any;
  formatted: string;
  metadata?: {
    sql_query?: string;
    execution_time?: number;
    row_count?: number;
    session_id?: string;
    query_id?: string;
    confidence?: number;
  };
  error?: string;
}

export class SQLQueryEngineServiceWrapper {
  private sqlEngineUrl: string;
  private isHealthy = false;

  constructor() {
    this.sqlEngineUrl = process.env.SQL_ENGINE_URL || 'http://sql-engine:8002';
    console.log('[SQLQueryEngineWrapper] Configured with URL:', this.sqlEngineUrl);
  }

  async initialize(): Promise<void> {
    try {
      const healthy = await this.checkHealth();
      if (!healthy) {
        throw new Error('SQL Engine service is not healthy');
      }
      this.isHealthy = true;
      console.log('[SQLQueryEngineWrapper] Service initialized successfully');
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] Failed to initialize:', error);
      this.isHealthy = false;
      throw error;
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.sqlEngineUrl}/api/health`, {
        timeout: 5000
      });
      
      const data = response.data;
      this.isHealthy = data.healthy || false;
      return this.isHealthy;
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] Health check error:', error);
      this.isHealthy = false;
      return false;
    }
  }

  async processNaturalQuery(query: string, sessionId?: string): Promise<QueryResult> {
    try {
      const response = await axios.post(`${this.sqlEngineUrl}/api/process-query`, {
        query,
        sessionId
      }, {
        timeout: 30000, // 30 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] Query processing error:', error);
      
      let errorMessage = 'Unknown error';
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.error || error.message;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      return {
        success: false,
        type: 'error',
        data: null,
        formatted: '❌ שגיאה בתקשורת עם שירות SQL. אנא נסה שוב.',
        error: errorMessage
      };
    }
  }

  async getStatistics(): Promise<any> {
    try {
      const response = await axios.get(`${this.sqlEngineUrl}/api/stats`, {
        timeout: 5000
      });

      return response.data.data || response.data;
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] Statistics error:', error);
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getSchemaInfo(): Promise<any> {
    try {
      const response = await axios.get(`${this.sqlEngineUrl}/api/schema`, {
        timeout: 5000
      });

      return response.data.data || response.data;
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] Schema error:', error);
      throw error;
    }
  }

  // Direct SQL execution (for debugging/admin)
  async executeSQL(sql: string, params?: any[]): Promise<QueryResult> {
    try {
      const response = await axios.post(`${this.sqlEngineUrl}/api/execute-sql`, {
        sql,
        params
      }, {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      console.error('[SQLQueryEngineWrapper] SQL execution error:', error);
      
      let errorMessage = 'Unknown error';
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.error || error.message;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      return {
        success: false,
        type: 'error',
        data: null,
        formatted: `Error: ${errorMessage}`,
        error: errorMessage
      };
    }
  }
}

// Singleton instance
let wrapperInstance: SQLQueryEngineServiceWrapper | null = null;

export function getSQLQueryEngineServiceWrapper(): SQLQueryEngineServiceWrapper {
  if (!wrapperInstance) {
    wrapperInstance = new SQLQueryEngineServiceWrapper();
  }
  return wrapperInstance;
}

// Export types for compatibility
export type { 
  Decision, 
  QueryRequest, 
  QueryResponse, 
  QueryMetadata,
  CountResult,
  AggregateResult,
  HealthCheckResult,
  SchemaInfo 
} from './sqlQueryEngine/types';
