"""
Logic evaluator for complex advancement rules.
Supports boolean logic (AND, OR, NOT) and various operators.
"""

from typing import Any, Dict, Union
from .pedagogical_models import AdvancementRule, Condition, RuleOperator

class RuleEvaluator:
    """Evaluates complex advancement rules against a set of facts."""
    
    @staticmethod
    def evaluate(rule: Union[AdvancementRule, Condition], facts: Dict[str, Any]) -> bool:
        """
        Recursively evaluate a rule or condition against the provided facts.
        
        Args:
            rule: The rule or condition to evaluate.
            facts: A dictionary of facts (e.g., student attributes, scores).
            
        Returns:
            True if the rule/condition is met, False otherwise.
        """
        if isinstance(rule, Condition):
            return RuleEvaluator._evaluate_condition(rule, facts)
        
        if isinstance(rule, AdvancementRule):
            results = [RuleEvaluator.evaluate(c, facts) for c in rule.conditions]
            
            if not results:
                return True  # Empty rule is considered met
            
            if rule.logic_operator == RuleOperator.AND:
                return all(results)
            elif rule.logic_operator == RuleOperator.OR:
                return any(results)
            elif rule.logic_operator == RuleOperator.NOT:
                return not any(results)  # Simplified NOT logic
                
        return False

    @staticmethod
    def _evaluate_condition(condition: Condition, facts: Dict[str, Any]) -> bool:
        """Evaluate a single condition."""
        # Handle nested fields (e.g., "attribute.becado")
        field_parts = condition.field.split('.')
        val = facts
        for part in field_parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                val = None
                break
        
        if val is None:
            return False
            
        op = condition.operator
        target = condition.value
        
        if op == "==": return val == target
        if op == "!=": return val != target
        if op == ">":  return val > target
        if op == ">=": return val >= target
        if op == "<":  return val < target
        if op == "<=": return val <= target
        if op == "contains": return target in val
        
        return False
