"""
Dynamic Orchestration Engine for Multi-Agent Loan Processing.

This module provides configuration-driven orchestration that can execute
different workflow patterns (sequential, parallel, collaborative) without
requiring changes to agent code.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from loan_processing.agents.shared.models.application import LoanApplication
from loan_processing.agents.shared.models.decision import LoanDecision, LoanDecisionStatus
from loan_processing.agents.providers.openai.agentregistry import AgentRegistry


@dataclass
class OrchestrationContext:
    """Unified context that evolves through the agent workflow."""
    
    application: LoanApplication
    session_id: str
    processing_start_time: datetime
    pattern_name: str
    
    # Agent results accumulate as processing progresses
    intake_result: Optional[Dict[str, Any]] = None
    credit_result: Optional[Dict[str, Any]] = None
    income_result: Optional[Dict[str, Any]] = None
    risk_result: Optional[Dict[str, Any]] = None
    
    # Audit and monitoring data
    audit_trail: List[str] = field(default_factory=list)
    agent_durations: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_audit_entry(self, message: str) -> None:
        """Add entry to audit trail with timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.audit_trail.append(f"[{timestamp}] {message}")
    
    def set_agent_result(self, agent_type: str, result: Dict[str, Any], duration: float) -> None:
        """Set result for a specific agent."""
        setattr(self, f"{agent_type}_result", result)
        self.agent_durations[agent_type] = duration
        self.add_audit_entry(f"{agent_type.title()} agent completed in {duration:.2f}s")


class OrchestrationEngine:
    """Dynamic orchestration engine supporting multiple workflow patterns."""
    
    def __init__(self, patterns_dir: Optional[Path] = None):
        """Initialize the orchestration engine."""
        self.patterns_dir = patterns_dir or Path(__file__).parent.parent.parent / "shared" / "config"
        self.agent_registry = AgentRegistry()
        self._pattern_cache: Dict[str, Dict] = {}
        
        # Initialize pattern executors
        self.pattern_executors: Dict[str, Any] = {}
        self._register_default_executors()
        
    def _register_default_executors(self):
        """Register default pattern executors."""
        # Import here to avoid circular dependencies
        from loan_processing.agents.providers.openai.orchestration.sequential import SequentialPatternExecutor
        from loan_processing.agents.providers.openai.orchestration.parallel import ParallelPatternExecutor
        
        executors = [
            SequentialPatternExecutor(self.agent_registry),
            ParallelPatternExecutor(self.agent_registry),
        ]
        
        for executor in executors:
            self.register_executor(executor)
    
    def register_executor(self, executor: Any):
        """Register a new pattern executor."""
        pattern_type = executor.get_pattern_type()
        self.pattern_executors[pattern_type] = executor
        
    async def execute_pattern(
        self,
        pattern_name: str,
        application: LoanApplication,
        model: str | None = None,
        context_overrides: Optional[Dict[str, Any]] = None
    ) -> LoanDecision:
        """
        Execute a specific orchestration pattern.
        
        Args:
            pattern_name: Name of the pattern to execute (e.g., "sequential", "parallel")
            application: Loan application to process
            model: OpenAI model to use for agents
            context_overrides: Additional context data
            
        Returns:
            Final loan decision
        """
        start_time = datetime.now(timezone.utc)
        
        # Load pattern configuration
        pattern_config = self._load_pattern(pattern_name)
        
        # Create processing context
        context = OrchestrationContext(
            application=application,
            session_id=f"{pattern_name}_{application.application_id}_{int(time.time())}",
            processing_start_time=start_time,
            pattern_name=pattern_name,
            metadata=context_overrides or {}
        )
        
        context.add_audit_entry(f"Started {pattern_name} orchestration for application {application.application_id}")
        
        try:
            # Get and validate executor
            executor = self._get_executor(pattern_config)
            
            # Validate configuration
            config_errors = executor.validate_config(pattern_config)
            if config_errors:
                raise ValueError(f"Configuration errors: {'; '.join(config_errors)}")
            
            # Execute pattern using appropriate executor
            await executor.execute(pattern_config, context, model)
                
            # Generate final decision
            decision = self._generate_loan_decision(pattern_config, context)
            
            context.add_audit_entry(f"Orchestration completed successfully")
            return decision
            
        except Exception as e:
            context.add_audit_entry(f"Orchestration failed: {str(e)}")
            context.errors.append(str(e))
            
            # Generate fallback decision
            return self._generate_error_decision(context, e)
    
    def _get_executor(self, pattern_config: Dict[str, Any]):
        """Get appropriate executor for pattern type."""
        pattern_type = pattern_config.get("pattern_type")
        
        if not pattern_type:
            raise ValueError("Pattern configuration missing 'pattern_type' field")
        
        if pattern_type not in self.pattern_executors:
            available_types = list(self.pattern_executors.keys())
            raise ValueError(f"No executor registered for pattern type: {pattern_type}. Available: {available_types}")
        
        return self.pattern_executors[pattern_type]
    
    def _generate_loan_decision(
        self,
        pattern_config: Dict,
        context: OrchestrationContext
    ) -> LoanDecision:
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
            approved_amount=risk_result.get("approved_amount") if decision_status == LoanDecisionStatus.APPROVED else None,
            approved_rate=risk_result.get("recommended_rate"),
            approved_term_months=risk_result.get("recommended_terms"),
            decision_maker=f"{context.pattern_name}_orchestrator",
            review_priority=self._determine_priority(risk_result),
            reasoning=self._build_decision_reasoning(context),
            processing_duration_seconds=processing_time,
            orchestration_pattern=context.pattern_name,
        )
    
    def _apply_decision_matrix(
        self,
        decision_matrix: Dict,
        context: OrchestrationContext
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
    
    def _evaluate_condition(self, condition: str, result: Dict[str, Any]) -> bool:
        """Evaluate a single condition against agent result."""
        
        # Simple condition evaluation (can be enhanced with more sophisticated logic)
        try:
            # Replace field references with actual values
            for field, value in result.items():
                condition = condition.replace(field, repr(value))
            
            # Evaluate the condition
            return eval(condition)
        except:
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
    
    def _determine_priority(self, risk_result: Dict[str, Any]) -> str:
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
            "Agent Processing Summary:"
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
    
    def _load_pattern(self, pattern_name: str) -> Dict:
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


__all__ = ["OrchestrationEngine", "OrchestrationContext"]