"""
Shared utilities for the loan processing system.

This module provides:
1. Configuration loading utilities
2. Persona loading for agents
3. Output formatting utilities
4. Safe expression evaluation
5. Production-ready observability infrastructure with optional Azure Application Insights

Observability Features:
- Console logging for development (human-readable)
- Structured JSON logging for production
- Optional Azure Application Insights integration
- Automatic correlation ID tracking
- Graceful degradation when Azure is unavailable

Usage:
    from loan_processing.utils import get_logger, ConfigurationLoader

    logger = get_logger(__name__)
    logger.info("Processing started", application_id="123")

Environment Variables:
    LOG_LEVEL: INFO, DEBUG, WARNING, ERROR (default: INFO)
    LOG_FORMAT: console, json (default: console)
    AZURE_MONITOR_CONNECTION_STRING: Azure App Insights connection (optional)
"""

# Import existing utilities
# Import observability infrastructure
from .config import configure_logging, is_azure_enabled, is_configured
from .config_loader import ConfigurationLoader
from .correlation import correlation_context, generate_correlation_id, get_correlation_id, set_correlation_id
from .decorators import log_execution
from .logger import get_logger, get_logging_status
from .output_formatter import OutputFormatGenerator
from .persona_loader import PersonaLoader, load_persona
from .safe_evaluator import SafeConditionEvaluator, evaluate_condition

# Global state (accessed by submodules)
_azure_enabled = False
_logging_configured = False


def _ensure_configured():
    """Ensure logging is configured before use."""
    global _azure_enabled, _logging_configured

    if not _logging_configured:
        configure_logging()
        _azure_enabled = is_azure_enabled()
        _logging_configured = is_configured()


# Initialize logging on import
_ensure_configured()

# Export public API
__all__ = [
    # Existing utilities
    "ConfigurationLoader",
    "OutputFormatGenerator",
    "PersonaLoader",
    "load_persona",
    "SafeConditionEvaluator",
    "evaluate_condition",
    # Observability
    "get_logger",
    "get_logging_status",
    "log_execution",
    "correlation_context",
    "get_correlation_id",
    "set_correlation_id",
    "generate_correlation_id",
]
