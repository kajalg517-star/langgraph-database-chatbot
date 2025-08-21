"""
Custom Supabase Database Tool for Google ADK.
Provides database access functionality as an ADK tool.
"""

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from supabase import create_client, Client
from google.adk.tools import FunctionTool

from ..config.environment import config
from ..utils.logger import logger, log_query_processing


class DatabaseQueryResult(BaseModel):
    """Result of a database query."""
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    row_count: int = 0
    success: bool = False


class SupabaseDatabaseService:
    """
    Service for executing SQL queries against Supabase database.
    Maintains compatibility with the original TypeScript RPC approach.
    """

    def __init__(self):
        self._client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Supabase client."""
        try:
            self._client = create_client(
                config.supabase.url,
                config.supabase.service_role_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Supabase client", error=str(e))
            raise
    
    async def execute_query(self, sql_query: str) -> DatabaseQueryResult:
        """Execute the database query asynchronously."""
        if not self._client:
            return DatabaseQueryResult(
                error="Database client not initialized",
                success=False
            )

        sql_query = sql_query.strip()
        
        # Security validation - only allow SELECT queries
        if not self._is_safe_query(sql_query):
            error_msg = "Only SELECT queries are allowed for security reasons"
            log_query_processing(
                logger,
                user_query="N/A",
                sql_query=sql_query,
                error=error_msg
            )
            return DatabaseQueryResult(
                error=error_msg,
                success=False
            )
        
        try:
            # Use the same RPC function as the TypeScript implementation
            result = await self._execute_rpc_query(sql_query)
            
            log_query_processing(
                logger,
                user_query="N/A",
                sql_query=sql_query,
                results_count=result.row_count
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Database query failed: {str(e)}"
            log_query_processing(
                logger,
                user_query="N/A",
                sql_query=sql_query,
                error=error_msg
            )
            return DatabaseQueryResult(
                error=error_msg,
                success=False
            )
    
    async def _execute_rpc_query(self, sql_query: str) -> DatabaseQueryResult:
        """Execute query using the same RPC function as TypeScript implementation."""
        try:
            # Clean SQL - remove trailing semicolon and extra whitespace
            clean_sql = sql_query.strip().rstrip(';')
            
            # Call the same RPC function: execute_college_query
            response = self._client.rpc('execute_college_query', {
                'query_text': clean_sql
            }).execute()
            
            if response.data is None:
                return DatabaseQueryResult(
                    error="No data returned from query",
                    success=False
                )
            
            # Extract actual data from JSONB result format
            # The RPC function returns [{result: {...}}, {result: {...}}]
            actual_data = []
            if isinstance(response.data, list):
                for row in response.data:
                    if isinstance(row, dict) and 'result' in row:
                        actual_data.append(row['result'])
                    else:
                        actual_data.append(row)
            
            return DatabaseQueryResult(
                data=actual_data,
                row_count=len(actual_data),
                success=True
            )
            
        except Exception as e:
            return DatabaseQueryResult(
                error=f"RPC execution failed: {str(e)}",
                success=False
            )
    
    def _is_safe_query(self, sql_query: str) -> bool:
        """Validate that the query is safe to execute (SELECT only)."""
        # Convert to lowercase and remove extra whitespace
        query_lower = sql_query.lower().strip()
        
        # Check if it starts with SELECT
        if not query_lower.startswith('select'):
            return False
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'insert', 'update', 'delete', 'drop', 'create', 'alter',
            'truncate', 'grant', 'revoke', 'exec', 'execute',
            'sp_', 'xp_', '--', '/*', '*/'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        return True
    
    async def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            if not self._client:
                return False
            
            # Simple test query
            test_result = await self._execute_rpc_query("SELECT 1 as test")
            return test_result.success
            
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            return False
    
    async def get_schema_info(self) -> DatabaseQueryResult:
        """Get database schema information."""
        schema_query = f"""
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_schema = '{config.supabase.schema}'
        ORDER BY table_name, ordinal_position
        """
        
        return await self._execute_rpc_query(schema_query)


# Create service instance
database_service = SupabaseDatabaseService()

# Create function tool for ADK
async def execute_database_query(sql_query: str) -> Dict[str, Any]:
    """
    Execute SQL queries against the database. Use this tool to retrieve data
    from the database based on user questions. Only SELECT queries are allowed
    for security reasons.

    Args:
        sql_query: The SQL query to execute

    Returns:
        Dictionary with query results or error information
    """
    result = await database_service.execute_query(sql_query)

    return {
        "success": result.success,
        "data": result.data or [],
        "row_count": result.row_count,
        "error": result.error
    }

# Create the ADK function tool
database_tool = FunctionTool(func=execute_database_query)
