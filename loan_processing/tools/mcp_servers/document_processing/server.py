"""Document Processing MCP Server.

Provides document analysis tools for loan processing agents.
Uses the DocumentProcessingService implementation for business logic.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .service import MCPDocumentProcessingService

# Create MCP server
mcp = FastMCP("document-processing")

# Configure for SSE transport
mcp.settings.host = "localhost"
mcp.settings.port = 8011

# Initialize service implementation
document_service = MCPDocumentProcessingService()


@mcp.tool()
async def extract_text_from_document(document_path: str, document_type: str = "auto") -> str:
    """
    Extract text from uploaded documents using OCR.

    Args:
        document_path: Path to the document file
        document_type: Type of document for optimized processing

    Returns:
        JSON string with extracted text and metadata
    """
    result = await document_service.extract_text_from_document(document_path, document_type)
    return str(result)


@mcp.tool()
async def classify_document_type(document_content: str) -> str:
    """
    Classify document type based on content analysis.

    Args:
        document_content: Raw text content of the document

    Returns:
        JSON string with document classification results
    """
    result = await document_service.classify_document_type(document_content)
    return str(result)


@mcp.tool()
async def validate_document_format(document_path: str, expected_format: str) -> str:
    """
    Validate document format and authenticity.

    Args:
        document_path: Path to the document file
        expected_format: Expected document format/type

    Returns:
        JSON string with validation results
    """
    result = await document_service.validate_document_format(document_path, expected_format)
    return str(result)


@mcp.tool()
async def extract_structured_data(document_path: str, data_schema: str) -> str:
    """
    Extract structured data from documents based on schema.

    Args:
        document_path: Path to the document file
        data_schema: JSON string defining expected data structure

    Returns:
        JSON string with extracted structured data
    """
    import json

    schema_dict = json.loads(data_schema)
    result = await document_service.extract_structured_data(document_path, schema_dict)
    return str(result)


@mcp.tool()
async def convert_document_format(input_path: str, output_format: str) -> str:
    """
    Convert document to different format.

    Args:
        input_path: Path to input document
        output_format: Target format for conversion

    Returns:
        JSON string with conversion results and output path
    """
    result = await document_service.convert_document_format(input_path, output_format)
    return str(result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        print("🚀 Starting Document Processing MCP Server with SSE transport...")
        print("   Server will be available at: http://localhost:8011/sse")
        mcp.run(transport="sse")
    else:
        print("🔧 Starting Document Processing MCP Server with stdio transport...")
        mcp.run()
