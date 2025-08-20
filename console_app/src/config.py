"""
Simple console app configuration.

This module handles ONLY UI/presentation configuration.
All backend configuration is managed by the loan_processing module.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


@dataclass
class ConsoleAppConfig:
    """Console application UI configuration - presentation layer only."""

    # UI Display Settings
    debug: bool = False
    show_detailed_output: bool = True
    auto_save_results: bool = True
    results_dir: str = "results"

    # Console App Behavior
    default_pattern: str = "sequential"
    enable_pattern_comparison: bool = True

    # Display Preferences
    show_banner: bool = True
    show_prerequisites: bool = True

    @classmethod
    def from_env(cls) -> "ConsoleAppConfig":
        """Load configuration from environment variables."""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            show_detailed_output=os.getenv("SHOW_DETAILED_OUTPUT", "true").lower() == "true",
            auto_save_results=os.getenv("AUTO_SAVE_RESULTS", "true").lower() == "true",
            results_dir=os.getenv("RESULTS_DIR", "results"),
            default_pattern=os.getenv("DEFAULT_PATTERN", "sequential"),
            enable_pattern_comparison=os.getenv("ENABLE_PATTERN_COMPARISON", "true").lower() == "true",
            show_banner=os.getenv("SHOW_BANNER", "true").lower() == "true",
            show_prerequisites=os.getenv("SHOW_PREREQUISITES", "true").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate console app configuration."""
        errors = []

        # Validate results directory can be created
        try:
            Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create results directory '{self.results_dir}': {e}")

        # Validate pattern name
        if not self.default_pattern:
            errors.append("Default pattern cannot be empty")

        return errors


def get_console_config() -> ConsoleAppConfig:
    """Get console app configuration."""
    return ConsoleAppConfig.from_env()
