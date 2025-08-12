# Agent Patterns

How to build autonomous agents that select their own tools.

## Overview

Our agents are **autonomous** - they decide which tools to use based on what they need to accomplish. No hardcoded workflows.

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Agent      │ ──▶│  MCP Servers    │ ──▶│ Business Logic  │
│   (Autonomous)  │    │ (Tool Servers)  │    │ (Domain Logic)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Key Principle**: Agents get access to tool servers. They decide what to use.

## Agent Implementation

Each agent follows this pattern:

1. **Load Persona**: Instructions on what tools to use and when
2. **Connect to MCP Servers**: Access to multiple tool servers
3. **Autonomous Selection**: Agent picks tools based on assessment needs

**Example**: See [`loan_processing/providers/openai/agents/credit.py`](../loan_processing/providers/openai/agents/credit.py)

## MCP Server Pattern

Business capabilities are exposed as independent tool servers:

```text
Port 8010: Application Verification
├── retrieve_credit_report()
├── verify_employment()
└── get_bank_account_data()

Port 8011: Document Processing
├── extract_text_from_document()
├── classify_document_type()
└── validate_document_format()

Port 8012: Financial Calculations
├── calculate_debt_to_income_ratio()
├── calculate_loan_affordability()
└── analyze_income_stability()
```

**Implementation**: See [`mcp_servers/`](../mcp_servers/) directory

## Agent Personas

Personas guide autonomous tool selection:

- [`agent-persona/credit-agent-persona.md`](../agent-persona/credit-agent-persona.md) - Credit assessment guidance
- [`agent-persona/intake-agent-persona.md`](../agent-persona/intake-agent-persona.md) - Application validation
- [`agent-persona/income-agent-persona.md`](../agent-persona/income-agent-persona.md) - Income verification
- [`agent-persona/risk-agent-persona.md`](../agent-persona/risk-agent-persona.md) - Risk analysis

## Current Implementation

### What's Built

```text
providers/openai/
├── agents/
│   └── credit.py     ✅ Credit assessment agent
└── orchestrators/
    └── sequential.py ✅ Sequential processing
```

### Planned

```text
providers/openai/
├── agents/
│   ├── credit.py     ✅ Built
│   ├── intake.py     📋 Planned
│   ├── income.py     📋 Planned
│   └── risk.py       📋 Planned
└── orchestrators/
    ├── sequential.py ✅ Built
    └── parallel.py   📋 Planned
```

## Benefits

- **Flexible**: Agents adapt to different loan types
- **Maintainable**: Business logic separate from agent logic
- **Scalable**: Independent MCP servers can scale separately
- **Testable**: Each component can be tested independently

See the actual code files for complete implementation details.
