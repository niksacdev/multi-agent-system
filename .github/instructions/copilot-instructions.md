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
**CRITICAL**: Run validation locally BEFORE every commit to prevent CI failures.

**Quick Validation**: `uv run python scripts/validate_ci_fix.py`
- See full implementation: `scripts/validate_ci_fix.py`
- CI automation: `.github/workflows/test.yml`

**Key Requirements**:
- Linting: Must pass `ruff check`
- Formatting: Must pass `ruff format`
- Tests: Core tests must pass
- Coverage: ≥85% on critical modules

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

## Development Support Agents

### Available Virtual Development Agents
GitHub Copilot chatmodes are defined in `.github/chatmodes/` directory (SOURCE OF TRUTH):

1. **System Architecture Reviewer** (`/architecture-review` - `.github/chatmodes/architecture-reviewer.chatmode.md`)
   - **USE WHEN**: Designing new features, reviewing system architecture, analyzing impacts
   - **PROVIDES**: Architecture guidance, system design reviews, impact analysis
   - **QUESTIONS TO ASK**: "What are the system-wide impacts?", "Does this align with our architecture?", "What are the trade-offs?"

2. **Product Manager Advisor** (`/pm-requirements` - `.github/chatmodes/product-manager.chatmode.md`)
   - **USE WHEN**: Creating GitHub issues, defining requirements, making technical decisions
   - **PROVIDES**: Business value alignment, user story creation, test validation
   - **QUESTIONS TO ASK**: "What's the business value?", "How does this help users?", "What are the acceptance criteria?"

3. **UX/UI Designer** (`/ui-validation` - `.github/chatmodes/ux-designer.chatmode.md`)
   - **USE WHEN**: Designing UI components, validating user experience, creating interfaces
   - **PROVIDES**: Design validation, UI/UX improvements, usability analysis
   - **QUESTIONS TO ASK**: "Is this intuitive?", "What's the user journey?", "How accessible is this?"

4. **Code Reviewer** (`/code-quality` - `.github/chatmodes/code-reviewer.chatmode.md`)
   - **USE WHEN**: After writing significant code, before committing changes
   - **PROVIDES**: Best practices feedback, architecture alignment, code quality review
   - **QUESTIONS TO ASK**: "Does this follow patterns?", "Are there edge cases?", "Is this maintainable?"

5. **GitOps CI/CD Specialist** (`/gitops-ci` - `.github/chatmodes/gitops-ci-specialist.chatmode.md`)
   - **USE WHEN**: Committing code, troubleshooting CI/CD issues, optimizing pipelines
   - **PROVIDES**: Git workflow guidance, CI/CD pipeline optimization, deployment strategies
   - **QUESTIONS TO ASK**: "Will this pass CI?", "How can I optimize the pipeline?", "What's the deployment strategy?"

6. **Agent Sync Coordinator** (`/sync-instructions` - `.github/chatmodes/sync-coordinator.chatmode.md`)
   - **USE WHEN**: **MANDATORY before committing** changes to instruction files, ADRs, or developer agents
   - **PROVIDES**: Consistency analysis across `.claude/agents/` (if exists), `.github/chatmodes/`, `.cursor/rules/`, `.cursorrules`
   - **QUESTIONS TO ASK**: "Are instruction files in sync?", "What needs updating?", "How should I resolve conflicts?"
   - **CRITICAL**: Always run before committing changes to CLAUDE.md, ADRs, developer agents, or instruction files
   - **NAMING**: Use "agent-sync-coordinator" not "instruction-sync-coordinator"

### When to Use Support Agents

#### MANDATORY Agent Usage:
- **Before Implementation**: Use `/architecture-review` for design validation
- **After Code Writing**: Use `/code-quality` for all significant code changes
- **For UI Changes**: Use `/ui-validation` for any user-facing components
- **For Requirements**: Use `/pm-requirements` when creating features or issues
- **Before Committing**: Use `/gitops-ci` to validate CI/CD compatibility
- **For CI Issues**: Use `/gitops-ci` when tests fail in CI but pass locally
- **Before ANY Commit with Instruction/ADR/Agent Changes**: Use `/sync-instructions` (agent-sync-coordinator) to ensure consistency

#### Proactive Usage Pattern:
```
1. User requests feature → Use /pm-requirements for requirements
2. Design solution → Use /architecture-review for validation  
3. Implement code → Write the implementation
4. Pre-commit checks → Run MANDATORY local quality checks (ruff, tests, coverage)
5. Review code → Use /code-quality for feedback (AFTER checks pass)
6. If UI involved → Use /ui-validation for validation
7. If instruction files changed → Use /sync-instructions (agent-sync-coordinator, MANDATORY)
8. Before commit → Use /gitops-ci to ensure CI/CD compatibility
```

## Development Workflows with Support Agents

### Feature Development Workflow
```
1. User Request → Use /pm-requirements:
   - Analyze requirements and business value
   - Create proper GitHub issues
   - Define acceptance criteria

2. Design Phase → Use /architecture-review:
   - Review proposed architecture changes
   - Analyze system impacts
   - Validate design decisions

3. Implementation → Write code following patterns

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify ≥85% coverage on core components

5. Code Review → Use /code-quality (ONLY after checks pass):
   - Review for best practices
   - Check architecture alignment
   - Validate code quality

6. UI Components → Use /ui-validation (if applicable):
   - Review user experience
   - Validate interface design
   - Ensure usability standards

7. CI/CD Validation → Use /gitops-ci:
   - Validate commit structure
   - Ensure CI pipeline compatibility
   - Review deployment strategy

8. Document Decisions → Create ADR (MANDATORY):
   - Document context and changes made based on support agent feedback
   - Explain rationale for future developers
   - Include support agent assessments and scores
   - Track outstanding issues for future implementation
```

