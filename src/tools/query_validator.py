"""
🔍 QUERY VALIDATION TOOL - Checks if questions are database-related

WHAT THIS FILE DOES:
This tool acts as the first filter in our chatbot pipeline. Before doing any work,
it determines whether a user's question is actually about the database or just
casual conversation.

EXAMPLES:
✅ Database questions: "How many students?", "Show me high anxiety levels"
❌ Not database: "Hello", "What's the weather?", "Tell me a joke"

WHY THIS MATTERS:
We don't want to waste time trying to create database queries for casual conversation.
This step acts like a smart filter that saves processing time and provides better
user experience by handling non-database questions appropriately.

TECHNICAL DETAILS:
Uses Gemini AI to analyze the semantic content of user queries and classify them
as database-related or general conversation. Returns structured validation results
with explanations for transparency.
"""

from typing import Dict, Any
from ..services.gemini_service import gemini_service
from ..utils.logger import logger


async def validate_database_query(user_query: str) -> Dict[str, Any]:
    """
    🔍 STEP 1: CHECK IF QUESTION IS ABOUT THE DATABASE
    
    WHAT THIS DOES:
    Before doing any work, we need to check if your question is actually about the database.
    
    EXAMPLES:
    ✅ Database questions: "How many students?", "Show me high anxiety levels"
    ❌ Not database: "Hello", "What's the weather?", "Tell me a joke"
    
    WHY THIS MATTERS:
    We don't want to waste time trying to create database queries for casual conversation.
    This step acts like a smart filter.
    
    RETURNS:
    - is_valid: True if it's about the database, False if not
    - reason: Explanation of why it was accepted or rejected
    
    Args:
        user_query: The user's question in natural language
        
    Returns:
        Dictionary containing validation results and reasoning
    """
    try:
        validation_result = await gemini_service.validate_database_query(user_query)
        
        return {
            "is_valid": validation_result.is_valid,
            "reason": validation_result.reason,
            "user_query": user_query
        }
    except Exception as e:
        logger.error("Query validation failed", error=str(e))
        return {
            "is_valid": False,
            "reason": f"Validation error: {str(e)}",
            "user_query": user_query
        }
