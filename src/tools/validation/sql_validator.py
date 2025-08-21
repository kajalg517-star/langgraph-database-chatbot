"""
🛡️ SQL SAFETY VALIDATOR - Ensures queries are safe before execution

WHAT THIS FILE DOES:
Before running any query on your database, this tool acts as a security guard
that double-checks every query for safety. It's like having a bouncer at a club
who checks IDs before letting anyone in.

SAFETY CHECKS:
✅ Only allows SELECT queries (reading data)
❌ Blocks DELETE, UPDATE, DROP (changing/deleting data)
❌ Blocks dangerous operations that could harm your database
❌ Blocks attempts to access system information
❌ Blocks SQL injection attempts

WHY THIS IS CRITICAL:
Your database contains important information. We never want to accidentally:
- Delete your data
- Change your data
- Access sensitive system information
- Run malicious code

EXAMPLES:
Safe: "SELECT COUNT(*) FROM students"
Unsafe: "DELETE FROM students" (would delete all your student data!)

TECHNICAL DETAILS:
Uses both pattern matching and AI-based analysis to identify potentially
dangerous SQL operations. Provides detailed reasoning for any rejections
to help with debugging and transparency.
"""

from typing import Dict, Any
from ...services import ai_service
from ...utils.logger import logger


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
    
    This step ensures we only read data, never modify it.
    
    Args:
        sql_query: The SQL query to validate for safety
        
    Returns:
        Dictionary containing validation results and reasoning
    """
    try:
        validation_result = await ai_service.validate_sql_query(sql_query)
        
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
