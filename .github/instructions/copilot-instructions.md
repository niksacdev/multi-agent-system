---
applyTo: '**'
---
<!-- 📋 Sync Note: This file syncs with CLAUDE.md (master reference). Update from CLAUDE.md only. See .github/sync-instructions.md -->

Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# Copilot Instructions - Loan Processing Multi-Agent Sample

## Project Context
This is a **loan processing multi-agent system** demonstrating enterprise-grade architecture using OpenAI Agents SDK with MCP (Model Context Protocol) servers as tools. The system implements autonomous agents that process loan applications through coordinated workflows.

## Critical Lessons Learned

### Token Optimization
- **Problem**: Large persona files (2000+ lines) cause excessive token consumption
- **Solution**: Keep personas under 500 lines with focused directives
- **Result**: 75% token reduction, 10x faster responses

### Context Management
- **Problem**: Context loss after large refactoring leads to conflicting changes
- **Solution**: Use checkpoints, explicit context anchoring, 2-3 hour focused sessions
- **Never**: Run 8+ hour marathon sessions without context management

### Circular Debugging
- **Problem**: AI repeats failed solutions in endless loops
- **Solution**: Track attempted fixes, detect loops, request human intervention
- **Human Role**: Provide strategic pivots and "be pragmatic" guidance

**Key Design Principles**:
- **Agent Autonomy**: Agents autonomously select MCP tools based on their assessment needs
- **Persona-Driven**: Agent behavior defined in markdown personas, not hardcoded logic
- **Clean Orchestration**: Minimal orchestrator code; business logic lives in personas
- **Jobs-to-be-Done Focus**: Agents designed around customer jobs, not internal processes
- **Token Optimized**: Keep personas concise (300-500 lines) for performance
- **Configuration-Driven**: Define orchestration patterns in YAML, not code

## Core Architecture
- **Autonomous Agents**: Four specialized agents (Intake, Credit, Income, Risk) with persona-driven behavior
- **MCP Servers**: Tool servers for application verification, document processing, financial calculations
- **Sequential Orchestration**: Agents process in order, passing context forward
- **Configuration-Driven**: Agent creation from YAML config via `AgentRegistry.create_agent()`
- **Persona Loading**: Agent instructions loaded from markdown files automatically
- **Security First**: Always use `applicant_id` (UUID) instead of SSN for privacy compliance
- **Repository Separation**: Clear separation between agents/ (domain) and tools/ (infrastructure)

## Development Standards

### Python Best Practices (Non-Negotiable)
- **Modern Types**: Use `X | None`, `list[str]`, `dict[str, Any]` (Python 3.10+)
- **Async First**: All I/O operations must be async/await
- **Pydantic v2**: All data models use Pydantic for validation
- **Comprehensive Types**: Every function/method fully type-annotated
- **UV Package Manager**: Use `uv add`, `uv sync`, `uv run` (NEVER pip, poetry, or conda)

### Pre-Commit Quality Checks (MANDATORY)
**CRITICAL**: Run these commands locally BEFORE every commit to prevent CI failures:

```bash
# 1. Code Quality (MANDATORY - must pass)
uv run ruff check .                     # Check for lint issues
uv run ruff check . --fix              # Auto-fix fixable issues
uv run ruff format --check .           # Check code formatting
uv run ruff format .                    # Auto-format code
uv run ruff check .                     # Final verification (must show "All checks passed!")

# 2. Test Validation (MANDATORY - must pass)
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v \
  --cov=loan_processing.agents.providers.openai.agentregistry \
  --cov=loan_processing.agents.shared --cov-report=term-missing    # Must be ≥85% coverage

# 3. Type Checking (RECOMMENDED)
uv run mypy loan_processing/ --ignore-missing-imports

# 4. Complete Validation (shortcut for all checks)
uv run python validate_ci_fix.py
```

**⚠️ NEVER COMMIT if any checks fail. Fix all issues locally first.**

### Code Quality Gates
- **Error Handling**: Custom exceptions with proper inheritance
- **Logging**: Structured logging with correlation IDs
- **Testing**: ≥85% coverage on core components, unit/integration tests
- **Documentation**: Update docs immediately with code changes
- **Domain Purity**: Models/services contain no SDK type imports
- **Pre-Commit Validation**: MANDATORY quality checks before every commit

### Development Workflow
- **Before Coding**: Plan with support agents (product-manager-advisor, system-architecture-reviewer)
- **After Coding**: Run MANDATORY pre-commit checks (ruff, tests, coverage)
- **Before Committing**: Use code-reviewer agent for feedback (only after checks pass)
- **No Exceptions**: Never commit code that breaks quality gates or tests
- **CI/CD Enforcement**: GitHub Actions automatically validate all PRs and commits

### Provider / SDK Integration
- **Current Default**: OpenAI / OpenAI Agents SDK
- **Repository Separation**: 
  - `loan_processing/agents/` - Domain-focused agent creation and orchestration
  - `loan_processing/tools/` - Infrastructure (MCP servers, services)
