# ADR-015: Multi-Agent vs Single Orchestrator Architecture Choice

## Status

Accepted

## Context

During development review, we questioned whether the multi-agent architecture was over-engineered for current requirements. A single orchestrator calling MCP servers directly could be simpler with less overhead (4x fewer LLM calls, 75% latency reduction). We needed to decide whether to simplify to a single orchestrator or maintain the multi-agent architecture.

## Decision

**Keep the multi-agent architecture** as the strategic foundation for future extensibility and progressive autonomy.

## Rationale

### Current State vs Future Vision

While current MCP servers return mock data and agents follow sequential patterns, this is the starting point, not the end state. The multi-agent architecture is an investment in the right foundation that will pay dividends as complexity grows.

### Key Advantages

1. **Progressive Enhancement Without Refactoring**: Agents can gain intelligence as MCP servers are added without architectural changes
2. **Independent Evolution**: Different teams can enhance different agents without coordination
3. **Clean Integration Points**: New MCP servers plug into existing agents easily through configuration
4. **Regulatory Compliance**: Clear agent boundaries provide audit trails and explainable decisions

### Future MCP Ecosystem

The architecture supports a planned expansion to 20+ MCP servers, with each agent becoming increasingly autonomous in tool selection and decision-making.

## Consequences

### Positive
- No refactoring needed when complexity increases
- Teams can work independently on different agents
- Clear upgrade path from simple to sophisticated
- Audit-friendly architecture for regulated industry

### Negative
- Higher initial overhead (4x LLM calls)
- More complex debugging across agent boundaries
- Longer processing times in current state

## Future Work (GitHub Issues)

- [ ] Add document OCR capabilities to Intake Agent
- [ ] Integrate real credit bureau APIs for Credit Agent
- [ ] Implement parallel agent execution in orchestrator
- [ ] Add ML-based risk scoring models to Risk Agent
- [ ] Create fraud detection MCP server
- [ ] Implement dynamic agent routing based on application characteristics
- [ ] Add caching layer to reduce repeated MCP calls
- [ ] Optimize agent personas for token efficiency

## Related Decisions

- ADR-002: Agent Base Architecture
- ADR-004: Agent Handoff Pattern Implementation
- ADR-005: Configuration-Driven Orchestration

**Decision Date**: 2025-08-25
**Decision Author**: Development Team with system-architecture-reviewer validation