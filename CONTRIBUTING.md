# Contributing to Multi-Agent Loan Processing System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (`pip install uv`)
- OpenAI API key (or Azure OpenAI credentials)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/multi-agent-system.git
   cd multi-agent-system
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Install pre-commit hooks**
   ```bash
   uv pip install pre-commit
   pre-commit install
   ```

5. **Run tests to verify setup**
   ```bash
   uv run pytest tests/test_agent_registry.py -v
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow these guidelines:
- Write clean, readable code following PEP 8
- Add type hints to all functions
- Include docstrings for modules, classes, and functions
- Keep functions focused and small
- Follow existing patterns in the codebase

### 3. Write Tests

- Add tests for new functionality
- Ensure existing tests pass
- Maintain >80% code coverage

```bash
# Run specific tests
uv run pytest tests/test_your_feature.py -v

# Run with coverage
uv run pytest tests/ --cov=loan_processing --cov-report=term-missing
```

### 4. Run Quality Checks

Before committing, run all quality checks:

```bash
# Linting
uv run ruff check . --fix
uv run ruff format .

# Type checking
uv run mypy loan_processing/

# Tests
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git commit -m "feat: add income trend analysis to income agent"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots/examples if applicable
- Test results

## 🏗️ Architecture Guidelines

### Agent Development

When adding new agents:

1. **Create persona file**: `loan_processing/agents/agent-persona/your-agent-persona.md`
2. **Update configuration**: Add to `loan_processing/config/agents.yaml`
3. **Define output format**: Specify structured output requirements
4. **Add tests**: Create `tests/test_your_agent.py`

### MCP Server Development

When adding MCP servers:

1. **Create server module**: `loan_processing/tools/mcp_servers/your_server/`
2. **Implement server.py**: Follow existing server patterns
3. **Add to configuration**: Update `agents.yaml` with server details
4. **Document tools**: List all tools the server provides

## 📋 Code Style

### Python Style Guide

- Use `ruff` for linting and formatting
- Follow PEP 8 with 120 character line limit
- Use descriptive variable names
- Add type hints for all functions
- Write comprehensive docstrings

### Example Function:

```python
def calculate_debt_to_income_ratio(
    monthly_debt: Decimal,
    monthly_income: Decimal,
    include_proposed_payment: bool = True
) -> float:
    """
    Calculate the debt-to-income ratio for loan qualification.
    
    Args:
        monthly_debt: Total monthly debt payments
        monthly_income: Gross monthly income
        include_proposed_payment: Whether to include proposed loan payment
        
    Returns:
        DTI ratio as a percentage (0-100)
        
    Raises:
        ValueError: If monthly_income is zero or negative
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be positive")
        
    return float((monthly_debt / monthly_income) * 100)
```

## 🧪 Testing Guidelines

### Test Structure

- Unit tests: `tests/test_*.py`
- Integration tests: `tests/test_integration_*.py`
- Use pytest fixtures for common test data
- Mock external dependencies
- Test both success and failure cases

### Example Test:

```python
def test_agent_creation():
    """Test that agents are created with correct configuration."""
    agent = AgentRegistry.create_agent("intake", model="gpt-4")
    
    assert agent.name == "Intake Agent"
    assert agent.model == "gpt-4"
    assert len(agent.mcp_servers) == 0  # Optimized for speed
```

## 📚 Documentation

### Documentation Requirements

- Update README.md for user-facing changes
- Update CLAUDE.md for AI development instructions
- Add docstrings to all new code
- Create ADRs for architectural decisions
- Update configuration examples

### ADR Format

Create `docs/decisions/adr-XXX-title.md`:

```markdown
# ADR-XXX: Title

## Status
Accepted/Proposed/Deprecated

## Context
Why this decision is needed

## Decision
What we're doing

## Consequences
What happens as a result
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs
- Environment details

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Impact on existing functionality

## 🔒 Security

- Never commit secrets or API keys
- Report security issues privately (see SECURITY.md)
- Use secure coding practices
- Validate all inputs
- Follow principle of least privilege

## 📊 Performance

- Profile code for bottlenecks
- Optimize database queries
- Use async operations where appropriate
- Cache expensive computations
- Monitor memory usage

## 🎯 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Coverage maintained >80%
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No hardcoded values
- [ ] No sensitive data exposed
- [ ] Commit messages follow format
- [ ] PR description is complete

## 💬 Getting Help

- Open an issue for bugs/features
- Check existing issues first
- Join discussions in issues/PRs
- Review documentation thoroughly
- Ask questions - we're here to help!

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to make loan processing more efficient and accessible!

---

*By contributing, you agree that your contributions will be licensed under the MIT License.*