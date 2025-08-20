import { StateGraph, Annotation, START, END } from '@langchain/langgraph';
import { MemorySaver } from '@langchain/langgraph';
import { getSupabaseRpcUtil } from '../utils/supabase-rpc.js';
import { getGeminiService } from '../services/gemini.js';
import { logger } from '../utils/logger.js';

// Simple schema interface for the RPC approach
interface DatabaseSchema {
  [tableName: string]: {
    table_name: string;
    columns: Array<{
      column_name: string;
      data_type: string;
    }>;
    description: string;
  };
}

// Define the state annotation for our LangGraph workflow
export const ChatbotStateAnnotation = Annotation.Root({
  userQuery: Annotation<string>,
  isValidDatabaseQuery: Annotation<boolean>,
  databaseSchema: Annotation<DatabaseSchema>,
  generatedSQL: Annotation<string>,
  sqlExplanation: Annotation<string>,
  queryResults: Annotation<any[]>,
  finalResponse: Annotation<string>,
  error: Annotation<string>,
  confidence: Annotation<number>,
  rejectionReason: Annotation<string>,
});

export type ChatbotState = typeof ChatbotStateAnnotation.State;

// Node 1: Validate if the query is database-related
async function validateDatabaseQuery(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('🔍 Validating if query is database-related...');
    logger.info(`📝 User Query: ${state.userQuery}`);

    const geminiService = getGeminiService();

    const validationPrompt = `
You are a database query validator. Determine if the following user query is related to database operations, data retrieval, or database management.

User Query: "${state.userQuery}"

Database-related queries include:
- Asking for data from tables (SELECT operations)
- Questions about table structure, columns, or schema
- Data analysis questions that require database queries
- Questions about relationships between data
- Requests to find, count, filter, or aggregate data
- Questions about database contents

Non-database queries include:
- General conversation
- Questions about topics unrelated to data
- Requests for explanations of concepts not related to the database
- Personal questions
- Weather, news, or other general information

Respond with JSON format:
{
  "isValid": true/false,
  "reason": "explanation of why this is or isn't a database query"
}
`;

    const result = await geminiService.validateDatabaseQuery(validationPrompt);

    if (!result.isValid) {
      logger.warn(`❌ Query rejected: ${result.reason}`);
      return {
        isValidDatabaseQuery: false,
        rejectionReason: result.reason || 'Query is not related to database operations',
      };
    }

    logger.info('✅ Query validated as database-related');
    return {
      isValidDatabaseQuery: true,
    };
  } catch (error) {
    logger.error('Query validation failed', error);
    return {
      isValidDatabaseQuery: false,
      error: `Query validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// Node 2: Load database schema
async function loadDatabaseSchema(_state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('📊 Loading database schema...');

    // Create accurate schema based on actual database structure
    const schema: DatabaseSchema = {
      'student_stress_levels': {
        table_name: 'student_stress_levels',
        columns: [
          { column_name: 'id', data_type: 'integer' },
          { column_name: 'anxiety_level', data_type: 'integer' },
          { column_name: 'self_esteem', data_type: 'integer' },
          { column_name: 'mental_health_history', data_type: 'integer' },
          { column_name: 'depression', data_type: 'integer' },
          { column_name: 'headache', data_type: 'integer' },
          { column_name: 'blood_pressure', data_type: 'integer' },
          { column_name: 'sleep_quality', data_type: 'integer' },
          { column_name: 'breathing_problem', data_type: 'integer' },
          { column_name: 'noise_level', data_type: 'integer' },
          { column_name: 'living_conditions', data_type: 'integer' },
          { column_name: 'safety', data_type: 'integer' },
          { column_name: 'basic_needs', data_type: 'integer' },
          { column_name: 'academic_performance', data_type: 'integer' },
          { column_name: 'study_load', data_type: 'integer' },
          { column_name: 'teacher_student_relationship', data_type: 'integer' },
          { column_name: 'future_career_concerns', data_type: 'integer' },
          { column_name: 'social_support', data_type: 'integer' },
          { column_name: 'peer_pressure', data_type: 'integer' },
          { column_name: 'extracurricular_activities', data_type: 'integer' },
          { column_name: 'bullying', data_type: 'integer' },
          { column_name: 'stress_level', data_type: 'integer' },
          { column_name: 'created_at', data_type: 'timestamp with time zone' },
        ],
        description: 'Student stress levels data with comprehensive mental health and environmental factors (23 columns)',
      },
      'student_stress_survey': {
        table_name: 'student_stress_survey',
        columns: [
          { column_name: 'id', data_type: 'integer' },
          { column_name: 'gender', data_type: 'integer' },
          { column_name: 'age', data_type: 'integer' },
          { column_name: 'recent_stress', data_type: 'integer' },
          { column_name: 'rapid_heartbeat', data_type: 'integer' },
          { column_name: 'anxiety_tension', data_type: 'integer' },
          { column_name: 'sleep_problems', data_type: 'integer' },
          { column_name: 'anxiety_tension_duplicate', data_type: 'integer' },
          { column_name: 'headaches_frequent', data_type: 'integer' },
          { column_name: 'irritated_easily', data_type: 'integer' },
          { column_name: 'concentration_trouble', data_type: 'integer' },
          { column_name: 'sadness_low_mood', data_type: 'integer' },
          { column_name: 'illness_health_issues', data_type: 'integer' },
          { column_name: 'lonely_isolated', data_type: 'integer' },
          { column_name: 'overwhelmed_workload', data_type: 'integer' },
          { column_name: 'peer_competition', data_type: 'integer' },
          { column_name: 'relationship_stress', data_type: 'integer' },
          { column_name: 'professor_difficulties', data_type: 'integer' },
          { column_name: 'unpleasant_work_environment', data_type: 'integer' },
          { column_name: 'no_time_relaxation', data_type: 'integer' },
          { column_name: 'hostel_home_difficulties', data_type: 'integer' },
          { column_name: 'lack_academic_confidence', data_type: 'integer' },
          { column_name: 'lack_subject_confidence', data_type: 'integer' },
          { column_name: 'activities_conflicting', data_type: 'integer' },
          { column_name: 'attend_classes_regularly', data_type: 'integer' },
          { column_name: 'weight_change', data_type: 'integer' },
          { column_name: 'stress_type', data_type: 'text' },
          { column_name: 'created_at', data_type: 'timestamp with time zone' },
        ],
        description: 'Student stress survey responses with detailed demographic and stress indicators (28 columns). Note: Cannot be used with UNION operations with student_stress_levels due to different column counts.',
      }
    };

    logger.info(`✅ Schema loaded with ${Object.keys(schema).length} tables`);

    return {
      databaseSchema: schema,
    };
  } catch (error) {
    logger.error('Failed to load database schema', error);
    return {
      error: `Failed to load database schema: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// Node 3: Generate SQL from natural language
async function generateSQL(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('🧠 Generating SQL from natural language query...');
    logger.info(`📝 User Query: ${state.userQuery}`);
    logger.info(`🗄️ Available Tables: ${Object.keys(state.databaseSchema).join(', ')}`);

    const geminiService = getGeminiService();
    const result = await geminiService.generateSQL(state.userQuery, state.databaseSchema);

    if (result.error) {
      logger.error(`❌ SQL generation failed: ${result.error}`);
      return {
        error: `Failed to generate SQL: ${result.error}`,
      };
    }

    logger.info('✅ SQL generated successfully');
    return {
      generatedSQL: result.sql,
      sqlExplanation: result.explanation,
      confidence: result.confidence,
    };
  } catch (error) {
    logger.error('SQL generation failed', error);
    return {
      error: `SQL generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// Node 4: Validate SQL for security
async function validateSQL(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('🔒 Validating generated SQL for security...');
    logger.info(`🔍 SQL to validate: ${state.generatedSQL}`);

    const geminiService = getGeminiService();
    const validation = await geminiService.validateQuery(state.generatedSQL);

    if (!validation.isValid) {
      logger.warn(`❌ SQL validation failed: ${validation.reason}`);
      return {
        error: `Generated SQL is not safe: ${validation.reason}`,
      };
    }

    logger.info('✅ SQL validation passed - query is safe to execute');
    return {}; // SQL is valid, continue
  } catch (error) {
    logger.error('SQL validation failed', error);
    return {
      error: `SQL validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// Node 5: Execute SQL query
async function executeQuery(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('⚡ Executing SQL query against database...');
    logger.info(`🗄️ SQL: ${state.generatedSQL}`);

    const rpcUtil = getSupabaseRpcUtil();
    const result = await rpcUtil.executeRawSql(state.generatedSQL);

    if (result.error) {
      logger.error(`❌ Query execution failed: ${result.error}`);
      return {
        error: `Query execution failed: ${result.error}`,
      };
    }

    logger.info('✅ Query executed successfully');
    logger.info(`📊 Results count: ${result.data?.length || 0}`);
    if (result.data && result.data.length > 0) {
      logger.info(`📋 Sample data: ${JSON.stringify(result.data[0], null, 2)}`);
    } else {
      logger.info('📋 No data returned');
    }

    return {
      queryResults: result.data || [],
    };
  } catch (error) {
    logger.error('Query execution failed', error);
    return {
      error: `Query execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// Node 6: Format response
async function formatResponse(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('📝 Formatting response...');
    const geminiService = getGeminiService();
    const result = await geminiService.formatResponse(
      state.userQuery,
      state.generatedSQL,
      state.queryResults,
      state.error
    );

    logger.info('✅ Response formatted successfully');
    return {
      finalResponse: result.response,
    };
  } catch (error) {
    logger.error('Response formatting failed', error);
    return {
      finalResponse: error instanceof Error ? error.message : 'An error occurred while processing your query.',
    };
  }
}

// Node 7: Handle rejected queries
async function handleRejectedQuery(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('🚫 Handling rejected query...');

    const rejectionMessage = `I can only help you with database-related questions. Your query "${state.userQuery}" appears to be about something else.

${state.rejectionReason}

Please ask me questions about:
- Finding data in the database
- Table structures and columns
- Data analysis and reporting
- Counting, filtering, or aggregating data
- Relationships between data

For example:
- "Show me all users from California"
- "What tables are available in the database?"
- "Count the number of orders from last month"
- "Find the top 5 products by sales"`;

    return {
      finalResponse: rejectionMessage,
    };
  } catch (error) {
    logger.error('Error handling rejected query', error);
    return {
      finalResponse: 'I can only help with database-related questions. Please ask about data, tables, or database operations.',
    };
  }
}

// Node 8: Handle errors
async function handleError(state: ChatbotState): Promise<Partial<ChatbotState>> {
  try {
    logger.info('🔧 Handling error...');
    const geminiService = getGeminiService();

    const result = await geminiService.formatResponse(
      state.userQuery || '',
      state.generatedSQL || '',
      [],
      state.error
    );

    return {
      finalResponse: result.response,
    };
  } catch (error) {
    logger.error('Error handling failed', error);
    return {
      finalResponse: state.error || 'An unexpected error occurred while processing your query.',
    };
  }
}

// Conditional edge functions
function shouldContinueAfterValidation(state: ChatbotState): string {
  if (state.error) {
    return 'handleError';
  }
  if (!state.isValidDatabaseQuery) {
    return 'handleRejectedQuery';
  }
  return 'loadDatabaseSchema';
}

function shouldContinueAfterSchema(state: ChatbotState): string {
  if (state.error) {
    return 'handleError';
  }
  return 'generateSQL';
}

function shouldContinueAfterSQL(state: ChatbotState): string {
  if (state.error) {
    return 'handleError';
  }
  return 'validateSQL';
}

function shouldContinueAfterValidation2(state: ChatbotState): string {
  if (state.error) {
    return 'handleError';
  }
  return 'executeQuery';
}

function shouldContinueAfterExecution(state: ChatbotState): string {
  if (state.error) {
    return 'handleError';
  }
  return 'formatResponse';
}

// Create the LangGraph workflow
function createChatbotGraph() {
  const workflow = new StateGraph(ChatbotStateAnnotation)
    // Add all nodes
    .addNode('validateDatabaseQuery', validateDatabaseQuery)
    .addNode('loadDatabaseSchema', loadDatabaseSchema)
    .addNode('generateSQL', generateSQL)
    .addNode('validateSQL', validateSQL)
    .addNode('executeQuery', executeQuery)
    .addNode('formatResponse', formatResponse)
    .addNode('handleRejectedQuery', handleRejectedQuery)
    .addNode('handleError', handleError)

    // Define the flow
    .addEdge(START, 'validateDatabaseQuery')

    // Conditional edges based on validation
    .addConditionalEdges(
      'validateDatabaseQuery',
      shouldContinueAfterValidation,
      {
        'loadDatabaseSchema': 'loadDatabaseSchema',
        'handleRejectedQuery': 'handleRejectedQuery',
        'handleError': 'handleError',
      }
    )

    // Continue with database operations
    .addConditionalEdges(
      'loadDatabaseSchema',
      shouldContinueAfterSchema,
      {
        'generateSQL': 'generateSQL',
        'handleError': 'handleError',
      }
    )

    .addConditionalEdges(
      'generateSQL',
      shouldContinueAfterSQL,
      {
        'validateSQL': 'validateSQL',
        'handleError': 'handleError',
      }
    )

    .addConditionalEdges(
      'validateSQL',
      shouldContinueAfterValidation2,
      {
        'executeQuery': 'executeQuery',
        'handleError': 'handleError',
      }
    )

    .addConditionalEdges(
      'executeQuery',
      shouldContinueAfterExecution,
      {
        'formatResponse': 'formatResponse',
        'handleError': 'handleError',
      }
    )

    // All terminal nodes go to END
    .addEdge('formatResponse', END)
    .addEdge('handleRejectedQuery', END)
    .addEdge('handleError', END);

  // Compile with memory for state persistence
  const memory = new MemorySaver();
  return workflow.compile({ checkpointer: memory });
}

// Singleton instance
let graphInstance: ReturnType<typeof createChatbotGraph> | null = null;

export function getChatbotWorkflow() {
  if (!graphInstance) {
    graphInstance = createChatbotGraph();
  }
  return graphInstance;
}

// Main processing function (single query with optional thread ID)
export async function processQuery(userQuery: string, threadId?: string): Promise<string> {
  try {
    logger.info(`🚀 Processing query: ${userQuery}`);

    const graph = getChatbotWorkflow();
    const config = {
      configurable: {
        thread_id: threadId || `query_${Date.now()}`
      }
    };

    logger.info(`🧵 Using thread ID: ${config.configurable.thread_id}`);

    const result = await graph.invoke(
      { userQuery },
      config
    );

    logger.info('✅ Query processing completed');
    return result.finalResponse || 'No response generated.';
  } catch (error) {
    logger.error('Workflow execution failed', error);
    return `I encountered an error while processing your query: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}


