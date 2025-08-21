# 🤖 Database Chatbot with Google ADK

A production-ready interactive database chatbot built with **Google's Agent Development Kit (ADK)**, **Supabase**, and **Gemini AI**. This implementation leverages ADK's agent-first architecture for enhanced performance and seamless Google ecosystem integration.

## ✨ Features

- **🔄 Interactive Chat Mode**: Continuous conversation with session persistence
- **🗄️ Real Database Access**: Connects to actual Supabase database with direct SQL execution
- **🧠 Smart Query Validation**: Only processes database-related questions using ADK agents
- **🔒 Security First**: SQL injection protection and query validation
- **📊 Actual Data Results**: No mock data - real database queries and results
- **🧵 Session Persistence**: Maintains conversation context across queries using ADK sessions
- **⚡ Google ADK Architecture**: Modern agent-based workflow with proper state management
- **🎯 Google Integration**: Native integration with Gemini and Google Cloud services

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │───▶│  Google ADK      │───▶│   Supabase      │
│   (Interactive) │    │  Agent           │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Gemini AI      │
                       │   (Query Gen)    │
                       └──────────────────┘
```

### Core Components

- **Google ADK Agent**: Manages query processing with tools and state management
- **Database Tool**: Direct Supabase/PostgreSQL access using custom ADK tool
- **Gemini AI Integration**: Natural language to SQL generation and validation
- **Interactive CLI**: Python-based CLI with ADK Runner integration
- **Session Service**: ADK session management for conversation persistence

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ and pip
- Supabase account and project
- Google AI Studio API key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   
   Create `.env` file:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SUPABASE_SCHEMA=your_schema_name
   
   # Gemini AI Configuration
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Database Setup**
   
   Use the same RPC function from the original implementation:
   ```sql
   CREATE OR REPLACE FUNCTION public.execute_college_query(query_text TEXT) 
   RETURNS TABLE(result JSONB) AS $$ 
   BEGIN 
     RETURN QUERY EXECUTE 'SELECT to_jsonb(t) FROM (' || query_text || ') t'; 
   END; 
   $$ LANGUAGE plpgsql SECURITY DEFINER;
   ```

6. **Run the Chatbot**
   ```bash
   python main.py chat
   ```

## 💬 Usage

### Interactive Chat Mode
```bash
python main.py chat
```

### Single Query Mode
```bash
python main.py query "Count all students in the database"
```

### Test Database Connection
```bash
python main.py test
```

## 🛠️ Development

### Project Structure
```
chatbot/
├── src/
│   ├── agents/
│   │   └── chatbot_agent.py      # Main ADK agent implementation
│   ├── tools/
│   │   └── database_tool.py      # Custom Supabase database tool
│   ├── services/
│   │   └── gemini_service.py     # Gemini AI integration
│   ├── cli/
│   │   └── interface.py          # CLI interface with ADK Runner
│   ├── config/
│   │   └── environment.py        # Environment configuration
│   └── utils/
│       └── logger.py             # Logging utilities
├── tests/
├── requirements.txt
├── main.py                       # Application entry point
└── README.md
```

### Key Technologies

- **[Google ADK](https://github.com/google/adk-python)**: Agent Development Kit for Python
- **[Supabase](https://supabase.com)**: PostgreSQL database with direct SQL access
- **[Gemini AI](https://ai.google.dev)**: Natural language processing and SQL generation
- **Python 3.9+**: Modern Python with type hints and async support

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for database access | ✅ |
| `SUPABASE_SCHEMA` | Database schema name (e.g., 'college') | ✅ |
| `GEMINI_API_KEY` | Google AI Studio API key | ✅ |

## 🎯 Migration from TypeScript

This Python implementation maintains full feature parity with the original TypeScript version while leveraging Google ADK's advantages:

### Key Improvements
- **Agent-First Architecture**: Built specifically for AI agent workflows
- **Better Google Integration**: Native Gemini and Google Cloud integration
- **Simplified State Management**: ADK handles session and state persistence
- **Enhanced Tool System**: Rich ecosystem of pre-built and custom tools
- **Production Ready**: Designed for scalable deployment

### Maintained Features
- All original CLI commands and functionality
- Same database integration and RPC functions
- Identical query validation and security measures
- Thread persistence and session management
- Interactive and single-query modes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK Team** for the excellent agent development framework
- **Supabase** for the powerful database platform
- **Google AI** for Gemini API
- **Original TypeScript Implementation** for the solid foundation

---

**Built with ❤️ using Google ADK, Supabase, and Gemini AI**
