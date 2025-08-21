#!/usr/bin/env python3
"""
Main entry point for the Python Database Chatbot with Google ADK.
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.environment import config
from src.utils.logger import logger
from src.cli.interface import cli


def main():
    """Main entry point."""
    try:
        # Validate configuration
        config.validate_required_fields()
        
        logger.info(
            "Starting Python Database Chatbot",
            app_name=config.app.name,
            gemini_model=config.gemini.model,
            supabase_schema=config.supabase.schema
        )
        
        # Run CLI
        cli()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("See .env.example for reference.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error("Application error", error=str(e))
        print(f"❌ Application Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
