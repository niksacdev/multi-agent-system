"""
Tests for the configuration-driven orchestration engine.

Tests the OrchestrationEngine, AgentRegistry, and pattern execution.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from loan_processing.agents.providers.openai.agentregistry import AgentRegistry, MCPServerFactory
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext, OrchestrationEngine
from loan_processing.agents.shared.models.application import (
    EmploymentStatus,
    LoanApplication,
    LoanPurpose,
)
from loan_processing.agents.shared.models.decision import LoanDecision, LoanDecisionStatus


@pytest.fixture
def sample_application():
    """Create a sample loan application for testing."""
    return LoanApplication(
        application_id="LN1234567890",
        applicant_name="Test Applicant",
        ssn="123-45-6789",
        email="test@example.com",
        phone="2125551234",
        date_of_birth=datetime(1985, 1, 1),
        loan_amount=400000.00,
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=120000.00,
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Test Corp",
        months_employed=24,
        monthly_expenses=3000.00,
        existing_debt=800.00,
        assets=180000.00,
        down_payment=120000.00,
        additional_data={
            "internal_applicant_id": "APP-TEST-001",
            "property_address": "123 Test St, Test City, TS 12345",
            "property_value": 500000.00,
        },
    )


@pytest.fixture
def mock_runner():
    """Mock the OpenAI Agents SDK Runner."""
    with patch("loan_processing.agents.providers.openai.orchestration.engine.Runner") as mock:
        # Mock successful agent responses
        mock_responses = {
            "intake": {
                "validation_status": "PASSED",
                "confidence_score": 0.85,
                "data_completeness_score": 0.90,
                "fraud_indicators": [],
                "verification_results": {"identity": True, "address": True},
                "processing_path": "FAST_TRACK",
                "issues_found": [],
            },
            "credit": {
                "credit_score": 720,
                "credit_tier": "GOOD",
                "debt_to_income_ratio": 0.32,
                "credit_utilization_ratio": 0.15,
                "payment_history_score": 0.92,
                "risk_category": "LOW",
                "red_flags": [],
                "confidence_score": 0.88,
            },
            "income": {
                "verified_monthly_income": 10000.00,
                "employment_verification_status": "VERIFIED",
                "employment_stability_score": 0.95,
                "income_trend": "STABLE",
                "income_sources": ["primary_employment"],
                "qualifying_income": 10000.00,
                "concerns": [],
                "confidence_score": 0.92,
            },
            "risk": {
                "final_risk_category": "LOW",
                "recommendation": "APPROVE",
                "approved_amount": 400000.00,
                "recommended_rate": 4.25,
                "recommended_terms": 360,
                "key_risk_factors": [],
                "mitigating_factors": ["stable_income", "good_credit"],
                "conditions": [],
                "reasoning": "Low risk application with stable income",
                "confidence_score": 0.90,
                "compliance_verified": True,
            },
        }

        def mock_run(agent, input=None):
            # Extract agent type from input or use fallback
            agent_type = "intake"  # Default
            if hasattr(agent, "name"):
                name_lower = agent.name.lower()
                if "credit" in name_lower:
                    agent_type = "credit"
                elif "income" in name_lower:
                    agent_type = "income"
                elif "risk" in name_lower:
                    agent_type = "risk"

            response_data = mock_responses.get(agent_type, mock_responses["intake"])
            return AsyncMock(return_value=json.dumps(response_data))()

        mock.run = AsyncMock(side_effect=mock_run)
        yield mock


class TestAgentRegistry:
    """Test the AgentRegistry functionality."""

    def test_create_intake_agent(self):
        """Test creating an intake agent."""
        agent = AgentRegistry.create_agent("intake")

        assert agent.name == "Intake Agent"
        assert agent.instructions is not None
        assert len(agent.mcp_servers) == 2  # application_verification + document_processing
        assert "JSON format" in agent.instructions  # Structured output instructions

    def test_create_credit_agent(self):
        """Test creating a credit agent."""
        agent = AgentRegistry.create_agent("credit", model="gpt-4")

        assert agent.name == "Credit Agent"
        assert agent.model == "gpt-4"
        assert len(agent.mcp_servers) == 3  # All three MCP servers
        assert "credit_score" in agent.instructions

    def test_create_income_agent(self):
        """Test creating an income agent."""
        agent = AgentRegistry.create_agent("income")

        assert agent.name == "Income Verification Agent"
        assert len(agent.mcp_servers) == 3
        assert "employment_verification_status" in agent.instructions

    def test_create_risk_agent(self):
        """Test creating a risk agent."""
        agent = AgentRegistry.create_agent("risk")

        assert agent.name == "Risk Evaluation Agent"
        assert len(agent.mcp_servers) == 3
        assert "final_risk_category" in agent.instructions

    def test_invalid_agent_type(self):
        """Test handling of invalid agent types."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgentRegistry.create_agent("invalid_agent")

    def test_get_agent_info(self):
        """Test getting agent information."""
        info = AgentRegistry.get_agent_info("intake")

        assert info["name"] == "Intake Agent"
        assert info["persona_file"] == "intake"
        assert "application_verification" in info["mcp_servers"]
        assert "Application validation" in info["capabilities"]

    def test_list_agent_types(self):
        """Test listing available agent types."""
        types = AgentRegistry.list_agent_types()

        assert "intake" in types
        assert "credit" in types
        assert "income" in types
        assert "risk" in types
        assert len(types) == 4


