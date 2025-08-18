#!/usr/bin/env python3
"""
Console Application for Multi-Agent Loan Processing System

This is a standalone client application that consumes the loan_processing backend module.
It provides an interactive command-line interface for testing and demonstrating 
the loan processing workflow through different orchestration patterns.

This application is completely decoupled from the loan_processing backend and uses
its own configuration management system.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path for loan_processing imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import configuration from our dedicated console app config system
from config.settings import (
    get_app_config,
    get_available_patterns,
    get_pattern_by_id,
    get_config_loader
)
# Removed complex health checking - keep it simple

# Import loan_processing backend as external dependency
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine
from loan_processing.agents.shared.models.application import (
    EmploymentStatus,
    LoanApplication,
    LoanPurpose,
)


class LoanProcessingConsole:
    """Console interface for the loan processing system."""

    def __init__(self):
        self.config = None
        self.orchestrator = None
        self.results_dir = None

    async def initialize(self):
        """Initialize the console application with configuration."""
        # Load configuration
        self.config = get_app_config()
        
        # Validate configuration
        issues = get_config_loader().validate_configuration()
        if issues:
            print("❌ Configuration Issues Found:")
            for issue in issues:
                print(f"  - {issue}")
            raise ValueError("Configuration validation failed")
        
        # Initialize orchestrator - it will use environment variables for provider config
        # The console app doesn't need to manage provider configuration details
        self.orchestrator = OrchestrationEngine()
        
        # Setup results directory
        self.results_dir = Path(self.config.results_directory)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Console application initialized")
        print(f"   Provider: {self.config.agent_provider.provider_type.value}")
        print(f"   Environment: {self.config.environment}")
        print(f"   Available patterns: {len(self.config.orchestration_patterns)}")
        print()

    def display_banner(self):
        """Display the application banner."""
        print("=" * 80)
        print(f"{self.config.name.upper()}")
        print("=" * 80)
        print("Transform 3-5 day loan processing into 3-5 minute automated decisions")
        print(f"Version: {self.config.version}")
        print(f"Environment: {self.config.environment}")
        print()

    def display_prerequisites(self):
        """Display simple prerequisites message."""
        print("📋 PREREQUISITES:")
        print("Please ensure MCP servers are running on ports 8010-8012")
        print()
        print("Start them in separate terminals:")
        print("  uv run python -m loan_processing.tools.mcp_servers.application_verification.server")
        print("  uv run python -m loan_processing.tools.mcp_servers.document_processing.server") 
        print("  uv run python -m loan_processing.tools.mcp_servers.financial_calculations.server")
        print()
        print("Note: If you get connection errors during processing, check that these services are running.")
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
        print(f"Loan Purpose: {application.loan_purpose.value}")
        print(f"Employment: {application.employment_status.value}")
        print()

    def get_available_patterns(self) -> list[str]:
        """Get list of available orchestration patterns from backend."""
        patterns = get_available_patterns()
        return [pattern["id"] for pattern in patterns]

    def display_pattern_info(self, pattern_id: str):
        """Display information about the selected pattern from backend."""
        pattern = get_pattern_by_id(pattern_id)
        
        if pattern:
            print(f"🔄 ORCHESTRATION PATTERN: {pattern['name'].upper()}")
            print("-" * 40)
            print(f"Description: {pattern['description']}")
            print()
            if pattern.get("workflow") and len(pattern["workflow"]) > 0:
                print("Workflow:")
                for step in pattern["workflow"]:
                    print(f"  {step}")
            else:
                print("Workflow: Details managed by backend orchestration engine")
            print(f"Status: {'Available' if pattern.get('available', True) else 'Unavailable'}")
        else:
            print(f"🔄 ORCHESTRATION PATTERN: {pattern_id.upper()}")
            print("-" * 40)
            print(f"Description: {pattern_id} orchestration pattern")
            print("Workflow: Details managed by backend orchestration engine")
        
        print()
        print("✓ Patterns defined and controlled by backend business logic")
        print("✓ Each agent autonomously selects MCP tools based on their needs")
        print("✓ Orchestrator manages agent execution and context passing")
        print()

    async def process_application(self, application: LoanApplication, pattern_id: str, model: str):
        """Process the loan application using the specified pattern."""
        print(f"🚀 STARTING LOAN PROCESSING...")
        print("-" * 40)
        print()
        
        start_time = time.time()
        
        try:
            decision = await self.orchestrator.execute_pattern(
                pattern_name=pattern_id,
                application=application,
                model=model
            )
            
            processing_time = time.time() - start_time
            
            # Display results
            if self.config.show_detailed_output:
                self.display_results(decision, processing_time)
            else:
                self.display_summary_results(decision, processing_time)
            
            # Save results
            if self.config.auto_save_results:
                self.save_results(decision, application, pattern_id)
            
            return decision
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            print()
            print("💡 Common solutions:")
            print("   • Make sure MCP servers are running (see prerequisites above)")
            print("   • Check your OpenAI API key is valid")
            print("   • Verify network connectivity")
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

        if hasattr(decision, 'approved_amount') and decision.approved_amount:
            print("✅ APPROVED TERMS:")
            print(f"  Amount: ${decision.approved_amount:,.2f}")
            if hasattr(decision, 'approved_rate'):
                print(f"  Rate: {decision.approved_rate:.2f}%")
            if hasattr(decision, 'approved_term_months'):
                print(f"  Term: {decision.approved_term_months} months")
            print()

        print("📝 DECISION REASONING:")
        print("-" * 40)
        print(decision.decision_reason)
        print()

        if hasattr(decision, 'reasoning'):
            print("📊 DETAILED ANALYSIS:")
            print("-" * 40)
            print(decision.reasoning)
            print()

    def display_summary_results(self, decision, processing_time: float):
        """Display summary loan decision results."""
        print(f"\n🎯 Decision: {decision.decision.value} | " +
              f"Confidence: {decision.confidence_score:.1%} | " +
              f"Time: {processing_time:.1f}s")

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
                "pattern_used": pattern_id
            },
            "decision": decision.model_dump() if hasattr(decision, 'model_dump') else str(decision),
            "configuration": {
                "provider_type": self.config.agent_provider.provider_type.value,
                "environment": self.config.environment,
                "version": self.config.version
            }
        }
        
        with open(output_file, "w") as f:
            json.dump(result_data, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        print()

    async def run_interactive_mode(self):
        """Run the console application in interactive mode."""
        await self.initialize()
        
        self.display_banner()
        self.display_prerequisites()
        
        input("Press Enter to continue...")
        print()
        
        # Create or use sample application
        print("📋 APPLICATION OPTIONS:")
        print("1. Use sample application")
        print("2. Create custom application (future feature)")
        print()
        
        choice = input("Choose option [1]: ").strip() or "1"
        
        if choice == "1":
            application = self.create_sample_application()
        else:
            print("Custom application creation coming soon! Using sample application.")
            application = self.create_sample_application()
        
        self.display_application_summary(application)
        
        # Select orchestration pattern from backend
        print("🔄 AVAILABLE ORCHESTRATION PATTERNS:")
        
        patterns_data = get_available_patterns()
        for i, pattern in enumerate(patterns_data, 1):
            print(f"{i}. {pattern['name']} ({pattern['id']})")
            print(f"   {pattern['description']}")
            print(f"   Status: {'✅ Available' if pattern.get('available', True) else '❌ Unavailable'}")
            print()
        
        pattern_choice = input(f"Choose pattern [1]: ").strip() or "1"
        try:
            pattern_index = int(pattern_choice) - 1
            selected_pattern = patterns_data[pattern_index]
            pattern_id = selected_pattern['id']
        except (ValueError, IndexError):
            pattern_id = self.config.orchestration_ui.default_selection
            print(f"Invalid choice, using default: {pattern_id}")
        
        print()
        self.display_pattern_info(pattern_id)
        
        # Model is configured through provider settings, no need for user selection
        provider_config = self.config.agent_provider.get_effective_config()
        model = provider_config.get("model", "gpt-4")  # Get from provider config
        
        print(f"🤖 Using model: {model} (configured via {self.config.agent_provider.provider_type.value})")
        print()
        
        # Process application
        await self.process_application(application, pattern_id, model)
        
        # Ask for pattern comparison
        if self.config.orchestration_ui.enable_comparison:
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
        
        patterns_data = get_available_patterns()
        print("Available patterns for comparison:")
        for i, pattern in enumerate(patterns_data, 1):
            print(f"{i}. {pattern['name']} ({pattern['id']})")
        print()
        
        pattern_choice = input("Choose pattern for comparison: ").strip()
        try:
            pattern_index = int(pattern_choice) - 1
            selected_pattern = patterns_data[pattern_index]
            pattern_id = selected_pattern['id']
        except (ValueError, IndexError):
            print("Invalid choice, skipping comparison.")
            return
        
        print(f"\n🔄 Processing with {selected_pattern['name']} pattern...")
        self.display_pattern_info(pattern_id)
        
        # Use the same model as configured
        provider_config = self.config.agent_provider.get_effective_config()
        model = provider_config.get("model", "gpt-4")
        
        await self.process_application(application, pattern_id, model)


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
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        else:
            print("Use --debug flag for detailed error information")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)