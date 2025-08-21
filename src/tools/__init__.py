"""
🛠️ TOOLS MODULE - All the specialized tools for database operations

WHAT THIS MODULE CONTAINS:
This module contains all the specialized tools that the chatbot uses to process
your database questions. Each tool has a specific job in the pipeline:

1. 🔍 Query Validator - Checks if questions are database-related
2. 📊 Schema Loader - Learns your database structure
3. 🧠 SQL Generator - Converts English to SQL
4. 🛡️ SQL Validator - Ensures queries are safe
5. 🗄️ Database Tool - Executes queries safely
6. 💬 Response Formatter - Converts results to friendly answers

MODULAR DESIGN:
Each tool is in its own file for better organization and maintainability.
This makes it easy to:
- Understand what each tool does
- Test individual components
- Modify or extend specific functionality
- Debug issues in isolation

IMPORT STRUCTURE:
All tools are available through this module for easy importing throughout the codebase.
"""

# Import all tool functions for easy access
from .query_validator import validate_database_query
from .schema_loader import load_database_schema
from .sql_generator import generate_sql_query
from .sql_validator import validate_sql_query
from .database_executor import database_executor_tool, database_tool
from .response_formatter import format_final_response

# Export all tools for external use
__all__ = [
    'validate_database_query',
    'load_database_schema',
    'generate_sql_query',
    'validate_sql_query',
    'database_executor_tool',
    'database_tool',  # Backward compatibility
    'format_final_response'
]
