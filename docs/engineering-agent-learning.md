# Engineering Team Agent Learnings

> This document captures learnings on developing this sample with systematic agent collaboration. Based on `34` PRs, `50+` commits, and `18` ADRs created during rapid development. While the data is not enough to describe a pattern, we were able to validate the hypothesis of using Humain-AIagent interaction for software development lifecyle.

Published insights at [Applied Context](https://www.appliedcontext.ai/p/beyond-vibe-coding-a-multi-agent).

## Important Limitations

This was a `72-hour` sprint with `1` human + `7` AI agents. Results may differ for:
- Larger teams (`10+` developers)
- Longer projects (`3+` months)  
- Different project types (embedded systems, mobile apps, etc.)
- Teams without existing AI development experience

## Core Insights

Through this experiment, we discovered three fundamental patterns that shaped our understanding of human-agent collaboration:

### 1. Human Strategy + Agent Execution = Optimal Results

**What we observed**: The most effective development occurred when humans provided strategic direction while agents handled systematic execution tasks.

**Evidence**:
- **Security Analysis**: Code-reviewer agent detected `6` critical issues (model compatibility errors, phone validation failures) before production deployment
- **Documentation Consistency**: `18` ADRs created with consistent format and systematic decision capture
- **Content Optimization**: Reduced instruction bloat from `6,000` to `1,897` lines (`68%` reduction) with measurable response time improvements

**In practice**: 
- Agents excel at specialized review, validation, and systematic documentation
- Humans provide strategic direction, architectural vision, and final decisions
- Continuous feedback loop improves agent effectiveness over time

### 2. Agent Learning Curve Significantly Impacts Value

**What we observed**: Agent effectiveness improved dramatically as instructions became more tuned to repository structure, business goals, and project constraints.

**Evidence**:
- **Early failures**: Commit `254e065` - `125` lines of invalid tests deleted (agents designed incompatible test structure)
- **Architecture violations**: Commit `1fd1877` - Complete repository restructure needed after agents violated separation of concerns
- **Business constraint violations**: Commit `431f9ea` - Full API integration revert when agents added dependencies against provider-agnostic principles

**The Pattern**: Generic agent instructions produce poor results. Project-specific tuning and iterative refinement are essential for agent effectiveness.

### 3. Specialization Outperforms Generalization

**What we observed**: Focused domain agents delivered clear value, while generalized approaches struggled with cross-cutting architectural decisions.

**Evidence**:
- **Specialized success**: Security analysis found specific vulnerabilities, documentation agents maintained consistent ADR format
- **Generalized struggles**: Architecture decisions requiring broad system understanding needed human oversight to prevent complete restructures

**The Pattern**: Agent specialization within clear domain boundaries produces better outcomes than broad, generalized agent personas.

## The Development Journey

### Early Challenges: "Vibe Coding" Problems

Our initial approach suffered from typical AI development issues:
- **Test Infrastructure Breakdown**: Agents created tests incompatible with existing codebase patterns
- **Architecture Inconsistency**: Multiple restructure cycles as agents violated established principles  
- **Documentation Redundancy**: Overlapping content creation without hierarchical planning
- **Business Constraint Violations**: Agents ignored documented project principles

### Evolution to Structured Approach

Through iteration, we developed a systematic workflow:

**Generate → Test → Review → Refine → Commit**

This 5-stage process introduced explicit handoffs and human oversight at critical decision points.

### Key Turning Points

1. **Token Optimization Discovery**: Large persona files (`2000+` lines) caused `30+` second response times. Focused `300-line` personas with clear directives reduced token usage by `75%` and improved response times significantly.

2. **Context Management Solutions**: Long development sessions (`8+` hours) led to "loss in the middle" problems - agents would revert previous fixes and forget decisions. Solution: shorter focused sessions with explicit context management.

3. **Human Intervention Patterns**: We learned to detect when agents entered circular debugging loops and needed human strategic guidance to break out.

## Agent Orchestration Observations

### What Works: Structured Handoffs

**Pattern**: Each agent has explicit entry/exit criteria with clear output expectations.

**Implementation**: 
- Product manager creates GitHub issues → System architect validates design → Developer implements → Code reviewer validates → Sync coordinator maintains consistency

**Result**: Reduced circular discussions and clearer accountability for each development phase.

### What Works: Decentralized Decision-Making

**Pattern**: Agents make decisions within their domain expertise, with clear authority boundaries as compared to a single chat windows running all tasks.

**Implementation**: Code Review agent has authority over vulnerability assessment, architecture agent over design patterns, while humans still retain strategic direction.

**Result**: Faster specialized feedback without constant human mediation.

## Performance Trade-offs

### Token Consumption Reality

**Observation**: Multi-agent approaches consumed `5-15x` more tokens than single-agent development.

**Justification**: For complex projects requiring quality controls, the additional cost might be offset by:
- Earlier detection of architectural issues
- Consistent documentation creation
- Reduced technical debt accumulation

> These have to be tested on a larger codebase and more complex environment

### Coordination Overhead

**Investment Required**:
- Significant upfront time in agent persona configuration and definition
- Ongoing maintenance of agent instructions as project evolves
- Learning curve for team members adapting to agent workflows

**Payoff Observed**: After initial setup, agents provided consistent value in specialized domains without requiring re-training. Also, a pattern emerged where we modified agent prompts to learn as significant event happenned. For Example, the whenever the architect agent created an ADR it also updated it own prompts to better manage future changes.

## Implementation Lessons

### Start Conservative

**What worked**: Beginning with `2-3` specialized agents (system architect, code reviewer, product manager) allowed focus on core workflow patterns.

**What didn't work**: Trying to implement all agents simultaneously created too much complexity to manage effectively.

### Measure Specific Outcomes

**Metrics that mattered**:
- Code quality improvements (security vulnerabilities detected)
- Documentation consistency (ADR creation and format)
- Response time improvements (from instruction optimization)

**Metrics that didn't**: General productivity claims were difficult to substantiate with limited dataset.

## Context Management Reality

### The "Loss in Middle" challenge for IDE Agents
**What actually happened**: During long development sessions, Claude would contradict its own earlier decisions, revert fixes it had just made, or suggest solutions we'd already tried and rejected.

**Specific example**: In one session, Claude suggested the same failed API integration approach three times within an hour, each time "forgetting" why we'd rejected it previously.

**What we learned**: This isn't a bug - it's the natural result of context windows filling up and early conversation context getting pushed out.

**Practical solution that worked**: Using `/compact` command to summarize key decisions and reset the conversation context. This preserved important decisions while clearing noise.

## What We Won't Repeat

- **Long sessions without breaks**: `8+` hour sessions led to context confusion and contradictory decisions
- **Vague task boundaries**: "Fix the architecture" is too broad - agents need specific, focused tasks
- **Ignoring repeated failures**: When agents suggest the same failed solution twice, human intervention is needed


---

*These observations represent early learnings in multi-agent development. As the field evolves, we expect patterns and best practices to continue developing.*