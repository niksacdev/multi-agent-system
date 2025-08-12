---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# Copilot Instructions - Loan Processing Multi-Agent Sample

## Project Context
This is a **loan processing multi-agent system** demonstrating enterprise-grade architecture. Strategy: be provider portable long-term while keeping initial implementation pragmatic (OpenAI / OpenAI Agents first). Domain models & service abstractions must remain cleanly provider-agnostic; SDK-specific code is isolated so additional adapters (e.g., Microsoft Agent Framework) can be added later with minimal churn.

## Core Architecture
- **Sub-Agents**: Handle complex reasoning (credit assessment, income verification, risk analysis)
- **MCP Tools**: Deterministic operations (APIs, databases, calculations)
- **Business Services**: Domain-focused interfaces independent of AI implementation
- **Provider Boundary (Evolving)**: Start simple (direct OpenAI integration). Introduce minimal `AIProvider` seam only when a second implementation lands.
- **Portability Goal**: Environment/config switch (e.g., `LOAN_AI_PROVIDER=openai|agent_framework`) without user code changes.

## Development Standards

### Python Best Practices (Non-Negotiable)
- **Modern Types**: Use `X | None`, `list[str]`, `dict[str, Any]` (Python 3.10+)
- **Async First**: All I/O operations must be async/await
- **Pydantic v2**: All data models use Pydantic for validation
- **Comprehensive Types**: Every function/method fully type-annotated
- **UV Package Manager**: Use `uv add`, `uv sync`, `uv run` (never pip directly)

### Code Quality Gates
- **Error Handling**: Custom exceptions with proper inheritance
- **Logging**: Structured logging with correlation IDs
- **Testing**: >90% coverage, unit/integration/e2e tests
- **Documentation**: Update docs immediately with code changes
- **Domain Purity**: Models/services contain no SDK type imports

### Provider / SDK Integration
- **Current Default**: OpenAI / OpenAI Agents SDK
- **Separation**: SDK-specific logic lives under `loan_processing/agents` or future `loan_processing/providers/*`
- **No Leakage**: Domain layers (`models`, `services`) never import SDK symbols
- **Future Adapters**: Add new provider files; keep orchestration & business logic unchanged

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

### Project Structure
```
loan_processing/
├── models/          # Pydantic data models
├── services/        # Business service abstractions
├── providers/       # (Future) AI provider adapters
├── tools/           # MCP / tool integration layer
├── agents/          # Concrete agent implementations (current: OpenAI)
└── orchestration/   # Workflow coordination & patterns
```

### Agent Persona
- **Location**: `agent-persona/`
- **Purpose**: System prompts for agents (not general docs)
- **Naming**: `<function>-agent-persona.md`
- **Content**: Domain expertise, business rules, tool usage expectations
- **Constraint**: Avoid provider-specific syntax to preserve portability

## Quality Assurance

### Before Committing
- [ ] All type hints present and correct
- [ ] Tests written and passing (>90% coverage)
- [ ] Documentation updated
- [ ] Lint errors resolved (`ruff check`, `mypy`)
- [ ] Domain layers free of SDK imports
- [ ] Added/changed prompts aligned with persona guidelines

### Code Review Checklist
- [ ] Business logic separated from AI implementation
- [ ] Proper error handling with custom exceptions
- [ ] Async patterns used correctly
- [ ] No leaking SDK types into domain code
- [ ] Tests cover success / failure / malformed provider output
- [ ] Personas avoid provider lock-in

## Copilot Prompt Usage

### Available Prompts
- `/agent-persona` - Review agent code for business compliance
- `/design-review` - Evaluate architecture and design decisions
- `/test-generation` - Create comprehensive test suites
- `/workflow-analysis` - Analyze business process flows
- `/create-adr` - Help document architecture decisions

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