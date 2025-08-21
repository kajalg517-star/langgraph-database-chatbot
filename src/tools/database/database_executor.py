"""
⚡ DATABASE EXECUTOR TOOL - Executes SQL queries using the database service

WHAT THIS FILE DOES:
This tool is responsible for executing SQL queries against the database using
the database service layer. It acts as a bridge between the agent/tools layer
and the database service layer.

KEY FEATURES:
- 🔌 Uses the database service interface (database-agnostic)
- 🛡️ Includes safety checks and validation
- 📊 Provides detailed logging and monitoring
- 🔄 Handles errors gracefully with user-friendly messages

SEPARATION OF CONCERNS:
This tool focuses purely on:
- Receiving validated SQL queries
- Executing them via the database service
- Returning formatted results
- Handling execution errors

DATABASE INDEPENDENCE:
- Works with any database service implementation
- No database-specific code or assumptions
- Uses dependency injection for database service
- Completely decoupled from AI logic

SAFETY FEATURES:
- Only executes pre-validated SQL queries
- Uses the database service's safety mechanisms
- Comprehensive error handling and logging
- User-friendly error messages

TECHNICAL DETAILS:
Uses the database service interface to execute queries, ensuring that
the tool works with any database provider (Supabase, PostgreSQL, MySQL, etc.).
"""

from typing import Dict, Any, List
from google.adk.tools import FunctionTool

from ...core.interfaces.database_service_interface import DatabaseServiceInterface
from ...services import database_service
from ...utils.logger import logger


async def execute_database_query(sql_query: str) -> Dict[str, Any]:
    """
    ⚡ EXECUTE DATABASE QUERY - Run SQL query and return results

    WHAT THIS DOES:
    Executes the provided SQL query using the database service and returns
    the results in a format suitable for the agent and response formatting.

    SAFETY ASSUMPTIONS:
    - SQL query has already been validated for safety
    - Query is known to be a SELECT statement
    - Query syntax has been checked

    PROCESS:
    1. Log the query execution attempt
    2. Execute query via database service
    3. Process and format results
    4. Handle any errors gracefully
    5. Return structured response

    Args:
        sql_query: The SQL query to execute (pre-validated)

    Returns:
        Dictionary containing execution results and metadata
    """
    try:
        logger.info("Executing database query", query_preview=sql_query[:100])

        # Execute the query using the database service
        result = await database_service.execute_safe_query(sql_query)

        if result.success:
            logger.info(
                "Database query executed successfully",
                row_count=result.row_count,
                execution_time=result.execution_time
            )

            return {
                "success": True,
                "data": result.data or [],
                "row_count": result.row_count,
                "execution_time": result.execution_time,
                "sql_query": sql_query
            }
        else:
            logger.error("Database query execution failed", error=result.error)

            return {
                "success": False,
                "error": result.error,
                "data": [],
                "row_count": 0,
                "sql_query": sql_query
            }

    except Exception as e:
        logger.error("Database query execution exception", error=str(e), query=sql_query)

        return {
            "success": False,
            "error": f"Query execution failed: {str(e)}",
            "data": [],
            "row_count": 0,
            "sql_query": sql_query
        }

# Create the ADK function tool
database_executor_tool = FunctionTool(execute_database_query)
