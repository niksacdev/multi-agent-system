"""
Multi-Provider Loan Processing System.

This module provides a provider-agnostic entry point for the loan processing system,
supporting multiple agent frameworks through clear repository separation.
"""

from __future__ import annotations

from typing import Optional

from loan_processing.agents.shared.models.application import LoanApplication
from loan_processing.agents.shared.models.decision import LoanDecision


class LoanProcessingSystem:
    """Main entry point for the loan processing system with multi-provider support."""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize the loan processing system with specified provider.
        
        Args:
            provider: Provider name (e.g., "openai", "semantic_kernel", "autogen")
        """
        self.provider = provider
        self.engine = self._create_engine(provider)
    
    def _create_engine(self, provider: str):
        """Create provider-specific orchestration engine."""
        if provider == "openai":
            from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine
            return OrchestrationEngine()
        elif provider == "semantic_kernel":
            # Future implementation
            raise NotImplementedError("Semantic Kernel provider not yet implemented")
        elif provider == "autogen":
            # Future implementation
            raise NotImplementedError("AutoGen provider not yet implemented")
        else:
            available_providers = ["openai", "semantic_kernel", "autogen"]
            raise ValueError(f"Unknown provider: {provider}. Available: {available_providers}")
    
    async def process_application(
        self, 
        application: LoanApplication, 
        pattern: str = "sequential",
        model: Optional[str] = None
    ) -> LoanDecision:
        """
        Process a loan application using the configured provider.
        
        Args:
            application: Loan application to process
            pattern: Orchestration pattern to use (e.g., "sequential", "parallel")
            model: Optional model override for this processing
            
        Returns:
            Loan decision result
        """
        return await self.engine.execute_pattern(pattern, application, model)
    
    def get_available_patterns(self) -> list[str]:
        """Get list of available orchestration patterns for this provider."""
        # This could be enhanced to dynamically discover patterns
        return ["sequential", "parallel"]
    
    def get_provider_info(self) -> dict[str, str]:
        """Get information about the current provider."""
        return {
            "name": self.provider,
            "engine_type": type(self.engine).__name__,
            "module": type(self.engine).__module__
        }


# Provider-specific factory functions for backwards compatibility
def create_openai_system() -> LoanProcessingSystem:
    """Create a loan processing system using OpenAI provider."""
    return LoanProcessingSystem(provider="openai")


def create_semantic_kernel_system() -> LoanProcessingSystem:
    """Create a loan processing system using Semantic Kernel provider."""
    return LoanProcessingSystem(provider="semantic_kernel")


def create_autogen_system() -> LoanProcessingSystem:
    """Create a loan processing system using AutoGen provider."""
    return LoanProcessingSystem(provider="autogen")


__all__ = [
    "LoanProcessingSystem",
    "create_openai_system", 
    "create_semantic_kernel_system",
    "create_autogen_system",
    "LoanApplication",
    "LoanDecision"
]