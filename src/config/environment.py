"""
Environment configuration for the Python Database Chatbot.
Handles loading and validation of environment variables.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SupabaseConfig(BaseModel):
    """Supabase database configuration."""
    url: str = Field(..., description="Supabase project URL")
    service_role_key: str = Field(..., description="Supabase service role key")
    schema: str = Field(default="public", description="Database schema name")


class GeminiConfig(BaseModel):
    """Gemini AI configuration."""
    api_key: str = Field(..., description="Gemini API key")
    model: str = Field(default="gemini-2.0-flash", description="Gemini model to use")


class GoogleCloudConfig(BaseModel):
    """Optional Google Cloud configuration."""
    project_id: Optional[str] = Field(None, description="Google Cloud project ID")
    credentials_path: Optional[str] = Field(None, description="Path to service account JSON")


class AppConfig(BaseModel):
    """Application configuration."""
    name: str = Field(default="python_database_chatbot", description="Application name")
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")


class Config(BaseModel):
    """Main configuration class."""
    supabase: SupabaseConfig
    gemini: GeminiConfig
    google_cloud: GoogleCloudConfig
    app: AppConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            supabase=SupabaseConfig(
                url=os.getenv("SUPABASE_URL", ""),
                service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
                schema=os.getenv("SUPABASE_SCHEMA", "public"),
            ),
            gemini=GeminiConfig(
                api_key=os.getenv("GEMINI_API_KEY", ""),
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            ),
            google_cloud=GoogleCloudConfig(
                project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
                credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            ),
            app=AppConfig(
                name=os.getenv("APP_NAME", "python_database_chatbot"),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                debug=os.getenv("DEBUG", "false").lower() == "true",
            ),
        )

    def validate_required_fields(self) -> None:
        """Validate that all required configuration fields are present."""
        errors = []
        
        if not self.supabase.url:
            errors.append("SUPABASE_URL is required")
        if not self.supabase.service_role_key:
            errors.append("SUPABASE_SERVICE_ROLE_KEY is required")
        if not self.gemini.api_key:
            errors.append("GEMINI_API_KEY is required")
        
        if errors:
            raise ValueError(f"Missing required environment variables: {', '.join(errors)}")


# Global configuration instance
config = Config.from_env()
