# ADR-005: Configuration-Driven Orchestration Architecture

**Date**: 2025-08-15  
**Status**: Accepted  
**Authors**: Development Team with System Architecture Reviewer and Code Reviewer

## Context

During the development of our multi-agent loan processing system, a critical architectural issue was identified: agent definitions contained hardcoded handoff configurations that tightly coupled agent capabilities to specific workflow patterns. This violated our persona-driven architecture principles where agents should be pure capability providers.

### Problem Statement

The original implementation had several issues:

1. **Tight Coupling**: Agents had hardcoded `handoff()` calls to specific next agents
2. **Circular Dependencies**: Agent imports created circular dependency chains
3. **Workflow Rigidity**: Switching between orchestration patterns (sequential, parallel, collaborative) required code changes
4. **Violation of Persona-Driven Architecture**: Agent behavior was mixed with workflow orchestration logic

### User Feedback

> "You now have handoff hardcoded for each agent in their agent creation, but should that not be in their persona definition instead? I think tomorrow if we change from a sequential to a parallel pattern then we will have to update the agent code due to handoff hardcodings" - User feedback that triggered this refactor

## Decision

We will implement a **Configuration-Driven Orchestration Architecture** that separates agent capabilities from workflow orchestration through:

### 1. Agent Registry Pattern

- **AgentRegistry**: Centralized factory for creating workflow-agnostic agents
- **MCPServerFactory**: Centralized management of MCP server instances
- **Agents**: Pure capability providers without hardcoded handoffs

### 2. Dynamic Orchestration Engine

- **OrchestrationEngine**: Executes different workflow patterns dynamically
- **OrchestrationContext**: Unified context that evolves through the workflow
- **Pattern Configurations**: YAML files defining workflow behavior

### 3. Configuration-Based Workflows

- **YAML Pattern Files**: Define agent execution order, handoff rules, and decision matrices
- **Pattern Types**: Support for sequential, parallel, and future collaborative patterns
- **Flexible Handoffs**: Condition-based transitions between agents

## Architecture Components

### AgentRegistry (`loan_processing/providers/openai/agents/registry.py`)

```python
class AgentRegistry:
    """Central registry for agent types and configurations."""
    
    @classmethod
    def create_agent(cls, agent_type: str, model: str | None = None) -> Agent:
        """Create a workflow-agnostic agent instance."""
```

**Responsibilities:**
- Agent creation without hardcoded handoffs
- MCP server configuration
- Structured output format definition
- Persona loading and enhancement

### OrchestrationEngine (`loan_processing/orchestration/engine.py`)

```python
class OrchestrationEngine:
    """Dynamic orchestration engine supporting multiple workflow patterns."""
    
    async def execute_pattern(
        self,
        pattern_name: str,
        application: LoanApplication,
        model: str | None = None
    ) -> LoanDecision:
```

**Responsibilities:**
- Pattern loading from YAML configurations
- Agent execution and context management
- Handoff condition evaluation
- Final decision generation

### Pattern Configurations

**Sequential Pattern** (`loan_processing/orchestration/patterns/sequential.yaml`):
```yaml
name: "sequential_loan_processing"
pattern_type: "sequential"
agents:
  - type: "intake"
    timeout_seconds: 180
    success_conditions:
      - "validation_status in ['PASSED', 'REQUIRES_REVIEW']"
handoff_rules:
  - from: "intake"
    to: "credit"
    conditions:
      - "validation_status == 'PASSED'"
```

**Parallel Pattern** (`loan_processing/orchestration/patterns/parallel.yaml`):
```yaml
name: "parallel_loan_processing" 
pattern_type: "parallel"
parallel_branches:
  - branch_name: "credit_branch"
    agents:
      - type: "credit"
        depends_on: ["intake"]
  - branch_name: "income_branch"  
    agents:
      - type: "income"
        depends_on: ["intake"]
```

## Benefits

### 1. **Clean Separation of Concerns**
- Agents focus purely on their domain capabilities
- Orchestration logic is externalized to configuration
- No circular dependencies between agents

### 2. **Pattern Flexibility**
- Switch between orchestration patterns without code changes
- Add new patterns by creating YAML configurations
- Support for complex workflows (parallel, conditional, etc.)

