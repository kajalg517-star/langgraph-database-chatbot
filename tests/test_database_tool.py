"""
Tests for the database tool.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.tools.database_tool import SupabaseDatabaseTool, DatabaseQueryParams


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = [
        {"result": {"id": 1, "name": "test"}},
        {"result": {"id": 2, "name": "test2"}}
    ]
    return client


@pytest.fixture
def database_tool(mock_supabase_client):
    """Database tool with mocked client."""
    tool = SupabaseDatabaseTool()
    tool._client = mock_supabase_client
    return tool


class TestSupabaseDatabaseTool:
    """Test cases for SupabaseDatabaseTool."""
    
    def test_is_safe_query_valid_select(self, database_tool):
        """Test that valid SELECT queries are considered safe."""
        assert database_tool._is_safe_query("SELECT * FROM users")
        assert database_tool._is_safe_query("select id, name from users where id = 1")
        assert database_tool._is_safe_query("  SELECT COUNT(*) FROM orders  ")
    
    def test_is_safe_query_invalid_operations(self, database_tool):
        """Test that dangerous operations are rejected."""
        assert not database_tool._is_safe_query("INSERT INTO users VALUES (1, 'test')")
        assert not database_tool._is_safe_query("UPDATE users SET name = 'test'")
        assert not database_tool._is_safe_query("DELETE FROM users")
        assert not database_tool._is_safe_query("DROP TABLE users")
        assert not database_tool._is_safe_query("CREATE TABLE test (id INT)")
        assert not database_tool._is_safe_query("ALTER TABLE users ADD COLUMN test VARCHAR(50)")
    
    def test_is_safe_query_sql_injection_attempts(self, database_tool):
        """Test that SQL injection attempts are rejected."""
        assert not database_tool._is_safe_query("SELECT * FROM users; DROP TABLE users;")
        assert not database_tool._is_safe_query("SELECT * FROM users -- comment")
        assert not database_tool._is_safe_query("SELECT * FROM users /* comment */")
    
    @pytest.mark.asyncio
    async def test_execute_rpc_query_success(self, database_tool, mock_supabase_client):
        """Test successful RPC query execution."""
        result = await database_tool._execute_rpc_query("SELECT * FROM users")
        
        assert result.success is True
        assert result.row_count == 2
        assert len(result.data) == 2
        assert result.data[0] == {"id": 1, "name": "test"}
        assert result.data[1] == {"id": 2, "name": "test2"}
        
        # Verify RPC was called correctly
        mock_supabase_client.rpc.assert_called_once_with(
            'execute_college_query',
            {'query_text': 'SELECT * FROM users'}
        )
    
    @pytest.mark.asyncio
    async def test_execute_rpc_query_no_data(self, database_tool, mock_supabase_client):
        """Test RPC query with no data returned."""
        mock_supabase_client.rpc.return_value.execute.return_value.data = None
        
        result = await database_tool._execute_rpc_query("SELECT * FROM empty_table")
        
        assert result.success is False
        assert result.error == "No data returned from query"
    
    @pytest.mark.asyncio
    async def test_run_async_impl_unsafe_query(self, database_tool):
        """Test that unsafe queries are rejected."""
        params = DatabaseQueryParams(sql_query="DROP TABLE users")
        
        result = await database_tool._run_async_impl(params)
        
        assert result.success is False
        assert "Only SELECT queries are allowed" in result.error
    
    @pytest.mark.asyncio
    async def test_run_async_impl_safe_query(self, database_tool, mock_supabase_client):
        """Test successful execution of safe query."""
        params = DatabaseQueryParams(sql_query="SELECT * FROM users")
        
        result = await database_tool._run_async_impl(params)
        
        assert result.success is True
        assert result.row_count == 2
        assert len(result.data) == 2
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, database_tool, mock_supabase_client):
        """Test successful connection test."""
        mock_supabase_client.rpc.return_value.execute.return_value.data = [{"result": {"test": 1}}]
        
        connection_ok = await database_tool.test_connection()
        
        assert connection_ok is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, database_tool):
        """Test connection test failure."""
        database_tool._client = None
        
        connection_ok = await database_tool.test_connection()
        
        assert connection_ok is False
    
    @pytest.mark.asyncio
    async def test_get_schema_info(self, database_tool, mock_supabase_client):
        """Test schema information retrieval."""
        mock_supabase_client.rpc.return_value.execute.return_value.data = [
            {"result": {
                "table_name": "users",
                "column_name": "id",
                "data_type": "integer",
                "is_nullable": "NO"
            }},
            {"result": {
                "table_name": "users",
                "column_name": "name",
                "data_type": "varchar",
                "is_nullable": "YES"
            }}
        ]
        
        result = await database_tool.get_schema_info()
        
        assert result.success is True
        assert result.row_count == 2
        assert result.data[0]["table_name"] == "users"
        assert result.data[0]["column_name"] == "id"
