"""
Safe expression evaluator for condition checking.

This module provides secure alternatives to eval() for evaluating simple
conditional expressions without the risk of code injection.
"""

from __future__ import annotations

import operator
import re
from typing import Any


class SafeConditionEvaluator:
    """Safe evaluator for simple conditional expressions."""

    # Allowed operators mapping
    OPERATORS = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        'in': lambda a, b: a in b,
        'not in': lambda a, b: a not in b,
    }

    @classmethod
    def evaluate_condition(cls, condition: str, context: dict[str, Any]) -> bool:
        """
        Safely evaluate a condition against a context.

        Supports conditions like:
        - "credit_score > 650"
        - "status == 'approved'"
        - "risk_level in ['low', 'medium']"
        - "amount >= 1000 and amount <= 50000"

        Args:
            condition: The condition string to evaluate
            context: Dictionary of field names to values

        Returns:
            Boolean result of the condition evaluation

        Raises:
            ValueError: If condition format is invalid or uses unsupported operators
        """
        if not condition or not isinstance(condition, str):
            return False

        condition = condition.strip()

        # Handle compound conditions (and/or)
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(cls._evaluate_simple_condition(part.strip(), context) for part in parts)
        elif ' or ' in condition:
            parts = condition.split(' or ')
            return any(cls._evaluate_simple_condition(part.strip(), context) for part in parts)
        else:
            return cls._evaluate_simple_condition(condition, context)

    @classmethod
    def _evaluate_simple_condition(cls, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a simple condition without compound operators."""

        # Handle empty conditions
        if not condition or not condition.strip():
            return False

        # Pattern to match: field_name operator value
        # Supports operators: >, <, >=, <=, ==, !=, in, not in
        pattern = r'^(\w+)\s*(>=|<=|==|!=|>|<|in|not\s+in)\s*(.+)$'
        match = re.match(pattern, condition)

        if not match:
            raise ValueError(f"Invalid condition format: {condition}")

        field_name, op, value_str = match.groups()

        # Clean up operator
        op = op.strip()
        if op not in cls.OPERATORS:
            raise ValueError(f"Unsupported operator: {op}")

        # Get field value from context
        if field_name not in context:
            raise ValueError(f"Field '{field_name}' not found in context")

        field_value = context[field_name]

        # Parse the comparison value
        comparison_value = cls._parse_value(value_str.strip())

        # Perform the comparison
        try:
            result = cls.OPERATORS[op](field_value, comparison_value)
            return bool(result)  # Ensure we return bool, not Any
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot compare {field_value} {op} {comparison_value}: {e}") from e

    @classmethod
    def _parse_value(cls, value_str: str) -> Any:
        """Parse a value string into appropriate Python type."""

        value_str = value_str.strip()

        # Handle quoted strings
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]  # Remove quotes

        # Handle lists
        if value_str.startswith('[') and value_str.endswith(']'):
            # Simple list parsing - split by comma and parse each item
            items_str = value_str[1:-1]  # Remove brackets
            if not items_str.strip():
                return []

            items = []
            for item in items_str.split(','):
                items.append(cls._parse_value(item.strip()))
            return items

        # Handle numbers
        try:
            # Try integer first
            if '.' not in value_str:
                return int(value_str)
            else:
                return float(value_str)
        except ValueError:
            pass

        # Handle boolean
        if value_str.lower() == 'true':
            return True
        elif value_str.lower() == 'false':
            return False

        # Handle None
        if value_str.lower() == 'none':
            return None

        # Default to string
        return value_str


def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    """
    Convenience function for safe condition evaluation.

    This is a drop-in replacement for dangerous eval() usage.

    Example:
        >>> evaluate_condition("credit_score > 650", {"credit_score": 720})
        True
        >>> evaluate_condition("status == 'approved'", {"status": "pending"})
        False
    """
    return SafeConditionEvaluator.evaluate_condition(condition, context)


__all__ = ["SafeConditionEvaluator", "evaluate_condition"]
