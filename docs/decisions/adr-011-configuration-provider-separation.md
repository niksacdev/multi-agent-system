# ADR-011: Configuration Provider Separation (Agent vs AI Model Providers)

## Status
Accepted

## Context
The system originally conflated two distinct architectural concepts under a single "provider" configuration, creating confusion and limiting future extensibility.

### Problem Statement
The original configuration used `PROVIDER_TYPE` to mean "AI model service provider" but terminology and architecture suggested it could also mean "agent framework provider". This created several issues:

1. **Terminology Confusion**: "Provider" was ambiguous - SDK framework or AI service?
2. **Future Limitations**: When adding AutoGen or Semantic Kernel, the distinction becomes critical
3. **Configuration Complexity**: Mixed concerns in a single configuration parameter
4. **Architecture Misalignment**: Two distinct architectural layers incorrectly coupled

### Original Configuration (Problematic)
```bash
# Ambiguous - what kind of provider?
PROVIDER_TYPE=openai  # Could mean OpenAI SDK or OpenAI API service
OPENAI_API_KEY=key
```

### Architectural Distinction
The system actually has two distinct provider layers:

1. **Agent Provider (SDK/Framework Layer)**
   - OpenAI Agents SDK (current)
   - AutoGen (future)
   - Semantic Kernel (future)  
   - Custom agent framework (future)

2. **AI Model Provider (LLM Service Layer)**
   - OpenAI API
   - Azure OpenAI Service
   - Anthropic Claude API
   - Local models (future)

### Alternatives Considered

#### Option 1: Keep Single Provider Configuration
**Pros:** Simpler configuration, less variables
**Cons:** Architectural confusion, limits future flexibility, unclear separation of concerns

#### Option 2: Implicit Provider Relationships
**Pros:** Less configuration needed
**Cons:** Hidden assumptions, brittle when adding new combinations

#### Option 3: Explicit Separation with Clear Naming
**Pros:** Clear architectural separation, flexible combinations, future-proof
**Cons:** More configuration parameters, need to update existing code

## Decision
**Selected Option 3: Explicit Separation with Clear Naming**

Separate agent framework provider from AI model service provider with distinct environment variables and configuration classes.

### New Configuration Architecture
```bash
# Agent Provider (SDK/Framework)
LOAN_PROCESSING_AGENT_PROVIDER=openai_agents_sdk

# AI Model Provider (LLM Service)  
LOAN_PROCESSING_AI_MODEL_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

## Implementation

### Environment Variables Structure
```bash
# =============================================================================
# Agent Provider Configuration (SDK/Framework)
# =============================================================================
# Options: "openai_agents_sdk", "autogen", "semantic_kernel"
LOAN_PROCESSING_AGENT_PROVIDER=openai_agents_sdk

# =============================================================================
# AI Model Provider Configuration (LLM Service)
# =============================================================================
# Options: "openai", "azure_openai", "anthropic"
LOAN_PROCESSING_AI_MODEL_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_key_here

# Azure OpenAI Configuration
# AZURE_OPENAI_API_KEY=your_key_here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Anthropic Configuration  
# ANTHROPIC_API_KEY=your_key_here
```

### Configuration Classes
```python
class AgentProviderType(Enum):
    """Agent SDK/framework provider types."""
    OPENAI_AGENTS_SDK = "openai_agents_sdk"
    AUTOGEN = "autogen"
    SEMANTIC_KERNEL = "semantic_kernel"

