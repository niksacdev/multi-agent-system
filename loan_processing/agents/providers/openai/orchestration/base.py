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
from typing import Any

from agents import Runner

from loan_processing.agents.providers.openai.agentregistry import AgentRegistry  # noqa: E402
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext  # noqa: E402


class PatternExecutor(ABC):
    """Abstract base class for all orchestration pattern executors."""

    def __init__(self, agent_registry: AgentRegistry | None = None):
        """Initialize pattern executor with agent registry."""
        self.agent_registry = agent_registry or AgentRegistry()
        self.agent_execution_service = AgentExecutionService(self.agent_registry)

    @abstractmethod
    async def execute(self, pattern_config: dict[str, Any], context: OrchestrationContext, model: str | None) -> None:
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
    def validate_config(self, pattern_config: dict[str, Any]) -> list[str]:
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
            return class_name[: -len("PatternExecutor")].lower()
        return class_name.lower()

    def _validate_base_config(self, pattern_config: dict[str, Any]) -> list[str]:
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
        self, agent_type: str, agent_config: dict[str, Any], context: OrchestrationContext, model: str | None
    ) -> None:
        """Execute a single agent and update context with results."""

        start_time = time.time()
        context.add_audit_entry(f"Starting {agent_type} agent execution")

        # Notify progress callback that agent is starting
        context.notify_agent_start(agent_type)

        try:
            # Create agent instance
            agent = self.agent_registry.create_configured_agent(agent_type, model)

            # Connect MCP servers before execution if not already connected
            for i, mcp_server in enumerate(agent.mcp_servers):
                try:
                    if hasattr(mcp_server, "connect") and not getattr(mcp_server, "_connected", False):
                        context.add_audit_entry(f"Connecting to MCP server {i + 1}...")
                        await mcp_server.connect()
                        mcp_server._connected = True
                        context.add_audit_entry(f"MCP server {i + 1} connected successfully")
                except Exception as e:
                    # Log connection issues with more detail
                    error_msg = f"MCP server {i + 1} connection failed: {str(e)}"
                    context.add_audit_entry(error_msg)
                    # Don't continue - this will cause the agent to fail which is correct behavior
                    raise RuntimeError(f"Cannot execute {agent_type} agent: {error_msg}") from e

            # Prepare input with accumulated context
            agent_input = self._prepare_agent_input(agent_type, context)

            # Execute agent with timeout and progress indication
            timeout = agent_config.get("timeout_seconds", 120)  # 2 minutes default instead of 5
            context.add_audit_entry(f"Sending request to OpenAI for {agent_type} agent...")

            # Notify that agent is waiting for OpenAI response
            context.notify_agent_thinking(agent_type)

            try:
                result = await asyncio.wait_for(Runner.run(agent, input=agent_input), timeout=timeout)
                context.add_audit_entry(f"Received response from OpenAI for {agent_type} agent")
            except asyncio.TimeoutError as e:
                raise RuntimeError(f"{agent_type} agent timed out after {timeout} seconds") from e

            # Parse and store result
            parsed_result = self._parse_agent_result(result)
            duration = time.time() - start_time

            # Debug: log what agent returned
            context.add_audit_entry(f"DEBUG: {agent_type} agent returned: {parsed_result}")

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

            # Notify progress callback of the error
            context.notify_agent_error(agent_type, str(e), duration)

            raise

    def _prepare_agent_input(self, agent_type: str, context: OrchestrationContext) -> str:
        """Prepare optimized input for an agent based on accumulated context."""

        # Build essential context summary for the agent
        context_parts = [
            f"Application Summary:\n{self._create_application_summary(context.application)}",
            f"Session ID: {context.session_id}",
        ]

        # Add relevant previous agent results (summarized, not full)
        if context.intake_result and agent_type != "intake":
            intake_summary = self._summarize_agent_result("intake", context.intake_result)
            context_parts.append(f"Intake Summary: {intake_summary}")

        if context.credit_result and agent_type not in ["intake", "credit"]:
            credit_summary = self._summarize_agent_result("credit", context.credit_result)
            context_parts.append(f"Credit Summary: {credit_summary}")

        if context.income_result and agent_type not in ["intake", "credit", "income"]:
            income_summary = self._summarize_agent_result("income", context.income_result)
            context_parts.append(f"Income Summary: {income_summary}")

        # Add processing instructions
        context_parts.append(
            "Provide structured JSON output as specified. Use secure applicant_id (UUID) for all tool calls."
        )

        return "\n\n".join(context_parts)

    def _create_application_summary(self, application) -> str:
        """Create comprehensive application data for agents - include all available fields."""
        from decimal import Decimal

        # Start with all core application fields
        summary = {
            # Application identification
            "application_id": application.application_id,
            "applicant_name": application.applicant_name,
            "applicant_id": getattr(application, "applicant_id", None),  # Secure UUID identifier
            # Contact information
            "email": getattr(application, "email", None),
            "phone": getattr(application, "phone", None),
            "date_of_birth": application.date_of_birth.isoformat()
            if hasattr(application, "date_of_birth") and application.date_of_birth
            else None,
            # Loan details
            "loan_amount": float(application.loan_amount)
            if isinstance(application.loan_amount, Decimal)
            else application.loan_amount,
            "loan_purpose": application.loan_purpose.value
            if hasattr(application.loan_purpose, "value")
            else application.loan_purpose,
            "loan_term_months": getattr(application, "loan_term_months", None),
            # Financial information
            "annual_income": float(application.annual_income)
            if isinstance(application.annual_income, Decimal)
            else application.annual_income,
            "employment_status": application.employment_status.value
            if hasattr(application.employment_status, "value")
            else application.employment_status,
            "employer_name": getattr(application, "employer_name", None),
            "months_employed": getattr(application, "months_employed", None),
            "monthly_expenses": float(application.monthly_expenses)
            if getattr(application, "monthly_expenses", None) and isinstance(application.monthly_expenses, Decimal)
            else getattr(application, "monthly_expenses", None),
            "existing_debt": float(application.existing_debt)
            if getattr(application, "existing_debt", None) and isinstance(application.existing_debt, Decimal)
            else getattr(application, "existing_debt", None),
            "assets": float(application.assets)
            if getattr(application, "assets", None) and isinstance(application.assets, Decimal)
            else getattr(application, "assets", None),
            "down_payment": float(application.down_payment)
            if getattr(application, "down_payment", None) and isinstance(application.down_payment, Decimal)
            else getattr(application, "down_payment", None),
        }

        # Add all additional_data fields - these often contain required intake data
        if hasattr(application, "additional_data") and application.additional_data:
            for key, value in application.additional_data.items():
                # Convert Decimal values to float for JSON serialization
                if isinstance(value, Decimal):
                    summary[key] = float(value)
                else:
                    summary[key] = value

        # Remove None values to keep payload clean
        summary = {k: v for k, v in summary.items() if v is not None}
        return json.dumps(summary, indent=2)

    def _summarize_agent_result(self, agent_type: str, result: dict[str, Any]) -> str:
        """Create concise summaries of agent results to reduce token usage."""
        if agent_type == "intake":
            summary = {
                "validation_status": result.get("validation_status"),
                "routing_decision": result.get("routing_decision"),
                "confidence_score": result.get("confidence_score"),
                "data_quality_score": result.get("data_quality_score"),
            }
        elif agent_type == "credit":
            summary = {
                "credit_score": result.get("credit_score"),
                "risk_category": result.get("risk_category"),
                "debt_to_income_ratio": result.get("debt_to_income_ratio"),
                "confidence_score": result.get("confidence_score"),
                "recommendation": result.get("recommendation"),
            }
        elif agent_type == "income":
            summary = {
                "qualifying_monthly_income": result.get("qualifying_monthly_income"),
                "employment_stability": result.get("employment_stability"),
                "confidence_score": result.get("confidence_score"),
                "recommendation": result.get("recommendation"),
            }
        else:
            # Default: extract key fields
            summary = {k: v for k, v in result.items() if k in ["confidence_score", "recommendation", "status"]}

        # Remove None values and return compact JSON
        summary = {k: v for k, v in summary.items() if v is not None}
        return json.dumps(summary)

    def _parse_agent_result(self, result: Any) -> dict[str, Any]:
        """Parse agent result into structured data."""

        result_str = str(result)

        # Try to extract JSON from the result
        try:
            # Look for JSON pattern in the result
            import re

            json_match = re.search(r"\{.*\}", result_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Fallback to basic parsing if JSON extraction fails
        return {
            "raw_output": result_str,
            "parsed_successfully": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_success_conditions(self, conditions: list[str], result: dict[str, Any]) -> bool:
        """Validate that agent result meets success conditions."""

        for condition in conditions:
            if not self._evaluate_condition(condition, result):
                return False
        return True

    def _evaluate_condition(self, condition: str, result: dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""

        # Safe condition evaluation without eval()
        try:
            from loan_processing.utils import evaluate_condition

            return evaluate_condition(condition, result)
        except Exception:
            return False


class HandoffValidationService:
    """Service for validating handoff conditions between agents."""

    def __init__(self):
        """Initialize handoff validation service."""
        pass

    def check_handoff_conditions(
        self, handoff_rules: dict[str, Any], from_agent: str, context: OrchestrationContext
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

    def _evaluate_condition(self, condition: str, result: dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""

        # Safe condition evaluation without eval()
        try:
            from loan_processing.utils import evaluate_condition

            return evaluate_condition(condition, result)
        except Exception:
            return False


__all__ = ["PatternExecutor", "AgentExecutionService", "HandoffValidationService"]
