# Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Build the Application**
   ```bash
   npm run build
   ```

4. **Test the Setup**
   ```bash
   node test-basic.js
   ```

## Required API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Supabase Configuration
1. Create a new project at [Supabase](https://supabase.com)
2. Go to Settings > API
3. Copy the following values to your `.env` file:
   - `SUPABASE_URL`: Your project URL
   - `SUPABASE_ANON_KEY`: Your anon/public key
   - `SUPABASE_SERVICE_ROLE_KEY`: Your service role key (keep this secret!)

## Usage Examples

### Interactive Chat
```bash
npm run chat
```

### Single Query
```bash
npm run query "Show me all users from the last 30 days"
```

### Test Connection
```bash
npm run test-connection
```

## Sample Database Setup

If you need a sample database to test with, here's a simple schema you can create in Supabase:

```sql
-- Create a users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  city VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample data
INSERT INTO users (name, email, city) VALUES
('John Doe', 'john@example.com', 'New York'),
('Jane Smith', 'jane@example.com', 'California'),
('Bob Johnson', 'bob@example.com', 'Texas');

-- Create an orders table
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  product_name VARCHAR(100) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  order_date TIMESTAMP DEFAULT NOW()
);

-- Insert sample orders
INSERT INTO orders (user_id, product_name, amount) VALUES
(1, 'Laptop', 999.99),
(2, 'Phone', 599.99),
(1, 'Mouse', 29.99);
```

## Example Queries

Once your database is set up, try these natural language queries:

- "Show me all users"
- "How many users are from California?"
- "What are the recent orders?"
- "Show me users and their total order amounts"
- "List all products ordered in the last week"

## Troubleshooting

### Common Issues

1. **"Configuration Error" on startup**
   - Make sure all required environment variables are set in `.env`
   - Check that your API keys are valid

2. **"Database connection failed"**
   - Verify your Supabase URL and keys
   - Ensure your Supabase project is active
   - Check that the service role key has the necessary permissions

3. **"Gemini API Error"**
   - Verify your Gemini API key is correct
   - Check your API quota and billing status
   - Ensure you have internet connectivity

4. **"MCP Server Issues"**
   - Make sure `npx` is available in your PATH
   - Try running `npx @supabase/mcp-server-postgrest --help` manually
   - Check if the MCP server package is properly installed

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
LOG_LEVEL=debug npm run chat
```

### Manual Testing

You can test individual components:

```bash
# Test the workflow
node -e "
import('./dist/workflow/chatbot-workflow.js').then(m => {
  const workflow = m.getChatbotWorkflow();
  console.log('Workflow loaded successfully');
});
"

# Test Gemini service
node -e "
import('./dist/services/gemini.js').then(m => {
  const service = m.getGeminiService();
  console.log('Gemini service loaded successfully');
});
"
```

## Development

### Project Structure
```
src/
├── cli/           # CLI interface
├── config/        # Configuration management
├── services/      # External service integrations
├── utils/         # Utilities and logging
├── workflow/      # Main workflow logic
└── index.ts       # Application entry point
```

### Available Scripts
- `npm run dev` - Development mode with hot reload
- `npm run build` - Build for production
- `npm run clean` - Clean build artifacts
- `npm run chat` - Start interactive chat
- `npm run query` - Execute single query
- `npm run test-connection` - Test database connection

## Next Steps

1. Set up your real API keys in `.env`
2. Create or connect to your Supabase database
3. Test the connection with `npm run test-connection`
4. Start chatting with your database using `npm run chat`

For more detailed information, see the main README.md file.
