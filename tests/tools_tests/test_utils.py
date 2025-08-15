"""
Test utilities for MCP server testing.

Provides common fixtures, helpers, and mock data for testing MCP servers.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest


class MCPTestHelpers:
    """Helper methods for MCP server testing."""

    @staticmethod
    def create_mock_credit_report(applicant_id: str = "test-123") -> dict[str, Any]:
        """Create mock credit report data."""
        return {
            "applicant_id": applicant_id,
            "full_name": "Test User",
            "address": "123 Test St",
            "credit_score": 720,
            "credit_bureau": "TestBureau",
            "credit_utilization": 0.25,
            "payment_history_score": 0.92,
            "recent_inquiries": 2,
            "delinquencies": 0,
            "bankruptcies": 0,
            "trade_lines": 8,
            "risk_level": "low",
            "recommendation": "approve",
            "type": "credit_report"
        }

    @staticmethod
    def create_mock_employment_data(applicant_id: str = "test-456") -> dict[str, Any]:
        """Create mock employment verification data."""
        return {
            "applicant_id": applicant_id,
            "employer_name": "Test Corp",
            "position": "Test Engineer",
            "employment_status": "verified",
            "employment_type": "full-time",
            "annual_income": 75000,
            "tenure_months": 36,
            "verification_date": "2023-08-11T10:30:00Z",
            "hr_contact": "hr@testcorp.com",
            "income_stability": "stable",
            "recommendation": "verify",
            "type": "employment_verification"
        }

    @staticmethod
    def create_mock_bank_data(account_suffix: str = "7890") -> dict[str, Any]:
        """Create mock bank account data."""
        return {
            "account_number_suffix": account_suffix,
            "routing_number": "987654321",
            "current_balance": 15000.50,
            "average_daily_balance": 14500.25,
            "owner_verified": True,
            "recent_transactions": [
                {"date": "2023-08-10", "amount": -125.34, "description": "Utility Bill"},
                {"date": "2023-08-05", "amount": -58.12, "description": "Groceries"},
                {"date": "2023-08-01", "amount": 3250.00, "description": "Payroll"}
            ],
            "overdrafts_last_90_days": 0,
            "type": "bank_account_data"
        }

    @staticmethod
    def create_mock_document_extraction() -> dict[str, Any]:
        """Create mock document extraction result."""
        return {
            "extracted_text": "Sample document content with loan application data",
            "confidence": 0.95,
            "language": "en",
            "page_count": 2,
            "type": "text_extraction"
        }

    @staticmethod
    def create_mock_financial_calculation(
        calculation_type: str = "dti_calculation"
    ) -> dict[str, Any]:
        """Create mock financial calculation result."""
        base_result = {
            "calculation_timestamp": "2023-08-11T10:30:00Z",
            "type": calculation_type
        }

        if calculation_type == "dti_calculation":
            base_result.update({
                "debt_to_income_ratio": 32.5,
                "monthly_income": 6000.0,
                "monthly_debt_payments": 1950.0,
                "qualification_status": "excellent",
                "risk_level": "low",
                "max_additional_debt": 630.0
            })
        elif calculation_type == "payment_calculation":
            base_result.update({
                "loan_amount": 250000.0,
                "annual_interest_rate": 0.045,
                "term_months": 360,
                "payment_type": "principal_and_interest",
                "monthly_payment": 1266.71,
                "total_payment": 456015.60,
                "total_interest": 206015.60,
                "interest_percentage": 82.41
            })

        return base_result

    @staticmethod
    def validate_response_structure(
        response: dict[str, Any],
        required_fields: list[str],
        response_type: str
    ) -> bool:
        """Validate that a response has the required structure."""
        # Check all required fields are present
        for field in required_fields:
            if field not in response:
                return False

        # Check type field matches expected
        if response.get("type") != response_type:
            return False

        return True

    @staticmethod
    def assert_financial_ranges(result: dict[str, Any]) -> None:
        """Assert financial values are within reasonable ranges."""
        if "credit_score" in result:
            assert 300 <= result["credit_score"] <= 850

        if "debt_to_income_ratio" in result:
            assert 0 <= result["debt_to_income_ratio"] <= 500  # Allow extreme cases

        if "monthly_payment" in result:
            assert result["monthly_payment"] >= 0

        if "utilization_ratio" in result:
            assert 0 <= result["utilization_ratio"] <= 100

        if "approval_probability" in result:
            assert 0 <= result["approval_probability"] <= 1


@pytest.fixture
def mock_application_verification_service():
    """Mock application verification service with realistic responses."""
    service = AsyncMock()

    service.retrieve_credit_report.return_value = MCPTestHelpers.create_mock_credit_report()
    service.verify_employment.return_value = MCPTestHelpers.create_mock_employment_data()
    service.get_bank_account_data.return_value = MCPTestHelpers.create_mock_bank_data()

    return service


@pytest.fixture
def mock_document_mcp_client():
    """Mock MCP client for document processing with realistic responses."""
    client = AsyncMock()

    # Default responses for different tool calls
    responses = {
        "extract_text_from_document": MCPTestHelpers.create_mock_document_extraction(),
        "classify_document_type": {
            "document_type": "loan_application",
            "confidence": 0.88,
            "identified_forms": ["application"],
            "type": "classification"
        },
        "validate_document_format": {
            "is_valid": True,
            "format_matches": True,
            "file_integrity": True,
            "detected_format": "pdf",
            "type": "validation"
        }
    }

    def mock_call_tool(tool_name: str, params: dict[str, Any]) -> str:
        """Mock implementation of call_tool method."""
        response = responses.get(tool_name, {"error": f"Unknown tool: {tool_name}"})
        return json.dumps(response)

    client.call_tool.side_effect = mock_call_tool
    return client


@pytest.fixture
def mock_financial_service():
    """Mock financial calculations service with realistic responses."""
    service = AsyncMock()

    service.calculate_debt_to_income_ratio.return_value = MCPTestHelpers.create_mock_financial_calculation("dti_calculation")
    service.calculate_monthly_payment.return_value = MCPTestHelpers.create_mock_financial_calculation("payment_calculation")

    return service


class LoanApplicationTestData:
    """Test data for loan application scenarios."""

    @staticmethod
    def excellent_credit_application() -> dict[str, Any]:
        """Data for an applicant with excellent credit."""
        return {
            "applicant_id": "excellent-001",
            "personal_info": {
                "name": "Alice Johnson",
                "address": "123 Perfect St, Creditville, ST 12345",
                "phone": "555-0001"
            },
            "employment": {
                "employer": "BigTech Corp",
                "position": "Senior Engineer",
                "annual_income": 120000,
                "tenure_months": 48
            },
            "credit_profile": {
                "credit_score": 780,
                "utilization": 0.15,
                "payment_history": 0.98,
                "delinquencies": 0
            },
            "financial": {
                "monthly_income": 10000,
                "monthly_debt": 800,
                "liquid_assets": 50000
            },
            "loan_request": {
                "amount": 400000,
                "purpose": "home_purchase",
                "term_months": 360
            }
        }

    @staticmethod
    def marginal_credit_application() -> dict[str, Any]:
        """Data for an applicant with marginal credit."""
        return {
            "applicant_id": "marginal-002",
            "personal_info": {
                "name": "Bob Smith",
                "address": "456 Average St, Townsville, ST 67890",
                "phone": "555-0002"
            },
            "employment": {
                "employer": "Local Business",
                "position": "Assistant Manager",
                "annual_income": 55000,
                "tenure_months": 18
            },
            "credit_profile": {
                "credit_score": 650,
                "utilization": 0.45,
                "payment_history": 0.85,
                "delinquencies": 1
            },
            "financial": {
                "monthly_income": 4583,
                "monthly_debt": 1200,
                "liquid_assets": 8000
            },
            "loan_request": {
                "amount": 180000,
                "purpose": "home_purchase",
                "term_months": 360
            }
        }

    @staticmethod
    def high_risk_application() -> dict[str, Any]:
        """Data for a high-risk applicant."""
        return {
            "applicant_id": "highrisk-003",
            "personal_info": {
                "name": "Charlie Brown",
                "address": "789 Risky Rd, Struggle City, ST 13579",
                "phone": "555-0003"
            },
            "employment": {
                "employer": "Startup Inc",
                "position": "Contract Worker",
                "annual_income": 38000,
                "tenure_months": 6
            },
            "credit_profile": {
                "credit_score": 580,
                "utilization": 0.85,
                "payment_history": 0.65,
                "delinquencies": 3
            },
            "financial": {
                "monthly_income": 3167,
                "monthly_debt": 1800,
                "liquid_assets": 1500
            },
            "loan_request": {
                "amount": 150000,
                "purpose": "debt_consolidation",
                "term_months": 240
            }
        }


class MCPServerTestRunner:
    """Test runner for MCP server test suites."""

    @staticmethod
    def run_comprehensive_tests(test_categories: list[str] | None = None) -> dict[str, Any]:
        """Run comprehensive test suite for MCP servers."""
        import subprocess
        import sys

        if test_categories is None:
            test_categories = ["unit", "integration", "edge_cases"]

        results = {}

        for category in test_categories:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/mcp_servers/",
                "-v",
                "--tb=short",
                f"--junit-xml=test_results_{category}.xml"
            ]

            if category == "unit":
                cmd.extend(["-k", "not integration"])
            elif category == "integration":
                cmd.extend(["-k", "integration"])
            elif category == "edge_cases":
                cmd.extend(["-k", "edge or error or invalid"])

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                results[category] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
            except subprocess.TimeoutExpired:
                results[category] = {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "Test timeout after 300 seconds",
                    "success": False
                }

        return results


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as an edge case test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
