# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the loan processing multi-agent demo.

## ADR Format

We use a lightweight ADR template inspired by Michael Nygard's format:

- **Title**: Short, descriptive title
- **Status**: Proposed | Accepted | Superseded
- **Context**: The forces at play, including technological, political, social, and project local
- **Decision**: The response to these forces
- **Consequences**: The resulting context, including new problems introduced

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](adr-001-agent-communication.md) | Agent Communication Pattern | Proposed | 2025-08-04 |
| [009](adr-009-development-tooling-language-selection.md) | Development Tooling Language Selection | Accepted | 2025-08-19 |
| [010](adr-010-mcp-server-lifecycle-management.md) | MCP Server Lifecycle Management Strategy | Accepted | 2025-08-19 |
| [011](adr-011-configuration-provider-separation.md) | Configuration Provider Separation | Accepted | 2025-08-19 |
| [012](adr-012-clean-architecture-implementation.md) | Clean Architecture Implementation | Accepted | 2025-08-19 |

## Creating New ADRs

1. Copy the template below
2. Number sequentially (adr-XXX-title.md)
3. Fill out all sections
4. Link to relevant GitHub issues
5. Update this index

## ADR Template

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Superseded]

## Context
[What is the issue that we're seeing that is motivating this decision or change?]

## Decision
[What is the change that we're proposing or have agreed to implement?]

## Consequences
[What becomes easier or more difficult to do and any risks introduced by this change?]

## Implementation
[Specific implementation details and steps]

Related Issues: #XXX
```

## Guidelines

- Write ADRs for significant architectural decisions
- Keep them concise but complete
- Include trade-offs and alternatives considered
- Link to GitHub issues and implementation details
- Update status as decisions evolve
