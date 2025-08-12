"""Sequential loan processing orchestration using OpenAI Agents SDK.

This orchestrator demonstrates the autonomous agent approach where agents
decide which tools to use based on their assessment needs. Each agent has
access to multiple MCP servers and can autonomously select appropriate tools.
"""

from __future__ import annotations

from agents import Runner

from loan_processing.models.application import LoanApplication
from loan_processing.models.decision import LoanDecision, LoanDecisionStatus
from loan_processing.providers.openai.agents.credit import credit_agent


async def process_application_sequential(application: LoanApplication, model: str | None = None) -> LoanDecision:
    """
    Process a loan application using sequential autonomous agents.

    Each agent has access to multiple MCP tool servers and can autonomously
    decide which tools to use based on the specific assessment requirements.

    Args:
        application: The loan application to process
        model: OpenAI model to use (e.g., "gpt-4")

    Returns:
        Final loan decision with all assessments
    """

    # Step 1: Autonomous Credit Assessment
    # Agent has access to: credit service, loan calculator, income verification, risk assessment tools
    credit_agent_instance = credit_agent(model)

    credit_result = await Runner.run(
        credit_agent_instance,
        input=f"""
        Perform comprehensive credit assessment for loan application:

        Application Data:
        {application.model_dump_json(indent=2)}
        
        You have access to multiple tool servers:
        - Application verification tools: retrieve_credit_report, verify_employment,
          get_bank_account_data, get_tax_transcript_data
        - Financial calculation tools: calculate_debt_to_income_ratio,
          calculate_credit_utilization_ratio, analyze_income_stability
        - Document processing tools: extract_text_from_document, validate_document_format
        - Risk assessment tools: assess_loan_risk, analyze_market_conditions
        
        Please autonomously decide which tools to use to provide a complete credit assessment.
        Include your reasoning for tool selection and provide structured results.
        """,
    )

    # Create a loan decision based on the agent's assessment
    # In a full implementation, you might parse the agent's response for specific decisions

    decision = LoanDecision(
        application_id=application.application_id,
        decision=LoanDecisionStatus.APPROVED,  # Mock decision
        decision_reason="Credit assessment completed successfully",
        confidence_score=0.85,
        approved_amount=application.loan_amount,
        approved_rate=4.5,  # Mock rate
        approved_term_months=360,  # 30 years
        decision_maker="autonomous_credit_agent",
        review_priority="standard",
        reasoning=f"Credit agent assessment: {str(credit_result)[:500]}...",  # Truncate for brevity
        processing_duration_seconds=45.0,
        orchestration_pattern="sequential_autonomous",
    )

    return decision
