"""
Processing Engine for Multi-Agent Loan Processing.

This module provides configuration-driven processing that can execute
different workflow patterns (sequential, parallel, collaborative) without
requiring changes to agent code. Agents remain autonomous in tool selection.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loan_processing.agents.providers.openai.agentregistry import AgentRegistry  # noqa: E402
from loan_processing.config.settings import SystemConfig, get_system_config  # noqa: E402
from loan_processing.models.application import LoanApplication  # noqa: E402
from loan_processing.models.decision import LoanDecision, LoanDecisionStatus  # noqa: E402
from loan_processing.utils import correlation_context, get_logger, log_execution  # noqa: E402

# Initialize logging
logger = get_logger(__name__)


@dataclass
class OrchestrationContext:
    """Unified context that evolves through the agent workflow."""

    application: LoanApplication
    session_id: str
    processing_start_time: datetime
    pattern_name: str

    # Agent results accumulate as processing progresses
    intake_result: dict[str, Any] | None = None
    credit_result: dict[str, Any] | None = None
    income_result: dict[str, Any] | None = None
    risk_result: dict[str, Any] | None = None

    # Audit and monitoring data
    audit_trail: list[str] = field(default_factory=list)
    agent_durations: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Progress callback for real-time updates
    progress_callback: Any = field(default=None)

    def add_audit_entry(self, message: str) -> None:
        """Add entry to audit trail with timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.audit_trail.append(f"[{timestamp}] {message}")

    def set_agent_result(self, agent_type: str, result: dict[str, Any], duration: float) -> None:
        """Set result for a specific agent."""
        setattr(self, f"{agent_type}_result", result)
        self.agent_durations[agent_type] = duration
        self.add_audit_entry(f"{agent_type.title()} agent completed in {duration:.2f}s")

        # Notify progress callback if available
        if self.progress_callback:
            try:
                self.progress_callback(
                    {
                        "type": "agent_completed",
                        "agent": agent_type,
                        "duration": duration,
                        "status": "success",
                        "confidence": result.get("confidence_score", 0.0),
                        "summary": self._get_agent_summary(agent_type, result),
                    }
                )
            except Exception:
                pass  # Don't fail processing if callback fails

    def notify_agent_start(self, agent_type: str) -> None:
        """Notify that an agent is starting."""
        if self.progress_callback:
            try:
                self.progress_callback({"type": "agent_started", "agent": agent_type, "status": "processing"})
            except Exception:
                pass

    def notify_agent_thinking(self, agent_type: str) -> None:
        """Notify that an agent is waiting for OpenAI response."""
        if self.progress_callback:
            try:
                self.progress_callback(
                    {"type": "agent_thinking", "agent": agent_type, "status": "waiting_for_response"}
                )
            except Exception:
                pass

    def notify_agent_error(self, agent_type: str, error: str, duration: float) -> None:
        """Notify that an agent failed."""
        if self.progress_callback:
            try:
                self.progress_callback(
                    {
                        "type": "agent_error",
                        "agent": agent_type,
                        "duration": duration,
                        "status": "error",
                        "error": error,
                    }
                )
            except Exception:
                pass

    def _get_agent_summary(self, agent_type: str, result: dict[str, Any]) -> str:
        """Get a brief summary of agent result for progress updates."""
        if agent_type == "intake":
            return f"Validation: {result.get('validation_status', 'Unknown')}"
        elif agent_type == "credit":
            return f"Credit Score: {result.get('credit_score', 'N/A')}, Risk: {result.get('risk_category', 'Unknown')}"
        elif agent_type == "income":
            return f"Income Verified: {result.get('employment_verification_status', 'Unknown')}"
        elif agent_type == "risk":
            return f"Decision: {result.get('recommendation', 'Unknown')}"
        else:
            return f"Status: {result.get('status', 'Completed')}"


