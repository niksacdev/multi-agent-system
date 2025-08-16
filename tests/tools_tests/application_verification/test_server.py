"""
Tests for Application Verification MCP Server.

This module tests the MCP server implementation for application verification,
including both the server tools and the service implementation.
"""

from __future__ import annotations

import json

import pytest

from loan_processing.tools.mcp_servers.application_verification.server import (
    get_bank_account_data,
    get_tax_transcript_data,
    retrieve_credit_report,
    verify_asset_information,
    verify_employment,
)
from loan_processing.tools.mcp_servers.application_verification.service import ApplicationVerificationServiceImpl


class TestApplicationVerificationServiceImpl:
    """Test the service implementation directly."""

    @pytest.fixture
    def service_impl(self) -> ApplicationVerificationServiceImpl:
        """Create service implementation for testing."""
        return ApplicationVerificationServiceImpl()

    @pytest.mark.asyncio
    async def test_retrieve_credit_report(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test credit report retrieval with valid data."""
        result = await service_impl.retrieve_credit_report(
            applicant_id="test-123", full_name="John Doe", address="123 Main St, Anytown, ST 12345"
        )

        # Verify structure and required fields
        assert "applicant_id" in result
        assert "full_name" in result
        assert "address" in result
        assert "credit_score" in result
        assert "type" in result

        assert result["applicant_id"] == "test-123"
        assert result["full_name"] == "John Doe"
        assert result["address"] == "123 Main St, Anytown, ST 12345"
        assert result["type"] == "credit_report"

        # Verify credit score is in reasonable range
        assert 620 <= result["credit_score"] <= 780

        # Verify utilization ratio is reasonable
        assert 0.15 <= result["credit_utilization"] <= 0.45

        # Verify recommendation logic
        if result["credit_score"] >= 700 and result["credit_utilization"] <= 0.3:
            assert result["recommendation"] == "approve"
        else:
            assert result["recommendation"] == "review"

    @pytest.mark.asyncio
    async def test_verify_employment(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test employment verification with valid data."""
        result = await service_impl.verify_employment(
            applicant_id="test-456", employer_name="Tech Corp", position="Software Engineer"
        )

        # Verify structure and required fields
        assert "applicant_id" in result
        assert "employer_name" in result
        assert "position" in result
        assert "employment_status" in result
        assert "annual_income" in result
        assert "type" in result

        assert result["applicant_id"] == "test-456"
        assert result["employer_name"] == "Tech Corp"
        assert result["position"] == "Software Engineer"
        assert result["employment_status"] == "verified"
        assert result["type"] == "employment_verification"

        # Verify income is in reasonable range
        assert 50000 <= result["annual_income"] <= 120000

        # Verify recommendation logic
        if result["annual_income"] >= 50000 and result["employment_type"] == "full-time":
            assert result["recommendation"] == "verify"
        else:
            assert result["recommendation"] == "review"

    @pytest.mark.asyncio
    async def test_get_bank_account_data(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test bank account data retrieval."""
        result = await service_impl.get_bank_account_data(account_number="1234567890", routing_number="987654321")

        # Verify structure and required fields
        assert "account_number_suffix" in result
        assert "routing_number" in result
        assert "current_balance" in result
        assert "owner_verified" in result
        assert "type" in result

        assert result["account_number_suffix"] == "7890"
        assert result["routing_number"] == "987654321"
        assert result["owner_verified"] is True
        assert result["type"] == "bank_account_data"

        # Verify balance is in reasonable range
        assert 500 <= result["current_balance"] <= 25000

        # Verify recent transactions exist
        assert "recent_transactions" in result
        assert isinstance(result["recent_transactions"], list)
        assert len(result["recent_transactions"]) > 0

    @pytest.mark.asyncio
    async def test_get_tax_transcript_data(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test tax transcript data retrieval."""
        result = await service_impl.get_tax_transcript_data(applicant_id="test-789", tax_year=2023)

        # Verify structure and required fields
        assert "applicant_id" in result
        assert "tax_year" in result
        assert "adjusted_gross_income" in result
        assert "total_income" in result
        assert "filing_status" in result
        assert "type" in result

        assert result["applicant_id"] == "test-789"
        assert result["tax_year"] == 2023
        assert result["type"] == "tax_transcript"

        # Verify income is in reasonable range
        assert 55000 <= result["adjusted_gross_income"] <= 150000

        # Verify filing status is valid
        assert result["filing_status"] in ["single", "married_joint", "head_of_household"]

    @pytest.mark.asyncio
    async def test_verify_asset_information(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test asset information verification."""
        asset_details = {"description": "2019 Honda Civic", "vin": "12345678901234567"}

        result = await service_impl.verify_asset_information(asset_type="vehicle", asset_details=asset_details)

        # Verify structure and required fields
        assert "asset_type" in result
        assert "asset_details" in result
        assert "ownership_verified" in result
        assert "estimated_value" in result
        assert "type" in result

        assert result["asset_type"] == "vehicle"
        assert result["asset_details"] == asset_details
        assert result["ownership_verified"] is True
        assert result["type"] == "asset_verification"

        # Verify value is in reasonable range
        assert 10000 <= result["estimated_value"] <= 500000

        # Verify verification confidence is reasonable
        assert 0.75 <= result["verification_confidence"] <= 0.95


class TestApplicationVerificationMCPServer:
    """Test the MCP server tools."""

    @pytest.mark.asyncio
    async def test_retrieve_credit_report_tool(self) -> None:
        """Test the MCP tool wrapper for credit report retrieval."""
        result_str = await retrieve_credit_report(applicant_id="test-123", full_name="John Doe", address="123 Main St")

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["applicant_id"] == "test-123"
        assert result["type"] == "credit_report"

    @pytest.mark.asyncio
    async def test_verify_employment_tool(self) -> None:
        """Test the MCP tool wrapper for employment verification."""
        result_str = await verify_employment(
            applicant_id="test-456", employer_name="Tech Corp", position="Software Engineer"
        )

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["applicant_id"] == "test-456"
        assert result["type"] == "employment_verification"

    @pytest.mark.asyncio
    async def test_get_bank_account_data_tool(self) -> None:
        """Test the MCP tool wrapper for bank account data."""
        result_str = await get_bank_account_data(account_number="1234567890", routing_number="987654321")

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["account_number_suffix"] == "7890"
        assert result["type"] == "bank_account_data"

    @pytest.mark.asyncio
    async def test_get_tax_transcript_data_tool(self) -> None:
        """Test the MCP tool wrapper for tax transcript data."""
        result_str = await get_tax_transcript_data(applicant_id="test-789", tax_year=2023)

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["applicant_id"] == "test-789"
        assert result["tax_year"] == 2023
        assert result["type"] == "tax_transcript"

    @pytest.mark.asyncio
    async def test_verify_asset_information_tool(self) -> None:
        """Test the MCP tool wrapper for asset verification."""
        asset_details_json = json.dumps({"description": "2019 Honda Civic", "vin": "12345678901234567"})

        result_str = await verify_asset_information(asset_type="vehicle", asset_details_json=asset_details_json)

        # Verify result is valid JSON
        result = json.loads(result_str)
        assert result["asset_type"] == "vehicle"
        assert result["type"] == "asset_verification"

    @pytest.mark.asyncio
    async def test_verify_asset_information_tool_invalid_json(self) -> None:
        """Test asset verification tool with invalid JSON."""
        result_str = await verify_asset_information(asset_type="vehicle", asset_details_json="invalid json")

        # Verify result is valid JSON and handles error gracefully
        result = json.loads(result_str)
        assert result["asset_type"] == "vehicle"
        assert result["asset_details"] == {"raw": "invalid json"}

    @pytest.mark.asyncio
    async def test_verify_asset_information_tool_empty_json(self) -> None:
        """Test asset verification tool with empty JSON."""
        result_str = await verify_asset_information(asset_type="vehicle", asset_details_json="")

        # Verify result is valid JSON and handles empty input
        result = json.loads(result_str)
        assert result["asset_type"] == "vehicle"
        assert result["asset_details"] == {}


class TestApplicationVerificationServiceConsistency:
    """Test service behavior consistency and edge cases."""

    @pytest.fixture
    def service_impl(self) -> ApplicationVerificationServiceImpl:
        """Create service implementation for testing."""
        return ApplicationVerificationServiceImpl()

    @pytest.mark.asyncio
    async def test_credit_report_risk_level_consistency(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test that credit score and risk level are consistent."""
        # Run multiple times to test consistency
        for _ in range(10):
            result = await service_impl.retrieve_credit_report(
                applicant_id="test-consistency", full_name="Test User", address="123 Test St"
            )

            score = result["credit_score"]
            risk_level = result["risk_level"]

            # Verify risk level matches score
            if score >= 740:
                assert risk_level == "low"
            elif score >= 680:
                assert risk_level == "medium"
            else:
                assert risk_level == "high"

    @pytest.mark.asyncio
    async def test_employment_income_stability_consistency(
        self, service_impl: ApplicationVerificationServiceImpl
    ) -> None:
        """Test employment verification income stability logic."""
        for _ in range(10):
            result = await service_impl.verify_employment(
                applicant_id="test-stability", employer_name="Test Corp", position="Test Position"
            )

            tenure = result["tenure_months"]
            stability = result["income_stability"]

            # Verify stability matches tenure
            if tenure >= 24:
                assert stability == "stable"
            else:
                assert stability == "developing"

    @pytest.mark.asyncio
    async def test_bank_account_data_structure(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test bank account data always has required structure."""
        result = await service_impl.get_bank_account_data(account_number="9876543210", routing_number="123456789")

        # Verify required fields are always present
        required_fields = [
            "account_number_suffix",
            "routing_number",
            "current_balance",
            "average_daily_balance",
            "owner_verified",
            "recent_transactions",
            "overdrafts_last_90_days",
            "type",
        ]

        for field in required_fields:
            assert field in result

        # Verify transactions have required structure
        transactions = result["recent_transactions"]
        assert isinstance(transactions, list)
        for transaction in transactions:
            assert "date" in transaction
            assert "amount" in transaction
            assert "description" in transaction

    @pytest.mark.asyncio
    async def test_asset_verification_confidence_range(self, service_impl: ApplicationVerificationServiceImpl) -> None:
        """Test asset verification confidence is always in valid range."""
        for _ in range(20):
            result = await service_impl.verify_asset_information(
                asset_type="real_estate", asset_details={"address": "456 Property Lane", "year_built": 2015}
            )

            confidence = result["verification_confidence"]
            assert 0.0 <= confidence <= 1.0
            assert confidence >= 0.75  # As per implementation
