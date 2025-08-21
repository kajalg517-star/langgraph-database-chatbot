"""
Main Chatbot Agent using Google ADK.
Orchestrates the database query workflow with proper state management.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.genai import types

from ..tools.database_tool import database_tool, database_service
from ..services.gemini_service import gemini_service, DatabaseSchema
from ..config.environment import config
from ..utils.logger import logger, log_agent_interaction


class ChatbotState(BaseModel):
    """State management for the chatbot agent."""
    user_query: str = ""
    is_valid_database_query: bool = False
    database_schema: Optional[DatabaseSchema] = None
    generated_sql: str = ""
    sql_explanation: str = ""
    query_results: List[Dict[str, Any]] = []
    final_response: str = ""
    error: Optional[str] = None
    confidence: float = 0.0
    rejection_reason: Optional[str] = None


async def validate_database_query(user_query: str) -> Dict[str, Any]:
    """
    Tool function to validate if a query is database-related.
    """
    try:
        validation_result = await gemini_service.validate_database_query(user_query)
        
        return {
            "is_valid": validation_result.is_valid,
            "reason": validation_result.reason,
            "user_query": user_query
        }
    except Exception as e:
        logger.error("Query validation failed", error=str(e))
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "user_query": user_query
        }


async def load_database_schema() -> Dict[str, Any]:
    """
    Tool function to load database schema information.
    """
    try:
        schema_result = await database_service.get_schema_info()
        
        if not schema_result.success:
            return {
                "success": False,
                "error": schema_result.error,
                "schema": {}
            }
        
        # Process schema data into the expected format
        tables = {}
        if schema_result.data:
            current_table = None
            for row in schema_result.data:
                table_name = row.get('table_name')
                if table_name != current_table:
                    current_table = table_name
                    tables[table_name] = {
                        'table_name': table_name,
                        'columns': [],
                        'description': f'Table containing {table_name} data'
                    }
                
                tables[table_name]['columns'].append({
                    'column_name': row.get('column_name'),
                    'data_type': row.get('data_type')
                })
        
        return {
            "success": True,
            "schema": {"tables": tables}
        }
        
    except Exception as e:
        logger.error("Schema loading failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "schema": {}
        }


async def generate_sql_query(user_query: str, schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool function to generate SQL from natural language.
    """
    try:
        # Convert schema data to DatabaseSchema object
        database_schema = DatabaseSchema(tables=schema_data.get("tables", {}))
        
        sql_result = await gemini_service.generate_sql(user_query, database_schema)
        
        return {
            "sql": sql_result.sql,
            "explanation": sql_result.explanation,
            "confidence": sql_result.confidence,
            "success": bool(sql_result.sql)
        }
        
    except Exception as e:
        logger.error("SQL generation failed", error=str(e))
        return {
            "sql": "",
            "explanation": f"Failed to generate SQL: {str(e)}",
            "confidence": 0.0,
            "success": False
        }


async def validate_sql_query(sql_query: str) -> Dict[str, Any]:
    """
    Tool function to validate generated SQL for safety.
    """
    try:
        validation_result = await gemini_service.validate_sql_query(sql_query)
        
        return {
            "is_valid": validation_result.is_valid,
            "reason": validation_result.reason,
            "sql_query": sql_query
        }
        
    except Exception as e:
        logger.error("SQL validation failed", error=str(e))
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "sql_query": sql_query
        }


# The execute_database_query function is now defined in database_tool.py


async def format_final_response(
    user_query: str, 
    sql_query: str, 
    query_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Tool function to format the final response.
    """
    try:
        formatting_result = await gemini_service.format_response(
            user_query, sql_query, query_results
        )
        
        return {
            "response": formatting_result.response,
            "success": True,
            "error": formatting_result.error
        }
        
    except Exception as e:
        logger.error("Response formatting failed", error=str(e))
        return {
            "response": f"I found {len(query_results)} result(s) for your query.",
            "success": False,
            "error": str(e)
        }


# Create function tools for the agent
validate_query_tool = FunctionTool(validate_database_query)
load_schema_tool = FunctionTool(load_database_schema)
generate_sql_tool = FunctionTool(generate_sql_query)
validate_sql_tool = FunctionTool(validate_sql_query)
# database_tool is already created in database_tool.py
format_response_tool = FunctionTool(format_final_response)


def create_chatbot_agent() -> Agent:
    """
    Create and configure the main chatbot agent with all necessary tools.
    """

    instruction = """
You are an intelligent database assistant that helps users query their database using natural language.

Your workflow should follow these steps:

1. **Validate Query**: First, determine if the user's question is database-related using the validate_database_query tool.
   - If not database-related, politely explain that you can only help with database questions.

2. **Load Schema**: If the query is valid, load the database schema using load_database_schema.

3. **Generate SQL**: Use the schema to generate appropriate SQL using generate_sql_query.

4. **Validate SQL**: Ensure the generated SQL is safe using validate_sql_query.

5. **Execute Query**: Run the SQL query using execute_database_query.

6. **Format Response**: Format the results into a natural language response using format_final_response.

Important guidelines:
- Only process database-related questions
- Always validate SQL for security before execution
- Provide clear, helpful responses based on actual data
- If any step fails, explain the issue to the user
- Maintain conversation context and be helpful

Example valid questions:
- "How many students have anxiety levels above 15?"
- "Show me the top 10 students with highest stress levels"
- "What's the average depression score?"
- "Count students by anxiety level"

Example invalid questions:
- "Hello" or "Hi" (greetings)
- "What's the weather?" (not database-related)
- "Tell me a joke" (not database-related)
"""

    agent = Agent(
        name="database_chatbot",
        model=config.gemini.model,
        instruction=instruction,
        description="An intelligent database assistant that helps users query their database using natural language",
        tools=[
            validate_query_tool,
            load_schema_tool,
            generate_sql_tool,
            validate_sql_tool,
            database_tool,
            format_response_tool
        ]
    )

    logger.info("Database chatbot agent created successfully")
    return agent


async def test_database_connection() -> bool:
    """Test the database connection."""
    try:
        return await database_service.test_connection()
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False


# Create the singleton agent instance
chatbot_agent = create_chatbot_agent()
