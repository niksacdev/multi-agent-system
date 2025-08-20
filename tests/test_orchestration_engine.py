"""
Comprehensive tests for Orchestration Engine.

Tests the main processing engine, context management, pattern loading, and workflow coordination.
"""

import pytest
import yaml
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from loan_processing.agents.providers.openai.orchestration.engine import (
    OrchestrationContext, 
    ProcessingEngine
)
from loan_processing.models.application import LoanApplication, EmploymentStatus, LoanPurpose
from loan_processing.models.decision import LoanDecision, LoanDecisionStatus


class TestOrchestrationContext:
    """Test the OrchestrationContext functionality."""

    def setup_method(self):
        """Set up test environment."""
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

    def test_context_initialization(self):
        """Test that context initializes correctly."""
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        
        assert context.application == self.sample_application
        assert context.session_id == "test-session-123"
        assert context.pattern_name == "test_pattern"
        assert len(context.audit_trail) == 0
        assert len(context.agent_durations) == 0
        assert len(context.errors) == 0
        assert len(context.metadata) == 0

    def test_add_audit_entry(self):
        """Test adding audit trail entries."""
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        
        context.add_audit_entry("Test audit message")
        
        assert len(context.audit_trail) == 1
        assert "Test audit message" in context.audit_trail[0]
        # Should include timestamp
        assert "[" in context.audit_trail[0]
        assert "]" in context.audit_trail[0]

    def test_set_agent_result(self):
        """Test setting agent results."""
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        
        test_result = {"status": "completed", "confidence": 0.95}
        context.set_agent_result("intake", test_result, 2.5)
        
        assert context.intake_result == test_result
        assert context.agent_durations["intake"] == 2.5

    def test_set_multiple_agent_results(self):
        """Test setting results for multiple agents."""
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        
        # Set results for different agents
        context.set_agent_result("intake", {"status": "complete"}, 1.5)
        context.set_agent_result("credit", {"score": 720}, 3.2)
        context.set_agent_result("income", {"verified": True}, 2.1)
        context.set_agent_result("risk", {"level": "low"}, 1.8)
        
        assert context.intake_result == {"status": "complete"}
        assert context.credit_result == {"score": 720}
        assert context.income_result == {"verified": True}
        assert context.risk_result == {"level": "low"}
        
        assert len(context.agent_durations) == 4
        assert abs(sum(context.agent_durations.values()) - 8.6) < 0.001  # Account for floating point precision

    def test_notify_agent_start(self):
        """Test notifying agent start."""
        callback_calls = []
        
        def test_callback(update):
            callback_calls.append(update)
        
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        context.progress_callback = test_callback
        
        context.notify_agent_start("intake")
        
        assert len(callback_calls) == 1
        assert callback_calls[0]["agent"] == "intake"
        assert callback_calls[0]["type"] == "agent_started"

    def test_notify_agent_thinking(self):
        """Test notifying agent thinking."""
        callback_calls = []
        
        def test_callback(update):
            callback_calls.append(update)
        
        context = OrchestrationContext(
            application=self.sample_application,
            session_id="test-session-123",
            processing_start_time=datetime.now(),
            pattern_name="test_pattern"
        )
        context.progress_callback = test_callback
        
        context.notify_agent_thinking("credit")
        
        assert len(callback_calls) == 1
        assert callback_calls[0]["agent"] == "credit"
        assert callback_calls[0]["type"] == "agent_thinking"


class TestProcessingEngine:
    """Test the ProcessingEngine functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.mock_system_config = MagicMock()
        self.mock_system_config.ai_model = "gpt-3.5-turbo"
        self.mock_system_config.validate.return_value = []
        
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

    def test_engine_initialization(self):
        """Test that engine initializes correctly."""
        with patch('loan_processing.agents.providers.openai.orchestration.engine.AgentRegistry'):
            engine = ProcessingEngine(self.mock_system_config)
            
            assert engine.system_config == self.mock_system_config
            assert engine.pattern_executors is not None
            assert isinstance(engine.pattern_executors, dict)

    @pytest.mark.asyncio
    async def test_execute_pattern_success(self):
        """Test successful pattern execution."""
        # Mock pattern loading
        mock_pattern = {
            "name": "test_pattern",
            "pattern_type": "sequential",
            "version": "1.0",
            "agents": [
                {
                    "type": "intake",
                    "name": "Intake Agent", 
                    "required": True,
                    "timeout_seconds": 30
                }
            ]
        }
        
        # Mock pattern executor
        mock_executor = AsyncMock()
        
        with patch('loan_processing.agents.providers.openai.orchestration.engine.AgentRegistry'), \
             patch.object(ProcessingEngine, '_load_pattern') as mock_load:
            
            mock_load.return_value = mock_pattern
            
            engine = ProcessingEngine(self.mock_system_config)
            # Manually set the executor for testing
            engine.pattern_executors['sequential'] = mock_executor
            
            result = await engine.execute_pattern(
                "sequential",
                self.sample_application,
                "gpt-4"
            )
            
            assert isinstance(result, LoanDecision)
            assert result.application_id == self.sample_application.application_id

    def test_create_configured_engine(self):
        """Test creating a configured engine from environment."""
        mock_config = MagicMock()
        mock_config.validate.return_value = []
        
        with patch('loan_processing.agents.providers.openai.orchestration.engine.get_system_config') as mock_get_config, \
             patch('loan_processing.agents.providers.openai.orchestration.engine.AgentRegistry'):
            
            mock_get_config.return_value = mock_config
            
            engine = ProcessingEngine.create_configured()
            
            assert engine is not None
            assert engine.system_config == mock_config

    def test_create_configured_engine_validation_errors(self):
        """Test creating configured engine with validation errors."""
        mock_config = MagicMock()
        mock_config.validate.return_value = ["Config error 1", "Config error 2"]
        
        with patch('loan_processing.agents.providers.openai.orchestration.engine.get_system_config') as mock_get_config:
            mock_get_config.return_value = mock_config
            
            with pytest.raises(ValueError, match="System configuration errors"):
                ProcessingEngine.create_configured()

    def test_register_executor(self):
        """Test registering a pattern executor."""
        mock_executor = MagicMock()
        mock_executor.get_pattern_type.return_value = "test_pattern"
        
        with patch('loan_processing.agents.providers.openai.orchestration.engine.AgentRegistry'):
            engine = ProcessingEngine(self.mock_system_config)
            engine.register_executor(mock_executor)
            
            assert "test_pattern" in engine.pattern_executors
            assert engine.pattern_executors["test_pattern"] == mock_executor




if __name__ == "__main__":
    pytest.main([__file__, "-v"])