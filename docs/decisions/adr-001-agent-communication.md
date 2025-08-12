# ADR-001: Agent Communication Pattern

## Status

Proposed

## Context

We need to establish how agents in the loan processing system will communicate and share data:

1. **Shared State vs. Message Passing**: Agents could share mutable state or pass immutable data
2. **Data Format**: Raw dictionaries, Pydantic models, or Agent Framework types
3. **Context Passing**: How to provide previous agent results to subsequent agents
4. **Error Handling**: How failed agent responses are handled in the orchestration

The Agent Framework provides `AgentRunResponse` as the standard response type, but we need to decide how to structure the data payload and context sharing.

## Decision

**Use structured Pydantic models passed through orchestration layer rather than shared state:**

1. **Data Contracts**: Define Pydantic models for all inter-agent data exchange
2. **Immutable Passing**: Pass data as immutable models between agents
3. **Orchestration Layer**: Orchestration functions handle data transformation and routing
4. **Context Objects**: Use explicit context parameters with typed data structures

```python
# Agents receive typed inputs and return structured outputs
async def assess_application(
    self, 
    application: LoanApplication,
    context: Optional[AssessmentContext] = None
) -> AssessmentResult:
```

## Consequences

### Positive

- ✅ **Type Safety**: Comprehensive validation and IDE support
- ✅ **Testability**: Easy to mock and test individual agents
- ✅ **Clarity**: Clear data contracts between agents
- ✅ **Debugging**: Structured data is easier to inspect and log
- ✅ **Framework Alignment**: Works well with Agent Framework patterns

### Negative

- ❌ **Performance Overhead**: Model serialization/validation costs
- ❌ **Upfront Design**: Need comprehensive data models before implementation
- ❌ **Complexity**: More complex than simple dictionary passing

### Risks

- **Over-engineering**: Risk of creating overly complex data structures
- **Evolution**: Data models may need frequent changes during development

## Implementation

1. **Create `models/` package** with comprehensive Pydantic models
2. **Define context types** for each agent interaction
3. **Implement orchestration functions** that handle data transformation
4. **Document data flow** in system architecture diagrams

```python
# Example implementation structure
from loan_processing.models import (
    LoanApplication,
    IntakeResult, 
    CreditAssessment,
    IncomeVerification,
    RiskEvaluation,
    LoanDecision
)

async def sequential_processing(app: LoanApplication) -> LoanDecision:
    intake = await intake_agent.assess(app)
    credit = await credit_agent.assess(app, context=intake)
    income = await income_agent.assess(app, context=intake)
    decision = await risk_agent.assess(app, context={
        'intake': intake,
        'credit': credit, 
        'income': income
    })
    return decision
```

Related Issues: TBD (create implementation issues)
