"""
MCP-based implementation of document processing service.

This implementation uses the Document Processing MCP server (Port 8011)
to provide document analysis and data extraction capabilities.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.tools.services.document_processing import DocumentProcessingService  # noqa: E402
from loan_processing.utils import get_logger, log_execution  # noqa: E402

# Initialize logging
logger = get_logger(__name__)


class MCPDocumentProcessingService(DocumentProcessingService):
    """
    MCP-based implementation of document processing service.

    Uses Document Processing MCP server (Port 8011) for:
    - OCR text extraction
    - Document type classification
    - Format validation
    - Structured data extraction
    - Document format conversion
    """

    def __init__(self, mcp_client: Any = None):
        """
        Initialize with MCP client connection.

        Args:
            mcp_client: Client connection to Document Processing MCP server
        """
        self.mcp_client = mcp_client

        logger.info(
            "Document processing service initialized",
            has_mcp_client=mcp_client is not None,
            component="document_service",
        )

    @log_execution(component="document_service", operation="extract_text_from_document")
    async def extract_text_from_document(self, document_path: str, document_type: str = "auto") -> dict[str, Any]:
        """Extract text from document using Document Processing MCP server."""
        logger.info(
            "Extracting text from document",
            document_path=document_path,
            document_type=document_type,
            component="document_service",
        )

        try:
            result = await self.mcp_client.call_tool(
                "extract_text_from_document", {"document_path": document_path, "document_type": document_type}
            )

            parsed_result = json.loads(result) if isinstance(result, str) else result

            logger.info(
                "Document text extraction completed",
                document_path=document_path,
                success=True,
                component="document_service",
            )

            return parsed_result if isinstance(parsed_result, dict) else {}

        except (json.JSONDecodeError, TypeError) as e:
            logger.error(
                "Failed to parse document extraction result",
                document_path=document_path,
                error_message=str(e),
                error_type=type(e).__name__,
                component="document_service",
            )
            return {}
        except Exception as e:
            logger.error(
                "Document text extraction failed",
                document_path=document_path,
                error_message=str(e),
                error_type=type(e).__name__,
                component="document_service",
            )
            return {}

    async def classify_document_type(self, document_content: str) -> dict[str, Any]:
        """Classify document type using Document Processing MCP server."""
        result = await self.mcp_client.call_tool("classify_document_type", {"document_content": document_content})
        try:
            parsed_result = json.loads(result) if isinstance(result, str) else result
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed_result if isinstance(parsed_result, dict) else {}

    async def validate_document_format(self, document_path: str, expected_format: str) -> dict[str, Any]:
        """Validate document format using Document Processing MCP server."""
        result = await self.mcp_client.call_tool(
            "validate_document_format", {"document_path": document_path, "expected_format": expected_format}
        )
        try:
            parsed_result = json.loads(result) if isinstance(result, str) else result
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed_result if isinstance(parsed_result, dict) else {}

    async def extract_structured_data(self, document_path: str, data_schema: dict[str, Any]) -> dict[str, Any]:
        """Extract structured data using Document Processing MCP server."""
        result = await self.mcp_client.call_tool(
            "extract_structured_data", {"document_path": document_path, "data_schema": json.dumps(data_schema)}
        )
        try:
            parsed_result = json.loads(result) if isinstance(result, str) else result
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed_result if isinstance(parsed_result, dict) else {}

    async def convert_document_format(self, input_path: str, output_format: str) -> dict[str, Any]:
        """Convert document format using Document Processing MCP server."""
        result = await self.mcp_client.call_tool(
            "convert_document_format", {"input_path": input_path, "output_format": output_format}
        )
        try:
            parsed_result = json.loads(result) if isinstance(result, str) else result
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed_result if isinstance(parsed_result, dict) else {}
