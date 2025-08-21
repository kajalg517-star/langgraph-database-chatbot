"""Abstract interfaces and protocols for the database chatbot."""

from .ai_service_interface import AIServiceInterface
from .database_service_interface import DatabaseServiceInterface

__all__ = [
    'AIServiceInterface',
    'DatabaseServiceInterface'
]
