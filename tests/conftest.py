"""
Pytest configuration and shared fixtures for MCP server tests.

This module provides common fixtures and configuration that can be used
across all test files in the MCP servers test suite.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from loan_processing.tools.mcp_servers.application_verification.service import ApplicationVerificationServiceImpl
from loan_processing.tools.mcp_servers.document_processing.service import MCPDocumentProcessingService
from loan_processing.tools.mcp_servers.financial_calculations.service import FinancialCalculationsServiceImpl


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "edge_case: mark test as an edge case test")
    config.addinivalue_line("markers", "orchestration: mark test as an orchestration test")
    config.addinivalue_line("markers", "agent_registry: mark test as an agent registry test")
    config.addinivalue_line("markers", "pattern_config: mark test as a pattern configuration test")


# Service fixtures
@pytest.fixture
def app_verification_service() -> ApplicationVerificationServiceImpl:
    """Create application verification service instance."""
    return ApplicationVerificationServiceImpl()


@pytest.fixture
def financial_service() -> FinancialCalculationsServiceImpl:
    """Create financial calculations service instance."""
    return FinancialCalculationsServiceImpl()


@pytest.fixture
def mock_mcp_client() -> AsyncMock:
    """Create mock MCP client for document processing."""
    client = AsyncMock()
    
    # Default successful responses
    default_responses = {
        "extract_text_from_document": {
            "extracted_text": "Sample document text content",
            "confidence": 0.95,
            "language": "en",
            "page_count": 1,
            "type": "text_extraction"
        },
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
        },
        "extract_structured_data": {
            "extracted_data": {
                "applicant_name": "John Doe",
                "annual_income": 75000,
                "employer": "Tech Corp"
            },
            "confidence": 0.92,
            "type": "structured_extraction"
        },
        "convert_document_format": {
            "output_path": "/path/to/converted_document.jpg",
            "conversion_successful": True,
            "original_format": "pdf",
            "target_format": "jpg",
            "type": "conversion"
        }
    }
    
    def mock_call_tool(tool_name: str, params: dict[str, Any]) -> str:
        """Mock implementation of call_tool method."""
        response = default_responses.get(
            tool_name, 
            {"error": f"Unknown tool: {tool_name}", "type": "error"}
        )
        return json.dumps(response)
    
    client.call_tool.side_effect = mock_call_tool
    return client


@pytest.fixture
def document_service(mock_mcp_client: AsyncMock) -> MCPDocumentProcessingService:
    """Create document processing service with mock MCP client."""
    return MCPDocumentProcessingService(mcp_client=mock_mcp_client)


# Test data fixtures
@pytest.fixture
def sample_applicant_data() -> dict[str, Any]:
    """Sample applicant data for testing."""
    return {
        "applicant_id": "test-app-001",
        "personal_info": {
            "full_name": "John Doe",
            "address": "123 Main St, Anytown, ST 12345",
            "phone": "555-0123",
            "email": "john.doe@email.com"
        },
        "employment": {
            "employer_name": "Tech Corporation",
            "position": "Software Engineer",
            "annual_income": 85000,
            "tenure_months": 24
        },
        "financial": {
            "monthly_income": 7083.33,
            "monthly_debt_payments": 1200.0,
            "liquid_assets": 25000.0
        },
        "loan_request": {
            "amount": 300000.0,
            "purpose": "home_purchase",
            "term_months": 360,
            "interest_rate": 0.045
        }
    }


@pytest.fixture
def sample_credit_report() -> dict[str, Any]:
    """Sample credit report data for testing."""
    return {
        "applicant_id": "test-app-001",
        "full_name": "John Doe",
        "address": "123 Main St, Anytown, ST 12345",
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


@pytest.fixture
def sample_employment_verification() -> dict[str, Any]:
    """Sample employment verification data for testing."""
    return {
        "applicant_id": "test-app-001",
        "employer_name": "Tech Corporation",
        "position": "Software Engineer",
        "employment_status": "verified",
        "employment_type": "full-time",
        "annual_income": 85000,
        "tenure_months": 24,
        "verification_date": "2023-08-11T10:30:00Z",
        "hr_contact": "hr@techcorp.com",
        "income_stability": "stable",
        "recommendation": "verify",
        "type": "employment_verification"
    }


@pytest.fixture
def sample_bank_data() -> dict[str, Any]:
    """Sample bank account data for testing."""
    return {
        "account_number_suffix": "7890",
        "routing_number": "987654321",
        "current_balance": 25000.50,
        "average_daily_balance": 24500.25,
        "owner_verified": True,
        "recent_transactions": [
            {"date": "2023-08-10", "amount": -125.34, "description": "Utility Bill"},
            {"date": "2023-08-05", "amount": -58.12, "description": "Groceries"},
            {"date": "2023-08-01", "amount": 3250.00, "description": "Payroll"}
        ],
        "overdrafts_last_90_days": 0,
        "type": "bank_account_data"
    }


@pytest.fixture
def sample_dti_calculation() -> dict[str, Any]:
    """Sample DTI calculation result for testing."""
    return {
        "debt_to_income_ratio": 16.95,
        "monthly_income": 7083.33,
        "monthly_debt_payments": 1200.0,
        "qualification_status": "excellent",
        "risk_level": "low",
        "max_additional_debt": 2445.83,
        "calculation_timestamp": "2023-08-11T10:30:00Z",
        "type": "dti_calculation"
    }


@pytest.fixture
def sample_loan_affordability() -> dict[str, Any]:
    """Sample loan affordability assessment for testing."""
    return {
        "loan_amount": 300000.0,
        "monthly_payment": 1520.06,
        "total_monthly_debt": 2720.06,
        "debt_to_income_ratio": 38.4,
        "affordability_status": "affordable",
        "approval_probability": 0.78,
        "total_interest": 247221.60,
        "payment_to_income_ratio": 21.46,
        "calculation_timestamp": "2023-08-11T10:30:00Z",
        "type": "affordability_assessment"
    }


# Helper fixtures
@pytest.fixture
def validation_helpers():
    """Helper functions for test validation."""
    
    class ValidationHelpers:
        @staticmethod
        def assert_response_structure(
            response: dict[str, Any],
            required_fields: list[str],
            response_type: str
        ) -> None:
            """Assert that response has required structure."""
            for field in required_fields:
                assert field in response, f"Missing required field: {field}"
            assert response.get("type") == response_type, f"Expected type {response_type}, got {response.get('type')}"
        
        @staticmethod
        def assert_financial_ranges(result: dict[str, Any]) -> None:
            """Assert financial values are within reasonable ranges."""
            if "credit_score" in result:
                assert 300 <= result["credit_score"] <= 850
            if "debt_to_income_ratio" in result:
                assert 0 <= result["debt_to_income_ratio"] <= 500
            if "monthly_payment" in result:
                assert result["monthly_payment"] >= 0
            if "utilization_ratio" in result:
                assert 0 <= result["utilization_ratio"] <= 100
            if "approval_probability" in result:
                assert 0 <= result["approval_probability"] <= 1
        
        @staticmethod
        def assert_dates_valid(result: dict[str, Any]) -> None:
            """Assert that date fields are valid ISO format."""
            date_fields = ["verification_date", "calculation_timestamp"]
            for field in date_fields:
                if field in result:
                    # Basic check for ISO format
                    assert "T" in result[field]
                    assert result[field].endswith("Z") or "+" in result[field] or "-" in result[field][-6:]
    
    return ValidationHelpers()


# Parametrized test data
@pytest.fixture(params=[
    {"income": 5000, "debt": 1000, "expected_status": "excellent"},
    {"income": 5000, "debt": 2000, "expected_status": "good"},
    {"income": 5000, "debt": 2500, "expected_status": "marginal"},
    {"income": 3000, "debt": 2000, "expected_status": "poor"}
])
def dti_test_cases(request):
    """Parametrized DTI test cases."""
    return request.param


@pytest.fixture(params=[
    {"used": 1000, "available": 10000, "expected_impact": "excellent"},
    {"used": 2500, "available": 10000, "expected_impact": "good"},
    {"used": 4000, "available": 10000, "expected_impact": "fair"},
    {"used": 7500, "available": 10000, "expected_impact": "poor"}
])
def utilization_test_cases(request):
    """Parametrized credit utilization test cases."""
    return request.param


# Async test helpers
@pytest.fixture
def async_test_helpers():
    """Helper functions for async testing."""
    
    class AsyncTestHelpers:
        @staticmethod
        async def run_concurrent_calls(callable_func, args_list: list, max_concurrency: int = 10):
            """Run multiple async calls concurrently with concurrency limit."""
            import asyncio
            
            semaphore = asyncio.Semaphore(max_concurrency)
            
            async def limited_call(args):
                async with semaphore:
                    return await callable_func(*args)
            
            tasks = [limited_call(args) for args in args_list]
            return await asyncio.gather(*tasks)
        
        @staticmethod
        async def measure_execution_time(callable_func, *args, **kwargs):
            """Measure execution time of an async function."""
            import time
            start_time = time.time()
            result = await callable_func(*args, **kwargs)
            execution_time = time.time() - start_time
            return result, execution_time
    
    return AsyncTestHelpers()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test."""
    yield
    # Any cleanup code would go here
    # For now, our tests don't create persistent state that needs cleanup


