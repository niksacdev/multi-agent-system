# ADR-009: Development Tooling Language Selection (Python vs Shell)

## Status
Accepted

## Context
Need to choose between Python scripts vs shell scripts for development tooling, specifically MCP server management and future development utilities.

### Problem Statement
The multi-agent loan processing system requires MCP (Model Context Protocol) servers to be running before agents can access data services. Developers need a simple way to start, stop, and monitor these servers during development.

### Key Requirements
- Cross-platform compatibility (Windows, macOS, Linux)
- Process lifecycle management (start, stop, status checking)
- Developer-friendly error messages and feedback
- Integration with existing Python ecosystem
- PID tracking and proper process cleanup
- Future extensibility for monitoring and health checks

### Alternatives Considered

#### Option 1: Shell Scripts (Unix) + Batch Files (Windows)
```bash
#!/bin/bash
# start_mcp_servers.sh
python -m loan_processing.tools.mcp_servers.application_verification.server &
python -m loan_processing.tools.mcp_servers.document_processing.server &
python -m loan_processing.tools.mcp_servers.financial_calculations.server &
```

**Pros:**
- Native to Unix/Linux environments
- Faster startup
- Simple for basic server orchestration
- Lighter weight

**Cons:**
- Platform-specific (need separate .bat for Windows)
- Limited error handling capabilities
- Difficult to track PIDs reliably across platforms
- No structured status reporting
- Hard to extend for complex management features

#### Option 2: Python Development Tool
```python
class MCPServerManager:
    def start_servers(self):
        # Cross-platform process management
        # PID tracking with JSON persistence
        # Rich status reporting and error handling
```

**Pros:**
- Cross-platform (Windows, macOS, Linux)
- Rich error handling and user feedback
- JSON-based PID tracking
- Consistent with project's Python ecosystem
- Easy to extend for health checks and monitoring
- Proper process lifecycle management

**Cons:**
- Slower startup than shell scripts
- More complex for simple tasks
- Requires Python runtime (already required for project)

## Decision
**Selected Option 2: Python Development Tool**

Use Python for development tooling scripts rather than shell scripts, specifically:
- Server management: `start_mcp_servers.py`
- Future development tools: Python-based approach
- Exception: Simple CI/CD tasks can use shell when appropriate

### Rationale
1. **Distributed Systems Best Practice**: Multi-process management with proper PID tracking and status monitoring aligns with distributed systems patterns
2. **Developer Experience**: Rich error messages, cross-platform compatibility, and user-friendly feedback
3. **Architectural Consistency**: Maintains single-language ecosystem for main codebase and tooling
4. **Extensibility**: Easy to add health checks, monitoring, and integration with future observability tools
5. **Reliability**: Robust process management with proper cleanup and error handling

## Consequences

### Positive
- **Cross-Platform Support**: Single tool works on Windows, macOS, and Linux
- **Rich Process Management**: PID tracking, status monitoring, proper cleanup
- **Developer Experience**: Clear error messages, help text, and status reporting
- **Maintainability**: Consistent with project's Python ecosystem and patterns
- **Extensibility**: Easy to add health checks, metrics, and monitoring features
- **Integration**: Can leverage existing Python dependencies and patterns

### Negative
- **Startup Overhead**: Slightly slower than shell scripts (negligible for development use)
- **Complexity**: More verbose than simple shell scripts for basic tasks
- **Dependencies**: Requires Python runtime (already required for project)

## Implementation

### Current Implementation
Created `start_mcp_servers.py` with:
- Cross-platform process management
- JSON-based PID file management for process tracking
- Status checking with detailed server information
- Proper error handling and user feedback
- Help system and command-line interface

### Usage
```bash
# Start all MCP servers
python start_mcp_servers.py

# Check server status
python start_mcp_servers.py --status

# Stop all servers
python start_mcp_servers.py --stop
```

### Future Enhancements
Based on architect feedback, planned extensions include:
- Health check endpoints for servers
- Performance monitoring capabilities
- Integration with project logging systems
- Docker/container support for production deployments

### Development Tool Pattern
Established pattern for future Python-based development tools:
```python
class DevelopmentTool:
    def __init__(self):
        self.config = self.load_config()
        
    def execute(self) -> bool:
        try:
            return self._do_work()
        except Exception as e:
            self._handle_error(e)
            return False
```

## Related Decisions
- ADR-010: MCP Server Lifecycle Management Strategy
- Future: Container orchestration strategy for production deployments

## References
- System Architecture Review: Development tooling analysis
- Cross-platform process management best practices
- Distributed systems monitoring patterns