"""
Tests for the SafeConditionEvaluator.

This module tests the security fix that replaces dangerous eval() usage
with a safe expression evaluator.
"""

import pytest
from loan_processing.agents.shared.utils.safe_evaluator import SafeConditionEvaluator, evaluate_condition


class TestSafeConditionEvaluator:
    """Test the safe condition evaluator functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.context = {
            "credit_score": 720,
            "income": 75000,
            "debt_ratio": 0.25,
            "status": "approved",
            "risk_level": "low",
            "amount": 250000,
            "age": 35,
            "categories": ["prime", "qualified"]
        }
    
    def test_basic_numeric_comparisons(self):
        """Test basic numeric comparison operators."""
        # Greater than
        assert SafeConditionEvaluator.evaluate_condition("credit_score > 650", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("credit_score > 800", self.context)
        
        # Less than
        assert SafeConditionEvaluator.evaluate_condition("debt_ratio < 0.5", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("debt_ratio < 0.2", self.context)
        
        # Greater than or equal
        assert SafeConditionEvaluator.evaluate_condition("credit_score >= 720", self.context)
        assert SafeConditionEvaluator.evaluate_condition("credit_score >= 650", self.context)
        
        # Less than or equal
        assert SafeConditionEvaluator.evaluate_condition("debt_ratio <= 0.25", self.context)
        assert SafeConditionEvaluator.evaluate_condition("debt_ratio <= 0.5", self.context)
    
    def test_equality_comparisons(self):
        """Test equality and inequality operators."""
        # Equality
        assert SafeConditionEvaluator.evaluate_condition("status == 'approved'", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("status == 'denied'", self.context)
        
        # Inequality
        assert SafeConditionEvaluator.evaluate_condition("status != 'denied'", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("status != 'approved'", self.context)
        
        # Numeric equality
        assert SafeConditionEvaluator.evaluate_condition("credit_score == 720", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("credit_score == 650", self.context)
    
    def test_membership_operators(self):
        """Test 'in' and 'not in' operators."""
        # In operator with list
        assert SafeConditionEvaluator.evaluate_condition("risk_level in ['low', 'medium']", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("risk_level in ['high', 'very_high']", self.context)
        
        # Not in operator
        assert SafeConditionEvaluator.evaluate_condition("risk_level not in ['high', 'very_high']", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("risk_level not in ['low', 'medium']", self.context)
    
    def test_compound_conditions(self):
        """Test compound conditions with 'and' and 'or'."""
        # AND conditions
        assert SafeConditionEvaluator.evaluate_condition("credit_score > 650 and income > 50000", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("credit_score > 650 and income > 100000", self.context)
        
        # OR conditions
        assert SafeConditionEvaluator.evaluate_condition("credit_score > 800 or income > 50000", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("credit_score > 800 or income > 100000", self.context)
        
        # Complex compound conditions
        assert SafeConditionEvaluator.evaluate_condition("credit_score >= 720 and debt_ratio <= 0.3 and status == 'approved'", self.context)
    
    def test_convenience_function(self):
        """Test the convenience evaluate_condition function."""
        assert evaluate_condition("credit_score > 650", self.context)
        assert not evaluate_condition("credit_score > 800", self.context)
        assert evaluate_condition("status == 'approved'", self.context)
    
    def test_error_handling(self):
        """Test error handling for invalid conditions."""
        # Invalid field name
        with pytest.raises(ValueError, match="Field 'nonexistent' not found"):
            SafeConditionEvaluator.evaluate_condition("nonexistent > 100", self.context)
        
        # Invalid operator
        with pytest.raises(ValueError, match="Invalid condition format"):
            SafeConditionEvaluator.evaluate_condition("credit_score ** 2", self.context)
        
        # Invalid condition format
        with pytest.raises(ValueError, match="Invalid condition format"):
            SafeConditionEvaluator.evaluate_condition("invalid condition", self.context)
    
    def test_type_conversions(self):
        """Test proper type parsing and conversions."""
        # String values
        assert SafeConditionEvaluator.evaluate_condition("status == 'approved'", self.context)
        
        # Integer values
        assert SafeConditionEvaluator.evaluate_condition("age == 35", self.context)
        
        # Float values
        assert SafeConditionEvaluator.evaluate_condition("debt_ratio == 0.25", self.context)
        
        # List values
        assert SafeConditionEvaluator.evaluate_condition("risk_level in ['low', 'medium', 'high']", self.context)
    
    def test_security_isolation(self):
        """Test that dangerous operations are prevented."""
        # These should all fail safely without executing dangerous code
        
        # Should not allow function calls
        with pytest.raises(ValueError):
            SafeConditionEvaluator.evaluate_condition("__import__('os').system('echo test')", self.context)
        
        # Should not allow attribute access
        with pytest.raises(ValueError):
            SafeConditionEvaluator.evaluate_condition("credit_score.__class__", self.context)
        
        # Should not allow complex expressions
        with pytest.raises(ValueError):
            SafeConditionEvaluator.evaluate_condition("credit_score + income * 2", self.context)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty condition
        assert not SafeConditionEvaluator.evaluate_condition("", self.context)
        assert not SafeConditionEvaluator.evaluate_condition("   ", self.context)
        
        # None condition
        assert not SafeConditionEvaluator.evaluate_condition(None, self.context)
        
        # Empty context
        with pytest.raises(ValueError):
            SafeConditionEvaluator.evaluate_condition("credit_score > 650", {})
    
    def test_real_world_scenarios(self):
        """Test conditions that would be used in actual loan processing."""
        loan_context = {
            "credit_score": 680,
            "income": 85000,
            "employment_years": 3,
            "debt_to_income": 0.35,
            "loan_amount": 300000,
            "down_payment": 60000,
            "property_type": "primary",
            "loan_purpose": "purchase"
        }
        
        # Loan approval conditions
        assert evaluate_condition("credit_score >= 620", loan_context)
        assert evaluate_condition("debt_to_income <= 0.43", loan_context)
        assert evaluate_condition("employment_years >= 2", loan_context)
        assert evaluate_condition("property_type == 'primary'", loan_context)
        
        # Complex approval logic
        approval_condition = "credit_score >= 620 and debt_to_income <= 0.43 and employment_years >= 2"
        assert evaluate_condition(approval_condition, loan_context)
        
        # Loan amount validation
        ltv_ratio = (loan_context["loan_amount"] - loan_context["down_payment"]) / loan_context["loan_amount"]
        loan_context["ltv_ratio"] = ltv_ratio
        assert evaluate_condition("ltv_ratio <= 0.8", loan_context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])