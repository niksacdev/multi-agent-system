"""
Agent implementations for multi-provider loan processing system.

This module contains provider-specific agent implementations and shared
agent assets that can be used across different frameworks.
"""

# Available agent providers
AVAILABLE_PROVIDERS = ["openai"]

# Future providers will be added here:
# AVAILABLE_PROVIDERS = ["openai", "semantic_kernel", "autogen"]

__all__ = ["AVAILABLE_PROVIDERS"]
