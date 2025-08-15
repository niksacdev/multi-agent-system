"""
OpenAI-specific orchestration implementation.

This module contains the orchestration engine and pattern executors
optimized for OpenAI Agents SDK.
"""

from .engine import OrchestrationEngine, OrchestrationContext
from .sequential import SequentialPatternExecutor
from .parallel import ParallelPatternExecutor
from .base import PatternExecutor, AgentExecutionService, HandoffValidationService

__all__ = [
    "OrchestrationEngine", 
    "OrchestrationContext",
    "SequentialPatternExecutor",
    "ParallelPatternExecutor",
    "PatternExecutor",
    "AgentExecutionService", 
    "HandoffValidationService"
]