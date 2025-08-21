"""
🤖 AI SERVICE INTERFACE - Abstract base for all AI providers

WHAT THIS FILE DOES:
This file defines the contract that all AI services must follow. Think of it like
a blueprint or template that ensures all AI providers (Gemini, OpenAI, Ollama, etc.)
work the same way from the chatbot's perspective.

WHY WE NEED THIS:
- **Flexibility**: Easy to switch between different AI providers
- **Extensibility**: Add new AI providers without changing existing code
- **Consistency**: All AI services provide the same functionality
- **Testing**: Mock AI services for testing without real API calls

SUPPORTED OPERATIONS:
1. 🔍 Query Validation - Check if questions are database-related
2. 🧠 SQL Generation - Convert English to SQL queries
3. 🛡️ SQL Validation - Ensure queries are safe before execution
4. 💬 Response Formatting - Convert results to friendly answers

DESIGN PATTERN:
This uses the Strategy Pattern and Abstract Base Class pattern to define
a common interface that all AI providers must implement.

FUTURE AI PROVIDERS:
- OpenAI GPT-4/GPT-3.5
- Anthropic Claude
- Local models via Ollama
- Azure OpenAI
- AWS Bedrock
- Google Vertex AI
"""

from abc import ABC, abstractmethod
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


class DatabaseSchema(BaseModel):
    """
    🗄️ DATABASE SCHEMA - Structure information about the database
    
    WHAT THIS CONTAINS:
    - tables: Dictionary of table information including columns and types
    
    This is database-agnostic and works with any database system.
    """
    tables: Dict[str, Dict[str, Any]]


class AIServiceInterface(ABC):
    """
    🎯 AI SERVICE INTERFACE - The contract all AI providers must follow
    
    WHAT THIS IS:
    This is an abstract base class that defines what methods every AI service
    must implement. It's like a contract that ensures consistency across
    different AI providers.
    
    WHY THIS MATTERS:
    - The chatbot can work with any AI provider that implements this interface
    - Easy to switch from Gemini to OpenAI or any other provider
    - New AI providers just need to implement these 4 methods
    - Testing becomes easier with mock implementations
    
    REQUIRED METHODS:
    Every AI service must implement these 4 methods:
    1. validate_database_query() - Check if question is database-related
    2. generate_sql() - Convert English to SQL
    3. validate_sql_query() - Check if SQL is safe
    4. format_response() - Convert results to friendly text
    """

    @abstractmethod
    async def validate_database_query(self, query: str) -> QueryValidationResult:
        """
        🔍 VALIDATE DATABASE QUERY - Check if question is database-related
        
        WHAT THIS SHOULD DO:
        Analyze a user's question and determine if it requires database access.
        
        EXAMPLES:
        ✅ "How many students?" → is_valid=True
        ❌ "Hello there!" → is_valid=False
        
        Args:
            query: The user's question in natural language
            
        Returns:
            QueryValidationResult with validation decision and reasoning
        """
        pass

    @abstractmethod
    async def generate_sql(
        self, 
        natural_language_query: str, 
        database_schema: DatabaseSchema
    ) -> SQLGenerationResult:
        """
        🧠 GENERATE SQL - Convert English question to database query
        
        WHAT THIS SHOULD DO:
        Take a natural language question and database schema, then generate
        appropriate SQL query to answer the question.
        
        EXAMPLE:
        Input: "How many students have anxiety above 15?"
        Output: "SELECT COUNT(*) FROM students WHERE anxiety_level > 15"
        
        Args:
            natural_language_query: User's question in plain English
            database_schema: Information about database structure
            
        Returns:
            SQLGenerationResult with SQL, explanation, and confidence
        """
        pass

    @abstractmethod
    async def validate_sql_query(self, sql_query: str) -> QueryValidationResult:
        """
        🛡️ VALIDATE SQL QUERY - Ensure SQL is safe before execution
        
        WHAT THIS SHOULD DO:
        Check that the generated SQL is safe to run (only SELECT statements,
        no dangerous operations, proper syntax).
        
        SAFETY CHECKS:
        ✅ Only SELECT queries allowed
        ❌ No DELETE, UPDATE, DROP operations
        ❌ No system table access
        
        Args:
            sql_query: The SQL query to validate
            
        Returns:
            QueryValidationResult with safety assessment
        """
        pass

    @abstractmethod
    async def format_response(
        self,
        user_query: str,
        sql_query: str,
        query_results: List[Dict[str, Any]]
    ) -> ResponseFormattingResult:
        """
        💬 FORMAT RESPONSE - Convert raw data to friendly answer
        
        WHAT THIS SHOULD DO:
        Take the raw database results and convert them into a natural,
        conversational response that answers the user's original question.
        
        EXAMPLE:
        Input: [{"count": 23}]
        Output: "There are 23 students with high anxiety levels."
        
        Args:
            user_query: Original question from user
            sql_query: SQL that was executed
            query_results: Raw results from database
            
        Returns:
            ResponseFormattingResult with friendly response text
        """
        pass
