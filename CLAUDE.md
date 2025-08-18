# Claude Development Rules for Multi-Agent System

> **📋 Instruction Sync**: This is the **master reference** for all development practices. When updating, sync changes to `.cursorrules` and `.github/instructions/copilot-instructions.md`. See `.github/sync-instructions.md` for guidelines.

## Project Overview
This is a Multi-Agent Loan Processing System using OpenAI Agents SDK with MCP (Model Context Protocol) servers as tools. The system implements autonomous agents that process loan applications through a coordinated workflow.

## Development Support Agents (USE PROACTIVELY)

### Available Support Agents
Claude has access to specialized development agents that MUST be used proactively for brainstorming, design validation and implementation:

1. **system-architecture-reviewer**: 
   - USE WHEN: Designing new features, reviewing system architecture, analyzing impacts
   - PROVIDES: Architecture guidance, system design reviews, impact analysis

2. **product-manager-advisor**:
   - USE WHEN: Creating GitHub issues, defining requirements, making technical decisions
   - PROVIDES: Business value alignment, user story creation, test validation

3. **ux-ui-designer**:
   - USE WHEN: Designing UI components, validating user experience, creating interfaces
   - PROVIDES: Design validation, UI/UX improvements, usability analysis

4. **code-reviewer**:
   - USE WHEN: After writing significant code, before committing changes
   - PROVIDES: Best practices feedback, architecture alignment, code quality review

### When to Use Support Agents

#### MANDATORY Usage:
- **Before Implementation**: Use system-architecture-reviewer for design validation
- **After Code Writing**: Use code-reviewer for all significant code changes
- **For UI Changes**: Use ux-ui-designer for any user-facing components
- **For Requirements**: Use product-manager-advisor when creating features or issues

#### Proactive Usage Pattern:
```
1. User requests feature → Use product-manager-advisor for requirements
2. Design solution → Use system-architecture-reviewer for validation  
3. Implement code → Write the implementation
4. Pre-commit checks → Run MANDATORY local quality checks (ruff, tests, coverage)
5. Review code → Use code-reviewer for feedback (AFTER checks pass)
6. If UI involved → Use ux-ui-designer for validation
```

## Architecture Principles

### 1. Agent Autonomy
- **Agents are autonomous**: Each agent decides which MCP tools to use based on their assessment needs
- **Persona-driven behavior**: Agent instructions are loaded from persona markdown files
- **No hardcoded logic**: Avoid embedding business logic in orchestrator code

### 2. Clean Orchestration
- **Minimal orchestrator code**: Orchestrators should only handle agent coordination and context passing
- **Use personas for instructions**: All agent-specific logic lives in persona files
- **Context accumulation**: Pass previous agent assessments as context to subsequent agents

### 3. MCP Server Integration
- **Tool selection by agents**: Agents autonomously select appropriate MCP servers based on needs
- **Secure parameters**: Always use `applicant_id` (UUID) instead of SSN for privacy compliance
- **Multiple server access**: Agents can access multiple MCP servers for comprehensive functionality

## Repository Architecture (Updated)

### Directory Structure
```
loan_processing/
├── agents/
│   ├── providers/
│   │   └── openai/
│   │       ├── agentregistry.py      # Agent creation and configuration
│   │       └── orchestration/        # Orchestration patterns (sequential, parallel)
│   └── shared/
│       ├── config/
│       │   └── agents.yaml           # Agent configurations and MCP server mappings
│       ├── models/                   # Data models (application, assessment, decision)
│       ├── utils/                    # Shared utilities (config loader, output formatter, persona loader)
│       └── agent-persona/            # Agent instruction markdown files
├── tools/
│   ├── mcp_servers/                  # MCP server implementations
│   │   ├── application_verification/
│   │   ├── document_processing/
│   │   └── financial_calculations/
│   └── services/                     # Business services used by MCP servers
```

### Configuration-Driven Agent Creation
The system now uses YAML configuration for agent definitions and a registry pattern:

