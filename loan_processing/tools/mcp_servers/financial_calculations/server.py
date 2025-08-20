"""Financial Calculations MCP Server.

Provides financial calculation tools for loan processing agents.
Uses the FinancialCalculationsService implementation for business logic.
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

from mcp.server.fastmcp import FastMCP

from loan_processing.utils import get_logger, log_execution  # noqa: E402

from .service import FinancialCalculationsServiceImpl

# Initialize logging
logger = get_logger(__name__)

# Create MCP server
mcp = FastMCP("financial-calculations")

# Configure for SSE transport
mcp.settings.host = "localhost"
mcp.settings.port = 8012

# Initialize service implementation
financial_service = FinancialCalculationsServiceImpl()

logger.info(
    "Financial Calculations MCP Server initialized",
    component="mcp_server",
    server_name="financial_calculations",
    port=8012,
)


@mcp.tool()
@log_execution(component="mcp_server", operation="calculate_debt_to_income_ratio")
async def calculate_debt_to_income_ratio(monthly_income: float, monthly_debt_payments: float) -> str:
    """
    Calculate debt-to-income ratio for loan qualification.

    Args:
        monthly_income: Total monthly income
        monthly_debt_payments: Total monthly debt payments

    Returns:
        JSON string with DTI calculation results
    """
    logger.info("DTI calculation request", component="mcp_server")
    result = await financial_service.calculate_debt_to_income_ratio(monthly_income, monthly_debt_payments)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="calculate_loan_affordability")
async def calculate_loan_affordability(
    monthly_income: float, existing_debt: float, loan_amount: float, interest_rate: float, loan_term_months: int
) -> str:
    """
    Calculate loan affordability assessment.

    Args:
        monthly_income: Monthly income amount
        existing_debt: Current monthly debt payments
        loan_amount: Requested loan amount
        interest_rate: Annual interest rate as decimal
        loan_term_months: Loan term in months

    Returns:
        JSON string with affordability assessment
    """
    logger.info("Loan affordability calculation request", component="mcp_server")
    result = await financial_service.calculate_loan_affordability(
        monthly_income, existing_debt, loan_amount, interest_rate, loan_term_months
    )
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="calculate_monthly_payment")
async def calculate_monthly_payment(
    loan_amount: float, interest_rate: float, loan_term_months: int, payment_type: str = "principal_and_interest"
) -> str:
    """
    Calculate monthly payment for a loan.

    Args:
        loan_amount: Loan principal amount
        interest_rate: Annual interest rate as decimal
        loan_term_months: Loan term in months
        payment_type: Type of payment calculation

    Returns:
        JSON string with payment calculation
    """
    logger.info("Monthly payment calculation request", component="mcp_server")
    result = await financial_service.calculate_monthly_payment(
        loan_amount, interest_rate, loan_term_months, payment_type
    )
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="calculate_credit_utilization_ratio")
async def calculate_credit_utilization_ratio(total_credit_used: float, total_credit_available: float) -> str:
    """
    Calculate credit utilization ratio.

    Args:
        total_credit_used: Current total credit balances
        total_credit_available: Total available credit limits

    Returns:
        JSON string with utilization calculation
    """
    logger.info(
        "Credit utilization calculation request",
        total_credit_used=total_credit_used,
        total_credit_available=total_credit_available,
        component="mcp_server",
    )
    result = await financial_service.calculate_credit_utilization_ratio(total_credit_used, total_credit_available)
    return json.dumps(result)


@mcp.tool()
@log_execution(component="mcp_server", operation="calculate_total_debt_service_ratio")
async def calculate_total_debt_service_ratio(
    monthly_income: float,
    total_monthly_debt: float,
    property_taxes: float = 0,
    insurance: float = 0,
    hoa_fees: float = 0,
) -> str:
    """
    Calculate total debt service ratio including housing expenses.

    Args:
        monthly_income: Total monthly income
        total_monthly_debt: All monthly debt obligations
        property_taxes: Monthly property taxes
        insurance: Monthly insurance payments
        hoa_fees: Monthly HOA fees

    Returns:
        JSON string with TDSR calculation
    """
    logger.info(
        "TDSR calculation request",
        monthly_income=monthly_income,
        total_monthly_debt=total_monthly_debt,
        component="mcp_server",
    )
    result = await financial_service.calculate_total_debt_service_ratio(
        monthly_income, total_monthly_debt, property_taxes, insurance, hoa_fees
    )
    return json.dumps(result)


@mcp.tool()
async def financial_calculations_health_check() -> str:
    """Health check endpoint for financial calculations service."""
    from datetime import datetime, timezone

    return json.dumps(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": "financial_calculations",
            "version": "1.0.0",
            "port": 8012,
        }
    )


if __name__ == "__main__":
    # Default to SSE transport as recommended by architect
    transport = "sse"
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        transport = "stdio"  # Allow stdio override for development

    if transport == "sse":
        logger.info(
            "Starting Financial Calculations MCP Server",
            transport="sse",
            url="http://localhost:8012/sse",
            component="mcp_server",
        )
    else:
        logger.info("Starting Financial Calculations MCP Server", transport="stdio", component="mcp_server")

    mcp.run(transport=transport)
