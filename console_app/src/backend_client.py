"""
Backend client for console app.

This module provides a clean interface between the console app (presentation layer)
and the loan_processing module (business logic layer).

The console app doesn't need to know about provider configuration, orchestration
patterns, or other backend concerns - it just needs to send applications and
receive decisions.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path for loan_processing imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import backend modules
from loan_processing.agents.providers.openai.orchestration.engine import (  # noqa: E402
    ProcessingEngine,
)
from loan_processing.models.application import LoanApplication  # noqa: E402
from loan_processing.models.decision import LoanDecision  # noqa: E402


class LoanProcessingBackendClient:
    """
    Clean interface to the loan processing backend.

    This class encapsulates all backend interactions and hides implementation
    details from the console app. The console app only needs to know about
    applications and decisions.
    """

    def __init__(self):
        """Initialize backend client."""
        self._processing_engine = None

    async def initialize(self) -> None:
        """Initialize the backend connection."""
        # Backend handles all its own configuration from environment variables
        # Console app doesn't need to manage this
        self._processing_engine = ProcessingEngine.create_configured()

    def get_available_patterns(self) -> list[dict[str, Any]]:
        """
        Get available orchestration patterns from backend.

        Returns:
            List of pattern information dictionaries
        """
        # This could be made dynamic by querying the backend
        # For now, return the known patterns
        return [
            {
                "id": "sequential",
                "name": "Sequential Processing",
                "description": "Process agents in sequence: Intake → Credit → Income → Risk",
                "available": True,
                "workflow": [
                    "1. Intake Agent validates and enriches application",
                    "2. Credit Agent assesses creditworthiness",
                    "3. Income Agent verifies employment and income",
                    "4. Risk Agent makes final decision",
                ],
            },
            {
                "id": "parallel",
                "name": "Parallel Processing",
                "description": "Run Credit and Income agents in parallel for faster processing",
                "available": True,
                "workflow": [
                    "1. Intake Agent validates and enriches application",
                    "2. Credit & Income Agents run in parallel",
                    "3. Risk Agent synthesizes results and decides",
                ],
            },
            {
                "id": "adaptive",
                "name": "Adaptive Processing",
                "description": "Dynamically adjust workflow based on application complexity",
                "available": True,
                "workflow": [
                    "1. Intake Agent analyzes complexity",
                    "2. Dynamic agent selection based on risk profile",
                    "3. Optimized processing path",
                ],
            },
        ]

    def get_pattern_by_id(self, pattern_id: str) -> dict[str, Any] | None:
        """
        Get pattern information by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern information or None if not found
        """
        patterns = self.get_available_patterns()
        for pattern in patterns:
            if pattern["id"] == pattern_id:
                return pattern
        return None

    async def process_application(self, application: LoanApplication, pattern_id: str) -> LoanDecision:
        """
        Process a loan application using the specified pattern.

        Args:
            application: The loan application to process
            pattern_id: Orchestration pattern to use

        Returns:
            Loan decision from the backend

        Raises:
            ValueError: If pattern_id is invalid
            Exception: For processing errors
        """
        if not self._processing_engine:
            raise RuntimeError("Backend client not initialized. Call initialize() first.")

        # Validate pattern exists
        if not self.get_pattern_by_id(pattern_id):
            raise ValueError(f"Unknown pattern: {pattern_id}")

        # Backend processing engine handles all the complexity
        # Console app just needs to pass the application and pattern
        decision = await self._processing_engine.execute_pattern(
            pattern_name=pattern_id,
            application=application,
            model=None,  # Backend will use its configured model from SystemConfig
        )

        return decision

    def get_backend_status(self) -> dict[str, Any]:
        """
        Get backend system status for health checks.

        Returns:
            Status information dictionary
        """
        # Could be enhanced to actually check data service connectivity
        return {
            "backend_initialized": self._processing_engine is not None,
            "required_services": [
                "Application Verification Data Service (port 8010)",
                "Document Processing Data Service (port 8011)",
                "Financial Calculations Data Service (port 8012)",
            ],
            "note": "Data services must be started manually",
        }


# Global backend client instance
_backend_client = None


def get_backend_client() -> LoanProcessingBackendClient:
    """Get the global backend client instance."""
    global _backend_client
    if _backend_client is None:
        _backend_client = LoanProcessingBackendClient()
    return _backend_client
