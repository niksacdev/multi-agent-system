"""
Assessment result models for loan processing.

Independent models that represent the output of different assessment agents.
These models can be used by any orchestration pattern or downstream service.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AssessmentStatus(str, Enum):
    """Status of an assessment."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class BaseAssessment(BaseModel):
    """Base class for all assessment results."""

    application_id: str = Field(description="Reference to loan application", pattern=r"^LN\d{10}$")

    assessment_type: str = Field(description="Type of assessment performed")

    status: AssessmentStatus = Field(description="Assessment status")

    confidence_score: float = Field(description="Confidence in assessment results", ge=0.0, le=1.0)

    assessed_at: datetime = Field(default_factory=datetime.utcnow, description="Assessment completion timestamp")

    assessed_by: str = Field(description="Agent or system that performed assessment")

    notes: str | None = Field(None, description="Additional notes or explanations")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional assessment metadata")


class CreditAssessment(BaseAssessment):
    """Credit assessment results from credit evaluation agent."""

    assessment_type: Literal["credit"] = Field(default="credit")

    # Credit score information
    credit_score: int = Field(description="Verified credit score", ge=300, le=850)

    credit_bureau: str = Field(description="Source credit bureau (Experian, Equifax, TransUnion)")

    # Credit history details
    payment_history_score: float = Field(description="Payment history assessment score", ge=0.0, le=1.0)

    credit_utilization: float = Field(description="Credit utilization ratio", ge=0.0, le=1.0)

    credit_age_months: int = Field(description="Average age of credit accounts in months", ge=0)

    recent_inquiries: int = Field(description="Hard credit inquiries in last 6 months", ge=0)

    delinquencies: int = Field(description="Number of delinquent accounts", ge=0)

    bankruptcies: int = Field(description="Number of bankruptcies on record", ge=0)

    # Assessment results
    risk_level: RiskLevel = Field(description="Assessed credit risk level")

    recommendation: str = Field(description="Credit assessment recommendation")

    red_flags: list[str] = Field(default_factory=list, description="Identified credit risk factors")


class IncomeVerification(BaseAssessment):
    """Income verification results from income verification agent."""

    assessment_type: Literal["income"] = Field(default="income")

    # Income verification
    stated_income: Decimal = Field(description="Income stated by applicant", ge=0, max_digits=10, decimal_places=2)

    verified_income: Decimal = Field(description="Verified income amount", ge=0, max_digits=10, decimal_places=2)

    verification_method: str = Field(description="Method used for verification (paystub, tax_return, employer_contact)")

    verification_source: str = Field(description="Source of verification data")

    # Employment verification
    employment_verified: bool = Field(description="Whether employment was successfully verified")

    employer_contact_verified: bool = Field(description="Whether employer contact information was verified")

    employment_start_date: datetime | None = Field(None, description="Employment start date if verified")

    # Income analysis
    income_stability_score: float = Field(description="Income stability assessment score", ge=0.0, le=1.0)

    income_trend: str = Field(description="Income trend analysis (increasing, stable, declining)")

    # Discrepancy analysis
    discrepancy_amount: Decimal = Field(
        description="Absolute difference between stated and verified income", ge=0, max_digits=10, decimal_places=2
    )

    discrepancy_percentage: float = Field(description="Percentage discrepancy in income", ge=0.0)

    verification_issues: list[str] = Field(default_factory=list, description="Issues encountered during verification")


class RiskAssessment(BaseAssessment):
    """Risk assessment results from risk evaluation agent."""

    assessment_type: Literal["risk"] = Field(default="risk")

    # Overall risk scoring
    overall_risk_score: float = Field(description="Overall risk score", ge=0.0, le=1.0)

    risk_level: RiskLevel = Field(description="Categorized risk level")

    # Risk component scores
    credit_risk_score: float = Field(description="Credit-related risk component", ge=0.0, le=1.0)

    income_risk_score: float = Field(description="Income-related risk component", ge=0.0, le=1.0)

    employment_risk_score: float = Field(description="Employment-related risk component", ge=0.0, le=1.0)

    debt_risk_score: float = Field(description="Debt-related risk component", ge=0.0, le=1.0)

    loan_specific_risk_score: float = Field(description="Loan-specific risk factors", ge=0.0, le=1.0)

    # Risk factors
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")

    mitigating_factors: list[str] = Field(default_factory=list, description="Risk mitigating factors")

    # Recommendations
    approval_recommendation: bool = Field(description="Whether to approve the loan")

    recommended_amount: Decimal | None = Field(
        None, description="Recommended loan amount if different from requested", ge=0, max_digits=10, decimal_places=2
    )

    recommended_rate: float | None = Field(None, description="Recommended interest rate", ge=0.0, le=1.0)

    required_conditions: list[str] = Field(default_factory=list, description="Required conditions for approval")


class ComprehensiveAssessment(BaseModel):
    """
    Comprehensive assessment combining results from all agents.

    This model aggregates all individual assessments and provides
    the final assessment state for decision making.
    """

    application_id: str = Field(description="Reference to loan application", pattern=r"^LN\d{10}$")

    # Individual assessment results
    credit_assessment: CreditAssessment | None = Field(None, description="Credit assessment results")

    income_verification: IncomeVerification | None = Field(None, description="Income verification results")

    risk_assessment: RiskAssessment | None = Field(None, description="Risk assessment results")

    # Overall assessment metadata
    assessment_completed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Assessment completion timestamp"
    )

    processing_time_seconds: float | None = Field(None, description="Total processing time in seconds")

    agents_involved: list[str] = Field(
        default_factory=list, description="List of agents that participated in assessment"
    )

    # Overall assessment status
    overall_status: AssessmentStatus = Field(description="Overall assessment status")

    overall_confidence: float | None = Field(
        None, description="Overall confidence score across all assessments", ge=0.0, le=1.0
    )


__all__ = [
    "AssessmentStatus",
    "RiskLevel",
    "BaseAssessment",
    "CreditAssessment",
    "IncomeVerification",
    "RiskAssessment",
    "ComprehensiveAssessment",
]
