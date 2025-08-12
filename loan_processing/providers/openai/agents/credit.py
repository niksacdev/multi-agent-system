from __future__ import annotations

from agents import Agent
from agents.mcp.server import MCPServerSse

from loan_processing.providers.persona_loader import load_persona


def create_application_verification_mcp_server() -> MCPServerSse:
    """Create MCP server for application verification tools."""
    return MCPServerSse(
        params={"url": "http://localhost:8010/sse"}
    )


def create_financial_calculations_mcp_server() -> MCPServerSse:
    """Create MCP server for financial calculations tools."""
    return MCPServerSse(
        params={"url": "http://localhost:8012/sse"}
    )


def create_document_processing_mcp_server() -> MCPServerSse:
    """Create MCP server for document processing tools."""
    return MCPServerSse(
        params={"url": "http://localhost:8011/sse"}
    )


def credit_agent(model: str | None = None) -> Agent:
    """
    Create an autonomous Credit Agent with access to multiple MCP tool servers.

    The agent can decide which tools to use based on the assessment requirements:
    - Application verification tools for credit data and employment verification
    - Financial calculations tools for DTI and affordability calculations
    - Document processing tools for extracting data from financial documents

    Args:
        model: OpenAI model to use (e.g., "gpt-4")

    Returns:
        Configured Agent with autonomous tool access
    """
    return Agent(
        name="Credit Agent",
        instructions=load_persona("credit"),
        model=model,
        mcp_servers=[
            create_application_verification_mcp_server(),  # Credit data, employment verification
            create_financial_calculations_mcp_server(),    # DTI, affordability calculations
            create_document_processing_mcp_server(),       # Document analysis
        ],
    )


__all__ = ["credit_agent", "create_application_verification_mcp_server", "create_financial_calculations_mcp_server"]
