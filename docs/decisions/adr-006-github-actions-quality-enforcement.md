# ADR-006: GitHub Actions for Quality Enforcement

## Status: Accepted

## Context

We needed to establish consistent code quality enforcement across the development team. Traditional approaches include:

- **Git hooks**: Client-side enforcement with setup complexity
- **Manual reviews**: Time-intensive and inconsistent 
- **CI/CD pipelines**: Server-side enforcement but can be complex

Our multi-agent development approach requires reliable quality gates since AI agents can generate code rapidly but may miss quality considerations.

## Decision

We chose **GitHub Actions over git hooks** for comprehensive quality enforcement.

### Implementation

**GitHub Actions Workflows**:
- **Test Suite** (`.github/workflows/test.yml`): Full test suite + coverage ≥90%
- **Code Quality**: Type checking, linting, formatting validation  
- **Security**: Dependency vulnerability scanning
- **Architecture**: Domain boundary validation (no SDK imports in models/services)
- **Branch Protection**: Required status checks prevent merging failed builds

**Branch Protection Rules**:
- Main branch protected with required status checks
- All quality gates must pass before merging
- No bypassing enforcement mechanisms

## Consequences

### Positive
- **Cannot be bypassed**: Server-side enforcement ensures consistency
- **Universal application**: Same environment and checks for all contributors
- **Comprehensive validation**: 83+ tests, >90% coverage, security, architecture
- **Clear feedback**: PR status checks and detailed failure reports
- **Team collaboration**: Automated reports and notifications
- **Audit trail**: Historical quality metrics and compliance records

### Negative
- **CI/CD dependency**: Requires GitHub Actions availability
- **Build time**: Quality checks add ~3-5 minutes per PR
- **Learning curve**: Developers must understand Actions feedback

### Neutral
- **Local development**: Optional local checks for faster feedback
- **Cost**: GitHub Actions minutes usage (minimal for current team size)

## Implementation Details

### Workflow Structure
```yaml
# .github/workflows/test.yml
Triggers: push, pull_request (main, develop)
Jobs:
  - test: 83+ tests, coverage validation
  - lint: mypy, ruff checks  
  - security: pip-audit dependency scan
  - validate-architecture: Domain boundary enforcement
```

### Quality Requirements
- All tests pass
- Coverage ≥90% 
- No type checking errors
- No linting violations
- Clean architecture boundaries
- No security vulnerabilities

### Developer Experience
```bash
# Local development (optional but recommended)
python run_tests.py --type all
mypy loan_processing/
ruff check .

# PR submission automatically triggers all checks
# Clear feedback on failures with actionable guidance
```

## Alternatives Considered

### Git Hooks
- **Rejected**: Can be bypassed, inconsistent setup, local environment dependencies
- **Use case**: Could complement for faster local feedback

### Manual Reviews Only  
- **Rejected**: Time-intensive, inconsistent standards, doesn't scale with AI-generated code

### External CI Services
- **Rejected**: Additional complexity, GitHub Actions integration superior for our workflow

## Related Decisions

- Complements ADR-003 (Support Agent Feedback) by providing automated quality gates
- Supports ADR-005 (Configuration-Driven Orchestration) quality requirements
- Enables reliable foundation for multi-agent development workflows

## Monitoring and Metrics

**Quality Metrics Tracked**:
- Test pass rate: Target >99%
- Coverage maintenance: ≥90% requirement  
- Build success rate: Monitor CI reliability
- Time to feedback: Optimize for <5 minutes total

**Success Indicators**:
- Zero quality regressions merged to main
- Consistent standards across all contributors
- Reduced manual review time for basic quality issues
- Historical quality trend improvement

This decision ensures **enterprise-grade quality** while maintaining **developer productivity** and **team collaboration** in our multi-agent development environment.