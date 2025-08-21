"""
🤖 CHATBOT AGENT - Main entry point for the database chatbot

WHAT THIS FILE DOES:
This file provides the main interface to the database chatbot system.
It imports and exposes the key components needed to use the chatbot:

- Agent creation and configuration
- Database connection testing
- Conversation state management (if needed)

REFACTORED ARCHITECTURE:
This file has been refactored for better maintainability:
- Individual tools are now in separate files in src/tools/
- Agent creation logic is in agent_factory.py
- Database testing is in utils/database_tester.py
- Each component has a single, focused responsibility

HOW TO USE:
Import the chatbot agent and database tester from this module:
```python
from src.agents.chatbot_agent import chatbot_agent, test_database_connection
```

EXAMPLE CONVERSATION FLOW:
You: "How many students have high anxiety?"
Bot: 1. Validates question is database-related ✓
     2. Loads database schema to understand structure
     3. Generates SQL: "SELECT COUNT(*) FROM students WHERE anxiety_level > 15"
     4. Validates SQL for safety
     5. Executes query on your database
     6. Formats results: "There are 23 students with high anxiety levels."

This orchestration happens automatically through the ADK agent framework.
"""

from typing import Optional
from pydantic import BaseModel

# Import the main components
from .agent_factory import create_chatbot_agent
from ..utils.database_tester import test_database_connection


class ChatbotState(BaseModel):
    """
    📝 CHATBOT MEMORY - Keeps track of what's happening in a conversation
    
    WHAT THIS IS:
    Think of this like the chatbot's notepad where it writes down:
    - What you asked
    - Whether it's a database question
    - What SQL query it created
    - What results it found
    - Any errors that happened
    
    WHY WE NEED THIS:
    Just like you might take notes during a conversation to remember what was said,
    the chatbot needs to remember each step of processing your question.
    
    NOTE: This state class is kept for potential future use with more complex
    conversation flows. The current ADK implementation handles state automatically.
    """
    user_query: str = ""
    is_valid_database_query: bool = False
    generated_sql: str = ""
    sql_explanation: str = ""
    final_response: str = ""
    error: Optional[str] = None
    confidence: float = 0.0
    rejection_reason: Optional[str] = None


# Create the singleton agent instance
chatbot_agent = create_chatbot_agent()


# Export the main components for backward compatibility
__all__ = [
    'chatbot_agent',
    'test_database_connection',
    'ChatbotState'
]
