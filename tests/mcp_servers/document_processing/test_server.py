"""
Tests for Document Processing MCP Server.

This module tests the MCP server implementation for document processing,
including both the server tools and the service implementation.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from loan_processing.tools.mcp_servers.document_processing.server import (
    classify_document_type,
    convert_document_format,
    document_service,
    extract_structured_data,
    extract_text_from_document,
    validate_document_format,
)
from loan_processing.tools.mcp_servers.document_processing.service import MCPDocumentProcessingService


class TestMCPDocumentProcessingService:
    """Test the MCP-based document processing service implementation."""

    @pytest.fixture
    def mock_mcp_client(self) -> AsyncMock:
        """Create a mock MCP client for testing."""
        return AsyncMock()

    @pytest.fixture
    def service_impl(self, mock_mcp_client: AsyncMock) -> MCPDocumentProcessingService:
        """Create service implementation with mock MCP client."""
        return MCPDocumentProcessingService(mcp_client=mock_mcp_client)

    @pytest.mark.asyncio
    async def test_extract_text_from_document(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test text extraction from document."""
        # Setup mock response
        expected_result = {
            "extracted_text": "Sample document text content",
            "confidence": 0.95,
            "language": "en",
            "page_count": 1,
            "type": "text_extraction",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        # Call the service method
        result = await service_impl.extract_text_from_document(
            document_path="/path/to/document.pdf", document_type="pdf"
        )

        # Verify the MCP client was called correctly
        mock_mcp_client.call_tool.assert_called_once_with(
            "extract_text_from_document", {"document_path": "/path/to/document.pdf", "document_type": "pdf"}
        )

        # Verify the result
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_extract_text_from_document_default_type(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test text extraction with default document type."""
        expected_result = {"extracted_text": "Content", "type": "text_extraction"}
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.extract_text_from_document(document_path="/path/to/document.pdf")

        # Verify default document_type is used
        mock_mcp_client.call_tool.assert_called_once_with(
            "extract_text_from_document", {"document_path": "/path/to/document.pdf", "document_type": "auto"}
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_classify_document_type(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test document type classification."""
        expected_result = {
            "document_type": "tax_form",
            "confidence": 0.87,
            "identified_forms": ["1040", "W2"],
            "type": "classification",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.classify_document_type(
            document_content="Sample tax document content with W2 information"
        )

        mock_mcp_client.call_tool.assert_called_once_with(
            "classify_document_type", {"document_content": "Sample tax document content with W2 information"}
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_validate_document_format(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test document format validation."""
        expected_result = {
            "is_valid": True,
            "format_matches": True,
            "file_integrity": True,
            "detected_format": "pdf",
            "type": "validation",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.validate_document_format(
            document_path="/path/to/document.pdf", expected_format="pdf"
        )

        mock_mcp_client.call_tool.assert_called_once_with(
            "validate_document_format", {"document_path": "/path/to/document.pdf", "expected_format": "pdf"}
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_extract_structured_data(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test structured data extraction."""
        schema = {
            "fields": [
                {"name": "applicant_name", "type": "string", "required": True},
                {"name": "income", "type": "number", "required": True},
            ]
        }
        expected_result = {
            "extracted_data": {"applicant_name": "John Doe", "income": 75000},
            "confidence": 0.92,
            "type": "structured_extraction",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.extract_structured_data(
            document_path="/path/to/application.pdf", data_schema=schema
        )

        # Verify the schema was JSON-encoded in the call
        call_args = mock_mcp_client.call_tool.call_args[0][1]
        assert call_args["document_path"] == "/path/to/application.pdf"
        assert json.loads(call_args["data_schema"]) == schema
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_convert_document_format(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test document format conversion."""
        expected_result = {
            "output_path": "/path/to/converted_document.jpg",
            "conversion_successful": True,
            "original_format": "pdf",
            "target_format": "jpg",
            "type": "conversion",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.convert_document_format(input_path="/path/to/document.pdf", output_format="jpg")

        mock_mcp_client.call_tool.assert_called_once_with(
            "convert_document_format", {"input_path": "/path/to/document.pdf", "output_format": "jpg"}
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_mcp_client_returns_dict(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test handling when MCP client returns dict instead of JSON string."""
        expected_result = {"extracted_text": "Content", "type": "text_extraction"}
        mock_mcp_client.call_tool.return_value = expected_result  # Return dict directly

        result = await service_impl.extract_text_from_document(document_path="/path/to/document.pdf")

        assert result == expected_result

    @pytest.mark.asyncio
    async def test_mcp_client_returns_invalid_json(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test handling when MCP client returns invalid JSON."""
        mock_mcp_client.call_tool.return_value = "invalid json string"

        result = await service_impl.extract_text_from_document(document_path="/path/to/document.pdf")

        # Should return empty dict when JSON parsing fails
        assert result == {}

    @pytest.mark.asyncio
    async def test_mcp_client_returns_non_dict(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test handling when MCP client returns valid JSON but not a dict."""
        mock_mcp_client.call_tool.return_value = json.dumps(["list", "instead", "of", "dict"])

        result = await service_impl.extract_text_from_document(document_path="/path/to/document.pdf")

        # Should return empty dict when parsed result is not a dict
        assert result == {}


class TestDocumentProcessingMCPServer:
    """Test the MCP server tools."""

    @pytest.mark.asyncio
    async def test_extract_text_from_document_tool(self) -> None:
        """Test the MCP tool wrapper for text extraction."""
        # Mock the document_service
        with patch.object(document_service, "extract_text_from_document") as mock_extract:
            expected_result = {
                "extracted_text": "Sample document content",
                "confidence": 0.95,
                "type": "text_extraction",
            }
            mock_extract.return_value = expected_result

            result_str = await extract_text_from_document(document_path="/path/to/test.pdf", document_type="pdf")

            # Verify the service was called correctly
            mock_extract.assert_called_once_with("/path/to/test.pdf", "pdf")

            # Verify result is converted to string
            assert result_str == str(expected_result)

    @pytest.mark.asyncio
    async def test_classify_document_type_tool(self) -> None:
        """Test the MCP tool wrapper for document classification."""
        with patch.object(document_service, "classify_document_type") as mock_classify:
            expected_result = {"document_type": "bank_statement", "confidence": 0.88, "type": "classification"}
            mock_classify.return_value = expected_result

            result_str = await classify_document_type(document_content="Account Balance: $5,000 Transaction History")

            mock_classify.assert_called_once_with("Account Balance: $5,000 Transaction History")
            assert result_str == str(expected_result)

    @pytest.mark.asyncio
    async def test_validate_document_format_tool(self) -> None:
        """Test the MCP tool wrapper for document validation."""
        with patch.object(document_service, "validate_document_format") as mock_validate:
            expected_result = {"is_valid": True, "format_matches": True, "type": "validation"}
            mock_validate.return_value = expected_result

            result_str = await validate_document_format(document_path="/path/to/document.pdf", expected_format="pdf")

            mock_validate.assert_called_once_with("/path/to/document.pdf", "pdf")
            assert result_str == str(expected_result)

    @pytest.mark.asyncio
    async def test_extract_structured_data_tool(self) -> None:
        """Test the MCP tool wrapper for structured data extraction."""
        with patch.object(document_service, "extract_structured_data") as mock_extract:
            expected_result = {
                "extracted_data": {"name": "John Doe", "amount": 1000},
                "confidence": 0.90,
                "type": "structured_extraction",
            }
            mock_extract.return_value = expected_result

            schema_json = json.dumps(
                {"fields": [{"name": "name", "type": "string"}, {"name": "amount", "type": "number"}]}
            )

            result_str = await extract_structured_data(document_path="/path/to/form.pdf", data_schema=schema_json)

            # Verify the schema was parsed correctly
            call_args = mock_extract.call_args[0]
            assert call_args[0] == "/path/to/form.pdf"
            assert call_args[1] == json.loads(schema_json)
            assert result_str == str(expected_result)

    @pytest.mark.asyncio
    async def test_convert_document_format_tool(self) -> None:
        """Test the MCP tool wrapper for document conversion."""
        with patch.object(document_service, "convert_document_format") as mock_convert:
            expected_result = {
                "output_path": "/path/to/converted.jpg",
                "conversion_successful": True,
                "type": "conversion",
            }
            mock_convert.return_value = expected_result

            result_str = await convert_document_format(input_path="/path/to/input.pdf", output_format="jpg")

            mock_convert.assert_called_once_with("/path/to/input.pdf", "jpg")
            assert result_str == str(expected_result)


class TestDocumentProcessingServiceEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def mock_mcp_client(self) -> AsyncMock:
        """Create a mock MCP client for testing."""
        return AsyncMock()

    @pytest.fixture
    def service_impl(self, mock_mcp_client: AsyncMock) -> MCPDocumentProcessingService:
        """Create service implementation with mock MCP client."""
        return MCPDocumentProcessingService(mcp_client=mock_mcp_client)

    @pytest.mark.asyncio
    async def test_extract_text_empty_document_path(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test text extraction with empty document path."""
        mock_mcp_client.call_tool.return_value = json.dumps({"error": "Invalid path"})

        result = await service_impl.extract_text_from_document(document_path="", document_type="pdf")

        mock_mcp_client.call_tool.assert_called_once_with(
            "extract_text_from_document", {"document_path": "", "document_type": "pdf"}
        )
        assert result == {"error": "Invalid path"}

    @pytest.mark.asyncio
    async def test_classify_document_empty_content(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test document classification with empty content."""
        mock_mcp_client.call_tool.return_value = json.dumps(
            {"document_type": "unknown", "confidence": 0.0, "type": "classification"}
        )

        result = await service_impl.classify_document_type(document_content="")

        mock_mcp_client.call_tool.assert_called_once_with("classify_document_type", {"document_content": ""})
        assert result["document_type"] == "unknown"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_extract_structured_data_empty_schema(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test structured data extraction with empty schema."""
        mock_mcp_client.call_tool.return_value = json.dumps(
            {"extracted_data": {}, "confidence": 0.0, "type": "structured_extraction"}
        )

        result = await service_impl.extract_structured_data(document_path="/path/to/document.pdf", data_schema={})

        call_args = mock_mcp_client.call_tool.call_args[0][1]
        assert json.loads(call_args["data_schema"]) == {}
        assert result["extracted_data"] == {}

    @pytest.mark.asyncio
    async def test_service_without_mcp_client(self) -> None:
        """Test service initialization without MCP client."""
        service = MCPDocumentProcessingService(mcp_client=None)
        assert service.mcp_client is None

        # Should return empty dict when client is None (error is logged)
        result = await service.extract_text_from_document("/path/to/doc.pdf")
        assert result == {}

    @pytest.mark.asyncio
    async def test_mcp_client_exception_handling(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test handling when MCP client raises an exception."""
        mock_mcp_client.call_tool.side_effect = Exception("MCP client error")

        # Should return empty dict on exception (error is logged)
        result = await service_impl.extract_text_from_document("/path/to/doc.pdf")
        assert result == {}

    @pytest.mark.asyncio
    async def test_complex_schema_handling(
        self, service_impl: MCPDocumentProcessingService, mock_mcp_client: AsyncMock
    ) -> None:
        """Test handling of complex data schema."""
        complex_schema = {
            "type": "object",
            "properties": {
                "personal_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "required": True},
                        "age": {"type": "integer", "minimum": 18},
                    },
                },
                "financial_data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"account_type": {"type": "string"}, "balance": {"type": "number"}},
                    },
                },
            },
        }

        expected_result = {
            "extracted_data": {
                "personal_info": {"name": "Jane Doe", "age": 30},
                "financial_data": [
                    {"account_type": "checking", "balance": 5000.0},
                    {"account_type": "savings", "balance": 15000.0},
                ],
            },
            "confidence": 0.85,
            "type": "structured_extraction",
        }
        mock_mcp_client.call_tool.return_value = json.dumps(expected_result)

        result = await service_impl.extract_structured_data(
            document_path="/path/to/complex_document.pdf", data_schema=complex_schema
        )

        # Verify complex schema was properly JSON-encoded
        call_args = mock_mcp_client.call_tool.call_args[0][1]
        decoded_schema = json.loads(call_args["data_schema"])
        assert decoded_schema == complex_schema
        assert result == expected_result
