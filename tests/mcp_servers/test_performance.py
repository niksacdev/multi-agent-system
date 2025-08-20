"""
Performance tests for MCP servers.

These tests verify that the MCP servers perform well under various load conditions
and meet response time requirements.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from loan_processing.tools.mcp_servers.application_verification.service import ApplicationVerificationServiceImpl
from loan_processing.tools.mcp_servers.document_processing.service import MCPDocumentProcessingService
from loan_processing.tools.mcp_servers.financial_calculations.service import FinancialCalculationsServiceImpl


class TestMCPServerPerformance:
    """Performance tests for MCP servers."""

    @pytest.fixture
    def app_verification_service(self) -> ApplicationVerificationServiceImpl:
        """Create application verification service."""
        return ApplicationVerificationServiceImpl()

    @pytest.fixture
    def mock_mcp_client(self) -> AsyncMock:
        """Create mock MCP client for document processing."""
        client = AsyncMock()
        client.call_tool.return_value = '{"result": "test", "type": "mock_response"}'
        return client

    @pytest.fixture
    def document_service(self, mock_mcp_client: AsyncMock) -> MCPDocumentProcessingService:
        """Create document processing service with mock client."""
        return MCPDocumentProcessingService(mcp_client=mock_mcp_client)

    @pytest.fixture
    def financial_service(self) -> FinancialCalculationsServiceImpl:
        """Create financial calculations service."""
        return FinancialCalculationsServiceImpl()

    @pytest.mark.asyncio
    async def test_application_verification_response_time(
        self, app_verification_service: ApplicationVerificationServiceImpl
    ) -> None:
        """Test that application verification calls complete within acceptable time."""
        
        # Test credit report retrieval performance
        start_time = time.time()
        result = await app_verification_service.retrieve_credit_report(
            applicant_id="perf-test-001",
            full_name="Performance Test User",
            address="123 Speed St, Fast City, ST 12345"
        )
        credit_time = time.time() - start_time
        
        assert result["type"] == "credit_report"
        assert credit_time < 0.1  # Should complete in under 100ms
        
        # Test employment verification performance
        start_time = time.time()
        result = await app_verification_service.verify_employment(
            applicant_id="perf-test-001",
            employer_name="Speed Corp",
            position="Fast Worker"
        )
        employment_time = time.time() - start_time
        
        assert result["type"] == "employment_verification"
        assert employment_time < 0.1  # Should complete in under 100ms

    @pytest.mark.asyncio
    async def test_financial_calculations_response_time(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test that financial calculations complete within acceptable time."""
        
        # Test DTI calculation performance
        start_time = time.time()
        result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=5000.0,
            monthly_debt_payments=1500.0
        )
        dti_time = time.time() - start_time
        
        assert result["type"] == "dti_calculation"
        assert dti_time < 0.05  # Should complete in under 50ms
        
        # Test loan affordability calculation performance
        start_time = time.time()
        result = await financial_service.calculate_loan_affordability(
            monthly_income=6000.0,
            existing_debt=1000.0,
            loan_amount=200000.0,
            interest_rate=0.05,
            loan_term_months=360
        )
        affordability_time = time.time() - start_time
        
        assert result["type"] == "affordability_assessment"
        assert affordability_time < 0.1  # Should complete in under 100ms

    @pytest.mark.asyncio
    async def test_document_processing_response_time(
        self, document_service: MCPDocumentProcessingService
    ) -> None:
        """Test that document processing calls complete within acceptable time."""
        
        # Test text extraction performance
        start_time = time.time()
        result = await document_service.extract_text_from_document(
            document_path="/path/to/perf_test.pdf",
            document_type="pdf"
        )
        extraction_time = time.time() - start_time
        
        assert result is not None
        assert extraction_time < 0.2  # Should complete in under 200ms (allows for mock processing)

    @pytest.mark.asyncio
    async def test_concurrent_application_verification_calls(
        self, app_verification_service: ApplicationVerificationServiceImpl
    ) -> None:
        """Test performance with concurrent application verification calls."""
        
        async def make_credit_call(applicant_id: str) -> dict:
            return await app_verification_service.retrieve_credit_report(
                applicant_id=f"concurrent-{applicant_id}",
                full_name=f"User {applicant_id}",
                address=f"{applicant_id} Test St"
            )
        
        # Run 10 concurrent credit report calls
        start_time = time.time()
        tasks = [make_credit_call(str(i)) for i in range(10)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # All calls should complete
        assert len(results) == 10
        for result in results:
            assert result["type"] == "credit_report"
        
        # Total time should be reasonable (not much more than single call due to async)
        assert total_time < 1.0  # Should complete in under 1 second
        
        # Average time per call should be efficient
        avg_time = total_time / 10
        assert avg_time < 0.2  # Average under 200ms per call

    @pytest.mark.asyncio
    async def test_concurrent_financial_calculations(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test performance with concurrent financial calculations."""
        
        async def make_calculation(index: int) -> dict:
            return await financial_service.calculate_debt_to_income_ratio(
                monthly_income=5000.0 + (index * 100),
                monthly_debt_payments=1500.0 + (index * 50)
            )
        
        # Run 20 concurrent DTI calculations
        start_time = time.time()
        tasks = [make_calculation(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # All calculations should complete
        assert len(results) == 20
        for result in results:
            assert result["type"] == "dti_calculation"
            assert result["debt_to_income_ratio"] > 0
        
        # Total time should be reasonable
        assert total_time < 0.5  # Should complete in under 500ms
        
        # Average time per calculation should be very fast
        avg_time = total_time / 20
        assert avg_time < 0.05  # Average under 50ms per calculation

    @pytest.mark.asyncio
    async def test_complex_calculation_performance(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test performance of complex financial calculations."""
        
        # Test income stability analysis with large dataset
        income_history = [
            {"amount": 5000 + (i * 10), "date": f"2023-{(i % 12) + 1:02d}"}
            for i in range(100)  # 100 data points
        ]
        employment_history = [
            {"month": f"2023-{(i % 12) + 1:02d}"}
            for i in range(50)  # 50 months
        ]
        
        start_time = time.time()
        result = await financial_service.analyze_income_stability(
            income_history=income_history,
            employment_history=employment_history
        )
        calculation_time = time.time() - start_time
        
        assert result["type"] == "income_stability_analysis"
        assert result["income_count"] == 100
        assert calculation_time < 0.2  # Should complete in under 200ms even with large dataset

    @pytest.mark.asyncio
    async def test_high_precision_calculations(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test performance with high precision financial calculations."""
        
        # Test calculation with very precise numbers
        start_time = time.time()
        result = await financial_service.calculate_monthly_payment(
            loan_amount=123456.789,
            interest_rate=0.04567,  # High precision interest rate
            loan_term_months=360
        )
        calculation_time = time.time() - start_time
        
        assert result["type"] == "payment_calculation"
        assert result["monthly_payment"] > 0
        assert calculation_time < 0.05  # Should complete quickly even with precision

    @pytest.mark.asyncio
    async def test_memory_usage_stability(
        self, app_verification_service: ApplicationVerificationServiceImpl,
        financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test that memory usage remains stable under repeated calls."""
        import gc
        import sys
        
        # Get initial memory usage (approximate)
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for i in range(100):
            # Mix of different service calls
            await app_verification_service.retrieve_credit_report(
                applicant_id=f"memory-test-{i}",
                full_name=f"User {i}",
                address=f"{i} Memory Lane"
            )
            
            await financial_service.calculate_debt_to_income_ratio(
                monthly_income=5000.0,
                monthly_debt_payments=1500.0 + i
            )
            
            # Periodic garbage collection
            if i % 20 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be minimal (allowing for some interpreter overhead)
        memory_growth = final_objects - initial_objects
        assert memory_growth < 1000  # Less than 1000 new objects retained

    @pytest.mark.asyncio
    async def test_error_handling_performance(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test that error handling doesn't significantly impact performance."""
        
        # Test performance with invalid inputs (should fail fast)
        start_time = time.time()
        result = await financial_service.calculate_debt_to_income_ratio(
            monthly_income=0.0,  # Invalid input
            monthly_debt_payments=1500.0
        )
        error_time = time.time() - start_time
        
        assert "error" in result
        assert error_time < 0.01  # Error handling should be very fast (under 10ms)

    @pytest.mark.asyncio 
    async def test_batch_processing_performance(
        self, app_verification_service: ApplicationVerificationServiceImpl
    ) -> None:
        """Test performance when processing batch requests."""
        
        # Simulate batch processing of multiple applications
        async def process_application(app_id: str) -> dict:
            # Simulate processing multiple data points for one application
            credit_task = app_verification_service.retrieve_credit_report(
                applicant_id=app_id,
                full_name=f"Applicant {app_id}",
                address=f"{app_id} Batch St"
            )
            
            employment_task = app_verification_service.verify_employment(
                applicant_id=app_id,
                employer_name=f"Company {app_id}",
                position="Worker"
            )
            
            bank_task = app_verification_service.get_bank_account_data(
                account_number=f"12345{app_id}",
                routing_number="987654321"
            )
            
            # Wait for all tasks for this application
            credit, employment, bank = await asyncio.gather(
                credit_task, employment_task, bank_task
            )
            
            return {
                "applicant_id": app_id,
                "credit_score": credit["credit_score"],
                "employment_verified": employment["employment_status"] == "verified",
                "bank_balance": bank["current_balance"]
            }
        
        # Process 5 applications concurrently
        start_time = time.time()
        batch_tasks = [process_application(f"batch-{i}") for i in range(5)]
        batch_results = await asyncio.gather(*batch_tasks)
        batch_time = time.time() - start_time
        
        # All applications should be processed successfully
        assert len(batch_results) == 5
        for result in batch_results:
            assert "applicant_id" in result
            assert "credit_score" in result
            assert "employment_verified" in result
            assert "bank_balance" in result
        
        # Batch processing should be efficient
        assert batch_time < 2.0  # Should complete in under 2 seconds
        
        # Average processing time per application should be reasonable
        avg_time_per_app = batch_time / 5
        assert avg_time_per_app < 0.5  # Under 500ms per application on average


@pytest.mark.slow
class TestMCPServerStressTests:
    """Stress tests for MCP servers under heavy load."""

    @pytest.fixture
    def financial_service(self) -> FinancialCalculationsServiceImpl:
        """Create financial calculations service."""
        return FinancialCalculationsServiceImpl()

    @pytest.mark.asyncio
    async def test_high_volume_calculations(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test server performance under high volume of calculations."""
        
        async def calculation_batch() -> list[dict]:
            tasks = []
            for i in range(50):  # 50 calculations per batch
                task = financial_service.calculate_debt_to_income_ratio(
                    monthly_income=5000.0 + (i * 10),
                    monthly_debt_payments=1500.0 + (i * 5)
                )
                tasks.append(task)
            return await asyncio.gather(*tasks)
        
        # Run 10 batches (500 total calculations)
        start_time = time.time()
        batch_tasks = [calculation_batch() for _ in range(10)]
        all_results = await asyncio.gather(*batch_tasks)
        total_time = time.time() - start_time
        
        # Verify all calculations completed
        total_calculations = sum(len(batch) for batch in all_results)
        assert total_calculations == 500
        
        # Performance should be acceptable even under high load
        assert total_time < 5.0  # Should complete 500 calculations in under 5 seconds
        
        # Average time per calculation should remain low
        avg_time = total_time / 500
        assert avg_time < 0.01  # Under 10ms per calculation on average

    @pytest.mark.asyncio
    async def test_sustained_load_performance(
        self, financial_service: FinancialCalculationsServiceImpl
    ) -> None:
        """Test performance under sustained load over time."""
        
        results = []
        durations = []
        
        # Run calculations continuously for multiple iterations
        for iteration in range(10):
            start_time = time.time()
            
            # Burst of calculations
            tasks = [
                financial_service.calculate_monthly_payment(
                    loan_amount=100000.0 + (i * 1000),
                    interest_rate=0.05 + (i * 0.001),
                    loan_term_months=360
                )
                for i in range(20)
            ]
            
            batch_results = await asyncio.gather(*tasks)
            iteration_time = time.time() - start_time
            
            results.extend(batch_results)
            durations.append(iteration_time)
            
            # Small delay between iterations
            await asyncio.sleep(0.1)
        
        # Verify all calculations completed successfully
        assert len(results) == 200
        for result in results:
            assert result["type"] == "payment_calculation"
            assert result["monthly_payment"] > 0
        
        # Performance should remain consistent across iterations
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        # Performance should be stable (no significant degradation)
        # Make thresholds even more flexible to account for system variability
        assert max_duration < avg_duration * 5  # Max shouldn't be more than 5x average
        assert min_duration > avg_duration * 0.1  # Min shouldn't be less than 0.1x average (very permissive)
        assert avg_duration < 1.0  # Average iteration should be under 1 second
