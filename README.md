# 🤖 LangGraph Database Chatbot

A production-ready interactive database chatbot built with **LangGraph**, **Supabase**, and **Gemini AI**. This chatbot allows users to query their database using natural language and get intelligent responses with actual data.

## ✨ Features

- **🔄 Interactive Chat Mode**: Continuous conversation with thread persistence
- **🗄️ Real Database Access**: Connects to actual Supabase database with RPC functions
- **🧠 Smart Query Validation**: Only processes database-related questions
- **🔒 Security First**: SQL injection protection and query validation
- **📊 Actual Data Results**: No mock data - real database queries and results
- **🧵 Thread Persistence**: Maintains conversation context across queries
- **⚡ LangGraph Workflow**: Proper state management and conditional routing
- **🎯 Context7 Patterns**: Clean, maintainable code following best practices

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │───▶│  LangGraph       │───▶│   Supabase      │
│   (Interactive) │    │  Workflow        │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Gemini AI      │
                       │   (Query Gen)    │
                       └──────────────────┘
```

### Core Components

- **LangGraph Workflow**: Manages query processing with nodes and conditional edges
- **Supabase RPC Utility**: Direct database access using Context7 patterns
- **Gemini AI Service**: Natural language to SQL generation and validation
- **Interactive CLI**: Simple, reliable input handling following official patterns

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Supabase account and project
- Google AI Studio API key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   
   Create `.env` file:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SUPABASE_SCHEMA=your_schema_name
   
   # Gemini AI Configuration
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Database Setup**
   
   Create the RPC function in your Supabase SQL editor:
   ```sql
   CREATE OR REPLACE FUNCTION public.execute_college_query(query_text TEXT) 
   RETURNS TABLE(result JSONB) AS $$ 
   BEGIN 
     RETURN QUERY EXECUTE 'SELECT to_jsonb(t) FROM (' || query_text || ') t'; 
   END; 
   $$ LANGUAGE plpgsql SECURITY DEFINER;
   ```

5. **Build and Run**
   ```bash
   npm run build
   npm run chat
   ```

## 💬 Usage

### Interactive Chat Mode
```bash
npm run chat
```

Start an interactive conversation:
```
🤖 Interactive Database Chatbot with LangGraph
Ask me questions about your database in natural language!
⚠️  I can only answer database-related questions.
Type "exit" or "quit" to end the session.

🧵 Session ID: chat_1755713996766_wgvl925d3

💬 Your database question: Show me students with high anxiety levels
```

### Single Query Mode
```bash
npm run query "Count all students in the database"
```

### Example Queries

✅ **Valid Database Questions:**
- "How many students have anxiety levels above 15?"
- "Show me the top 10 students with highest stress levels"
- "What's the average depression score?"
- "Count students by anxiety level"

❌ **Invalid Questions (Will be rejected):**
- "Hello" or "Hi"
- "What's the weather?"
- "Tell me a joke"

## 🛠️ Development

### Project Structure
```
src/
├── cli/interface.ts              # Interactive CLI with official LangGraph patterns
├── config/environment.ts         # Environment configuration
├── services/gemini.ts            # Gemini AI service for NL to SQL
├── utils/
│   ├── logger.ts                 # Structured logging
│   └── supabase-rpc.ts          # Supabase RPC utility (Context7)
├── workflow/chatbot-workflow.ts  # LangGraph workflow implementation
└── index.ts                     # Application entry point
```

### Available Scripts

```bash
npm run build      # Build TypeScript to JavaScript
npm run clean      # Clean dist directory
npm run chat       # Start interactive chat mode
npm run query      # Run single query (requires argument)
npm run test       # Test database connection
```

### Key Technologies

- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Workflow orchestration with state management
- **[Supabase](https://supabase.com)**: PostgreSQL database with RPC functions
- **[Gemini AI](https://ai.google.dev)**: Natural language processing and SQL generation
- **TypeScript**: Type-safe development
- **Context7 Patterns**: Clean, maintainable code architecture

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for database access | ✅ |
| `SUPABASE_SCHEMA` | Database schema name (e.g., 'college') | ✅ |
| `GEMINI_API_KEY` | Google AI Studio API key | ✅ |

### Database Schema

The chatbot expects your database to have tables with student data. Example schema:
- `student_stress_levels`: Student mental health data
- `student_stress_survey`: Survey responses

## 🎯 Features in Detail

### LangGraph Workflow
- **Query Validation**: Filters non-database questions
- **Schema Loading**: Automatic database schema discovery
- **SQL Generation**: Natural language to SQL conversion
- **Security Validation**: SQL injection protection
- **Query Execution**: Safe database query execution
- **Response Formatting**: Natural language response generation

### Thread Persistence
Each chat session maintains context:
```typescript
const threadId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
// All queries in the session use the same threadId for context
```

### Security Features
- SQL injection prevention
- Query validation and sanitization
- Service role key protection
- Schema-restricted access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph Team** for the excellent workflow framework
- **Supabase** for the powerful database platform
- **Google AI** for Gemini API
- **Context7** for clean code patterns

---

**Built with ❤️ using LangGraph, Supabase, and Gemini AI**
