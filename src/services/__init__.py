"""
🔧 SERVICES MODULE - AI and external service integrations

WHAT THIS MODULE CONTAINS:
This module contains all the services that integrate with external systems
like AI providers and databases. It provides a clean, extensible architecture
for working with different service providers.

ARCHITECTURE OVERVIEW:
- 🎯 AI Service Interface: Abstract base for all AI providers
- 🤖 Gemini AI Service: Google Gemini implementation
- 🏭 AI Service Factory: Creates appropriate AI service instances
- 📊 Database Services: Database connection and operations (in tools/)

KEY BENEFITS:
- **Provider Agnostic**: Easy to switch between AI providers
- **Extensible**: Add new providers without changing existing code
- **Testable**: Mock services for testing
- **Consistent**: All providers follow the same interface

SUPPORTED AI PROVIDERS:
- ✅ Google Gemini AI (current default)
- 🔮 OpenAI GPT (future)
- 🦙 Ollama (future)
- 🧠 Anthropic Claude (future)

USAGE EXAMPLES:
```python
# Use the default AI service (recommended)
from src.services import ai_service

# Create specific AI service
from src.services import AIServiceFactory, AIProvider
ai_service = AIServiceFactory.create_ai_service(AIProvider.GEMINI)

# Backward compatibility
from src.services import gemini_service  # Same as ai_service
```

MIGRATION FROM OLD ARCHITECTURE:
The old `gemini_service` is still available for backward compatibility,
but now it's created through the new factory system. All existing code
continues to work without changes.
"""

# Import AI service components
from .ai_service_interface import (
    AIServiceInterface,
    SQLGenerationResult,
    QueryValidationResult,
    ResponseFormattingResult
)
from .gemini_ai_service import GeminiAIService
from .ai_service_factory import (
    AIServiceFactory,
    AIProvider,
    create_default_ai_service,
    ai_service,
    gemini_service  # Backward compatibility
)

# Import database service components
from .database_service_interface import (
    DatabaseServiceInterface,
    DatabaseQueryResult,
    DatabaseSchema,
    DatabaseConnectionInfo
)
from .supabase_database_service import SupabaseDatabaseService
from .database_service_factory import (
    DatabaseServiceFactory,
    DatabaseProvider,
    create_default_database_service,
    database_service
)

# Export all components for external use
__all__ = [
    # AI service interfaces and models
    'AIServiceInterface',
    'SQLGenerationResult',
    'QueryValidationResult',
    'ResponseFormattingResult',

    # AI service implementations
    'GeminiAIService',

    # AI service factory and utilities
    'AIServiceFactory',
    'AIProvider',
    'create_default_ai_service',

    # Database service interfaces and models
    'DatabaseServiceInterface',
    'DatabaseQueryResult',
    'DatabaseSchema',
    'DatabaseConnectionInfo',

    # Database service implementations
    'SupabaseDatabaseService',

    # Database service factory and utilities
    'DatabaseServiceFactory',
    'DatabaseProvider',
    'create_default_database_service',

    # Service instances
    'ai_service',
    'database_service',
    'gemini_service'  # Backward compatibility
]
