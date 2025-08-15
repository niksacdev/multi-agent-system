"""
Business service interfaces for loan processing system.

This module exports capability-based service interfaces that align with
our MCP server architecture, providing clean abstractions for:
- Application data verification
- Document processing and analysis
- Financial calculations
- Compliance validation and fraud detection

These interfaces are provider-agnostic and can be implemented using
MCP servers, REST APIs, direct database calls, or other methods.
"""

from __future__ import annotations

# Export new capability-based service interfaces
from .application_verification import ApplicationVerificationService
from .compliance_validation import ComplianceValidationService
from .document_processing import DocumentProcessingService
from .financial_calculations import FinancialCalculationsService

__all__ = [
    "ApplicationVerificationService",
    "DocumentProcessingService",
    "FinancialCalculationsService",
    "ComplianceValidationService",
]
