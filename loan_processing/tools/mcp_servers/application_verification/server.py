"""Application Verification MCP Server."""
# ruff: noqa: I001

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .service import ApplicationVerificationServiceImpl

# Create MCP server and configure optional SSE
mcp = FastMCP("application-verification")
mcp.settings.host = "localhost"
mcp.settings.port = 8010

# Initialize service implementation
service = ApplicationVerificationServiceImpl()


@mcp.tool()
async def retrieve_credit_report(applicant_id: str, full_name: str, address: str) -> str:
    """Return a credit report summary as JSON string."""
    result = await service.retrieve_credit_report(applicant_id, full_name, address)
    return json.dumps(result)


@mcp.tool()
async def verify_employment(applicant_id: str, employer_name: str, position: str) -> str:
    """Return employment verification as JSON string."""
    result = await service.verify_employment(applicant_id, employer_name, position)
    return json.dumps(result)


@mcp.tool()
async def get_bank_account_data(account_number: str, routing_number: str) -> str:
    """Return bank account details and balance as JSON string."""
    result = await service.get_bank_account_data(account_number, routing_number)
    return json.dumps(result)


@mcp.tool()
async def get_tax_transcript_data(applicant_id: str, tax_year: int) -> str:
    """Return tax transcript summary as JSON string."""
    result = await service.get_tax_transcript_data(applicant_id, tax_year)
    return json.dumps(result)


@mcp.tool()
async def verify_asset_information(asset_type: str, asset_details_json: str) -> str:
    """Return asset verification results as JSON string."""
    try:
        asset_details = json.loads(asset_details_json) if asset_details_json else {}
    except json.JSONDecodeError:
        asset_details = {"raw": asset_details_json}
    result = await service.verify_asset_information(asset_type, asset_details)
    return json.dumps(result)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        print("Starting Application Verification MCP Server (SSE) at http://localhost:8010/sse")
        mcp.run(transport="sse")
    else:
        print("Starting Application Verification MCP Server (stdio)")
        mcp.run()
