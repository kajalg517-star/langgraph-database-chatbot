"""
🏗️ AGENT FACTORY - Assembles the complete chatbot agent

WHAT THIS FILE DOES:
This file is like an assembly line that builds the complete chatbot.
It takes all the individual "tools" and combines them into one smart agent
that can handle your database questions.

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

TECHNICAL DETAILS:
Uses Google ADK's Agent framework to orchestrate multiple specialized tools
into a cohesive conversational AI system. Configures the agent with proper
instructions, tool access, and error handling capabilities.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..config.environment import config
from ..utils.logger import logger
from ..tools import (
    validate_database_query,
    load_database_schema,
    generate_sql_query,
    validate_sql_query,
    database_executor_tool,
    table_discovery_tool,
    table_names_tool,
    format_final_response
)


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
    
    Returns:
        Configured ADK Agent ready to handle database conversations
    """
    
    # Create function tools from our specialized functions
    validate_query_tool = FunctionTool(validate_database_query)
    load_schema_tool = FunctionTool(load_database_schema)
    generate_sql_tool = FunctionTool(generate_sql_query)
    validate_sql_tool = FunctionTool(validate_sql_query)
    # database_executor_tool is already created in database_executor.py
    format_response_tool = FunctionTool(format_final_response)
    
    # Define the agent's personality and instructions
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

    # Create and configure the agent
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
            database_executor_tool,
            table_discovery_tool,
            table_names_tool,
            format_response_tool
        ]
    )
    
    logger.info("Database chatbot agent created successfully")
    return agent
