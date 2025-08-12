# Extension Guide

How to extend the loan processing system with custom capabilities.

## Overview

The system is designed to be **extensible** with minimal changes to core code. Add new:

- **MCP Tools**: Custom business logic
- **Data Sources**: External APIs and databases  
- **Agent Types**: Specialized processing agents
- **Orchestration**: Custom workflow patterns

## Adding MCP Tools

### 1. Create New Tool

**Example**: Custom credit scoring model

**File**: Create `mcp_servers/custom_scoring/server.py`

```python
@mcp.tool()
async def ai_credit_score(applicant_id: str, alternative_data: dict) -> dict:
    """Custom AI credit scoring using alternative data."""
    # Your custom logic here
    return {"ai_score": 750, "confidence": 0.92}
```

### 2. Register with Agent

Update agent configuration to include your new MCP server:

```python
# In loan_processing/providers/openai/agents/credit.py
def credit_agent(model: str | None = None) -> Agent:
    return Agent(
        name="Credit Agent",
        mcp_servers=[
            create_application_verification_mcp_server(),  # Port 8010
            create_custom_scoring_mcp_server(),            # Your new server
            # ... other servers
        ]
    )
```

**Result**: Agent can now autonomously use your custom scoring tool.

## Adding Data Sources

### External APIs

Integrate third-party services via MCP tools:

```python
@mcp.tool()
async def alternative_credit_bureau(applicant_id: str) -> dict:
    """Get data from alternative credit bureau."""
    # Call external API
    response = await external_api.get_credit_data(applicant_id)
    return response.to_dict()
```

### Custom Databases

Connect to proprietary data sources:

```python
@mcp.tool() 
async def internal_customer_history(applicant_id: str) -> dict:
    """Get customer history from internal systems."""
    # Query your database
    history = await internal_db.get_customer_history(applicant_id)
    return history
```

## Adding Agent Types

### 1. Create Agent Persona

**File**: Create `agent-persona/fraud-agent-persona.md`

```markdown
# Fraud Detection Agent

You are a fraud detection specialist for loan applications.

## Your Role
- Detect suspicious patterns in applications
- Flag high-risk applications for review
- Use multiple data sources for comprehensive analysis

## Available Tools
Use tools from these MCP servers:
- Application Verification (Port 8010): Basic applicant data
- Custom Fraud Detection (Port 8014): Specialized fraud tools

## Decision Process
1. First, get basic applicant data
2. Run fraud detection algorithms
3. Provide clear risk assessment with reasoning
```

### 2. Implement Agent

**File**: Create `loan_processing/providers/openai/agents/fraud.py`

```python
def fraud_agent(model: str | None = None) -> Agent:
    return Agent(
        name="Fraud Agent",
        instructions=load_persona("fraud"),
        model=model,
        mcp_servers=[
            create_application_verification_mcp_server(),
            create_fraud_detection_mcp_server(),  # Your custom server
        ]
    )
```

### 3. Add to Orchestration

Update orchestrator to include new agent:

```python
# In sequential.py or parallel.py
fraud_agent_instance = fraud_agent(model)
fraud_result = await Runner.run(fraud_agent_instance, input=application_data)
```

## Custom Orchestration

### New Processing Pattern

**File**: Create `loan_processing/providers/openai/orchestrators/conditional.py`

```python
async def process_application_conditional(
    application: LoanApplication,
    model: str | None = None
) -> LoanDecision:
    """Conditional processing based on application risk."""
    
    # Quick risk assessment first
    risk_score = await quick_risk_assessment(application)
    
    if risk_score < 0.3:
        # Low risk: fast track
        return await fast_track_processing(application, model)
    else:
        # High risk: comprehensive review
        return await full_review_processing(application, model)
```

## Integration Patterns

### 1. Plugin Architecture

All extensions follow the same pattern:

```text
1. Create MCP Server → 2. Register Tools → 3. Update Agent → 4. Test
```

### 2. Configuration-Driven

Control extensions via environment variables:

```python
# Enable custom features
ENABLE_AI_SCORING = True
ENABLE_FRAUD_DETECTION = True
CUSTOM_MCP_SERVERS = ["scoring:8014", "fraud:8015"]
```

### 3. Graceful Degradation

Extensions should fail gracefully:

```python
@mcp.tool()
async def optional_enhancement(applicant_id: str) -> dict:
    try:
        return await external_service.enhance(applicant_id)
    except Exception:
        # Log error, return basic data
        return {"status": "unavailable", "fallback_used": True}
```

## Testing Extensions

### Unit Tests

Test each MCP tool independently:

```python
def test_custom_scoring():
    result = await ai_credit_score("test-id", {"income": 50000})
    assert result["ai_score"] > 0
    assert "confidence" in result
```

### Integration Tests

Test agent behavior with new tools:

```python
def test_agent_uses_custom_tools():
    agent = credit_agent_with_custom_scoring()
    result = await Runner.run(agent, input=test_application)
    # Verify agent used custom tools in reasoning
```

## Current Extension Points

### Available Now

- **MCP Tools**: Add to any of the 3 existing servers
- **Agent Personas**: Update instruction files
- **Data Models**: Extend via `additional_data` field

### Planned

- **New Agent Types**: Fraud, compliance, document specialists
- **Workflow Patterns**: Conditional, human-in-loop, batch processing
- **Provider Support**: Microsoft Agent Framework, LangChain

## File Structure

```text
your_extensions/
├── mcp_servers/
│   └── custom_feature/
│       ├── server.py     # MCP tool implementations
│       └── service.py    # Business logic
├── agent-persona/
│   └── custom-agent-persona.md
└── tests/
    └── test_custom_feature.py
```

## Best Practices

- **Keep Tools Atomic**: One tool, one responsibility
- **Use Type Hints**: Full type annotations for all functions
- **Error Handling**: Graceful degradation when services unavailable
- **Documentation**: Update personas when adding tools
- **Testing**: Test both tools and agent behavior

**Next Step**: See existing implementations in [`mcp_servers/`](../mcp_servers/) for examples.
