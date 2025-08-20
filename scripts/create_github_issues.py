#!/usr/bin/env python3
"""
Script to create GitHub issues for experimental features.
This creates issues for both completed and future features of the multi-agent system.

Usage:
    python scripts/create_github_issues.py --dry-run  # Preview issues without creating
    python scripts/create_github_issues.py            # Create issues in GitHub
"""

import json
import os
import sys
from typing import Dict, List

# You'll need to install PyGithub: pip install PyGithub
# from github import Github


def get_completed_features() -> List[Dict]:
    """Get list of completed features that need documentation issues."""
    return [
        {
            "title": "Document and Reference Configuration-Driven Agent Management Implementation",
            "body": """## Completed Feature Documentation

This issue documents our configuration-driven agent management system implementation.

### Implementation References
- **Core Implementation:** `loan_processing/agents/providers/openai/agentregistry.py`
- **Configuration:** `loan_processing/agents/shared/config/agents.yaml`
- **Utils:** `loan_processing/utils/`
- **Key Commits:** 
  - `567bc4a` - Updated tests and CI to match optimized configuration
  - `5850ec2` - Configuration cleanup and optimization

### What This Provides
- YAML-based agent definitions with MCP server mappings
- Dynamic agent creation via `AgentRegistry.create_agent()`
- Persona-driven agent instructions from markdown files
- MCP server factory with caching for tool selection
- Type-safe configuration validation

### Why This Matters
- Enables rapid agent type addition without code changes
- Supports experimental agent configurations
- Maintains agent autonomy in tool selection
- Clear separation between orchestration and agent logic

### Acceptance Criteria
- [x] Agent registry supports configuration-driven creation
- [x] YAML configuration defines all agent types and capabilities
- [x] MCP server factory manages tool availability
- [x] Persona loader supports markdown-based instructions
- [x] Output format generator adds structured response requirements""",
            "labels": ["documentation", "completed-feature", "architecture", "enhancement"],
        },
        {
            "title": "Reference Sequential Multi-Agent Orchestration Pattern",
            "body": """## Completed Feature Documentation

Sequential orchestration pattern implementation for multi-agent loan processing.

### Implementation References
- **Core:** `loan_processing/agents/providers/openai/orchestration/sequential.py`
- **Base Classes:** `loan_processing/agents/providers/openai/orchestration/base.py`
- **Engine:** `loan_processing/agents/providers/openai/orchestration/engine.py`
- **Tests:** `tests/test_sequential_orchestration.py`
- **Key Commits:**
  - `44d162c` - Added comprehensive orchestration tests
  - `779898c` - Enhanced test scenarios for decision differentiation

### What This Provides
- Sequential agent execution with context passing
- Handoff condition validation between agents
- Audit trail and session management
- Error handling and workflow interruption
- Configurable agent dependencies

### User Journey
1. Application enters intake agent for initial validation
2. Credit agent evaluates creditworthiness using previous context
3. Income agent verifies employment and income
4. Risk agent synthesizes all assessments for final decision

### Acceptance Criteria
- [x] Sequential execution with context accumulation
- [x] Handoff validation between agents
- [x] Comprehensive audit trail
- [x] Error handling and recovery
- [x] Configuration-driven agent selection""",
            "labels": ["completed-feature", "orchestration", "architecture", "experimental"],
        },
        {
            "title": "Reference OpenAI Agents SDK Integration with MCP Tools",
            "body": """## Completed Feature Documentation

Integration with OpenAI Agents SDK and MCP (Model Context Protocol) servers.

### Implementation References
- **MCP Servers:**
  - `loan_processing/tools/mcp_servers/application_verification/`
  - `loan_processing/tools/mcp_servers/document_processing/`
  - `loan_processing/tools/mcp_servers/financial_calculations/`
- **Service Layer:** `loan_processing/tools/services/`
- **Tests:** `tests/mcp_servers/` (83 tests)
- **Key Commit:** `c319ab5` - Restored MCP server tests and updated CI

### What This Provides
- Three specialized MCP servers for loan processing tools
- Agent-autonomous tool selection based on task requirements
- Secure parameter handling (applicant_id instead of SSN)
- Service layer abstraction for business logic
- RESTful tool interfaces via MCP protocol

### Available Tools
- **Identity & Employment:** verify_identity, verify_employment, check_fraud_indicators
- **Document Processing:** extract_text, classify_documents, validate_formats
- **Financial Calculations:** calculate_dti, loan_affordability, risk_scoring

### Acceptance Criteria
- [x] MCP servers implement tool protocols
- [x] Agents autonomously select appropriate tools
- [x] Secure parameter handling enforced
- [x] Service layer abstracts business logic
- [x] Comprehensive test coverage (83 tests)""",
            "labels": ["completed-feature", "integration", "mcp-servers", "tools"],
        },
        {
            "title": "Reference Type-Safe Data Model Implementation with Pydantic",
            "body": """## Completed Feature Documentation

Comprehensive Pydantic models for type-safe loan processing data structures.

### Implementation References
- **Models:** `loan_processing/agents/shared/models/`
  - `application.py` - Loan application data structures
  - `assessment.py` - Agent assessment result models
  - `decision.py` - Final decision and recommendation models
- **Integration:** Used throughout agent registry and orchestration

### What This Provides
- Runtime data validation for all loan processing entities
- Type hints for better developer experience
- Serialization/deserialization for API integration
- Clear data contracts between system components
- Input sanitization and constraint enforcement

### Key Models
- `LoanApplication` - Core application data with validation rules
- `AgentAssessment` - Standardized assessment output format
- `LoanDecision` - Final decision with reasoning and conditions

### Acceptance Criteria
- [x] Pydantic models for all core entities
- [x] Runtime validation enforced
- [x] Type hints throughout codebase
- [x] Serialization for API readiness
- [x] Comprehensive field validation""",
            "labels": ["completed-feature", "data-models", "type-safety"],
        },
        {
            "title": "Reference AI-Assisted Development Workflow Integration",
            "body": """## Completed Feature Documentation

Integration of AI development agents for architecture, code quality, and product guidance.

### Implementation References
- **Documentation:** `CLAUDE.md` - Development workflow and agent usage
- **ADRs:** `docs/decisions/` - Architecture decisions with agent feedback
- **Integration:** Development agents used throughout the project

### Available Development Agents
- **system-architecture-reviewer** - Architecture validation and design review
- **code-reviewer** - Code quality and alignment checks
- **product-manager-advisor** - Requirements and business value alignment
- **ux-ui-designer** - User experience validation

### Development Workflow
1. Feature planning with product-manager-advisor
2. Architecture validation with system-architecture-reviewer
3. Implementation with continuous code-reviewer feedback
4. UI/UX validation with ux-ui-designer

### Acceptance Criteria
- [x] Development agent integration documented
- [x] Workflow guidelines established
- [x] ADRs created for agent feedback
- [x] Integration with Claude Code, GitHub Copilot, Cursor""",
            "labels": ["completed-feature", "developer-experience", "ai-assisted", "workflow"],
        },
        {
            "title": "Reference Agent Observability with OpenTelemetry",
            "body": """## Completed Feature Documentation

OTEL-based observability for monitoring agent communications and decisions.

### Implementation References
- **Observability Module:** `loan_processing/utils/observability.py`
- **Integration:** Throughout orchestration and agent execution
- **Configuration:** Environment-based OTEL configuration

### What This Provides
- Agent communication tracing
- Decision-making audit trail
- Performance metrics collection
- Context correlation across agents
- Structured logging with correlation IDs

### Observability Features
- Trace agent handoffs and context passing
- Monitor MCP server tool usage
- Track agent execution times
- Log decision reasoning
- Capture error propagation

### Acceptance Criteria
- [x] OTEL integration implemented
- [x] Correlation context tracking
- [x] Structured logging format
- [x] Agent communication visibility
- [x] Performance metrics collection""",
            "labels": ["completed-feature", "observability", "monitoring", "experimental"],
        },
    ]