class TestMCPServerFactory:
    """Test the MCP server factory."""

    def test_get_server_creates_instance(self):
        """Test that get_server creates server instances."""
        server = MCPServerFactory.get_server("application_verification")
        assert server is not None

    def test_get_server_caches_instances(self):
        """Test that get_server caches server instances."""
        server1 = MCPServerFactory.get_server("financial_calculations")
        server2 = MCPServerFactory.get_server("financial_calculations")
        assert server1 is server2  # Same instance

    def test_invalid_server_type(self):
        """Test handling of invalid server types."""
        with pytest.raises(ValueError, match="Unknown server type"):
            MCPServerFactory.get_server("invalid_server")


class TestOrchestrationContext:
    """Test the OrchestrationContext functionality."""

    def test_context_initialization(self, sample_application):
        """Test context initialization."""
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        assert context.application.application_id == "LN1234567890"
        assert context.session_id == "test-session"
        assert context.pattern_name == "sequential"
        assert context.intake_result is None
        assert len(context.audit_trail) == 0

    def test_add_audit_entry(self, sample_application):
        """Test adding audit entries."""
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        context.add_audit_entry("Test message")

        assert len(context.audit_trail) == 1
        assert "Test message" in context.audit_trail[0]
        assert "[" in context.audit_trail[0]  # Contains timestamp

    def test_set_agent_result(self, sample_application):
        """Test setting agent results."""
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        result = {"status": "completed", "score": 0.85}
        context.set_agent_result("intake", result, 2.5)

        assert context.intake_result == result
        assert context.agent_durations["intake"] == 2.5
        assert len(context.audit_trail) == 1
        assert "Intake agent completed in 2.50s" in context.audit_trail[0]


