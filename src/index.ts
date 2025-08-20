#!/usr/bin/env node

import { ChatbotCLI } from './cli/interface.js';
import { getSupabaseRpcUtil } from './utils/supabase-rpc.js';
import chalk from 'chalk';

// Prevent process from exiting on unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error(chalk.red('🚨 Unhandled Promise Rejection:'), reason);
  console.error(chalk.gray('Promise:'), promise);
  console.log(chalk.yellow('⚠️  The application will continue running...'));
});

// Prevent process from exiting on uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error(chalk.red('🚨 Uncaught Exception:'), error);
  console.log(chalk.yellow('⚠️  The application will continue running...'));
});

async function main() {
  try {
    // Check if environment variables are properly configured
    const requiredEnvVars = [
      'GEMINI_API_KEY',
      'SUPABASE_URL',
      'SUPABASE_SERVICE_ROLE_KEY'
    ];

    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
      console.error(chalk.red.bold('❌ Configuration Error'));
      console.error(chalk.red('Missing required environment variables:'));
      missingVars.forEach(varName => {
        console.error(chalk.red(`  - ${varName}`));
      });
      console.error(chalk.yellow('\nPlease create a .env file with the required variables.'));
      console.error(chalk.yellow('See .env.example for reference.'));
      process.exit(1);
    }

    // Test database connection
    console.log(chalk.blue('🔄 Testing database connection...'));
    const rpcUtil = getSupabaseRpcUtil();
    const connectionOk = await rpcUtil.testRpcConnection();

    if (!connectionOk) {
      console.error(chalk.red('❌ Database connection failed'));
      process.exit(1);
    }

    console.log(chalk.green('✅ Database connection successful'));

    const cli = new ChatbotCLI();
    await cli.run(process.argv);
  } catch (error) {
    console.error(chalk.red.bold('❌ Application Error:'));
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(chalk.red.bold('❌ Fatal Error:'));
  console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
  process.exit(1);
});
