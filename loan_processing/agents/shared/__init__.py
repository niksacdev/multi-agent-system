"""
Shared agent assets for multi-provider loan processing system.

This module contains domain-specific assets that are shared across
all agent provider implementations, including models, configurations,
and common utilities.
"""

# Re-export commonly used shared models for convenience
from loan_processing.agents.shared.models.application import LoanApplication
from loan_processing.agents.shared.models.assessment import RiskAssessment
from loan_processing.agents.shared.models.decision import LoanDecision, LoanDecisionStatus

__all__ = [
    "LoanApplication",
    "LoanDecision",
    "LoanDecisionStatus",
    "RiskAssessment"
]
