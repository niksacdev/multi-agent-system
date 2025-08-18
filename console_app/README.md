# Console Application for Multi-Agent Loan Processing

A standalone console client application for the Multi-Agent Loan Processing System.

This application is **completely decoupled** from the `loan_processing` backend module and uses its own configuration management system. It demonstrates proper separation of concerns and is ready for when the backend becomes an API service.

## Features

- **🏗️ Decoupled Architecture**: Independent from backend implementation details
- **⚙️ Flexible Configuration**: Support for OpenAI and Azure OpenAI providers
- **🔄 Pattern Selection**: Choose between different orchestration patterns
- **🎯 Interactive Interface**: User-friendly console experience
- **💾 Results Management**: Auto-save results with detailed metadata
- **🔀 Pattern Comparison**: Compare different orchestration approaches
- **🌍 Environment-Based Config**: Development, staging, production configurations

## Quick Start

### 1. Configuration

Copy the environment template and configure your settings:

```bash
cd console_app
cp .env.example .env
```

Edit `.env` with your API keys and preferences:

```bash
# For OpenAI
AGENT_PROVIDER_TYPE=openai
OPENAI_API_KEY=your-openai-api-key-here

# For Azure OpenAI
# AGENT_PROVIDER_TYPE=azure_openai  
# AZURE_OPENAI_KEY=your-azure-key-here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 2. Run the Application

From the project root:

```bash
uv run python run_console_app.py
```

Or directly from the console_app directory:

```bash
cd console_app
python src/main.py
```

### 3. Prerequisites

Ensure MCP servers are running on ports 8010-8012:

```bash
# Terminal 1: Application Verification Server
uv run python -m loan_processing.tools.mcp_servers.application_verification.server

# Terminal 2: Document Processing Server  
uv run python -m loan_processing.tools.mcp_servers.document_processing.server

# Terminal 3: Financial Calculations Server
uv run python -m loan_processing.tools.mcp_servers.financial_calculations.server
```

**Note**: If you get connection errors during processing, the console app will show helpful error messages to guide you.

## Architecture

### Configuration-Driven Design

The console app uses a **configuration-first** approach:

```yaml
# config/app_config.yaml
orchestration:
  patterns:
    - id: "sequential"
      name: "Sequential Processing"
      description: "Agents process in sequence" 
      workflow:
        - "INTAKE AGENT → Validates application"
        - "CREDIT AGENT → Retrieves credit data"
        # ...
```

No more filesystem traversal or hardcoded pattern discovery!

### Provider Flexibility

Single configuration supports both OpenAI and Azure OpenAI:

```yaml
agent_provider:
  provider_type: "${AGENT_PROVIDER_TYPE:-openai}"
  
  # OpenAI Configuration
  api_key: "${OPENAI_API_KEY}"
  
  # Azure OpenAI Configuration  
  azure_api_key: "${AZURE_OPENAI_KEY}"
  azure_api_base: "${AZURE_OPENAI_ENDPOINT}"
```

### Clean Dependencies

The console app imports `loan_processing` as an **external dependency**:

```python
# console_app/src/main.py
from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine
```

This maintains clean separation for future API-based deployment.

## Directory Structure

```
console_app/
├── config/                    # Configuration management
│   ├── app_config.yaml       # Main configuration
│   ├── settings.py           # Configuration loader
│   └── __init__.py
├── src/                      # Application source
│   ├── main.py               # Main console application
│   ├── utils.py              # Utility functions
│   └── __init__.py
├── .env.example              # Environment template
├── README.md                 # This file
└── __init__.py
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_PROVIDER_TYPE` | `openai` or `azure_openai` | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | Required for OpenAI |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | Required for Azure |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Required for Azure |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure deployment name | Required for Azure |
| `SHOW_DETAILED_OUTPUT` | Show detailed processing output | `true` |
| `AUTO_SAVE_RESULTS` | Automatically save results | `true` |
| `PATTERN_COMPARISON` | Enable pattern comparison | `true` |

### Architecture Note: Patterns are Backend-Controlled

**Important**: Orchestration patterns are **business logic** controlled by the backend, not by the console application.

- **❌ Console app cannot add new patterns** - patterns are discovered from backend
- **✅ Console app provides UI preferences** - which pattern to pre-select, show details, etc.
- **🔮 Future**: When backend becomes API service, patterns discovered via API calls

```yaml
# console_app/config/app_config.yaml  
orchestration:
  # UI preferences only, NOT business logic
  discovery_method: "backend_query"
  default_selection: "sequential"    # Which to pre-select  
  show_pattern_details: true        # UI behavior
  enable_comparison: true           # Feature flag
```

To add new patterns, modify the **backend configuration**:
```bash
# Backend controls business logic
loan_processing/agents/shared/config/my_new_pattern.yaml
```

### MCP Server Configuration

Configure servers in `config/app_config.yaml`:

```yaml
mcp_servers:
  servers:
    - name: "custom_server"
      host: "${CUSTOM_SERVER_HOST:-localhost}"
      port: "${CUSTOM_SERVER_PORT:-8020}"
      module: "path.to.custom.server"
      required: true
```

## Development

### Running in Debug Mode

```bash
python src/main.py --debug
```

This provides detailed error traces and configuration validation.

### Configuration Validation

The app validates configuration on startup:

```python
from config.settings import get_config_loader

loader = get_config_loader()
issues = loader.validate_configuration()
if issues:
    print("Configuration issues:", issues)
```

### Testing Configuration

```bash
# Test OpenAI configuration
AGENT_PROVIDER_TYPE=openai \
OPENAI_API_KEY=test \
OPENAI_MODEL=gpt-3.5-turbo \
python src/main.py

# Test Azure OpenAI configuration  
AGENT_PROVIDER_TYPE=azure_openai \
AZURE_OPENAI_KEY=test \
AZURE_OPENAI_ENDPOINT=https://test.openai.azure.com/ \
AZURE_OPENAI_DEPLOYMENT_NAME=my-gpt-4 \
python src/main.py
```

## Future Roadiness

This architecture is designed for the future when `loan_processing` becomes an API service:

1. **Current**: Console app imports `loan_processing` as Python module
2. **Future**: Console app calls `loan_processing` REST/GraphQL API
3. **Configuration**: Same configuration system, different transport layer

The clean separation ensures minimal changes when migrating to API-based architecture.

## Troubleshooting

### Configuration Issues

```bash
❌ Configuration Issues Found:
  - OPENAI_API_KEY is required for OpenAI provider
```

**Solution**: Check your `.env` file and ensure required variables are set.

### MCP Server Connection Issues

```bash
❌ Error during processing: [Connection error details]

💡 Common solutions:
   • Make sure MCP servers are running (see prerequisites above)
   • Check your OpenAI API key is valid
   • Verify network connectivity
```

**Solution**: The console app provides helpful error messages. Follow the suggested solutions.

### Module Import Issues

```bash
❌ ModuleNotFoundError: No module named 'loan_processing'
```

**Solution**: Run from project root using `uv run python run_console_app.py`

## Contributing

When adding features to the console app:

1. **Configuration first**: Add settings to `app_config.yaml`
2. **Environment variables**: Use `${VAR:-default}` syntax  
3. **Validation**: Add validation to `settings.py`
4. **Documentation**: Update this README

This ensures the app remains configuration-driven and maintainable.