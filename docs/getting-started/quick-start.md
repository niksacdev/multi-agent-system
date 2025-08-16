# Quick Start Guide

This guide walks you through setting up and running the Multi-Agent Loan Processing System in your environment.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Azure OpenAI credentials)
- 8GB RAM minimum (16GB recommended for production)
- macOS, Linux, or Windows with WSL2

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/niksacdev/multi-agent-system.git
cd multi-agent-system
```

### Step 2: Install Dependencies

We use `uv` for fast, reliable package management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Optional: Model Selection
MODEL_NAME=gpt-4  # or gpt-3.5-turbo for lower cost
```

## Running the System

### Basic Demo

Run the sequential processing demo to see the system in action:

```bash
uv run python demo_sequential_processing.py
```

This will:
1. Start all MCP servers (application verification, document processing, financial calculations)
2. Create a sample loan application
3. Process it through all agents sequentially
4. Display the final decision with detailed reasoning

### Running Tests

Ensure everything is working correctly:

```bash
# Run all tests
uv run python run_tests.py --type all

# Run specific test categories
uv run python run_tests.py --type unit       # Unit tests only
uv run python run_tests.py --type integration # Integration tests
uv run python run_tests.py --type system     # Full system tests
```

### Development Mode

For development with hot-reload:

```bash
# Start MCP servers in development mode
uv run python -m loan_processing.tools.start_servers --dev

# In another terminal, run the application
uv run python main.py --mode development
```

## Project Structure

```
multi-agent-system/
├── loan_processing/
│   ├── agents/           # Agent implementations
│   │   ├── shared/       # Shared models and utilities
│   │   │   ├── agent-persona/  # JTBD-aligned agent instructions
│   │   │   ├── models/         # Data models
│   │   │   └── utils/          # Shared utilities
│   │   └── providers/    # Provider implementations (OpenAI, etc.)
│   │       └── openai/
│   │           ├── orchestration/  # Workflow patterns
│   │           └── agentregistry.py
│   └── tools/            # MCP server implementations
│       └── mcp_servers/
│           ├── application_verification/
│           ├── document_processing/
│           └── financial_calculations/
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation
└── demo_sequential_processing.py  # Main demo script
```

## Configuration Options

### Agent Configuration

Agents are configured in `loan_processing/agents/shared/config/agents.yaml`:

```yaml
agents:
  intake:
    name: "Application Intake Agent"
    model: "gpt-4"  # Can override per agent
    timeout_seconds: 300
    mcp_servers:
      - application_verification
      - document_processing
```

### Orchestration Patterns

Choose between different processing patterns:

```python
from loan_processing import LoanProcessingSystem

# Sequential processing (default)
system = LoanProcessingSystem(provider="openai")
decision = await system.process_application(
    application=loan_app,
    pattern="sequential"
)

# Parallel processing (coming soon)
decision = await system.process_application(
    application=loan_app,
    pattern="parallel"
)
```

### MCP Server Configuration

MCP servers run on specific ports:

- **Application Verification**: Port 8010
- **Document Processing**: Port 8011
- **Financial Calculations**: Port 8012

Configure in `loan_processing/agents/shared/config/mcp_servers.yaml`:

```yaml
mcp_servers:
  application_verification:
    url: "http://localhost:8010/sse"
    timeout: 30
    retry_attempts: 3
```

## Troubleshooting

### Common Issues

**1. OpenAI API Key Not Found**
```bash
export OPENAI_API_KEY="your-key-here"
# Or add to .env file
```

**2. MCP Server Connection Failed**
```bash
# Check if servers are running
ps aux | grep mcp_server

# Restart servers
uv run python -m loan_processing.tools.restart_servers
```

**3. Import Errors**
```bash
# Ensure you're in the virtual environment
uv sync
uv run python your_script.py  # Always use 'uv run'
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

## Next Steps

- **Customize Agents**: See [Adding New Agents](../adding-new-agents.md)
- **Extend the System**: See [Extension Guide](../extension-guide.md)
- **Understand Architecture**: See [Agent Strategy](../architecture/agent-strategy.md)
- **Explore JTBD Framework**: See [Jobs-to-be-Done](../architecture/jobs-to-be-done.md)

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/niksacdev/multi-agent-system/issues)
- Documentation: [Full documentation](../README.md)
- Examples: See `/examples` directory for more use cases