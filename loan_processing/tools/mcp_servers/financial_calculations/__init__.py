"""
Financial Calculations MCP Server.

This module provides both the MCP server implementation and the service
contract implementation for mathematical calculations capabilities.

Exports:
- server: MCP server implementation
- service: Service contract implementation
"""

from .server import mcp as server
from .service import FinancialCalculationsServiceImpl as service

__all__ = ["server", "service"]
