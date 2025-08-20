# ADR-007: Configuration System Architecture for Console Application

## Status

Accepted

## Context

The console application was directly accessing agent configuration directories through filesystem navigation, creating tight coupling and violating separation of concerns. This approach was problematic for several reasons:

### Issues with Previous Architecture

1. **Tight Coupling**: Console app directly accessed agent directory structure
   ```python
   # BEFORE: Direct filesystem access
   patterns_dir = Path(__file__).parent.parent.parent / "agents" / "shared" / "config"
   pattern_files = [f.stem for f in patterns_dir.glob("*.yaml") if f.stem != "agents"]
   ```

2. **Brittle Path Dependencies**: Hard-coded relative paths that break easily
3. **Separation of Concerns Violation**: Application layer knew agent implementation details
4. **Future API Incompatibility**: Approach wouldn't work when agents become services
5. **Limited Configuration Sources**: Only supported local YAML files
6. **No Dependency Injection**: Hard to test and maintain

### Requirements for Improvement

- Console application decoupled from agent implementation details
- Support for OpenAI and Azure OpenAI configurations
- Configurable orchestration patterns without direct filesystem access
- Future-ready for API-based agent services
- Support multiple configuration sources (.env, JSON, YAML)
- Dependency injection pattern for configuration
- Clean separation between application and agent layers

## Decision

**Implement a layered configuration architecture with dependency injection and multiple provider support.**

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Console Application                      │
├─────────────────────────────────────────────────────────────┤
│                  Dependency Container                       │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │ Configuration   │  │        Orchestrator             │  │
│  │    Service      │  │       (Injected)                │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│              Configuration Providers                        │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │  Environment    │  │       Future: API               │  │
│  │   Provider      │  │       Provider                  │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                Configuration Sources                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    .env     │ │   YAML      │ │      Agent Service      │ │
│  │    files    │ │   files     │ │         API             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Configuration Service Layer
- **ConfigurationProvider**: Abstract interface for configuration sources
- **EnvironmentConfigurationProvider**: Default implementation using env vars and files
- **ConfigurationService**: Main service interface for the application

#### 2. Dependency Injection Container
- **DependencyContainer**: Manages all application dependencies
- **Global factory functions**: Convenient access to common dependencies
- **Initialization and lifecycle management**: Proper setup and teardown

#### 3. Configuration Models
- **ApplicationSettings**: Main application configuration (Pydantic model)
- **AgentProviderConfig**: Agent provider settings (OpenAI, Azure)
- **OrchestrationPatternInfo**: Pattern metadata and descriptions

### Implementation Details

#### Configuration Loading Strategy
```python
# Priority order for configuration loading:
1. Environment variables (highest priority)
2. Configuration files (.env, YAML, JSON)
3. Default values (lowest priority)

# Pattern discovery strategy:
1. Agent service API (future - production)
2. Local configuration files (current - development)  
3. Hardcoded defaults (fallback)
```

#### Dependency Injection Pattern
```python
# AFTER: Clean dependency injection
async def get_available_patterns() -> list[str]:
    patterns = await get_available_patterns()  # Via DI
    return [pattern.name for pattern in patterns]

# Orchestrator access via DI
orchestrator = await get_orchestrator()
decision = await orchestrator.execute_pattern(...)
```

#### Multi-Provider Support
```yaml
# Environment configuration for different providers
agent_provider:
  provider_type: "openai"  # or "azure_openai"
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4"

# Azure configuration
agent_provider:
  provider_type: "azure_openai"
  api_key: "${AZURE_OPENAI_KEY}"
  api_base: "${AZURE_OPENAI_ENDPOINT}"
  api_version: "2024-02-01"
  deployment_name: "${AZURE_OPENAI_DEPLOYMENT}"
```

## File Structure

```
loan_processing/
├── app/
│   ├── shared/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── app_settings.py      # Configuration models and providers
│   │   │   └── app_config.yaml      # Default application configuration
│   │   └── dependencies.py          # Dependency injection container
│   └── console/
│       └── main.py                  # Updated console app (no direct FS access)
├── .env.example                     # Environment configuration template
└── docs/decisions/
    └── adr-007-configuration-system-architecture.md
```

## Migration Path

