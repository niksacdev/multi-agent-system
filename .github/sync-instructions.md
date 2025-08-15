# Instruction Files Synchronization Guide

## Overview
This repository has multiple instruction files that must stay synchronized to provide consistent guidance across different AI assistants and development environments.

## Instruction Files (Keep in Sync)

### 1. **CLAUDE.md** - Primary Development Rules
- **Purpose**: Comprehensive development guidelines for Claude Code
- **Scope**: Architecture, testing, development workflows, support agents
- **Authority**: Master reference for all development practices

### 2. **.cursorrules** - Cursor IDE Instructions  
- **Purpose**: Concise rules for Cursor AI assistance
- **Scope**: Code patterns, architecture principles, quick commands
- **Sync From**: CLAUDE.md (condensed version)

### 3. **.github/instructions/copilot-instructions.md** - GitHub Copilot Rules
- **Purpose**: Enterprise-grade coding standards for GitHub Copilot
- **Scope**: Quality gates, testing requirements, development workflows
- **Sync From**: CLAUDE.md (enterprise-focused version)

## Synchronization Rules

### When to Update (Trigger Events)
- ✅ **Repository structure changes** (directory moves, new modules)
- ✅ **Testing command changes** (new test patterns, coverage requirements)
- ✅ **Package manager updates** (uv commands, dependency management)
- ✅ **Architecture pattern changes** (new abstractions, design patterns)
- ✅ **Development workflow updates** (commit patterns, CI/CD changes)

### Update Process (No Circular Loops)
1. **CLAUDE.md is the source of truth** - Always update this first
2. **Extract relevant sections** for other files (don't copy everything)
3. **Update .cursorrules** - Focus on concise patterns and commands
4. **Update copilot-instructions.md** - Focus on quality gates and enterprise standards
5. **Commit each file separately** with clear commit messages

### What to Keep in Sync

#### Core Elements (Must Match)
- ✅ **Repository structure** (directory paths, file locations)
- ✅ **Package manager commands** (uv usage, never pip/poetry)
- ✅ **Test commands** (`uv run pytest tests/test_agent_registry.py`)
- ✅ **Coverage requirements** (>90% on core components)
- ✅ **Agent creation patterns** (`AgentRegistry.create_agent()`)
- ✅ **Configuration paths** (`agents/shared/config/agents.yaml`)

#### File-Specific Focus (Can Differ)
- **CLAUDE.md**: Comprehensive, detailed, includes support agents
- **.cursorrules**: Concise, pattern-focused, quick reference
- **copilot-instructions.md**: Quality-focused, enterprise standards, CI/CD

## Sync Checklist

When updating any instruction file, verify these elements are consistent:

- [ ] **Directory Structure**: `loan_processing/agents/` and `loan_processing/tools/` paths
- [ ] **Package Manager**: All commands use `uv run`, `uv add`, `uv sync`
- [ ] **Test Commands**: Core test suite with coverage (`uv run pytest tests/test_agent_registry.py`)
- [ ] **Agent Creation**: `AgentRegistry.create_agent()` pattern
- [ ] **Configuration**: `agents/shared/config/agents.yaml` and `agents/shared/agent-persona/`
- [ ] **Coverage Requirement**: >90% on core components
- [ ] **Architecture Patterns**: Repository separation (agents/ vs tools/)

## Anti-Patterns (Avoid Circular Updates)

❌ **Don't**: Update all files simultaneously in one commit
❌ **Don't**: Copy-paste entire sections between files  
❌ **Don't**: Create auto-sync scripts (risk of infinite loops)
❌ **Don't**: Update files based on other instruction files

✅ **Do**: Use CLAUDE.md as single source of truth
✅ **Do**: Extract and adapt content for each audience
✅ **Do**: Commit each file update separately
✅ **Do**: Test changes before committing

## Commit Strategy

### Small, Focused Commits
```bash
# Good: Specific, focused commits
git commit -m "docs: update repository structure in CLAUDE.md"
git commit -m "chore: sync .cursorrules with new test commands" 
git commit -m "docs: update copilot instructions for uv usage"

# Bad: Large, unfocused commits  
git commit -m "update all documentation files"
```

### Commit Frequency Guidelines
- **After each logical change** (not after hours of work)
- **Before major refactoring** (create checkpoint)
- **After test fixes** (working state preservation)
- **When switching contexts** (different features/bugs)

## Version Control Best Practices

1. **Atomic Commits**: One logical change per commit
2. **Clear Messages**: Describe what and why, not how
3. **Test Before Commit**: Always run tests before committing
4. **Small PRs**: Target 50-200 lines changed per PR
5. **Frequent Pushes**: Don't accumulate many local commits

This approach ensures maintainable, reviewable changes while keeping all AI assistants properly informed and synchronized.