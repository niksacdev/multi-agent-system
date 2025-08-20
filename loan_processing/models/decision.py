"""
Loan decision models for final loan processing outcomes.

Independent models that represent the final decision state of loan applications.
These models are used by orchestration patterns and external systems.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class LoanDecisionStatus(str, Enum):
    """Final loan decision status."""

    APPROVED = "approved"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    MANUAL_REVIEW = "manual_review"
    PENDING = "pending"


class LoanDecision(BaseModel):
    """
    Final loan decision with structured reasoning.

    This model represents the final outcome of the loan processing workflow
    and contains all necessary information for downstream systems.
    """

    application_id: str = Field(description="Reference to loan application", pattern=r"^LN\d{10}$")

    # Decision details
    decision: LoanDecisionStatus = Field(description="Final loan decision")

    decision_reason: str = Field(description="Primary reason for the decision")

    confidence_score: float = Field(description="Confidence in the decision", ge=0.0, le=1.0)

    # Approved loan terms (if applicable)
    approved_amount: Decimal | None = Field(
        None, description="Approved loan amount (may differ from requested)", ge=0, max_digits=10, decimal_places=2
    )

    approved_rate: float | None = Field(None, description="Approved interest rate", ge=0.0, le=1.0)

    approved_term_months: int | None = Field(None, description="Approved loan term in months", gt=0, le=360)

    # Conditions and requirements
    conditions: list[str] = Field(default_factory=list, description="Conditions that must be met for approval")

    required_documents: list[str] = Field(default_factory=list, description="Additional documents required")

    # Decision metadata
    decision_date: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")

    decision_maker: str = Field(description="Agent or system that made the final decision")

    review_required: bool = Field(default=False, description="Whether human review is required")

    review_priority: str | None = Field(
        None, description="Priority level for manual review (low, medium, high, urgent)"
    )

    # Audit trail
    reasoning: str = Field(description="Detailed reasoning for the decision")

    risk_factors: list[str] = Field(default_factory=list, description="Key risk factors considered")

    mitigating_factors: list[str] = Field(default_factory=list, description="Factors that mitigate risk")

    # Processing information
    processing_duration_seconds: float | None = Field(None, description="Total processing time", ge=0.0)

    agents_consulted: list[str] = Field(default_factory=list, description="Agents involved in the decision process")

    orchestration_pattern: str | None = Field(None, description="Orchestration pattern used for processing")

    @property
    def is_approved(self) -> bool:
        """Check if loan is approved."""
        return self.decision in [LoanDecisionStatus.APPROVED, LoanDecisionStatus.CONDITIONAL]

    @property
    def requires_action(self) -> bool:
        """Check if decision requires further action."""
        return self.decision in [
            LoanDecisionStatus.CONDITIONAL,
            LoanDecisionStatus.MANUAL_REVIEW,
            LoanDecisionStatus.PENDING,
        ]

    def add_condition(self, condition: str) -> None:
        """Add a condition to the approval."""
        if condition not in self.conditions:
            self.conditions.append(condition)

    def add_required_document(self, document: str) -> None:
        """Add a required document."""
        if document not in self.required_documents:
            self.required_documents.append(document)


class DecisionAuditLog(BaseModel):
    """
    Audit log entry for decision tracking and compliance.

    Provides detailed audit trail for regulatory compliance and
    decision transparency.
    """

    application_id: str = Field(description="Reference to loan application", pattern=r"^LN\d{10}$")

    event_type: str = Field(description="Type of audit event (assessment, decision, review)")

    event_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")

    event_description: str = Field(description="Description of the event")

    actor: str = Field(description="Agent or user responsible for the event")

    data_changed: dict = Field(default_factory=dict, description="Data that was changed during the event")

    compliance_notes: str | None = Field(None, description="Compliance-related notes")


__all__ = [
    "LoanDecisionStatus",
    "LoanDecision",
    "DecisionAuditLog",
]
