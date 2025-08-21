"""
🤖 GEMINI AI SERVICE - Google Gemini implementation of AI service interface

WHAT THIS FILE DOES:
This file implements the AI service interface specifically for Google's Gemini AI.
It handles all the Gemini-specific details while providing the standard interface
that the chatbot expects. This service is now completely database-agnostic.

KEY FEATURES:
- 🔌 Implements the standard AIServiceInterface
- 🧠 Uses Google Gemini 2.0 Flash for AI processing
- 🛡️ Includes safety checks and error handling
- 📊 Provides detailed logging and monitoring
- 🔄 Database-agnostic design (works with any database)

GEMINI-SPECIFIC FEATURES:
- Advanced natural language understanding
- High-quality SQL generation
- Robust safety validation
- Excellent response formatting
- Fast processing with async support

SEPARATION OF CONCERNS:
This AI service is now purely focused on language model operations:
- Query validation (is it database-related?)
- SQL generation (convert English to SQL)
- SQL validation (is the SQL safe?)
- Response formatting (convert results to friendly text)

DATABASE INDEPENDENCE:
- No database-specific code or assumptions
- Works with any database system (PostgreSQL, MySQL, SQLite, etc.)
- Receives database schema as input parameter
- Does not handle database connections or query execution

TECHNICAL DETAILS:
Uses Google's generativeai library to interact with Gemini models.
Handles JSON parsing, error recovery, and maintains conversation context.
"""

import json
import re
from typing import Dict, Any, List
import google.generativeai as genai

from .ai_service_interface import (
    AIServiceInterface,
    SQLGenerationResult,
    QueryValidationResult,
    ResponseFormattingResult
)
from .database_service_interface import DatabaseSchema
from ..config.environment import config
from ..utils.logger import logger