```yaml
# loan_processing/agents/shared/config/agents.yaml
agents:
  intake:
    name: "Intake Agent" 
    persona_file: "intake"
    mcp_servers: ["application_verification", "document_processing"]
    capabilities: ["Application validation", "Identity verification"]
    output_format:
      validation_status: "string"
      confidence_score: "number"
```

```python
# Agent creation via registry
from loan_processing.agents.providers.openai.agentregistry import AgentRegistry

# Create any agent type from configuration
agent = AgentRegistry.create_agent("intake", model="gpt-4")
```

### Shared Utilities
- **ConfigurationLoader**: Loads and validates YAML configuration
- **OutputFormatGenerator**: Adds structured output instructions to agent personas  
- **persona_loader**: Loads agent persona files from `agents/shared/agent-persona/` directory

## Development Guidelines

### Pre-Commit Quality Checks (MANDATORY)

**CRITICAL**: Always run these checks locally BEFORE making any commit to prevent GitHub Actions failures:

#### 1. Code Quality Checks (MANDATORY)
```bash
# Run ALL checks in this exact order before committing:

# 1. Linting check (must pass)
uv run ruff check .

# 2. Auto-fix any fixable issues
uv run ruff check . --fix

# 3. Format check (must pass)
uv run ruff format --check .

# 4. Auto-format if needed
uv run ruff format .

# 5. Final verification (must show "All checks passed!")
uv run ruff check .
```

#### 2. Test Validation (MANDATORY)
```bash
# Run core stable tests (must pass)
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v

# Run with coverage check (must be ≥85%)
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v \
  --cov=loan_processing.agents.providers.openai.agentregistry \
  --cov=loan_processing.agents.shared \
  --cov-report=term-missing
```

#### 3. Type Checking (RECOMMENDED)
```bash
# Check types (warnings okay, but no errors)
uv run mypy loan_processing/ --ignore-missing-imports
```

#### 4. Complete Pre-Commit Validation Script
Use the validation script to check everything at once:
```bash
uv run python validate_ci_fix.py
```

**⚠️ NEVER COMMIT if any of these checks fail. Fix issues locally first.**

#### Integration with Support Agents
- **ALWAYS run pre-commit checks** before using the code-reviewer agent
- **Include check results** when asking for agent feedback
- **Fix any issues** identified by checks before requesting code review

### Commit Best Practices

#### Commit Frequency (CRITICAL)
- **Commit often**: After each logical change (not after hours of work)
- **Atomic commits**: One logical change per commit
- **Small PRs**: Target 50-200 lines changed per PR
- **Test before commit**: Always run tests before committing

#### Good Commit Examples
```bash
# ✅ Good: Specific, focused commits
git commit -m "feat: add agent registry configuration loading"
git commit -m "test: add coverage for persona loading functionality" 
git commit -m "fix: update persona_loader path for shared directory"
git commit -m "docs: sync .cursorrules with new repository structure"

# ❌ Bad: Large, unfocused commits
git commit -m "update everything"
git commit -m "fix tests and update docs and refactor code"
```

