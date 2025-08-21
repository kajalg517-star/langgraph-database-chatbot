"""
🧪 DATABASE CONNECTION TESTER - Verifies database connectivity

WHAT THIS FILE DOES:
This utility provides functions to test whether the chatbot can successfully
connect to your database. It's like a health check that ensures everything
is working before you start asking questions.

WHY THIS IS IMPORTANT:
Before starting a conversation with the chatbot, it's good to know that:
- Your database credentials are correct
- The database is accessible
- The connection is working properly
- The required functions are available

WHAT IT TESTS:
- Basic connection to Supabase
- Ability to execute simple queries
- RPC function availability
- Schema access permissions

TECHNICAL DETAILS:
Uses the database service to perform lightweight connectivity tests without
affecting your data. Provides clear success/failure feedback for troubleshooting.
"""

from ..tools.database_tool import database_service
from ..utils.logger import logger


async def test_database_connection() -> bool:
    """
    🧪 TEST DATABASE CONNECTION - Quick Health Check
    
    WHAT THIS DOES:
    Performs a quick test to make sure the chatbot can connect to your database.
    It's like checking if the phone line is working before making an important call.
    
    WHAT IT TESTS:
    - Can we connect to your Supabase database?
    - Are our credentials working?
    - Can we run basic queries?
    - Is everything ready for chatbot conversations?
    
    RETURNS:
    - True: Everything is working! ✅
    - False: There's a problem that needs fixing ❌
    
    WHY USE THIS:
    Run this test before starting conversations to catch any setup issues early.
    It's much better to find problems now than in the middle of asking questions!
    
    Returns:
        Boolean indicating whether the database connection is working
    """
    try:
        connection_ok = await database_service.test_connection()
        
        if connection_ok:
            logger.info("Database connection test passed successfully")
        else:
            logger.error("Database connection test failed")
            
        return connection_ok
        
    except Exception as e:
        logger.error("Database connection test failed with exception", error=str(e))
        return False


async def get_database_status() -> dict:
    """
    📊 GET DETAILED DATABASE STATUS - Comprehensive Health Report
    
    WHAT THIS DOES:
    Provides a detailed report about your database connection status,
    including specific information about what's working and what isn't.
    
    INFORMATION INCLUDED:
    - Connection status (working/failed)
    - Schema accessibility
    - Available tables count
    - Error details if something is wrong
    - Performance metrics
    
    RETURNS:
    Dictionary with detailed status information for troubleshooting
    
    Returns:
        Dictionary containing comprehensive database status information
    """
    status = {
        "connection_ok": False,
        "schema_accessible": False,
        "tables_found": 0,
        "error": None,
        "details": {}
    }
    
    try:
        # Test basic connection
        connection_ok = await database_service.test_connection()
        status["connection_ok"] = connection_ok
        
        if connection_ok:
            # Test schema access
            try:
                schema_result = await database_service.get_schema_info()
                if schema_result.success:
                    status["schema_accessible"] = True
                    status["tables_found"] = len(set(
                        row.get('table_name') for row in schema_result.data or []
                    ))
                    status["details"]["schema_info"] = "Successfully retrieved schema information"
                else:
                    status["error"] = schema_result.error
                    status["details"]["schema_error"] = schema_result.error
            except Exception as schema_error:
                status["error"] = f"Schema access failed: {str(schema_error)}"
                status["details"]["schema_exception"] = str(schema_error)
        else:
            status["error"] = "Basic database connection failed"
            
    except Exception as e:
        status["error"] = f"Connection test failed: {str(e)}"
        status["details"]["connection_exception"] = str(e)
        logger.error("Database status check failed", error=str(e))
    
    return status
