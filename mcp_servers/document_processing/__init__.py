"""
Document Processing MCP Server.

This module provides both the MCP server implementation and the service
contract implementation for document analysis capabilities.

Exports:
- server: MCP server implementation
- service: Service contract implementation
"""

from .server import mcp as server
from .service import MCPDocumentProcessingService as service

__all__ = ["server", "service"]
