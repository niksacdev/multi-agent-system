"""
Loan application data models.

Independent data models that can be used by any agent or service.
Following the sample-specific quality standards from Copilot instructions.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EmploymentStatus(str, Enum):
    """Employment status options."""
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"  
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class LoanPurpose(str, Enum):
    """Loan purpose categories."""
    HOME_PURCHASE = "home_purchase"
    HOME_REFINANCE = "home_refinance"
    AUTO = "auto"
    PERSONAL = "personal"
    BUSINESS = "business"
    EDUCATION = "education"
    DEBT_CONSOLIDATION = "debt_consolidation"


class LoanApplication(BaseModel):
    """
    Core loan application model with comprehensive validation.
    
    This model represents the initial loan application data and is immutable
    once created. All agents and services use this as the primary data source.
    """
    
    # Application identification
    application_id: str = Field(
        description="Unique application identifier",
        pattern=r"^LN\d{10}$"  # Format: LN1234567890
    )
    
    # Applicant information
    applicant_name: str = Field(
        description="Full name of the applicant",
        min_length=2,
        max_length=100
    )
    
    ssn: str = Field(
        description="Social Security Number", 
        pattern=r"^\d{3}-\d{2}-\d{4}$"  # Format: XXX-XX-XXXX
    )
    
    email: str = Field(
        description="Contact email address",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    phone: str = Field(
        description="Contact phone number",
        pattern=r"^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$"  # US phone format
    )
    
    date_of_birth: datetime = Field(
        description="Date of birth for age verification"
    )
    
    # Loan details
    loan_amount: Decimal = Field(
        description="Requested loan amount in USD",
        gt=0,
        max_digits=10,
        decimal_places=2
    )
    
    loan_purpose: LoanPurpose = Field(
        description="Purpose of the loan"
    )
    
    loan_term_months: int = Field(
        description="Loan term in months",
        gt=0,
        le=360  # Maximum 30 years
    )
    
    # Financial information
    annual_income: Decimal = Field(
        description="Annual income in USD",
        ge=0,
        max_digits=10,
        decimal_places=2
    )
    
    employment_status: EmploymentStatus = Field(
        description="Current employment status"
    )
    
    employer_name: str | None = Field(
        None,
        description="Name of current employer",
        max_length=100
    )
    
    months_employed: int | None = Field(
        None,
        description="Months at current job",
        ge=0
    )
    
    # Optional financial details
    monthly_expenses: Decimal | None = Field(
        None,
        description="Monthly expenses in USD",
        ge=0,
        max_digits=8,
        decimal_places=2
    )
    
    existing_debt: Decimal | None = Field(
        None,
        description="Total existing debt in USD", 
        ge=0,
        max_digits=10,
        decimal_places=2
    )
    
    assets: Decimal | None = Field(
        None,
        description="Total assets in USD",
        ge=0,
        max_digits=12,
        decimal_places=2
    )
    
    down_payment: Decimal | None = Field(
        None,
        description="Down payment amount in USD",
        ge=0,
        max_digits=10,
        decimal_places=2
    )
    
    # System fields
    submitted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Application submission timestamp"
    )
    
    # Extensible data for additional requirements
    additional_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional application data for custom requirements"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        
    def __hash__(self) -> int:
        """Make application hashable for caching."""
        return hash(self.application_id)
    
    @property
    def debt_to_income_ratio(self) -> float | None:
        """Calculate debt-to-income ratio if data available."""
        if self.existing_debt is None or self.annual_income <= 0:
            return None
        monthly_income = self.annual_income / 12
        return float(self.existing_debt / monthly_income)
    
    @property
    def loan_to_income_ratio(self) -> float:
        """Calculate loan-to-income ratio."""
        if self.annual_income <= 0:
            return float('inf')
        return float(self.loan_amount / self.annual_income)
    
    def add_custom_field(self, field_name: str, value: Any) -> None:
        """Add custom field to additional_data."""
        self.additional_data[field_name] = value
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get custom field from additional_data."""
        return self.additional_data.get(field_name, default)


__all__ = [
    "EmploymentStatus",
    "LoanPurpose", 
    "LoanApplication",
]
