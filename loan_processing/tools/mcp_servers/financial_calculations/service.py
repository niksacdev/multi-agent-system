"""
Financial Calculations Service Implementation.

Implements the FinancialCalculationsService interface with mock business logic.
This provides realistic demo data for the loan processing system.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import get_logger, log_execution  # noqa: E402

from loan_processing.tools.services.financial_calculations import FinancialCalculationsService

# Initialize logging
logger = get_logger(__name__)


class FinancialCalculationsServiceImpl(FinancialCalculationsService):
    """
    Mock implementation of financial calculations service.

    Provides realistic calculations with some randomization for demo purposes.
    In production, this would connect to actual financial calculation engines.
    """

    @log_execution(component="financial_service", operation="calculate_debt_to_income_ratio")
    async def calculate_debt_to_income_ratio(
        self, monthly_income: float, monthly_debt_payments: float
    ) -> dict[str, Any]:
        """Calculate debt-to-income ratio with qualification assessment."""
        logger.info("Calculating debt-to-income ratio", 
                   component="financial_service")
        # Note: application_id correlation available via correlation_context from caller
        
        if monthly_income <= 0:
            logger.error("Invalid monthly income for DTI calculation", 
                        component="financial_service")
            return {"error": "Monthly income must be greater than zero", "type": "calculation_error"}

        dti_ratio = (monthly_debt_payments / monthly_income) * 100

        # Qualification thresholds (typical lending standards)
        if dti_ratio <= 36:
            qualification = "excellent"
            risk_level = "low"
        elif dti_ratio <= 43:
            qualification = "good"
            risk_level = "moderate"
        elif dti_ratio <= 50:
            qualification = "marginal"
            risk_level = "high"
        else:
            qualification = "poor"
            risk_level = "very_high"

        logger.info("DTI calculation completed", 
                   dti_ratio=round(dti_ratio, 2),
                   qualification=qualification,
                   risk_level=risk_level,
                   component="financial_service")

        return {
            "debt_to_income_ratio": round(dti_ratio, 2),
            "monthly_income": monthly_income,
            "monthly_debt_payments": monthly_debt_payments,
            "qualification_status": qualification,
            "risk_level": risk_level,
            "max_additional_debt": max(0, (monthly_income * 0.43) - monthly_debt_payments),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "dti_calculation",
        }

    @log_execution(component="financial_service", operation="calculate_loan_affordability")
    async def calculate_loan_affordability(
        self,
        monthly_income: float,
        existing_debt: float,
        loan_amount: float,
        interest_rate: float,
        loan_term_months: int,
    ) -> dict[str, Any]:
        """Calculate loan affordability with comprehensive assessment."""
        logger.info("Calculating loan affordability", 
                   component="financial_service")
        # Calculate monthly payment
        monthly_rate = interest_rate / 12
        if monthly_rate == 0:
            monthly_payment = loan_amount / loan_term_months
        else:
            monthly_payment = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** loan_term_months)
                / ((1 + monthly_rate) ** loan_term_months - 1)
            )

        # Calculate DTI with new loan
        total_debt = existing_debt + monthly_payment
        new_dti = (total_debt / monthly_income) * 100

        # Affordability assessment
        if new_dti <= 36:
            affordability = "highly_affordable"
            approval_probability = random.uniform(0.85, 0.95)
        elif new_dti <= 43:
            affordability = "affordable"
            approval_probability = random.uniform(0.70, 0.85)
        elif new_dti <= 50:
            affordability = "marginal"
            approval_probability = random.uniform(0.40, 0.70)
        else:
            affordability = "unaffordable"
            approval_probability = random.uniform(0.10, 0.40)

        logger.info("Loan affordability calculation completed", 
                   affordability_status=affordability,
                   approval_probability=round(approval_probability, 3),
                   new_dti=round(new_dti, 2),
                   monthly_payment=round(monthly_payment, 2),
                   component="financial_service")

        return {
            "loan_amount": loan_amount,
            "monthly_payment": round(monthly_payment, 2),
            "total_monthly_debt": round(total_debt, 2),
            "debt_to_income_ratio": round(new_dti, 2),
            "affordability_status": affordability,
            "approval_probability": round(approval_probability, 3),
            "total_interest": round((monthly_payment * loan_term_months) - loan_amount, 2),
            "payment_to_income_ratio": round((monthly_payment / monthly_income) * 100, 2),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "affordability_assessment",
        }

    @log_execution(component="financial_service", operation="calculate_monthly_payment")
    async def calculate_monthly_payment(
        self,
        loan_amount: float,
        interest_rate: float,
        loan_term_months: int,
        payment_type: str = "principal_and_interest",
    ) -> dict[str, Any]:
        """Calculate monthly loan payment using standard formula."""
        logger.info("Calculating monthly payment", 
                   component="financial_service")
        monthly_rate = interest_rate / 12

        if monthly_rate == 0:
            monthly_payment = loan_amount / loan_term_months
        else:
            monthly_payment = (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** loan_term_months)
                / ((1 + monthly_rate) ** loan_term_months - 1)
            )

        total_payment = monthly_payment * loan_term_months
        total_interest = total_payment - loan_amount

        return {
            "loan_amount": loan_amount,
            "annual_interest_rate": interest_rate,
            "term_months": loan_term_months,
            "payment_type": payment_type,
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "interest_percentage": round((total_interest / loan_amount) * 100, 2),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "payment_calculation",
        }

    async def calculate_credit_utilization_ratio(
        self, total_credit_used: float, total_credit_available: float
    ) -> dict[str, Any]:
        """Calculate credit utilization ratio with recommendations."""
        if total_credit_available <= 0:
            return {"error": "Total credit available must be greater than zero", "type": "calculation_error"}

        utilization_ratio = (total_credit_used / total_credit_available) * 100

        # Credit scoring impact
        if utilization_ratio <= 10:
            impact = "excellent"
            recommendation = "Optimal utilization for credit score"
        elif utilization_ratio <= 30:
            impact = "good"
            recommendation = "Good utilization, consider keeping below 10%"
        elif utilization_ratio <= 50:
            impact = "fair"
            recommendation = "Consider paying down balance to improve score"
        else:
            impact = "poor"
            recommendation = "High utilization negatively impacts credit score"

        return {
            "total_credit_used": total_credit_used,
            "total_credit_available": total_credit_available,
            "utilization_ratio": round(utilization_ratio, 2),
            "available_credit": total_credit_available - total_credit_used,
            "credit_impact": impact,
            "recommendation": recommendation,
            "optimal_balance": round(total_credit_available * 0.10, 2),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "utilization_calculation",
        }

    async def calculate_total_debt_service_ratio(
        self,
        monthly_income: float,
        total_monthly_debt: float,
        property_taxes: float = 0,
        insurance: float = 0,
        hoa_fees: float = 0,
    ) -> dict[str, Any]:
        """Calculate total debt service ratio including housing expenses."""
        total_housing_expenses = property_taxes + insurance + hoa_fees
        total_debt_payments = total_monthly_debt + total_housing_expenses
        tdsr = (total_debt_payments / monthly_income) * 100

        # TDSR thresholds (Canadian standards)
        if tdsr <= 42:
            qualification = "qualified"
            risk_assessment = "low_risk"
        elif tdsr <= 44:
            qualification = "marginal"
            risk_assessment = "moderate_risk"
        else:
            qualification = "unqualified"
            risk_assessment = "high_risk"

        return {
            "monthly_income": monthly_income,
            "total_monthly_debt": total_monthly_debt,
            "property_taxes": property_taxes,
            "insurance": insurance,
            "hoa_fees": hoa_fees,
            "total_housing_expenses": total_housing_expenses,
            "total_debt_payments": total_debt_payments,
            "total_debt_service_ratio": round(tdsr, 2),
            "qualification_status": qualification,
            "risk_assessment": risk_assessment,
            "maximum_additional_payment": max(0, (monthly_income * 0.42) - total_debt_payments),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "tdsr_calculation",
        }

    async def analyze_income_stability(
        self, income_history: list[dict[str, Any]], employment_history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze income stability and consistency over time."""
        if not income_history:
            return {"error": "Income history is required for stability analysis", "type": "analysis_error"}

        # Extract income values
        incomes = [item.get("amount", 0) for item in income_history]

        # Calculate basic statistics
        avg_income = sum(incomes) / len(incomes)
        min_income = min(incomes)
        max_income = max(incomes)

        # Calculate coefficient of variation (stability measure)
        if avg_income > 0:
            variance = sum((x - avg_income) ** 2 for x in incomes) / len(incomes)
            std_dev = variance**0.5
            coefficient_of_variation = (std_dev / avg_income) * 100
        else:
            coefficient_of_variation = 100

        # Stability assessment
        if coefficient_of_variation <= 10:
            stability = "very_stable"
            risk_level = "low"
        elif coefficient_of_variation <= 20:
            stability = "stable"
            risk_level = "moderate"
        elif coefficient_of_variation <= 35:
            stability = "variable"
            risk_level = "high"
        else:
            stability = "unstable"
            risk_level = "very_high"

        # Employment stability
        employment_months = len(employment_history)
        if employment_months >= 24:
            employment_stability = "stable"
        elif employment_months >= 12:
            employment_stability = "adequate"
        else:
            employment_stability = "insufficient"

        return {
            "income_count": len(incomes),
            "average_income": round(avg_income, 2),
            "minimum_income": min_income,
            "maximum_income": max_income,
            "income_variance": round(coefficient_of_variation, 2),
            "stability_rating": stability,
            "income_risk_level": risk_level,
            "employment_months": employment_months,
            "employment_stability": employment_stability,
            "overall_score": random.uniform(0.3, 0.9),
            "calculation_timestamp": "2025-08-11T10:30:00Z",
            "type": "income_stability_analysis",
        }