@pytest.mark.asyncio
class TestOrchestrationEngine:
    """Test the OrchestrationEngine functionality."""

    def test_engine_initialization(self):
        """Test orchestration engine initialization."""
        engine = OrchestrationEngine()

        assert engine.patterns_dir.name == "patterns"
        assert engine.agent_registry is not None
        assert isinstance(engine._pattern_cache, dict)

    async def test_execute_sequential_pattern(self, sample_application, mock_runner):
        """Test executing sequential orchestration pattern."""
        engine = OrchestrationEngine()

        decision = await engine.execute_pattern(
            pattern_name="sequential", application=sample_application, model="gpt-4"
        )

        assert isinstance(decision, LoanDecision)
        assert decision.application_id == "LN1234567890"
        assert decision.orchestration_pattern == "sequential"
        assert decision.decision_maker == "sequential_orchestrator"
        assert decision.processing_duration_seconds > 0

    async def test_execute_parallel_pattern(self, sample_application, mock_runner):
        """Test executing parallel orchestration pattern."""
        engine = OrchestrationEngine()

        decision = await engine.execute_pattern(pattern_name="parallel", application=sample_application, model="gpt-4")

        assert isinstance(decision, LoanDecision)
        assert decision.orchestration_pattern == "parallel"
        assert decision.decision_maker == "parallel_orchestrator"

    async def test_invalid_pattern(self, sample_application):
        """Test handling of invalid pattern names."""
        engine = OrchestrationEngine()

        with pytest.raises(FileNotFoundError):
            await engine.execute_pattern(pattern_name="invalid_pattern", application=sample_application)

    def test_prepare_agent_input(self, sample_application):
        """Test preparing agent input with context."""
        engine = OrchestrationEngine()
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        # Test intake agent input (no previous results)
        intake_input = engine._prepare_agent_input("intake", context)

        assert "Application Data:" in intake_input
        assert sample_application.application_id in intake_input
        assert "Session ID: test-session" in intake_input
        assert "Processing Pattern: sequential" in intake_input

        # Add intake result and test credit agent input
        context.intake_result = {"validation_status": "PASSED", "confidence_score": 0.85}
        credit_input = engine._prepare_agent_input("credit", context)

        assert "Intake Assessment:" in credit_input
        assert "validation_status" in credit_input

    def test_parse_agent_result_json(self):
        """Test parsing JSON agent results."""
        engine = OrchestrationEngine()

        # Test valid JSON result
        json_result = '{"status": "completed", "score": 0.85}'
        parsed = engine._parse_agent_result(json_result)

        assert parsed["status"] == "completed"
        assert parsed["score"] == 0.85
        assert parsed.get("parsed_successfully")

    def test_parse_agent_result_fallback(self):
        """Test parsing non-JSON agent results."""
        engine = OrchestrationEngine()

        # Test non-JSON result
        text_result = "This is not JSON"
        parsed = engine._parse_agent_result(text_result)

        assert parsed["raw_output"] == "This is not JSON"
        assert not parsed["parsed_successfully"]
        assert "timestamp" in parsed

    def test_check_handoff_conditions_success(self, sample_application):
        """Test successful handoff condition checking."""
        engine = OrchestrationEngine()
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        # Set up successful intake result
        context.intake_result = {"validation_status": "PASSED", "confidence_score": 0.85}

        handoff_rules = {"intake": {"conditions": ["validation_status == 'PASSED'", "confidence_score >= 0.8"]}}

        result = engine._check_handoff_conditions(handoff_rules, "intake", context)
        assert result is True

    def test_check_handoff_conditions_failure(self, sample_application):
        """Test failed handoff condition checking."""
        engine = OrchestrationEngine()
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        # Set up failed intake result
        context.intake_result = {"validation_status": "FAILED", "confidence_score": 0.5}

        handoff_rules = {"intake": {"conditions": ["validation_status == 'PASSED'"]}}

        result = engine._check_handoff_conditions(handoff_rules, "intake", context)
        assert result is False

    def test_apply_decision_matrix(self, sample_application):
        """Test applying decision matrix logic."""
        engine = OrchestrationEngine()
        context = OrchestrationContext(
            application=sample_application,
            session_id="test-session",
            processing_start_time=datetime.now(),
            pattern_name="sequential",
        )

        # Set up results for auto-approval
        context.risk_result = {
            "final_risk_category": "LOW",
            "credit_score": 760,
            "debt_to_income_ratio": 0.25,
            "employment_verification_status": "VERIFIED",
            "red_flags": [],
        }

        decision_matrix = {
            "auto_approve": {
                "description": "Auto approve",
                "conditions": [
                    "final_risk_category == 'LOW'",
                    "credit_score >= 750",
                    "debt_to_income_ratio <= 0.28",
                    "len(red_flags) == 0",
                ],
            }
        }

        status, reasoning = engine._apply_decision_matrix(decision_matrix, context)

        assert status == LoanDecisionStatus.APPROVED
        assert "Auto approve" in reasoning


@pytest.mark.integration
class TestOrchestrationIntegration:
    """Integration tests for the full orchestration system."""

    @pytest.mark.asyncio
    async def test_full_sequential_workflow(self, sample_application, mock_runner):
        """Test complete sequential workflow from start to finish."""
        engine = OrchestrationEngine()

        # Execute full workflow
        decision = await engine.execute_pattern(
            pattern_name="sequential", application=sample_application, model="gpt-4"
        )

        # Verify decision structure
        assert isinstance(decision, LoanDecision)
        assert decision.application_id == sample_application.application_id
        assert decision.decision in [
            LoanDecisionStatus.APPROVED,
            LoanDecisionStatus.CONDITIONAL_APPROVAL,
            LoanDecisionStatus.MANUAL_REVIEW,
            LoanDecisionStatus.DENIED,
        ]
        assert decision.confidence_score >= 0.0
        assert decision.confidence_score <= 1.0
        assert decision.processing_duration_seconds > 0
        assert decision.orchestration_pattern == "sequential"

        # Verify reasoning contains orchestration information
        assert "Orchestration Pattern: sequential" in decision.reasoning
        assert "Session ID:" in decision.reasoning

    @pytest.mark.asyncio
    async def test_pattern_error_handling(self, sample_application):
        """Test error handling in pattern execution."""
        engine = OrchestrationEngine()

        with patch.object(engine, "_execute_sequential_pattern") as mock_execute:
            mock_execute.side_effect = Exception("Test error")

            decision = await engine.execute_pattern(pattern_name="sequential", application=sample_application)

            # Should return error decision instead of raising
            assert decision.decision == LoanDecisionStatus.MANUAL_REVIEW
            assert "Processing error" in decision.decision_reason
            assert decision.confidence_score == 0.0
            assert "Test error" in decision.reasoning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