### 3. **Maintainability**
- Agent persona changes don't affect orchestration
- Workflow modifications are configuration-only
- Clear audit trail of orchestration decisions

### 4. **Scalability**
- Easy addition of new agent types
- Support for complex multi-branch workflows
- Performance optimizations at orchestration level

### 5. **Enterprise Readiness**
- Comprehensive error handling and timeouts
- Detailed audit trails and monitoring
- Compliance-ready decision reconstruction

## Implementation Details

### Agent Refactoring

Legacy agents were refactored to use the registry pattern:

```python
# OLD: Hardcoded handoffs
def intake_agent(model: str | None = None) -> Agent:
    from loan_processing.providers.openai.agents.credit import credit_agent
    return Agent(
        name="Intake Agent",
        handoffs=[handoff(agent=credit_agent(model), ...)]
    )

# NEW: Registry-based creation
def intake_agent(model: str | None = None) -> Agent:
    return AgentRegistry.create_agent("intake", model)
```

### Pattern Execution

The orchestration engine supports multiple execution patterns:

```python
# Sequential execution
await orchestrator.execute_pattern("sequential", application)

# Parallel execution  
await orchestrator.execute_pattern("parallel", application)

# Future: Collaborative execution
await orchestrator.execute_pattern("collaborative", application)
```

### Context Management

`OrchestrationContext` accumulates results as agents complete:

```python
@dataclass
class OrchestrationContext:
    application: LoanApplication
    intake_result: Optional[Dict[str, Any]] = None
    credit_result: Optional[Dict[str, Any]] = None
    income_result: Optional[Dict[str, Any]] = None
    risk_result: Optional[Dict[str, Any]] = None
    audit_trail: List[str] = field(default_factory=list)
```

## Migration Strategy

### Phase 1: ✅ Completed
- Implement AgentRegistry and OrchestrationEngine
- Create sequential and parallel pattern configurations
- Refactor existing agent definitions for backward compatibility

### Phase 2: Future Enhancements
- Add collaborative pattern support
- Implement advanced condition evaluation
- Add pattern validation and testing tools
- Performance monitoring and optimization

## Backward Compatibility

Legacy agent functions are maintained for compatibility:

```python
# Legacy function still works
from loan_processing.providers.openai.agents import intake_agent
agent = intake_agent(model="gpt-4")

# But internally uses new registry
def intake_agent(model: str | None = None) -> Agent:
    return AgentRegistry.create_agent("intake", model)
```

## Testing Strategy

The new architecture enables comprehensive testing:

1. **Unit Tests**: Agent registry, orchestration engine components
2. **Integration Tests**: Pattern execution with mock agents
3. **End-to-End Tests**: Full workflow validation
4. **Configuration Tests**: YAML pattern validation

## Monitoring and Observability

The orchestration engine provides rich monitoring capabilities:

- **Audit Trails**: Complete record of agent executions and handoffs
- **Performance Metrics**: Agent durations, success rates, bottlenecks
- **Error Tracking**: Detailed error context and recovery actions
- **Decision Reconstruction**: Full traceability of decision factors

## Risks and Mitigations

### Risk: Configuration Complexity
**Mitigation**: Comprehensive validation, documentation, and tooling

### Risk: Performance Overhead
**Mitigation**: Pattern caching, optimized context passing, performance monitoring

### Risk: Debugging Difficulty
**Mitigation**: Detailed audit trails, structured logging, development tools

## Conclusion

The configuration-driven orchestration architecture successfully addresses the original tight coupling issues while providing:

- ✅ **Workflow Agnostic Agents**: Pure capability providers
- ✅ **Pattern Flexibility**: Easy switching between orchestration patterns
- ✅ **Maintainability**: Clean separation of concerns
- ✅ **Enterprise Features**: Comprehensive monitoring and error handling
- ✅ **Scalability**: Support for complex multi-agent workflows

This architectural change enables rapid experimentation with different orchestration patterns while maintaining clean, maintainable code that follows persona-driven architecture principles.

## References

- [ADR-003: Support Agent Feedback Implementation](./adr-003-support-agent-feedback-implementation.md)
- [ADR-004: Agent Handoff Pattern Implementation](./adr-004-agent-handoff-pattern-implementation.md)
- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents)
- [Configuration Files: `loan_processing/orchestration/patterns/`](../../loan_processing/orchestration/patterns/)