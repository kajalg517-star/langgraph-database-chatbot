import { GoogleGenerativeAI } from '@google/generative-ai';
import { config } from '../config/environment.js';

// Simple schema interface
interface DatabaseSchema {
  [tableName: string]: {
    table_name: string;
    columns: Array<{
      column_name: string;
      data_type: string;
      is_nullable?: string;
      column_default?: string;
    }>;
    description: string;
  };
}

export interface SQLGenerationResult {
  sql: string;
  explanation: string;
  confidence: number;
  error?: string;
}

export interface ResponseFormattingResult {
  response: string;
  error?: string;
}

export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor() {
    this.genAI = new GoogleGenerativeAI(config.gemini.apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
  }

  async generateSQL(
    naturalLanguageQuery: string,
    databaseSchema: DatabaseSchema
  ): Promise<SQLGenerationResult> {
    try {
      const schemaContext = this.buildSchemaContext(databaseSchema);
      
      const prompt = `
You are a SQL expert. Convert the following natural language query into a PostgreSQL query.

Database Schema:
${schemaContext}

Natural Language Query: "${naturalLanguageQuery}"

Rules:
1. Generate ONLY valid PostgreSQL SQL
2. Use proper table and column names from the schema
3. ALWAYS prefix table names with the schema name 'college.' (e.g., college.student_stress_survey)
4. Include appropriate WHERE clauses, JOINs, and ORDER BY as needed
5. Limit results to reasonable numbers (use LIMIT when appropriate)
6. Handle case-insensitive searches with ILIKE when searching text
7. Return only SELECT statements (no INSERT, UPDATE, DELETE)

Respond in JSON format:
{
  "sql": "your SQL query here",
  "explanation": "brief explanation of what the query does",
  "confidence": 0.95
}
`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      // Parse JSON response
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('Invalid response format from Gemini');
      }

      const parsed = JSON.parse(jsonMatch[0]);

      // Log the generated SQL for debugging
      console.log('\n🔍 Generated SQL Query:');
      console.log('📝 Natural Language:', naturalLanguageQuery);
      console.log('🗄️ Generated SQL:', parsed.sql);
      console.log('💡 Explanation:', parsed.explanation);
      console.log('🎯 Confidence:', parsed.confidence || 0.8);
      console.log('');

      return {
        sql: parsed.sql,
        explanation: parsed.explanation,
        confidence: parsed.confidence || 0.8,
      };
    } catch (error) {
      console.error('SQL generation error:', error);
      return {
        sql: '',
        explanation: '',
        confidence: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async formatResponse(
    originalQuery: string,
    sqlQuery: string,
    queryResults: any[],
    error?: string
  ): Promise<ResponseFormattingResult> {
    try {
      const prompt = `
You are a helpful database assistant. Format the following query results into a natural, conversational response.

Original Question: "${originalQuery}"
SQL Query Used: "${sqlQuery}"
${error ? `Error: ${error}` : `Results: ${JSON.stringify(queryResults, null, 2)}`}

Instructions:
1. Provide a natural, conversational response
2. If there are results, summarize them clearly
3. If there's an error, explain it in user-friendly terms
4. If no results, explain that no matching data was found
5. Keep the response concise but informative
6. Don't include technical SQL details unless relevant

Respond with just the formatted text response (no JSON):
`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return {
        response: text.trim(),
      };
    } catch (error) {
      console.error('Response formatting error:', error);
      return {
        response: error ? 
          `I encountered an error while processing your query: ${error}` :
          `I found ${queryResults.length} result(s) for your query.`,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private buildSchemaContext(schema: DatabaseSchema): string {
    let context = '';

    for (const [tableName, tableInfo] of Object.entries(schema)) {
      context += `\nTable: ${tableName}\n`;
      if (tableInfo.description) {
        context += `Description: ${tableInfo.description}\n`;
      }
      context += 'Columns:\n';

      for (const column of tableInfo.columns) {
        context += `  - ${column.column_name} (${column.data_type})`;
        if (column.is_nullable === 'NO') {
          context += ' NOT NULL';
        }
        if (column.column_default) {
          context += ` DEFAULT ${column.column_default}`;
        }
        context += '\n';
      }
    }

    // Add critical constraint information
    context += `\n⚠️  IMPORTANT CONSTRAINTS:
- student_stress_levels has 23 columns, student_stress_survey has 28 columns
- NEVER use UNION or UNION ALL between these tables (different column counts will cause errors)
- Use JOINs when combining data from both tables
- Both tables can be joined on the 'id' column
- For queries needing data from both tables, use explicit JOINs with specific column selections
- Example: SELECT ssl.anxiety_level, sss.age FROM college.student_stress_levels ssl JOIN college.student_stress_survey sss ON ssl.id = sss.id`;

    return context;
  }

  async validateQuery(query: string): Promise<{ isValid: boolean; reason?: string }> {
    try {
      const prompt = `
Analyze this SQL query for safety and validity:
"${query}"

Check for:
1. Only SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
2. No dangerous functions or operations
3. Proper SQL syntax
4. No attempts to access system tables or sensitive data

Respond in JSON format:
{
  "isValid": true/false,
  "reason": "explanation if invalid"
}
`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        return { isValid: false, reason: 'Could not validate query' };
      }

      const parsed = JSON.parse(jsonMatch[0]);
      return {
        isValid: parsed.isValid,
        reason: parsed.reason,
      };
    } catch (error) {
      console.error('Query validation error:', error);
      return { isValid: false, reason: 'Validation failed' };
    }
  }

  async validateDatabaseQuery(prompt: string): Promise<{ isValid: boolean; reason?: string }> {
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        return { isValid: false, reason: 'Could not validate query intent' };
      }

      const parsed = JSON.parse(jsonMatch[0]);
      return {
        isValid: parsed.isValid,
        reason: parsed.reason,
      };
    } catch (error) {
      console.error('Database query validation error:', error);
      return { isValid: false, reason: 'Query validation failed' };
    }
  }
}

// Singleton instance
let geminiService: GeminiService | null = null;

export function getGeminiService(): GeminiService {
  if (!geminiService) {
    geminiService = new GeminiService();
  }
  return geminiService;
}
