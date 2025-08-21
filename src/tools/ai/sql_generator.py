"""
🧠 SQL GENERATION TOOL - Translates English to Database Language

WHAT THIS FILE DOES:
This is where the magic happens! This tool takes your plain English questions
and converts them into SQL (the language databases understand). It's like having
a universal translator between human language and database language.

TRANSLATION EXAMPLES:
You ask: "How many students have anxiety above 15?"
Tool creates: "SELECT COUNT(*) FROM student_stress_survey WHERE anxiety_level > 15"

You ask: "Show me the top 5 most stressed students"
Tool creates: "SELECT * FROM student_stress_survey ORDER BY stress_level DESC LIMIT 5"

HOW IT WORKS:
1. Uses Google's AI (Gemini) to understand your question
2. Looks at the database structure learned from the schema loader
3. Combines both to create the perfect SQL query
4. Includes safety checks to make sure the query is valid

TECHNICAL DETAILS:
Leverages Gemini AI's natural language processing capabilities combined with
database schema context to generate accurate, safe SQL queries. Includes
confidence scoring and detailed explanations for transparency.
"""

from typing import Dict, Any
from ...services import ai_service
from ...core.models.database_models import DatabaseSchema
from ...utils.logger import logger


async def generate_sql_query(user_query: str, schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    🧠 STEP 3: TRANSLATE YOUR QUESTION INTO DATABASE LANGUAGE (SQL)
    
    WHAT THIS DOES:
    This is where the magic happens! The chatbot takes your plain English question
    and converts it into SQL (the language databases understand).
    
    TRANSLATION EXAMPLES:
    You ask: "How many students have anxiety above 15?"
    Bot creates: "SELECT COUNT(*) FROM student_stress_survey WHERE anxiety_level > 15"
    
    You ask: "Show me the top 5 most stressed students"
    Bot creates: "SELECT * FROM student_stress_survey ORDER BY stress_level DESC LIMIT 5"
    
    HOW IT WORKS:
    1. Uses Google's AI (Gemini) to understand your question
    2. Looks at the database structure it learned in Step 2
    3. Combines both to create the perfect SQL query
    4. Includes safety checks to make sure the query is valid
    
    RETURNS:
    - sql: The actual database query
    - explanation: Plain English explanation of what the query does
    - confidence: How sure the AI is that this query is correct (0-1 scale)
    
    Args:
        user_query: The user's question in natural language
        schema_data: Database structure information from schema loader
        
    Returns:
        Dictionary containing generated SQL, explanation, and confidence score
    """
    try:
        # Import config to get schema name
        from ...config.environment import config

        # Convert schema data to DatabaseSchema object with schema name and database type
        database_schema = DatabaseSchema(
            tables=schema_data.get("tables", {}),
            schema_name=config.supabase.schema,
            database_type=config.supabase.database_type
        )

        sql_result = await ai_service.generate_sql(user_query, database_schema)
        
        return {
            "sql": sql_result.sql,
            "explanation": sql_result.explanation,
            "confidence": sql_result.confidence,
            "success": bool(sql_result.sql)
        }
        
    except Exception as e:
        logger.error("SQL generation failed", error=str(e))
        return {
            "sql": "",
            "explanation": f"Failed to generate SQL: {str(e)}",
            "confidence": 0.0,
            "success": False
        }
