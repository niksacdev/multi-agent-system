# ADR-008: MCP Server Configuration Separation

## Status
Accepted

## Context

Initially, the console application was managing MCP server configuration directly, including server URLs, ports, modules, and health checking. This created several architectural issues:

1. **Violation of Separation of Concerns**: UI layer (console app) managing infrastructure configuration
2. **Tight Coupling**: Console app knowing about backend infrastructure details
3. **API Readiness Blocker**: Infrastructure details embedded in client applications prevent clean API service transition
4. **Configuration Duplication**: MCP server details in both console and backend configs
5. **Maintenance Burden**: Infrastructure changes requiring console app updates

### Previous Architecture (Problematic)
```yaml
# console_app/config/app_config.yaml
mcp_servers:
  servers:
    - name: "application_verification"
      host: "localhost"
      port: 8010
      module: "loan_processing.tools.mcp_servers.application_verification.server"
```

## Decision

**Separate infrastructure configuration from client application configuration**:

1. **Backend Manages Infrastructure**: All MCP server configuration moved to `loan_processing/config/infrastructure.yaml`
2. **Console App Manages UI Only**: Client apps only configure UI preferences and backend connectivity
3. **Health Service Abstraction**: Backend provides health checking service that clients can query without knowing infrastructure details
4. **Future API Readiness**: Architecture supports transition to API-based backend deployment

### New Architecture

#### Backend Infrastructure Configuration
```yaml
# loan_processing/config/infrastructure.yaml
mcp_servers:
  application_verification:
    url: "http://localhost:8010/sse"
    timeout_seconds: 30
    health_check_path: "/health"
    required: true
```

#### Console App Configuration (UI Only)
```yaml
# console_app/config/app_config.yaml
backend:
  mode: "direct"  # or "api" in future
  health_check_enabled: true
  health_check_timeout_seconds: 5
```

#### Health Service Abstraction
```python
# loan_processing/infrastructure/health.py
class InfrastructureHealthService:
    async def get_infrastructure_health() -> InfrastructureHealth:
        # Check all MCP servers, return user-friendly status
        
# console_app/src/backend_health.py  
class BackendHealthChecker:
    async def check_backend_health() -> Tuple[bool, str, List[str]]:
        # Query backend health without knowing infrastructure details
```

## Consequences

### Positive
- **✅ Clean Separation**: UI layer only manages user preferences, backend manages infrastructure
- **✅ API Ready**: Console app can easily switch to API mode without configuration changes
- **✅ Better Error Handling**: Centralized health monitoring with user-friendly messages
- **✅ Security**: Infrastructure details not exposed to client applications
- **✅ Scalability**: Backend can independently scale and manage dependencies
- **✅ Maintainability**: Infrastructure changes don't require client app updates

### Neutral
- **📋 Additional Abstraction**: Health service layer adds complexity but provides clear benefits
- **📋 Import Dependencies**: Console app imports backend modules in "direct" mode (temporary until API mode)

### Negative
- **⚠️ Migration Required**: Existing configurations need to be updated
- **⚠️ Development Setup**: Developers need to understand new health checking flow

## Implementation

### Phase 1: Infrastructure Separation (Completed)
1. Created `loan_processing/config/infrastructure.yaml` with all MCP server configuration
2. Created `loan_processing/infrastructure/health.py` for health monitoring
3. Updated console app configuration to remove infrastructure details
4. Added `console_app/src/backend_health.py` for backend health checking
5. Updated console app to use health checking instead of direct MCP server management

### Phase 2: API Mode (Future)
1. Create REST API endpoints for orchestration
2. Add service discovery and health endpoints
3. Update console app to support API mode
4. Remove direct backend imports from console app

## Validation

### Architecture Validation
- **✅ Console app configuration loads without MCP server details**
- **✅ Backend health service works independently**
- **✅ Health checking provides user-friendly error messages**
- **✅ Console app gracefully handles backend unavailability**

### User Experience
- **Before**: Console app showed cryptic MCP server connection details
- **After**: Console app shows "Backend services unavailable" with clear setup instructions

### Code Organization
- **Before**: Infrastructure config spread across backend and console app
- **After**: Infrastructure config centralized in backend, UI config in console app

## Future Considerations

### API Service Mode
When backend becomes API service:
```yaml
# console_app/config/app_config.yaml
backend:
  mode: "api"
  api_base_url: "https://loan-processing-api.company.com"
```

### Service Discovery
For dynamic service environments:
```yaml
# loan_processing/config/infrastructure.yaml
infrastructure:
  service_discovery_enabled: true
  service_registry_url: "https://consul.company.com"
```

This architectural decision provides a clear separation of concerns and positions the system for future API-based deployment while maintaining excellent developer and user experience.