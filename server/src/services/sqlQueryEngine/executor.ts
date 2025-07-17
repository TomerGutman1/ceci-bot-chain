/**
 * Query Executor
 * Executes SQL queries against Supabase
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

export interface ExecutionResult {
  success: boolean;
  data?: any;
  error?: string;
  executionTime: number;
  rowCount: number;
}

export class QueryExecutor {
  private supabase: SupabaseClient;
  
  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;
    
    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Missing Supabase credentials');
    }
    
    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  async execute(sql: string, params: any[] = []): Promise<ExecutionResult> {
    const startTime = Date.now();
    console.log('[QueryExecutor] Executing SQL:', sql);
    console.log('[QueryExecutor] With params:', params);
    
    try {
      // First try to use RPC function if available
      const useRPC = process.env.USE_SUPABASE_RPC === 'true';
      
      if (useRPC) {
        const result = await this.executeWithRPC(sql, params);
        const executionTime = Date.now() - startTime;
        
        if (result.success) {
          return {
            success: true,
            data: result.data,
            executionTime,
            rowCount: result.row_count || (Array.isArray(result.data) ? result.data.length : 1)
          };
        } else {
          throw new Error(result.error || 'RPC execution failed');
        }
      } else {
        // Fallback to query builder
        const result = await this.executeWithQueryBuilder(sql, params);
        
        const executionTime = Date.now() - startTime;
        console.log(`[QueryExecutor] Query executed in ${executionTime}ms`);
        
        return {
          success: true,
          data: result.data,
          executionTime,
          rowCount: Array.isArray(result.data) ? result.data.length : 1
        };
      }
    } catch (error: any) {
      console.error('[QueryExecutor] Execution error:', error);
      return {
        success: false,
        error: error.message || 'Unknown error',
        executionTime: Date.now() - startTime,
        rowCount: 0
      };
    }
  }

  private async executeWithRPC(sql: string, params: any[]): Promise<any> {
    console.log('[QueryExecutor] Executing via RPC function');
    
    // Clean SQL - remove extra whitespace and newlines
    const cleanSQL = sql.trim().replace(/\s+/g, ' ');
    
    // Replace parameter placeholders with actual values for the RPC
    let finalSQL = cleanSQL;
    params.forEach((param, index) => {
      const placeholder = `$${index + 1}`;
      if (typeof param === 'string') {
        finalSQL = finalSQL.replace(placeholder, `'${param.replace(/'/g, "''")}'`);
      } else if (param === null) {
        finalSQL = finalSQL.replace(placeholder, 'NULL');
      } else {
        finalSQL = finalSQL.replace(placeholder, param.toString());
      }
    });
    
    console.log('[QueryExecutor] Cleaned SQL:', finalSQL);
    
    const { data, error } = await this.supabase.rpc('execute_simple_sql', {
      query_text: finalSQL
    });
    
    if (error) {
      throw error;
    }
    
    return data;
  }

  private async executeWithQueryBuilder(sql: string, params: any[]): Promise<any> {
    // Parse the SQL to extract the query components
    const queryInfo = this.parseSQL(sql);
    
    if (!queryInfo) {
      throw new Error('Unable to parse SQL query');
    }

    let query = this.supabase.from(queryInfo.table).select('*');

    // Handle SELECT
    if (queryInfo.type === 'SELECT') {
      // Select columns
      if (queryInfo.columns !== '*') {
        query = this.supabase.from(queryInfo.table).select(queryInfo.columns);
      }

      // Apply WHERE conditions
      if (queryInfo.conditions) {
        query = this.applyConditions(query, queryInfo.conditions, params) as any;
      }

      // Apply ORDER BY
      if (queryInfo.orderBy) {
        for (const order of queryInfo.orderBy) {
          query = query.order(order.column, { ascending: order.ascending });
        }
      }

      // Apply LIMIT
      if (queryInfo.limit) {
        query = query.limit(queryInfo.limit);
      }

      return await query;
    }

    // Handle COUNT
    if (queryInfo.type === 'COUNT') {
      let countQuery = this.supabase.from(queryInfo.table).select('*', { count: 'exact', head: true });
      
      if (queryInfo.conditions) {
        countQuery = this.applyConditions(countQuery, queryInfo.conditions, params) as any;
      }

      const result = await countQuery;
      
      // Transform count result to match expected format
      return {
        data: [{
          count: result.count || 0,
          ...this.extractAggregateParams(params)
        }]
      };
    }

    throw new Error(`Unsupported query type: ${queryInfo.type}`);
  }

  private parseSQL(sql: string): any {
    // Remove extra whitespace and newlines
    const cleanSQL = sql.replace(/\s+/g, ' ').trim();
    
    // Match SELECT queries
    const selectMatch = cleanSQL.match(
      /SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?(?:\s+ORDER\s+BY\s+(.+?))?(?:\s+LIMIT\s+(\d+))?$/i
    );
    
    if (selectMatch) {
      const [, columns, table, where, orderBy, limit] = selectMatch;
      
      return {
        type: 'SELECT',
        columns: columns.trim(),
        table: table.trim(),
        conditions: where ? this.parseWhereClause(where) : null,
        orderBy: orderBy ? this.parseOrderBy(orderBy) : null,
        limit: limit ? parseInt(limit) : null
      };
    }

    // Match COUNT queries
    const countMatch = cleanSQL.match(
      /SELECT\s+COUNT\(\*\)(?:\s+as\s+\w+)?.*?\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?$/i
    );
    
    if (countMatch) {
      const [, table, where] = countMatch;
      
      return {
        type: 'COUNT',
        table: table.trim(),
        conditions: where ? this.parseWhereClause(where) : null
      };
    }

    return null;
  }

  private parseWhereClause(where: string): any[] {
    const conditions = [];
    
    // Parse simple conditions like "column = $1"
    const conditionPattern = /(\w+)\s*(=|!=|>|<|>=|<=|LIKE|ILIKE)\s*\$(\d+)/gi;
    let match;
    
    while ((match = conditionPattern.exec(where)) !== null) {
      conditions.push({
        column: match[1],
        operator: match[2].toUpperCase(),
        paramIndex: parseInt(match[3]) - 1
      });
    }
    
    // Parse AND conditions
    if (where.includes(' AND ')) {
      const parts = where.split(' AND ');
      conditions.length = 0; // Clear and reparse
      
      for (const part of parts) {
        const partMatch = part.trim().match(/(\w+)\s*(=|!=|>|<|>=|<=|LIKE|ILIKE)\s*\$(\d+)/i);
        if (partMatch) {
          conditions.push({
            column: partMatch[1],
            operator: partMatch[2].toUpperCase(),
            paramIndex: parseInt(partMatch[3]) - 1,
            combinator: 'AND'
          });
        }
      }
    }
    
    return conditions;
  }

  private parseOrderBy(orderBy: string): any[] {
    const orders = [];
    const parts = orderBy.split(',');
    
    for (const part of parts) {
      const trimmed = part.trim();
      const descMatch = trimmed.match(/(\w+)\s+(DESC|ASC)?/i);
      
      if (descMatch) {
        orders.push({
          column: descMatch[1],
          ascending: !descMatch[2] || descMatch[2].toUpperCase() === 'ASC'
        });
      }
    }
    
    return orders;
  }

  private applyConditions(query: any, conditions: any[], params: any[]): any {
    for (const condition of conditions) {
      const value = params[condition.paramIndex];
      
      switch (condition.operator) {
        case '=':
          query = query.eq(condition.column, value);
          break;
        case '!=':
          query = query.neq(condition.column, value);
          break;
        case '>':
          query = query.gt(condition.column, value);
          break;
        case '<':
          query = query.lt(condition.column, value);
          break;
        case '>=':
          query = query.gte(condition.column, value);
          break;
        case '<=':
          query = query.lte(condition.column, value);
          break;
        case 'LIKE':
        case 'ILIKE':
          query = query.ilike(condition.column, value);
          break;
      }
    }
    
    return query;
  }

  private extractAggregateParams(params: any[]): any {
    // Extract additional info from params for aggregate queries
    const result: any = {};
    
    // If first param is a year, add it
    if (params.length > 0 && typeof params[0] === 'number' && params[0] > 1900 && params[0] < 2100) {
      result.year = params[0];
    }
    
    // If first param is a string (topic), add it
    if (params.length > 0 && typeof params[0] === 'string' && !params[0].includes('%')) {
      result.topic = params[0];
    }
    
    return result;
  }

  // Direct query builder method for simple queries
  async executeDirectQuery(
    table: string, 
    filters: Record<string, any>,
    options?: {
      select?: string;
      limit?: number;
      orderBy?: { column: string; ascending?: boolean };
    }
  ): Promise<ExecutionResult> {
    const startTime = Date.now();
    
    try {
      let query = this.supabase.from(table).select(options?.select || '*');
      
      // Apply filters
      for (const [key, value] of Object.entries(filters)) {
        if (typeof value === 'string' && value.includes('%')) {
          query = query.ilike(key, value);
        } else {
          query = query.eq(key, value);
        }
      }
      
      // Apply ordering
      if (options?.orderBy) {
        query = query.order(options.orderBy.column, { 
          ascending: options.orderBy.ascending ?? true 
        });
      }
      
      // Apply limit
      if (options?.limit) {
        query = query.limit(options.limit);
      }
      
      const { data, error } = await query;
      
      return {
        success: !error,
        data: data,
        error: error?.message,
        executionTime: Date.now() - startTime,
        rowCount: data ? data.length : 0
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
        executionTime: Date.now() - startTime,
        rowCount: 0
      };
    }
  }

  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      const { data, error } = await this.supabase
        .from('israeli_government_decisions')
        .select('decision_number')
        .limit(1);
      
      return !error && data !== null;
    } catch {
      return false;
    }
  }
}
