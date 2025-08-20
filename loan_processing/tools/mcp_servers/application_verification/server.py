"""Application Verification MCP Server."""
# ruff: noqa: I001

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

from .service import ApplicationVerificationServiceImpl  # noqa: E402

# Initialize logging
logger = get_logger(__name__)

# Create MCP server and configure optional SSE
mcp = FastMCP("application-verification")
mcp.settings.host = "localhost"
mcp.settings.port = 8010

# Initialize service implementation
service = ApplicationVerificationServiceImpl()

logger.info(
    "Application Verification MCP Server initialized",
    component="mcp_server",
    server_name="application_verification",
    port=8010,
)


@mcp.tool()
@log_execution(component="mcp_server", operation="retrieve_credit_report")
async def retrieve_credit_report(applicant_id: str, full_name: str, address: str) -> str:
    """Return a credit report summary as JSON string."""
    logger.info("Credit report request", applicant_id=applicant_id, component="mcp_server")
    result = await service.retrieve_credit_report(applicant_id, full_name, address)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="verify_employment")
async def verify_employment(applicant_id: str, employer_name: str, position: str) -> str:
    """Return employment verification as JSON string."""
    logger.info("Employment verification request", applicant_id=applicant_id, component="mcp_server")
    result = await service.verify_employment(applicant_id, employer_name, position)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="get_bank_account_data")
async def get_bank_account_data(account_number: str, routing_number: str) -> str:
    """Return bank account details and balance as JSON string."""
    logger.info("Bank account data request", component="mcp_server")
    result = await service.get_bank_account_data(account_number, routing_number)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="get_tax_transcript_data")
async def get_tax_transcript_data(applicant_id: str, tax_year: int) -> str:
    """Return tax transcript summary as JSON string."""
    logger.info("Tax transcript request", applicant_id=applicant_id, tax_year=tax_year, component="mcp_server")
    result = await service.get_tax_transcript_data(applicant_id, tax_year)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="verify_asset_information")
async def verify_asset_information(asset_type: str, asset_details_json: str) -> str:
    """Return asset verification results as JSON string."""
    logger.info("Asset verification request", asset_type=asset_type, component="mcp_server")
    try:
        asset_details = json.loads(asset_details_json) if asset_details_json else {}
    except json.JSONDecodeError:
        asset_details = {"raw": asset_details_json}
    result = await service.verify_asset_information(asset_type, asset_details)
    return json.dumps(result)


@mcp.tool()
async def application_verification_health_check() -> str:
    """Health check endpoint for application verification service."""
    from datetime import datetime, timezone

    return json.dumps(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "application_verification",
            "version": "1.0.0",
            "port": 8010,
        }
    )


if __name__ == "__main__":
    # Default to SSE transport as recommended by architect
    transport = "sse"
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        transport = "stdio"  # Allow stdio override for development

    if transport == "sse":
        logger.info(
            "Starting Application Verification MCP Server",
            transport="sse",
            url="http://localhost:8010/sse",
            component="mcp_server",
        )
    else:
        logger.info("Starting Application Verification MCP Server", transport="stdio", component="mcp_server")

    mcp.run(transport=transport)
