# Orchestration Patterns

Configuration-driven patterns for coordinating multi-agent workflows.

## Overview

Our orchestration system is **configuration-driven** - define agent workflows in YAML, not code. This enables:

- **Rapid iteration** without code changes
- **A/B testing** different workflows
- **Domain expert configuration** without programming
- **Clean separation** between orchestration and business logic

## Current Implementation

### Sequential Pattern ✅

Agents process one after another with context accumulation.

**Configuration**: [`loan_processing/agents/shared/config/orchestration.yaml`](../loan_processing/agents/shared/config/orchestration.yaml)

```yaml
orchestration:
  loan_processing:
    pattern: "sequential"
    agents: ["intake", "credit", "income", "risk"]
    context_passing: "accumulative"
    handoff_validation: true
    timeout_seconds: 300
    fallback: "manual_review"
```

**Implementation**: [`loan_processing/agents/providers/openai/orchestration/sequential.py`](../loan_processing/agents/providers/openai/orchestration/sequential.py)

```text
Application → Intake → Credit → Income → Risk → Decision
     ↓          ↓        ↓        ↓       ↓
  Context    Context  Context  Context  Final
   Init      +Intake  +Credit  +Income  Decision
```

**Key Features**:
- Each agent sees all previous assessments
- Handoff validation between agents
- Comprehensive audit trail
- Error recovery and fallback

**When to Use**: 
- Default pattern for most loan processing
- When agents depend on previous assessments
- When audit trail is critical

**Performance**: ~2-5 minutes total processing

## Planned Patterns

### Parallel Pattern 🔄

Multiple agents work simultaneously for faster processing.

**Planned Configuration**:
```yaml
orchestration:
  fast_track:
    pattern: "parallel"
    branches:
      financial:
        agents: ["credit", "income"]
        timeout: 120
      compliance:
        agents: ["risk", "fraud"]
        timeout: 150
    aggregator: "decision_maker"
    merge_strategy: "all_complete"
```

**Concept**:
```text
         Application
              ↓
         Intake Agent
          ↙       ↘
    Credit Agent  Income Agent
          ↘       ↙
         Risk Agent
              ↓
          Decision
```

**Benefits**:
- 40-50% faster processing
- Independent assessments
- Better resource utilization

### Conditional Pattern 🔀

Dynamic routing based on assessment results.

**Planned Configuration**:
```yaml
orchestration:
  adaptive:
    pattern: "conditional"
    initial: "intake"
    routing_rules:
      - condition: "intake.routing_decision == 'FAST_TRACK'"
        agents: ["simplified_credit", "risk"]
        
      - condition: "intake.routing_decision == 'ENHANCED'"
        agents: ["credit", "income", "employment", "assets", "risk"]
        
      - condition: "intake.routing_decision == 'FRAUD_CHECK'"
        agents: ["fraud", "identity", "manual_review"]
        
    default_path: ["credit", "income", "risk"]
```

**Concept**:
```text
Application → Intake → [Dynamic Path Based on Rules] → Decision
                ↓
         Evaluates conditions
         Selects agent path
```

**Use Cases**:
- Fast-track high-quality applications
- Enhanced review for complex cases
- Special handling for fraud indicators

### Hierarchical Pattern 🌳

Supervisor agents managing specialist teams.

**Planned Configuration**:
```yaml
orchestration:
  hierarchical:
    pattern: "hierarchical"
    supervisor: "loan_supervisor"
    teams:
      credit_team:
        lead: "credit_lead"
        members: ["fico_agent", "alternative_credit", "credit_history"]
      income_team:
        lead: "income_lead"
        members: ["w2_agent", "gig_economy", "asset_income"]
    escalation_path: ["supervisor", "manual_review"]
```

**Benefits**:
- Complex decision decomposition
- Specialist agent teams
- Clear escalation paths

## Context Management

### Accumulative Context (Default)
```python
context = {
    "application": loan_application,
    "assessments": {
        "intake": intake_assessment,
        "credit": credit_assessment,
        "income": income_assessment
    }
}
```

### Selective Context
```yaml
context_passing:
  credit_agent:
    receives: ["application", "intake_assessment"]
  risk_agent:
    receives: ["application", "all_assessments"]
```

## Handoff Patterns

### Validation-Based Handoff
```python
# Current implementation
def validate_handoff(prev_assessment, next_agent):
    if prev_assessment.confidence < 0.7:
        return HandoffDecision.RETRY
    if prev_assessment.status == "FAILED":
        return HandoffDecision.FALLBACK
    return HandoffDecision.PROCEED
```

### Condition-Based Handoff
```yaml
handoff_rules:
  credit_to_income:
    proceed_if: "credit.score > 650"
    skip_if: "credit.score > 750"
    fallback_if: "credit.score < 600"
```

## Error Handling

### Retry Strategy
```yaml
retry_policy:
  max_attempts: 3
  backoff: "exponential"
  initial_delay: 1
  max_delay: 30
```

### Fallback Options
```yaml
fallback:
  agent_timeout: "skip_agent"
  agent_error: "manual_review"
  orchestration_error: "escalate"
```

## Observability

### Built-in Tracing
```python
# Automatic with OpenTelemetry
with correlation_context(application_id):
    result = await orchestrator.execute(application)
    # Traces include:
    # - Agent execution times
    # - Tool usage
    # - Context passing
    # - Decision points
```

### Audit Trail
```yaml
audit:
  log_level: "detailed"
  include:
    - agent_inputs
    - agent_outputs
    - tool_calls
    - decision_rationale
  exclude:
    - internal_prompts
```

## Configuration Examples

### Simple Sequential
```yaml
orchestration:
  simple:
    pattern: "sequential"
    agents: ["credit", "risk"]
```

### Complex Conditional
```yaml
orchestration:
  complex:
    pattern: "conditional"
    initial: "intake"
    routing_rules:
      - condition: "high_value_loan"
        path: ["enhanced_credit", "asset_verification", "senior_risk"]
      - condition: "first_time_buyer"
        path: ["credit", "income", "first_time_programs", "risk"]
    default: ["credit", "income", "risk"]
```

## Benefits of Configuration-Driven Orchestration

1. **Business Agility**: Change workflows without deployments
2. **Experimentation**: A/B test different patterns
3. **Domain Control**: Business experts configure workflows
4. **Maintainability**: Logic in configuration, not code
5. **Observability**: Built-in tracing and audit trails

## Implementation Files

- **Base Classes**: [`loan_processing/agents/providers/openai/orchestration/base.py`](../loan_processing/agents/providers/openai/orchestration/base.py)
- **Sequential**: [`loan_processing/agents/providers/openai/orchestration/sequential.py`](../loan_processing/agents/providers/openai/orchestration/sequential.py)
- **Engine**: [`loan_processing/agents/providers/openai/orchestration/engine.py`](../loan_processing/agents/providers/openai/orchestration/engine.py)
- **Tests**: [`tests/test_sequential_orchestration.py`](../tests/test_sequential_orchestration.py)

See actual code files for complete implementation details.