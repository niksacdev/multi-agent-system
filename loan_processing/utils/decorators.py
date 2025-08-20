"""
Logging decorators for automatic instrumentation.

This module provides decorators to automatically log function execution
with timing and error handling.
"""

import asyncio
import functools
import time
from typing import Any

from .correlation import get_correlation_id
from .logger import get_logger


def log_execution(component: str, operation: str):
    """
    Decorator to automatically log function execution with timing.

    Args:
        component: Component name (e.g., "mcp_server", "agent", "orchestrator")
        operation: Operation name (e.g., "credit_check", "process_application")

    Usage:
        @log_execution(component="mcp_server", operation="retrieve_credit_report")
        async def retrieve_credit_report(applicant_id: str) -> str:
            return result
    """

    def decorator(func):
        logger = get_logger(func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            correlation_id = get_correlation_id()
            start_time = time.time()

            logger.info(
                f"{operation} started",
                component=component,
                operation=operation,
                correlation_id=correlation_id,
                function=func.__name__,
            )

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"{operation} completed",
                    component=component,
                    operation=operation,
                    correlation_id=correlation_id,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="success",
                )
                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"{operation} failed: {str(e)}",
                    component=component,
                    operation=operation,
                    correlation_id=correlation_id,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            correlation_id = get_correlation_id()
            start_time = time.time()

            logger.info(
                f"{operation} started",
                component=component,
                operation=operation,
                correlation_id=correlation_id,
                function=func.__name__,
            )

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"{operation} completed",
                    component=component,
                    operation=operation,
                    correlation_id=correlation_id,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="success",
                )
                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"{operation} failed: {str(e)}",
                    component=component,
                    operation=operation,
                    correlation_id=correlation_id,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
