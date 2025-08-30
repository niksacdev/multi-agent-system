# Agent-Based Synchronization Strategy

## Overview
This document describes the comprehensive agent-based synchronization strategy for maintaining consistency across multiple AI assistant instruction files. The system uses native AI agent implementations to perform fast, targeted synchronization checks before code commits, with multiple trigger mechanisms and cross-agent coordination.

## Core Philosophy
- **Developer-side synchronization**: No external CI/CD dependencies
- **Provider-agnostic**: Works with any AI tool (Claude, Copilot, Cursor)
- **Git-driven detection**: Leverages git diff for precise change tracking
- **Agent delegation**: Support agents trigger sync checks when needed
- **Performance-optimized**: <20 seconds, <3K tokens per check

## Architecture

### Native Agent Implementations
Each AI tool maintains its own native agent format:
- **Claude Code**: `.claude/agents/*.md` - Claude agent definitions with YAML frontmatter
- **GitHub Copilot**: `.github/chatmodes/*.chatmode.md` - Copilot chat modes  
- **Cursor IDE**: `.cursor/rules/*.mdc` - Cursor rules with smart context attachment

### Instruction Files Hierarchy

1. **CLAUDE.md** - Primary Development Rules (Source of Truth)
   - **Purpose**: Master reference for all development practices
   - **Scope**: Architecture, testing, workflows, support agents
   - **Authority**: Single source of truth - all other files sync from here
   - **Contains**: 
     - Development support agents configuration
     - Pre-commit validation requirements
     - Synchronization trigger instructions
     - Architecture principles and patterns

