# ADR-004: Prompt Optimization Through File References

## Status
Accepted

## Context

As our multi-agent system has grown, we've discovered that instruction files containing inline code snippets and verbose documentation significantly increase token consumption and costs. This affects:
- Development speed (slower AI responses)
- API costs (larger context windows)
- Maintainability (duplicate information across files)
- Clarity (verbose instructions obscure key directives)

Initial measurements showed:
- Large instruction files with inline code: 2000+ tokens per file
- Response times: 30+ seconds for complex operations
- Estimated cost increase: 3-5x due to repeated context

## Decision

We will implement a **file reference strategy** for all instruction files, replacing inline content with references to existing repository files.

### Core Principles

1. **Never Include Code Snippets**
   - ❌ Bad: Inline code examples in instructions
   - ✅ Good: `See implementation: path/to/file.py:line-range`

2. **Reference Documentation**
   - ❌ Bad: Explaining architecture in instruction files
   - ✅ Good: `See architecture: docs/decisions/adr-001.md`

3. **Cross-Reference Sections**
   - ❌ Bad: Duplicating information across files
   - ✅ Good: `As defined in CLAUDE.md:Security-Guidelines`

4. **Use Repository Structure**
   - ❌ Bad: Describing file locations verbosely
   - ✅ Good: Direct path references to actual files

### Implementation Guidelines

#### For Code Examples
```
Before: 
"Use this pattern for error handling:
```python
try:
    result = await agent.run()
except Exception as e:
    logger.error(e)
```"

After:
"Error handling pattern: See `loan_processing/orchestration/base.py:187-210`"
```

#### For Documentation
```
Before:
"The system uses a multi-agent architecture where each agent..."
[long explanation]

After:
"System architecture: See `docs/decisions/adr-001-agent-registry-pattern.md`"
```

#### For Configuration
```
Before:
"Configure agents using this YAML structure..."
[inline YAML example]

After:
"Agent configuration: See `loan_processing/agents/shared/config/agents.yaml`"
```

### Scope of Application

This strategy applies to:
- `CLAUDE.md` - Main instruction file
- `.github/instructions/copilot-instructions.md` - GitHub Copilot instructions
- `docs/developer-agents/*.md` - All developer agent definitions
- `.github/chatmodes/*.chatmode.md` - All chatmode files
- `.cursor/rules/*.mdc` - Cursor IDE rule files
- Any future instruction or configuration files

### Synchronization Integration

The sync-coordinator agent will:
1. Detect inline code during synchronization
2. Replace with appropriate file references
3. Consolidate duplicate information
4. Maintain a compact, reference-based structure

## Consequences

### Positive
- **75% Token Reduction**: Measured reduction in context size
- **10x Faster Responses**: From 30+ seconds to 3-5 seconds
- **Cost Savings**: 60-80% reduction in API costs
- **Better Maintainability**: Single source of truth for each concept
- **Clearer Instructions**: Focus on directives, not implementation
- **Automatic Updates**: When code changes, references remain valid

### Negative
- **Navigation Required**: Users must follow references to see details
- **IDE Integration**: Some tools may not auto-link references
- **Initial Learning**: Team needs to adopt reference pattern

### Neutral
- **Documentation Style Change**: Shift from self-contained to reference-based
- **Review Process**: Reviewers need to check referenced files

## Validation

Success metrics:
1. Average instruction file size < 500 lines
2. Token consumption per operation < 2000 tokens
3. No inline code blocks in instruction files
4. All examples reference actual repository files
5. Response time < 5 seconds for standard operations

## Migration Plan

1. **Phase 1**: Update sync-coordinator with compaction rules
2. **Phase 2**: Apply to CLAUDE.md and copilot-instructions.md
3. **Phase 3**: Update all developer agents
4. **Phase 4**: Optimize chatmodes
5. **Phase 5**: Continuous enforcement via sync agent

## Examples of Optimized Instructions

### Before (Verbose)
```markdown
## Pre-Commit Checks
Run these commands before committing:
```bash
uv run ruff check .
uv run ruff format .
uv run pytest tests/
```
Make sure coverage is above 85%...
```

### After (Optimized)
```markdown
## Pre-Commit Checks
Run validation: `uv run python scripts/validate_ci_fix.py`
- Implementation: `scripts/validate_ci_fix.py`
- CI config: `.github/workflows/test.yml`
- Coverage requirement: ≥85% on core modules
```

## References

- Token optimization discovery: `CLAUDE.md:Token-Optimization-Discovery`
- Validation script: `scripts/validate_ci_fix.py`
- CI workflows: `.github/workflows/`
- Agent configurations: `loan_processing/agents/shared/config/agents.yaml`

## Last Updated

2024-12-28 - Initial strategy definition and implementation guidelines