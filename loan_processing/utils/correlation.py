"""
Correlation ID management for request tracing across components.

This module provides correlation ID generation and propagation using
async context variables for clean request tracking.
"""

import uuid
from contextvars import ContextVar
from typing import Optional


# Context variable for correlation ID (when not using Azure OTEL)
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.
    
    Returns:
        New UUID-based correlation ID
    """
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    _correlation_id.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID from context.
    
    Returns:
        Current correlation ID or None if not set
    """
    from . import _azure_enabled
    
    if _azure_enabled:
        # Try to get from OpenTelemetry context
        try:
            from opentelemetry import trace
            span = trace.get_current_span()
            if span.is_recording():
                return f"{span.get_span_context().trace_id:032x}"
        except ImportError:
            pass
    
    # Fallback to our context variable
    return _correlation_id.get()


class correlation_context:
    """
    Context manager for correlation ID propagation.
    
    Usage:
        async with correlation_context(correlation_id):
            # All operations inherit correlation_id
            result = await process_application(app)
    """
    
    def __init__(self, correlation_id: Optional[str] = None):
        """
        Initialize correlation context.
        
        Args:
            correlation_id: Correlation ID to set, or None to generate new one
        """
        self.correlation_id = correlation_id or generate_correlation_id()
        self.token = None
    
    def __enter__(self):
        """Enter the correlation context."""
        self.token = _correlation_id.set(self.correlation_id)
        return self.correlation_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the correlation context."""
        if self.token is not None:
            _correlation_id.reset(self.token)
    
    async def __aenter__(self):
        """Async enter the correlation context."""
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit the correlation context."""
        return self.__exit__(exc_type, exc_val, exc_tb)