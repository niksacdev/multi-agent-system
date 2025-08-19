# Console Application - Simplified Architecture# Console Application for Multi-Agent Loan Processing



This console application is now a **thin client** that provides a clean command-line interface to the loan processing backend. A standalone console client application for the Multi-Agent Loan Processing System.



## Architecture OverviewThis application is **completely decoupled** from the `loan_processing` backend module and uses its own configuration management system. It demonstrates proper separation of concerns and is ready for when the backend becomes an API service.



```## Features

console_app/           # Presentation layer only

├── .env              # UI preferences only- **🏗️ Decoupled Architecture**: Independent from backend implementation details

├── src/- **⚙️ Flexible Configuration**: Support for OpenAI and Azure OpenAI providers

│   ├── main.py       # Clean console interface - **🔄 Pattern Selection**: Choose between different orchestration patterns

│   ├── config.py     # Simple UI configuration (20 lines)- **🎯 Interactive Interface**: User-friendly console experience

│   └── backend_client.py  # Clean interface to loan_processing- **💾 Results Management**: Auto-save results with detailed metadata

└── README.md- **🔀 Pattern Comparison**: Compare different orchestration approaches

- **🌍 Environment-Based Config**: Development, staging, production configurations

loan_processing/       # Business logic layer

├── config/## Quick Start

│   └── settings.py   # ALL backend configuration

├── agents/           # AI provider implementations  ### 1. Configuration

├── tools/            # MCP server integrations

└── ...Copy the environment template and configure your settings:

```

```bash

## Simplified Configurationcd console_app

cp .env.example .env

### Console App (.env) - UI Preferences Only```

```bash

# UI Display SettingsEdit `.env` with your API keys and preferences:

DEBUG=false

SHOW_DETAILED_OUTPUT=true```bash

AUTO_SAVE_RESULTS=true# For OpenAI

RESULTS_DIR=resultsAGENT_PROVIDER_TYPE=openai

OPENAI_API_KEY=your-openai-api-key-here

# Console App Behavior

DEFAULT_PATTERN=sequential# For Azure OpenAI

ENABLE_PATTERN_COMPARISON=true# AGENT_PROVIDER_TYPE=azure_openai  

```# AZURE_OPENAI_KEY=your-azure-key-here

# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

### Backend Configuration - Environment Variables```

The loan_processing module handles all backend configuration:

### 2. Run the Application

```bash

# AI Provider (required)From the project root:

PROVIDER_TYPE=openai

OPENAI_API_KEY=your_key_here```bash

uv run python run_console_app.py

# Or for Azure OpenAI```

PROVIDER_TYPE=azure_openai

AZURE_OPENAI_API_KEY=your_azure_keyOr directly from the console_app directory:

AZURE_OPENAI_ENDPOINT=your_azure_endpoint

```bash

# Optional: MCP Server Ports (defaults shown)cd console_app

MCP_APP_VERIFICATION_PORT=8010python src/main.py

MCP_DOCUMENT_PROCESSING_PORT=8011```

MCP_FINANCIAL_CALCULATIONS_PORT=8012

```### 3. Prerequisites



## Benefits of Simplified ArchitectureEnsure MCP servers are running on ports 8010-8012:



### ✅ **Separation of Concerns**```bash

- **Console App**: Only handles UI/presentation logic# Terminal 1: Application Verification Server

- **Backend Module**: Handles all business logic and configurationuv run python -m loan_processing.tools.mcp_servers.application_verification.server

- **Clear Interface**: Clean API between layers

# Terminal 2: Document Processing Server  

### ✅ **Reduced Complexity**uv run python -m loan_processing.tools.mcp_servers.document_processing.server

- **Single Config Source**: No more .env vs YAML confusion

- **No Duplication**: Configuration lives in the right place# Terminal 3: Financial Calculations Server

- **Simple Classes**: ~20 line config class vs 300+ line complex loaderuv run python -m loan_processing.tools.mcp_servers.financial_calculations.server

```

### ✅ **Better Maintainability**

- **Easier Testing**: Simple configuration is easier to mock**Note**: If you get connection errors during processing, the console app will show helpful error messages to guide you.

- **Clear Boundaries**: UI concerns vs business concerns

- **Scalable**: Easy to add new UI clients (web, API, etc.)## Architecture



## Running the Application### Configuration-Driven Design



```bashThe console app uses a **configuration-first** approach with **all backend concerns consolidated**:

# Start MCP servers (in separate terminals)

uv run python -m mcp_servers.application_verification.server```yaml

uv run python -m mcp_servers.document_processing.server  # config/app_config.yaml

uv run python -m mcp_servers.financial_calculations.serverbackend:

  # All backend configuration in one place

# Set backend configuration  agent_provider:

export OPENAI_API_KEY=your_key_here    provider_type: "${AGENT_PROVIDER_TYPE:-openai}"

    api_key: "${OPENAI_API_KEY}"

# Run console app    azure_api_key: "${AZURE_OPENAI_KEY}"

cd console_app    azure_api_base: "${AZURE_OPENAI_ENDPOINT}"

uv run python src/main.py  

```  orchestration:

    discovery_method: "backend_query"  # No filesystem traversal!

## Migration from Complex Version    default_selection: "sequential"    # UI preference only

```

The old complex configuration system has been removed:

- ❌ `config/app_config.yaml` - Removed (backend configs moved to loan_processing)### Backend Configuration Consolidation

- ❌ `config/simple_config.yaml` - Removed (redundant)

- ❌ `config/settings.py` - Removed (300+ lines of complexity)**All backend concerns are organized under the `backend:` section**:

- ❌ `.env.example` - Removed (redundant)

- ❌ `.env.simple` - Removed (redundant)- **Agent providers** (OpenAI/Azure OpenAI) 

- **Orchestration pattern discovery**

✅ **New simplified files:**- **Infrastructure connectivity**

- `src/config.py` - Simple 20-line configuration class

- `src/backend_client.py` - Clean interface to backendThis creates a **clear separation** between backend business logic and console app UI preferences.

- `src/main.py` - Streamlined console interface

- `.env` - UI preferences only### Clean Dependencies



## Architecture ValidationThe console app imports `loan_processing` as an **external dependency**:



This new architecture follows the **system-architecture-reviewer** recommendations:```python

# console_app/src/main.py

### ✅ **Proper Boundaries**from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationEngine

- Console app doesn't know about AI providers```

- Backend doesn't know about UI preferences  

- Clear interface between layersThis maintains clean separation for future API-based deployment.



### ✅ **Single Responsibility**## Directory Structure

- Console app: User interaction only

- Backend: Business logic only```

- Configuration: Appropriate to each layerconsole_app/

├── config/                    # Configuration management

### ✅ **Simplified Configuration**│   ├── app_config.yaml       # Main configuration

- Environment variables for backend│   ├── settings.py           # Configuration loader

- Simple .env for UI preferences│   └── __init__.py

- No complex YAML substitution├── src/                      # Application source

│   ├── main.py               # Main console application

This achieves the **Option B** architecture recommended by the system-architecture-reviewer agent.│   ├── utils.py              # Utility functions
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
backend:
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

### Infrastructure Configuration

MCP server configuration is managed by the **backend** in `loan_processing/config/infrastructure.yaml`. 

The console app only needs to know that backend services are available - it doesn't manage infrastructure details.

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