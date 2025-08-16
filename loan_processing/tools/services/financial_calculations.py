"""
Financial calculations service interface.

Defines business capabilities for performing mathematical calculations
and financial analysis required for loan processing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class FinancialCalculationsService(ABC):
    """
    Abstract service for financial calculations and analysis.

    This service handles all mathematical operations including:
    - Debt-to-income ratio calculations
    - Credit utilization analysis
    - Loan affordability assessments
    - Payment calculations
    - Income stability analysis
    - Asset-to-debt ratios

    Business Rules:
    - All calculations must use industry-standard formulas
    - Results must include confidence intervals where applicable
    - Calculations must be auditable and reproducible
    - Regulatory calculation requirements must be met
    """

    @abstractmethod
    async def calculate_debt_to_income_ratio(
        self, monthly_income: float, monthly_debt_payments: float
    ) -> dict[str, Any]:
        """
        Calculate debt-to-income ratio for loan qualification.

        Args:
            monthly_income: Total verified monthly income
            monthly_debt_payments: Total monthly debt obligations

        Returns:
            dict with DTI calculation results and interpretation

        Raises:
            CalculationError: If calculation cannot be performed
        """
        ...

    @abstractmethod
    async def calculate_credit_utilization_ratio(
        self, total_credit_used: float, total_credit_available: float
    ) -> dict[str, Any]:
        """
        Calculate credit utilization ratio.

        Args:
            total_credit_used: Current total credit balances
            total_credit_available: Total available credit limits

        Returns:
            dict with utilization ratio and impact assessment

        Raises:
            CalculationError: If calculation cannot be performed
        """
        ...

    @abstractmethod
    async def calculate_loan_affordability(
        self,
        monthly_income: float,
        existing_debt: float,
        loan_amount: float,
        interest_rate: float,
        loan_term_months: int,
    ) -> dict[str, Any]:
        """
        Calculate loan affordability based on income and existing debt.

        Args:
            monthly_income: Total monthly income
            existing_debt: Existing monthly debt payments
            loan_amount: Requested loan amount
            interest_rate: Annual interest rate (as decimal)
            loan_term_months: Loan term in months

        Returns:
            dict with affordability analysis and payment calculations

        Raises:
            CalculationError: If calculation cannot be performed
        """
        ...

    @abstractmethod
    async def calculate_monthly_payment(
        self,
        loan_amount: float,
        interest_rate: float,
        loan_term_months: int,
        payment_type: str = "principal_and_interest",
    ) -> dict[str, Any]:
        """
        Calculate monthly loan payment.

        Args:
            loan_amount: Principal loan amount
            interest_rate: Annual interest rate (as decimal)
            loan_term_months: Loan term in months
            payment_type: Type of payment calculation

        Returns:
            dict with payment breakdown and amortization details

        Raises:
            CalculationError: If calculation cannot be performed
        """
        ...

    @abstractmethod
    async def analyze_income_stability(
        self, income_history: list[dict[str, Any]], employment_history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Analyze income stability and consistency over time.

        Args:
            income_history: Historical income data
            employment_history: Employment history records

        Returns:
            dict with stability analysis and trend indicators

        Raises:
            AnalysisError: If analysis cannot be performed
        """
        ...

    @abstractmethod
    async def calculate_total_debt_service_ratio(
        self,
        monthly_income: float,
        total_monthly_debt: float,
        property_taxes: float = 0,
        insurance: float = 0,
        hoa_fees: float = 0,
    ) -> dict[str, Any]:
        """
        Calculate total debt service ratio including housing expenses.

        Args:
            monthly_income: Total monthly income
            total_monthly_debt: All monthly debt obligations
            property_taxes: Monthly property taxes
            insurance: Monthly insurance payments
            hoa_fees: Monthly HOA fees

        Returns:
            dict with comprehensive debt service analysis

        Raises:
            CalculationError: If calculation cannot be performed
        """
        ...
