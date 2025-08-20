"""
Comprehensive tests for Sequential Orchestration Pattern.

Tests sequential agent execution, handoff validation, error handling, and workflow management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

from loan_processing.agents.providers.openai.orchestration.sequential import SequentialPatternExecutor
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext
from loan_processing.models.application import LoanApplication, EmploymentStatus, LoanPurpose


class TestSequentialPatternExecutor:
    """Test the SequentialPatternExecutor functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.mock_agent_registry = MagicMock()
        self.executor = SequentialPatternExecutor(self.mock_agent_registry)
        
        # Create a sample application for testing
        self.sample_application = LoanApplication(
            application_id="LN1234567890",
            applicant_name="Test User",
            applicant_id="12345678-1234-1234-1234-123456789012",
            email="test@example.com",
            phone="2125551234",
            date_of_birth=datetime(1985, 5, 15),
            annual_income=Decimal("100000"),
            loan_amount=Decimal("300000"),
            loan_purpose=LoanPurpose.HOME_PURCHASE,
            loan_term_months=360,
            employment_status=EmploymentStatus.EMPLOYED,
            down_payment=Decimal("60000"),
            existing_debt=Decimal("1000")
        )
        
        self.sample_context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_sequential"
        )

    def test_executor_initialization(self):
        """Test that executor initializes correctly."""
        executor = SequentialPatternExecutor()
        assert executor is not None
        assert executor.handoff_service is not None
        
        # Test with agent registry
        registry = MagicMock()
        executor_with_registry = SequentialPatternExecutor(registry)
        assert executor_with_registry.agent_registry == registry

    @pytest.mark.asyncio
    async def test_execute_simple_sequential_pattern(self):
        """Test execution of a simple sequential pattern."""
        # Mock the agent execution service
        mock_agent_service = AsyncMock()
        self.executor.agent_execution_service = mock_agent_service
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60},
                {"type": "income", "timeout": 60}
            ],
            "handoff_rules": []
        }
        
        await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")
        
        # Verify all agents were executed in order
        assert mock_agent_service.execute_agent.call_count == 3
        
        # Check the call order
        calls = mock_agent_service.execute_agent.call_args_list
        assert calls[0][0][0] == "intake"  # First agent type
        assert calls[1][0][0] == "credit"  # Second agent type
        assert calls[2][0][0] == "income"  # Third agent type

    @pytest.mark.asyncio
    async def test_execute_with_handoff_conditions(self):
        """Test execution with handoff conditions."""
        # Mock the agent execution service
        mock_agent_service = AsyncMock()
        self.executor.agent_execution_service = mock_agent_service
        
        # Mock handoff service to allow handoffs
        self.executor.handoff_service.check_handoff_conditions = MagicMock(return_value=True)
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": [
                {
                    "from": "intake",
                    "to": "credit", 
                    "conditions": ["validation_status == 'COMPLETE'"]
                }
            ]
        }
        
        await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")
        
        # Verify handoff conditions were checked
        self.executor.handoff_service.check_handoff_conditions.assert_called_once()
        
        # Verify both agents executed
        assert mock_agent_service.execute_agent.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_stops_on_failed_handoff(self):
        """Test that execution stops when handoff conditions are not met."""
        # Mock the agent execution service
        mock_agent_service = AsyncMock()
        self.executor.agent_execution_service = mock_agent_service
        
        # Mock handoff service to reject handoffs
        self.executor.handoff_service.check_handoff_conditions = MagicMock(return_value=False)
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60},
                {"type": "income", "timeout": 60}
            ],
            "handoff_rules": [
                {
                    "from": "intake",
                    "to": "credit",
                    "conditions": ["validation_status == 'COMPLETE'"]
                }
            ]
        }
        
        await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")
        
        # Verify only the first agent executed (intake)
        assert mock_agent_service.execute_agent.call_count == 1
        calls = mock_agent_service.execute_agent.call_args_list
        assert calls[0][0][0] == "intake"

    @pytest.mark.asyncio
    async def test_execute_with_audit_logging(self):
        """Test that audit entries are created during execution."""
        # Mock the agent execution service
        mock_agent_service = AsyncMock()
        self.executor.agent_execution_service = mock_agent_service
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": []
        }
        
        # Track audit entries
        initial_audit_count = len(self.sample_context.audit_trail)
        
        await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")
        
        # Verify audit entries were added
        final_audit_count = len(self.sample_context.audit_trail)
        assert final_audit_count > initial_audit_count
        
        # Check for specific audit messages
        audit_messages = self.sample_context.audit_trail
        assert any("Starting sequential execution" in msg for msg in audit_messages)
        assert any("Sequential execution completed" in msg for msg in audit_messages)

    def test_validate_config_valid_sequential(self):
        """Test configuration validation for valid sequential patterns."""
        # Mock the agent registry to avoid registry validation errors
        mock_registry = MagicMock()
        mock_registry.get_agent_info.return_value = {"name": "Test Agent"}
        executor = SequentialPatternExecutor(mock_registry)
        
        valid_config = {
            "name": "test_sequential_pattern",
            "version": "1.0",
            "pattern_type": "sequential", 
            "agents": [
                {
                    "type": "intake", 
                    "name": "Intake Agent",
                    "required": True,
                    "timeout_seconds": 30
                },
                {
                    "type": "credit",
                    "name": "Credit Agent", 
                    "required": True,
                    "timeout_seconds": 60
                }
            ],
            "handoff_rules": [
                {
                    "from": "intake",
                    "to": "credit",
                    "conditions": ["validation_status == 'COMPLETE'"]
                }
            ]
        }
        
        errors = executor.validate_config(valid_config)
        assert len(errors) == 0

    def test_validate_config_wrong_pattern_type(self):
        """Test configuration validation with wrong pattern type."""
        invalid_config = {
            "pattern_type": "parallel",  # Wrong for SequentialPatternExecutor
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ]
        }
        
        errors = self.executor.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("Pattern type must be 'sequential'" in error for error in errors)

    def test_validate_config_insufficient_agents(self):
        """Test configuration validation with insufficient agents."""
        invalid_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30}
            ]  # Only one agent, need at least 2
        }
        
        errors = self.executor.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("at least 2 agents" in error for error in errors)

    def test_validate_config_invalid_handoff_rules(self):
        """Test configuration validation with invalid handoff rules."""
        invalid_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": [
                {
                    # Missing 'from' field
                    "to": "credit",
                    "conditions": ["validation_status == 'COMPLETE'"]
                }
            ]
        }
        
        errors = self.executor.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("missing 'from' field" in error for error in errors)

    def test_validate_config_unknown_agent_in_handoff(self):
        """Test configuration validation with unknown agent in handoff rules."""
        invalid_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": [
                {
                    "from": "nonexistent",  # Unknown agent
                    "to": "credit",
                    "conditions": ["validation_status == 'COMPLETE'"]
                }
            ]
        }
        
        errors = self.executor.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("unknown 'from' agent 'nonexistent'" in error for error in errors)

    def test_validate_config_invalid_handoff_conditions_format(self):
        """Test configuration validation with invalid handoff conditions format."""
        invalid_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": [
                {
                    "from": "intake",
                    "to": "credit",
                    "conditions": "not_a_list"  # Should be a list
                }
            ]
        }
        
        errors = self.executor.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("'conditions' must be a list" in error for error in errors)

    def test_validate_sequential_dependencies_first_agent(self):
        """Test validation of sequential dependencies for first agent."""
        # First agent should not have dependencies
        agents = [
            {"type": "intake", "depends_on": ["credit"]},  # Invalid - first agent has deps
            {"type": "credit", "depends_on": ["intake"]}
        ]
        
        errors = self.executor._validate_sequential_dependencies(agents)
        assert len(errors) > 0
        assert any("First agent 'intake' should not have dependencies" in error for error in errors)

    def test_validate_sequential_dependencies_subsequent_agents(self):
        """Test validation of sequential dependencies for subsequent agents."""
        # Subsequent agents should depend on previous agent
        agents = [
            {"type": "intake"},
            {"type": "credit", "depends_on": ["income"]},  # Invalid - should depend on intake
            {"type": "income", "depends_on": ["credit"]}
        ]
        
        errors = self.executor._validate_sequential_dependencies(agents)
        assert len(errors) > 0
        assert any("should depend on previous agent 'intake'" in error for error in errors)

    def test_validate_handoff_rules_detailed(self):
        """Test detailed handoff rules validation."""
        pattern_config = {
            "agents": [
                {"type": "intake"},
                {"type": "credit"},
                {"type": "income"}
            ]
        }
        
        # Test various invalid handoff rule scenarios
        invalid_rules = [
            {"to": "credit"},  # Missing 'from'
            {"from": "intake"},  # Missing 'to'
            {"from": "unknown", "to": "credit"},  # Unknown 'from' agent
            {"from": "intake", "to": "unknown"},  # Unknown 'to' agent
            {"from": "intake", "to": "credit", "conditions": "not_a_list"},  # Invalid conditions format
            {"from": "intake", "to": "credit", "conditions": [123]},  # Non-string condition
        ]
        
        for rule in invalid_rules:
            errors = self.executor._validate_handoff_rules([rule], pattern_config)
            assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_execution_with_agent_failure(self):
        """Test execution behavior when an agent fails."""
        # Mock the agent execution service to raise an exception
        mock_agent_service = AsyncMock()
        mock_agent_service.execute_agent.side_effect = Exception("Agent execution failed")
        self.executor.agent_execution_service = mock_agent_service
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": []
        }
        
        # Should propagate the exception
        with pytest.raises(Exception, match="Agent execution failed"):
            await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")

    @pytest.mark.asyncio
    async def test_execution_logging(self):
        """Test that appropriate logging occurs during execution."""
        # Mock the agent execution service
        mock_agent_service = AsyncMock()
        self.executor.agent_execution_service = mock_agent_service
        
        pattern_config = {
            "pattern_type": "sequential",
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": []
        }
        
        with patch('loan_processing.agents.providers.openai.orchestration.sequential.logger') as mock_logger:
            await self.executor.execute(pattern_config, self.sample_context, "gpt-3.5-turbo")
            
            # Verify logging calls were made
            assert mock_logger.info.call_count > 0
            
            # Check for specific log messages
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Starting sequential execution" in msg for msg in log_calls)
            assert any("Sequential execution completed" in msg for msg in log_calls)

    def test_config_validation_edge_cases(self):
        """Test configuration validation edge cases."""
        # Empty agents list
        empty_config = {
            "pattern_type": "sequential",
            "agents": []
        }
        errors = self.executor.validate_config(empty_config)
        assert len(errors) > 0
        
        # Missing agents field
        missing_agents_config = {
            "pattern_type": "sequential"
        }
        errors = self.executor.validate_config(missing_agents_config)
        assert len(errors) > 0
        
        # Invalid handoff_rules type
        invalid_handoff_config = {
            "pattern_type": "sequential", 
            "agents": [
                {"type": "intake", "timeout": 30},
                {"type": "credit", "timeout": 60}
            ],
            "handoff_rules": "not_a_list"
        }
        errors = self.executor.validate_config(invalid_handoff_config)
        assert len(errors) > 0
        assert any("'handoff_rules' must be a list" in error for error in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])