def get_future_features() -> List[Dict]:
    """Get list of future features that need implementation issues."""
    return [
        {
            "title": "Implement Parallel Agent Processing for Independent Assessments",
            "body": """## Enhancement: Parallel Orchestration Pattern

Enable simultaneous agent processing when assessments are independent.

### User Story
As a loan processor, I want credit and income verification to happen simultaneously so that loan decisions can be made faster when agents don't depend on each other's results.

### Why This Matters
- Reduces loan processing time for time-sensitive applications
- Improves system throughput for high-volume scenarios
- Enables more responsive user experience
- Maintains audit trail even with concurrent processing

### Acceptance Criteria
- [ ] Create `ParallelPatternExecutor` similar to sequential pattern
- [ ] Implement agent dependency analysis
- [ ] Add parallel configuration support in YAML
- [ ] Ensure thread-safe context management
- [ ] Maintain audit trail for concurrent execution
- [ ] Add timeout handling for parallel agents
- [ ] Create configuration validation

### Technical Approach
- Build on existing orchestration base classes
- Reuse MCP server factory for concurrent access
- Extend OrchestrationContext for thread safety
- Add parallel-specific configuration validation""",
            "labels": ["enhancement", "orchestration", "experimental", "performance"],
        },
        {
            "title": "Implement Dynamic Agent Routing Based on Assessment Results",
            "body": """## Enhancement: Conditional Routing

Enable dynamic agent routing based on previous assessment results.

### User Story
As a risk manager, I want loan applications to follow different processing paths based on initial risk indicators so that low-risk applications can be fast-tracked while high-risk ones get enhanced scrutiny.

### Why This Matters
- Optimizes processing time based on application risk profile
- Enables fast-track processing for qualified applications
- Provides enhanced review path for complex cases
- Improves operational efficiency through smart routing

### Acceptance Criteria
- [ ] Design conditional routing configuration schema
- [ ] Implement `ConditionalRoutingExecutor`
- [ ] Add routing rule evaluation engine
- [ ] Support multiple routing paths
- [ ] Enable rule-based agent selection
- [ ] Add routing decision audit logging
- [ ] Create routing configuration validation

### Routing Examples
- High credit score → Skip enhanced credit checks
- Complex income sources → Add specialized income verification
- Fraud indicators → Add manual review step""",
            "labels": ["enhancement", "orchestration", "business-logic", "experimental"],
        },
        {
            "title": "Add Microsoft Autogen Provider Support",
            "body": """## Enhancement: Autogen Framework Integration

Implement Microsoft Autogen as an alternative multi-agent framework provider.

### User Story
As a developer, I want to experiment with different multi-agent frameworks so that I can compare approaches and choose the most suitable solution for specific use cases.

### Why This Matters
- Provides framework flexibility for different use cases
- Enables comparative analysis of multi-agent approaches
- Reduces vendor lock-in risk
- Supports diverse team preferences and expertise

### Acceptance Criteria
- [ ] Create Autogen provider implementation
- [ ] Add Autogen-specific configuration support
- [ ] Implement agent registry integration for Autogen
- [ ] Support MCP server integration with Autogen agents
- [ ] Add provider-specific orchestration patterns
- [ ] Create comparative testing framework
- [ ] Document framework selection guidelines

### Technical Approach
- Extend existing provider architecture
- Reuse MCP server implementations
- Maintain configuration-driven approach
- Support provider-specific optimizations""",
            "labels": ["enhancement", "integration", "framework-support", "experimental"],
        },
        {
            "title": "Implement LangChain Agents Framework Support",
            "body": """## Enhancement: LangChain Integration

Add LangChain Agents integration for additional framework flexibility.

### User Story
As a developer familiar with LangChain, I want to use LangChain agents in the loan processing system so that I can leverage existing LangChain tools and expertise.

### Why This Matters
- Leverages extensive LangChain tool ecosystem
- Supports developers with LangChain expertise
- Enables integration with existing LangChain applications
- Provides additional framework comparison data

### Acceptance Criteria
- [ ] Implement LangChain provider integration
- [ ] Add LangChain-specific agent configuration
- [ ] Support LangChain tool integration with MCP servers
- [ ] Create LangChain orchestration pattern adapters
- [ ] Add LangChain memory management integration
- [ ] Support LangChain callback systems
- [ ] Document LangChain-specific optimizations""",
            "labels": ["enhancement", "integration", "framework-support", "experimental"],
        },
        {
            "title": "Create REST API for Loan Processing Operations",
            "body": """## Enhancement: REST API Interface

Implement RESTful API for external system integration.

### User Story
As an application developer, I want a REST API for loan processing so that I can integrate loan decisions into web applications and mobile apps.

### Why This Matters
- Enables external system integration
- Supports web and mobile application development
- Provides standardized access interface
- Enables API-driven loan processing workflows

### Acceptance Criteria
- [ ] Design REST API schema for loan operations
- [ ] Implement FastAPI or similar framework
- [ ] Add authentication and authorization
- [ ] Support async processing with status endpoints
- [ ] Add API documentation and OpenAPI spec
- [ ] Implement rate limiting and error handling
- [ ] Add API monitoring and logging

### API Endpoints
- `POST /applications` - Submit loan application
- `GET /applications/{id}/status` - Check processing status
- `GET /applications/{id}/decision` - Retrieve final decision
- `POST /applications/{id}/reprocess` - Trigger reprocessing
- `GET /agents/types` - List available agent types""",
            "labels": ["enhancement", "api", "integration", "experimental"],
        },
        {
            "title": "Add GraphQL Interface for Complex Data Queries",
            "body": """## Enhancement: GraphQL Interface

Implement GraphQL for flexible data queries and real-time updates.

### User Story
As a frontend developer, I want a GraphQL API so that I can efficiently query exactly the loan processing data I need and receive real-time updates.

### Why This Matters
- Enables efficient data fetching for complex UIs
- Provides real-time processing status updates
- Reduces API calls through flexible querying
- Supports modern frontend development patterns

### Acceptance Criteria
- [ ] Design GraphQL schema for loan domain
- [ ] Implement GraphQL server with async resolvers
- [ ] Add subscription support for real-time updates
- [ ] Create data loaders for efficient access
- [ ] Add authentication and authorization
- [ ] Support complex queries across entities
- [ ] Add GraphQL playground and documentation""",
            "labels": ["enhancement", "api", "graphql", "experimental"],
        },
        {
            "title": "Build React-Based Web Application UI",
            "body": """## Enhancement: Web Application Interface

Create modern web UI for loan application submission and tracking.

### User Story
As a loan applicant, I want a web interface to submit my loan application and track its status so that I can complete the process online.

### Why This Matters
- Provides user-friendly application interface
- Enables self-service loan applications
- Reduces manual data entry
- Improves customer experience

### Acceptance Criteria
- [ ] Design responsive web UI with React
- [ ] Implement application submission forms
- [ ] Add real-time status tracking
- [ ] Create document upload interface
- [ ] Add decision visualization
- [ ] Implement user authentication
- [ ] Support mobile-responsive design

### UI Components
- Application form with validation
- Document upload with preview
- Status timeline visualization
- Decision explanation display
- Agent assessment details view""",
            "labels": ["enhancement", "frontend", "ui", "experimental"],
        },
        {
            "title": "Implement Enhanced Agent Communication Tracing",
            "body": """## Enhancement: Distributed Tracing

Enhance observability with comprehensive distributed tracing.

### User Story
As a system operator, I want detailed tracing of agent communications so that I can debug complex loan processing issues and optimize agent performance.

### Why This Matters
- Enables debugging of complex multi-agent workflows
- Provides performance optimization insights
- Supports compliance auditing requirements
- Improves system reliability through better observability

### Acceptance Criteria
- [ ] Extend OTEL integration for distributed tracing
- [ ] Add trace correlation across agent handoffs
- [ ] Implement communication span tracking
- [ ] Add trace visualization integration
- [ ] Support trace sampling for high volume
- [ ] Add trace-based performance metrics
- [ ] Create trace analysis dashboards

### Trace Information
- Agent execution times and dependencies
- MCP server tool usage patterns
- Context passing between agents
- Decision reasoning chains
- Error propagation paths""",
            "labels": ["enhancement", "observability", "tracing", "experimental"],
        },
        {
            "title": "Implement A/B Testing Framework for Agent Configurations",
            "body": """## Enhancement: A/B Testing Framework

Enable safe experimentation with different agent configurations.

### User Story
As a product manager, I want to A/B test different agent configurations so that I can optimize loan processing performance while maintaining risk controls.

### Why This Matters
- Enables data-driven agent optimization
- Reduces risk of experimental configuration deployment
- Provides quantitative comparison of agent approaches
- Supports continuous improvement of loan processing

### Acceptance Criteria
- [ ] Design A/B testing configuration schema
- [ ] Implement experiment assignment logic
- [ ] Add metric collection for analysis
- [ ] Create experiment result analysis tools
- [ ] Support gradual rollout of winning configs
- [ ] Add statistical significance testing
- [ ] Enable experiment safety controls

### A/B Test Examples
- Different credit scoring models
- Alternative orchestration patterns
- Varying agent timeout configurations
- Different persona instructions for agents""",
            "labels": ["enhancement", "experimentation", "testing", "experimental"],
        },
    ]


