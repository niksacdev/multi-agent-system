"""
Core logging functionality.

This module provides the main logging interface with structured logging
and optional Azure Application Insights integration.
"""

import os

import structlog


def get_logger(name: str):
    """
    Get a structured logger that works with or without Azure.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    from . import _ensure_configured

    # Ensure logging is configured
    _ensure_configured()

    return structlog.get_logger(name)


def get_logging_status():
    """
    Return current logging configuration status.

    Returns:
        Dictionary with logging configuration details
    """
    from . import _azure_enabled

    return {
        "console_logging": True,  # Always available
        "azure_enabled": _azure_enabled,
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_format": os.getenv("LOG_FORMAT", "console"),
        "azure_connection_configured": bool(os.getenv("AZURE_MONITOR_CONNECTION_STRING")),
    }
