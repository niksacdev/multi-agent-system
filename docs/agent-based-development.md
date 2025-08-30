# AI Agents in Software Development: Practical Patterns

> **How we structured AI-assisted development with specialized agents**

> DISCLAIMER: This system was built in 72 hours by 1 human developer with Claude and specialized agents. It's not production-ready, but it demonstrates structured development learnings for a human-agent engineering team.

## Table of Contents

1. [The Problem](#the-problem)
2. [Overview](#overview)
3. [Agent Configuration Patterns](#1-agent-configuration-patterns)
   - [Copy-Paste Agent Setup](#copy-paste-agent-setup)
   - [Development Workflow Agents](#development-workflow-agents)
   - [Agent Invocation: Beyond Chat Windows](#agent-invocation-beyond-chat-windows)
4. [Development Workflow](#2-development-workflow)
   - [Core Development Pattern](#core-development-pattern)
   - [Inner Loop: Local Development](#inner-loop-local-development-with-agent-orchestration)
   - [Outer Loop: GitOps Integration](#outer-loop-gitops-agent--claude-integration)
5. [Cross-IDE / Tool Compatibility](#3-cross-ide--tool-compatibility)
   - [Claude Code vs Multi-Window IDEs](#claude-code-vs-multi-window-ides)
   - [Single Source of Truth](#our-solution-single-source-of-truth-with-tool-specific-adaptations)
6. [Jobs-to-be-Done Framework](#4-jobs-to-be-done-framework-for-business-agent-personas)
7. [Key Insights and Gotchas](#5-key-insights-and-gotchas)
8. [Architecture Decision Records](#6-architecture-decision-records-pattern)
9. [Critical Lessons Learned](#7-critical-lessons-learned)
   - [Token Optimization](#token-optimization-discovery)
   - [Context Loss Prevention](#the-loss-in-the-middle-problem)
   - [Development Pattern Evolution](#development-pattern-evolution)
10. [Common Pitfalls](#common-pitfalls)
11. [Appendix: Getting Started Resources](#appendix-getting-started-resources)

## The Problem

AI coding tools (vibe coding assistants) often lead to unmaintainable code:
- Copy-paste development without architectural consideration
- Missing documentation of decisions and trade-offs
- No systematic quality checks
- Technical debt accumulation

We tried a structured approach with specialized AI agents and documented the results.

## Overview

An experiment using AI development agents to build a multi-agent system:
- 5 specialized development workflow agents (architecture review, code review, etc.)
- Structured inner/outer development loops
- Architecture Decision Records for capturing agent feedback
- Automated quality gates integrated with agent workflow

Results: Real world implementation, 91% coverage, working CI/CD pipeline.

### Conclusion: Moving Beyond Vibe Coding

Our experiment showed that structured Human-AI collaboration can move beyond typical "vibe coding" to create maintainable systems. Success requires:

1. **Clear agent roles** and boundaries
2. **Human strategic oversight** 
3. **Quality automation** and gates
4. **Honest assessment** of what works

This isn't about replacing developers—it's about creating better development practices with AI assistance. The goal is sustainable code, not just working code.

### Lessons Learned

1. **Agents need boundaries**: Without explicit rules, they make process mistakes
2. **Humans provide perspective**: Strategic thinking can't be delegated
3. **Context is everything**: Lost context means repeated work
4. **Simpler is better**: Agents tend toward complexity
5. **Trust but verify**: Always review agent output

## 1. Agent Configuration Patterns

### Copy-Paste Agent Setup

We've extracted all our development agent configurations for reuse: **[Developer Agents →](./developer-agents/)**

**What's included**:
- Complete agent persona definitions with prompts
- CLAUDE.md configuration templates  
- Quality gate automation patterns
- IDE integration examples (.cursor/rules/, copilot-instructions)

### Development Workflow Agents

We configured 5 specialized development agents in CLAUDE.md with persistent personas:

```markdown
## Development Support Agents (USE PROACTIVELY)
```

1. **[system-architecture-reviewer](./developer-agents/system-architecture-reviewer.md)**: 
   - JOB: Review proposed system designs for maintainability and best practices
   - TRIGGER: MANDATORY before implementing new features or refactoring
   - OUTPUT: Grade (A-F), specific issues, concrete recommendations

2. **[code-reviewer](./developer-agents/code-reviewer.md)**:
   - JOB: Analyze code for security, quality, and adherence to patterns
   - TRIGGER: MANDATORY after writing significant code, before commits
   - OUTPUT: Security scan, quality feedback, improvement suggestions

3. **[product-manager-advisor](./developer-agents/product-manager-advisor.md)**:
   - JOB: Translate business needs into technical requirements
   - TRIGGER: When defining features, creating issues, validating tests
   - OUTPUT: GitHub issues, acceptance criteria, business context

4. **[ux-ui-designer](./developer-agents/ux-ui-designer.md)**:
   - JOB: Design validation and user experience analysis
   - TRIGGER: When designing UI components or validating UX
   - OUTPUT: Design validation, usability analysis, interface recommendations

5. **[gitops-ci-specialist](./developer-agents/gitops-ci-specialist.md)**:
   - JOB: Git workflow guidance and CI/CD pipeline management
   - TRIGGER: When committing code or troubleshooting CI/CD issues
   - OUTPUT: Git workflow guidance, pipeline troubleshooting, automation setup

### Agent Invocation: Beyond Chat Windows

**Key insight**: Agents are persistent markdown persona files with configured trigger rules, not one-off chat prompts.

**In CLAUDE.md configuration**:
```markdown
## Development Support Agents (USE PROACTIVELY)

**system-architecture-reviewer**: 
- TRIGGER: MANDATORY before implementation
- PERSONA: Persistent instructions for architecture review
- INVOCATION: Claude Code orchestration loop automatically calls based on context

**code-reviewer**:
- TRIGGER: MANDATORY after significant code changes  
- PERSONA: Persistent security and quality review instructions
- INVOCATION: Triggered by code completion, not explicit user request
```

**Advantages over chat**:
1. **Persistent expertise**: Agent personas don't reset between sessions
2. **Consistent output**: Same review criteria every time
3. **IDE integration**: Works with Claude Code orchestration, Cursor, GitHub Copilot
4. **Automatic triggering**: Based on development context, not manual prompts
5. **Portable**: Same .md files work across AI development tools


## 2. Development Workflow

### Core Development Pattern

1. **Human + Claude pair programming**:
   - Human: Strategic decisions, context, priorities
   - Claude: Implementation, code generation, file operations

2. **Specialized agent consultation**:
   - Triggered by specific development phases
   - Each agent provides domain expertise
   - Results feed back into main development

### Inner Loop: Local Development with Agent Orchestration

```bash
# Human provides strategic direction, Claude orchestrates agents based on CLAUDE.md triggers

1. Feature Request → product-manager-advisor → GitHub issues, acceptance criteria
2. Design Phase → system-architecture-reviewer → Pattern validation, grade design  
3. Implementation → Human + Claude → Code generation, strategic decisions
4. Quality Gate → code-reviewer → Security scan, best practices check
5. Local Validation → Automated → ruff check, pytest, coverage
```

### Outer Loop: GitOps Agent + Claude Integration

**How we created an effective outer loop using agents**:

#### Step 1: GitOps Agent Designs CI/CD Strategy

We used the [gitops-ci-specialist](./developer-agents/gitops-ci-specialist.md) agent to design our CI/CD approach:

```bash
# Claude Code session with gitops agent
claude> Use gitops-ci-specialist to design a CI/CD pipeline for our multi-agent system

# Agent output:
- Recommended multi-job pipeline with quality gates
- Suggested Claude integration points for automated review
- Designed failure escalation patterns
- Created branch protection strategies
```

#### Step 2: Claude Implements Agent Recommendations

Based on gitops agent guidance, Claude Code created the actual GitHub Actions:

```yaml
# .github/workflows/test.yml - Multi-stage quality gates
jobs:
  test:        # Core stable tests (38 passing, 91% coverage)
  lint:        # Ruff linting and formatting  
  security:    # pip-audit security scan
  validate-architecture:  # Domain boundary validation

# .github/workflows/claude-code-review.yml - Automatic PR review
claude-review:
  uses: anthropics/claude-code-action@beta
  # Reviews every PR against same standards as local development

# .github/workflows/claude.yml - Interactive troubleshooting
# Triggered by @claude mentions in PR comments
```

#### Step 3: GitOps Agent + Claude Handle CI Failures

**Real example - The Testing Crisis (Hours 4-8)**:

```bash
# Initial problem: 15+ test failures after refactoring
# GitHub Actions failing repeatedly

# GitOps agent analysis:
claude> Use gitops-ci-specialist to analyze these CI failures

GitOps Agent Output:
- "Pipeline is unstable due to test interdependencies"
- "Recommend: Focus on core stable tests, mark legacy tests"
- "Priority: Get CI green, then iterate"

# Claude + Human decision:
Human: "Be pragmatic - focus on stable core suite"
Claude: Creates focused test.yml running only core stable tests

# Result: 30-minute fix, stable CI pipeline
```

#### Step 4: Continuous Feedback Loop

**GitOps agent continuously improves the pipeline**:

```bash
# After each sprint:
claude> Use gitops-ci-specialist to review our CI/CD effectiveness

# Agent provides:
- Performance metrics analysis
- Failure pattern identification  
- Optimization recommendations
- New automation opportunities
```

**Human-in-the-Loop Integration**:
```bash
# Automatic escalation triggers:
├── Core test failures → Block merging, notify humans
├── Coverage drops below 85% → Request manual review
├── Security audit warnings → Require human approval
├── Architecture violations → Flag for architect review

# Interactive help:
# Comment "@claude" on any PR for context-aware assistance
# Claude reads CI results and provides specific guidance
```

**Key insight**: The gitops agent designed the strategy, Claude implemented it, and together they created a self-improving CI/CD system that escalates appropriately to humans.

## 3. Cross-IDE / Tool Compatibility

### Claude Code vs Multi-Window IDEs

**Key Discovery**: Claude Code's ability to orchestrate specialized sub-agents provided superior development workflow compared to multi-window IDE approaches (like GitHub Copilot with multiple panels).

#### Claude Code's Sub-Agent Orchestration Advantage

**Traditional Multi-Window Approach (GitHub Copilot, Cursor)**:
```
┌──────────────┬──────────────┬──────────────┐
│   Editor     │   Chat 1     │   Chat 2     │
│              │ (General AI) │ (Another AI) │
│   Code       ├──────────────┼──────────────┤
│              │   Terminal   │   Explorer   │
└──────────────┴──────────────┴──────────────┘

Problems:
- Context scattered across windows
- Manual coordination between AI instances
- No persistent agent specialization
- Repeated context establishment
```

**Claude Code's Orchestrated Sub-Agents**:
```
Claude Code (Orchestrator)
    ├── system-architecture-reviewer (persistent persona)
    ├── code-reviewer (persistent persona)
    ├── product-manager-advisor (persistent persona)
    ├── ux-ui-designer (persistent persona)
    └── gitops-ci-specialist (persistent persona)

Benefits:
- Single conversational flow
- Automatic agent invocation based on context
- Persistent specialized expertise
- Accumulated context across all agents
```

#### Real Example: Feature Development

**Multi-Window Approach**:
```bash
# Window 1: Ask Copilot for architecture review
"Can you review this architecture?"
# Copy response, paste into notes

# Window 2: Ask different AI for code review
"Can you review this code?" 
# Copy response, manually merge feedback

# Window 3: Ask for PM perspective
"What are the business implications?"
# Lose context, re-explain everything
```

**Claude Code Sub-Agent Orchestration**:
```bash
# Single conversation with Claude Code
claude> "I need to add a new authentication feature"

# Claude automatically orchestrates:
1. Invokes product-manager-advisor → Creates requirements
2. Invokes system-architecture-reviewer → Validates design
3. Main Claude implements code
4. Invokes code-reviewer → Reviews implementation
5. Invokes gitops-ci-specialist → Sets up CI/CD

# All in one flow, context preserved
```

#### Measurable Benefits

| Metric | Multi-Window | Claude Code Sub-Agents | Improvement |
|--------|--------------|------------------------|-------------|
| Context Switches | 15-20 per feature | 0 (single flow) | 100% reduction |
| Time to Feature | 4-6 hours | 1-2 hours | 66% faster |
| Context Re-establishment | 5-10 times | 0 times | 100% reduction |
| Agent Expertise Consistency | Variable | Persistent | 100% consistent |
| Decision Documentation | Manual | Automatic via ADRs | 100% automated |

### The Challenge: Team Using Different AI Tools

Despite Claude Code's advantages, development teams often use different AI tools:
- Some developers prefer Claude Code terminal
- Others use Cursor IDE with AI features
- GitHub Copilot users want consistent behavior
- New team members may have different tool preferences

### Our Solution: Single Source of Truth with Tool-Specific Adaptations

**Master configuration**: `CLAUDE.md` contains all development practices and agent definitions.

**Tool-specific adaptations**: We asked Claude to create compatible instruction files for each tool:

```bash
# Repository structure for multi-tool support
CLAUDE.md                           # Master configuration (Claude Code)
.cursor/rules/*.mdc                 # Cursor IDE rule files  
.github/instructions/copilot-instructions.md  # GitHub Copilot instructions
```

### Implementation Pattern

**Step 1**: Define everything in `CLAUDE.md`
```markdown
## Development Support Agents (USE PROACTIVELY)
**system-architecture-reviewer**: 
- TRIGGER: MANDATORY before implementation
- OUTPUT: Grade (A-F), specific issues, recommendations
```

**Step 2**: Ask Claude to generate tool-specific versions
```bash
# In Claude Code terminal:
claude> Create Cursor rules that mirror our CLAUDE.md agent definitions
claude> Create GitHub Copilot instructions that follow our development workflow
```

**Step 3**: Synchronization process
```markdown
# In CLAUDE.md:
> **📋 Instruction Sync**: This is the **master reference** for all development practices. 
> When updating, sync changes to `.cursor/rules/` and `.github/instructions/copilot-instructions.md`. 
> See `.github/sync-instructions.md` for guidelines.
```

### Result: Consistent Development Experience

Any developer can join the project and get the same AI assistance:
- **Claude Code users**: Follow CLAUDE.md directly
- **Cursor users**: Get same agent patterns through .cursor/rules/
- **GitHub Copilot users**: Follow adapted instructions for their tool
- **Mixed teams**: All tools provide consistent guidance

**Benefits**:
1. **No tool lock-in**: Teams can choose preferred AI tools
2. **Consistent quality**: Same standards regardless of tool choice
3. **Easy onboarding**: New developers get instant AI guidance
4. **Future-proof**: Add support for new AI tools as they emerge

## 4. Jobs-to-be-Done Framework for Business Agent Personas

### Real World Scenario Alignment with Agents

While the previous sections focused on **development workflow agents** (architecture review, code review, etc.), we also built **business domain agents** using the Jobs-to-be-Done framework.

### The JTBD Approach for Business Agents

Instead of defining agents by technical capabilities, we used Jobs-to-be-Done to understand what customers actually want to accomplish:

**Example**: Intake Agent persona uses JTBD thinking:

```markdown
# From: loan_processing/agents/shared/agent-persona/intake-agent-persona.md

## Jobs-to-be-Done Focus

**Primary Customer Job**: "I want to provide my information once and have it processed accurately and quickly, so I can move forward with confidence."

**Key Outcomes You Enable**:
- Submit complete application without re-entries (eliminate repetitive data entry)
- Get immediate validation and clear guidance (reduce anxiety about completeness) 
- Experience progress momentum (build confidence in the process)
- Receive confirmation and transparent status (trust in system capability)

**Success Metrics**: <5min processing, 95%+ satisfaction, <3% re-work rate, zero security incidents
```

### Using Development Agents to Build Business Agents

**Key insight**: We used our **development workflow agents** to help design the **business domain agents**.

**Process**:
```bash
# Step 1: Market research with UX agent
claude> Use ux-ui-designer to analyze loan application user journeys and pain points

# Step 2: Business context with PM agent  
claude> Use product-manager-advisor to define customer jobs-to-be-done for loan processing

# Step 3: Architecture review
claude> Use system-architecture-reviewer to design agent persona structure

# Result: Business agent personas like intake-agent-persona.md
```

**UX Agent Contribution**:
- Analyzed user pain points in loan applications through LLM knowledge (can be augmented with local knowledge)
- Identified friction points in data collection
- Designed user-centric success metrics
- Validated agent behavior against user needs

**PM Agent Contribution**:
- Defined measurable success criteria
- Created acceptance criteria for agent behavior
- Ensured business value alignment

### Result: Agent Personas That Understand Customer Jobs

Each business agent persona includes:
```markdown
## Agent Identity & Role
[Technical capabilities]

## Jobs-to-be-Done Focus  
**Primary Customer Job**: [What customer wants to accomplish]
**Key Outcomes You Enable**: [How you help them succeed]
**Success Metrics**: [Measurable outcomes]

## Business Domain Knowledge
[Industry-specific context]
```

This approach created agents that understand not just **how** to process data, but **why** customers need it processed and **what outcomes** matter most.

## 5. Key Insights and Gotchas

### When Agent Specialization Helped vs Hurt

**Helped**: 
- **Architecture reviews** caught design flaws before implementation
- **Security scans** found `eval()` vulnerability that would have reached production
- **PM agent** created proper GitHub issues with acceptance criteria
- **UX agent** identified user pain points we hadn't considered

**Hurt**: 
- **Over-consultation** - asking every agent about everything slowed development
- **Context switching** - jumping between agent mindsets created confusion
- **Perfectionism paralysis** - agents pushed for ideal solutions over working solutions

### Critical Human Intervention Points

**When humans had to step in**:

1. **The GitHub Actions Spiral** (Hours 4-8):
   - Agents got stuck in circular debugging 
   - Same failed solutions repeated
   - **Human solution**: "Be pragmatic - focus on stable core tests, mark others as legacy"
   - **Result**: Fixed in 30 minutes

2. **Architecture Over-Engineering**:
   - Agents pushed for complex patterns
   - **Human guidance**: "Use existing tools, don't reinvent"
   - **Result**: Simpler, maintainable code

3. **Strategic Pivots**:
   - Agents excel at **known patterns**, struggle with **novel situations**
   - Humans provide course correction and context preservation

| Agents Excel At | Humans Essential For |
|----------------|---------------------|
| Pattern recognition | Breaking debugging loops |
| Systematic implementation | Strategic pivots |
| Security scanning | Business priority calls |
| Code generation | Process decisions |

## 6. Architecture Decision Records Pattern

**Problem**: AI development often lacks decision documentation.

**Solution**: Capture agent feedback in structured ADRs.

**Template**:
```markdown
# ADR-XXX: [Decision Title]

## Status: [Proposed/Accepted/Rejected]

## Context
[Agent that provided feedback]: [Agent assessment]
Grade: [A-F rating if provided]
Issues identified: [List of specific problems]

## Decision  
[What we decided to implement]

## Consequences
+ [Benefits]
- [Trade-offs]

## Implementation
[Specific code changes made]
```

**Example**: [adr-001-agent-registry-pattern.md](./decisions/adr-001-agent-registry-pattern.md)

## 7. Critical Lessons Learned

### Token Optimization Discovery

**Problem**: Large persona files (2000+ lines) causing excessive token consumption and slower agent responses.

**Discovery Process**:
- Intake agent taking 30+ seconds for simple validations
- Token usage analysis showed persona consuming 80% of context
- Business logic descriptions too verbose

**Solution**: 
```yaml
# Before: 2000+ line persona with extensive examples
# After: 300 line focused persona with clear directives

Key optimizations:
1. Remove redundant examples
2. Use concise bullet points over paragraphs  
3. Reference external docs instead of inline explanations
4. Focus on WHAT not HOW
```

**Result**: 
- 75% reduction in token usage
- 10x faster agent response times
- Clearer, more maintainable personas

### The "Loss in the Middle" Problem

**Problem**: After large refactoring sessions, Claude loses track of critical context and starts making conflicting changes.

**Symptoms**:
- Reverting previous fixes
- Forgetting architectural decisions
- Inconsistent naming conventions
- Circular debugging loops

**Solution Strategies**:

1. **Use `/compact` command in Claude**:
   ```
   /compact
   
   This consolidates the conversation, preserving key decisions while clearing noise
   ```

2. **Checkpoint Strategy**:
   ```bash
   # After major refactoring
   git commit -m "checkpoint: refactoring complete"
   
   # Create a summary for Claude
   "We just completed X refactoring. Key changes:
   1. Moved Y to Z
   2. Renamed A to B
   3. Next task: C"
   ```

3. **Context Anchoring**:
   - Start new sessions with clear context
   - Reference specific commits
   - Use ADRs to preserve decisions

### Development Pattern Evolution

**Early Approach** (Problematic):
- Long continuous sessions (8+ hours)
- Accumulating context without cleanup
- Vague instructions

**Optimized Approach**:
- Focused 2-3 hour sessions
- Clear task boundaries
- Explicit context management
- Regular `/compact` usage

### Debugging Patterns

**Context Loss Issues**:
```bash
# Problem: Terminal closes, lose all debugging context
# Solution: Implement session persistence
export CLAUDE_SESSION_ID="debugging-session-$(date +%s)"
echo "Session: $CLAUDE_SESSION_ID" >> debug.log
```

**Circular Debugging Detection**:
```python
# Problem: Agent repeats failed solutions
# Pattern: Track attempted solutions
attempted_fixes = set()
if current_fix in attempted_fixes:
    print("LOOP DETECTED: Human intervention needed")
```

## 7. Gotchas and Learnings

### Common Pitfalls

| Gotcha | Impact | Solution |
|--------|--------|----------|
| Context loss on terminal close | Lost debugging state | Implement session persistence |
| Circular debugging loops | Hours wasted | Add loop detection |
| Over-engineering tendency | Complex solutions for simple problems | Human guidance: "Use existing tools" |
| Token exhaustion | Amnesia and repeated failures | Human summarization and restart |
| Process violations | Commits to main, skipped tests | Explicit rules in CLAUDE.md |

---

## Appendix: Getting Started Resources

- [CLAUDE.md Template](../CLAUDE.md) - Copy and customize for your project
- [Agent Personas](../loan_processing/agents/shared/agent-persona/) - Example agent definitions
- [CI/CD Workflows](../.github/workflows/) - Production-ready automation
- [Architecture Decisions](./decisions/) - How we made key choices

Ready to build your own Tiny Team? Start with one agent, one developer, and one ambitious goal.