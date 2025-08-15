"""
Shared output format generation utilities.

This module provides utilities for generating structured output instructions
from configuration specifications that can be used across different agent providers.
"""

from __future__ import annotations

from typing import Dict, Any


class OutputFormatGenerator:
    """Generates structured output instructions from configuration."""
    
    @classmethod
    def generate_output_instructions(cls, output_format: Dict[str, Any]) -> str:
        """Generate JSON output instructions from format specification."""
        field_descriptions = []
        
        for field_name, field_spec in output_format.items():
            # Build field description based on type and constraints
            description_parts = [f'    "{field_name}": ']
            
            field_type = field_spec.get("type", "string")
            
            if field_type == "enum":
                values = "|".join(field_spec.get("values", []))
                description_parts.append(f'"{values}"')
            elif field_type == "integer":
                if "range" in field_spec:
                    min_val, max_val = field_spec["range"]
                    description_parts.append(f"integer {min_val}-{max_val}")
                else:
                    description_parts.append("integer")
            elif field_type == "float":
                if "range" in field_spec:
                    min_val, max_val = field_spec["range"]
                    description_parts.append(f"float {min_val}-{max_val}")
                else:
                    description_parts.append("float")
            elif field_type == "decimal":
                description_parts.append("decimal amount")
            elif field_type == "array":
                item_type = field_spec.get("item_type", "string")
                description_parts.append(f"[list of {item_type}s]")
            elif field_type == "object":
                description_parts.append("{{object}}")
            elif field_type == "boolean":
                description_parts.append("true|false")
            else:
                description_parts.append("string value")
            
            # Add comment with description if available
            if "description" in field_spec:
                description_parts.append(f",  // {field_spec['description']}")
            
            field_descriptions.append("".join(description_parts))
        
        return "\n".join(field_descriptions)
    
    @classmethod
    def add_structured_output_instructions(
        cls, 
        base_instructions: str, 
        output_format: Dict[str, Any]
    ) -> str:
        """Add structured output requirements to agent instructions."""
        
        if not output_format:
            return base_instructions
        
        # Generate field specifications from configuration
        field_specs = cls.generate_output_instructions(output_format)
        
        structured_output = f"""

## Structured Output Requirements

When you complete your assessment, provide your results in valid JSON format with these fields:

```json
{{
{field_specs}
}}
```

CRITICAL: Your output must be valid JSON that can be parsed by the orchestration system.
Focus on your core responsibilities as defined in your persona above.
Use secure applicant_id (from application additional_data) for all MCP tool calls, never use SSN.
"""
        
        return base_instructions + structured_output


__all__ = ["OutputFormatGenerator"]