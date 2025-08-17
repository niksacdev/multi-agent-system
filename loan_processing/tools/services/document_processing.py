"""
Document processing service interface.

Defines business capabilities for analyzing, extracting data from,
and processing various document types in loan applications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DocumentProcessingService(ABC):
    """
    Abstract service for document analysis and data extraction.

    This service handles all document operations including:
    - OCR text extraction
    - Document type classification
    - Format validation
    - Structured data extraction
    - Document format conversion

    Business Rules:
    - Must maintain document integrity and authenticity
    - Extracted data must be validated for accuracy
    - Document retention policies must be followed
    - Privacy protection for sensitive documents
    """

    @abstractmethod
    async def extract_text_from_document(self, document_path: str, document_type: str = "auto") -> dict[str, Any]:
        """
        Extract text from uploaded documents using OCR.

        Args:
            document_path: Path to the document file
            document_type: Type of document for optimized processing

        Returns:
            dict with extracted text and metadata

        Raises:
            DocumentProcessingError: If document cannot be processed
        """
        ...

    @abstractmethod
    async def classify_document_type(self, document_content: str) -> dict[str, Any]:
        """
        Classify document type based on content analysis.

        Args:
            document_content: Raw text content of the document

        Returns:
            dict with document classification results

        Raises:
            ClassificationError: If document type cannot be determined
        """
        ...

    @abstractmethod
    async def validate_document_format(self, document_path: str, expected_format: str) -> dict[str, Any]:
        """
        Validate document format and authenticity.

        Args:
            document_path: Path to the document file
            expected_format: Expected document format/type

        Returns:
            dict with validation results

        Raises:
            ValidationError: If document format is invalid
        """
        ...

    @abstractmethod
    async def extract_structured_data(self, document_path: str, data_schema: dict[str, Any]) -> dict[str, Any]:
        """
        Extract structured data from documents based on schema.

        Args:
            document_path: Path to the document file
            data_schema: Schema defining expected data structure

        Returns:
            dict with extracted structured data

        Raises:
            ExtractionError: If structured data cannot be extracted
        """
        ...

    @abstractmethod
    async def convert_document_format(self, input_path: str, output_format: str) -> dict[str, Any]:
        """
        Convert document to different format.

        Args:
            input_path: Path to input document
            output_format: Target format for conversion

        Returns:
            dict with conversion results and output path

        Raises:
            ConversionError: If document cannot be converted
        """
        ...
