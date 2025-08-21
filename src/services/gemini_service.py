"""
Gemini AI Service for SQL generation and query validation.
Maintains compatibility with the original TypeScript implementation.
"""

import json
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import google.generativeai as genai

from ..config.environment import config
from ..utils.logger import logger


class SQLGenerationResult(BaseModel):
    """Result of SQL generation from natural language."""
    sql: str
    explanation: str
    confidence: float


class QueryValidationResult(BaseModel):
    """Result of query validation."""
    is_valid: bool
    reason: Optional[str] = None


class ResponseFormattingResult(BaseModel):
    """Result of response formatting."""
    response: str
    error: Optional[str] = None


class DatabaseSchema(BaseModel):
    """Database schema information."""
    tables: Dict[str, Dict[str, Any]]


class GeminiService:
    """
    Service for interacting with Gemini AI for SQL generation and validation.
    Maintains the same functionality as the TypeScript implementation.
    """
    
    def __init__(self):
        """Initialize the Gemini service."""
        genai.configure(api_key=config.gemini.api_key)
        self.model = genai.GenerativeModel(config.gemini.model)
        logger.info(f"Gemini service initialized with model: {config.gemini.model}")
    
    async def generate_sql(
        self,
        natural_language_query: str,
        database_schema: DatabaseSchema
    ) -> SQLGenerationResult:
        """
        Generate SQL query from natural language input.
        Maintains compatibility with TypeScript implementation.
        """
        try:
            schema_context = self._build_schema_context(database_schema)
            
            prompt = f"""
You are a SQL expert. Convert the following natural language query into a PostgreSQL query.

Database Schema:
{schema_context}

Natural Language Query: "{natural_language_query}"

Rules:
1. Generate ONLY valid PostgreSQL SQL
2. Use proper table and column names from the schema
3. ALWAYS prefix table names with the schema name '{config.supabase.schema}.' (e.g., {config.supabase.schema}.student_stress_survey)
4. Include appropriate WHERE clauses, JOINs, and ORDER BY as needed
5. Limit results to reasonable numbers (use LIMIT when appropriate)
6. Handle case-insensitive searches with ILIKE when searching text
7. Return only SELECT statements (no INSERT, UPDATE, DELETE)

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
                "Generated SQL query",
                natural_language=natural_language_query,
                sql=result.sql,
                explanation=result.explanation,
                confidence=result.confidence
            )
            
            return result
            
        except Exception as e:
            logger.error("SQL generation failed", error=str(e))
            return SQLGenerationResult(
                sql="",
                explanation=f"Failed to generate SQL: {str(e)}",
                confidence=0.0
            )
    
    async def validate_database_query(self, query: str) -> QueryValidationResult:
        """
        Validate if a query is database-related.
        Maintains compatibility with TypeScript implementation.
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
            logger.error("Query validation failed", error=str(e))
            return QueryValidationResult(
                is_valid=False,
                reason=f"Validation failed: {str(e)}"
            )
    
    async def validate_sql_query(self, sql_query: str) -> QueryValidationResult:
        """
        Validate SQL query for safety and correctness.
        Maintains compatibility with TypeScript implementation.
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
            logger.error("SQL validation failed", error=str(e))
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
        Format query results into a natural language response.
        Maintains compatibility with TypeScript implementation.
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
            logger.error("Response formatting failed", error=str(e))
            return ResponseFormattingResult(
                response=f"I found {len(query_results)} result(s) for your query.",
                error=str(e)
            )
    
    def _build_schema_context(self, database_schema: DatabaseSchema) -> str:
        """Build schema context string for prompts."""
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


# Singleton instance for use in agents
gemini_service = GeminiService()
