"""
🏭 DATABASE SERVICE FACTORY - Creates the right database service for your needs

WHAT THIS FILE DOES:
This file acts like a factory that creates the appropriate database service based on
your configuration. It's the central place that decides which database provider to use
and handles the creation of database service instances.

WHY WE NEED THIS:
- **Centralized Configuration**: One place to control which database provider is used
- **Easy Switching**: Change database providers by updating configuration
- **Future Expansion**: Easy to add new database providers
- **Testing Support**: Can create mock database services for testing

SUPPORTED DATABASE PROVIDERS:
- 🗄️ Supabase (PostgreSQL-based) - Current default
- 🐘 PostgreSQL (Direct connection, Future)
- 🐬 MySQL/MariaDB (Future)
- 📁 SQLite (Future)
- 🏢 Microsoft SQL Server (Future)

HOW IT WORKS:
1. Reads configuration to determine which database provider to use
2. Creates and configures the appropriate database service instance
3. Returns a service that implements the standard DatabaseServiceInterface
4. The rest of the application doesn't need to know which provider is being used

DESIGN PATTERN:
This implements the Factory Pattern, which is perfect for creating objects
when you don't know exactly which type you need until runtime.
"""

from typing import Optional
from enum import Enum

from ...core.interfaces.database_service_interface import DatabaseServiceInterface
from ..database.supabase_database_service import SupabaseDatabaseService
from ...config.environment import config
from ...utils.logger import logger


class DatabaseProvider(Enum):
    """
    🎯 DATABASE PROVIDER ENUM - Supported database providers
    
    WHAT THIS IS:
    An enumeration of all supported database providers. This makes it easy to
    add new providers and ensures type safety when selecting providers.
    
    CURRENT PROVIDERS:
    - SUPABASE: Supabase PostgreSQL (default)
    
    FUTURE PROVIDERS:
    - POSTGRESQL: Direct PostgreSQL connection
    - MYSQL: MySQL/MariaDB
    - SQLITE: SQLite database
    - SQLSERVER: Microsoft SQL Server
    """
    SUPABASE = "supabase"
    # Future providers can be added here:
    # POSTGRESQL = "postgresql"
    # MYSQL = "mysql"
    # SQLITE = "sqlite"
    # SQLSERVER = "sqlserver"


class DatabaseServiceFactory:
    """
    🏭 DATABASE SERVICE FACTORY - Creates database service instances
    
    WHAT THIS CLASS DOES:
    This factory class is responsible for creating the right database service
    based on configuration. It handles all the complexity of instantiating
    different database providers.
    
    BENEFITS:
    - **Abstraction**: Hides the complexity of creating different database services
    - **Flexibility**: Easy to switch between database providers
    - **Consistency**: All database services follow the same interface
    - **Testability**: Can create mock services for testing
    
    USAGE:
    ```python
    # Create the default database service (Supabase)
    db_service = DatabaseServiceFactory.create_database_service()
    
    # Create a specific database service
    db_service = DatabaseServiceFactory.create_database_service(DatabaseProvider.SUPABASE)
    ```
    """
    
    @staticmethod
    def create_database_service(provider: Optional[DatabaseProvider] = None) -> DatabaseServiceInterface:
        """
        🎯 CREATE DATABASE SERVICE - Factory method to create database service instances
        
        WHAT THIS DOES:
        Creates and returns a database service instance based on the specified provider
        or the default configuration.
        
        PROVIDER SELECTION:
        1. Use the provider parameter if specified
        2. Otherwise, use the provider from configuration
        3. Fall back to Supabase as the default
        
        ERROR HANDLING:
        - Validates that the requested provider is supported
        - Provides helpful error messages for unsupported providers
        - Falls back to default provider if configuration is invalid
        
        Args:
            provider: Optional specific database provider to use
            
        Returns:
            DatabaseServiceInterface: Configured database service instance
            
        Raises:
            ValueError: If the requested provider is not supported
        """
        # Determine which provider to use
        if provider is None:
            # Try to get provider from configuration
            provider_name = getattr(config.supabase, 'provider', 'supabase').lower()
            try:
                provider = DatabaseProvider(provider_name)
            except ValueError:
                logger.warning(
                    f"Unknown database provider '{provider_name}' in configuration, falling back to Supabase"
                )
                provider = DatabaseProvider.SUPABASE
        
        # Create the appropriate service
        if provider == DatabaseProvider.SUPABASE:
            logger.info("Creating Supabase database service")
            return SupabaseDatabaseService()
        
        # Future providers can be added here:
        # elif provider == DatabaseProvider.POSTGRESQL:
        #     logger.info("Creating PostgreSQL database service")
        #     return PostgreSQLDatabaseService()
        # elif provider == DatabaseProvider.MYSQL:
        #     logger.info("Creating MySQL database service")
        #     return MySQLDatabaseService()
        
        else:
            raise ValueError(f"Unsupported database provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> list[DatabaseProvider]:
        """
        📋 GET AVAILABLE PROVIDERS - List all supported database providers
        
        WHAT THIS DOES:
        Returns a list of all currently supported database providers.
        Useful for configuration validation and user interfaces.
        
        Returns:
            List of supported DatabaseProvider enum values
        """
        return [DatabaseProvider.SUPABASE]
        # Future: return [DatabaseProvider.SUPABASE, DatabaseProvider.POSTGRESQL, ...]
    
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
            DatabaseProvider(provider.lower())
            return True
        except ValueError:
            return False


# Convenience function for creating the default database service
def create_default_database_service() -> DatabaseServiceInterface:
    """
    🎯 CREATE DEFAULT DATABASE SERVICE - Quick way to get the default database service
    
    WHAT THIS DOES:
    Creates and returns the default database service instance. This is a convenience
    function that most of the application will use.
    
    CURRENT DEFAULT:
    Supabase PostgreSQL database service
    
    FUTURE:
    The default can be changed by updating the configuration or this function.
    
    Returns:
        DatabaseServiceInterface: Default database service instance
    """
    return DatabaseServiceFactory.create_database_service()


# Create the singleton database service instance
database_service = create_default_database_service()