class ProcessingEngine:
    """Processing engine supporting multiple workflow patterns with agent autonomy."""

    def __init__(self, system_config: SystemConfig, patterns_dir: Path | None = None):
        """Initialize the processing engine with system configuration."""
        self.system_config = system_config
        self.patterns_dir = patterns_dir or Path(__file__).parent.parent.parent.parent.parent / "config"
        self.agent_registry = AgentRegistry(system_config.ai_model)
        self._pattern_cache: dict[str, dict] = {}

        # Initialize pattern executors
        self.pattern_executors: dict[str, Any] = {}
        self._register_default_executors()

    @classmethod
    def create_configured(cls, patterns_dir: Path | None = None) -> ProcessingEngine:
        """Create a processing engine with system configuration from environment."""
        system_config = get_system_config()

        # Validate configuration
        errors = system_config.validate()
        if errors:
            raise ValueError(f"System configuration errors: {'; '.join(errors)}")

        return cls(system_config, patterns_dir)

    def _register_default_executors(self):
        """Register default pattern executors."""
        # Import here to avoid circular dependencies
        from loan_processing.agents.providers.openai.orchestration.sequential import SequentialPatternExecutor

        # Only register sequential pattern until parallel is fully implemented
        executors = [
            SequentialPatternExecutor(self.agent_registry),
        ]

        for executor in executors:
            self.register_executor(executor)

    def register_executor(self, executor: Any):
        """Register a new pattern executor."""
        pattern_type = executor.get_pattern_type()
        self.pattern_executors[pattern_type] = executor

    @log_execution(component="orchestrator", operation="execute_pattern")
    async def execute_pattern(
        self,
        pattern_name: str,
        application: LoanApplication,
        model: str | None = None,
        context_overrides: dict[str, Any] | None = None,
        progress_callback=None,
    ) -> LoanDecision:
        """
        Execute a specific orchestration pattern.

        Args:
            pattern_name: Name of the pattern to execute (e.g., "sequential", "parallel")
            application: Loan application to process
            model: OpenAI model to use for agents
            context_overrides: Additional context data
            progress_callback: Optional callback for progress updates

        Returns:
            Final loan decision
        """
        start_time = datetime.now(timezone.utc)

        # Create correlation context for this processing session
        async with correlation_context(f"{pattern_name}_{application.application_id}") as session_id:
            logger.info(
                "Starting orchestration pattern execution",
                pattern_name=pattern_name,
                application_id=application.application_id,
                session_id=session_id,
                component="orchestrator",
            )

            # Load pattern configuration
            pattern_config = self._load_pattern(pattern_name)

            # Create processing context
            context = OrchestrationContext(
                application=application,
                session_id=session_id,
                processing_start_time=start_time,
                pattern_name=pattern_name,
                metadata=context_overrides or {},
            )

            # Add progress callback to context
            context.progress_callback = progress_callback

            context.add_audit_entry(
                f"Started {pattern_name} orchestration for application {application.application_id}"
            )

            try:
                # Get and validate executor
                executor = self._get_executor(pattern_config)

                # Validate configuration
                config_errors = executor.validate_config(pattern_config)
                if config_errors:
                    raise ValueError(f"Configuration errors: {'; '.join(config_errors)}")

                logger.info(
                    "Pattern configuration validated",
                    pattern_type=pattern_config.get("pattern_type"),
                    component="orchestrator",
                )

                # Execute pattern using appropriate executor
                await executor.execute(pattern_config, context, model)

                # Generate final decision
                decision = self._generate_loan_decision(pattern_config, context)

                logger.info(
                    "Orchestration completed successfully",
                    decision_status=decision.decision.value,
                    confidence_score=decision.confidence_score,
                    processing_time_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
                    component="orchestrator",
                )

                context.add_audit_entry("Orchestration completed successfully")
                return decision

            except Exception as e:
                logger.error(
                    "Orchestration failed", error_message=str(e), error_type=type(e).__name__, component="orchestrator"
                )

                context.add_audit_entry(f"Orchestration failed: {str(e)}")
                context.errors.append(str(e))

                # Generate fallback decision
                return self._generate_error_decision(context, e)

    def _get_executor(self, pattern_config: dict[str, Any]):
        """Get appropriate executor for pattern type."""
        pattern_type = pattern_config.get("pattern_type")

        if not pattern_type:
            raise ValueError("Pattern configuration missing 'pattern_type' field")

        if pattern_type not in self.pattern_executors:
            available_types = list(self.pattern_executors.keys())
            raise ValueError(f"No executor registered for pattern type: {pattern_type}. Available: {available_types}")

        return self.pattern_executors[pattern_type]

    def _generate_loan_decision(self, pattern_config: dict, context: OrchestrationContext) -> LoanDecision:
        """Generate final loan decision from orchestration results."""

        # Apply decision matrix
        decision_matrix = pattern_config.get("decision_matrix", {})
        decision_status, reasoning = self._apply_decision_matrix(decision_matrix, context)

        # Calculate processing time
        processing_time = (datetime.now(timezone.utc) - context.processing_start_time).total_seconds()

        # Extract decision details from risk result
        risk_result = context.risk_result or {}

        return LoanDecision(
            application_id=context.application.application_id,
            decision=decision_status,
            decision_reason=reasoning[:500],
            confidence_score=risk_result.get("confidence_score", 0.75),
            approved_amount=(
                risk_result.get("approved_amount") if decision_status == LoanDecisionStatus.APPROVED else None
            ),
            approved_rate=(
                risk_result.get("recommended_rate") if decision_status == LoanDecisionStatus.APPROVED else None
            ),
            approved_term_months=(
                risk_result.get("recommended_terms") if decision_status == LoanDecisionStatus.APPROVED else None
            ),
            decision_maker=f"{context.pattern_name}_orchestrator",
            review_priority=self._determine_priority(risk_result),
            reasoning=self._build_decision_reasoning(context),
            processing_duration_seconds=processing_time,
            orchestration_pattern=context.pattern_name,
        )

    def _apply_decision_matrix(
        self, decision_matrix: dict, context: OrchestrationContext
    ) -> tuple[LoanDecisionStatus, str]:
        """Apply decision matrix to determine final decision."""

        # Get all results for evaluation
        all_results = {}
        for agent_type in ["intake", "credit", "income", "risk"]:
            result = getattr(context, f"{agent_type}_result", None)
            if result:
                all_results.update({f"{agent_type}_{k}": v for k, v in result.items()})

        # Check each decision type in order of preference
        for decision_type, config in decision_matrix.items():
            conditions = config.get("conditions", [])
            if all(self._evaluate_condition(cond, all_results) for cond in conditions):
                # Map decision type to status
                status_map = {
                    "auto_approve": LoanDecisionStatus.APPROVED,
                    "conditional_approval": LoanDecisionStatus.CONDITIONAL_APPROVAL,
                    "manual_review": LoanDecisionStatus.MANUAL_REVIEW,
                    "auto_deny": LoanDecisionStatus.DENIED,
                }

                status = status_map.get(decision_type, LoanDecisionStatus.MANUAL_REVIEW)
                reasoning = config.get("description", f"Decision: {decision_type}")

                return status, reasoning

        # Default to manual review
        return LoanDecisionStatus.MANUAL_REVIEW, "No decision matrix conditions matched"

    def _evaluate_condition(self, condition: str, result: dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""

        # Safe condition evaluation without eval()
        try:
            from loan_processing.utils import evaluate_condition

            return evaluate_condition(condition, result)
        except Exception:
            return False

    def _generate_error_decision(self, context: OrchestrationContext, error: Exception) -> LoanDecision:
        """Generate decision when orchestration encounters errors."""

        processing_time = (datetime.now(timezone.utc) - context.processing_start_time).total_seconds()

        return LoanDecision(
            application_id=context.application.application_id,
            decision=LoanDecisionStatus.MANUAL_REVIEW,
            decision_reason=f"Processing error: {str(error)[:200]}",
            confidence_score=0.0,
            approved_amount=None,
            approved_rate=None,
            approved_term_months=None,
            decision_maker=f"{context.pattern_name}_orchestrator_error",
            review_priority="urgent",
            reasoning=self._build_error_reasoning(context, error),
            processing_duration_seconds=processing_time,
            orchestration_pattern=context.pattern_name,
        )

    def _determine_priority(self, risk_result: dict[str, Any]) -> str:
        """Determine review priority from risk assessment."""

        risk_category = risk_result.get("final_risk_category", "MODERATE")
        if risk_category == "VERY_HIGH":
            return "urgent"
        elif risk_category == "HIGH":
            return "high"
        elif risk_category == "LOW":
            return "low"
        else:
            return "standard"

    def _build_decision_reasoning(self, context: OrchestrationContext) -> str:
        """Build comprehensive decision reasoning."""

        reasoning_parts = [
            f"Orchestration Pattern: {context.pattern_name}",
            f"Session ID: {context.session_id}",
            f"Total Processing Time: {sum(context.agent_durations.values()):.2f}s",
            "",
            "Agent Processing Summary:",
        ]

        for agent_type, duration in context.agent_durations.items():
            result = getattr(context, f"{agent_type}_result", {})
            confidence = result.get("confidence_score", 0.0)
            reasoning_parts.append(f"- {agent_type.title()}: {duration:.2f}s (confidence: {confidence:.2f})")

        if context.audit_trail:
            reasoning_parts.extend(["", "Audit Trail:"] + context.audit_trail[-10:])  # Last 10 entries

        return "\n".join(reasoning_parts)

    def _build_error_reasoning(self, context: OrchestrationContext, error: Exception) -> str:
        """Build reasoning for error decisions."""

        return f"""
Orchestration Error Details:
Pattern: {context.pattern_name}
Session: {context.session_id}
Error: {str(error)}

Completed Agents: {list(context.agent_durations.keys())}
Processing Durations: {context.agent_durations}

Audit Trail:
{chr(10).join(context.audit_trail)}

Errors:
{chr(10).join(context.errors)}
"""

    def _load_pattern(self, pattern_name: str) -> dict:
        """Load orchestration pattern configuration."""

        if pattern_name in self._pattern_cache:
            return self._pattern_cache[pattern_name]

        pattern_file = self.patterns_dir / f"{pattern_name}.yaml"

        if not pattern_file.exists():
            raise FileNotFoundError(f"Pattern file not found: {pattern_file}")

        with open(pattern_file) as f:
            pattern_config = yaml.safe_load(f)

        self._pattern_cache[pattern_name] = pattern_config
        return pattern_config


# Backward compatibility alias
OrchestrationEngine = ProcessingEngine

__all__ = ["ProcessingEngine", "OrchestrationEngine", "OrchestrationContext"]
