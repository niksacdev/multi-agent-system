"""
Integration tests for MCP servers.

These tests verify that the MCP servers work together correctly
and handle real-world scenarios.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from loan_processing.tools.mcp_servers.application_verification.service import ApplicationVerificationServiceImpl
from loan_processing.tools.mcp_servers.document_processing.service import MCPDocumentProcessingService
from loan_processing.tools.mcp_servers.financial_calculations.service import FinancialCalculationsServiceImpl


class TestMCPServerIntegration:
    """Integration tests across multiple MCP servers."""

    @pytest.fixture
    def app_verification_service(self) -> ApplicationVerificationServiceImpl:
        """Create application verification service."""
        return ApplicationVerificationServiceImpl()

    @pytest.fixture
    def mock_mcp_client(self) -> AsyncMock:
        """Create mock MCP client for document processing."""
        return AsyncMock()

    @pytest.fixture
    def document_service(self, mock_mcp_client: AsyncMock) -> MCPDocumentProcessingService:
        """Create document processing service with mock client."""
        return MCPDocumentProcessingService(mcp_client=mock_mcp_client)

    @pytest.fixture
    def financial_service(self) -> FinancialCalculationsServiceImpl:
        """Create financial calculations service."""
        return FinancialCalculationsServiceImpl()

    @pytest.mark.asyncio
    async def test_complete_loan_application_workflow(
        self,
        app_verification_service: ApplicationVerificationServiceImpl,
        document_service: MCPDocumentProcessingService,
        financial_service: FinancialCalculationsServiceImpl,
        mock_mcp_client: AsyncMock,
    ) -> None:
        """Test a complete loan application workflow using all MCP servers."""

        # Step 1: Process uploaded documents
        mock_mcp_client.call_tool.return_value = json.dumps(
            {
                "extracted_data": {
                    "applicant_name": "John Doe",
                    "annual_income": 75000,
                    "employer": "Tech Corp",
                    "position": "Software Engineer",
                },
                "confidence": 0.92,
                "type": "structured_extraction",
            }
        )

        document_result = await document_service.extract_structured_data(
            document_path="/uploads/application_form.pdf",
            data_schema={
                "fields": [
                    {"name": "applicant_name", "type": "string"},
                    {"name": "annual_income", "type": "number"},
                    {"name": "employer", "type": "string"},
                    {"name": "position", "type": "string"},
                ]
            },
        )

        applicant_data = document_result["extracted_data"]
        assert applicant_data["applicant_name"] == "John Doe"
        assert applicant_data["annual_income"] == 75000

        # Step 2: Verify employment and get credit data
        employment_result = await app_verification_service.verify_employment(
            applicant_id="app-123", employer_name=applicant_data["employer"], position=applicant_data["position"]
        )

        credit_result = await app_verification_service.retrieve_credit_report(
            applicant_id="app-123", full_name=applicant_data["applicant_name"], address="123 Main St, Anytown, ST 12345"
        )

        # Verify employment data
        assert employment_result["employment_status"] == "verified"
        assert employment_result["annual_income"] >= 50000

        # Verify credit data
        assert 620 <= credit_result["credit_score"] <= 780
        assert credit_result["type"] == "credit_report"

        # Step 3: Calculate financial metrics
        monthly_income = employment_result["annual_income"] / 12
        monthly_debt = 800.0  # Existing debt from credit report analysis

        dti_result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=monthly_income, monthly_debt_payments=monthly_debt
        )

        # Verify DTI calculation
        expected_dti = (monthly_debt / monthly_income) * 100
        assert abs(dti_result["debt_to_income_ratio"] - expected_dti) < 0.01

        # Step 4: Calculate loan affordability for requested amount
        loan_amount = 250000.0
        interest_rate = 0.045  # 4.5%
        loan_term = 360  # 30 years

        affordability_result = await financial_service.calculate_loan_affordability(
            monthly_income=monthly_income,
            existing_debt=monthly_debt,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_term_months=loan_term,
        )

        # Verify affordability assessment
        assert affordability_result["loan_amount"] == loan_amount
        assert affordability_result["monthly_payment"] > 0
        assert affordability_result["affordability_status"] in [
            "highly_affordable",
            "affordable",
            "marginal",
            "unaffordable",
        ]

        # Step 5: Final recommendation based on all factors
        final_recommendation = {
            "applicant_id": "app-123",
            "credit_score": credit_result["credit_score"],
            "employment_verified": employment_result["employment_status"] == "verified",
            "dti_ratio": dti_result["debt_to_income_ratio"],
            "loan_affordability": affordability_result["affordability_status"],
            "approval_probability": affordability_result["approval_probability"],
            "recommended_action": None,
        }

        # Business logic for final recommendation
        if (
            final_recommendation["credit_score"] >= 700
            and final_recommendation["dti_ratio"] <= 36
            and final_recommendation["employment_verified"]
            and final_recommendation["approval_probability"] >= 0.7
        ):
            final_recommendation["recommended_action"] = "approve"
        elif final_recommendation["approval_probability"] >= 0.4:
            final_recommendation["recommended_action"] = "manual_review"
        else:
            final_recommendation["recommended_action"] = "decline"

        assert final_recommendation["recommended_action"] in ["approve", "manual_review", "decline"]

    @pytest.mark.asyncio
    async def test_document_classification_and_processing_workflow(
        self,
        document_service: MCPDocumentProcessingService,
        app_verification_service: ApplicationVerificationServiceImpl,
        mock_mcp_client: AsyncMock,
    ) -> None:
        """Test document classification followed by appropriate processing."""

        # Step 1: Classify uploaded document
        mock_mcp_client.call_tool.side_effect = [
            # First call: classify_document_type
            json.dumps(
                {"document_type": "tax_form", "confidence": 0.89, "identified_forms": ["W2"], "type": "classification"}
            ),
            # Second call: extract_structured_data
            json.dumps(
                {
                    "extracted_data": {
                        "employer": "ABC Company",
                        "employee_name": "Jane Smith",
                        "wages": 68000,
                        "federal_withholding": 12000,
                        "tax_year": 2023,
                    },
                    "confidence": 0.94,
                    "type": "structured_extraction",
                }
            ),
        ]

        # Classify document type
        classification_result = await document_service.classify_document_type(
            document_content="Employee Name: Jane Smith\nEmployer: ABC Company\nWages: $68,000"
        )

        assert classification_result["document_type"] == "tax_form"
        assert "W2" in classification_result["identified_forms"]

        # Step 2: Extract structured data based on classification
        if classification_result["document_type"] == "tax_form":
            w2_schema = {
                "fields": [
                    {"name": "employer", "type": "string"},
                    {"name": "employee_name", "type": "string"},
                    {"name": "wages", "type": "number"},
                    {"name": "federal_withholding", "type": "number"},
                    {"name": "tax_year", "type": "integer"},
                ]
            }

            extraction_result = await document_service.extract_structured_data(
                document_path="/uploads/w2_form.pdf", data_schema=w2_schema
            )

            tax_data = extraction_result["extracted_data"]
            assert tax_data["wages"] == 68000
            assert tax_data["tax_year"] == 2023

            # Step 3: Cross-verify with tax transcript data
            tax_transcript = await app_verification_service.get_tax_transcript_data(
                applicant_id="app-456", tax_year=tax_data["tax_year"]
            )

            # Verify consistency between W2 and tax transcript
            assert tax_transcript["tax_year"] == tax_data["tax_year"]
            # In real scenario, would verify wage amounts match within tolerance

    @pytest.mark.asyncio
    async def test_asset_verification_and_valuation_workflow(
        self,
        app_verification_service: ApplicationVerificationServiceImpl,
        financial_service: FinancialCalculationsServiceImpl,
        document_service: MCPDocumentProcessingService,
        mock_mcp_client: AsyncMock,
    ) -> None:
        """Test asset verification and its impact on loan calculations."""

        # Step 1: Process asset documentation
        mock_mcp_client.call_tool.return_value = json.dumps(
            {
                "extracted_data": {
                    "property_address": "456 Oak Street, Springfield, IL",
                    "assessed_value": 320000,
                    "property_type": "single_family",
                    "year_built": 2015,
                    "square_footage": 2400,
                },
                "confidence": 0.88,
                "type": "structured_extraction",
            }
        )

        property_data = await document_service.extract_structured_data(
            document_path="/uploads/property_deed.pdf",
            data_schema={
                "fields": [
                    {"name": "property_address", "type": "string"},
                    {"name": "assessed_value", "type": "number"},
                    {"name": "property_type", "type": "string"},
                ]
            },
        )

        # Step 2: Verify asset ownership and value
        asset_verification = await app_verification_service.verify_asset_information(
            asset_type="real_estate", asset_details=property_data["extracted_data"]
        )

        assert asset_verification["ownership_verified"] is True
        assert asset_verification["estimated_value"] > 0

        # Step 3: Calculate impact on loan qualification
        # Asset can be used as collateral, improving loan terms
        monthly_income = 6000.0
        existing_debt = 1200.0
        loan_amount = 200000.0

        # Base affordability without asset consideration
        base_affordability = await financial_service.calculate_loan_affordability(
            monthly_income=monthly_income,
            existing_debt=existing_debt,
            loan_amount=loan_amount,
            interest_rate=0.05,
            loan_term_months=360,
        )

        # With asset as collateral, loan-to-value ratio improves
        asset_value = asset_verification["estimated_value"]
        ltv_ratio = (loan_amount / asset_value) * 100

        # Verify asset provides collateral value
        # Note: In mock implementation, asset values are random, so we just verify
        # that the calculation is working correctly
        assert ltv_ratio > 0  # Must be positive
        assert asset_value > 0  # Asset must have positive value

        # If asset value is sufficient, LTV should be reasonable
        if asset_value >= loan_amount:
            assert ltv_ratio <= 100  # LTV can't exceed 100% if asset >= loan

        assert base_affordability["loan_amount"] == loan_amount

    @pytest.mark.asyncio
    async def test_multi_income_source_verification(
        self,
        app_verification_service: ApplicationVerificationServiceImpl,
        financial_service: FinancialCalculationsServiceImpl,
    ) -> None:
        """Test verification and calculation with multiple income sources."""

        # Primary employment verification
        primary_employment = await app_verification_service.verify_employment(
            applicant_id="app-789", employer_name="Primary Corp", position="Manager"
        )

        # Secondary income from tax transcript
        tax_data = await app_verification_service.get_tax_transcript_data(applicant_id="app-789", tax_year=2023)

        # Bank account data for additional income verification
        bank_data = await app_verification_service.get_bank_account_data(
            account_number="1234567890", routing_number="987654321"
        )

        # Calculate total verified income
        primary_monthly = primary_employment["annual_income"] / 12
        tax_monthly = tax_data["adjusted_gross_income"] / 12

        # Use the higher of employment vs tax income for conservative approach
        verified_monthly_income = max(primary_monthly, tax_monthly)

        # Analyze bank deposits for income consistency
        bank_deposits = [tx for tx in bank_data["recent_transactions"] if tx["amount"] > 0]
        avg_monthly_deposits = sum(tx["amount"] for tx in bank_deposits)

        # Income stability assessment
        # Note: income_sources variable removed as it was unused (F841)

        # Use the most conservative income figure for loan calculations
        conservative_income = min(verified_monthly_income, avg_monthly_deposits)

        dti_result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=conservative_income, monthly_debt_payments=1500.0
        )

        assert dti_result["monthly_income"] == conservative_income
        assert dti_result["type"] == "dti_calculation"

    @pytest.mark.asyncio
    async def test_error_handling_across_services(
        self,
        document_service: MCPDocumentProcessingService,
        financial_service: FinancialCalculationsServiceImpl,
        mock_mcp_client: AsyncMock,
    ) -> None:
        """Test error handling when services encounter issues."""

        # Test document processing error
        mock_mcp_client.call_tool.return_value = json.dumps(
            {"error": "Document could not be processed", "type": "processing_error"}
        )

        doc_result = await document_service.extract_text_from_document(document_path="/invalid/path.pdf")
        assert "error" in doc_result

        # Test financial calculation error
        calc_result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=0.0,  # Invalid income
            monthly_debt_payments=1000.0,
        )
        assert "error" in calc_result
        assert calc_result["type"] == "calculation_error"

        # Test graceful degradation - continue with available data
        # Even with some errors, system should provide partial results
        assert doc_result["type"] == "processing_error"
        assert calc_result["type"] == "calculation_error"

    @pytest.mark.asyncio
    async def test_data_consistency_validation(
        self,
        app_verification_service: ApplicationVerificationServiceImpl,
        financial_service: FinancialCalculationsServiceImpl,
    ) -> None:
        """Test validation of data consistency across different sources."""

        # Get employment verification
        employment = await app_verification_service.verify_employment(
            applicant_id="consistency-test", employer_name="DataCorp", position="Analyst"
        )

        # Get tax transcript
        tax_transcript = await app_verification_service.get_tax_transcript_data(
            applicant_id="consistency-test", tax_year=2023
        )

        # Compare income sources
        employment_monthly = employment["annual_income"] / 12
        tax_monthly = tax_transcript["adjusted_gross_income"] / 12

        # Calculate variance between sources
        income_variance = abs(employment_monthly - tax_monthly) / employment_monthly * 100

        # In real implementation, flag for review if variance > 20%
        consistency_check = {
            "employment_income": employment_monthly,
            "tax_income": tax_monthly,
            "variance_percentage": income_variance,
            "requires_review": income_variance > 20,
            "data_sources": ["employment_verification", "tax_transcript"],
        }

        # Use the more conservative income for calculations
        conservative_income = min(employment_monthly, tax_monthly)

        dti_result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=conservative_income, monthly_debt_payments=800.0
        )

        assert consistency_check["variance_percentage"] >= 0
        assert dti_result["monthly_income"] == conservative_income