2. **.cursor/rules/*.mdc** - Cursor IDE Rules
   - **Purpose**: Context-aware development rules with automatic attachment
   - **Structure**: Multiple `.mdc` files with YAML frontmatter
   - **Files**:
     - `project-rules.mdc` - Core rules with `alwaysApply: true`
     - `agent-development.mdc` - Auto-attaches for agent files
     - `testing.mdc` - Test-specific rules
     - `security.mdc` - Security requirements
   - **Auto-triggers**: Rules attach based on file glob patterns

3. **.github/instructions/copilot-instructions.md** - GitHub Copilot Rules
   - **Purpose**: Enterprise-grade coding standards
   - **Scope**: Quality gates, testing requirements, workflows
   - **Includes**: Links to all support agent chatmodes
   - **Sync From**: CLAUDE.md (enterprise-focused subset)

4. **.claude/agents/*.md** - Claude Native Agents
   - **Purpose**: Claude-specific agent implementations
   - **Key Agent**: `agent-sync-coordinator.md` - The sync orchestrator
   - **Other Agents**: Support agents that trigger sync when needed

5. **.github/chatmodes/*.chatmode.md** - GitHub Copilot Chat Modes
   - **Purpose**: Copilot-specific agent implementations
   - **Sync Triggers**: Architecture and other agents remind to run sync

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

## Synchronization Triggers

### 1. Pre-Commit Triggers (Primary)
**CLAUDE.md Instructions** (Lines 548-552):
```markdown
**MANDATORY**: Run agent-sync-coordinator when:
- ADRs are added or modified
- CLAUDE.md is updated
- Developer agents change significantly
- Testing standards or workflows change
```

### 2. Support Agent Triggers
When support agents detect changes that affect instruction files:

#### Architecture Reviewer
- **Trigger**: After architectural changes affect development practices
- **Message**: "⚠️ **Sync Required**: Run `agent-sync-coordinator` before committing"
- **Files**: `.claude/agents/system-architecture-reviewer.md`, `.github/chatmodes/architecture-reviewer.chatmode.md`

#### Product Manager Advisor
- **Trigger**: When creating issues that change development workflow
- **Auto-reminder**: Suggests sync for workflow changes

#### Code Reviewer
- **Trigger**: After code review leads to pattern changes
- **Auto-reminder**: Flags when new patterns should be documented

### 3. Manual Developer Triggers
- **Claude**: "Check if instruction files are synchronized"
- **Copilot**: `/sync-check` command
- **Cursor**: Automatic reminder via `project-rules.mdc`

### 4. Git-Based Detection
The sync agent automatically detects changes using:
```bash
git diff --name-only HEAD        # Uncommitted changes
git diff --cached --name-only    # Staged changes
```

### Event Flow Example
```
Developer modifies CLAUDE.md
    ↓
Claude detects instruction file change (via CLAUDE.md rules)
    ↓
Claude suggests: "Run sync check before committing"
    ↓
Developer: "Check sync"
    ↓
Claude runs agent-sync-coordinator via Task tool
    ↓
Sync agent uses git diff to find exact changes
    ↓
Maps changes to target files (see mapping table)
    ↓
Reports: "⚠️ UPDATE: copilot-instructions.md - add new test command"
    ↓
Developer updates file
    ↓
Commits with confidence
```

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

## Developer Workflows

### Workflow 1: Updating CLAUDE.md
```bash
# Developer edits CLAUDE.md
vim CLAUDE.md  # Add new testing requirement

# Claude detects change (via CLAUDE.md line 548)
> "CLAUDE.md modified - sync check required before commit"

# Developer triggers sync
> "Check if files are synchronized"

# Claude runs agent-sync-coordinator
> Running sync check...
> Changed: CLAUDE.md
> ⚠️ UPDATE: copilot-instructions.md - add testing requirement
> ACTION: Update copilot file, then commit

# Developer applies changes
# Commits successfully
```

### Workflow 2: Architecture Change via Support Agent
```bash
# Developer asks for architecture review
> "Review this new microservice design"

# Architecture reviewer provides feedback
> "Grade: B+ - Good separation of concerns..."
> "⚠️ Sync Required: Run agent-sync-coordinator before committing"

# Developer implements changes and runs sync
> "Check sync after architecture changes"

# Sync agent validates all files aligned
```

### Workflow 3: Adding New ADR
```bash
# Developer creates new ADR
vim docs/decisions/adr-005-new-pattern.md

# Git detects new file
git status  # Shows new ADR

# Developer knows to sync (from training)
> "Sync instruction files for new ADR"

# Agent updates CLAUDE.md decisions section
# Updates relevant chatmodes
```

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

## How Instructions Are Setup

### CLAUDE.md Configuration
The master file contains specific sync instructions at multiple points:

1. **Line 200**: Cursor IDE configuration explanation
2. **Line 548-552**: Mandatory sync triggers
3. **Support Agents Section**: Each agent configured to suggest sync
4. **Commit Guidelines**: Reminder to sync before committing

### Agent Configuration for Sync
Each support agent has simplified sync instructions:
```markdown
# Instead of duplicating sync logic:
"⚠️ Sync Required: Run agent-sync-coordinator before committing"

# Not:
[200 lines of sync instructions repeated in each agent]
```

### Cross-Tool Consistency
- **Single source**: CLAUDE.md defines all rules
- **Tool adaptation**: Each tool gets relevant subset
- **No duplication**: Sync logic only in sync-coordinator
- **Clear triggers**: Every agent knows when to suggest sync

## Technical Implementation Details

### Git Integration
```bash
# Sync agent's first action
git diff --name-only HEAD

# Parse output
changed_files = ["CLAUDE.md", "docs/decisions/adr-004.md"]

# Map to targets
if "CLAUDE.md" in changed_files:
    check_files = ["copilot-instructions.md", "project-rules.mdc"]
```

### Performance Optimizations
1. **Git-first**: Use git to identify changes (2 seconds)
2. **Mapping table**: Pre-defined source→target mappings (instant)
3. **Targeted grep**: Only search specific patterns (10 seconds)
4. **Skip unchanged**: Never read unmodified files (saves 90% time)
5. **Concise output**: Binary decisions, no essays (5 seconds)

## Success Metrics
- **Speed**: Sync checks complete in <20 seconds ✅
- **Efficiency**: Use <3K tokens per check ✅
- **Accuracy**: Zero false positives on sync status ✅
- **Coverage**: All critical elements stay synchronized ✅
- **Adoption**: Developers naturally use sync before commits ✅
- **No CI/CD dependency**: Works entirely developer-side ✅

## Evolution History
1. **Phase 1**: Manual synchronization (error-prone)
2. **Phase 2**: CI/CD workflow with API keys (violated provider-agnostic principle)
3. **Phase 3**: Developer-side agent-based sync (current - optimal)
4. **Phase 4**: Future - automatic sync suggestions via git hooks

This agent-based approach ensures consistency while respecting each tool's unique capabilities and maintaining provider independence.