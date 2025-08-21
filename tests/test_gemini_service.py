"""
Tests for the Gemini service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.gemini_service import GeminiService, DatabaseSchema


@pytest.fixture
def mock_genai_model():
    """Mock Gemini model."""
    model = MagicMock()
    
    # Mock response for SQL generation
    sql_response = MagicMock()
    sql_response.text = '''
    {
        "sql": "SELECT COUNT(*) FROM college.students",
        "explanation": "Count all students in the database",
        "confidence": 0.95
    }
    '''
    model.generate_content_async.return_value = sql_response
    
    return model


@pytest.fixture
def gemini_service(mock_genai_model):
    """Gemini service with mocked model."""
    with patch('src.services.gemini_service.genai.GenerativeModel') as mock_model_class:
        mock_model_class.return_value = mock_genai_model
        service = GeminiService()
        return service


@pytest.fixture
def sample_schema():
    """Sample database schema."""
    return DatabaseSchema(tables={
        "students": {
            "table_name": "students",
            "columns": [
                {"column_name": "id", "data_type": "integer"},
                {"column_name": "name", "data_type": "varchar"},
                {"column_name": "anxiety_level", "data_type": "integer"}
            ],
            "description": "Student information and mental health data"
        }
    })


class TestGeminiService:
    """Test cases for GeminiService."""
    
    @pytest.mark.asyncio
    async def test_generate_sql_success(self, gemini_service, sample_schema, mock_genai_model):
        """Test successful SQL generation."""
        result = await gemini_service.generate_sql(
            "How many students are there?",
            sample_schema
        )
        
        assert result.sql == "SELECT COUNT(*) FROM college.students"
        assert result.explanation == "Count all students in the database"
        assert result.confidence == 0.95
        
        # Verify the model was called
        mock_genai_model.generate_content_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_sql_invalid_json(self, gemini_service, sample_schema, mock_genai_model):
        """Test SQL generation with invalid JSON response."""
        # Mock invalid JSON response
        invalid_response = MagicMock()
        invalid_response.text = "This is not valid JSON"
        mock_genai_model.generate_content_async.return_value = invalid_response
        
        result = await gemini_service.generate_sql(
            "How many students are there?",
            sample_schema
        )
        
        assert result.sql == ""
        assert "Failed to generate SQL" in result.explanation
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_validate_database_query_valid(self, gemini_service, mock_genai_model):
        """Test validation of valid database query."""
        # Mock validation response
        validation_response = MagicMock()
        validation_response.text = '''
        {
            "isValid": true,
            "reason": "This is a database-related question asking for student count"
        }
        '''
        mock_genai_model.generate_content_async.return_value = validation_response
        
        result = await gemini_service.validate_database_query(
            "How many students are in the database?"
        )
        
        assert result.is_valid is True
        assert "database-related question" in result.reason
    
    @pytest.mark.asyncio
    async def test_validate_database_query_invalid(self, gemini_service, mock_genai_model):
        """Test validation of invalid database query."""
        # Mock validation response
        validation_response = MagicMock()
        validation_response.text = '''
        {
            "isValid": false,
            "reason": "This is a greeting, not a database-related question"
        }
        '''
        mock_genai_model.generate_content_async.return_value = validation_response
        
        result = await gemini_service.validate_database_query("Hello")
        
        assert result.is_valid is False
        assert "greeting" in result.reason
    
    @pytest.mark.asyncio
    async def test_validate_sql_query_safe(self, gemini_service, mock_genai_model):
        """Test validation of safe SQL query."""
        # Mock SQL validation response
        sql_validation_response = MagicMock()
        sql_validation_response.text = '''
        {
            "isValid": true,
            "reason": "This is a safe SELECT query"
        }
        '''
        mock_genai_model.generate_content_async.return_value = sql_validation_response
        
        result = await gemini_service.validate_sql_query(
            "SELECT COUNT(*) FROM students"
        )
        
        assert result.is_valid is True
        assert "safe SELECT query" in result.reason
    
    @pytest.mark.asyncio
    async def test_validate_sql_query_unsafe(self, gemini_service, mock_genai_model):
        """Test validation of unsafe SQL query."""
        # Mock SQL validation response
        sql_validation_response = MagicMock()
        sql_validation_response.text = '''
        {
            "isValid": false,
            "reason": "This query contains dangerous DELETE operation"
        }
        '''
        mock_genai_model.generate_content_async.return_value = sql_validation_response
        
        result = await gemini_service.validate_sql_query(
            "DELETE FROM students"
        )
        
        assert result.is_valid is False
        assert "dangerous DELETE operation" in result.reason
    
    @pytest.mark.asyncio
    async def test_format_response_success(self, gemini_service, mock_genai_model):
        """Test successful response formatting."""
        # Mock formatting response
        format_response = MagicMock()
        format_response.text = "I found 150 students in the database."
        mock_genai_model.generate_content_async.return_value = format_response
        
        query_results = [{"count": 150}]
        
        result = await gemini_service.format_response(
            "How many students are there?",
            "SELECT COUNT(*) FROM students",
            query_results
        )
        
        assert result.response == "I found 150 students in the database."
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_format_response_error(self, gemini_service, mock_genai_model):
        """Test response formatting with error."""
        # Mock exception during formatting
        mock_genai_model.generate_content_async.side_effect = Exception("API Error")
        
        query_results = [{"count": 150}]
        
        result = await gemini_service.format_response(
            "How many students are there?",
            "SELECT COUNT(*) FROM students",
            query_results
        )
        
        assert "I found 1 result(s)" in result.response
        assert result.error == "API Error"
    
    def test_build_schema_context(self, gemini_service, sample_schema):
        """Test schema context building."""
        context = gemini_service._build_schema_context(sample_schema)
        
        assert "Table: students" in context
        assert "id (integer)" in context
        assert "name (varchar)" in context
        assert "anxiety_level (integer)" in context
        assert "Student information and mental health data" in context
