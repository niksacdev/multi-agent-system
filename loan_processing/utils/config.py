"""
Observability configuration and setup.

This module handles the configuration of structured logging with optional
Azure Application Insights integration.
"""

import logging
import os

import structlog

# Load environment variables from .env file if not already loaded
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv is optional for observability module
    pass

from .correlation import get_correlation_id

# Global configuration state
_logging_configured = False
_azure_enabled = False


def configure_logging():
    """
    Configure logging with optional Azure integration.

    This function is safe to call multiple times and will only configure once.
    """
    global _logging_configured, _azure_enabled

    if _logging_configured:
        return

    # Determine log format
    log_format = os.getenv("LOG_FORMAT", "console").lower()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure structlog processors
    processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        _add_correlation_context,  # Add our correlation ID
    ]

    # Add appropriate renderer based on format
    if log_format == "console":
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Set log level for root logger
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

    # Optional Azure integration
    azure_connection_string = os.getenv("AZURE_MONITOR_CONNECTION_STRING")
    if azure_connection_string:
        _azure_enabled = _configure_azure_monitor(azure_connection_string)
    else:
        print("📝 Using console logging (set AZURE_MONITOR_CONNECTION_STRING for Azure integration)")

    # Quiet noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    _logging_configured = True


def _configure_azure_monitor(connection_string: str) -> bool:
    """
    Configure Azure Monitor integration.

    Args:
        connection_string: Azure Monitor connection string

    Returns:
        True if Azure was successfully configured, False otherwise
    """
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string, enable_live_metrics=True)
        print("✅ Azure Application Insights enabled")
        return True
    except ImportError:
        print("⚠️  Azure dependencies not installed (install with: uv sync --extra azure)")
        print("   Using console logging only")
        return False
    except Exception as e:
        print(f"⚠️  Azure configuration failed: {e}")
        print("   Using console logging only")
        return False


def _add_correlation_context(logger, method_name, event_dict):
    """Add correlation ID to log events."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def is_configured() -> bool:
    """Check if logging has been configured."""
    return _logging_configured


def is_azure_enabled() -> bool:
    """Check if Azure integration is enabled."""
    return _azure_enabled
