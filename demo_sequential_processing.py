#!/usr/bin/env python3
"""
Demonstration of the Sequential Multi-Agent Loan Processing System.

This script demonstrates:
1. Starting MCP servers for tool access
2. Creating a sample loan application
3. Processing it through sequential agents (Intake -> Credit -> Income -> Risk)
4. Each agent autonomously selecting MCP tools based on their needs
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from loan_processing.models.application import (
    LoanApplication,
    LoanPurpose,
    EmploymentStatus,
)
from loan_processing.orchestration.engine import OrchestrationEngine


def start_mcp_servers():
    """Start all MCP servers required for loan processing."""
    servers = [
        {
            "name": "Application Verification",
            "port": 8010,
            "module": "mcp_servers.application_verification.server",
        },
        {
            "name": "Document Processing",
            "port": 8011,
            "module": "mcp_servers.document_processing.server",
        },
        {
            "name": "Financial Calculations",
            "port": 8012,
            "module": "mcp_servers.financial_calculations.server",
        },
    ]
    
    processes = []
    for server in servers:
        print(f"Starting {server['name']} server on port {server['port']}...")
        process = subprocess.Popen(
            ["python", "-m", server["module"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(process)
        time.sleep(2)  # Give server time to start
    
    print("All MCP servers started successfully!\n")
    return processes


def create_sample_application() -> LoanApplication:
    """Create a sample loan application for demonstration."""
    return LoanApplication(
        application_id="LN2024000001",  # Following the required pattern
        applicant_name="John Smith",
        ssn="123-45-6789",  # Note: This will be converted to applicant_id by agents
        email="john.smith@example.com",
        phone="2125551234",
        date_of_birth=datetime(1985, 3, 15),
        loan_amount=450000.00,
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=150000.00,
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="TechCorp Inc.",
        months_employed=48,  # 4 years
        monthly_expenses=3500.00,
        existing_debt=950.00,  # Monthly debt payments
        assets=225000.00,  # Total assets
        down_payment=150000.00,
        # Add custom fields for additional data
        additional_data={
            "property_address": "789 Oak Avenue, San Francisco, CA 94110",
            "property_value": 600000.00,
            "property_type": "SINGLE_FAMILY",
            "intended_use": "PRIMARY_RESIDENCE",
            "internal_applicant_id": "APP-12345-UUID",  # Secure internal ID for MCP tools
        },
    )


async def run_demo():
    """Run the sequential processing demonstration."""
    print("=" * 80)
    print("MULTI-AGENT LOAN PROCESSING SYSTEM - CONFIGURATION-DRIVEN ORCHESTRATION DEMO")
    print("=" * 80)
    print()
    
    # Create sample application
    print("Creating sample loan application...")
    application = create_sample_application()
    print(f"Application ID: {application.application_id}")
    print(f"Applicant: {application.applicant_name}")
    print(f"Loan Amount: ${application.loan_amount:,.2f}")
    print(f"Property Value: ${application.additional_data['property_value']:,.2f}")
    print(f"Annual Income: ${application.annual_income:,.2f}")
    print()
    
    # Initialize orchestration engine
    print("Initializing Configuration-Driven Orchestration Engine...")
    orchestrator = OrchestrationEngine()
    print("✓ OrchestrationEngine initialized with pattern configurations")
    print("✓ AgentRegistry loaded with workflow-agnostic agents")
    print()
    
    # Process through sequential pattern
    print("Starting Sequential Pattern Processing...")
    print("-" * 40)
    print()
    
    print("ORCHESTRATION PATTERN: Sequential")
    print("AGENT WORKFLOW (Configuration-Driven):")
    print("1. INTAKE AGENT -> Validates application and checks for fraud")
    print("2. CREDIT AGENT -> Retrieves credit data and calculates DTI")
    print("3. INCOME AGENT -> Verifies employment and income stability")
    print("4. RISK AGENT -> Synthesizes all data and makes final decision")
    print()
    print("✓ No hardcoded handoffs - workflow defined in YAML configuration")
    print("✓ Each agent autonomously selects MCP tools based on their needs")
    print("✓ Orchestrator manages agent execution and context passing")
    print("-" * 40)
    print()
    
    start_time = time.time()
    
    # Process application using sequential pattern
    try:
        decision = await orchestrator.execute_pattern(
            pattern_name="sequential",
            application=application,
            model="gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper processing
        )
        
        processing_time = time.time() - start_time
        
        # Display results
        print("\n" + "=" * 80)
        print("LOAN DECISION RESULTS")
        print("=" * 80)
        print(f"Decision: {decision.decision.value}")
        print(f"Confidence Score: {decision.confidence_score:.2%}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Orchestration Pattern: {decision.orchestration_pattern}")
        print(f"Processing Duration: {decision.processing_duration_seconds:.2f} seconds")
        print(f"Decision Maker: {decision.decision_maker}")
        print()
        
        if decision.approved_amount:
            print("APPROVED TERMS:")
            print(f"  - Amount: ${decision.approved_amount:,.2f}")
            print(f"  - Rate: {decision.approved_rate:.2f}%")
            print(f"  - Term: {decision.approved_term_months} months")
        
        print()
        print("DECISION REASONING:")
        print("-" * 40)
        print(decision.decision_reason)
        print()
        
        print("DETAILED ORCHESTRATION SUMMARY:")
        print("-" * 40)
        print(decision.reasoning)
        
        # Save results
        output_file = Path("demo_results.json")
        with open(output_file, "w") as f:
            json.dump(decision.model_dump(), f, indent=2, default=str)
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"\nError during processing: {e}")
        raise


async def run_pattern_comparison_demo():
    """Demonstrate pattern switching capability."""
    print("\n" + "=" * 80)
    print("PATTERN SWITCHING DEMONSTRATION")
    print("=" * 80)
    print()
    
    application = create_sample_application()
    orchestrator = OrchestrationEngine()
    
    print("The same loan application can be processed using different orchestration patterns:")
    print("✓ Sequential Pattern: Agents process in sequence, each building on the previous")
    print("✓ Parallel Pattern: Credit and Income agents process simultaneously after Intake")
    print()
    
    # Show available patterns
    print("Available orchestration patterns:")
    pattern_files = list(Path("loan_processing/orchestration/patterns").glob("*.yaml"))
    for pattern_file in pattern_files:
        pattern_name = pattern_file.stem
        print(f"  - {pattern_name}.yaml")
    
    print()
    pattern_choice = input("Choose pattern to demonstrate (sequential/parallel) [sequential]: ").strip() or "sequential"
    
    print(f"\nProcessing loan application using '{pattern_choice}' pattern...")
    decision = await orchestrator.execute_pattern(
        pattern_name=pattern_choice,
        application=application,
        model="gpt-4"
    )
    
    print(f"\n✓ Successfully processed using {decision.orchestration_pattern} orchestration")
    print(f"Decision: {decision.decision.value}")
    print(f"Processing Time: {decision.processing_duration_seconds:.2f} seconds")


def main():
    """Main entry point for the demonstration."""
    # Note: In production, MCP servers would be managed separately
    print("Note: Please ensure MCP servers are running on ports 8010-8012")
    print("You can start them with:")
    print("  python -m mcp_servers.application_verification.server")
    print("  python -m mcp_servers.document_processing.server")
    print("  python -m mcp_servers.financial_calculations.server")
    print()
    
    input("Press Enter to continue with the demo...")
    print()
    
    # Run the main demo
    asyncio.run(run_demo())
    
    # Ask if user wants to see pattern switching demo
    print("\n" + "=" * 80)
    show_patterns = input("Would you like to see the pattern switching demonstration? (y/N): ").strip().lower()
    if show_patterns in ['y', 'yes']:
        asyncio.run(run_pattern_comparison_demo())


if __name__ == "__main__":
    main()