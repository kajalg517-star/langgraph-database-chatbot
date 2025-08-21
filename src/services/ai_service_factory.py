"""
🏭 AI SERVICE FACTORY - Creates the right AI service for your needs

WHAT THIS FILE DOES:
This file acts like a factory that creates the appropriate AI service based on
your configuration. It's the central place that decides which AI provider to use
and handles the creation of AI service instances.

WHY WE NEED THIS:
- **Centralized Configuration**: One place to control which AI provider is used
- **Easy Switching**: Change AI providers by updating configuration
- **Future Expansion**: Easy to add new AI providers
- **Testing Support**: Can create mock AI services for testing

SUPPORTED AI PROVIDERS:
- 🤖 Gemini AI (Google) - Current default
- 🔮 OpenAI GPT (Future)
- 🦙 Ollama (Local models, Future)
- 🧠 Anthropic Claude (Future)
- ☁️ Azure OpenAI (Future)

HOW IT WORKS:
1. Reads configuration to determine which AI provider to use
2. Creates and configures the appropriate AI service instance
3. Returns a service that implements the standard AIServiceInterface
4. The rest of the application doesn't need to know which provider is being used

DESIGN PATTERN:
This implements the Factory Pattern, which is perfect for creating objects
when you don't know exactly which type you need until runtime.
"""

from typing import Optional
from enum import Enum

from .ai_service_interface import AIServiceInterface
from .gemini_ai_service import GeminiAIService
from ..config.environment import config
from ..utils.logger import logger


class AIProvider(Enum):
    """
    🎯 AI PROVIDER ENUM - Supported AI providers
    
    WHAT THIS IS:
    An enumeration of all supported AI providers. This makes it easy to
    add new providers and ensures type safety when selecting providers.
    
    CURRENT PROVIDERS:
    - GEMINI: Google's Gemini AI (default)
    
    FUTURE PROVIDERS:
    - OPENAI: OpenAI GPT models
    - OLLAMA: Local models via Ollama
    - CLAUDE: Anthropic's Claude
    - AZURE_OPENAI: Microsoft Azure OpenAI
    """
    GEMINI = "gemini"
    # Future providers can be added here:
    # OPENAI = "openai"
    # OLLAMA = "ollama"
    # CLAUDE = "claude"
    # AZURE_OPENAI = "azure_openai"


class AIServiceFactory:
    """
    🏭 AI SERVICE FACTORY - Creates AI service instances
    
    WHAT THIS CLASS DOES:
    This factory class is responsible for creating the right AI service
    based on configuration. It handles all the complexity of instantiating
    different AI providers.
    
    BENEFITS:
    - **Abstraction**: Hides the complexity of creating different AI services
    - **Flexibility**: Easy to switch between AI providers
    - **Consistency**: All AI services follow the same interface
    - **Testability**: Can create mock services for testing
    
    USAGE:
    ```python
    # Create the default AI service (Gemini)
    ai_service = AIServiceFactory.create_ai_service()
    
    # Create a specific AI service
    ai_service = AIServiceFactory.create_ai_service(AIProvider.GEMINI)
    ```
    """
    
    @staticmethod
    def create_ai_service(provider: Optional[AIProvider] = None) -> AIServiceInterface:
        """
        🎯 CREATE AI SERVICE - Factory method to create AI service instances
        
        WHAT THIS DOES:
        Creates and returns an AI service instance based on the specified provider
        or the default configuration.
        
        PROVIDER SELECTION:
        1. Use the provider parameter if specified
        2. Otherwise, use the provider from configuration
        3. Fall back to Gemini as the default
        
        ERROR HANDLING:
        - Validates that the requested provider is supported
        - Provides helpful error messages for unsupported providers
        - Falls back to default provider if configuration is invalid
        
        Args:
            provider: Optional specific AI provider to use
            
        Returns:
            AIServiceInterface: Configured AI service instance
            
        Raises:
            ValueError: If the requested provider is not supported
        """
        # Determine which provider to use
        if provider is None:
            # Try to get provider from configuration
            provider_name = getattr(config.gemini, 'provider', 'gemini').lower()
            try:
                provider = AIProvider(provider_name)
            except ValueError:
                logger.warning(
                    f"Unknown AI provider '{provider_name}' in configuration, falling back to Gemini"
                )
                provider = AIProvider.GEMINI
        
        # Create the appropriate service
        if provider == AIProvider.GEMINI:
            logger.info("Creating Gemini AI service")
            return GeminiAIService()
        
        # Future providers can be added here:
        # elif provider == AIProvider.OPENAI:
        #     logger.info("Creating OpenAI service")
        #     return OpenAIService()
        # elif provider == AIProvider.OLLAMA:
        #     logger.info("Creating Ollama service")
        #     return OllamaService()
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> list[AIProvider]:
        """
        📋 GET AVAILABLE PROVIDERS - List all supported AI providers
        
        WHAT THIS DOES:
        Returns a list of all currently supported AI providers.
        Useful for configuration validation and user interfaces.
        
        Returns:
            List of supported AIProvider enum values
        """
        return [AIProvider.GEMINI]
        # Future: return [AIProvider.GEMINI, AIProvider.OPENAI, AIProvider.OLLAMA, ...]
    
    @staticmethod
    def is_provider_supported(provider: str) -> bool:
        """
        ✅ IS PROVIDER SUPPORTED - Check if a provider is supported
        
        WHAT THIS DOES:
        Validates whether a given provider name is supported by the factory.
        Useful for configuration validation.
        
        Args:
            provider: Provider name to check (case-insensitive)
            
        Returns:
            Boolean indicating if the provider is supported
        """
        try:
            AIProvider(provider.lower())
            return True
        except ValueError:
            return False


# Convenience function for creating the default AI service
def create_default_ai_service() -> AIServiceInterface:
    """
    🎯 CREATE DEFAULT AI SERVICE - Quick way to get the default AI service
    
    WHAT THIS DOES:
    Creates and returns the default AI service instance. This is a convenience
    function that most of the application will use.
    
    CURRENT DEFAULT:
    Google Gemini AI (gemini-2.0-flash)
    
    FUTURE:
    The default can be changed by updating the configuration or this function.
    
    Returns:
        AIServiceInterface: Default AI service instance
    """
    return AIServiceFactory.create_ai_service()


# Create the singleton AI service instance for backward compatibility
ai_service = create_default_ai_service()

# For backward compatibility, also export as gemini_service
# This allows existing code to continue working without changes
gemini_service = ai_service
