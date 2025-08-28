# Agent-Based Synchronization Strategy

## Overview
This document describes the agent-based synchronization strategy for maintaining consistency across multiple AI assistant instruction files. The system uses native AI agent implementations to perform fast, targeted synchronization checks before code commits.

## Architecture

### Native Agent Implementations
Each AI tool maintains its own native agent format:
- **Claude Code**: `.claude/agents/*.md` - Claude agent definitions with YAML frontmatter
- **GitHub Copilot**: `.github/chatmodes/*.chatmode.md` - Copilot chat modes  
- **Cursor IDE**: `.cursor/rules/*.mdc` - Cursor rules with smart context attachment

### Instruction Files Hierarchy

1. **CLAUDE.md** - Primary Development Rules
   - **Purpose**: Master reference for all development practices
   - **Scope**: Architecture, testing, workflows, support agents
   - **Authority**: Source of truth for synchronization

2. **.cursor/rules/*.mdc** - Cursor IDE Rules
   - **Purpose**: Context-aware development rules
   - **Scope**: Project patterns, agent development, testing, security
   - **Structure**: Multiple `.mdc` files with YAML frontmatter

3. **.github/instructions/copilot-instructions.md** - GitHub Copilot Rules
   - **Purpose**: Enterprise-grade coding standards
   - **Scope**: Quality gates, testing requirements, workflows
   - **Sync From**: CLAUDE.md (enterprise-focused subset)

## Agent-Based Synchronization

### The Sync Agent: agent-sync-coordinator
- **Location**: `.claude/agents/agent-sync-coordinator.md`
- **Performance**: Optimized for <20 seconds, <3K tokens
- **Strategy**: Git-driven detection + exact file mapping
- **Model**: Inherits from parent (provider-agnostic)

### How It Works
1. **Agent uses git** to detect exactly what changed:
   ```bash
   git diff --name-only HEAD
   ```
2. **Maps changes** to specific target files:
   - `CLAUDE.md` → `.github/instructions/copilot-instructions.md`, `.cursor/rules/project-rules.mdc`
   - `docs/decisions/adr-*.md` → `CLAUDE.md`, sync chatmode
   - `docs/developer-agents/*.md` → corresponding chatmodes and agents
3. **Targeted grep** for specific patterns in mapped files only
4. **Reports sync status** in concise format:
   ```
   Changed: CLAUDE.md
   ✅ SYNCED: [files that match]
   ⚠️ UPDATE: [specific file] - [one-line change]
   ACTION: [what to do]
   ```
5. **Developer applies updates** if needed, then commits

### Trigger Events
- ✅ **Architecture Decision Records** (ADRs) added or modified
- ✅ **CLAUDE.md updates** - testing commands, workflows, patterns
- ✅ **Developer agent changes** in `docs/developer-agents/`
- ✅ **Repository structure changes** - directories, modules
- ✅ **Package manager updates** - uv commands, dependencies

## What to Synchronize

### Core Elements (Must Match Across All Files)
- ✅ **Repository structure** - directory paths, file locations
- ✅ **Package manager commands** - uv usage, never pip/poetry
- ✅ **Test commands** - `uv run pytest tests/test_agent_registry.py`
- ✅ **Coverage requirements** - ≥85% on core components
- ✅ **Agent patterns** - `AgentRegistry.create_agent()`
- ✅ **Security rules** - Use applicant_id, never SSN
- ✅ **Pre-commit checks** - ruff, pytest requirements

### Tool-Specific Elements (Preserve Differences)
- **CLAUDE.md**: Comprehensive reference, support agents, workflows
- **Cursor rules**: Pattern-focused, glob attachments, concise
- **Copilot instructions**: Enterprise standards, quality gates

## Performance Optimization

### Token Reduction Strategy (75% Reduction)
Following ADR-004, all instruction files now use:
- **File references** instead of inline code: `See: path/to/file.py:123-145`
- **Concise directives** instead of verbose explanations
- **External links** for detailed documentation
- **Focused content** under 500 lines per file

### Sync Agent Optimization
- **Git-driven**: Use `git diff` to identify exact changes
- **File mapping**: Predefined source → target file mappings
- **Pattern grep**: Use `rg` to find specific patterns quickly
- **Skip unchanged**: Never read files not in the mapping
- **Performance target**: <20 seconds, <3K tokens

## Implementation in Each Tool

### Claude Code
1. **Before committing**, Claude runs agent-sync-coordinator
2. **Agent location**: `.claude/agents/agent-sync-coordinator.md`
3. **Invocation**: Via Task tool with `subagent_type: agent-sync-coordinator`
4. **Process**: Check → Report → Fix if needed → Commit

### GitHub Copilot
1. **Chatmode**: `.github/chatmodes/sync-coordinator.chatmode.md`
2. **Command**: `/sync-check` before commits
3. **Focus**: Enterprise standards and quality gates

### Cursor IDE
1. **Rule files**: `.cursor/rules/*.mdc` auto-attach by context
2. **Sync reminder**: In `project-rules.mdc` with `alwaysApply: true`
3. **Pattern matching**: Rules attach based on file globs

## Developer Workflow

### Pre-Commit Synchronization
```bash
# 1. Make changes to CLAUDE.md or ADRs
# 2. AI assistant automatically suggests sync check
# 3. Run sync agent (each tool has native implementation)
# 4. Apply any needed updates
# 5. Commit with confidence
```

### Manual Sync Check
When in doubt, manually invoke the sync agent:
- **Claude**: "Check if instruction files are synchronized"
- **Copilot**: "/sync-check" 
- **Cursor**: Agent reminder appears automatically

## Best Practices

### Do's ✅
- **Run sync before committing** instruction changes
- **Use CLAUDE.md as source of truth**
- **Preserve tool-specific features** in each file
- **Keep sync checks fast** - under 30 seconds
- **Focus on changed content** only

### Don'ts ❌
- **Don't sync unchanged sections** - wastes tokens
- **Don't hardcode provider dependencies** - stay agnostic  
- **Don't create sync loops** - one-way from CLAUDE.md
- **Don't sync minor typos** - focus on semantic changes
- **Don't use external APIs** - developer-side only

## File Mapping Reference

### Source → Target Synchronization Map
| Source File | Target Files to Check |
|------------|----------------------|
| `CLAUDE.md` | `.github/instructions/copilot-instructions.md`<br>`.cursor/rules/project-rules.mdc` |
| `docs/decisions/adr-*.md` | `CLAUDE.md` (decisions section)<br>`.github/chatmodes/sync-coordinator.chatmode.md` |
| `docs/developer-agents/*.md` | `.github/chatmodes/[agent-name].chatmode.md`<br>`.claude/agents/[agent-name].md` |
| `.claude/agents/*.md` | `.github/chatmodes/[same-name].chatmode.md` |
| Test/package commands | `CLAUDE.md`, `.cursor/rules/testing.mdc`, copilot instructions |

### Known Instruction Locations
- **Primary**: `CLAUDE.md` (source of truth)
- **GitHub Copilot**: `.github/instructions/copilot-instructions.md`
- **Chatmodes**: `.github/chatmodes/*.chatmode.md`  
- **Claude agents**: `.claude/agents/*.md`
- **Cursor rules**: `.cursor/rules/*.mdc`

## Success Metrics
- **Speed**: Sync checks complete in <20 seconds
- **Efficiency**: Use <3K tokens per check
- **Accuracy**: Zero false positives on sync status
- **Coverage**: All critical elements stay synchronized
- **Adoption**: Developers naturally use sync before commits

This agent-based approach ensures consistency while respecting each tool's unique capabilities and maintaining provider independence.