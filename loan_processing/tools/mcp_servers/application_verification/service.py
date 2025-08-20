"""
Application Verification Service Implementation (Mock).

Implements the ApplicationVerificationService interface with mock logic.
The MCP server calls into this service and returns JSON strings to clients.
"""

from __future__ import annotations

import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import get_logger, log_execution  # noqa: E402

from loan_processing.tools.services.application_verification import ApplicationVerificationService

# Initialize logging
logger = get_logger(__name__)


class ApplicationVerificationServiceImpl(ApplicationVerificationService):
    """
    Mock implementation providing deterministic structures with slight
    randomization to simulate real-world variability for demos.
    """

    @log_execution(component="verification_service", operation="retrieve_credit_report")
    async def retrieve_credit_report(self, applicant_id: str, full_name: str, address: str) -> dict[str, Any]:
        logger.info("Retrieving credit report", 
                   applicant_id=applicant_id,
                   component="verification_service")
        
        score = random.randint(620, 780)
        utilization = round(random.uniform(0.15, 0.45), 2)
        payment_history = round(random.uniform(0.85, 0.99), 2)
        inquiries = random.randint(0, 5)
        
        risk_level = "low" if score >= 740 else "medium" if score >= 680 else "high"
        recommendation = "approve" if score >= 700 and utilization <= 0.3 else "review"
        
        logger.info("Credit report generated", 
                   applicant_id=applicant_id,
                   credit_score=score,
                   risk_level=risk_level,
                   recommendation=recommendation,
                   component="verification_service")

        return {
            "applicant_id": applicant_id,
            "full_name": full_name,
            "address": address,
            "credit_score": score,
            "credit_bureau": random.choice(["Experian", "Equifax", "TransUnion"]),
            "credit_utilization": utilization,
            "payment_history_score": payment_history,
            "recent_inquiries": inquiries,
            "delinquencies": random.randint(0, 2),
            "bankruptcies": 0,
            "trade_lines": random.randint(3, 12),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "type": "credit_report",
        }

    @log_execution(component="verification_service", operation="verify_employment")
    async def verify_employment(self, applicant_id: str, employer_name: str, position: str) -> dict[str, Any]:
        logger.info("Verifying employment", 
                   applicant_id=applicant_id,
                   component="verification_service")
        
        income = random.randint(50000, 120000)
        tenure_months = random.randint(6, 60)
        employment_type = random.choice(["full-time", "part-time", "contract"])
        
        verification_status = "verified" if tenure_months >= 12 else "conditional"
        
        logger.info("Employment verification completed", 
                   applicant_id=applicant_id,
                   income=income,
                   tenure_months=tenure_months,
                   verification_status=verification_status,
                   component="verification_service")

        return {
            "applicant_id": applicant_id,
            "employer_name": employer_name,
            "position": position,
            "employment_status": "verified",
            "employment_type": employment_type,
            "annual_income": income,
            "tenure_months": tenure_months,
            "verification_date": datetime.now().isoformat(),
            "hr_contact": f"hr@{employer_name.lower().replace(' ', '')}.com",
            "income_stability": "stable" if tenure_months >= 24 else "developing",
            "recommendation": "verify" if income >= 50000 and employment_type == "full-time" else "review",
            "type": "employment_verification",
        }

    async def get_bank_account_data(self, account_number: str, routing_number: str) -> dict[str, Any]:
        balance = round(random.uniform(500, 25000), 2)

        return {
            "account_number_suffix": account_number[-4:],
            "routing_number": routing_number,
            "current_balance": balance,
            "average_daily_balance": round(balance * random.uniform(0.8, 1.0), 2),
            "owner_verified": True,
            "recent_transactions": [
                {"date": "2025-07-28", "amount": -125.34, "description": "Utility Bill"},
                {"date": "2025-07-22", "amount": -58.12, "description": "Groceries"},
                {"date": "2025-07-15", "amount": 3250.00, "description": "Payroll"},
            ],
            "overdrafts_last_90_days": random.randint(0, 1),
            "type": "bank_account_data",
        }

    async def get_tax_transcript_data(self, applicant_id: str, tax_year: int) -> dict[str, Any]:
        agi = round(random.uniform(55000, 150000), 2)

        return {
            "applicant_id": applicant_id,
            "tax_year": tax_year,
            "adjusted_gross_income": agi,
            "total_income": round(agi * random.uniform(1.0, 1.2), 2),
            "taxable_income": round(agi * random.uniform(0.7, 0.9), 2),
            "withholding": round(agi * random.uniform(0.15, 0.25), 2),
            "refund_or_amount_owed": round(random.uniform(-2500, 2500), 2),
            "filing_status": random.choice(["single", "married_joint", "head_of_household"]),
            "type": "tax_transcript",
        }

    async def verify_asset_information(self, asset_type: str, asset_details: dict[str, Any]) -> dict[str, Any]:
        value = round(random.uniform(10000, 500000), 2)

        return {
            "asset_type": asset_type,
            "asset_details": asset_details,
            "ownership_verified": True,
            "estimated_value": value,
            "liquidity_score": round(random.uniform(0.3, 0.9), 2),
            "lien_check": False,
            "verification_confidence": round(random.uniform(0.75, 0.95), 2),
            "type": "asset_verification",
        }