- **No Leakage**: Domain models never import SDK symbols
- **Provider Isolation**: OpenAI-specific code in `loan_processing/agents/providers/openai/`

## Development Workflow

### Collaborative Development
- **Iterate**: Avoid monolithic feature drops
- **Scope Control**: One cohesive concern per PR
- **Issue-Driven**: Every substantive change references a GitHub issue
- **ADRs**: Required for architectural / cross-cutting changes before code

### Github Issue-Driven Process
1. **Create Issue**: Clear acceptance criteria and design specs
2. **Design Review**: Create/update ADR if architectural change
3. **Implementation**: Build with tests and documentation
4. **Code Review**: Use `/agent-persona` prompts for reviews

### Architecture Decision Records
- **Location**: `docs/decisions/adr-NNN-title.md`
- **Template**: Context → Decision → Consequences → Status
- **Traceability**: Link ADR ↔ Issue ↔ Implementation PR

## File Organization

### Project Structure (Updated)
```
loan_processing/
├── agents/
│   ├── providers/
│   │   └── openai/
│   │       ├── agentregistry.py      # Agent creation from config
│   │       └── orchestration/        # Workflow patterns
│   └── shared/
│       ├── config/
│       │   └── agents.yaml           # Agent configurations
│       ├── models/                   # Pydantic data models
│       └── utils/                    # Shared utilities
└── tools/
    ├── mcp_servers/                  # MCP server implementations
    └── services/                     # Business service abstractions
```

### Agent Persona
- **Location**: `loan_processing/agents/shared/agent-persona/`
- **Purpose**: Complete agent instructions including responsibilities, tool usage, and decision authority
- **Files**: `intake-agent-persona.md`, `credit-agent-persona.md`, `income-agent-persona.md`, `risk-agent-persona.md`
- **Usage**: Configured in `agents.yaml`, loaded automatically via `AgentRegistry`
- **Updates**: Modify personas to change agent behavior without touching orchestrator code
- **Security**: Personas must emphasize using `applicant_id` instead of SSN
- **Optimization**: Keep personas under 500 lines for 10x faster responses
- **Focus**: Clear directives over verbose explanations

## Quality Assurance

### Before Committing
- [ ] **COMMIT OFTEN**: Make atomic commits after each logical change
- [ ] All type hints present and correct
- [ ] Tests written and passing (>90% coverage)
- [ ] **CRITICAL**: Run `uv run pytest tests/test_agent_registry.py -v` and verify all tests pass and coverage is > 90%
- [ ] Documentation updated
- [ ] Lint errors resolved (`ruff check`, `mypy`)
- [ ] Domain layers free of SDK imports
- [ ] Added/changed prompts aligned with persona guidelines
- [ ] No failing tests or reduced coverage
- [ ] **Small PRs**: Target 50-200 lines changed per PR
- [ ] GitHub Actions will automatically validate PR (but test locally first)

### Code Review Checklist
- [ ] Business logic separated from AI implementation
- [ ] Proper error handling with custom exceptions
- [ ] Async patterns used correctly
- [ ] No leaking SDK types into domain code
- [ ] Tests cover success / failure / malformed provider output
- [ ] Personas avoid provider lock-in

## Copilot Prompt Usage

### Development Guidelines
- **Package Manager**: ALWAYS use `uv` commands (`uv run`, `uv add`, `uv sync`) - NEVER pip/poetry
- **Adding Agents**: Create persona markdown in `agents/shared/agent-persona/`, add config to `agents.yaml`, use `AgentRegistry.create_agent()`
- **Modifying Behavior**: Update persona files or `agents.yaml` config, not orchestrator code
- **MCP Integration**: Agents autonomously select tools based on persona instructions
- **Testing**: Run `uv run pytest tests/test_agent_registry.py` before commits
- **Demo Scripts**: Use `uv run python demo_sequential_processing.py` to test workflows

### When to Use Prompts
- **Design Phase**: `/design-review` for architecture validation
- **Implementation**: `/agent-persona` for code review
- **Testing**: `/test-generation` for comprehensive test coverage
- **Documentation**: `/create-adr` for significant decisions

## Success Criteria
- **Pragmatic Now / Portable Later**: Working OpenAI implementation with clear seams for additional providers
- **Provider-Ready Domain**: Models & services contain zero SDK references
- **Enterprise Ready**: Error handling, logging, OTEL-friendly instrumentation points
- **Educational Value**: Separation of concerns visibly demonstrable
- **Production Quality**: Comprehensive tests, documentation, type safety
- **Business Focused**: Services represent actual loan processing capabilities
- **Config Swap Path**: Documented plan for env-based provider selection

Remember: This sample demonstrates how to build **enterprise-grade multi-agent systems**. Favor clarity and maintainability now while preserving a low-friction path to multi-provider support.