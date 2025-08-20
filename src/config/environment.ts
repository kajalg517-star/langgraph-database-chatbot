import { config as dotenvConfig } from 'dotenv';
import { z } from 'zod';

// Load environment variables
dotenvConfig();

// Environment validation schema
const envSchema = z.object({
  GEMINI_API_KEY: z.string().min(1, 'Gemini API key is required'),
  SUPABASE_URL: z.string().url('Valid Supabase URL is required'),
  SUPABASE_ANON_KEY: z.string().min(1, 'Supabase anonymous key is required'),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1, 'Supabase service role key is required'),
  DATABASE_SCHEMA: z.string().default('public'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  CLI_TIMEOUT: z.string().transform(val => parseInt(val, 10)).default('30000'),
});

// Validate and export environment configuration
export const env = envSchema.parse(process.env);

// Configuration object for easy access
export const config = {
  gemini: {
    apiKey: env.GEMINI_API_KEY,
  },
  supabase: {
    url: env.SUPABASE_URL,
    anonKey: env.SUPABASE_ANON_KEY,
    serviceRoleKey: env.SUPABASE_SERVICE_ROLE_KEY,
    schema: env.DATABASE_SCHEMA,
  },
  app: {
    logLevel: env.LOG_LEVEL,
    cliTimeout: env.CLI_TIMEOUT,
  },
} as const;

// Type exports
export type Config = typeof config;
export type LogLevel = typeof env.LOG_LEVEL;
