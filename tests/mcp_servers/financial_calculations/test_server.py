"""
Tests for Financial Calculations MCP Server.

This module tests the MCP server implementation for financial calculations,
including both the server tools and the service implementation.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from mcp_servers.financial_calculations.server import (
    calculate_credit_utilization_ratio,
    calculate_debt_to_income_ratio,
    calculate_loan_affordability,
    calculate_monthly_payment,
    calculate_total_debt_service_ratio,
    financial_service,
)
from mcp_servers.financial_calculations.service import FinancialCalculationsServiceImpl


class TestFinancialCalculationsServiceImpl:
    """Test the service implementation directly."""

    @pytest.fixture
    def service_impl(self) -> FinancialCalculationsServiceImpl:
        """Create service implementation for testing."""
        return FinancialCalculationsServiceImpl()

    @pytest.mark.asyncio
    async def test_calculate_debt_to_income_ratio_excellent(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test DTI calculation for excellent qualification."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=5000.0,
            monthly_debt_payments=1500.0
        )

        # DTI should be 30% (1500/5000 * 100)
        assert result["debt_to_income_ratio"] == 30.0
        assert result["monthly_income"] == 5000.0
        assert result["monthly_debt_payments"] == 1500.0
        assert result["qualification_status"] == "excellent"
        assert result["risk_level"] == "low"
        assert result["type"] == "dti_calculation"
        
        # Max additional debt should be 43% - current 30% = 13% of income
        expected_max_debt = (5000.0 * 0.43) - 1500.0
        assert result["max_additional_debt"] == expected_max_debt

    @pytest.mark.asyncio
    async def test_calculate_debt_to_income_ratio_good(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test DTI calculation for good qualification."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=5000.0,
            monthly_debt_payments=2000.0
        )

        # DTI should be 40% (2000/5000 * 100)
        assert result["debt_to_income_ratio"] == 40.0
        assert result["qualification_status"] == "good"
        assert result["risk_level"] == "moderate"

    @pytest.mark.asyncio
    async def test_calculate_debt_to_income_ratio_poor(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test DTI calculation for poor qualification."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=3000.0,
            monthly_debt_payments=2000.0
        )

        # DTI should be 66.67% (2000/3000 * 100)
        assert result["debt_to_income_ratio"] == 66.67
        assert result["qualification_status"] == "poor"
        assert result["risk_level"] == "very_high"

    @pytest.mark.asyncio
    async def test_calculate_debt_to_income_ratio_zero_income(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test DTI calculation with zero income."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=0.0,
            monthly_debt_payments=1000.0
        )

        assert "error" in result
        assert result["error"] == "Monthly income must be greater than zero"
        assert result["type"] == "calculation_error"

    @pytest.mark.asyncio
    async def test_calculate_loan_affordability_affordable(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test loan affordability calculation for affordable loan."""
        result = await service_impl.calculate_loan_affordability(
            monthly_income=6000.0,
            existing_debt=1000.0,
            loan_amount=200000.0,
            interest_rate=0.05,  # 5% annual
            loan_term_months=360  # 30 years
        )

        assert result["loan_amount"] == 200000.0
        assert result["monthly_payment"] > 0
        assert result["debt_to_income_ratio"] > 0
        assert result["affordability_status"] in ["highly_affordable", "affordable", "marginal", "unaffordable"]
        assert 0.0 <= result["approval_probability"] <= 1.0
        assert result["type"] == "affordability_assessment"

    @pytest.mark.asyncio
    async def test_calculate_monthly_payment_standard(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test standard monthly payment calculation."""
        result = await service_impl.calculate_monthly_payment(
            loan_amount=100000.0,
            interest_rate=0.06,  # 6% annual
            loan_term_months=360,  # 30 years
            payment_type="principal_and_interest"
        )

        assert result["loan_amount"] == 100000.0
        assert result["annual_interest_rate"] == 0.06
        assert result["term_months"] == 360
        assert result["payment_type"] == "principal_and_interest"
        assert result["monthly_payment"] > 0
        assert abs(result["total_payment"] - (result["monthly_payment"] * 360)) < 1.0  # Allow for larger rounding differences due to floating point
        assert result["total_interest"] == result["total_payment"] - 100000.0
        assert result["type"] == "payment_calculation"

    @pytest.mark.asyncio
    async def test_calculate_monthly_payment_zero_interest(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test monthly payment calculation with zero interest rate."""
        result = await service_impl.calculate_monthly_payment(
            loan_amount=120000.0,
            interest_rate=0.0,
            loan_term_months=120
        )

        # With 0% interest, payment should be loan_amount / term_months
        expected_payment = 120000.0 / 120
        assert result["monthly_payment"] == expected_payment
        assert result["total_interest"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_credit_utilization_ratio_excellent(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test credit utilization for excellent impact."""
        result = await service_impl.calculate_credit_utilization_ratio(
            total_credit_used=500.0,
            total_credit_available=10000.0
        )

        # Utilization should be 5% (500/10000 * 100)
        assert result["utilization_ratio"] == 5.0
        assert result["total_credit_used"] == 500.0
        assert result["total_credit_available"] == 10000.0
        assert result["available_credit"] == 9500.0
        assert result["credit_impact"] == "excellent"
        assert "Optimal utilization" in result["recommendation"]
        assert result["optimal_balance"] == 1000.0  # 10% of available credit
        assert result["type"] == "utilization_calculation"

    @pytest.mark.asyncio
    async def test_calculate_credit_utilization_ratio_poor(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test credit utilization for poor impact."""
        result = await service_impl.calculate_credit_utilization_ratio(
            total_credit_used=7500.0,
            total_credit_available=10000.0
        )

        # Utilization should be 75%
        assert result["utilization_ratio"] == 75.0
        assert result["credit_impact"] == "poor"
        assert "High utilization negatively impacts" in result["recommendation"]

    @pytest.mark.asyncio
    async def test_calculate_credit_utilization_ratio_zero_available(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test credit utilization with zero available credit."""
        result = await service_impl.calculate_credit_utilization_ratio(
            total_credit_used=1000.0,
            total_credit_available=0.0
        )

        assert "error" in result
        assert result["error"] == "Total credit available must be greater than zero"
        assert result["type"] == "calculation_error"

    @pytest.mark.asyncio
    async def test_calculate_total_debt_service_ratio_qualified(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test TDSR calculation for qualified status."""
        result = await service_impl.calculate_total_debt_service_ratio(
            monthly_income=8000.0,
            total_monthly_debt=2000.0,
            property_taxes=300.0,
            insurance=150.0,
            hoa_fees=100.0
        )

        # Total debt payments: 2000 + 300 + 150 + 100 = 2550
        # TDSR: 2550 / 8000 * 100 = 31.875%
        assert result["total_debt_payments"] == 2550.0
        assert abs(result["total_debt_service_ratio"] - 31.88) < 0.01  # Allow small rounding differences
        assert result["qualification_status"] == "qualified"
        assert result["risk_assessment"] == "low_risk"
        assert result["type"] == "tdsr_calculation"

    @pytest.mark.asyncio
    async def test_calculate_total_debt_service_ratio_unqualified(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test TDSR calculation for unqualified status."""
        result = await service_impl.calculate_total_debt_service_ratio(
            monthly_income=5000.0,
            total_monthly_debt=2500.0,
            property_taxes=200.0,
            insurance=100.0,
            hoa_fees=50.0
        )

        # Total debt payments: 2500 + 200 + 100 + 50 = 2850
        # TDSR: 2850 / 5000 * 100 = 57%
        assert result["total_debt_service_ratio"] == 57.0
        assert result["qualification_status"] == "unqualified"
        assert result["risk_assessment"] == "high_risk"

    @pytest.mark.asyncio
    async def test_analyze_income_stability_stable(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test income stability analysis for stable income."""
        income_history = [
            {"amount": 5000, "date": "2023-01"},
            {"amount": 5100, "date": "2023-02"},
            {"amount": 4950, "date": "2023-03"},
            {"amount": 5050, "date": "2023-04"}
        ]
        employment_history = [{"month": f"2023-{i:02d}"} for i in range(1, 25)]  # 24 months

        result = await service_impl.analyze_income_stability(income_history, employment_history)

        assert result["income_count"] == 4
        assert result["average_income"] > 0
        assert result["stability_rating"] in ["very_stable", "stable", "variable", "unstable"]
        assert result["employment_months"] == 24
        assert result["employment_stability"] == "stable"
        assert result["type"] == "income_stability_analysis"

    @pytest.mark.asyncio
    async def test_analyze_income_stability_no_history(
        self, service_impl: FinancialCalculationsServiceImpl
    ) -> None:
        """Test income stability analysis with no history."""
        result = await service_impl.analyze_income_stability([], [])

        assert "error" in result
        assert result["error"] == "Income history is required for stability analysis"
        assert result["type"] == "analysis_error"


class TestFinancialCalculationsMCPServer:
    """Test the MCP server tools."""

    @pytest.mark.asyncio
    async def test_calculate_debt_to_income_ratio_tool(self) -> None:
        """Test the MCP tool wrapper for DTI calculation."""
        result_str = await calculate_debt_to_income_ratio(
            monthly_income=5000.0,
            monthly_debt_payments=1500.0
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["debt_to_income_ratio"] == 30.0
        assert result["type"] == "dti_calculation"

    @pytest.mark.asyncio
    async def test_calculate_loan_affordability_tool(self) -> None:
        """Test the MCP tool wrapper for loan affordability."""
        result_str = await calculate_loan_affordability(
            monthly_income=6000.0,
            existing_debt=1000.0,
            loan_amount=200000.0,
            interest_rate=0.05,
            loan_term_months=360
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["loan_amount"] == 200000.0
        assert result["type"] == "affordability_assessment"

    @pytest.mark.asyncio
    async def test_calculate_monthly_payment_tool(self) -> None:
        """Test the MCP tool wrapper for monthly payment calculation."""
        result_str = await calculate_monthly_payment(
            loan_amount=100000.0,
            interest_rate=0.06,
            loan_term_months=360,
            payment_type="principal_and_interest"
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["loan_amount"] == 100000.0
        assert result["payment_type"] == "principal_and_interest"
        assert result["type"] == "payment_calculation"

    @pytest.mark.asyncio
    async def test_calculate_credit_utilization_ratio_tool(self) -> None:
        """Test the MCP tool wrapper for credit utilization."""
        result_str = await calculate_credit_utilization_ratio(
            total_credit_used=1000.0,
            total_credit_available=10000.0
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["utilization_ratio"] == 10.0
        assert result["type"] == "utilization_calculation"

    @pytest.mark.asyncio
    async def test_calculate_total_debt_service_ratio_tool(self) -> None:
        """Test the MCP tool wrapper for TDSR calculation."""
        result_str = await calculate_total_debt_service_ratio(
            monthly_income=8000.0,
            total_monthly_debt=2000.0,
            property_taxes=300.0,
            insurance=150.0,
            hoa_fees=100.0
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["total_debt_payments"] == 2550.0
        assert result["type"] == "tdsr_calculation"

    @pytest.mark.asyncio
    async def test_calculate_total_debt_service_ratio_tool_defaults(self) -> None:
        """Test TDSR tool with default housing expense values."""
        result_str = await calculate_total_debt_service_ratio(
            monthly_income=8000.0,
            total_monthly_debt=2000.0
        )

        # Verify result is valid JSON and defaults are applied
        result = json.loads(result_str)
        assert result["property_taxes"] == 0
        assert result["insurance"] == 0
        assert result["hoa_fees"] == 0
        assert result["total_housing_expenses"] == 0
        assert result["total_debt_payments"] == 2000.0


class TestFinancialCalculationsEdgeCases:
    """Test edge cases and mathematical precision."""

    @pytest.fixture
    def service_impl(self) -> FinancialCalculationsServiceImpl:
        """Create service implementation for testing."""
        return FinancialCalculationsServiceImpl()

    @pytest.mark.asyncio
    async def test_very_small_amounts(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test calculations with very small monetary amounts."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=1.0,
            monthly_debt_payments=0.01
        )

        assert result["debt_to_income_ratio"] == 1.0
        assert result["qualification_status"] == "excellent"

    @pytest.mark.asyncio
    async def test_very_large_amounts(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test calculations with very large monetary amounts."""
        result = await service_impl.calculate_monthly_payment(
            loan_amount=10000000.0,  # 10 million
            interest_rate=0.03,
            loan_term_months=360
        )

        assert result["monthly_payment"] > 0
        assert result["total_payment"] > result["loan_amount"]

    @pytest.mark.asyncio
    async def test_high_interest_rate(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test payment calculation with high interest rate."""
        result = await service_impl.calculate_monthly_payment(
            loan_amount=100000.0,
            interest_rate=0.25,  # 25% annual rate
            loan_term_months=120
        )

        # High interest should result in higher total interest
        assert result["total_interest"] > result["loan_amount"]
        assert result["interest_percentage"] > 100

    @pytest.mark.asyncio
    async def test_short_term_loan(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test payment calculation for short-term loan."""
        result = await service_impl.calculate_monthly_payment(
            loan_amount=50000.0,
            interest_rate=0.08,
            loan_term_months=12  # 1 year
        )

        # Short term should have higher monthly payment but lower total interest
        assert result["monthly_payment"] > 4000  # Approximately loan_amount / 12
        assert result["total_interest"] < result["loan_amount"] * 0.1

    @pytest.mark.asyncio
    async def test_exact_threshold_dti(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test DTI calculation at exact qualification thresholds."""
        # Test at 36% threshold (excellent/good boundary)
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=1000.0,
            monthly_debt_payments=360.0
        )
        assert result["debt_to_income_ratio"] == 36.0
        assert result["qualification_status"] == "excellent"

        # Test at 43% threshold (good/marginal boundary)
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=1000.0,
            monthly_debt_payments=430.0
        )
        assert result["debt_to_income_ratio"] == 43.0
        assert result["qualification_status"] == "good"

    @pytest.mark.asyncio
    async def test_utilization_thresholds(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test credit utilization at exact impact thresholds."""
        # Test at 10% threshold (excellent/good boundary)
        result = await service_impl.calculate_credit_utilization_ratio(
            total_credit_used=1000.0,
            total_credit_available=10000.0
        )
        assert result["utilization_ratio"] == 10.0
        assert result["credit_impact"] == "excellent"

        # Test at 30% threshold (good/fair boundary)
        result = await service_impl.calculate_credit_utilization_ratio(
            total_credit_used=3000.0,
            total_credit_available=10000.0
        )
        assert result["utilization_ratio"] == 30.0
        assert result["credit_impact"] == "good"

    @pytest.mark.asyncio
    async def test_negative_debt_payments(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test DTI calculation with negative debt payments."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=5000.0,
            monthly_debt_payments=-100.0
        )

        # Should handle negative debt (perhaps a credit balance)
        assert result["debt_to_income_ratio"] == -2.0
        assert result["qualification_status"] == "excellent"

    @pytest.mark.asyncio
    async def test_income_stability_zero_average(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test income stability with zero average income."""
        income_history = [
            {"amount": 0, "date": "2023-01"},
            {"amount": 0, "date": "2023-02"}
        ]
        employment_history = [{"month": "2023-01"}]

        result = await service_impl.analyze_income_stability(income_history, employment_history)

        assert result["average_income"] == 0.0
        assert result["income_variance"] == 100  # Maximum variance for zero average
        assert result["stability_rating"] == "unstable"

    @pytest.mark.asyncio
    async def test_rounding_precision(self, service_impl: FinancialCalculationsServiceImpl) -> None:
        """Test that calculations maintain proper decimal precision."""
        result = await service_impl.calculate_debt_to_income_ratio(
            monthly_income=3333.33,
            monthly_debt_payments=1111.11
        )

        # Should be rounded to 2 decimal places
        expected_dti = round((1111.11 / 3333.33) * 100, 2)
        assert result["debt_to_income_ratio"] == expected_dti
        
        # Verify max additional debt calculation
        expected_max_debt = max(0, (3333.33 * 0.43) - 1111.11)
        assert result["max_additional_debt"] == expected_max_debt
