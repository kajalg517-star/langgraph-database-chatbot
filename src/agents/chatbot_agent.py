"""
🤖 MAIN CHATBOT BRAIN - This is the heart of our database chatbot!

WHAT THIS FILE DOES:
This file contains the "brain" of our chatbot that can answer questions about your database.
Think of it like a smart assistant that:
1. Listens to your questions in plain English
2. Figures out if it's about the database
3. Converts your question into database language (SQL)
4. Gets the answer from your database
5. Explains the results back to you in plain English

HOW IT WORKS:
- Uses Google's AI (Gemini) to understand your questions
- Has special "tools" to work with your database
- Follows a step-by-step process to get you accurate answers
- Keeps track of your conversation so you can ask follow-up questions

EXAMPLE CONVERSATION:
You: "How many students have high anxiety?"
Bot: 1. Checks if this is about the database ✓
     2. Looks at database structure to understand what data exists
     3. Creates SQL: "SELECT COUNT(*) FROM students WHERE anxiety_level > 15"
     4. Runs the query on your database
     5. Responds: "There are 23 students with high anxiety levels."

This file orchestrates all these steps using Google's Agent Development Kit (ADK).
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
    """
    📝 CHATBOT MEMORY - Keeps track of what's happening in a conversation

    WHAT THIS IS:
    Think of this like the chatbot's notepad where it writes down:
    - What you asked
    - Whether it's a database question
    - What SQL query it created
    - What results it found
    - Any errors that happened

    WHY WE NEED THIS:
    Just like you might take notes during a conversation to remember what was said,
    the chatbot needs to remember each step of processing your question.
    """
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
    🔍 STEP 1: CHECK IF QUESTION IS ABOUT THE DATABASE

    WHAT THIS DOES:
    Before doing any work, we need to check if your question is actually about the database.

    EXAMPLES:
    ✅ Database questions: "How many students?", "Show me high anxiety levels"
    ❌ Not database: "Hello", "What's the weather?", "Tell me a joke"

    WHY THIS MATTERS:
    We don't want to waste time trying to create database queries for casual conversation.
    This step acts like a smart filter.

    RETURNS:
    - is_valid: True if it's about the database, False if not
    - reason: Explanation of why it was accepted or rejected
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
    📊 STEP 2: LEARN ABOUT YOUR DATABASE STRUCTURE

    WHAT THIS DOES:
    Before creating a query, the chatbot needs to understand your database structure.
    It's like looking at a map before giving directions.

    WHAT IT FINDS:
    - What tables exist (like "students", "courses", "grades")
    - What columns are in each table (like "name", "age", "anxiety_level")
    - What type of data each column holds (numbers, text, dates)

    REAL EXAMPLE:
    Your database might have:
    - Table: "student_stress_survey"
    - Columns: "student_id" (number), "anxiety_level" (number), "depression_score" (number)

    WHY THIS IS IMPORTANT:
    Without knowing the structure, the chatbot can't create accurate database queries.
    It's like trying to find a book in a library without knowing how it's organized.
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
    🧠 STEP 3: TRANSLATE YOUR QUESTION INTO DATABASE LANGUAGE (SQL)

    WHAT THIS DOES:
    This is where the magic happens! The chatbot takes your plain English question
    and converts it into SQL (the language databases understand).

    TRANSLATION EXAMPLES:
    You ask: "How many students have anxiety above 15?"
    Bot creates: "SELECT COUNT(*) FROM student_stress_survey WHERE anxiety_level > 15"

    You ask: "Show me the top 5 most stressed students"
    Bot creates: "SELECT * FROM student_stress_survey ORDER BY stress_level DESC LIMIT 5"

    HOW IT WORKS:
    1. Uses Google's AI (Gemini) to understand your question
    2. Looks at the database structure it learned in Step 2
    3. Combines both to create the perfect SQL query
    4. Includes safety checks to make sure the query is valid

    RETURNS:
    - sql: The actual database query
    - explanation: Plain English explanation of what the query does
    - confidence: How sure the AI is that this query is correct (0-1 scale)
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
    🛡️ STEP 4: SAFETY CHECK - MAKE SURE THE QUERY IS SAFE

    WHAT THIS DOES:
    Before running any query on your database, we double-check that it's safe.
    Think of this like a security guard checking IDs before letting someone into a building.

    SAFETY CHECKS:
    ✅ Only allows SELECT queries (reading data)
    ❌ Blocks DELETE, UPDATE, DROP (changing/deleting data)
    ❌ Blocks dangerous operations that could harm your database
    ❌ Blocks attempts to access system information

    WHY THIS IS CRITICAL:
    Your database contains important information. We never want to accidentally:
    - Delete your data
    - Change your data
    - Access sensitive system information
    - Run malicious code

    EXAMPLE:
    Safe: "SELECT COUNT(*) FROM students"
    Unsafe: "DELETE FROM students" (would delete all your student data!)

    This step ensures we only READ data, never modify it.
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
    💬 STEP 6: TRANSLATE RESULTS BACK TO PLAIN ENGLISH

    WHAT THIS DOES:
    The database returns raw data (numbers, codes, etc.), but you want a friendly answer.
    This step converts the technical results into a conversational response.

    TRANSFORMATION EXAMPLES:

    Raw database result: [{"count": 23}]
    Your question: "How many students have high anxiety?"
    Friendly response: "There are 23 students with high anxiety levels in the database."

    Raw database result: [{"name": "John", "anxiety": 18}, {"name": "Sarah", "anxiety": 19}]
    Your question: "Who has the highest anxiety?"
    Friendly response: "Sarah has the highest anxiety level at 19, followed by John at 18."

    HOW IT WORKS:
    1. Takes your original question
    2. Looks at the SQL query that was used
    3. Analyzes the raw results from the database
    4. Uses AI to create a natural, conversational response
    5. Includes relevant insights and context

    This makes the chatbot feel like talking to a knowledgeable human assistant!
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
    🏗️ CHATBOT ASSEMBLY LINE - PUTTING IT ALL TOGETHER

    WHAT THIS DOES:
    This function is like an assembly line that builds the complete chatbot.
    It takes all the individual "tools" (the functions above) and combines them
    into one smart agent that can handle your database questions.

    THE CHATBOT'S TOOLBOX:
    1. 🔍 Question Validator - Checks if it's about the database
    2. 📊 Schema Loader - Learns your database structure
    3. 🧠 SQL Generator - Converts English to database language
    4. 🛡️ Safety Checker - Makes sure queries are safe
    5. ⚡ Query Executor - Runs the query on your database
    6. 💬 Response Formatter - Converts results back to English

    THE CHATBOT'S PERSONALITY:
    - Helpful and friendly
    - Only answers database-related questions
    - Always explains what it's doing
    - Prioritizes safety and accuracy
    - Maintains conversation context

    THINK OF IT LIKE:
    A knowledgeable librarian who knows exactly where everything is stored,
    can quickly find what you're looking for, and explains it in simple terms.
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
