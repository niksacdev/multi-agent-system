#!/usr/bin/env python3
"""
Test script to verify complete agent execution flow.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import get_logger, correlation_context
from console_app.src.backend_client import LoanProcessingBackendClient
from loan_processing.models.application import LoanApplication, LoanPurpose, EmploymentStatus

# Initialize logging
logger = get_logger(__name__)

async def test_agent_execution():
    """Test complete agent execution flow."""
    
    async with correlation_context("agent_execution_test") as session_id:
        logger.info("Starting agent execution test", 
                   session_id=session_id,
                   component="test_agent_execution")
        
        try:
            # Create backend client
            client = LoanProcessingBackendClient()
            await client.initialize()
            
            logger.info("Backend client initialized", 
                       component="test_agent_execution")
            
            # Create test application
            test_application = LoanApplication(
                application_id="LN1234567890",
                applicant_name="John Test Applicant",
                ssn="123-45-6789",
                email="john.test@example.com",
                phone="2125551234",
                date_of_birth=datetime(1985, 5, 15),
                loan_amount=350000.00,
                loan_purpose=LoanPurpose.HOME_PURCHASE,
                loan_term_months=360,
                annual_income=95000.00,
                employment_status=EmploymentStatus.EMPLOYED,
                employer_name="Test Corporation",
                months_employed=36,
                monthly_expenses=2800.00,
                existing_debt=450.00,
                assets=75000.00,
                down_payment=70000.00,
                additional_data={
                    "internal_applicant_id": "APP-TEST-001",
                    "property_address": "123 Test Lane, Test City, TS 12345",
                    "property_value": 420000.00,
                }
            )
            
            logger.info("Test application created", 
                       application_id=test_application.application_id,
                       component="test_agent_execution")
            
            # Process application using sequential pattern
            logger.info("Starting sequential processing", 
                       application_id=test_application.application_id,
                       pattern="sequential",
                       component="test_agent_execution")
            
            decision = await client.process_application(
                application=test_application,
                pattern_id="sequential"
            )
            
            logger.info("Processing completed successfully", 
                       application_id=test_application.application_id,
                       decision_status=decision.decision.value,
                       confidence_score=decision.confidence_score,
                       component="test_agent_execution")
            
            # Display results
            print("\n" + "="*60)
            print("🎉 AGENT EXECUTION TEST COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Application ID: {decision.application_id}")
            print(f"Decision: {decision.decision.value}")
            print(f"Confidence Score: {decision.confidence_score:.2f}")
            print(f"Processing Time: {decision.processing_duration_seconds:.2f}s")
            print(f"Decision Maker: {decision.decision_maker}")
            print(f"Orchestration Pattern: {decision.orchestration_pattern}")
            
            if decision.approved_amount:
                print(f"Approved Amount: ${decision.approved_amount:,.2f}")
            if decision.approved_rate:
                print(f"Approved Rate: {decision.approved_rate:.2f}%")
            if decision.approved_term_months:
                print(f"Approved Term: {decision.approved_term_months} months")
                
            print(f"\nDecision Reason: {decision.decision_reason}")
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error("Agent execution test failed", 
                        error_message=str(e),
                        error_type=type(e).__name__,
                        component="test_agent_execution")
            print(f"\n❌ TEST FAILED: {str(e)}")
            return False

if __name__ == "__main__":
    # Set OpenAI API key if not already set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Use commonly available model
    os.environ["LOAN_PROCESSING_DEFAULT_MODEL"] = "gpt-3.5-turbo"
    
    success = asyncio.run(test_agent_execution())
    sys.exit(0 if success else 1)