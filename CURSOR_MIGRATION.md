# Cursor IDE Configuration Migration Guide

## Important Update
Cursor IDE has changed from using a single `.cursorrules` file to a folder-based configuration system.

## Migration Steps

### 1. Create New Cursor Configuration
```bash
# Create the .cursor folder
mkdir .cursor

# Create the main rules file with optimized content
echo "# Cursor Rules for Multi-Agent System

See comprehensive development guidelines: \`CLAUDE.md\`

## Quick Reference
- Architecture: \`docs/decisions/adr-*.md\`
- Agent patterns: \`loan_processing/agents/\`
- Testing: \`scripts/validate_ci_fix.py\`
- Security: Always use applicant_id, never SSN

## Key Principles
- Autonomous agents select their own MCP tools
- Business logic in personas, not code
- Keep personas under 500 lines for performance
- Reference files instead of inline code" > .cursor/rules.md
```

### 2. Remove Old Configuration
```bash
# After verifying .cursor/rules.md works
rm .cursorrules
```

### 3. Add to .gitignore
```bash
echo ".cursor/" >> .gitignore
```

## Why This Change?

1. **Better Organization**: Multiple context files instead of one monolithic file
2. **Performance**: Smaller, focused files reduce token usage
3. **Flexibility**: Can have different rules for different parts of the project
4. **Modern Approach**: Aligns with Cursor's latest best practices

## File Structure

```
.cursor/
├── rules.md          # Main development rules (references CLAUDE.md)
├── context.md        # Project context (optional)
└── patterns.md       # Code patterns (optional)
```

## Note on Synchronization

Since `.cursor/` contains IDE-specific configuration, it should:
- Reference `CLAUDE.md` as the source of truth
- Not duplicate content from CLAUDE.md
- Be added to `.gitignore` for personal customization

## Legacy Support

The `.cursorrules` file is deprecated but will continue to work until Cursor removes support. We recommend migrating to the new structure as soon as possible.