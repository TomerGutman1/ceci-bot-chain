/**
 * SQL Query Engine Service
 * Main service that orchestrates the SQL query engine
 */

import { v4 as uuid } from 'uuid';
import { NLToSQLConverter } from './nlToSql';
import { QueryExecutor } from './executor';
import { ResponseFormatter } from './formatter';
import { DECISIONS_SCHEMA } from './schema';

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

export class SQLQueryEngineService {
  private converter: NLToSQLConverter;
  private executor: QueryExecutor;
  private formatter: ResponseFormatter;
  private isInitialized: boolean = false;

  constructor() {
    console.log('[SQLQueryEngine] Initializing service...');
    this.converter = new NLToSQLConverter();
    this.executor = new QueryExecutor();
    this.formatter = new ResponseFormatter();
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    console.log('[SQLQueryEngine] Testing database connection...');
    const isConnected = await this.executor.testConnection();
    
    if (!isConnected) {
      throw new Error('Failed to connect to database');
    }
    
    console.log('[SQLQueryEngine] Database connection successful');
    this.isInitialized = true;
  }

  async processNaturalQuery(
    naturalQuery: string, 
    sessionId?: string
  ): Promise<QueryResult> {
    const queryId = uuid();
    console.log(`[SQLQueryEngine] Processing query: "${naturalQuery}" (ID: ${queryId})`);
    
    try {
      // Ensure service is initialized
      if (!this.isInitialized) {
        await this.initialize();
      }

      // Step 1: Convert natural language to SQL
      console.log('[SQLQueryEngine] Step 1: Converting to SQL...');
      const conversion = await this.converter.convertToSQL(naturalQuery);
      console.log('[SQLQueryEngine] SQL generated:', conversion.sql);
      console.log('[SQLQueryEngine] Parameters:', conversion.params);
      
      // Validate SQL
      if (!this.converter.validateSQL(conversion.sql)) {
        throw new Error('Generated SQL contains potentially dangerous patterns');
      }
      
      // Step 2: Execute the SQL query
      console.log('[SQLQueryEngine] Step 2: Executing query...');
      const executionResult = await this.executor.execute(
        conversion.sql, 
        conversion.params
      );
      
      if (!executionResult.success) {
        throw new Error(executionResult.error || 'Query execution failed');
      }
      
      console.log(`[SQLQueryEngine] Query executed successfully. Rows: ${executionResult.rowCount}`);
      
      // Step 3: Format the results
      console.log('[SQLQueryEngine] Step 3: Formatting results...');
      const formatted = this.formatter.format(
        executionResult,
        conversion.expectedType,
        naturalQuery,
        {
          sql: conversion.sql,
          params: conversion.params,
          confidence: conversion.confidence
        }
      );
      
      // Step 4: Return complete result
      return {
        success: true,
        type: conversion.expectedType,
        data: executionResult.data,
        formatted,
        metadata: {
          sql_query: conversion.sql,
          execution_time: executionResult.executionTime,
          row_count: executionResult.rowCount,
          session_id: sessionId,
          query_id: queryId,
          confidence: conversion.confidence
        }
      };
      
    } catch (error: any) {
      console.error('[SQLQueryEngine] Error processing query:', error);
      
      return {
        success: false,
        type: 'error',
        data: null,
        formatted: this.formatError(error.message, naturalQuery),
        error: error.message,
        metadata: {
          query_id: queryId,
          session_id: sessionId
        }
      };
    }
  }

  private formatError(errorMessage: string, _query: string): string {
    // Provide helpful error messages in Hebrew
    if (errorMessage.includes('connection') || errorMessage.includes('connect')) {
      return '❌ שגיאת חיבור למסד הנתונים. אנא נסה שוב מאוחר יותר.';
    }
    
    if (errorMessage.includes('parse') || errorMessage.includes('SQL')) {
      return '❌ לא הצלחתי להבין את השאילתה. אנא נסה לנסח אותה אחרת.';
    }
    
    if (errorMessage.includes('timeout')) {
      return '❌ השאילתה לקחה יותר מדי זמן. אנא נסה שאילתה פשוטה יותר.';
    }
    
    // Default error message
    return `❌ אירעה שגיאה בעיבוד השאילתה: ${errorMessage}`;
  }

  async checkHealth(): Promise<boolean> {
    try {
      // Test database connection
      const isConnected = await this.executor.testConnection();
      
      // Test a simple conversion
      const testConversion = await this.converter.convertToSQL('החלטה 1');
      
      return isConnected && testConversion !== null;
    } catch (error) {
      console.error('[SQLQueryEngine] Health check failed:', error);
      return false;
    }
  }

  async getStatistics(): Promise<any> {
    try {
      // Get basic statistics about the database
      const countResult = await this.executor.execute(
        'SELECT COUNT(*) as total FROM israeli_government_decisions',
        []
      );
      
      const recentResult = await this.executor.execute(
        'SELECT MAX(decision_date) as most_recent FROM israeli_government_decisions',
        []
      );
      
      return {
        total_decisions: countResult.data?.[0]?.total || 0,
        most_recent_decision: recentResult.data?.[0]?.most_recent || null,
        status: 'operational'
      };
    } catch (error: any) {
      return {
        status: 'error',
        error: error.message
      };
    }
  }

  // Direct SQL execution for advanced users or debugging
  async executeSQL(sql: string, params: any[] = []): Promise<QueryResult> {
    console.log('[SQLQueryEngine] Direct SQL execution:', sql);
    
    try {
      // Validate SQL
      if (!this.converter.validateSQL(sql)) {
        throw new Error('SQL contains potentially dangerous patterns');
      }
      
      const result = await this.executor.execute(sql, params);
      
      if (!result.success) {
        throw new Error(result.error);
      }
      
      return {
        success: true,
        type: 'multiple',
        data: result.data,
        formatted: JSON.stringify(result.data, null, 2),
        metadata: {
          sql_query: sql,
          execution_time: result.executionTime,
          row_count: result.rowCount
        }
      };
    } catch (error: any) {
      return {
        success: false,
        type: 'error',
        data: null,
        formatted: `Error: ${error.message}`,
        error: error.message
      };
    }
  }

  // Get schema information
  getSchemaInfo(): any {
    return {
      table: DECISIONS_SCHEMA.table_name,
      columns: DECISIONS_SCHEMA.columns.map(col => ({
        name: col.name,
        type: col.type,
        hebrew_name: col.hebrew_name,
        description: col.description
      })),
      total_columns: DECISIONS_SCHEMA.columns.length,
      searchable_columns: DECISIONS_SCHEMA.columns
        .filter(col => col.searchable)
        .map(col => col.name),
      indexes: DECISIONS_SCHEMA.indexes
    };
  }
}

// Singleton instance
let instance: SQLQueryEngineService | null = null;

export function getSQLQueryEngineService(): SQLQueryEngineService {
  if (!instance) {
    instance = new SQLQueryEngineService();
  }
  return instance;
}
