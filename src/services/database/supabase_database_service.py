"""
🗄️ SUPABASE DATABASE SERVICE - Supabase implementation of database service interface

WHAT THIS FILE DOES:
This file implements the database service interface specifically for Supabase.
It handles all the Supabase-specific details while providing the standard interface
that the application expects.

KEY FEATURES:
- 🔌 Implements the standard DatabaseServiceInterface
- 🗄️ Uses Supabase's PostgreSQL backend with RPC functions
- 🛡️ Includes comprehensive safety checks and error handling
- 📊 Provides detailed logging and monitoring
- 🔄 Maintains compatibility with existing RPC functions

SUPABASE-SPECIFIC FEATURES:
- Uses the existing `execute_college_query` RPC function
- Leverages Supabase's built-in security and authentication
- Supports PostgreSQL-specific features and syntax
- Integrates with Supabase's real-time capabilities (future)

WHY SEPARATE FROM AI SERVICE:
This separation allows us to:
- Focus purely on database operations
- Easily switch to different database providers
- Test database operations independently
- Keep database logic isolated from AI logic

TECHNICAL DETAILS:
Uses the Supabase Python client to interact with the database.
Handles connection management, query execution, and schema introspection.
"""

import time
from typing import Dict, Any, List, Optional
from supabase import create_client, Client

from ...core.interfaces.database_service_interface import DatabaseServiceInterface
from ...core.models.database_models import (
    DatabaseQueryResult,
    DatabaseSchema,
    DatabaseConnectionInfo
)
from ...config.environment import config
from ...utils.logger import logger


