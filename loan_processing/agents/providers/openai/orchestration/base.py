"""
Base classes and interfaces for orchestration pattern executors.

This module provides the abstract base class and shared utilities
for implementing different orchestration patterns.
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents import Agent, Runner

from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext
from loan_processing.agents.providers.openai.agentregistry import AgentRegistry


class PatternExecutor(ABC):
    """Abstract base class for all orchestration pattern executors."""
    
    def __init__(self, agent_registry: Optional[AgentRegistry] = None):
        """Initialize pattern executor with agent registry."""
        self.agent_registry = agent_registry or AgentRegistry()
        self.agent_execution_service = AgentExecutionService(self.agent_registry)
    
    @abstractmethod
    async def execute(
        self, 
        pattern_config: Dict[str, Any], 
        context: OrchestrationContext, 
        model: str | None
    ) -> None:
        """
        Execute the orchestration pattern with given configuration and context.
        
        Args:
            pattern_config: Pattern configuration from YAML
            context: Orchestration context to accumulate results
            model: OpenAI model to use for agents
            
        Raises:
            ValueError: If pattern configuration is invalid
            RuntimeError: If pattern execution fails
        """
        pass
    
    @abstractmethod
    def validate_config(self, pattern_config: Dict[str, Any]) -> List[str]:
        """
        Validate pattern configuration and return any errors.
        
        Args:
            pattern_config: Pattern configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    def get_pattern_type(self) -> str:
        """Return the pattern type this executor handles."""
        class_name = self.__class__.__name__
        # Convert "SequentialPatternExecutor" -> "sequential"
        if class_name.endswith("PatternExecutor"):
            return class_name[:-len("PatternExecutor")].lower()
        return class_name.lower()
    
    def _validate_base_config(self, pattern_config: Dict[str, Any]) -> List[str]:
        """Validate common configuration fields across all patterns."""
        errors = []
        
        # Required top-level fields
        required_fields = ["name", "pattern_type", "version", "agents"]
        for field in required_fields:
            if field not in pattern_config:
                errors.append(f"Missing required field: {field}")
        
        # Validate agents section
        if "agents" in pattern_config:
            agents = pattern_config["agents"]
            if not isinstance(agents, list) or len(agents) == 0:
                errors.append("'agents' must be a non-empty list")
            else:
                for i, agent in enumerate(agents):
                    if not isinstance(agent, dict):
                        errors.append(f"Agent {i} must be a dictionary")
                        continue
                    
                    # Required agent fields
                    agent_required = ["type", "name", "required", "timeout_seconds"]
                    for field in agent_required:
                        if field not in agent:
                            errors.append(f"Agent {i} missing required field: {field}")
                    
                    # Validate agent type exists
                    if "type" in agent:
                        try:
                            self.agent_registry.get_agent_info(agent["type"])
                        except ValueError:
                            errors.append(f"Unknown agent type: {agent['type']}")
        
        return errors


class AgentExecutionService:
    """Shared service for executing agents across different patterns."""
    
    def __init__(self, agent_registry: AgentRegistry):
        """Initialize with agent registry."""
        self.agent_registry = agent_registry
    
    async def execute_agent(
        self,
        agent_type: str,
        agent_config: Dict[str, Any],
        context: OrchestrationContext,
        model: str | None
    ) -> None:
        """Execute a single agent and update context with results."""
        
        start_time = time.time()
        context.add_audit_entry(f"Starting {agent_type} agent execution")
        
        try:
            # Create agent instance
            agent = self.agent_registry.create_agent(agent_type, model)
            
            # Prepare input with accumulated context
            agent_input = self._prepare_agent_input(agent_type, context)
            
            # Execute agent with timeout
            timeout = agent_config.get("timeout_seconds", 300)
            result = await asyncio.wait_for(
                Runner.run(agent, input=agent_input),
                timeout=timeout
            )
            
            # Parse and store result
            parsed_result = self._parse_agent_result(result)
            duration = time.time() - start_time
            context.set_agent_result(agent_type, parsed_result, duration)
            
            # Validate success conditions
            success_conditions = agent_config.get("success_conditions", [])
            if not self._validate_success_conditions(success_conditions, parsed_result):
                raise ValueError(f"{agent_type} agent did not meet success conditions")
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{agent_type} agent failed after {duration:.2f}s: {str(e)}"
            context.add_audit_entry(error_msg)
            context.errors.append(error_msg)
            raise
    
    def _prepare_agent_input(self, agent_type: str, context: OrchestrationContext) -> str:
        """Prepare input for an agent based on accumulated context."""
        
        # Build context summary for the agent
        context_parts = [
            f"Application Data:\n{context.application.model_dump_json(indent=2)}",
            f"Session ID: {context.session_id}",
            f"Processing Pattern: {context.pattern_name}"
        ]
        
        # Add previous agent results
        if context.intake_result and agent_type != "intake":
            context_parts.append(f"Intake Assessment:\n{json.dumps(context.intake_result, indent=2)}")
        
        if context.credit_result and agent_type not in ["intake", "credit"]:
            context_parts.append(f"Credit Assessment:\n{json.dumps(context.credit_result, indent=2)}")
            
        if context.income_result and agent_type not in ["intake", "credit", "income"]:
            context_parts.append(f"Income Verification:\n{json.dumps(context.income_result, indent=2)}")
        
        # Add processing instructions
        context_parts.append(
            "Focus on your core responsibilities as defined in your persona. "
            "Provide structured JSON output as specified in your instructions. "
            "Use the secure applicant_id from application additional_data for all MCP tool calls."
        )
        
        return "\n\n".join(context_parts)
    
    def _parse_agent_result(self, result: Any) -> Dict[str, Any]:
        """Parse agent result into structured data."""
        
        result_str = str(result)
        
        # Try to extract JSON from the result
        try:
            # Look for JSON pattern in the result
            import re
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback to basic parsing if JSON extraction fails
        return {
            "raw_output": result_str,
            "parsed_successfully": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _validate_success_conditions(self, conditions: List[str], result: Dict[str, Any]) -> bool:
        """Validate that agent result meets success conditions."""
        
        for condition in conditions:
            if not self._evaluate_condition(condition, result):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, result: Dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""
        
        # Safe condition evaluation without eval()
        try:
            from loan_processing.agents.shared.utils import evaluate_condition
            return evaluate_condition(condition, result)
        except Exception:
            return False


class HandoffValidationService:
    """Service for validating handoff conditions between agents."""
    
    def __init__(self):
        """Initialize handoff validation service."""
        pass
    
    def check_handoff_conditions(
        self,
        handoff_rules: Dict[str, Any],
        from_agent: str,
        context: OrchestrationContext
    ) -> bool:
        """Check if handoff conditions are satisfied."""
        
        if from_agent not in handoff_rules:
            return True  # No conditions specified
            
        rule = handoff_rules[from_agent]
        conditions = rule.get("conditions", [])
        
        # Get the result from the previous agent
        agent_result = getattr(context, f"{from_agent}_result", None)
        if not agent_result:
            return False
        
        # Evaluate each condition
        for condition in conditions:
            if not self._evaluate_condition(condition, agent_result):
                return False
                
        return True
    
    def _evaluate_condition(self, condition: str, result: Dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""
        
        # Safe condition evaluation without eval()
        try:
            from loan_processing.agents.shared.utils import evaluate_condition
            return evaluate_condition(condition, result)
        except Exception:
            return False


__all__ = [
    "PatternExecutor",
    "AgentExecutionService", 
    "HandoffValidationService"
]