class AIModelProviderType(Enum):
    """AI model service provider types."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"

@dataclass
class AgentProviderConfig:
    """Agent SDK/framework configuration."""
    provider_type: AgentProviderType

@dataclass
class AIModelConfig:
    """AI model service provider configuration."""
    provider_type: AIModelProviderType
    api_key: str | None = None
    model: str = "gpt-4"
    # Provider-specific fields...

@dataclass
class SystemConfig:
    """Complete system configuration."""
    agent_provider: AgentProviderConfig
    ai_model: AIModelConfig
    data_services: DataConfig
```

### Validation Strategy
Each provider type validates its own requirements:
```python
def validate(self) -> list[str]:
    if self.provider_type == AIModelProviderType.OPENAI:
        if not self.api_key:
            return ["OPENAI_API_KEY is required for OpenAI provider"]
    elif self.provider_type == AIModelProviderType.AZURE_OPENAI:
        if not self.azure_api_key or not self.azure_endpoint:
            return ["AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required"]
```

### Backward Compatibility
```python
@property 
def ai(self) -> AIModelConfig:
    """Backward compatibility: access ai_model as 'ai'."""
    return self.ai_model
```

## Consequences

### Positive
- **Clear Architectural Separation**: Distinct concerns properly separated
- **Future Flexibility**: Support any combination (e.g., AutoGen + Azure OpenAI)
- **Configuration Clarity**: No ambiguity about what each setting controls
- **Validation Precision**: Each provider validates its own requirements
- **Documentation Improvement**: Clear explanations of each provider type
- **Extensibility**: Easy to add new agent frameworks or AI services

### Negative
- **More Configuration**: Increased number of environment variables
- **Migration Required**: Existing deployments need configuration updates
- **Initial Complexity**: Two provider concepts to understand instead of one

### Migration Impact
- Updated environment variable names across all configuration files
- Updated SystemConfig to include both provider types
- Updated AgentRegistry to use AIModelConfig instead of AIConfig
- Updated all import statements and references
- Maintained backward compatibility property for existing code

## Usage Examples

### Current Supported Combination
```bash
# OpenAI Agents SDK + OpenAI API
LOAN_PROCESSING_AGENT_PROVIDER=openai_agents_sdk
LOAN_PROCESSING_AI_MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Future Supported Combinations
```bash
# AutoGen + Azure OpenAI
LOAN_PROCESSING_AGENT_PROVIDER=autogen
LOAN_PROCESSING_AI_MODEL_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...

# Semantic Kernel + Anthropic Claude
LOAN_PROCESSING_AGENT_PROVIDER=semantic_kernel
LOAN_PROCESSING_AI_MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=...

# OpenAI Agents SDK + Local Model Server
LOAN_PROCESSING_AGENT_PROVIDER=openai_agents_sdk
LOAN_PROCESSING_AI_MODEL_PROVIDER=local
LOCAL_MODEL_ENDPOINT=http://localhost:8080
```

## Implementation Details

### Environment Variable Naming Convention
- **Prefix**: `LOAN_PROCESSING_` for all application settings
- **Agent Provider**: `LOAN_PROCESSING_AGENT_PROVIDER`
- **AI Model Provider**: `LOAN_PROCESSING_AI_MODEL_PROVIDER`
- **Service Keys**: Standard provider naming (OPENAI_API_KEY, etc.)

### Configuration Loading
```python
def from_env(cls) -> "SystemConfig":
    return cls(
        agent_provider=AgentProviderConfig.from_env(),
        ai_model=AIModelConfig.from_env(),
        data_services=DataConfig.from_env(),
    )
```

### Error Handling
- **Invalid Combinations**: Validate that agent provider and AI model provider are compatible
- **Missing Credentials**: Clear error messages for missing API keys
- **Unknown Providers**: Helpful suggestions for valid provider values

## Testing Strategy
- **Unit Tests**: Each configuration class validates independently
- **Integration Tests**: Verify agent registry works with new configuration
- **Backward Compatibility**: Ensure existing code continues to work
- **Configuration Validation**: Test all provider combinations

## Related Decisions
- ADR-009: Development Tooling Language Selection
- ADR-012: Clean Architecture Implementation
- Future: Multi-model support strategy
- Future: Authentication and authorization patterns

## References
- Clean Architecture principles (separation of concerns)
- Configuration management best practices
- Multi-provider system design patterns
- OpenAI Agents SDK documentation
- Azure OpenAI Service configuration guidelines