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

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Disable OpenAI agents tracing to prevent telemetry errors
import os  # noqa: E402

os.environ.setdefault("OPENAI_AGENTS_TRACE", "false")
os.environ.setdefault("OPENAI_TRACE", "false")

# Add project root to path for loan_processing imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import backend modules
from loan_processing.agents.providers.openai.orchestration.engine import (  # noqa: E402
    ProcessingEngine,
)
from loan_processing.models.application import LoanApplication  # noqa: E402
from loan_processing.models.decision import LoanDecision  # noqa: E402
from loan_processing.utils import get_logger, log_execution  # noqa: E402

# Initialize logging
logger = get_logger(__name__)


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

        logger.info("Backend client created", component="backend_client")

    @log_execution(component="backend_client", operation="initialize")
    async def initialize(self) -> None:
        """Initialize the backend connection."""
        logger.info("Initializing backend connection", component="backend_client")

        try:
            # Backend handles all its own configuration from environment variables
            # Console app doesn't need to manage this
            self._processing_engine = ProcessingEngine.create_configured()

            logger.info("Backend processing engine initialized successfully", component="backend_client")

        except Exception as e:
            logger.error(
                "Failed to initialize backend connection",
                error_message=str(e),
                error_type=type(e).__name__,
                component="backend_client",
            )
            raise

    def get_available_patterns(self) -> list[dict[str, Any]]:
        """
        Get available orchestration patterns from backend.

        Returns:
            List of pattern information dictionaries
        """
        # Only show sequential pattern until others are fully implemented
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

    @log_execution(component="backend_client", operation="process_application")
    async def process_application(
        self, application: LoanApplication, pattern_id: str, progress_callback=None
    ) -> LoanDecision:
        """
        Process a loan application using the specified pattern.

        Args:
            application: The loan application to process
            pattern_id: Orchestration pattern to use
            progress_callback: Optional callback function for progress updates

        Returns:
            Loan decision from the backend

        Raises:
            ValueError: If pattern_id is invalid
            Exception: For processing errors
        """
        logger.info(
            "Processing loan application",
            application_id=application.application_id,
            pattern_id=pattern_id,
            component="backend_client",
        )

        if not self._processing_engine:
            logger.error("Backend client not initialized", component="backend_client")
            raise RuntimeError("Backend client not initialized. Call initialize() first.")

        # Validate pattern exists
        if not self.get_pattern_by_id(pattern_id):
            logger.error("Unknown orchestration pattern", pattern_id=pattern_id, component="backend_client")
            raise ValueError(f"Unknown pattern: {pattern_id}")

        try:
            logger.info(
                "Executing orchestration pattern",
                pattern_id=pattern_id,
                application_id=application.application_id,
                component="backend_client",
            )

            # Backend processing engine handles all the complexity
            # Console app just needs to pass the application and pattern
            decision = await self._processing_engine.execute_pattern(
                pattern_name=pattern_id,
                application=application,
                model=None,  # Backend will use its configured model from SystemConfig
                progress_callback=progress_callback,
            )

            logger.info(
                "Application processing completed",
                application_id=application.application_id,
                pattern_id=pattern_id,
                decision_status=decision.decision.value,
                confidence_score=decision.confidence_score,
                component="backend_client",
            )

            return decision

        except Exception as e:
            logger.error(
                "Application processing failed",
                application_id=application.application_id,
                pattern_id=pattern_id,
                error_message=str(e),
                error_type=type(e).__name__,
                component="backend_client",
            )
            raise

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