### Phase 1: Implement Configuration Layer (Completed)
1. ✅ Create configuration service and models
2. ✅ Implement dependency injection container
3. ✅ Update console application to use DI
4. ✅ Create environment configuration template
5. ✅ Maintain backward compatibility with local files

### Phase 2: Transition Period (Current)
- Applications use local file access via configuration provider
- Environment variables override file-based settings
- Pattern source configurable via `LOAN_PROCESSING_PATTERNS_SOURCE`
- Full backward compatibility maintained

### Phase 3: API Integration (Future)
- Add API-based configuration provider
- Implement agent service discovery
- Support for distributed configuration management
- Graceful fallback to local configuration

## Benefits

### Immediate Benefits
1. **Separation of Concerns**: Console app no longer knows about agent directory structure
2. **Configuration Flexibility**: Support for multiple configuration sources
3. **Environment-Specific Settings**: Easy configuration for dev/staging/production
4. **Testability**: Mockable dependencies and configuration
5. **Provider Agnostic**: Easy switching between OpenAI and Azure OpenAI

### Future Benefits
1. **API Readiness**: Easy transition to service-based agent discovery
2. **Scalability**: Configuration can be distributed and cached
3. **Monitoring**: Built-in health checks and validation
4. **Multi-Environment**: Consistent deployment across environments

## Consequences

### Positive
- ✅ **Clean Architecture**: Proper separation between layers
- ✅ **Flexibility**: Multiple configuration sources and providers
- ✅ **Future-Proof**: Ready for API-based agent services
- ✅ **Maintainability**: Testable and mockable dependencies
- ✅ **Environment Support**: Easy configuration management

### Negative
- ❌ **Complexity**: More files and abstraction layers
- ❌ **Learning Curve**: Developers need to understand DI pattern
- ❌ **Migration Effort**: Existing code needs to be updated

### Risks and Mitigations

**Risk**: Configuration complexity could confuse developers
**Mitigation**: Comprehensive documentation and examples provided

**Risk**: Dependency injection might be overkill for simple console app
**Mitigation**: DI container provides factory functions for easy access

**Risk**: Multiple configuration sources could cause conflicts
**Mitigation**: Clear priority order documented and implemented

## Implementation Examples

### Before (Problematic)
```python
def get_available_patterns(self) -> list[str]:
    patterns_dir = Path(__file__).parent.parent.parent / "agents" / "shared" / "config"
    pattern_files = [f.stem for f in patterns_dir.glob("*.yaml") if f.stem != "agents"]
    return pattern_files
```

### After (Clean)
```python
async def get_available_patterns(self) -> list[str]:
    patterns = await get_available_patterns()  # Via configuration service
    return [pattern.name for pattern in patterns]

# Dependency injection in main
async def main():
    config_file = Path(__file__).parent.parent / "shared" / "config" / "app_config.yaml"
    await initialize_container(
        config_file=str(config_file) if config_file.exists() else None,
        patterns_source="local_files"
    )
    console = LoanProcessingConsole()
    await console.run_interactive_mode()
```

### Configuration Usage
```python
# Get settings via DI
settings = await get_application_settings()
orchestrator = await get_orchestrator()
patterns = await get_available_patterns()

# Environment variable configuration
export LOAN_PROCESSING_AGENT_PROVIDER=azure_openai
export AZURE_OPENAI_KEY=your_key_here
export LOAN_PROCESSING_PATTERNS_SOURCE=agent_service
```

## Future Enhancements

### Short-term
1. Add configuration validation and error reporting
2. Implement configuration hot-reloading
3. Add metrics and monitoring for configuration health

### Medium-term  
1. Implement API-based configuration provider
2. Add distributed configuration with Redis/etcd
3. Support for configuration versioning and rollback

### Long-term
1. Service mesh integration for configuration discovery
2. Multi-region configuration synchronization
3. Advanced configuration templating and inheritance

## Related

- **Previous**: Direct filesystem access in console application
- **Impact**: All future console applications should use this pattern
- **Dependencies**: None - this is foundational architecture
- **Follow-up**: API provider implementation when agent services are available

**Implementation Author:** Claude (with system-architecture-reviewer guidance)  
**Decision Date:** 2024-08-18  
**Review Date:** After API provider implementation