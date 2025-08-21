"""
🖥️ COMMAND LINE INTERFACE - Your Beautiful Chat Experience

WHAT THIS FILE DOES:
This file creates the beautiful, user-friendly interface you see when chatting
with your database bot. It's like the "face" of your chatbot that makes
everything look professional and easy to use.

FEATURES YOU'LL SEE:
🎨 Beautiful colored panels and formatting
⏳ Spinning animations while processing your questions
📊 Organized display of results
💬 Friendly conversation flow
🧵 Session tracking (remembers your conversation)
❌ Clear error messages if something goes wrong

THREE WAYS TO USE YOUR CHATBOT:

1. 🧪 TEST MODE: python main.py test
   - Quickly checks if your database connection works
   - Shows green ✅ if everything is working
   - Shows red ❌ with helpful tips if there are problems

2. 💬 INTERACTIVE CHAT MODE: python main.py chat (RECOMMENDED!)
   - Start a conversation with your database
   - Ask multiple questions in a row
   - The bot remembers context from previous questions
   - Type 'exit' when you're done
   - Beautiful welcome screen and formatting

3. ❓ SINGLE QUESTION MODE: python main.py query "your question"
   - Ask one quick question and get an answer
   - Perfect for scripts or quick lookups
   - No conversation memory, just one-and-done

The interface uses Google ADK's Runner system to manage conversations
and provides a much better experience than basic command-line tools.
"""

import asyncio
import sys
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..agents.chatbot_agent import chatbot_agent, test_database_connection
from ..config.environment import config
from ..utils.logger import logger, log_agent_interaction

# Initialize rich console
console = Console()


class ChatbotCLI:
    """CLI interface for the database chatbot."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=chatbot_agent,
            app_name=config.app.name,
            session_service=self.session_service
        )
        self.current_session = None
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        console.print("🔄 Testing database connection...", style="blue")
        
        try:
            connection_ok = await test_database_connection()
            
            if connection_ok:
                console.print("✅ Database connection successful", style="green")
                return True
            else:
                console.print("❌ Database connection failed", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Database connection error: {str(e)}", style="red")
            return False
    
    async def start_interactive_chat(self) -> None:
        """Start interactive chat session."""
        # Display welcome message
        welcome_panel = Panel.fit(
            Text.from_markup(
                "[bold blue]🤖 Interactive Database Chatbot with Google ADK[/bold blue]\n"
                "[dim]Ask me questions about your database in natural language![/dim]\n"
                "[yellow]⚠️  I can only answer database-related questions.[/yellow]\n"
                "[dim]Type 'exit' or 'quit' to end the session.[/dim]"
            ),
            title="Welcome",
            border_style="blue"
        )
        console.print(welcome_panel)
        console.print()
        
        # Test database connection first
        if not await self.test_connection():
            console.print("Cannot proceed without database connection.", style="red")
            return
        
        # Create session
        session_id = f"chat_{asyncio.get_event_loop().time()}_{id(self)}"
        user_id = "cli_user"
        
        try:
            self.current_session = await self.session_service.create_session(
                app_name=config.app.name,
                user_id=user_id,
                session_id=session_id
            )
            
            console.print(f"🧵 Session ID: [dim]{session_id}[/dim]")
            console.print()
            
            # Start interactive loop
            await self._interactive_loop(user_id, session_id)
            
        except Exception as e:
            console.print(f"❌ Failed to create session: {str(e)}", style="red")
            logger.error("Session creation failed", error=str(e))
    
    async def _interactive_loop(self, user_id: str, session_id: str) -> None:
        """Main interactive loop."""
        while True:
            try:
                # Get user input
                user_input = console.input("\n💬 [bold]Your database question:[/bold] ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("\n👋 [yellow]Goodbye! Thanks for using the database chatbot.[/yellow]")
                    break
                
                # Process the query
                await self._process_query_with_spinner(user_id, session_id, user_input)
                
            except KeyboardInterrupt:
                console.print("\n\n👋 [yellow]Shutting down gracefully...[/yellow]")
                break
            except EOFError:
                console.print("\n\n👋 [yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"\n❌ [red]Error:[/red] {str(e)}")
                logger.error("Interactive loop error", error=str(e))
    
    async def _process_query_with_spinner(self, user_id: str, session_id: str, user_input: str) -> None:
        """Process query with a spinner for better UX."""
        with console.status("[bold blue]Processing your database query...", spinner="dots"):
            try:
                # Log the interaction
                log_agent_interaction(
                    logger,
                    session_id=session_id,
                    user_id=user_id,
                    message_type="user_input",
                    content=user_input
                )
                
                # Create content for the agent
                content = types.Content(
                    role='user',
                    parts=[types.Part(text=user_input)]
                )
                
                # Run the agent
                events = self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content
                )
                
                # Process events and get final response
                final_response = None
                async for event in events:
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            final_response = event.content.parts[0].text
                        break
                
                # Display response
                if final_response:
                    response_panel = Panel.fit(
                        Text(final_response, style="white"),
                        title="🔍 Response",
                        border_style="green"
                    )
                    console.print("\n")
                    console.print(response_panel)
                    
                    # Log the response
                    log_agent_interaction(
                        logger,
                        session_id=session_id,
                        user_id=user_id,
                        message_type="agent_response",
                        content=final_response
                    )
                else:
                    console.print("\n❌ [red]No response generated.[/red]")
                
            except Exception as e:
                console.print(f"\n❌ [red]Error processing query:[/red] {str(e)}")
                logger.error("Query processing error", error=str(e), user_input=user_input)
    
    async def execute_single_query(self, query: str) -> None:
        """Execute a single query and exit."""
        # Display header
        header_panel = Panel.fit(
            Text.from_markup(
                "[bold blue]🤖 Database Chatbot with Google ADK[/bold blue]\n"
                f"[dim]Processing: \"{query}\"[/dim]\n"
                "[yellow]⚠️  I can only answer database-related questions.[/yellow]"
            ),
            title="Single Query Mode",
            border_style="blue"
        )
        console.print(header_panel)
        console.print()
        
        # Test database connection
        if not await self.test_connection():
            console.print("Cannot proceed without database connection.", style="red")
            return
        
        # Create temporary session
        session_id = f"single_{asyncio.get_event_loop().time()}"
        user_id = "cli_user"
        
        try:
            session = await self.session_service.create_session(
                app_name=config.app.name,
                user_id=user_id,
                session_id=session_id
            )
            
            # Process the query
            await self._process_query_with_spinner(user_id, session_id, query)
            
        except Exception as e:
            console.print(f"❌ Failed to process query: {str(e)}", style="red")
            logger.error("Single query execution failed", error=str(e))


# CLI command definitions
@click.group()
def cli():
    """Python Database Chatbot with Google ADK"""
    pass


@cli.command()
def chat():
    """Start interactive chat session"""
    try:
        chatbot_cli = ChatbotCLI()
        asyncio.run(chatbot_cli.start_interactive_chat())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('query')
def query(query: str):
    """Execute a single query"""
    try:
        chatbot_cli = ChatbotCLI()
        asyncio.run(chatbot_cli.execute_single_query(query))
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
def test():
    """Test database connection"""
    try:
        chatbot_cli = ChatbotCLI()
        connection_ok = asyncio.run(chatbot_cli.test_connection())
        sys.exit(0 if connection_ok else 1)
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
