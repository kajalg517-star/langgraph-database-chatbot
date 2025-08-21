"""
🤖 AGENTS MODULE - The brain of the chatbot system

WHAT THIS MODULE CONTAINS:
This module contains the core agent logic that orchestrates all the tools
and services to create an intelligent database assistant.

COMPONENTS:
- Agent Factory: Creates and configures the main chatbot agent
- Chatbot State: Manages conversation state and memory (if needed)

ARCHITECTURE:
The agent acts as the central coordinator that:
1. Receives user questions
2. Determines the appropriate workflow
3. Calls the right tools in the right order
4. Manages conversation context
5. Returns helpful responses

MODULAR DESIGN:
The agent factory is separated from tool implementations for better
organization and maintainability. This allows easy modification of
agent behavior without touching individual tool logic.
"""

# Import main agent components
from .agent_factory import create_chatbot_agent

# Export for external use
__all__ = [
    'create_chatbot_agent'
]
