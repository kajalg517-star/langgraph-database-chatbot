"""
Data models for database service operations.

This module contains Pydantic models that represent the data structures
used in database operations like query results, schema information,
and connection status.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class DatabaseQueryResult(BaseModel):
    """
    📋 DATABASE QUERY RESULT - What we get back from database operations
    
    WHAT THIS CONTAINS:
    - success: Whether the operation succeeded
    - data: The actual results from the database (list of records)
    - row_count: Number of rows returned or affected
    - error: Error message if something went wrong
    - execution_time: How long the query took (optional)
    
    EXAMPLE:
    DatabaseQueryResult(
        success=True,
        data=[{"count": 102}],
        row_count=1,
        error=None,
        execution_time=0.045
    )
    """
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    error: Optional[str] = None
    execution_time: Optional[float] = None


class DatabaseSchema(BaseModel):
    """
    🏗️ DATABASE SCHEMA - Structure information about the database
    
    WHAT THIS CONTAINS:
    - tables: Dictionary of table information including columns, types, and metadata
    - schema_name: Name of the database schema (if applicable)
    - database_type: Type of database system (postgresql, mysql, etc.)
    
    This is database-agnostic and works with any database system.
    """
    tables: Dict[str, Dict[str, Any]]
    schema_name: Optional[str] = None
    database_type: Optional[str] = None


class DatabaseConnectionInfo(BaseModel):
    """
    🔌 DATABASE CONNECTION INFO - Connection status and metadata
    
    WHAT THIS CONTAINS:
    - connected: Whether we're currently connected
    - database_type: Type of database (postgresql, mysql, etc.)
    - version: Database version information
    - schema_name: Current schema being used
    - connection_pool_size: Number of available connections (if applicable)
    """
    connected: bool
    database_type: Optional[str] = None
    version: Optional[str] = None
    schema_name: Optional[str] = None
    connection_pool_size: Optional[int] = None
