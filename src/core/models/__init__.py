"""Data models and schemas for the database chatbot."""

from .ai_models import (
    SQLGenerationResult,
    QueryValidationResult,
    ResponseFormattingResult
)
from .database_models import (
    DatabaseQueryResult,
    DatabaseSchema,
    DatabaseConnectionInfo
)

__all__ = [
    # AI models
    'SQLGenerationResult',
    'QueryValidationResult',
    'ResponseFormattingResult',

    # Database models
    'DatabaseQueryResult',
    'DatabaseSchema',
    'DatabaseConnectionInfo'
]
