"""
Compliance validation service interface.

Defines business capabilities for regulatory compliance checking,
fraud detection, and policy validation in loan processing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ComplianceValidationService(ABC):
    """
    Abstract service for compliance validation and fraud detection.

    This service handles all compliance operations including:
    - Fraud pattern analysis
    - Identity consistency verification
    - Regulatory compliance checking (TILA, RESPA, FCRA, ECOA)
    - Documentation completeness validation
    - Sanctions and watchlist screening
    - Internal policy validation

    Business Rules:
    - All compliance checks must be documented for audit
    - Fraud detection must follow industry best practices
    - Regulatory requirements must be current and accurate
    - Privacy and data protection laws must be observed
    """

    @abstractmethod
    async def check_fraud_patterns(self, application_data: str) -> dict[str, Any]:
        """
        Analyze application data for known fraud indicators and suspicious patterns.

        Args:
            application_data: JSON string with loan application data

        Returns:
            dict with fraud analysis results and risk assessment

        Raises:
            FraudCheckError: If fraud analysis cannot be performed
        """
        ...

    @abstractmethod
    async def validate_identity_consistency(self, identity_data: str) -> dict[str, Any]:
        """
        Check identity data consistency across multiple sources.

        Args:
            identity_data: JSON string with identity information from various sources

        Returns:
            dict with identity validation results and consistency analysis

        Raises:
            IdentityValidationError: If identity consistency cannot be verified
        """
        ...

    @abstractmethod
    async def check_regulatory_compliance(self, loan_data: str, regulation_type: str = "all") -> dict[str, Any]:
        """
        Validate loan data against regulatory requirements.

        Args:
            loan_data: JSON string with complete loan application and decision data
            regulation_type: Specific regulation to check or "all"

        Returns:
            dict with compliance validation results

        Raises:
            ComplianceCheckError: If compliance validation cannot be performed
        """
        ...

    @abstractmethod
    async def validate_documentation_completeness(self, required_docs: str, provided_docs: str) -> dict[str, Any]:
        """
        Check if all required documentation has been provided and is complete.

        Args:
            required_docs: JSON string with list of required document types
            provided_docs: JSON string with list of provided document types

        Returns:
            dict with documentation completeness analysis

        Raises:
            DocumentValidationError: If documentation completeness cannot be verified
        """
        ...

    @abstractmethod
    async def check_sanctions_and_watchlists(self, name: str, address: str) -> dict[str, Any]:
        """
        Check applicant against sanctions lists and watchlists.

        Args:
            name: Full name of applicant
            address: Address of applicant

        Returns:
            dict with sanctions screening results

        Raises:
            SanctionsCheckError: If sanctions screening cannot be performed
        """
        ...

    @abstractmethod
    async def validate_lending_policy_compliance(self, loan_details: str, policy_rules: str) -> dict[str, Any]:
        """
        Check loan details against internal lending policy rules.

        Args:
            loan_details: JSON string with loan amount, terms, rates, etc.
            policy_rules: JSON string with internal policy constraints

        Returns:
            dict with policy compliance results

        Raises:
            PolicyValidationError: If policy compliance cannot be verified
        """
        ...