#### Commit Message Format
```
<type>: <short description>

<optional longer description>
<optional breaking changes>
<optional issues closed>
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Support Agent Integration
- **ALWAYS consult appropriate support agents** before making significant changes
- **Use Task tool** to launch support agents with detailed prompts
- **Document agent recommendations** in commit messages or PR descriptions
- **Iterate based on feedback** from support agents before finalizing

### ADR Documentation for Support Agent Feedback
**MANDATORY**: When support agents provide feedback that leads to accepted changes, create an Architecture Decision Record:

- **Location**: `docs/decisions/adr-XXX-[descriptive-title].md`
- **Format**: Follow existing ADR template with Status, Context, Decision, Consequences, Implementation
- **Content Requirements**:
  - Document specific feedback received from support agents
  - Detail what changes were made and implementation approach
  - Explain rationale for decisions to help future developers
  - Include support agent assessment scores/grades when provided
  - List any outstanding issues identified but not yet addressed
  - Reference which support agents provided the feedback

**Purpose**: Create clear audit trail so future developers understand why architectural and implementation decisions were made

### 1. Adding New Agents
- Create persona markdown file in `loan_processing/agents/shared/agent-persona/`
- Add agent configuration in `loan_processing/agents/shared/config/agents.yaml`
- Configure MCP servers, capabilities, and output formats
- Use `AgentRegistry.create_agent()` to create instances
- Personas are loaded automatically via configuration

### 2. Modifying Agent Behavior
- **Update persona files**, not code
- Keep orchestrator code unchanged
- Test with demo scripts to verify behavior

### 3. MCP Server Usage
- Agents select tools autonomously based on their persona instructions
- Never hardcode tool selection in orchestrator
- Ensure all MCP servers use secure parameters (applicant_id, not SSN)

### 4. Orchestration Patterns
- **Sequential**: Agents process in order, passing context forward
- **Parallel**: Agents process simultaneously (future implementation)
- **Hybrid**: Combination of sequential and parallel (future implementation)

## Security & Privacy

### Critical Rules
1. **NEVER use SSN** in tool calls - always use `applicant_id`
2. **Secure all PII** - encrypt sensitive data in transit and at rest
3. **Audit logging** - maintain audit trails for all agent decisions
4. **Access control** - limit MCP server access to authorized agents only

## Testing Guidelines

### Package Manager: Use uv Only
**CRITICAL**: Always use `uv` for all package management and test execution:
- `uv add package` - Add dependencies
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
- Never use pip, poetry, or conda

### Current Test Status
Working tests:
- `tests/test_agent_registry.py` - Agent creation, configuration, and MCP server factory tests (27 tests passing)
- `tests/tools_tests/test_utils.py` - Utility function tests

### Test Commands
```bash
# Run core tests with coverage
uv run pytest tests/test_agent_registry.py tests/tools_tests/test_utils.py -v --cov=loan_processing --cov-report=term-missing

# Quick validation
uv run python validate_tests.py

# Agent registry tests only 
uv run pytest tests/test_agent_registry.py -v
```

### 1. Agent Registry Tests
- Test agent configuration loading from YAML
- Verify MCP server factory and caching
- Test structured output format generation
- Verify agent creation with all configurations
- Test utility methods (capabilities, info, types)

### 2. Integration Tests (In Progress)
- Full workflow tests need updating for new structure
- Agent coordination and context passing
- Error handling and edge cases

### 3. Console Application
- `console_app/src/main.py` - Standalone console application (decoupled from backend)
- `console_app/config/` - App-specific configuration system
- `run_console_app.py` - Easy launcher script from project root
- Include sample data that exercises different decision paths
- Document expected outcomes and user interactions

## Performance Considerations

### 1. Agent Efficiency
- Agents should complete assessments within defined time limits
- Use appropriate model sizes (gpt-3.5-turbo for speed, gpt-4 for accuracy)
- Cache MCP server responses when appropriate

### 2. Orchestrator Optimization
- Minimize context size passed between agents
- Use parallel processing where assessments are independent
- Implement timeout handling for long-running operations

## Maintenance & Evolution

### 1. Persona Updates
- Review and update personas based on business requirements
- Version control persona changes
- Test thoroughly after persona modifications

### 2. Adding MCP Servers
- Create new MCP server following existing patterns
- Update relevant agents to include new server access
- Document new tool capabilities in agent personas

### 3. Monitoring & Observability
- Log all agent decisions and tool usage
- Track processing times and success rates
- Monitor MCP server availability and performance

## Development Workflows with Support Agents

### Feature Development Workflow
```
1. User Request → Use product-manager-advisor:
   - Analyze requirements and business value
   - Create proper GitHub issues
   - Define acceptance criteria

2. Design Phase → Use system-architecture-reviewer:
   - Review proposed architecture changes
   - Analyze system impacts
   - Validate design decisions

3. Implementation → Write code following patterns

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify ≥85% coverage on core components

