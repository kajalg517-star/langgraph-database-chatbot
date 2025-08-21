"""
🔍 TABLE DISCOVERY TOOL - Helps discover available tables in the database

WHAT THIS FILE DOES:
When the AI agent encounters table not found errors or needs to understand
what tables are available in the database, this tool provides a simple way
to list all available tables and their basic structure.

KEY FEATURES:
- 📋 Lists all available tables in the schema
- 🏗️ Shows basic table structure (columns and types)
- 🔍 Helps with table name discovery and correction
- 🛡️ Safe read-only operations

USE CASES:
- Agent gets "table does not exist" error
- User asks about available data without specifying tables
- Need to suggest correct table names for typos
- Exploring database structure for better query generation

TECHNICAL DETAILS:
Uses the database service interface to query information_schema tables
for metadata about available tables and columns.
"""

from typing import Dict, Any, List
from google.adk.tools import FunctionTool
from ...services import database_service
from ...utils.logger import logger


async def list_available_tables() -> Dict[str, Any]:
    """
    🔍 LIST AVAILABLE TABLES - Discover what tables exist in the database
    
    WHAT THIS DOES:
    Queries the database to find all available tables in the current schema
    and returns basic information about each table including column names
    and data types.
    
    WHEN TO USE:
    - When you get "table does not exist" errors
    - When user asks general questions about available data
    - When you need to suggest correct table names
    - When exploring the database structure
    
    Returns:
        Dictionary containing list of tables and their basic structure
    """
    try:
        logger.info("Discovering available tables in database")
        
        # Get schema information from database service
        schema_result = await database_service.get_schema_info()
        
        if not schema_result.success:
            logger.error("Failed to retrieve schema information", error=schema_result.error)
            return {
                "success": False,
                "error": f"Could not retrieve table information: {schema_result.error}",
                "tables": []
            }
        
        # Process schema data to extract table information
        tables_info = {}
        if schema_result.data:
            for row in schema_result.data:
                # Handle the case where data is wrapped in a 'result' key (from RPC function)
                if 'result' in row and isinstance(row['result'], dict):
                    row_data = row['result']
                else:
                    row_data = row
                
                table_name = row_data.get('table_name')
                column_name = row_data.get('column_name')
                data_type = row_data.get('data_type')
                
                if table_name not in tables_info:
                    tables_info[table_name] = {
                        'table_name': table_name,
                        'columns': [],
                        'column_count': 0
                    }
                
                if column_name:
                    tables_info[table_name]['columns'].append({
                        'name': column_name,
                        'type': data_type
                    })
                    tables_info[table_name]['column_count'] += 1
        
        # Convert to list format for easier consumption
        tables_list = list(tables_info.values())
        
        logger.info(
            "Successfully discovered database tables",
            table_count=len(tables_list),
            total_columns=sum(table['column_count'] for table in tables_list)
        )
        
        return {
            "success": True,
            "tables": tables_list,
            "table_count": len(tables_list),
            "message": f"Found {len(tables_list)} tables in the database"
        }
        
    except Exception as e:
        logger.error("Table discovery failed", error=str(e))
        return {
            "success": False,
            "error": f"Table discovery failed: {str(e)}",
            "tables": []
        }


async def get_table_names_only() -> Dict[str, Any]:
    """
    📋 GET TABLE NAMES ONLY - Quick list of just table names
    
    WHAT THIS DOES:
    Returns a simple list of table names without detailed column information.
    Useful for quick table name discovery and suggestions.
    
    Returns:
        Dictionary containing just the table names
    """
    try:
        logger.info("Getting table names from database")
        
        # Use the full table discovery but extract just names
        full_result = await list_available_tables()
        
        if not full_result["success"]:
            return full_result
        
        table_names = [table["table_name"] for table in full_result["tables"]]
        
        return {
            "success": True,
            "table_names": table_names,
            "count": len(table_names),
            "message": f"Available tables: {', '.join(table_names)}"
        }
        
    except Exception as e:
        logger.error("Failed to get table names", error=str(e))
        return {
            "success": False,
            "error": f"Failed to get table names: {str(e)}",
            "table_names": []
        }


# Create ADK function tools
table_discovery_tool = FunctionTool(list_available_tables)
table_names_tool = FunctionTool(get_table_names_only)
