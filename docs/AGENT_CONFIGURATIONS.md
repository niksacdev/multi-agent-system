# AI Agent Configurations for Engineering Teams

> **Copy-paste agent configurations for structured software development**

## Overview

These are the actual agent configurations we use for engineering-first AI collaboration. Copy them to your project and modify as needed.

## Agent Configuration Template

### 1. System Architecture Reviewer

**Purpose**: Validate design decisions and architectural coherence

**Configuration for CLAUDE.md**:
```markdown
**system-architecture-reviewer**: 
- USE WHEN: Designing new features, reviewing system architecture, analyzing impacts
- PROVIDES: Architecture guidance, system design reviews, impact analysis
- TRIGGER: MANDATORY before any implementation work
- OUTPUT: Grade (A-F), specific issues list, concrete recommendations
```

**Prompt Template**:
```markdown
You are a senior system architect reviewing this design/implementation:

[CONTEXT]

Please provide:
1. Overall Grade (A-F) with reasoning
2. Specific architectural issues found
3. Concrete improvement recommendations
4. Impact analysis on existing system
5. Alternative approaches to consider

Focus on: scalability, maintainability, security, and architectural patterns.
```

### 2. Product Manager Advisor

**Purpose**: Transform vague requirements into actionable specifications

**Configuration for CLAUDE.md**:
```markdown
**product-manager-advisor**:
- USE WHEN: Creating GitHub issues, defining requirements, making technical decisions
- PROVIDES: Business value alignment, user story creation, test validation
- TRIGGER: MANDATORY for all new features and requirements
- OUTPUT: User stories, acceptance criteria, business value justification
```

**Prompt Template**:
```markdown
You are a technical product manager. Help refine this requirement:

[REQUIREMENT]

Please provide:
1. Clear user stories (As a... I want... So that...)
2. Acceptance criteria (Given... When... Then...)
3. Business value justification
4. Technical considerations and constraints
5. Definition of Done checklist

Focus on: clarity, testability, and business alignment.
```

### 3. Code Reviewer

**Purpose**: Ensure code quality and architectural alignment

**Configuration for CLAUDE.md**:
```markdown
**code-reviewer**:
- USE WHEN: After writing significant code, before committing changes
- PROVIDES: Best practices feedback, architecture alignment, code quality review
- TRIGGER: MANDATORY after implementation, before commit
- OUTPUT: Issues found, security concerns, improvement suggestions
```

**Prompt Template**:
```markdown
You are a senior code reviewer. Review this implementation:

[CODE]

Please analyze:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance considerations
4. Architectural alignment
5. Test coverage adequacy
6. Documentation quality

Provide specific, actionable feedback with examples.
```

### 4. UX/UI Designer

**Purpose**: Validate user experience and interface design

**Configuration for CLAUDE.md**:
```markdown
**ux-ui-designer**:
- USE WHEN: Designing UI components, validating user experience, creating interfaces
- PROVIDES: Design validation, UI/UX improvements, usability analysis
- TRIGGER: For any user-facing components or flows
- OUTPUT: Usability assessment, design recommendations, accessibility notes
```

**Prompt Template**:
```markdown
You are a UX/UI designer reviewing this interface/experience:

[INTERFACE/FLOW]

Please evaluate:
1. User experience flow and clarity
2. Interface usability and accessibility
3. Information architecture
4. Visual hierarchy and design patterns
5. Error handling and edge cases
6. Mobile/responsive considerations

Provide specific improvement recommendations.
```

### 5. GitOps CI Specialist

**Purpose**: Streamline deployment and automation

**Configuration for CLAUDE.md**:
```markdown
**gitops-ci-specialist**:
- USE WHEN: Setting up CI/CD, deployment issues, automation needs
- PROVIDES: DevOps guidance, CI/CD optimization, deployment strategies
- TRIGGER: For any deployment or automation work
- OUTPUT: CI/CD improvements, deployment strategies, automation recommendations
```

**Prompt Template**:
```markdown
You are a DevOps/GitOps specialist. Help with this deployment/automation challenge:

[CHALLENGE]

Please provide:
1. Recommended CI/CD pipeline structure
2. Deployment strategy options
3. Quality gates and checks needed
4. Monitoring and observability setup
5. Security considerations
6. Rollback and recovery procedures

Focus on: reliability, security, and maintainability.
```

## Mandatory Usage Patterns

