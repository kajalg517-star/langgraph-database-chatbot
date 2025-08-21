"""
🗄️ DATABASE SERVICE INTERFACE - Abstract base for all database providers

WHAT THIS FILE DOES:
This file defines the contract that all database services must follow. Think of it
like a blueprint that ensures all database providers (Supabase, PostgreSQL, MySQL, etc.)
work the same way from the application's perspective.

WHY WE NEED THIS:
- **Database Flexibility**: Easy to switch between different database providers
- **Extensibility**: Add new database systems without changing existing code
- **Consistency**: All database services provide the same functionality
- **Testing**: Mock database services for testing without real connections
- **Separation of Concerns**: Database operations are completely separate from AI logic

SUPPORTED OPERATIONS:
1. 🔌 Connection Management - Connect, test, and manage database connections
2. 📊 Schema Operations - Retrieve database structure and metadata
3. ⚡ Query Execution - Execute SQL queries safely and efficiently
4. 🛡️ Security - Built-in safety checks and validation

DESIGN PATTERN:
This uses the Strategy Pattern and Abstract Base Class pattern to define
a common interface that all database providers must implement.

FUTURE DATABASE PROVIDERS:
- Supabase (PostgreSQL-based)
- Raw PostgreSQL
- MySQL/MariaDB
- SQLite
- Microsoft SQL Server
- Oracle Database
- MongoDB (with SQL interface)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..models.database_models import (
    DatabaseQueryResult,
    DatabaseSchema,
    DatabaseConnectionInfo
)


class DatabaseServiceInterface(ABC):
    """
    🎯 DATABASE SERVICE INTERFACE - The contract all database providers must follow
    
    WHAT THIS IS:
    This is an abstract base class that defines what methods every database service
    must implement. It's like a contract that ensures consistency across
    different database providers.
    
    WHY THIS MATTERS:
    - The application can work with any database provider that implements this interface
    - Easy to switch from Supabase to PostgreSQL or any other database
    - New database providers just need to implement these methods
    - Testing becomes easier with mock implementations
    - Complete separation from AI/LLM logic
    
    REQUIRED METHODS:
    Every database service must implement these core methods:
    1. Connection Management (connect, disconnect, test_connection)
    2. Schema Operations (get_schema_info, get_table_info)
    3. Query Execution (execute_query, execute_safe_query)
    4. Health Monitoring (get_connection_status, get_health_info)
    """

    @abstractmethod
    async def connect(self) -> bool:
        """
        🔌 CONNECT - Establish connection to the database
        
        WHAT THIS SHOULD DO:
        Initialize and establish a connection to the database using the
        configured credentials and connection parameters.
        
        Returns:
            Boolean indicating if connection was successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        🔌 DISCONNECT - Close database connection
        
        WHAT THIS SHOULD DO:
        Properly close the database connection and clean up resources.
        
        Returns:
            Boolean indicating if disconnection was successful
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        🧪 TEST CONNECTION - Verify database connectivity
        
        WHAT THIS SHOULD DO:
        Perform a lightweight test to verify that the database is accessible
        and responding to queries.
        
        Returns:
            Boolean indicating if the database is accessible
        """
        pass

    @abstractmethod
    async def get_connection_status(self) -> DatabaseConnectionInfo:
        """
        📊 GET CONNECTION STATUS - Retrieve connection information
        
        WHAT THIS SHOULD DO:
        Return detailed information about the current database connection,
        including connection status, database type, version, etc.
        
        Returns:
            DatabaseConnectionInfo with connection details
        """
        pass

    @abstractmethod
    async def get_schema_info(self) -> DatabaseQueryResult:
        """
        🏗️ GET SCHEMA INFO - Retrieve database structure information
        
        WHAT THIS SHOULD DO:
        Query the database system tables to get information about all tables,
        columns, data types, and relationships in the current schema.
        
        Returns:
            DatabaseQueryResult containing schema information
        """
        pass

    @abstractmethod
    async def get_table_info(self, table_name: str) -> DatabaseQueryResult:
        """
        📋 GET TABLE INFO - Retrieve information about a specific table
        
        WHAT THIS SHOULD DO:
        Get detailed information about a specific table including columns,
        data types, constraints, and indexes.
        
        Args:
            table_name: Name of the table to inspect
            
        Returns:
            DatabaseQueryResult containing table information
        """
        pass

    @abstractmethod
    async def execute_query(self, sql_query: str) -> DatabaseQueryResult:
        """
        ⚡ EXECUTE QUERY - Run a SQL query against the database
        
        WHAT THIS SHOULD DO:
        Execute the provided SQL query and return the results. This method
        should include basic safety checks but trusts that the query has
        been validated by the caller.
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            DatabaseQueryResult with query results or error information
        """
        pass

    @abstractmethod
    async def execute_safe_query(self, sql_query: str) -> DatabaseQueryResult:
        """
        🛡️ EXECUTE SAFE QUERY - Run a SQL query with additional safety checks
        
        WHAT THIS SHOULD DO:
        Execute the SQL query with additional safety validations:
        - Only allow SELECT statements
        - Block dangerous operations (DELETE, UPDATE, DROP, etc.)
        - Validate query syntax
        - Apply query timeouts
        - Log query execution for monitoring
        
        Args:
            sql_query: The SQL query to execute (must be SELECT only)
            
        Returns:
            DatabaseQueryResult with query results or error information
        """
        pass

    @abstractmethod
    async def get_health_info(self) -> Dict[str, Any]:
        """
        🏥 GET HEALTH INFO - Retrieve database health and performance metrics
        
        WHAT THIS SHOULD DO:
        Return information about database health, performance metrics,
        connection pool status, and any other relevant operational data.
        
        Returns:
            Dictionary containing health and performance information
        """
        pass
