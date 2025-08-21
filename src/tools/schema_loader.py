"""
📊 DATABASE SCHEMA LOADER - Learns about your database structure

WHAT THIS FILE DOES:
Before creating any database queries, the chatbot needs to understand your database
structure. This tool acts like a database explorer that maps out what tables exist,
what columns they contain, and what types of data are stored.

REAL EXAMPLE:
Your database might have:
- Table: "student_stress_survey"
- Columns: "student_id" (number), "anxiety_level" (number), "depression_score" (number)

WHY THIS IS IMPORTANT:
Without knowing the structure, the chatbot can't create accurate database queries.
It's like trying to find a book in a library without knowing how it's organized.

TECHNICAL DETAILS:
Connects to the database service to retrieve schema information including table names,
column names, data types, and relationships. Processes this information into a
structured format that the SQL generation tool can use effectively.
"""

from typing import Dict, Any
from ..services import database_service
from ..utils.logger import logger


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
    
    Returns:
        Dictionary containing schema information and processing status
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