def create_issues_markdown() -> str:
    """Create markdown file with all issues for manual creation."""
    completed = get_completed_features()
    future = get_future_features()
    
    markdown = "# GitHub Issues for Multi-Agent Loan Processing System\n\n"
    markdown += "## Instructions\n"
    markdown += "1. Copy each issue below\n"
    markdown += "2. Create new issue in GitHub\n"
    markdown += "3. Add the specified labels\n"
    markdown += "4. For completed features, close the issue after creation\n\n"
    markdown += "---\n\n"
    
    markdown += "## Completed Features (Create and Close)\n\n"
    for i, issue in enumerate(completed, 1):
        markdown += f"### Issue {i}: {issue['title']}\n\n"
        markdown += f"**Labels:** {', '.join(issue['labels'])}\n\n"
        markdown += issue['body'] + "\n\n"
        markdown += "---\n\n"
    
    markdown += "## Future Features (Leave Open)\n\n"
    for i, issue in enumerate(future, len(completed) + 1):
        markdown += f"### Issue {i}: {issue['title']}\n\n"
        markdown += f"**Labels:** {', '.join(issue['labels'])}\n\n"
        markdown += issue['body'] + "\n\n"
        markdown += "---\n\n"
    
    return markdown


def main():
    """Main function to create GitHub issues."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create GitHub issues for experimental features")
    parser.add_argument("--dry-run", action="store_true", help="Preview issues without creating")
    parser.add_argument("--output", default="github_issues.md", help="Output markdown file")
    args = parser.parse_args()
    
    # Generate markdown file
    markdown_content = create_issues_markdown()
    
    with open(args.output, "w") as f:
        f.write(markdown_content)
    
    print(f"✅ Generated {args.output} with all issues")
    print(f"📋 Total issues: {len(get_completed_features())} completed, {len(get_future_features())} future")
    
    if args.dry_run:
        print("\n🔍 Dry run mode - no issues created in GitHub")
        print(f"📄 Review the issues in {args.output}")
    else:
        print("\n📝 To create issues in GitHub:")
        print("1. Install PyGithub: pip install PyGithub")
        print("2. Set GITHUB_TOKEN environment variable")
        print("3. Uncomment the GitHub API code in this script")
        print(f"4. Or manually create issues from {args.output}")


if __name__ == "__main__":
    main()