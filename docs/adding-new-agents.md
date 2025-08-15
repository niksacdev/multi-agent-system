# Adding New Agents to the System

This guide explains how to add new agent types to the loan processing system without modifying any Python code. The system is fully configuration-driven, so new agents are added by creating configuration files and persona definitions.

## Overview

To add a new agent, you need to:
1. Create a persona file that describes the agent's capabilities
2. Add the agent configuration to the agents.yaml file
3. Test the new agent

No Python code changes are required!

## Step 1: Create the Agent Persona

Create a new markdown file in `agent-persona/` directory:

**File**: `agent-persona/{agent_type}.md`

```markdown
# {Agent Name} Agent Persona

## Primary Responsibilities
- [List the main tasks this agent should perform]
- [Each responsibility should be clear and specific]

## Core Capabilities
- [Specific skills or functions this agent provides]
- [What tools or analysis methods it uses]

## Decision Criteria
- [What factors does the agent consider when making decisions]
- [Any specific thresholds or rules it should follow]

## Communication Style
- [How the agent should communicate with users]
- [Professional tone, level of detail, etc.]

## Key Constraints
- [Important limitations or requirements]
- [Compliance requirements]
- [Data security considerations]

## Example Assessment Process
1. [Step-by-step description of how the agent should work]
2. [Include any validation steps]
3. [Mention how it should handle edge cases]

## Success Metrics
- [How to measure if the agent is performing well]
- [What constitutes a successful assessment]
```

## Step 2: Add Agent Configuration

Edit `loan_processing/config/agents.yaml` and add your new agent:

```yaml
agents:
  your_agent_type:  # Use lowercase, underscores for consistency
    name: "Your Agent Name"
    description: "Brief description of what this agent does"
    persona_file: "your_agent_type"  # Must match the .md filename
    mcp_servers:
      - "application_verification"  # List required MCP servers
      - "document_processing"
      - "financial_calculations"
    capabilities:
      - "Capability 1"
      - "Capability 2"
      - "Capability 3"
    output_format:
      primary_result:
        type: "enum"
        values: ["PASS", "FAIL", "REVIEW"]
        description: "Primary assessment result"
      confidence_score:
        type: "float" 
        range: [0.0, 1.0]
        description: "Agent's confidence in assessment"
      detailed_findings:
        type: "array"
        item_type: "string"
        description: "List of detailed findings"
      recommendation:
        type: "string"
        description: "Agent's recommendation"
```

### Output Format Field Types

| Type | Description | Example |
|------|-------------|---------|
| `enum` | Fixed set of values | `values: ["LOW", "HIGH"]` |
| `integer` | Whole numbers | `range: [300, 850]` (optional) |
| `float` | Decimal numbers | `range: [0.0, 1.0]` (optional) |
| `decimal` | Money amounts | No range needed |
| `array` | List of items | `item_type: "string"` |
| `object` | JSON object | For complex nested data |
| `boolean` | true/false | For yes/no fields |
| `string` | Text values | Default type |

### MCP Server Options

Available MCP servers you can include:

- **application_verification**: Identity, address, employment verification
- **document_processing**: Document extraction and analysis
- **financial_calculations**: Financial calculations and risk assessments

## Step 3: Test Your New Agent

1. **Test Agent Creation**:
   ```python
   from loan_processing.providers.openai.agents import AgentRegistry
   
   # This should work without errors
   agent = AgentRegistry.create_agent("your_agent_type")
   print(f"Created: {agent.name}")
   ```

2. **Test in Orchestration Pattern**:
   Add your agent to an orchestration pattern in `loan_processing/orchestration/patterns/`:
   
   ```yaml
   agents:
     - type: "your_agent_type"
       name: "Your Agent Name"
       required: true
       timeout_seconds: 240
       description: "What this agent does in the workflow"
       success_conditions:
         - "primary_result != 'FAIL'"
         - "confidence_score >= 0.7"
   ```

## Examples

### Example 1: Compliance Agent

**File**: `agent-persona/compliance.md`
```markdown
# Compliance Agent Persona

## Primary Responsibilities
- Review loan applications for regulatory compliance
- Identify potential fair lending violations
- Ensure HMDA reporting requirements are met
- Validate ATR/QM compliance

## Core Capabilities
- Regulatory knowledge application
- Fair lending analysis
- Documentation review
- Compliance scoring

[... rest of persona definition]
```

