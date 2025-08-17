"""
Sequential orchestration pattern executor.

This module implements the sequential execution pattern where agents
process in order, with each agent building on the previous results.
"""

from __future__ import annotations

from typing import Any

from loan_processing.agents.providers.openai.orchestration.base import HandoffValidationService, PatternExecutor
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext


class SequentialPatternExecutor(PatternExecutor):
    """Executor for sequential orchestration patterns."""

    def __init__(self, agent_registry=None):
        """Initialize sequential pattern executor."""
        super().__init__(agent_registry)
        self.handoff_service = HandoffValidationService()

    async def execute(self, pattern_config: dict[str, Any], context: OrchestrationContext, model: str | None) -> None:
        """Execute sequential orchestration pattern."""

        agents = pattern_config.get("agents", [])
        handoff_rules = {rule["from"]: rule for rule in pattern_config.get("handoff_rules", [])}

        context.add_audit_entry(f"Starting sequential execution with {len(agents)} agents")

        for i, agent_config in enumerate(agents):
            agent_type = agent_config["type"]

            # Check if handoff conditions are met (skip for first agent)
            if i > 0:
                previous_agent_type = agents[i - 1]["type"]
                if not self.handoff_service.check_handoff_conditions(handoff_rules, previous_agent_type, context):
                    context.add_audit_entry(f"Handoff conditions not met for {agent_type}, stopping workflow")
                    break

            # Execute agent
            context.add_audit_entry(f"Executing agent: {agent_type}")
            await self.agent_execution_service.execute_agent(agent_type, agent_config, context, model)
            context.add_audit_entry(f"Completed agent: {agent_type}")

        context.add_audit_entry("Sequential execution completed")

    def validate_config(self, pattern_config: dict[str, Any]) -> list[str]:
        """Validate sequential pattern configuration."""
        errors = self._validate_base_config(pattern_config)

        # Validate pattern type
        if pattern_config.get("pattern_type") != "sequential":
            errors.append("Pattern type must be 'sequential' for SequentialPatternExecutor")

        # Validate handoff rules
        if "handoff_rules" in pattern_config:
            handoff_rules = pattern_config["handoff_rules"]
            if not isinstance(handoff_rules, list):
                errors.append("'handoff_rules' must be a list")
            else:
                errors.extend(self._validate_handoff_rules(handoff_rules, pattern_config))

        # Validate sequential-specific requirements
        agents = pattern_config.get("agents", [])
        if len(agents) < 2:
            errors.append("Sequential pattern requires at least 2 agents")

        # Validate agent dependencies for sequential pattern
        errors.extend(self._validate_sequential_dependencies(agents))

        return errors

    def _validate_handoff_rules(self, handoff_rules: list[dict[str, Any]], pattern_config: dict[str, Any]) -> list[str]:
        """Validate handoff rules for sequential pattern."""
        errors = []
        agent_types = {agent["type"] for agent in pattern_config.get("agents", [])}

        for i, rule in enumerate(handoff_rules):
            # Required fields
            if "from" not in rule:
                errors.append(f"Handoff rule {i} missing 'from' field")
                continue
            if "to" not in rule:
                errors.append(f"Handoff rule {i} missing 'to' field")
                continue

            # Validate agent types exist
            from_agent = rule["from"]
            to_agent = rule["to"]

            if from_agent not in agent_types:
                errors.append(f"Handoff rule {i}: unknown 'from' agent '{from_agent}'")
            if to_agent not in agent_types:
                errors.append(f"Handoff rule {i}: unknown 'to' agent '{to_agent}'")

            # Validate conditions format
            if "conditions" in rule:
                conditions = rule["conditions"]
                if not isinstance(conditions, list):
                    errors.append(f"Handoff rule {i}: 'conditions' must be a list")
                else:
                    for j, condition in enumerate(conditions):
                        if not isinstance(condition, str):
                            errors.append(f"Handoff rule {i}, condition {j}: must be a string")

        return errors

    def _validate_sequential_dependencies(self, agents: list[dict[str, Any]]) -> list[str]:
        """Validate that agent dependencies form a valid sequential chain."""
        errors = []

        for i, agent in enumerate(agents):
            agent_type = agent["type"]
            depends_on = agent.get("depends_on", [])

            if i == 0:
                # First agent should not have dependencies
                if depends_on:
                    errors.append(f"First agent '{agent_type}' should not have dependencies")
            else:
                # Subsequent agents should depend on previous agent
                previous_agent = agents[i - 1]["type"]
                if depends_on and previous_agent not in depends_on:
                    errors.append(
                        f"Agent '{agent_type}' should depend on previous agent '{previous_agent}' in sequential pattern"
                    )

        return errors


__all__ = ["SequentialPatternExecutor"]
