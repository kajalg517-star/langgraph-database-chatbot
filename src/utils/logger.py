"""
Logging configuration for the Python Database Chatbot.
Uses structlog for structured logging with rich console output.
"""

import sys
import logging
from typing import Any, Dict
import structlog
from rich.console import Console
from rich.logging import RichHandler

from ..config.environment import config


def setup_logging() -> structlog.BoundLogger:
    """Set up structured logging with rich console output."""
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, config.app.log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                show_time=True,
                show_path=config.app.debug,
                markup=True,
                rich_tracebacks=True,
            )
        ],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer(colors=True) if config.app.debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.app.log_level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def log_query_processing(
    logger: structlog.BoundLogger,
    user_query: str,
    sql_query: str = None,
    results_count: int = None,
    error: str = None,
    **kwargs: Any
) -> None:
    """Log query processing with structured data."""
    log_data: Dict[str, Any] = {
        "event": "query_processing",
        "user_query": user_query,
        **kwargs
    }
    
    if sql_query:
        log_data["sql_query"] = sql_query
    if results_count is not None:
        log_data["results_count"] = results_count
    if error:
        log_data["error"] = error
        logger.error("Query processing failed", **{k: v for k, v in log_data.items() if k != 'event'})
    else:
        logger.info("Query processed successfully", **{k: v for k, v in log_data.items() if k != 'event'})


def log_agent_interaction(
    logger: structlog.BoundLogger,
    session_id: str,
    user_id: str,
    message_type: str,
    content: str = None,
    **kwargs: Any
) -> None:
    """Log agent interactions with session context."""
    log_data: Dict[str, Any] = {
        "event": "agent_interaction",
        "session_id": session_id,
        "user_id": user_id,
        "message_type": message_type,
        **kwargs
    }
    
    if content:
        log_data["content"] = content[:200] + "..." if len(content) > 200 else content

    logger.info("Agent interaction", **{k: v for k, v in log_data.items() if k != 'event'})


# Global logger instance
logger = setup_logging()
