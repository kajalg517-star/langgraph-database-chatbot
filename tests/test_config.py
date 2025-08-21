"""
Tests for configuration management.
"""

import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.environment import Config, SupabaseConfig, GeminiConfig


class TestConfig:
    """Test cases for configuration management."""
    
    def test_config_from_env_complete(self):
        """Test configuration creation with all environment variables."""
        env_vars = {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test_key",
            "SUPABASE_SCHEMA": "test_schema",
            "GEMINI_API_KEY": "test_gemini_key",
            "GEMINI_MODEL": "gemini-2.0-flash",
            "APP_NAME": "test_app",
            "LOG_LEVEL": "DEBUG",
            "DEBUG": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            assert config.supabase.url == "https://test.supabase.co"
            assert config.supabase.service_role_key == "test_key"
            assert config.supabase.schema == "test_schema"
            assert config.gemini.api_key == "test_gemini_key"
            assert config.gemini.model == "gemini-2.0-flash"
            assert config.app.name == "test_app"
            assert config.app.log_level == "DEBUG"
            assert config.app.debug is True
    
    def test_config_from_env_defaults(self):
        """Test configuration creation with default values."""
        env_vars = {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test_key",
            "GEMINI_API_KEY": "test_gemini_key"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()
            
            # Check defaults
            assert config.supabase.schema == "public"
            assert config.gemini.model == "gemini-2.0-flash"
            assert config.app.name == "python_database_chatbot"
            assert config.app.log_level == "INFO"
            assert config.app.debug is False
    
    def test_validate_required_fields_success(self):
        """Test successful validation of required fields."""
        config = Config(
            supabase=SupabaseConfig(
                url="https://test.supabase.co",
                service_role_key="test_key"
            ),
            gemini=GeminiConfig(api_key="test_gemini_key"),
            google_cloud={},
            app={}
        )
        
        # Should not raise an exception
        config.validate_required_fields()
    
    def test_validate_required_fields_missing_supabase_url(self):
        """Test validation failure with missing Supabase URL."""
        config = Config(
            supabase=SupabaseConfig(
                url="",
                service_role_key="test_key"
            ),
            gemini=GeminiConfig(api_key="test_gemini_key"),
            google_cloud={},
            app={}
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate_required_fields()
        
        assert "SUPABASE_URL is required" in str(exc_info.value)
    
    def test_validate_required_fields_missing_service_key(self):
        """Test validation failure with missing service role key."""
        config = Config(
            supabase=SupabaseConfig(
                url="https://test.supabase.co",
                service_role_key=""
            ),
            gemini=GeminiConfig(api_key="test_gemini_key"),
            google_cloud={},
            app={}
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate_required_fields()
        
        assert "SUPABASE_SERVICE_ROLE_KEY is required" in str(exc_info.value)
    
    def test_validate_required_fields_missing_gemini_key(self):
        """Test validation failure with missing Gemini API key."""
        config = Config(
            supabase=SupabaseConfig(
                url="https://test.supabase.co",
                service_role_key="test_key"
            ),
            gemini=GeminiConfig(api_key=""),
            google_cloud={},
            app={}
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate_required_fields()
        
        assert "GEMINI_API_KEY is required" in str(exc_info.value)
    
    def test_validate_required_fields_multiple_missing(self):
        """Test validation failure with multiple missing fields."""
        config = Config(
            supabase=SupabaseConfig(
                url="",
                service_role_key=""
            ),
            gemini=GeminiConfig(api_key=""),
            google_cloud={},
            app={}
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate_required_fields()
        
        error_message = str(exc_info.value)
        assert "SUPABASE_URL is required" in error_message
        assert "SUPABASE_SERVICE_ROLE_KEY is required" in error_message
        assert "GEMINI_API_KEY is required" in error_message
