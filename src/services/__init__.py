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

# Use the default database service (recommended)
from src.services import database_service

# Create specific services
from src.services import AIServiceFactory, AIProvider, DatabaseServiceFactory, DatabaseProvider
ai_service = AIServiceFactory.create_ai_service(AIProvider.GEMINI)
db_service = DatabaseServiceFactory.create_database_service(DatabaseProvider.SUPABASE)
```

NEW MODULAR ARCHITECTURE:
This architecture provides complete separation of concerns between AI and database
operations, making the system more maintainable, testable, and extensible.
"""

# Import AI service components
from ..core.interfaces.ai_service_interface import AIServiceInterface
from ..core.models.ai_models import (
    SQLGenerationResult,
    QueryValidationResult,
    ResponseFormattingResult
)
from .ai.gemini_ai_service import GeminiAIService
from .factories.ai_service_factory import (
    AIServiceFactory,
    AIProvider,
    create_default_ai_service,
    ai_service
)

# Import database service components
from ..core.interfaces.database_service_interface import DatabaseServiceInterface
from ..core.models.database_models import (
    DatabaseQueryResult,
    DatabaseSchema,
    DatabaseConnectionInfo
)
from .database.supabase_database_service import SupabaseDatabaseService
from .factories.database_service_factory import (
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
    'database_service'
]
