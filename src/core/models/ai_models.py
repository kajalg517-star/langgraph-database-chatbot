"""
Data models for AI service operations.

This module contains Pydantic models that represent the data structures
used in AI service operations like query validation, SQL generation,
and response formatting.
"""

from typing import Dict, Any, List
from pydantic import BaseModel


class SQLGenerationResult(BaseModel):
    """
    📊 SQL GENERATION RESULT - What we get when AI creates SQL
    
    WHAT THIS CONTAINS:
    - sql: The actual database query created by AI
    - explanation: Plain English explanation of what the query does
    - confidence: How sure the AI is (0.0 to 1.0 scale)
    
    EXAMPLE:
    SQLGenerationResult(
        sql="SELECT COUNT(*) FROM students WHERE anxiety_level > 15",
        explanation="Counts students with anxiety levels above 15",
        confidence=0.95
    )
    """
    sql: str
    explanation: str
    confidence: float


class QueryValidationResult(BaseModel):
    """
    ✅ QUERY VALIDATION RESULT - Whether a question is database-related
    
    WHAT THIS CONTAINS:
    - is_valid: True if it's about the database, False if not
    - reason: Explanation of why it was accepted or rejected
    
    EXAMPLE:
    QueryValidationResult(
        is_valid=True,
        reason="Question asks for student count, which requires database query"
    )
    """
    is_valid: bool
    reason: str = ""


class ResponseFormattingResult(BaseModel):
    """
    💬 RESPONSE FORMATTING RESULT - Friendly answer from raw data
    
    WHAT THIS CONTAINS:
    - response: Natural language answer for the user
    - error: Any error that occurred during formatting (optional)
    
    EXAMPLE:
    ResponseFormattingResult(
        response="There are 23 students with high anxiety levels in the database.",
        error=None
    )
    """
    response: str
    error: str = ""
