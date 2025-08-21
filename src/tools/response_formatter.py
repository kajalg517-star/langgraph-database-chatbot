"""
💬 RESPONSE FORMATTER - Converts database results to friendly answers

WHAT THIS FILE DOES:
The database returns raw data (numbers, codes, etc.), but you want a friendly answer.
This tool acts like a translator that converts technical database results into
conversational, human-readable responses.

TRANSFORMATION EXAMPLES:

Raw database result: [{"count": 23}]
Your question: "How many students have high anxiety?"
Friendly response: "There are 23 students with high anxiety levels in the database."

Raw database result: [{"name": "John", "anxiety": 18}, {"name": "Sarah", "anxiety": 19}]
Your question: "Who has the highest anxiety?"
Friendly response: "Sarah has the highest anxiety level at 19, followed by John at 18."

HOW IT WORKS:
1. Takes your original question
2. Looks at the SQL query that was used
3. Analyzes the raw results from the database
4. Uses AI to create a natural, conversational response
5. Includes relevant insights and context

TECHNICAL DETAILS:
Leverages Gemini AI to analyze query context, results, and user intent to generate
natural language responses. Handles various data types and result structures,
providing meaningful summaries and insights from raw database output.
"""

from typing import Dict, Any, List
from ..services.gemini_service import gemini_service
from ..utils.logger import logger


async def format_final_response(
    user_query: str, 
    sql_query: str, 
    query_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    💬 STEP 6: TRANSLATE RESULTS BACK TO PLAIN ENGLISH
    
    WHAT THIS DOES:
    The database returns raw data (numbers, codes, etc.), but you want a friendly answer.
    This step converts the technical results into a conversational response.
    
    TRANSFORMATION EXAMPLES:
    
    Raw database result: [{"count": 23}]
    Your question: "How many students have high anxiety?"
    Friendly response: "There are 23 students with high anxiety levels in the database."
    
    Raw database result: [{"name": "John", "anxiety": 18}, {"name": "Sarah", "anxiety": 19}]
    Your question: "Who has the highest anxiety?"
    Friendly response: "Sarah has the highest anxiety level at 19, followed by John at 18."
    
    HOW IT WORKS:
    1. Takes your original question
    2. Looks at the SQL query that was used
    3. Analyzes the raw results from the database
    4. Uses AI to create a natural, conversational response
    5. Includes relevant insights and context
    
    This makes the chatbot feel like talking to a knowledgeable human assistant!
    
    Args:
        user_query: The original user question
        sql_query: The SQL query that was executed
        query_results: Raw results from the database
        
    Returns:
        Dictionary containing formatted response and processing status
    """
    try:
        formatting_result = await gemini_service.format_response(
            user_query, sql_query, query_results
        )
        
        return {
            "response": formatting_result.response,
            "success": True,
            "error": formatting_result.error
        }
        
    except Exception as e:
        logger.error("Response formatting failed", error=str(e))
        return {
            "response": f"I found {len(query_results)} result(s) for your query.",
            "success": False,
            "error": str(e)
        }