### Bug Fix Workflow
```
1. Issue Analysis → Use /architecture-review:
   - Understand system impact
   - Identify root cause areas

2. Solution Design → Use /pm-requirements:
   - Validate business impact
   - Prioritize fix approach

3. Implementation → Write fix

4. Pre-Commit Validation (MANDATORY) → Run local quality checks:
   - uv run ruff check . --fix (auto-fix issues)
   - uv run ruff format . (auto-format)
   - uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
   - Verify fix doesn't break existing functionality

5. Review → Use /code-quality (ONLY after checks pass):
   - Ensure fix doesn't introduce regressions
   - Validate approach

6. CI/CD Check → Use /gitops-ci:
   - Ensure fix won't break CI pipeline
   - Validate deployment safety

7. Document Fix → Create ADR (if significant):
   - Document root cause analysis from support agents
   - Explain solution approach and alternatives considered
   - Record lessons learned for future similar issues
```

### Branch Management (CRITICAL)
- **Always delete branches after PR merge**: Clean up both local and remote branches
- **Create new branch for new work**: Never reuse old feature branches
- **Branch naming**: Use descriptive names like `feat/feature-name` or `fix/bug-description`
- **Keep main clean**: Always work in feature branches, never commit directly to main

### Collaborative Development
- **Iterate**: Avoid monolithic feature drops
- **Scope Control**: One cohesive concern per PR
- **Issue-Driven**: Every substantive change references a GitHub issue
- **ADRs**: Required for architectural / cross-cutting changes before code

### Github Issue-Driven Process
1. **Create Issue**: Clear acceptance criteria and design specs
2. **Design Review**: Create/update ADR if architectural change
3. **Implementation**: Build with tests and documentation
4. **Code Review**: Use agent prompts for reviews

### Architecture Decision Records
- **Location**: `docs/decisions/adr-NNN-title.md`
- **Template**: Context → Decision → Consequences → Status
- **Traceability**: Link ADR ↔ Issue ↔ Implementation PR
- **MANDATORY**: Document all support agent feedback that leads to accepted changes

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

## Common Patterns

### Sequential Processing
See implementation: `loan_processing/agents/providers/openai/orchestration/sequential.py`
- Context accumulation pattern for agent coordination
- Each agent adds results to shared context

### Error Handling
See patterns: `loan_processing/agents/providers/openai/orchestration/base.py:187-210`
- MCPServerError handling
- AgentTimeoutError management
- Retry logic and fallback strategies

### Context Management (Loss Prevention)
Best practices from experience:
- Create git checkpoints after major changes
- Provide explicit context anchoring for new sessions
- Document key changes when switching tasks
- See detailed strategies: `CLAUDE.md:Context-Loss-Prevention`

### Debugging Circular Loops
Pattern implementation: `loan_processing/utils/decorators.py`
- Track attempted fixes to detect repetition
- Request human intervention when loops detected
- Apply "be pragmatic" guidance

## Copilot Prompt Usage

### Development Guidelines
- **Package Manager**: ALWAYS use `uv` commands (`uv run`, `uv add`, `uv sync`, `uv run python`) - NEVER pip/poetry
- **Adding Agents**: Create persona markdown in `agents/shared/agent-persona/`, add config to `agents.yaml`, use `AgentRegistry.create_agent()`
- **Modifying Behavior**: Update persona files or `agents.yaml` config, not orchestrator code
- **MCP Integration**: Agents autonomously select tools based on persona instructions
- **Testing**: Run `uv run pytest tests/test_agent_registry.py` before commits
- **Demo Scripts**: Use `uv run python demo_sequential_processing.py` to test workflows

### Copilot-Specific Agent Prompts
Use these prompts to activate specific agent behaviors:

#### Architecture Review
- `/architecture-review` - "Review this design for system-wide impacts and architecture alignment"
- Questions: "What are the trade-offs?", "How does this affect scalability?", "What patterns should I follow?"

#### Product Management
- `/pm-requirements` - "Help me create clear requirements and acceptance criteria"
- Questions: "What's the user story?", "How do we measure success?", "What are the edge cases?"

#### UX/UI Design
- `/ui-validation` - "Review this UI for usability and accessibility"
- Questions: "Is the flow intuitive?", "Are there accessibility issues?", "How can we simplify?"

#### Code Quality
- `/code-quality` - "Review this code for best practices and maintainability"
- Questions: "Are there performance issues?", "Is this testable?", "What edge cases am I missing?"

#### GitOps & CI/CD
- `/gitops-ci` - "Review my changes for CI/CD compatibility and deployment safety"
- Questions: "Will this pass CI?", "What's the deployment strategy?", "How can I fix failing tests?"

#### Agent Synchronization
- `/sync-instructions` - "Check if instruction files are synchronized and identify needed updates"
- Questions: "What changed in this ADR?", "Which files need updating?", "How do I resolve conflicts?"
- **Agent Name**: agent-sync-coordinator (not instruction-sync-coordinator)

### When to Use Agent Prompts
- **Design Phase**: `/architecture-review` for system design validation
- **Requirements**: `/pm-requirements` for creating issues and stories
- **Implementation**: `/code-quality` for code review (after tests pass)
- **UI Work**: `/ui-validation` for user experience review
- **CI/CD Issues**: `/gitops-ci` for pipeline troubleshooting and optimization
- **Before Commit**: `/gitops-ci` to validate CI compatibility
- **Instruction Updates**: `/sync-instructions` when ADRs or CLAUDE.md change
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