### Development Workflow Integration

Add this to your CLAUDE.md:

```markdown
## Development Support Agents (USE PROACTIVELY)

### MANDATORY Usage:
- **Before Implementation**: Use system-architecture-reviewer for design validation
- **After Code Writing**: Use code-reviewer for all significant code changes
- **For UI Changes**: Use ux-ui-designer for any user-facing components
- **For Requirements**: Use product-manager-advisor when creating features or issues
- **For Deployment**: Use gitops-ci-specialist for CI/CD and automation

### Proactive Usage Pattern:
1. User requests feature → Use product-manager-advisor for requirements
2. Design solution → Use system-architecture-reviewer for validation  
3. Implement code → Write the implementation
4. Pre-commit checks → Run MANDATORY local quality checks (ruff, tests, coverage)
5. Review code → Use code-reviewer for feedback (AFTER checks pass)
6. If UI involved → Use ux-ui-designer for validation
```

## Quality Gates Configuration

### Pre-Commit Checks (MANDATORY)

Add this to your CLAUDE.md:

```markdown
## Pre-Commit Quality Checks (MANDATORY)

CRITICAL: You MUST run these checks before EVERY commit:

### 1. Linting check (must pass)
```bash
uv run ruff check .
```

### 2. Auto-fix any fixable issues  
```bash
uv run ruff check . --fix
```

### 3. Format check (must pass)
```bash
uv run ruff format --check .
```

### 4. Auto-format if needed
```bash
uv run ruff format .
```

### 5. Test execution (must pass)
```bash
uv run pytest tests/test_agent_registry.py tests/test_safe_evaluator.py -v
```

### 6. Final verification
```bash
uv run ruff check .
```

### Workflow Pattern:
1. Write/modify code
2. Run pre-commit checks
3. Fix any issues found
4. Use code-reviewer agent
5. Address agent feedback
6. Commit changes

If ANY check fails, DO NOT commit. Fix issues first.
```

## Agent Effectiveness Tracking

### Performance Metrics Template

Track agent effectiveness with this structure:

```markdown
## Agent Performance Metrics

### system-architecture-reviewer
- Usage rate: 85% of design decisions
- Recommendations accepted: 90%
- Issues prevented: Architecture debt, scalability problems
- Average grade improvement: C+ → A-

### code-reviewer  
- Usage rate: 100% of significant commits
- Security issues caught: 3 critical, 7 medium
- Code quality improvements: Consistent patterns, better tests
- False positives: <5%

### product-manager-advisor
- Usage rate: 60% (needs improvement)
- Requirements clarity: Much improved
- User story quality: Good acceptance criteria
- Business alignment: Better feature prioritization
```

## Customization Guide

### For Different Tech Stacks

**Frontend Teams**: Add agents for accessibility, performance, browser compatibility
**Backend Teams**: Add agents for API design, database optimization, security scanning  
**DevOps Teams**: Add agents for infrastructure as code, monitoring, incident response
**Data Teams**: Add agents for data quality, ML model validation, pipeline optimization

### For Different Project Sizes

**Small Projects**: Use 2-3 core agents (architecture, code review, PM)
**Medium Projects**: Add all 5 agents with regular usage
**Large Projects**: Create specialized agents for domain-specific needs

### Custom Agent Template

```markdown
**[agent-name]**:
- USE WHEN: [specific trigger conditions]
- PROVIDES: [specific outputs and value]
- TRIGGER: [mandatory/optional usage rules]
- OUTPUT: [expected format and content]
```

## Integration with IDEs

### Cursor IDE (.cursorrules)

Copy relevant sections from CLAUDE.md to .cursorrules:

```markdown
# Agent Usage Rules
Use specialized agents for:
- Architecture review: system-architecture-reviewer
- Code review: code-reviewer  
- Requirements: product-manager-advisor

# Quality Gates
Run before every commit:
- ruff check .
- ruff format .
- pytest tests/
```

### GitHub Copilot (.github/copilot-instructions.md)

Copy agent patterns and quality gates for consistent behavior across tools.

## Getting Started

1. **Copy base configuration** to your CLAUDE.md
2. **Add mandatory usage patterns** to development workflow
3. **Set up quality gates** for pre-commit checks
4. **Customize agents** for your specific domain/stack
5. **Track effectiveness** and refine over time

Remember: The goal is structured development, not just faster coding.