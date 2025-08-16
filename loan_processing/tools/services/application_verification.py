"""
Application verification service interface.

Defines business capabilities for retrieving and verifying external data
required for loan processing applications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ApplicationVerificationService(ABC):
    """
    Abstract service for external data verification and retrieval.

    This service handles all external data operations including:
    - Credit bureau data retrieval
    - Employment verification
    - Bank account verification
    - Tax transcript data
    - Asset verification

    Business Rules:
    - Must verify data source authenticity
    - All external data requests must be logged for audit
    - Data freshness requirements must be met
    - Privacy and security protocols must be followed
    """

    @abstractmethod
    async def retrieve_credit_report(self, applicant_id: str, full_name: str, address: str) -> dict[str, Any]:
        """
        Retrieve credit report from credit bureaus.

        Args:
            applicant_id: Internal applicant identifier (UUID or similar)
            full_name: Full legal name
            address: Current address

        Returns:
            dict with credit report data including score, accounts, payment history

        Raises:
            CreditBureauError: If credit data cannot be retrieved
            IdentityVerificationError: If applicant identity cannot be verified
        """
        pass

    @abstractmethod
    async def verify_employment(self, applicant_id: str, employer_name: str, position: str) -> dict[str, Any]:
        """
        Verify employment status and income with employer.

        Args:
            applicant_id: Internal applicant identifier (UUID or similar)
            employer_name: Name of employer to verify
            position: Job position/title to verify

        Returns:
            dict with employment verification data

        Raises:
            EmploymentVerificationError: If employment cannot be verified
        """
        pass

    @abstractmethod
    async def get_bank_account_data(self, account_number: str, routing_number: str) -> dict[str, Any]:
        """
        Retrieve bank account data for asset verification.

        Args:
            account_number: Bank account number
            routing_number: Bank routing number

        Returns:
            dict with account balance, transaction history, ownership verification

        Raises:
            BankVerificationError: If bank data cannot be retrieved
        """
        pass

    @abstractmethod
    async def get_tax_transcript_data(self, applicant_id: str, tax_year: int) -> dict[str, Any]:
        """
        Retrieve tax transcript data from IRS.

        Args:
            applicant_id: Internal applicant identifier (UUID or similar)
            tax_year: Tax year to retrieve

        Returns:
            dict with tax transcript data including income, deductions

        Raises:
            TaxTranscriptError: If tax data cannot be retrieved
        """
        pass

    @abstractmethod
    async def verify_asset_information(self, asset_type: str, asset_details: dict[str, Any]) -> dict[str, Any]:
        """
        Verify asset information using internal applicant tracking.
        """
