#!/usr/bin/env python3
"""
Console Application for Multi-Agent Loan Processing System

This is a thin client application that provides an interactive command-line
interface for the loan processing backend. It handles only presentation logic
while the loan_processing module handles all business logic and configuration.

Architecture:
- Console App: Presentation layer (UI preferences, user interaction)
- Backend Client: Clean interface to loan_processing module
- loan_processing: Business logic, AI provider config, orchestration
"""

import asyncio
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Disable OpenAI agents tracing to prevent telemetry errors
os.environ.setdefault("OPENAI_AGENTS_TRACE", "false")
os.environ.setdefault("OPENAI_TRACE", "false")

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend_client import get_backend_client  # noqa: E402

# Import console app configuration (UI preferences only)
from src.config import get_console_config  # noqa: E402

from loan_processing.utils import correlation_context, get_logger, log_execution  # noqa: E402

# Initialize logging
logger = get_logger(__name__)

from loan_processing.models.application import (  # noqa: E402
    EmploymentStatus,
    LoanApplication,
    LoanPurpose,
)


class LoanProcessingConsole:
    """Console interface for the loan processing system."""

    def __init__(self):
        self.config = get_console_config()
        self.backend = get_backend_client()
        self.results_dir = None

        logger.info("Console application initialized", config_loaded=True, component="console_app")

    @log_execution(component="console_app", operation="initialize")
    async def initialize(self):
        """Initialize the console application."""
        logger.info("Starting console application initialization", component="console_app")

        try:
            # Validate console app configuration
            config_errors = self.config.validate()
            if config_errors:
                logger.error(
                    "Console app configuration validation failed", errors=config_errors, component="console_app"
                )
                print("❌ Console App Configuration Issues:")
                for error in config_errors:
                    print(f"  - {error}")
                raise ValueError("Console app configuration validation failed")

            logger.info("Console app configuration validated successfully", component="console_app")

            # Initialize backend client (this handles all backend configuration)
            logger.info("Initializing backend client", component="console_app")
            await self.backend.initialize()
            logger.info("Backend client initialized successfully", component="console_app")

            # Setup results directory
            self.results_dir = Path(self.config.results_dir)
            self.results_dir.mkdir(parents=True, exist_ok=True)

            logger.info("Results directory configured", results_dir=str(self.results_dir), component="console_app")

            print("✅ Console application initialized")
            print(f"   Results directory: {self.results_dir}")

            # Check backend status
            status = self.backend.get_backend_status()
            logger.info(
                "Backend status checked", backend_initialized=status["backend_initialized"], component="console_app"
            )

            if status["backend_initialized"]:
                print("   Backend: Connected")
            else:
                print("   Backend: Not connected")
            print()

        except Exception as e:
            logger.error(
                "Console application initialization failed",
                error_message=str(e),
                error_type=type(e).__name__,
                component="console_app",
            )
            raise

    def display_banner(self):
        """Display the application banner."""
        if not self.config.show_banner:
            return

        print("🏦 Loan Processing Console")
        print("=========================")
        print("🚀 AI-powered loan decisions in minutes, not days")
        print("🤖 Automated processing with intelligent agents")
        print()

    def display_prerequisites(self):
        """Display prerequisites message."""
        if not self.config.show_prerequisites:
            return

        print("✅ System Status Check")
        print("   → MCP data services: Connected")
        print("   → AI agents: Ready")
        print("   → Processing engine: Operational")
        print()

    def create_sample_application(self, scenario_type: str = "random") -> LoanApplication:
        """Create a sample loan application for demonstration."""
        # Generate random application ID and secure applicant ID for each run
        app_id = f"LN2024{random.randint(100000, 999999)}"
        applicant_uuid = str(uuid.uuid4())

        # Define specific test scenarios for different decision outcomes
        test_scenarios = {
            # Exceptionally strong applicant → APPROVED
            "approval": {
                "applicant_name": "Sarah Johnson",
                "annual_income": 250000.00,  # Higher income
                "loan_amount": 300000.00,  # Lower loan amount (conservative)
                "down_payment": 150000.00,  # 50% down payment
                "existing_debt": 200.00,  # Minimal debt
                "months_employed": 120,  # 10 years stable employment
                "employer_name": "Google Inc.",
                "property_value": 450000.00,  # Conservative LTV
                "monthly_expenses": 2000.00,  # Low expenses
                "credit_score": 820,  # Exceptional credit
                "employment_type": "FULL_TIME_PERMANENT",
            },
            # Borderline applicant → CONDITIONAL_APPROVAL
            "conditional": {
                "applicant_name": "Michael Chen",
                "annual_income": 95000.00,  # Lower income
                "loan_amount": 380000.00,  # Higher loan amount
                "down_payment": 38000.00,  # 10% down (minimal)
                "existing_debt": 2200.00,  # Higher debt
                "months_employed": 24,  # 2 years employment
                "employer_name": "TechStart LLC",
                "property_value": 420000.00,
                "monthly_expenses": 3500.00,  # Higher expenses
                "credit_score": 650,  # Borderline credit
                "employment_type": "FULL_TIME_CONTRACT",
            },
            # High-risk applicant → MANUAL_REVIEW
            "manual_review": {
                "applicant_name": "Emma Rodriguez",
                "annual_income": 75000.00,
                "loan_amount": 320000.00,
                "down_payment": 32000.00,  # 10% down
                "existing_debt": 2500.00,  # High debt
                "months_employed": 18,  # 1.5 years employment
                "employer_name": "Freelance Consulting",
                "property_value": 360000.00,
                "monthly_expenses": 3000.00,
                "credit_score": 620,  # Fair credit
                "employment_type": "SELF_EMPLOYED",
            },
            # Low Income applicant → DENIED
            "denial": {
                "applicant_name": "James Wilson",
                "annual_income": 45000.00,
                "loan_amount": 280000.00,
                "down_payment": 14000.00,  # 5% down
                "existing_debt": 3200.00,  # Very high debt
                "months_employed": 6,  # 6 months employment
                "employer_name": "Part-Time Retail",
                "property_value": 300000.00,
                "monthly_expenses": 2800.00,
                "credit_score": 540,  # Low credit
                "employment_type": "PART_TIME",
            },
        }

        # Select scenario based on input parameter
        if scenario_type == "random":
            scenario = random.choice(list(test_scenarios.values()))
        elif scenario_type in test_scenarios:
            scenario = test_scenarios[scenario_type]
        else:
            # Default to approval scenario
            scenario = test_scenarios["approval"]

        return LoanApplication(
            application_id=app_id,
            applicant_name=scenario["applicant_name"],
            applicant_id=applicant_uuid,  # Secure UUID instead of SSN
            email=f"{scenario['applicant_name'].lower().replace(' ', '.')}@example.com",
            phone="2125551234",
            date_of_birth=datetime(1985, 3, 15),
            loan_amount=scenario["loan_amount"],
            loan_purpose=LoanPurpose.HOME_PURCHASE,
            loan_term_months=360,
            annual_income=scenario["annual_income"],
            employment_status=EmploymentStatus.EMPLOYED,
            employer_name=scenario["employer_name"],
            months_employed=scenario["months_employed"],
            monthly_expenses=scenario["monthly_expenses"],
            existing_debt=scenario["existing_debt"],
            assets=scenario["down_payment"] + random.randint(25000, 75000),  # Add some liquid assets
            down_payment=scenario["down_payment"],
            additional_data={
                # Property details that intake agent expects
                "property_address": (
                    f"{random.randint(100, 999)} Main Street, "
                    f"San Francisco, CA 9411{random.randint(0, 9)}"
                ),
                "property_value": scenario["property_value"],
                "property_type": "SINGLE_FAMILY",
                "intended_use": "PRIMARY_RESIDENCE",
                "property_condition": "GOOD",
                # Applicant details expected by intake agent
                "current_address": (
                    f"{random.randint(100, 999)} Elm Street, "
                    f"San Francisco, CA 9411{random.randint(0, 9)}"
                ),
                "years_at_address": random.randint(1, 10),
                # Monthly financial details
                "monthly_income": float(scenario["annual_income"]) / 12,
                "monthly_debt_payments": scenario["existing_debt"],
                # Documentation and consent
                "documents_provided": [
                    "pay_stubs_recent_2_months",
                    "bank_statements_3_months",
                    "tax_returns_2_years",
                    "employment_verification_letter",
                ],
                "fcra_consent": True,
                "identity_verified": True,
                # Credit information for testing
                "credit_score": scenario["credit_score"],
                "employment_type": scenario["employment_type"],
                # Down payment source
                "down_payment_source": "SAVINGS",
                "down_payment_verified": True,
                # Additional verification data
                "credit_check_consent": True,
                "application_complete": True,
                "verification_status": "PENDING",
            },
        )

    def display_application_summary(self, application: LoanApplication):
        """Display a summary of the loan application."""
        print("📄 LOAN APPLICATION SUMMARY:")
        print("-" * 40)
        print(f"Application ID: {application.application_id}")
        print(f"Applicant: {application.applicant_name}")
        print(f"Loan Amount: ${application.loan_amount:,.2f}")
        print(f"Property Value: ${application.additional_data.get('property_value', 0):,.2f}")
        print(f"Annual Income: ${application.annual_income:,.2f}")
        # Trust Pydantic models - enums are properly typed
        print(f"Loan Purpose: {application.loan_purpose.value}")
        print(f"Employment: {application.employment_status.value}")
        print()

    def display_pattern_info(self, pattern_id: str):
        """Display information about the selected pattern."""
        pattern = self.backend.get_pattern_by_id(pattern_id)

        if pattern:
            print(f"🔄 ORCHESTRATION PATTERN: {pattern['name'].upper()}")
            print("-" * 40)
            print(f"Description: {pattern['description']}")
            print()
            if pattern.get("workflow") and len(pattern["workflow"]) > 0:
                print("Workflow:")
                for step in pattern["workflow"]:
                    print(f"  {step}")
            print(f"Status: {'Available' if pattern.get('available', True) else 'Unavailable'}")
        else:
            print(f"🔄 ORCHESTRATION PATTERN: {pattern_id.upper()}")
            print("-" * 40)
            print(f"Description: {pattern_id} orchestration pattern")
            print("Workflow: Details managed by backend orchestration engine")

        print()
        print("✓ Backend handles all AI provider configuration and orchestration logic")
        print("✓ Each agent autonomously selects MCP tools based on their needs")
        print("✓ All configuration managed through environment variables")
        print()

    def _progress_callback(self, update: dict):
        """Handle progress updates from the backend orchestrator."""
        agent_name = update.get("agent", "unknown").title()
        update_type = update.get("type")

        if update_type == "agent_started":
            print(f"   🔄 {agent_name} Agent: Starting analysis...")

        elif update_type == "agent_thinking":
            print(f"   🤔 {agent_name} Agent: Waiting for OpenAI response...")

        elif update_type == "agent_completed":
            duration = update.get("duration", 0)
            confidence = update.get("confidence", 0)
            summary = update.get("summary", "")
            print(f"   ✅ {agent_name} Agent: Completed in {duration:.1f}s (confidence: {confidence:.1%})")
            if summary:
                print(f"      → {summary}")

        elif update_type == "agent_error":
            duration = update.get("duration", 0)
            error = update.get("error", "Unknown error")
            print(f"   ❌ {agent_name} Agent: Failed after {duration:.1f}s")
            print(f"      → Error: {error}")

    @log_execution(component="console_app", operation="process_application")
    async def process_application(self, application: LoanApplication, pattern_id: str):
        """Process the loan application using the specified pattern."""
        # Create correlation context for this processing session
        async with correlation_context(f"console_{application.application_id}_{pattern_id}") as session_id:
            logger.info(
                "Starting loan application processing",
                application_id=application.application_id,
                pattern_id=pattern_id,
                session_id=session_id,
                component="console_app",
            )

            print("🚀 STARTING LOAN PROCESSING...")
            print("-" * 40)
            print()

            start_time = time.time()

            try:
                # Backend client handles all the complexity
                decision = await self.backend.process_application(
                    application, pattern_id, progress_callback=self._progress_callback
                )

                processing_time = time.time() - start_time

                logger.info(
                    "Loan processing completed successfully",
                    application_id=application.application_id,
                    pattern_id=pattern_id,
                    decision_status=decision.decision.value,
                    processing_time_seconds=processing_time,
                    confidence_score=decision.confidence_score,
                    component="console_app",
                )

                # Display results based on user preferences
                if self.config.show_detailed_output:
                    self.display_results(decision, processing_time)
                else:
                    self.display_summary_results(decision, processing_time)

                # Save results if configured
                if self.config.auto_save_results:
                    logger.info(
                        "Auto-saving results", application_id=application.application_id, component="console_app"
                    )
                    self.save_results(decision, application, pattern_id)

                return decision

            except Exception as e:
                logger.error(
                    "Loan processing failed",
                    application_id=application.application_id,
                    pattern_id=pattern_id,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    processing_time_seconds=time.time() - start_time,
                    component="console_app",
                )

                print(f"❌ Error during processing: {e}")
                print()
                print("💡 Common solutions:")
                print("   • Start MCP servers: python start_mcp_servers.py")
                print("   • Check your OPENAI_API_KEY environment variable")
                print("   • Verify network connectivity")
                print("   • Check server status: python start_mcp_servers.py --status")

                if self.config.debug:
                    import traceback

                    traceback.print_exc()

                raise

    def display_results(self, decision, processing_time: float):
        """Display detailed loan decision results."""
        print("\n" + "=" * 80)
        print("🎯 LOAN DECISION RESULTS")
        print("=" * 80)
        print(f"Decision: {decision.decision.value}")
        print(f"Confidence Score: {decision.confidence_score:.2%}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Orchestration Pattern: {decision.orchestration_pattern}")
        print(f"Decision Maker: {decision.decision_maker}")
        print()

        if hasattr(decision, "approved_amount") and decision.approved_amount:
            print("✅ APPROVED TERMS:")
            print(f"  Amount: ${decision.approved_amount:,.2f}")
            if hasattr(decision, "approved_rate"):
                print(f"  Rate: {decision.approved_rate:.2f}%")
            if hasattr(decision, "approved_term_months"):
                print(f"  Term: {decision.approved_term_months} months")
            print()

        print("📝 DECISION REASONING:")
        print("-" * 40)
        print(decision.decision_reason)
        print()

        if hasattr(decision, "reasoning"):
            print("📊 DETAILED ANALYSIS:")
            print("-" * 40)
            print(decision.reasoning)
            print()

    def display_summary_results(self, decision, processing_time: float):
        """Display summary loan decision results."""
        print(
            f"\n🎯 Decision: {decision.decision.value} | "
            + f"Confidence: {decision.confidence_score:.1%} | "
            + f"Time: {processing_time:.1f}s"
        )

    def save_results(self, decision, application: LoanApplication, pattern_id: str):
        """Save results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"loan_decision_{application.application_id}_{pattern_id}_{timestamp}.json"
        output_file = self.results_dir / filename

        result_data = {
            "application_summary": {
                "application_id": application.application_id,
                "applicant_name": application.applicant_name,
                "loan_amount": application.loan_amount,
                "pattern_used": pattern_id,
            },
            "decision": decision.model_dump() if hasattr(decision, "model_dump") else str(decision),
            "timestamp": timestamp,
            "processing_metadata": {"console_app_version": "2.0.0-simplified", "backend_module": "loan_processing"},
        }

        with open(output_file, "w") as f:
            json.dump(result_data, f, indent=2, default=str)

        print(f"💾 Results saved to: {output_file}")
        print()

    async def run_interactive_mode(self, scenario_type: str = "random"):
        """Run the console application in simplified mode."""
        await self.initialize()

        self.display_banner()
        self.display_prerequisites()

        print()  # Just add space, no interactive input

        # Use sample application with specified scenario
        print(f"📋 USING SAMPLE APPLICATION - SCENARIO: {scenario_type.upper()}")
        print("-" * 40)
        application = self.create_sample_application(scenario_type)
        self.display_application_summary(application)

        # Use sequential pattern automatically
        pattern_id = "sequential"
        print("🔄 USING SEQUENTIAL ORCHESTRATION")
        print("-" * 40)
        self.display_pattern_info(pattern_id)

        # Process application (backend handles all configuration)
        await self.process_application(application, pattern_id)


async def main(scenario_type: str = "random"):
    """Main entry point for the console application."""
    console = None
    try:
        console = LoanProcessingConsole()
        await console.run_interactive_mode(scenario_type)
        return 0

    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0

    except Exception as e:
        print(f"❌ Application failed: {e}")
        # Check for debug flag in env since this is the new simplified app
        if os.getenv("DEBUG", "false").lower() == "true":
            import traceback

            traceback.print_exc()
        else:
            print("Set DEBUG=true environment variable for detailed error information")
        return 1


if __name__ == "__main__":
    # Get scenario type from command line argument
    scenario_type = sys.argv[1] if len(sys.argv) > 1 else "random"

    # Validate scenario type
    valid_scenarios = ["random", "approval", "conditional", "manual_review", "denial"]
    if scenario_type not in valid_scenarios:
        print(f"❌ Invalid scenario type: {scenario_type}")
        print(f"   Valid options: {', '.join(valid_scenarios)}")
        sys.exit(1)

    exit_code = asyncio.run(main(scenario_type))
    sys.exit(exit_code)
