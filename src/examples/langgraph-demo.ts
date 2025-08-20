#!/usr/bin/env node

/**
 * LangGraph Chatbot Demo
 * 
 * This demo shows how the LangGraph workflow processes different types of queries:
 * 1. Valid database queries - processed through the full workflow
 * 2. Invalid non-database queries - rejected with helpful message
 * 3. Error handling - graceful error management
 */

import { processQuery } from '../workflow/chatbot-workflow.js';
import chalk from 'chalk';

async function runDemo() {
  console.log(chalk.blue.bold('\n🚀 LangGraph Database Chatbot Demo\n'));
  
  const testQueries = [
    {
      type: 'Valid Database Query',
      query: 'Show me all tables in the database',
      description: 'This should be processed through the full LangGraph workflow'
    },
    {
      type: 'Valid Database Query',
      query: 'Count the number of users',
      description: 'Another valid database query'
    },
    {
      type: 'Invalid Query - General Conversation',
      query: 'What is the weather like today?',
      description: 'This should be rejected as non-database related'
    },
    {
      type: 'Invalid Query - Personal Question',
      query: 'How are you doing?',
      description: 'This should be rejected as non-database related'
    },
    {
      type: 'Valid Database Query',
      query: 'What columns does the users table have?',
      description: 'Schema-related query that should be processed'
    },
    {
      type: 'Invalid Query - General Knowledge',
      query: 'Explain quantum physics',
      description: 'This should be rejected as non-database related'
    }
  ];

  for (let i = 0; i < testQueries.length; i++) {
    const test = testQueries[i];
    
    console.log(chalk.cyan.bold(`\n--- Test ${i + 1}: ${test.type} ---`));
    console.log(chalk.gray(`Query: "${test.query}"`));
    console.log(chalk.gray(`Expected: ${test.description}`));
    console.log(chalk.yellow('\nProcessing through LangGraph workflow...\n'));
    
    try {
      const response = await processQuery(test.query);
      
      console.log(chalk.green.bold('✅ Response:'));
      console.log(chalk.white(response));
      
    } catch (error) {
      console.log(chalk.red.bold('❌ Error:'));
      console.log(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    }
    
    console.log(chalk.gray('\n' + '='.repeat(80)));
    
    // Add a small delay between queries for better readability
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log(chalk.blue.bold('\n🎉 Demo completed!\n'));
  console.log(chalk.yellow('Key observations:'));
  console.log(chalk.white('• Database-related queries are processed through the full workflow'));
  console.log(chalk.white('• Non-database queries are rejected with helpful guidance'));
  console.log(chalk.white('• The LangGraph manages state and flow between nodes automatically'));
  console.log(chalk.white('• Error handling is built into the workflow\n'));
}

// Run the demo if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runDemo().catch(console.error);
}

export { runDemo };
