/**
 * Simple TypeScript utility for Supabase RPC functions
 * Based on Context7 patterns for @supabase/supabase-js
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { config } from '../config/environment.js';
import { logger } from './logger.js';

export interface RpcResult<T = any> {
  data: T[] | null;
  error: string | null;
}

export class SupabaseRpcUtil {
  private client: SupabaseClient;

  constructor() {
    // Create Supabase client using Context7 pattern
    this.client = createClient(
      config.supabase.url,
      config.supabase.serviceRoleKey
    );
  }

  /**
   * Execute a raw SQL query using RPC function
   * Based on Context7 documentation for client.rpc()
   */
  async executeRawSql(sql: string): Promise<RpcResult> {
    try {
      logger.debug(`Executing raw SQL via RPC: ${sql}`);

      // Clean SQL - remove trailing semicolon and extra whitespace
      const cleanSql = sql.trim().replace(/;$/, '');

      // Use the RPC method as documented in Context7
      // Signature: rpc<T>(fn: string, params?: object)
      const { data, error } = await this.client.rpc('execute_college_query', {
        query_text: cleanSql
      });

      if (error) {
        logger.error('RPC execution error:', error);
        return {
          data: null,
          error: error.message || 'RPC execution failed'
        };
      }

      // Extract actual data from JSONB result format
      // The RPC function returns [{result: {...}}, {result: {...}}]
      const actualData = data?.map((row: any) => row.result) || [];
      
      logger.info(`RPC query successful: ${actualData.length} rows returned`);
      
      return {
        data: actualData,
        error: null
      };

    } catch (error) {
      logger.error('RPC utility error:', error);
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Unknown RPC error'
      };
    }
  }

  /**
   * Test RPC connection and function availability
   */
  async testRpcConnection(): Promise<boolean> {
    try {
      logger.info('Testing RPC connection...');
      
      // Simple test query
      const result = await this.executeRawSql('SELECT 1 as test');
      
      if (result.error) {
        logger.error('RPC connection test failed:', result.error);
        return false;
      }

      if (result.data && result.data.length > 0 && result.data[0].test === 1) {
        logger.info('✅ RPC connection test successful');
        return true;
      }

      logger.warn('RPC connection test returned unexpected result');
      return false;

    } catch (error) {
      logger.error('RPC connection test error:', error);
      return false;
    }
  }

  /**
   * Get table count using RPC
   */
  async getTableCount(tableName: string): Promise<number> {
    try {
      const result = await this.executeRawSql(
        `SELECT COUNT(*) as count FROM college.${tableName}`
      );

      if (result.error || !result.data || result.data.length === 0) {
        logger.warn(`Could not get count for table ${tableName}`);
        return 0;
      }

      return parseInt(result.data[0].count) || 0;

    } catch (error) {
      logger.error(`Error getting count for table ${tableName}:`, error);
      return 0;
    }
  }

  /**
   * Get sample data from a table
   */
  async getSampleData(tableName: string, limit: number = 3): Promise<any[]> {
    try {
      const result = await this.executeRawSql(
        `SELECT * FROM college.${tableName} LIMIT ${limit}`
      );

      if (result.error || !result.data) {
        logger.warn(`Could not get sample data for table ${tableName}`);
        return [];
      }

      return result.data;

    } catch (error) {
      logger.error(`Error getting sample data for table ${tableName}:`, error);
      return [];
    }
  }

  /**
   * Execute a query with parameters (basic SQL injection protection)
   */
  async executeParameterizedQuery(
    baseQuery: string, 
    params: Record<string, any>
  ): Promise<RpcResult> {
    try {
      // Simple parameter substitution (for basic cases)
      let query = baseQuery;
      
      for (const [key, value] of Object.entries(params)) {
        const placeholder = `$${key}`;
        if (query.includes(placeholder)) {
          // Basic type handling
          if (typeof value === 'string') {
            query = query.replace(placeholder, `'${value.replace(/'/g, "''")}'`);
          } else if (typeof value === 'number') {
            query = query.replace(placeholder, value.toString());
          } else {
            query = query.replace(placeholder, `'${String(value)}'`);
          }
        }
      }

      return await this.executeRawSql(query);

    } catch (error) {
      logger.error('Parameterized query error:', error);
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Parameterized query failed'
      };
    }
  }
}

// Singleton instance
let rpcUtilInstance: SupabaseRpcUtil | null = null;

export function getSupabaseRpcUtil(): SupabaseRpcUtil {
  if (!rpcUtilInstance) {
    rpcUtilInstance = new SupabaseRpcUtil();
  }
  return rpcUtilInstance;
}

// Export for direct use
export const supabaseRpc = getSupabaseRpcUtil();
