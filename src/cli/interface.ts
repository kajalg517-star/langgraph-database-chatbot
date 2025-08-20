import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as readline from 'readline';
import { processQuery } from '../workflow/chatbot-workflow.js';

export class ChatbotCLI {
  private program: Command;
  private rl: readline.Interface;

  constructor() {
    this.program = new Command();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    this.setupCommands();
  }

  private setupCommands() {
    this.program
      .name('chatbot')
      .description('Natural Language Database Chatbot powered by LangGraph and Gemini')
      .version('1.0.0');

    this.program
      .command('chat')
      .description('Start interactive chat session')
      .action(this.startInteractiveChat.bind(this));

    this.program
      .command('query')
      .description('Execute a single query')
      .argument('<query>', 'Natural language query to execute')
      .action(this.executeSingleQuery.bind(this));

    this.program
      .command('test')
      .description('Test database connection')
      .action(this.testConnection.bind(this));
  }

  private async startInteractiveChat() {
    console.log(chalk.blue.bold('\n🤖 Interactive Database Chatbot with LangGraph'));
    console.log(chalk.gray('Ask me questions about your database in natural language!'));
    console.log(chalk.yellow('⚠️  I can only answer database-related questions.'));
    console.log(chalk.gray('Type "exit" or "quit" to end the session.\n'));

    // Create a unique thread ID for this chat session
    const threadId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    console.log(chalk.gray(`🧵 Session ID: ${threadId}\n`));

    // Use the official LangGraph interactive pattern - simple and reliable
    await this.runOfficialLangGraphPattern(threadId);

    await this.cleanup();
  }

  private async runOfficialLangGraphPattern(threadId: string) {
    // This follows the exact pattern from LangGraph official documentation
    // https://blog.futuresmart.ai/langgraph-tutorial-for-beginners
    while (true) {
      try {
        // Simple input prompt - no complex readline interface
        const userInput = await this.getInput('💬 Your database question: ');

        if (userInput.toLowerCase().trim() === 'exit' || userInput.toLowerCase().trim() === 'quit') {
          console.log(chalk.yellow('\n👋 Goodbye! Your conversation history has been saved.'));
          break;
        }

        if (!userInput.trim()) {
          console.log(chalk.red('Please enter a valid question.\n'));
          continue;
        }

        // Process the query using LangGraph with thread persistence
        const spinner = ora('Processing your database query...').start();

        try {
          const response = await processQuery(userInput, threadId);
          spinner.stop();

          console.log(chalk.green.bold('🔍 Response:'));
          console.log(chalk.white(this.formatResponse(response)));
          console.log(); // Add spacing
        } catch (error) {
          spinner.stop();
          console.error(chalk.red.bold('❌ Error:'));
          console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
          console.log(chalk.gray('You can continue asking questions...\n'));
        }
      } catch (error) {
        console.error(chalk.red('Input error:'), error);
        console.log(chalk.gray('Please try again or type "exit" to quit.\n'));
      }
    }
  }

  private async getInput(prompt: string): Promise<string> {
    // Simple input method that works reliably in all environments
    return new Promise((resolve) => {
      process.stdout.write(chalk.cyan(prompt));

      process.stdin.resume();
      process.stdin.setEncoding('utf8');

      const onData = (data: string) => {
        const input = data.toString().trim();
        process.stdin.removeListener('data', onData);
        process.stdin.pause();
        resolve(input);
      };

      process.stdin.on('data', onData);
    });
  }

  private async executeSingleQuery(query: string) {
    console.log(chalk.blue.bold('\n🤖 Database Chatbot with LangGraph'));
    console.log(chalk.gray(`Processing: "${query}"`));
    console.log(chalk.yellow('⚠️  I can only answer database-related questions.\n'));

    await this.processQueryWithLangGraph(query);
    await this.cleanup();
  }

  private async processQueryWithLangGraph(query: string) {
    const spinner = ora('Processing your database query through LangGraph workflow...').start();

    try {
      const response = await processQuery(query);
      spinner.stop();

      console.log(chalk.green.bold('🔍 Response:'));
      console.log(chalk.white(this.formatResponse(response)));
    } catch (error) {
      spinner.stop();
      console.error(chalk.red.bold('❌ Error:'));
      console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    }
  }



  private async testConnection() {
    console.log(chalk.blue.bold('\n🔧 Testing Database Connection with LangGraph'));

    const spinner = ora('Testing database connection through LangGraph workflow...').start();

    try {
      const testResponse = await processQuery('Show me the available tables');

      spinner.succeed('Database connection successful!');
      console.log(chalk.green('\n✅ Connection test passed'));
      console.log(chalk.gray('Sample query result:'));
      console.log(chalk.white(this.formatResponse(testResponse)));
    } catch (error) {
      spinner.fail('Database connection failed!');
      console.error(chalk.red('\n❌ Connection test failed:'));
      console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    }

    await this.cleanup();
  }

  private formatResponse(response: string): string {
    // Add some basic formatting to make responses more readable
    return response
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .join('\n');
  }



  private async cleanup() {
    this.rl.close();
  }

  async run(args: string[]) {
    try {
      await this.program.parseAsync(args);
    } catch (error) {
      console.error(chalk.red('CLI Error:'), error);
      process.exit(1);
    }
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log(chalk.yellow('\n\n👋 Shutting down gracefully...'));
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log(chalk.yellow('\n\n👋 Shutting down gracefully...'));
  process.exit(0);
});