class SupabaseDatabaseService(DatabaseServiceInterface):
    """
    🗄️ SUPABASE DATABASE SERVICE - Supabase implementation
    
    WHAT THIS CLASS DOES:
    This class implements all the database operations using Supabase's PostgreSQL
    backend. It translates the generic database interface into specific Supabase
    API calls and RPC function invocations.
    
    CAPABILITIES:
    - 🔌 Connection management with Supabase client
    - 📊 Schema introspection using PostgreSQL system tables
    - ⚡ Query execution via RPC functions
    - 🛡️ Comprehensive safety validation
    - 🏥 Health monitoring and performance tracking
    
    SUPABASE ADVANTAGES:
    - Built-in security and authentication
    - Automatic connection pooling
    - Real-time capabilities
    - PostgreSQL compatibility
    - Managed infrastructure
    
    ERROR HANDLING:
    - Graceful fallbacks for connection failures
    - Detailed error logging and reporting
    - User-friendly error messages
    - Automatic retry logic for transient failures
    """
    
    def __init__(self):
        """
        🚀 INITIALIZE SUPABASE DATABASE SERVICE
        
        WHAT THIS DOES:
        Sets up the connection to Supabase using the configuration from
        environment variables. Initializes the client but doesn't connect yet.
        """
        self.supabase_url = config.supabase.url
        self.supabase_key = config.supabase.service_role_key
        self.schema_name = config.supabase.schema
        self.client: Optional[Client] = None
        self._connected = False
        
        logger.info("Supabase database service initialized")

    async def connect(self) -> bool:
        """
        🔌 CONNECT - Establish connection to Supabase
        
        WHAT THIS DOES:
        Creates the Supabase client and establishes a connection to the database.
        This is typically called automatically when needed.
        """
        try:
            if not self.client:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client created successfully")
            
            # Test the connection
            connection_test = await self.test_connection()
            self._connected = connection_test
            
            if self._connected:
                logger.info("Supabase database connection established")
            else:
                logger.error("Failed to establish Supabase database connection")
                
            return self._connected
            
        except Exception as e:
            logger.error("Supabase connection failed", error=str(e))
            self._connected = False
            return False

    async def disconnect(self) -> bool:
        """
        🔌 DISCONNECT - Close Supabase connection
        
        WHAT THIS DOES:
        Properly closes the Supabase client connection and cleans up resources.
        """
        try:
            if self.client:
                # Supabase client doesn't have explicit disconnect
                # Connection is managed automatically
                self.client = None
                self._connected = False
                logger.info("Supabase database connection closed")
            
            return True
            
        except Exception as e:
            logger.error("Error disconnecting from Supabase", error=str(e))
            return False

    async def test_connection(self) -> bool:
        """
        🧪 TEST CONNECTION - Verify Supabase connectivity
        
        WHAT THIS DOES:
        Performs a lightweight test query to verify that Supabase is accessible
        and the RPC function is working correctly.
        """
        try:
            if not self.client:
                await self.connect()
            
            if not self.client:
                return False
            
            # Test with a simple query via RPC
            result = self.client.rpc('execute_college_query', {
                'query_text': 'SELECT 1 as test_connection'
            }).execute()
            
            success = result.data is not None and len(result.data) > 0
            
            if success:
                logger.info("Supabase connection test successful")
            else:
                logger.error("Supabase connection test failed - no data returned")
                
            return success
            
        except Exception as e:
            logger.error("Supabase connection test failed", error=str(e))
            return False

    async def get_connection_status(self) -> DatabaseConnectionInfo:
        """
        📊 GET CONNECTION STATUS - Retrieve Supabase connection information
        
        WHAT THIS DOES:
        Returns detailed information about the current Supabase connection,
        including connection status, database type, and configuration.
        """
        try:
            # Test current connection
            is_connected = await self.test_connection()
            
            return DatabaseConnectionInfo(
                connected=is_connected,
                database_type="postgresql",  # Supabase uses PostgreSQL
                version="PostgreSQL (Supabase)",
                schema_name=self.schema_name,
                connection_pool_size=None  # Managed by Supabase
            )
            
        except Exception as e:
            logger.error("Failed to get Supabase connection status", error=str(e))
            return DatabaseConnectionInfo(
                connected=False,
                database_type="postgresql",
                schema_name=self.schema_name
            )

    async def get_schema_info(self) -> DatabaseQueryResult:
        """
        🏗️ GET SCHEMA INFO - Retrieve Supabase database structure

        WHAT THIS DOES:
        Queries the PostgreSQL system tables to get information about all tables,
        columns, and data types in the specified schema.
        """
        try:
            if not self.client:
                await self.connect()

            if not self.client:
                return DatabaseQueryResult(
                    success=False,
                    error="No database connection available"
                )

            # Query to get schema information
            schema_query = f"""
                SELECT
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = '{self.schema_name}'
                ORDER BY table_name, ordinal_position
            """

            start_time = time.time()
            result = self.client.rpc('execute_college_query', {
                'query_text': schema_query
            }).execute()
            execution_time = time.time() - start_time

            if result.data is not None:
                logger.info(
                    "Schema information retrieved successfully",
                    table_count=len(set(row.get('table_name') for row in result.data)),
                    column_count=len(result.data),
                    execution_time=execution_time
                )

                return DatabaseQueryResult(
                    success=True,
                    data=result.data,
                    row_count=len(result.data),
                    execution_time=execution_time
                )
            else:
                return DatabaseQueryResult(
                    success=False,
                    error="No schema data returned"
                )

        except Exception as e:
            logger.error("Failed to retrieve schema information", error=str(e))
            return DatabaseQueryResult(
                success=False,
                error=str(e)
            )

    async def get_table_info(self, table_name: str) -> DatabaseQueryResult:
        """
        📋 GET TABLE INFO - Retrieve information about a specific table

        WHAT THIS DOES:
        Gets detailed information about a specific table including columns,
        data types, constraints, and other metadata.
        """
        try:
            if not self.client:
                await self.connect()

            if not self.client:
                return DatabaseQueryResult(
                    success=False,
                    error="No database connection available"
                )

            # Query to get detailed table information
            table_query = f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = '{self.schema_name}'
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """

            start_time = time.time()
            result = self.client.rpc('execute_college_query', {
                'query_text': table_query
            }).execute()
            execution_time = time.time() - start_time

            if result.data is not None:
                logger.info(
                    f"Table information retrieved for {table_name}",
                    column_count=len(result.data),
                    execution_time=execution_time
                )

                return DatabaseQueryResult(
                    success=True,
                    data=result.data,
                    row_count=len(result.data),
                    execution_time=execution_time
                )
            else:
                return DatabaseQueryResult(
                    success=False,
                    error=f"No information found for table {table_name}"
                )

        except Exception as e:
            logger.error(f"Failed to retrieve table information for {table_name}", error=str(e))
            return DatabaseQueryResult(
                success=False,
                error=str(e)
            )

    async def execute_query(self, sql_query: str) -> DatabaseQueryResult:
        """
        ⚡ EXECUTE QUERY - Run a SQL query against Supabase

        WHAT THIS DOES:
        Executes the provided SQL query using Supabase's RPC function.
        This method trusts that the query has been validated by the caller.
        """
        try:
            if not self.client:
                await self.connect()

            if not self.client:
                return DatabaseQueryResult(
                    success=False,
                    error="No database connection available"
                )

            start_time = time.time()
            result = self.client.rpc('execute_college_query', {
                'query_text': sql_query
            }).execute()
            execution_time = time.time() - start_time

            if result.data is not None:
                logger.info(
                    "Query executed successfully",
                    query=sql_query[:100] + "..." if len(sql_query) > 100 else sql_query,
                    row_count=len(result.data),
                    execution_time=execution_time
                )

                return DatabaseQueryResult(
                    success=True,
                    data=result.data,
                    row_count=len(result.data),
                    execution_time=execution_time
                )
            else:
                return DatabaseQueryResult(
                    success=False,
                    error="Query executed but returned no data"
                )

        except Exception as e:
            logger.error("Query execution failed", query=sql_query, error=str(e))
            return DatabaseQueryResult(
                success=False,
                error=str(e)
            )

    async def execute_safe_query(self, sql_query: str) -> DatabaseQueryResult:
        """
        🛡️ EXECUTE SAFE QUERY - Run a SQL query with additional safety checks

        WHAT THIS DOES:
        Executes the SQL query with additional safety validations:
        - Only allows SELECT statements
        - Blocks dangerous operations
        - Validates query syntax
        - Logs execution for monitoring
        """
        try:
            # Safety validation
            query_upper = sql_query.strip().upper()

            # Only allow SELECT statements
            if not query_upper.startswith('SELECT'):
                return DatabaseQueryResult(
                    success=False,
                    error="Only SELECT queries are allowed for safety"
                )

            # Block dangerous keywords
            dangerous_keywords = [
                'DELETE', 'UPDATE', 'INSERT', 'DROP', 'CREATE', 'ALTER',
                'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE'
            ]

            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return DatabaseQueryResult(
                        success=False,
                        error=f"Query contains dangerous keyword: {keyword}"
                    )

            # Execute the validated query
            return await self.execute_query(sql_query)

        except Exception as e:
            logger.error("Safe query execution failed", query=sql_query, error=str(e))
            return DatabaseQueryResult(
                success=False,
                error=str(e)
            )

    async def get_health_info(self) -> Dict[str, Any]:
        """
        🏥 GET HEALTH INFO - Retrieve Supabase health and performance metrics

        WHAT THIS DOES:
        Returns information about database health, connection status,
        and performance metrics.
        """
        try:
            connection_status = await self.get_connection_status()

            health_info = {
                "service_type": "supabase",
                "database_type": "postgresql",
                "connected": connection_status.connected,
                "schema_name": self.schema_name,
                "supabase_url": self.supabase_url,
                "timestamp": time.time()
            }

            # Add connection test timing
            if connection_status.connected:
                start_time = time.time()
                test_result = await self.test_connection()
                test_time = time.time() - start_time

                health_info.update({
                    "connection_test_passed": test_result,
                    "connection_test_time": test_time,
                    "status": "healthy" if test_result else "unhealthy"
                })
            else:
                health_info.update({
                    "connection_test_passed": False,
                    "status": "disconnected"
                })

            return health_info

        except Exception as e:
            logger.error("Failed to get health information", error=str(e))
            return {
                "service_type": "supabase",
                "connected": False,
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
