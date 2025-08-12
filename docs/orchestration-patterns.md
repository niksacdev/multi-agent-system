# Orchestration Patterns

How agents work together to process loan applications.

## Overview

We use **two patterns** to coordinate multiple agents:

- **Sequential**: Process one agent after another
- **Parallel**: Process independent agents simultaneously

## Sequential Processing

Each agent runs one after the other, with full context from previous agents.

```text
Application → Agent1 - Agent n → Decision
```

**When to use**: Start here. Simple, reliable, easy to debug.

**Implementation**: See [`loan_processing/providers/openai/orchestrators/sequential.py`](../loan_processing/providers/openai/orchestrators/sequential.py)

### How it works

1. **Credit Agent** gets the loan application
2. Agent autonomously selects tools from 3 MCP servers:
   - Application Verification (Port 8010)
   - Document Processing (Port 8011) 
   - Financial Calculations (Port 8012)
3. Agent makes comprehensive assessment and decision

**Performance**: ~30-60 seconds per application

## Parallel Processing

Multiple agents run simultaneously for faster processing.

```text
                Application
                     ↓
               Intake Agent
                ↙         ↘
         Credit Agent   Income Agent
                ↘         ↙
               Risk Agent
                     ↓
                 Decision
```

**When to use**: When you need faster processing and agents can work independently.

## Usage

```python
from loan_processing.providers.openai.orchestrators.sequential import process_application_sequential

# Process application
decision = await process_application_sequential(application, model="gpt-4")
```

See the actual implementation in the code files for complete examples.
