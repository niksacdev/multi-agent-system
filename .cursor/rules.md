# Cursor Rules - Multi-Agent Loan Processing System

## Primary Reference
See comprehensive guidelines: `CLAUDE.md`

## Quick Context
Multi-Agent System using OpenAI Agents SDK with MCP servers. Autonomous agents process loan applications.

## Critical Rules
1. **Security**: Use `applicant_id` (UUID), NEVER SSN
2. **Token Optimization**: Keep personas <500 lines
3. **References**: Use file paths, not inline code
4. **Testing**: Run `uv run python scripts/validate_ci_fix.py` before commits
5. **Package Manager**: Use `uv` only, never pip/poetry

## Architecture References
- Decisions: `docs/decisions/adr-*.md`  
- Agent patterns: `loan_processing/agents/providers/openai/`
- Personas: `loan_processing/agents/agent-persona/*.md`
- Config: `loan_processing/config/agents.yaml`

## Common Commands
```bash
# Validate before commit
uv run python scripts/validate_ci_fix.py

# Run tests
uv run pytest tests/test_agent_registry.py -v

# Start console app
uv run python scripts/run_console_app.py
```

## Development Workflow
1. Plan with support agents (see CLAUDE.md)
2. Implement with patterns from codebase
3. Run validation script before commit
4. Use small PRs (50-200 lines)

## File References Instead of Code
- Sequential pattern: `loan_processing/agents/providers/openai/orchestration/sequential.py`
- Error handling: `loan_processing/agents/providers/openai/orchestration/base.py:187-210`
- Agent creation: `loan_processing/agents/providers/openai/agentregistry.py`

## Support Agents
See `docs/developer-agents/*.md` for specialized guidance