**Configuration**:
```yaml
compliance:
  name: "Compliance Agent"
  description: "Ensures regulatory compliance and fair lending practices"
  persona_file: "compliance"
  mcp_servers:
    - "application_verification"
    - "document_processing"
  capabilities:
    - "Fair lending analysis"
    - "Regulatory compliance checking" 
    - "HMDA compliance validation"
  output_format:
    compliance_status:
      type: "enum"
      values: ["COMPLIANT", "NON_COMPLIANT", "REQUIRES_REVIEW"]
      description: "Overall compliance assessment"
    violations_found:
      type: "array"
      item_type: "string"
      description: "List of compliance violations"
    hmda_compliant:
      type: "boolean"
      description: "HMDA reporting compliance status"
    confidence_score:
      type: "float"
      range: [0.0, 1.0]
      description: "Confidence in compliance assessment"
```

### Example 2: Property Valuation Agent

```yaml
property_valuation:
  name: "Property Valuation Agent"
  description: "Assesses property value and related risks"
  persona_file: "property_valuation"
  mcp_servers:
    - "application_verification"
    - "financial_calculations"
  capabilities:
    - "Property value estimation"
    - "Market analysis"
    - "Appraisal review"
  output_format:
    estimated_value:
      type: "decimal"
      description: "Estimated property value"
    loan_to_value_ratio:
      type: "float"
      description: "LTV ratio calculation"
    market_conditions:
      type: "enum"
      values: ["STRONG", "STABLE", "DECLINING", "VOLATILE"]
      description: "Local market assessment"
    confidence_score:
      type: "float"
      range: [0.0, 1.0]
      description: "Confidence in valuation"
```

## Best Practices

### 1. Agent Naming
- Use lowercase with underscores: `property_valuation`, `fraud_detection`
- Keep names descriptive but concise
- Match the persona filename exactly

### 2. Output Format Design
- Always include a `confidence_score` field
- Use enums for standardized values
- Include arrays for lists of findings
- Add clear descriptions for all fields

### 3. Persona Writing
- Be specific about responsibilities and constraints
- Include examples of decision-making processes
- Mention any regulatory or compliance requirements
- Describe the expected communication style

### 4. MCP Server Selection
- Only include servers the agent actually needs
- Consider performance impact of multiple servers
- Document why each server is required

## Integration with Orchestration Patterns

Once your agent is configured, you can use it in orchestration patterns:

### Sequential Pattern
```yaml
agents:
  - type: "intake"
    # ... existing config
  - type: "your_agent_type"
    name: "Your Agent Name"
    required: true
    timeout_seconds: 180
    depends_on: ["intake"]
    success_conditions:
      - "primary_result == 'PASS'"
```

### Parallel Pattern
```yaml
parallel_branches:
  - branch_name: "your_agent_branch"
    agents:
      - type: "your_agent_type"
        depends_on: ["intake"]
```

## Configuration Validation

The system automatically validates your configuration when loading. Common errors:

- **Missing persona file**: Create the `.md` file in `agent-persona/`
- **Invalid MCP server**: Check the server name against available servers
- **Missing required fields**: Ensure all required fields are present
- **Invalid field types**: Check the field type documentation above

## Testing New Agents

Run these tests to verify your agent works:

```bash
# Test configuration loading
python -c "from loan_processing.providers.openai.agents import AgentRegistry; print(AgentRegistry.list_agent_types())"

# Test agent creation
python -c "from loan_processing.providers.openai.agents import AgentRegistry; agent = AgentRegistry.create_agent('your_agent_type'); print(f'Success: {agent.name}')"

# Test in orchestration
python -c "from loan_processing.orchestration.engine import OrchestrationEngine; engine = OrchestrationEngine(); print('Orchestration engine ready')"
```

## Need Help?

- Review existing agent configurations in `agents.yaml` for examples
- Check existing personas in `agent-persona/` for formatting
- Test configurations incrementally
- Use the `AgentRegistry.reload_configuration()` method to reload changes without restarting

The configuration-driven approach makes it easy to experiment with new agent types and iterate quickly!