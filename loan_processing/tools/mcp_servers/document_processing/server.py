"""Document Processing MCP Server.

Provides document analysis tools for loan processing agents.
Uses the DocumentProcessingService implementation for business logic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from loan_processing.utils import get_logger, log_execution  # noqa: E402

from .service import MCPDocumentProcessingService  # noqa: E402

# Initialize logging
logger = get_logger(__name__)

# Create MCP server
mcp = FastMCP("document-processing")

# Configure for SSE transport
mcp.settings.host = "localhost"
mcp.settings.port = 8011

# Initialize service implementation
document_service = MCPDocumentProcessingService()

logger.info(
    "Document Processing MCP Server initialized", component="mcp_server", server_name="document_processing", port=8011
)


@mcp.tool()
@log_execution(component="mcp_server", operation="extract_text_from_document")
async def extract_text_from_document(document_path: str, document_type: str = "auto") -> str:
    """
    Extract text from uploaded documents using OCR.

    Args:
        document_path: Path to the document file
        document_type: Type of document for optimized processing

    Returns:
        JSON string with extracted text and metadata
    """
    logger.info(
        "Document text extraction request",
        document_path=document_path,
        document_type=document_type,
        component="mcp_server",
    )
    result = await document_service.extract_text_from_document(document_path, document_type)
    return str(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="classify_document_type")
async def classify_document_type(document_content: str) -> str:
    """
    Classify document type based on content analysis.

    Args:
        document_content: Raw text content of the document

    Returns:
        JSON string with document classification results
    """
    logger.info("Document classification request", content_length=len(document_content), component="mcp_server")
    result = await document_service.classify_document_type(document_content)
    return str(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="validate_document_format")
async def validate_document_format(document_path: str, expected_format: str) -> str:
    """
    Validate document format and authenticity.

    Args:
        document_path: Path to the document file
        expected_format: Expected document format/type

    Returns:
        JSON string with validation results
    """
    logger.info(
        "Document validation request",
        document_path=document_path,
        expected_format=expected_format,
        component="mcp_server",
    )
    result = await document_service.validate_document_format(document_path, expected_format)
    return str(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="extract_structured_data")
async def extract_structured_data(document_path: str, data_schema: str) -> str:
    """
    Extract structured data from documents based on schema.

    Args:
        document_path: Path to the document file
        data_schema: JSON string defining expected data structure

    Returns:
        JSON string with extracted structured data
    """
    logger.info("Structured data extraction request", document_path=document_path, component="mcp_server")
    schema_dict = json.loads(data_schema)
    result = await document_service.extract_structured_data(document_path, schema_dict)
    return str(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="convert_document_format")
async def convert_document_format(input_path: str, output_format: str) -> str:
    """
    Convert document to different format.

    Args:
        input_path: Path to input document
        output_format: Target format for conversion

    Returns:
        JSON string with conversion results and output path
    """
    logger.info(
        "Document conversion request", input_path=input_path, output_format=output_format, component="mcp_server"
    )
    result = await document_service.convert_document_format(input_path, output_format)
    return str(result)


@mcp.tool()
async def document_processing_health_check() -> str:
    """Health check endpoint for document processing service."""
    from datetime import datetime, timezone

    return json.dumps(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "document_processing",
            "version": "1.0.0",
            "port": 8011,
        }
    )


if __name__ == "__main__":
    # Default to SSE transport as recommended by architect
    transport = "sse"
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        transport = "stdio"  # Allow stdio override for development

    if transport == "sse":
        logger.info(
            "Starting Document Processing MCP Server",
            transport="sse",
            url="http://localhost:8011/sse",
            component="mcp_server",
        )
    else:
        logger.info("Starting Document Processing MCP Server", transport="stdio", component="mcp_server")

    mcp.run(transport=transport)