class GeminiAIService(AIServiceInterface):
    """
    🤖 GEMINI AI SERVICE - Google Gemini implementation
    
    WHAT THIS CLASS DOES:
    This class implements all the AI operations using Google's Gemini AI.
    It translates the generic AI interface into specific Gemini API calls.
    
    CAPABILITIES:
    - 🔍 Smart question validation using natural language understanding
    - 🧠 Advanced SQL generation with context awareness
    - 🛡️ Comprehensive safety validation
    - 💬 Natural response formatting with conversation flow
    
    GEMINI ADVANTAGES:
    - Excellent understanding of natural language
    - Strong SQL generation capabilities
    - Built-in safety features
    - Fast response times
    - Good handling of complex queries
    
    ERROR HANDLING:
    - Graceful fallbacks for API failures
    - JSON parsing error recovery
    - Detailed logging for debugging
    - User-friendly error messages
    """
    
    def __init__(self):
        """
        🚀 INITIALIZE GEMINI SERVICE
        
        WHAT THIS DOES:
        Sets up the connection to Google's Gemini AI service using the
        API key from your configuration.
        
        CONFIGURATION:
        - Uses API key from environment variables
        - Configures the specific Gemini model (gemini-2.0-flash)
        - Sets up logging for monitoring
        """
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
        logger.info(f"Gemini AI service initialized with model: {config.gemini.model}")

    async def validate_database_query(self, query: str) -> QueryValidationResult:
        """
        🔍 VALIDATE DATABASE QUERY - Gemini implementation
        
        WHAT THIS DOES:
        Uses Gemini's natural language understanding to determine if a user's
        question is about database data or just casual conversation.
        
        GEMINI'S APPROACH:
        - Analyzes semantic meaning of the question
        - Considers context and intent
        - Provides detailed reasoning for decisions
        - Handles edge cases and ambiguous queries
        """
        try:
            prompt = f"""
Analyze the following user query and determine if it's a database-related question that requires querying data.

User Query: "{query}"

A query is database-related if it:
1. Asks for specific data or information that would be stored in a database
2. Requests counts, statistics, or analysis of data
3. Asks about records, entries, or specific entities
4. Requests filtering, sorting, or aggregation of data

A query is NOT database-related if it:
1. Is a greeting (hello, hi, how are you)
2. Asks about general topics unrelated to data
3. Requests explanations of concepts
4. Is casual conversation

Respond in JSON format:
{{
  "isValid": true/false,
  "reason": "explanation of why it is or isn't database-related"
}}
"""
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                return QueryValidationResult(
                    is_valid=False,
                    reason="Could not validate query"
                )
            
            parsed = json.loads(json_match.group(0))
            
            return QueryValidationResult(
                is_valid=parsed.get('isValid', False),
                reason=parsed.get('reason', 'No reason provided')
            )
            
        except Exception as e:
            logger.error("Gemini query validation failed", error=str(e))
            return QueryValidationResult(
                is_valid=False,
                reason=f"Validation failed: {str(e)}"
            )

    async def generate_sql(
        self,
        natural_language_query: str,
        database_schema: DatabaseSchema
    ) -> SQLGenerationResult:
        """
        🧠 GENERATE SQL - Gemini implementation
        
        WHAT THIS DOES:
        Uses Gemini's advanced language understanding to convert English
        questions into precise SQL queries based on the database schema.
        
        GEMINI'S APPROACH:
        - Analyzes the question's intent and requirements
        - Maps natural language to database concepts
        - Generates optimized SQL with proper syntax
        - Provides confidence scoring and explanations
        - Database-agnostic (works with any database system)
        """
        try:
            schema_context = self._build_schema_context(database_schema)

            # Determine database type and SQL dialect
            database_type = database_schema.database_type or "postgresql"
            schema_name = database_schema.schema_name or "public"

            # Create database-agnostic prompt
            prompt = f"""
You are a SQL expert. Convert the following natural language query into a {database_type.upper()} query.

Database Schema:
{schema_context}

Natural Language Query: "{natural_language_query}"

Rules:
1. Generate ONLY valid {database_type.upper()} SQL
2. Use proper table and column names from the schema
3. If schema name is provided, prefix table names appropriately (e.g., {schema_name}.table_name)
4. Include appropriate WHERE clauses, JOINs, and ORDER BY as needed
5. Limit results to reasonable numbers (use LIMIT when appropriate)
6. Handle case-insensitive searches appropriately for {database_type}
7. Return only SELECT statements (no INSERT, UPDATE, DELETE)
8. Use {database_type}-specific syntax and functions when beneficial

Respond in JSON format:
{{
  "sql": "your SQL query here",
  "explanation": "brief explanation of what the query does",
  "confidence": 0.95
}}
"""
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                raise ValueError('Invalid response format from Gemini')
            
            parsed = json.loads(json_match.group(0))
            
            result = SQLGenerationResult(
                sql=parsed.get('sql', ''),
                explanation=parsed.get('explanation', ''),
                confidence=parsed.get('confidence', 0.8)
            )
            
            # Log the generated SQL for debugging
            logger.info(
                "Gemini generated SQL query",
                natural_language=natural_language_query,
                sql=result.sql,
                explanation=result.explanation,
                confidence=result.confidence
            )
            
            return result
            
        except Exception as e:
            logger.error("Gemini SQL generation failed", error=str(e))
            return SQLGenerationResult(
                sql="",
                explanation=f"Failed to generate SQL: {str(e)}",
                confidence=0.0
            )

    async def validate_sql_query(self, sql_query: str) -> QueryValidationResult:
        """
        🛡️ VALIDATE SQL QUERY - Gemini implementation

        WHAT THIS DOES:
        Uses Gemini's understanding of SQL and security to validate that
        queries are safe to execute on the database.

        GEMINI'S APPROACH:
        - Analyzes SQL syntax and structure
        - Identifies potentially dangerous operations
        - Checks for security vulnerabilities
        - Provides detailed reasoning for rejections
        """
        try:
            prompt = f"""
Analyze this SQL query for safety and validity:
"{sql_query}"

Check for:
1. Only SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
2. No dangerous functions or operations
3. Proper SQL syntax
4. No attempts to access system tables or sensitive data

Respond in JSON format:
{{
  "isValid": true/false,
  "reason": "explanation if invalid"
}}
"""

            response = await self.model.generate_content_async(prompt)
            response_text = response.text

            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                return QueryValidationResult(
                    is_valid=False,
                    reason="Could not validate query"
                )

            parsed = json.loads(json_match.group(0))

            return QueryValidationResult(
                is_valid=parsed.get('isValid', False),
                reason=parsed.get('reason', 'No reason provided')
            )

        except Exception as e:
            logger.error("Gemini SQL validation failed", error=str(e))
            return QueryValidationResult(
                is_valid=False,
                reason=f"Validation failed: {str(e)}"
            )

    async def format_response(
        self,
        user_query: str,
        sql_query: str,
        query_results: List[Dict[str, Any]]
    ) -> ResponseFormattingResult:
        """
        💬 FORMAT RESPONSE - Gemini implementation

        WHAT THIS DOES:
        Uses Gemini's natural language generation to convert raw database
        results into friendly, conversational responses.

        GEMINI'S APPROACH:
        - Understands the context of the original question
        - Analyzes the data patterns and insights
        - Generates natural, conversational responses
        - Handles various data types and result structures
        """
        try:
            # Prepare results for the prompt
            results_text = json.dumps(query_results, indent=2, default=str)

            prompt = f"""
You are a helpful database assistant. Format the following query results into a natural, conversational response.

User's Question: "{user_query}"
SQL Query Used: "{sql_query}"
Query Results: {results_text}

Instructions:
1. Provide a clear, natural language answer to the user's question
2. Include relevant data from the results
3. If there are many results, summarize key insights
4. If no results, explain that no matching data was found
5. Be conversational but informative
6. Don't include technical SQL details in the response

Respond with just the formatted text response (no JSON):
"""

            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()

            return ResponseFormattingResult(response=response_text)

        except Exception as e:
            logger.error("Gemini response formatting failed", error=str(e))
            return ResponseFormattingResult(
                response=f"I found {len(query_results)} result(s) for your query.",
                error=str(e)
            )

    def _build_schema_context(self, database_schema: DatabaseSchema) -> str:
        """
        📊 BUILD SCHEMA CONTEXT - Helper method for Gemini prompts

        WHAT THIS DOES:
        Converts the database schema information into a text format
        that Gemini can understand and use for SQL generation.

        FORMAT:
        Creates a human-readable description of tables, columns, and data types
        that helps Gemini understand the database structure.
        """
        schema_lines = []

        for table_name, table_info in database_schema.tables.items():
            schema_lines.append(f"Table: {table_name}")

            if 'columns' in table_info:
                for column in table_info['columns']:
                    column_name = column.get('column_name', 'unknown')
                    data_type = column.get('data_type', 'unknown')
                    schema_lines.append(f"  - {column_name} ({data_type})")

            if 'description' in table_info:
                schema_lines.append(f"  Description: {table_info['description']}")

            schema_lines.append("")  # Empty line between tables

        return "\n".join(schema_lines)
