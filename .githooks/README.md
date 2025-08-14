# Git Hooks Setup

This directory contains git hooks to ensure code quality and testing standards.

## Pre-commit Hook

The `pre-commit` hook automatically runs the full test suite before allowing commits.

### Installation

Run from the project root:

```bash
# Configure git to use our custom hooks directory
git config core.hooksPath .githooks

# Make sure the hook is executable (should already be done)
chmod +x .githooks/pre-commit
```

### What it does

1. **Checks environment** - Ensures you're in the project root and virtual environment is available
2. **Activates venv** - Automatically activates `.venv` if not already active
3. **Runs test suite** - Executes `python run_tests.py --type all`
4. **Validates results** - Ensures all 83+ tests pass with >90% coverage
5. **Blocks bad commits** - Prevents commits if any tests fail

### Bypassing (NOT RECOMMENDED)

In rare cases where you need to commit without running tests:

```bash
git commit --no-verify
```

**Warning**: This should only be used for documentation-only changes or emergency fixes. All production code must pass tests.

### Test Requirements

- ✅ All 83+ tests must pass
- ✅ Coverage must be ≥90%
- ✅ No type checking errors
- ✅ No lint errors

### Troubleshooting

If the hook fails:

1. **Check test failures**: Review the test output to see what's broken
2. **Fix the code**: Address failing tests or coverage issues
3. **Run manually**: `python run_tests.py --type all`
4. **Retry commit**: Once tests pass, commit again

The hook ensures that our main branch always contains working, well-tested code.