# Session-scoped fixtures for expensive setup
@pytest.fixture(scope="session")
def test_config():
    """Test configuration that persists for the entire session."""
    return {
        "max_execution_time": {
            "unit_test": 0.1,  # 100ms
            "integration_test": 2.0,  # 2 seconds
            "performance_test": 10.0  # 10 seconds
        },
        "coverage_thresholds": {
            "line_coverage": 90,
            "branch_coverage": 85
        },
        "test_data_ranges": {
            "credit_score": (300, 850),
            "dti_ratio": (0, 500),
            "utilization_ratio": (0, 100),
            "approval_probability": (0, 1)
        }
    }


# Mock data factory fixtures
@pytest.fixture
def mock_data_factory():
    """Factory for creating mock test data."""
    
    class MockDataFactory:
        @staticmethod
        def create_applicant(
            credit_score: int = 720,
            annual_income: int = 75000,
            monthly_debt: float = 1200.0
        ) -> dict[str, Any]:
            """Create mock applicant data with specified characteristics."""
            return {
                "applicant_id": f"mock-{credit_score}-{annual_income}",
                "credit_score": credit_score,
                "annual_income": annual_income,
                "monthly_income": annual_income / 12,
                "monthly_debt": monthly_debt,
                "dti_ratio": (monthly_debt / (annual_income / 12)) * 100
            }
        
        @staticmethod
        def create_loan_scenario(
            loan_amount: float = 250000.0,
            interest_rate: float = 0.045,
            term_months: int = 360
        ) -> dict[str, Any]:
            """Create mock loan scenario data."""
            return {
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "term_months": term_months,
                "loan_type": "conventional",
                "purpose": "home_purchase"
            }
    
    return MockDataFactory()