5. Code Review → Use code-reviewer (ONLY after checks pass):
   - Review for best practices
   - Check architecture alignment
   - Validate code quality

6. UI Components → Use ux-ui-designer (if applicable):
   - Review user experience
   - Validate interface design
   - Ensure usability standards

7. Document Decisions → Create ADR (MANDATORY):
   - Document context and changes made based on support agent feedback
   - Explain rationale for future developers
   - Include support agent assessments and scores
   - Track outstanding issues for future implementation
```

### Bug Fix Workflow
```
1. Issue Analysis → Use system-architecture-reviewer:
   - Understand system impact
   - Identify root cause areas

2. Solution Design → Use product-manager-advisor:
   - Validate business impact
   - Prioritize fix approach

3. Implementation → Write fix

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify fix doesn't break existing functionality

5. Review → Use code-reviewer (ONLY after checks pass):
   - Ensure fix doesn't introduce regressions
   - Validate approach

6. Document Fix → Create ADR (if significant):
   - Document root cause analysis from support agents
   - Explain solution approach and alternatives considered
   - Record lessons learned for future similar issues
```

## Common Patterns

### Sequential Processing
```python
context = {"application": application_data}
context["intake_result"] = await intake_agent.run(context)
context["credit_result"] = await credit_agent.run(context)
context["income_result"] = await income_agent.run(context)
final_decision = await risk_agent.run(context)
```

### Error Handling
```python
try:
    result = await agent.run(input)
except MCPServerError:
    # Handle MCP server failures
except AgentTimeoutError:
    # Handle agent timeouts
```

## Best Practices

1. **Use support agents proactively** - Consult architecture, PM, design, and code review agents
2. **Keep orchestrators thin** - Business logic in personas, not code
3. **Validate with experts** - Use system-architecture-reviewer before implementing
4. **Review all code** - Use code-reviewer agent after writing significant code
5. **Define requirements properly** - Use product-manager-advisor for feature planning
6. **Design user experiences** - Use ux-ui-designer for any user-facing components
7. **Document tool usage** - Clear descriptions in agent personas
8. **Test comprehensively** - Unit, integration, and end-to-end tests
9. **Monitor production** - Track metrics and agent performance
10. **Iterate on personas** - Continuously improve based on outcomes

## Quick Reference

### Key Files
- Agent Personas: `loan_processing/agents/shared/agent-persona/*.md`
- Agent Registry: `loan_processing/agents/providers/openai/agentregistry.py`
- Agent Configuration: `loan_processing/agents/shared/config/agents.yaml`
- Orchestrators: `loan_processing/agents/providers/openai/orchestration/*.py`
- MCP Servers: `loan_processing/tools/mcp_servers/*/server.py`
- Console Application: `console_app/src/main.py`
- Console Configuration: `console_app/config/app_config.yaml`
- App Launcher: `run_console_app.py`

### Common Commands
```bash
# Package Management (Use uv for all package operations)
uv sync                     # Install dependencies
uv add package_name        # Add new dependency
uv add --dev package_name  # Add development dependency

# Run MCP servers
uv run python -m loan_processing.tools.mcp_servers.application_verification.server
uv run python -m loan_processing.tools.mcp_servers.document_processing.server
uv run python -m loan_processing.tools.mcp_servers.financial_calculations.server

# Run console application
uv run python run_console_app.py

# Run tests
uv run pytest tests/test_agent_registry.py -v                           # Agent registry tests
uv run pytest tests/tools_tests/test_utils.py -v                       # Utility tests
uv run pytest tests/test_agent_registry.py --cov=loan_processing       # With coverage

# Test validation
uv run python validate_tests.py    # Quick validation
uv run python run_tests.py          # Full test suite (when all tests are updated)
```

### Environment Variables
- `OPENAI_API_KEY`: Required for agent operation
- `MCP_SERVER_HOST`: Host for MCP servers (default: localhost)
- `MCP_SERVER_PORTS`: Port configuration for MCP servers
- make sure test pass and test coverage is > 90%