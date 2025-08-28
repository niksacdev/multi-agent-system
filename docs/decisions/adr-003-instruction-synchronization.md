# ADR-003: Pre-Merge Instruction File Synchronization

## Status
Accepted

## Context

As our multi-agent system has evolved, we maintain multiple instruction files for different AI development tools:
- `CLAUDE.md` - Master reference for Claude Code
- `.github/instructions/copilot-instructions.md` - GitHub Copilot instructions
- `docs/developer-agents/*.md` - Specialized development agent definitions  
- `.github/chatmodes/*.chatmode.md` - GitHub Copilot chat modes

Keeping these files synchronized is critical for consistent developer experience across tools. We evaluated several approaches:

1. **Template-based generation** - Rejected due to complexity and loss of natural language
2. **Post-merge synchronization** - Creates double-PR problem  
3. **Manual synchronization** - Error-prone and often forgotten
4. **Pre-merge synchronization** - Updates happen in same PR (chosen approach)

## Decision

We will implement **pre-merge automatic synchronization** using an AI-powered sync coordinator agent that:

1. **Triggers during PR review** when instruction files change
2. **Commits updates to the same PR** before merge
3. **Preserves natural language** without templates
4. **Maintains tool-specific features** while ensuring consistency
5. **Optimizes prompts** by replacing code snippets with file references to minimize context window usage

### Synchronization Hierarchy

When resolving conflicts, follow this precedence:

1. **ADRs** (Architecture Decision Records) - Override everything
2. **CLAUDE.md** - Primary source for development practices
3. **Developer agents** - Domain-specific expertise
4. **Copilot instructions** - Derived from above sources
5. **Chatmodes** - Tool-specific implementations

### Trigger Strategy

```yaml
Triggers:
- PR opened/updated with changes to:
  - docs/decisions/*.md (ADRs)
  - CLAUDE.md
  - docs/developer-agents/*.md
  - .github/instructions/copilot-instructions.md

Skip if:
- Last commit from sync-agent[bot]
- Commit message contains [skip-sync]
```

## Consequences

### Positive
- **Single PR workflow** - No follow-up PRs needed
- **Atomic changes** - Related updates reviewed together
- **Natural language preserved** - No template complexity
- **Immediate consistency** - Files synchronized before merge
- **Developer control** - Can modify sync changes in PR
- **Clean git history** - One merge for complete change

### Negative  
- **PR complexity** - PRs may have additional commits from sync
- **Potential noise** - Multiple sync runs if PR updated frequently
- **CI complexity** - More complex GitHub Actions workflow

### Neutral
- **Review burden** - Reviewers see sync changes (but this is actually good for transparency)
- **Commit count** - PRs will have 1-2 additional commits

## Implementation

### Phase 1: Sync Coordinator Agent
Create `docs/developer-agents/sync-coordinator.md` with:
- Natural language understanding of instruction relationships
- Semantic diff capabilities
- Tool-specific feature preservation
- **Prompt optimization**: Replace inline code with file references
- **Context reduction**: Remove duplicate information, use cross-references

### Phase 2: GitHub Action Workflow
Create `.github/workflows/sync-instructions.yml`:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    paths: [relevant instruction files]

jobs:
  sync:
    if: !contains(github.event.head_commit.message, '[skip-sync]')
    steps:
      - Run sync coordinator agent
      - Commit changes to PR with [skip-sync] flag
```

### Phase 3: Documentation
- Update CLAUDE.md with sync process
- Add notes to copilot-instructions about auto-sync
- Document in README for visibility

## Alternatives Considered

### Post-Merge Synchronization
**Rejected because**: Creates double-PR problem where every merge triggers another PR

### Template-Based Generation  
**Rejected because**: Adds complexity, loses natural language benefits, requires template engine

### Weekly Batch Synchronization
**Rejected because**: Too slow for active development, changes get out of sync

### Manual PR Comment Trigger
**Considered but not chosen**: Requires developer to remember, adds friction

## Validation

Success criteria:
1. No manual synchronization needed
2. Single PR contains all related changes
3. No synchronization loops occur
4. Tool-specific features preserved
5. Natural language maintained

## References

- [System Architecture Review](../developer-agents/system-architecture-reviewer.md) - Provided architectural analysis
- [CLAUDE.md](../../CLAUDE.md) - Master instruction reference
- [GitHub Copilot Instructions](../../.github/instructions/copilot-instructions.md) - Tool-specific implementation

## Decision Makers

- System Architecture Reviewer Agent - Grade: A- (90/100)
- Human Developer - Approved pre-merge approach
- Sync Coordinator Agent - Will implement synchronization

## Last Updated

2024-12-28 - Initial decision and implementation plan