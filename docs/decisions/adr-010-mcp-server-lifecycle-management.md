# ADR-010: MCP Server Lifecycle Management Strategy

## Status
Accepted

## Context
The multi-agent loan processing system requires MCP (Model Context Protocol) servers to provide data services to autonomous agents. These servers must be running before the console application can process loan applications.

### Problem Statement
- Agents need access to three MCP servers for loan processing workflow
- Developers were required to manually start servers in separate terminals
- No centralized way to monitor server health or manage lifecycle
- Error messages provided unclear guidance on server startup
- Poor developer experience for onboarding new team members

### Current MCP Server Architecture
The system requires three specialized MCP servers:

1. **Application Verification Server** (Port 8010)
   - Validates loan applications and fraud detection
   - Module: `loan_processing.tools.mcp_servers.application_verification.server`

2. **Document Processing Server** (Port 8011)
   - Processes and analyzes loan documents
   - Module: `loan_processing.tools.mcp_servers.document_processing.server`

3. **Financial Calculations Server** (Port 8012)
   - Performs financial calculations and risk assessments
   - Module: `loan_processing.tools.mcp_servers.financial_calculations.server`

### Previous State (Manual Management)
Developers had to manually start each server:
```bash
# Terminal 1
uv run python -m loan_processing.tools.mcp_servers.application_verification.server

# Terminal 2
uv run python -m loan_processing.tools.mcp_servers.document_processing.server

# Terminal 3
uv run python -m loan_processing.tools.mcp_servers.financial_calculations.server

# Terminal 4 - Finally run the application
uv run python run_console_app.py
```

### Alternatives Considered

#### Option 1: Keep Manual Management
**Pros:** Simple, no additional tooling needed
**Cons:** Poor developer experience, error-prone, hard to onboard new developers

#### Option 2: Docker Compose
**Pros:** Industry standard, isolated environments, reproducible
**Cons:** Adds Docker dependency, overkill for development, slower iteration

#### Option 3: Process Manager (PM2, Supervisor)
**Pros:** Professional process management, monitoring capabilities
**Cons:** Additional dependencies, complexity for development use

#### Option 4: Custom Python Server Manager
**Pros:** Integrated with project, customizable, cross-platform
**Cons:** Need to build and maintain custom tooling

## Decision
**Selected Option 4: Custom Python Server Manager**

Implemented `start_mcp_servers.py` providing centralized MCP server lifecycle management with:
- One-command startup and shutdown
- Process ID tracking and management
- Status monitoring and health checking
- Cross-platform compatibility
- Integration with existing development workflow

## Implementation

### Server Manager Features
```python
class MCPServerManager:
    def start_servers(self) -> bool:
        """Start all MCP servers in background processes."""
        
    def stop_servers(self) -> bool:
        """Stop all running MCP servers."""
        
    def check_status(self):
        """Check status of all MCP servers."""
```

### Process Lifecycle Management
- **Startup**: Servers started as detached background processes
- **PID Tracking**: JSON file stores process information for management
- **Health Monitoring**: Process existence checks and port validation
- **Cleanup**: Proper process termination with SIGTERM

### Developer Workflow Integration
```bash
# New simplified workflow
python start_mcp_servers.py          # Start all servers
uv run python run_console_app.py     # Run application

# Server management
python start_mcp_servers.py --status  # Check status
python start_mcp_servers.py --stop    # Stop all servers
```

### Error Handling Strategy
- **Startup Failures**: Clear error messages with remediation steps
- **Process Monitoring**: Detects when servers terminate unexpectedly
- **Port Conflicts**: Identifies and reports port usage conflicts
- **Recovery Guidance**: Provides specific commands for troubleshooting

### Cross-Platform Compatibility
- **Windows**: Uses `tasklist` and `taskkill` for process management
- **Unix/Linux/macOS**: Uses POSIX signals and process management
- **PID File Format**: JSON structure for reliable cross-platform parsing

## Consequences

### Positive
- **Developer Experience**: Reduced from 4 commands to 1 for startup
- **Onboarding**: New developers can start system immediately
- **Reliability**: Proper process lifecycle management and cleanup
- **Monitoring**: Centralized status checking and health monitoring
- **Documentation**: Clear error messages and troubleshooting guidance
- **Maintainability**: Single tool for all server management operations

### Negative
- **Additional Code**: Need to maintain custom server management tool
- **Complexity**: More sophisticated than simple shell scripts
- **Learning Curve**: Developers need to learn new management commands

### Risks and Mitigation
- **PID File Corruption**: Validates PID file format and handles corruption gracefully
- **Port Conflicts**: Checks port availability and provides clear error messages
- **Process Orphaning**: Uses proper process group management to prevent orphans
- **Platform Differences**: Tested across Windows, macOS, and Linux platforms

## Usage Examples

### Starting Servers
```bash
$ python start_mcp_servers.py
🚀 Starting MCP servers for loan processing...

Starting Application Verification (port 8010)...
   ✅ Started successfully (PID: 12345)
Starting Document Processing (port 8011)...
   ✅ Started successfully (PID: 12346)
Starting Financial Calculations (port 8012)...
   ✅ Started successfully (PID: 12347)

🎉 Successfully started 3/3 MCP servers
✅ All MCP servers are running! You can now use:
   uv run python run_console_app.py
```

### Checking Status
```bash
$ python start_mcp_servers.py --status
📊 MCP Server Status

✅ Application Verification   Port 8010 PID 12345  (Running)
✅ Document Processing        Port 8011 PID 12346  (Running)
✅ Financial Calculations     Port 8012 PID 12347  (Running)

Status: 3/3 servers running
✅ All servers operational!
```

## Integration Points

### Console Application Updates
- **Prerequisites Display**: Shows new startup command in help text
- **Error Messages**: Updated to reference server management tool
- **Troubleshooting**: Provides specific commands for server management

### Documentation Updates
- **README.md**: Updated quick start to include server management
- **Developer Guide**: Added server management section
- **Troubleshooting**: Centralized server-related troubleshooting

## Future Enhancements
Based on architect recommendations:
- **Health Check Endpoints**: HTTP health checks for servers
- **Performance Monitoring**: Server response time and throughput metrics
- **Log Aggregation**: Centralized logging for all MCP servers
- **Container Support**: Docker integration for production deployments
- **Service Discovery**: Dynamic server discovery for distributed deployments

## Related Decisions
- ADR-009: Development Tooling Language Selection (Python vs Shell)
- Future: Container orchestration for production environments
- Future: Observability and monitoring strategy

## References
- MCP Protocol Specification
- Process management best practices
- Cross-platform Python process handling
- Distributed systems monitoring patterns