"""
🔧 UTILITIES MODULE - Helper functions and common utilities

WHAT THIS MODULE CONTAINS:
This module contains utility functions and helpers that are used throughout
the chatbot system. These are the "support staff" that help everything run smoothly.

COMPONENTS:
- Logger: Structured logging for debugging and monitoring
- Database Tester: Connection testing and health checks

PURPOSE:
Utilities provide common functionality that multiple parts of the system need,
such as logging, testing, validation, and other support functions.

DESIGN PRINCIPLE:
Keep utilities focused and reusable. Each utility should have a single,
clear purpose and be usable by multiple parts of the system.
"""

# Import utility functions
from .logger import logger, log_agent_interaction, log_query_processing
from .database_tester import test_database_connection, get_database_status

# Export for external use
__all__ = [
    'logger',
    'log_agent_interaction',
    'log_query_processing',
    'test_database_connection',
    'get_database_status'
]
