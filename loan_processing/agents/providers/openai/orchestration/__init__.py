"""
OpenAI-specific orchestration implementation.

This module contains the orchestration engine and pattern executors
optimized for OpenAI Agents SDK.
"""

from .base import AgentExecutionService, HandoffValidationService, PatternExecutor
from .engine import OrchestrationContext, OrchestrationEngine
from .sequential import SequentialPatternExecutor

# ParallelPatternExecutor available but not exported until fully implemented
# from .parallel import ParallelPatternExecutor

__all__ = [
    "OrchestrationEngine",
    "OrchestrationContext",
    "SequentialPatternExecutor",
    "PatternExecutor",
    "AgentExecutionService",
    "HandoffValidationService",
]
