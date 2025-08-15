"""
Independent data models for loan processing.

This package contains all data models used throughout the loan processing system.
Models are designed to be independent and reusable across different agents,
services, and orchestration patterns.

Architecture:
- application.py: Core loan application data models
- assessment.py: Assessment result models for loan processing 
- decision.py: Final loan decision and audit models

All models follow enterprise-grade validation patterns and are designed
for extensibility and maintainability.
"""

from .application import (
    EmploymentStatus,
    LoanPurpose,
    LoanApplication,
)

from .assessment import (
    AssessmentStatus,
    RiskLevel,
    BaseAssessment,
    CreditAssessment,
    IncomeVerification,
    RiskAssessment,
    ComprehensiveAssessment,
)

from .decision import (
    LoanDecisionStatus,
    LoanDecision,
    DecisionAuditLog,
)

__all__ = [
    # Application models
    "EmploymentStatus",
    "LoanPurpose", 
    "LoanApplication",
    
    # Assessment models
    "AssessmentStatus",
    "RiskLevel",
    "BaseAssessment",
    "CreditAssessment",
    "IncomeVerification",
    "RiskAssessment",
    "ComprehensiveAssessment",
    
    # Decision models
    "LoanDecisionStatus",
    "LoanDecision",
    "DecisionAuditLog",
]
