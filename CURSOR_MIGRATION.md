# Cursor IDE Configuration Migration Guide

## Important Update
Cursor IDE has changed from using a single `.cursorrules` file to a rules-based system with `.mdc` files (Markdown with metadata) in `.cursor/rules/` directory.

## Current Structure
```
.cursor/rules/
├── project-rules.mdc      # Core rules (always applied)
├── agent-development.mdc  # Auto-attaches for agent files
├── testing.mdc           # Auto-attaches for test files
└── security.mdc          # Auto-attaches for sensitive files
```

## How It Works
1. **Always Applied**: Rules with `alwaysApply: true` are always included
2. **Auto-Attached**: Rules with `globs` patterns attach when matching files are referenced
3. **Hierarchical**: Subdirectories can have their own `.cursor/rules/` folders
4. **Metadata-Driven**: Each `.mdc` file includes metadata for behavior control

## Migration Steps

### 1. Remove Old Configuration
```bash
# Remove deprecated .cursorrules if it exists
rm .cursorrules
```

### 2. Verify New Rules Are Working
- Open Cursor IDE
- Open any Python file in `loan_processing/agents/`
- Check that agent development rules are automatically attached
- Open any test file to verify testing rules attach

## MDC File Format

### Example Structure
```markdown
---
description: "Brief description of these rules"
globs:  # Optional: file patterns for auto-attachment
  - "**/*.py"
  - "tests/**"
alwaysApply: true  # Optional: always include these rules
---

# Rule Content
Your markdown content here...
```

## Rule Types

1. **Always Applied** (`alwaysApply: true`)
   - Core project rules
   - Security requirements
   - Critical guidelines

2. **Auto-Attached** (with `globs` patterns)
   - Domain-specific rules
   - File-type specific guidance
   - Contextual helpers

3. **Manual** (no metadata)
   - Optional rules
   - Reference documentation

## Benefits of New System

1. **Smart Context**: Rules automatically attach based on what you're working on
2. **Performance**: Only relevant rules are loaded, reducing token usage
3. **Organization**: Clear separation of concerns with multiple rule files
4. **Flexibility**: Different rules for different parts of the codebase
5. **Hierarchical**: Subdirectories can have specialized rules

## Note on Synchronization

The `.cursor/rules/` directory:
- References `CLAUDE.md` as the source of truth
- Uses file references to avoid content duplication
- Should be committed to git for team consistency
- Follows our prompt optimization strategy (ADR-004)

## Legacy `.cursorrules`

The `.cursorrules` file is deprecated:
- Still works but not recommended
- Single monolithic file (poor performance)
- No smart context attachment
- Should be removed after migration

## Further Reading

- [Cursor Rules Documentation](https://docs.cursor.com/en/context/rules)
- `docs/decisions/adr-004-prompt-optimization-strategy.md` - Token optimization
- `CLAUDE.md` - Master development guidelines