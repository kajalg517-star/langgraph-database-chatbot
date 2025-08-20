import { config, type LogLevel } from '../config/environment.js';
import chalk from 'chalk';

export enum LogLevels {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

export class Logger {
  private static instance: Logger;
  private logLevel: LogLevels;

  private constructor() {
    this.logLevel = this.getLogLevelFromConfig(config.app.logLevel);
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private getLogLevelFromConfig(level: LogLevel): LogLevels {
    switch (level) {
      case 'debug':
        return LogLevels.DEBUG;
      case 'info':
        return LogLevels.INFO;
      case 'warn':
        return LogLevels.WARN;
      case 'error':
        return LogLevels.ERROR;
      default:
        return LogLevels.INFO;
    }
  }

  private shouldLog(level: LogLevels): boolean {
    return level >= this.logLevel;
  }

  private formatMessage(level: string, message: string, context?: any): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` ${JSON.stringify(context)}` : '';
    return `[${timestamp}] ${level}: ${message}${contextStr}`;
  }

  debug(message: string, context?: any): void {
    if (this.shouldLog(LogLevels.DEBUG)) {
      console.log(chalk.gray(this.formatMessage('DEBUG', message, context)));
    }
  }

  info(message: string, context?: any): void {
    if (this.shouldLog(LogLevels.INFO)) {
      console.log(chalk.blue(this.formatMessage('INFO', message, context)));
    }
  }

  warn(message: string, context?: any): void {
    if (this.shouldLog(LogLevels.WARN)) {
      console.warn(chalk.yellow(this.formatMessage('WARN', message, context)));
    }
  }

  error(message: string, error?: Error | any, context?: any): void {
    if (this.shouldLog(LogLevels.ERROR)) {
      const errorDetails = error instanceof Error ? {
        message: error.message,
        stack: error.stack,
        name: error.name,
      } : error;
      
      const fullContext = { ...context, error: errorDetails };
      console.error(chalk.red(this.formatMessage('ERROR', message, fullContext)));
    }
  }

  // Specialized logging methods for different components
  database(message: string, context?: any): void {
    this.debug(`[DATABASE] ${message}`, context);
  }

  gemini(message: string, context?: any): void {
    this.debug(`[GEMINI] ${message}`, context);
  }

  workflow(message: string, context?: any): void {
    this.debug(`[WORKFLOW] ${message}`, context);
  }

  cli(message: string, context?: any): void {
    this.debug(`[CLI] ${message}`, context);
  }
}

// Export singleton instance
export const logger = Logger.getInstance();

// Error handling utilities
export class AppError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly isOperational: boolean;

  constructor(
    message: string,
    code: string = 'UNKNOWN_ERROR',
    statusCode: number = 500,
    isOperational: boolean = true
  ) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.isOperational = isOperational;

    Error.captureStackTrace(this, this.constructor);
  }
}

export class DatabaseError extends AppError {
  constructor(message: string, originalError?: Error) {
    super(message, 'DATABASE_ERROR', 500);
    this.name = 'DatabaseError';
    
    if (originalError) {
      this.stack = originalError.stack;
    }
  }
}

export class GeminiError extends AppError {
  constructor(message: string, originalError?: Error) {
    super(message, 'GEMINI_ERROR', 500);
    this.name = 'GeminiError';
    
    if (originalError) {
      this.stack = originalError.stack;
    }
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}

export class ConfigurationError extends AppError {
  constructor(message: string) {
    super(message, 'CONFIGURATION_ERROR', 500);
    this.name = 'ConfigurationError';
  }
}

// Global error handler
export function handleError(error: Error | AppError, context?: string): void {
  if (error instanceof AppError) {
    logger.error(`${context ? `[${context}] ` : ''}${error.message}`, error, {
      code: error.code,
      statusCode: error.statusCode,
      isOperational: error.isOperational,
    });
  } else {
    logger.error(`${context ? `[${context}] ` : ''}Unexpected error: ${error.message}`, error);
  }
}

// Async error wrapper
export function asyncErrorHandler<T extends any[], R>(
  fn: (...args: T) => Promise<R>
): (...args: T) => Promise<R> {
  return async (...args: T): Promise<R> => {
    try {
      return await fn(...args);
    } catch (error) {
      handleError(error as Error, fn.name);
      throw error;
    }
  };
}
