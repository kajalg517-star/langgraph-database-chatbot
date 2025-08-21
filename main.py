#!/usr/bin/env python3
"""
🚀 MAIN PROGRAM LAUNCHER - Start Your Database Chatbot Here!

WHAT THIS FILE DOES:
This is the "front door" of your chatbot application. When you run the program,
this file starts everything up and gets the chatbot ready to answer your questions.

HOW TO USE:
1. Open your terminal/command prompt
2. Navigate to this folder
3. Run one of these commands:

   🧪 Test your database connection:
   python main.py test

   💬 Start interactive chat (recommended):
   python main.py chat

   ❓ Ask a single question:
   python main.py query "How many students are there?"

WHAT HAPPENS WHEN YOU RUN IT:
1. ✅ Checks your configuration (.env file)
2. ✅ Validates your database and AI credentials
3. ✅ Starts up the Google ADK agent
4. ✅ Connects to your Supabase database
5. ✅ Launches the beautiful command-line interface
6. 🎉 Ready to answer your database questions!

TROUBLESHOOTING:
If something goes wrong, this file will show you helpful error messages
to guide you toward fixing the problem.
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
    """
    🎬 MAIN FUNCTION - The Director of the Show

    WHAT THIS FUNCTION DOES:
    This is like the director of a movie - it coordinates everything:
    1. Checks that all your settings are correct
    2. Makes sure your database and AI credentials work
    3. Starts up all the chatbot components
    4. Handles any startup problems gracefully
    5. Launches the command-line interface

    IF SOMETHING GOES WRONG:
    This function will catch problems and show you friendly error messages
    instead of scary technical errors. It helps you understand what needs
    to be fixed.
    """
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
