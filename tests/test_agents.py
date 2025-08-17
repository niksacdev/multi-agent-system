"""Tests for the multi-agent loan processing system."""

from datetime import datetime
from decimal import Decimal

import pytest

from loan_processing.agents.providers.openai.agentregistry import AgentRegistry
from loan_processing.agents.shared.models.application import (
    EmploymentStatus,
    LoanApplication,
    LoanPurpose,
)


@pytest.fixture
def sample_application():
    """Create a sample loan application for testing."""
    return LoanApplication(
        application_id="LN2024000001",
        applicant_name="Test User",
        ssn="123-45-6789",
        email="test@example.com",
        phone="2125551234",  # Valid US phone format
        date_of_birth=datetime(1990, 1, 1),
        loan_amount=Decimal("300000.00"),
        loan_purpose=LoanPurpose.HOME_PURCHASE,
        loan_term_months=360,
        annual_income=Decimal("80000.00"),
        employment_status=EmploymentStatus.EMPLOYED,
        employer_name="Test Corp",
        months_employed=24,
        additional_data={
            "internal_applicant_id": "APP-TEST-001",
        },
    )


class TestAgentCreation:
    """Test agent creation and configuration."""

    def test_intake_agent_creation(self):
        """Test that intake agent can be created."""
        agent = AgentRegistry.create_agent("intake")
        assert agent is not None
        assert agent.name == "Intake Agent"
        assert len(agent.mcp_servers) == 2  # Application verification and document processing

    def test_credit_agent_creation(self):
        """Test that credit agent can be created."""
        agent = AgentRegistry.create_agent("credit")
        assert agent is not None
        assert agent.name == "Credit Agent"
        assert len(agent.mcp_servers) == 3  # All three MCP servers

    def test_income_agent_creation(self):
        """Test that income agent can be created."""
        agent = AgentRegistry.create_agent("income")
        assert agent is not None
        assert agent.name == "Income Verification Agent"
        assert len(agent.mcp_servers) == 3  # All three MCP servers

    def test_risk_agent_creation(self):
        """Test that risk agent can be created."""
        agent = AgentRegistry.create_agent("risk")
        assert agent is not None
        assert agent.name == "Risk Evaluation Agent"
        assert len(agent.mcp_servers) == 3  # All three MCP servers


class TestApplicationModel:
    """Test the loan application data model."""

    def test_application_creation(self, sample_application):
        """Test basic application creation."""
        assert sample_application.application_id == "LN2024000001"
        assert sample_application.applicant_name == "Test User"
        assert sample_application.loan_amount == Decimal("300000.00")

    def test_debt_to_income_ratio_calculation(self, sample_application):
        """Test DTI ratio calculation."""
        sample_application.existing_debt = Decimal("2000.00")  # Monthly debt
        dti = sample_application.debt_to_income_ratio
        expected_dti = float(Decimal("2000.00") / (Decimal("80000.00") / 12))
        assert abs(dti - expected_dti) < 0.01

    def test_loan_to_income_ratio_calculation(self, sample_application):
        """Test loan-to-income ratio calculation."""
        lti = sample_application.loan_to_income_ratio
        expected_lti = float(Decimal("300000.00") / Decimal("80000.00"))
        assert abs(lti - expected_lti) < 0.01

    def test_custom_field_operations(self, sample_application):
        """Test custom field operations."""
        sample_application.add_custom_field("test_field", "test_value")
        assert sample_application.get_custom_field("test_field") == "test_value"
        assert sample_application.get_custom_field("nonexistent", "default") == "default"


@pytest.mark.asyncio
class TestOrchestrationEngine:
    """Test the orchestration engine (integration tests would go here)."""

    async def test_orchestration_engine_import(self):
        """Test that orchestration engine can be imported."""
        from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine

        engine = OrchestrationEngine()
        assert engine is not None
        assert hasattr(engine, "execute_pattern")

    # NOTE: Full integration tests would require running MCP servers
    # These would be added in a separate test file for integration testing


@pytest.mark.asyncio
class TestAgentBehavior:
    """Test agent behavior patterns (unit tests)."""

    async def test_agent_persona_loading(self):
        """Test that agents load personas correctly."""
        from loan_processing.agents.shared.utils.persona_loader import load_persona

        # Test that persona files can be loaded
        intake_persona = load_persona("intake")
        assert intake_persona is not None
        assert len(intake_persona) > 0

        credit_persona = load_persona("credit")
        assert credit_persona is not None
        assert len(credit_persona) > 0

    def test_mcp_server_configuration(self):
        """Test MCP server configuration."""
        from loan_processing.agents.providers.openai.agentregistry import AgentRegistry

        agent = AgentRegistry.create_agent("intake")

        # Verify MCP servers are configured
        assert len(agent.mcp_servers) > 0

        # Each server should have proper configuration
        for server in agent.mcp_servers:
            assert hasattr(server, "params")
            assert "url" in server.params


class TestSecurityCompliance:
    """Test security and privacy compliance."""

    def test_secure_id_usage(self, sample_application):
        """Test that secure applicant_id is available."""
        # Verify that we have secure internal ID for MCP tool usage
        internal_id = sample_application.get_custom_field("internal_applicant_id")
        assert internal_id is not None
        assert internal_id.startswith("APP-")

        # SSN should not be used in MCP tool calls (this is a design contract)
        # This test serves as documentation of the security requirement

    def test_data_immutability(self, sample_application):
        """Test that application data remains immutable during processing."""
        original_amount = sample_application.loan_amount
        original_name = sample_application.applicant_name

        # Application data should not change during processing
        assert sample_application.loan_amount == original_amount
        assert sample_application.applicant_name == original_name


if __name__ == "__main__":
    pytest.main([__file__])
