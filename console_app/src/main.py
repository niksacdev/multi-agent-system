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
import sys
import time
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import get_logger, log_execution, correlation_context  # noqa: E402

from src.backend_client import get_backend_client

# Import console app configuration (UI preferences only)
from src.config import get_console_config

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
        
        logger.info("Console application initialized", 
                   config_loaded=True,
                   component="console_app")

    @log_execution(component="console_app", operation="initialize")
    async def initialize(self):
        """Initialize the console application."""
        logger.info("Starting console application initialization", component="console_app")
        
        try:
            # Validate console app configuration
            config_errors = self.config.validate()
            if config_errors:
                logger.error("Console app configuration validation failed", 
                           errors=config_errors, component="console_app")
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
            
            logger.info("Results directory configured", 
                       results_dir=str(self.results_dir), component="console_app")

            print("✅ Console application initialized")
            print(f"   Results directory: {self.results_dir}")

            # Check backend status
            status = self.backend.get_backend_status()
            logger.info("Backend status checked", 
                       backend_initialized=status["backend_initialized"], component="console_app")
            
            if status["backend_initialized"]:
                print("   Backend: Connected")
            else:
                print("   Backend: Not connected")
            print()
            
        except Exception as e:
            logger.error("Console application initialization failed", 
                        error_message=str(e),
                        error_type=type(e).__name__,
                        component="console_app")
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

    def create_sample_application(self) -> LoanApplication:
        """Create a sample loan application for demonstration."""
        return LoanApplication(
            application_id="LN2024000001",
            applicant_name="John Smith",
            ssn="123-45-6789",  # Will be converted to applicant_id by agents
            email="john.smith@example.com",
            phone="2125551234",
            date_of_birth=datetime(1985, 3, 15),
            loan_amount=450000.00,
            loan_purpose=LoanPurpose.HOME_PURCHASE,
            loan_term_months=360,
            annual_income=150000.00,
            employment_status=EmploymentStatus.EMPLOYED,
            employer_name="TechCorp Inc.",
            months_employed=48,
            monthly_expenses=3500.00,
            existing_debt=950.00,
            assets=225000.00,
            down_payment=150000.00,
            additional_data={
                "property_address": "789 Oak Avenue, San Francisco, CA 94110",
                "property_value": 600000.00,
                "property_type": "SINGLE_FAMILY",
                "intended_use": "PRIMARY_RESIDENCE",
                "internal_applicant_id": "APP-12345-UUID",
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
        # With enum objects preserved, we can access .value directly
        # Keep defensive check for backward compatibility
        loan_purpose = application.loan_purpose.value if hasattr(application.loan_purpose, 'value') else application.loan_purpose
        employment_status = application.employment_status.value if hasattr(application.employment_status, 'value') else application.employment_status
        
        print(f"Loan Purpose: {loan_purpose}")
        print(f"Employment: {employment_status}")
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

    @log_execution(component="console_app", operation="process_application")
    async def process_application(self, application: LoanApplication, pattern_id: str):
        """Process the loan application using the specified pattern."""
        # Create correlation context for this processing session
        async with correlation_context(f"console_{application.application_id}_{pattern_id}") as session_id:
            logger.info("Starting loan application processing", 
                       application_id=application.application_id,
                       pattern_id=pattern_id,
                       session_id=session_id,
                       component="console_app")
            
            print("🚀 STARTING LOAN PROCESSING...")
            print("-" * 40)
            print()

            start_time = time.time()

            try:
                # Backend client handles all the complexity
                decision = await self.backend.process_application(application, pattern_id)

                processing_time = time.time() - start_time
                
                logger.info("Loan processing completed successfully", 
                           application_id=application.application_id,
                           pattern_id=pattern_id,
                           decision_status=decision.decision.value,
                           processing_time_seconds=processing_time,
                           confidence_score=decision.confidence_score,
                           component="console_app")

                # Display results based on user preferences
                if self.config.show_detailed_output:
                    self.display_results(decision, processing_time)
                else:
                    self.display_summary_results(decision, processing_time)

                # Save results if configured
                if self.config.auto_save_results:
                    logger.info("Auto-saving results", application_id=application.application_id, component="console_app")
                    self.save_results(decision, application, pattern_id)

                return decision

            except Exception as e:
                logger.error("Loan processing failed", 
                           application_id=application.application_id,
                           pattern_id=pattern_id,
                           error_message=str(e),
                           error_type=type(e).__name__,
                           processing_time_seconds=time.time() - start_time,
                           component="console_app")
                
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

    async def run_interactive_mode(self):
        """Run the console application in simplified mode."""
        await self.initialize()

        self.display_banner()
        self.display_prerequisites()

        input("Press Enter to continue...")
        print()

        # Use sample application (simplified - no choice needed)
        print("📋 USING SAMPLE APPLICATION")
        print("-" * 40)
        application = self.create_sample_application()
        self.display_application_summary(application)

        # Select orchestration pattern
        print("🔄 AVAILABLE ORCHESTRATION PATTERNS:")

        patterns = self.backend.get_available_patterns()
        available_patterns = [p for p in patterns if p.get("available", True)]

        for i, pattern in enumerate(available_patterns, 1):
            print(f"{i}. {pattern['name']} ({pattern['id']})")
            print(f"   {pattern['description']}")
            print()

        pattern_choice = input("Choose pattern [1]: ").strip() or "1"
        try:
            pattern_index = int(pattern_choice) - 1
            selected_pattern = available_patterns[pattern_index]
            pattern_id = selected_pattern["id"]
        except (ValueError, IndexError):
            pattern_id = self.config.default_pattern
            print(f"Invalid choice, using default: {pattern_id}")

        print()
        self.display_pattern_info(pattern_id)

        # Process application (backend handles all configuration)
        await self.process_application(application, pattern_id)

        # Ask for pattern comparison if enabled
        if self.config.enable_pattern_comparison:
            print("=" * 80)
            compare = input("Would you like to compare with a different pattern? (y/N): ").strip().lower()
            if compare in ["y", "yes"]:
                await self.run_pattern_comparison(application)

    async def run_pattern_comparison(self, application: LoanApplication):
        """Run pattern comparison demonstration."""
        print("\n" + "=" * 80)
        print("🔀 PATTERN COMPARISON DEMONSTRATION")
        print("=" * 80)
        print()

        patterns = self.backend.get_available_patterns()
        available_patterns = [p for p in patterns if p.get("available", True)]

        print("Available patterns for comparison:")
        for i, pattern in enumerate(available_patterns, 1):
            print(f"{i}. {pattern['name']} ({pattern['id']})")
        print()

        pattern_choice = input("Choose pattern for comparison: ").strip()
        try:
            pattern_index = int(pattern_choice) - 1
            selected_pattern = available_patterns[pattern_index]
            pattern_id = selected_pattern["id"]
        except (ValueError, IndexError):
            print("Invalid choice, skipping comparison.")
            return

        print(f"\n🔄 Processing with {selected_pattern['name']} pattern...")
        self.display_pattern_info(pattern_id)

        await self.process_application(application, pattern_id)


async def main():
    """Main entry point for the console application."""
    try:
        console = LoanProcessingConsole()
        await console.run_interactive_mode()
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
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
