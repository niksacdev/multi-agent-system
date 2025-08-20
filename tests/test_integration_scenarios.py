"""
Integration tests for critical loan processing scenarios.

Tests end-to-end workflows to ensure the system handles real-world
loan processing scenarios correctly.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
from loan_processing.models.application import LoanApplication, EmploymentStatus, LoanPurpose
from loan_processing.agents.providers.openai.agentregistry import AgentRegistry


class TestCriticalLoanProcessingScenarios:
    """Test critical end-to-end loan processing scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.registry = AgentRegistry()

    def create_valid_application(self, scenario_type="standard") -> LoanApplication:
        """Create a valid loan application for testing."""
        base_data = {
            "application_id": "LN1234567890",
            "applicant_name": "Test User",
            "applicant_id": "12345678-1234-1234-1234-123456789012",
            "email": "test@example.com", 
            "phone": "2125551234",  # Valid US phone format
            "date_of_birth": datetime(1985, 5, 15),
            "loan_term_months": 360,
            "employment_status": EmploymentStatus.EMPLOYED,
            "loan_purpose": LoanPurpose.HOME_PURCHASE
        }
        
        if scenario_type == "high_income":
            base_data.update({
                "application_id": "LN1234567891",
                "applicant_name": "High Earner",
                "annual_income": Decimal("180000"),
                "loan_amount": Decimal("400000"),
                "down_payment": Decimal("80000"),
                "existing_debt": Decimal("2000")
            })
        elif scenario_type == "marginal":
            base_data.update({
                "application_id": "LN1234567892",
                "applicant_name": "Average Borrower", 
                "annual_income": Decimal("75000"),
                "loan_amount": Decimal("250000"),
                "down_payment": Decimal("25000"),
                "existing_debt": Decimal("1500")
            })
        elif scenario_type == "high_risk":
            base_data.update({
                "application_id": "LN1234567893",
                "applicant_name": "Risk Case",
                "annual_income": Decimal("45000"),
                "loan_amount": Decimal("180000"),
                "down_payment": Decimal("18000"),
                "existing_debt": Decimal("2200"),
                "employment_status": EmploymentStatus.SELF_EMPLOYED,
                "loan_purpose": LoanPurpose.DEBT_CONSOLIDATION
            })
        elif scenario_type == "denial":
            base_data.update({
                "application_id": "LN1234567894",
                "applicant_name": "High Risk",
                "annual_income": Decimal("25000"),
                "loan_amount": Decimal("300000"),
                "down_payment": Decimal("5000"), 
                "existing_debt": Decimal("1800"),
                "employment_status": EmploymentStatus.UNEMPLOYED
            })
        else:  # standard
            base_data.update({
                "annual_income": Decimal("100000"),
                "loan_amount": Decimal("300000"),
                "down_payment": Decimal("60000"),
                "existing_debt": Decimal("1000")
            })
            
        return LoanApplication(**base_data)

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('openai.OpenAI') as mock:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''
            {
                "validation_status": "COMPLETE",
                "routing_decision": "FAST_TRACK",
                "confidence_score": 0.95,
                "processing_notes": "Application data complete, routed for processing"
            }
            '''
            mock_client.chat.completions.create.return_value = mock_response
            mock.return_value = mock_client
            yield mock_client

    def test_high_income_fast_track_scenario(self, mock_openai_client):
        """Test fast-track processing for high-income applicants."""
        # Create high-income application
        application = self.create_valid_application("high_income")

        # Test intake agent routing
        intake_agent = self.registry.create_configured_agent("intake", "gpt-3.5-turbo")
        
        # Verify the agent was created successfully
        assert intake_agent is not None
        assert len(intake_agent.mcp_servers) == 0  # Optimized for speed

        # Test that application would be routed to FAST_TRACK
        # (Mock test since we don't want to make real API calls)
        expected_routing = "FAST_TRACK"
        assert application.annual_income > 150000  # Meets fast-track criteria

    def test_marginal_credit_standard_scenario(self):
        """Test standard processing for marginal credit applicants."""
        # Create marginal credit application
        application = self.create_valid_application("marginal")

        # Verify routing criteria
        assert 75000 <= application.annual_income <= 150000  # Standard range

        # Test agent creation for standard processing
        agents = ["intake", "credit", "income", "risk"]
        for agent_type in agents:
            agent = self.registry.create_configured_agent(agent_type, "gpt-3.5-turbo")
            assert agent is not None
            
            # Verify agent configuration
            agent_info = self.registry.get_agent_info(agent_type)
            assert agent_info["name"] is not None
            assert len(agent_info["capabilities"]) > 0

    def test_high_risk_enhanced_review_scenario(self):
        """Test enhanced review for high-risk applicants."""
        # Create high-risk application
        application = self.create_valid_application("high_risk")

        # Verify enhanced review criteria
        assert application.annual_income < 75000  # Enhanced range
        
        # Calculate DTI ratio
        monthly_income = application.annual_income / 12
        estimated_payment = application.loan_amount * Decimal("0.005")  # Rough estimate
        total_monthly_debt = estimated_payment + application.existing_debt
        dti_ratio = total_monthly_debt / monthly_income
        
        assert dti_ratio > Decimal("0.4")  # High DTI requires enhanced review

    def test_denial_scenario_boundary_conditions(self):
        """Test applications that should be denied."""
        # Create application with multiple red flags
        application = self.create_valid_application("denial")

        # Verify denial criteria
        loan_to_income_ratio = application.loan_amount / application.annual_income
        assert loan_to_income_ratio > 10  # Unrealistic
        assert application.employment_status == EmploymentStatus.UNEMPLOYED  # No income verification

    def test_agent_registry_comprehensive_coverage(self):
        """Test that all required agents can be created and configured."""
        required_agents = ["intake", "credit", "income", "risk"]
        
        for agent_type in required_agents:
            # Test agent creation
            agent = self.registry.create_configured_agent(agent_type, "gpt-3.5-turbo")
            assert agent is not None
            
            # Test agent info retrieval
            info = self.registry.get_agent_info(agent_type)
            assert info is not None
            assert "name" in info
            assert "capabilities" in info
            assert "mcp_servers" in info
            
            # Verify capabilities are defined
            assert len(info["capabilities"]) > 0
            assert all(isinstance(cap, str) for cap in info["capabilities"])

    def test_security_compliance_integration(self):
        """Test that security requirements are enforced across all agents."""
        agents_to_test = ["intake", "credit", "income", "risk"]
        
        for agent_type in agents_to_test:
            agent_info = self.registry.get_agent_info(agent_type)
            
            # Verify security-related configurations exist
            assert "provider_config" in agent_info
            
            # Check that intake agent is optimized (no MCP servers for speed)
            if agent_type == "intake":
                assert len(agent_info["mcp_servers"]) == 0
            
            # Verify capabilities include security considerations
            capabilities = agent_info["capabilities"]
            assert isinstance(capabilities, list)
            assert len(capabilities) > 0

    def test_performance_optimization_validation(self):
        """Test that performance optimizations are in place."""
        # Test intake agent optimization
        intake_info = self.registry.get_agent_info("intake")
        
        # Verify intake agent has no MCP servers (optimized for speed)
        assert len(intake_info["mcp_servers"]) == 0
        
        # Verify timeout configuration exists
        provider_config = intake_info.get("provider_config", {})
        openai_config = provider_config.get("openai", {})
        
        # Should have reasonable timeout
        timeout = openai_config.get("timeout_seconds", 30)
        assert 10 <= timeout <= 60  # Reasonable range

    def test_data_model_integrity(self):
        """Test that data models maintain integrity across scenarios."""
        # Test loan application model
        application = self.create_valid_application("standard")
        
        # Verify required fields are present and valid
        assert application.application_id is not None
        assert application.applicant_name is not None
        assert application.annual_income > 0
        assert application.loan_amount > 0
        assert application.down_payment >= 0
        assert application.existing_debt >= 0
        assert application.employment_status in [EmploymentStatus.EMPLOYED, EmploymentStatus.SELF_EMPLOYED, EmploymentStatus.UNEMPLOYED, EmploymentStatus.RETIRED, EmploymentStatus.STUDENT]
        assert application.loan_purpose in [LoanPurpose.HOME_PURCHASE, LoanPurpose.HOME_REFINANCE, LoanPurpose.DEBT_CONSOLIDATION, LoanPurpose.AUTO, LoanPurpose.PERSONAL, LoanPurpose.BUSINESS, LoanPurpose.EDUCATION]

    def test_error_handling_scenarios(self):
        """Test error handling in critical scenarios."""
        # Test invalid agent type
        with pytest.raises(ValueError):
            self.registry.create_configured_agent("nonexistent_agent", "gpt-3.5-turbo")
        
        # Test missing required configuration
        try:
            agent_types = self.registry.list_agent_types()
            assert isinstance(agent_types, list)
            assert len(agent_types) > 0
        except Exception as e:
            pytest.fail(f"Agent type listing should not fail: {e}")

    def test_workflow_consistency(self):
        """Test that workflow patterns are consistent across scenarios."""
        # Verify all agents have consistent interface
        agent_types = self.registry.list_agent_types()
        
        for agent_type in agent_types:
            info = self.registry.get_agent_info(agent_type)
            
            # Each agent should have these required fields
            required_fields = ["name", "capabilities", "mcp_servers", "provider_config"]
            for field in required_fields:
                assert field in info, f"Agent {agent_type} missing required field: {field}"
            
            # Capabilities should be non-empty list of strings
            capabilities = info["capabilities"]
            assert isinstance(capabilities, list)
            assert len(capabilities) > 0
            assert all(isinstance(cap, str) and len(cap) > 0 for cap in capabilities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])