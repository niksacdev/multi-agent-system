# Agent Patterns

How to build and configure domain-driven autonomous agents using the registry pattern.

## Overview

Our agents are **autonomous** and **configuration-driven** - they decide which tools to use based on domain expertise encoded in personas, not hardcoded workflows.

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Agent Registry │──▶│    Agent +      │──▶│   MCP Servers   │
│  (YAML Config)  │    │    Persona      │    │ (Tool Servers)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ↓                      ↓                      ↓
   Configuration         Domain Logic            Autonomous
   Driven Creation      in Markdown Files       Tool Selection
```

## Agent Registry Pattern

All agents are created through a centralized registry using YAML configuration:

```yaml
# loan_processing/agents/shared/config/agents.yaml
agents:
  intake:
    name: "Intake Agent"
    persona_file: "intake"
    mcp_servers: []  # Optimized for speed - no external tools
    capabilities: 
      - "Application validation"
      - "Data completeness check"
```

```python
# Simple agent creation
from loan_processing.agents.providers.openai.agentregistry import AgentRegistry

agent = AgentRegistry.create_agent("intake", model="gpt-4")
```

## Adding New Agents

### Step 1: Define Agent Configuration

Add your agent to `loan_processing/agents/shared/config/agents.yaml`:

```yaml
agents:
  your_new_agent:
    name: "Your Agent Name"
    description: "What this agent does"
    persona_file: "your_agent"  # References markdown file
    mcp_servers: 
      - "application_verification"  # Which MCP servers it can access
      - "document_processing"
    capabilities:
      - "Specific capability 1"
      - "Specific capability 2"
    output_format:
      assessment_field: "string"
      score_field: "number"
      decision: "string"
    provider_config:
      openai:
        model: "gpt-4"
        temperature: 0.1
        timeout_seconds: 60
```

### Step 2: Create Agent Persona

Create `loan_processing/agents/shared/agent-persona/your_agent.md`:

```markdown
# Your Agent Name

## Role
You are a specialized agent responsible for [specific domain task].

## Domain Expertise
[Describe the domain knowledge and expertise this agent has]

## Available Tools
You have access to the following MCP servers:
- **application_verification**: For identity and employment checks
- **document_processing**: For document analysis

## Decision Framework
[Provide decision-making guidance based on domain expertise]

## Output Requirements
Your assessment must include:
- assessment_field: Your primary assessment
- score_field: Numerical score (0-100)
- decision: APPROVE/REVIEW/DENY
```

### Step 3: Use Your Agent

```python
# In orchestration or standalone
agent = AgentRegistry.create_agent("your_new_agent")
result = await agent.run(context)
```

## Current Agents

### Domain Expert Agents

1. **Intake Agent** ([persona](../loan_processing/agents/shared/agent-persona/intake.md))
   - Fast application triage
   - No MCP servers (optimized for speed)
   - Routes applications to appropriate workflow

2. **Credit Agent** ([persona](../loan_processing/agents/shared/agent-persona/credit.md))
   - Comprehensive credit assessment
   - Uses all three MCP servers
   - Evaluates creditworthiness and risk

3. **Income Agent** ([persona](../loan_processing/agents/shared/agent-persona/income.md))
   - Employment and income verification
   - Handles traditional and gig economy income
   - Calculates debt-to-income ratios

4. **Risk Agent** ([persona](../loan_processing/agents/shared/agent-persona/risk.md))
   - Synthesizes all assessments
   - Makes final recommendations
   - Applies regulatory compliance checks

## MCP Server Pattern

Business capabilities exposed as independent tool servers:

```text
Port 8010: Application Verification
├── retrieve_credit_report()
├── verify_employment()
├── verify_identity()
└── get_bank_account_data()

Port 8011: Document Processing
├── extract_text_from_document()
├── classify_document_type()
├── validate_document_format()
└── extract_structured_data()

Port 8012: Financial Calculations
├── calculate_debt_to_income_ratio()
├── calculate_loan_affordability()
├── analyze_income_stability()
└── calculate_monthly_payment()
```

Agents autonomously select which tools to use based on their persona instructions.

## Orchestration Integration

Agents work within orchestration patterns:

### Sequential Pattern (Current)
```yaml
orchestration:
  loan_processing:
    pattern: "sequential"
    agents: ["intake", "credit", "income", "risk"]
    context_passing: "accumulative"
```

### Parallel Pattern (Planned)
```yaml
orchestration:
  fast_processing:
    pattern: "parallel"
    branches:
      - ["credit", "income"]  # Run simultaneously
    aggregator: "risk"
```

## Benefits of This Pattern

- **Domain-Driven**: Agents embody real domain expertise
- **Configuration-Based**: Add agents without code changes
- **Provider Agnostic**: Switch between OpenAI, Autogen, etc.
- **Maintainable**: Business logic in personas, not code
- **Testable**: Each component tested independently
- **Scalable**: MCP servers scale separately

## Future MCP Server Expansion

As the system evolves, agents will gain access to additional MCP servers:

**Intake Agent**:
- Document OCR and extraction
- Fraud detection services
- Application search and deduplication
- Public records enrichment

**Credit Agent**:
- Multiple credit bureau APIs (Experian, Equifax, TransUnion)
- Alternative credit data sources
- Business credit reports
- International credit databases

**Income Agent**:
- Payroll service integrations (ADP, Paychex)
- Tax transcript APIs
- Bank account aggregation
- Gig economy platform APIs

**Risk Agent**:
- ML-based risk scoring models
- Regulatory compliance tools (OFAC, AML)
- Property valuation services
- Insurance verification APIs

## Implementation Files

- **Agent Registry**: [`loan_processing/agents/providers/openai/agentregistry.py`](../loan_processing/agents/providers/openai/agentregistry.py)
- **Configuration**: [`loan_processing/agents/shared/config/agents.yaml`](../loan_processing/agents/shared/config/agents.yaml)
- **Personas**: [`loan_processing/agents/shared/agent-persona/`](../loan_processing/agents/shared/agent-persona/)
- **MCP Servers**: [`loan_processing/tools/mcp_servers/`](../loan_processing/tools/mcp_servers/)
- **Orchestration**: [`loan_processing/agents/providers/openai/orchestration/`](../loan_processing/agents/providers/openai/orchestration/)

See the actual code files for complete implementation details.