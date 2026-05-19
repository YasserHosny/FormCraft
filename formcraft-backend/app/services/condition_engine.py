"""ConditionEngine: evaluates element visibility, required status, and computed values."""

import ast
import operator as op
from typing import Any


ALLOWED_OPERATORS = {
    "equals",
    "not_equals",
    "contains",
    "greater_than",
    "less_than",
    "is_empty",
    "is_not_empty",
}

_SAFE_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.USub,
    ast.UAdd,
)

_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}

_UNARY_OPS = {
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


class ConditionEngine:
    def evaluate_condition(self, condition_obj: dict | None, form_data: dict[str, Any]) -> bool:
        if not condition_obj:
            return True

        conditions = condition_obj.get("conditions", [])
        if not conditions:
            return True

        results = [self._evaluate_single(c, form_data) for c in conditions]
        return all(results)

    def evaluate_visibility(
        self, elements: list[dict], form_data: dict[str, Any]
    ) -> set[str]:
        visible_keys: set[str] = set()
        for elem in elements:
            condition = elem.get("visible_when")
            if self.evaluate_condition(condition, form_data):
                visible_keys.add(elem["key"])
        return visible_keys

    def evaluate_required(
        self,
        elements: list[dict],
        form_data: dict[str, Any],
        visible_keys: set[str],
    ) -> set[str]:
        required_keys: set[str] = set()
        for elem in elements:
            key = elem["key"]
            if key not in visible_keys:
                continue
            if elem.get("required"):
                required_keys.add(key)
            elif elem.get("required_when"):
                if self.evaluate_condition(elem["required_when"], form_data):
                    required_keys.add(key)
        return required_keys

    def strip_hidden_values(
        self, form_data: dict[str, Any], visible_keys: set[str]
    ) -> dict[str, Any]:
        return {k: v for k, v in form_data.items() if k in visible_keys}

    def parse_expression(self, expr_string: str) -> ast.Expression:
        tree = ast.parse(expr_string, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, _SAFE_AST_NODES):
                raise ValueError(f"Unsupported syntax: {type(node).__name__}")
        return tree

    def evaluate_expression(
        self, expr_string: str, values: dict[str, float]
    ) -> float:
        tree = self.parse_expression(expr_string)
        return self._eval_node(tree.body, values)

    def get_expression_references(self, expr_string: str) -> set[str]:
        tree = self.parse_expression(expr_string)
        refs: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                refs.add(node.id)
        return refs

    def _evaluate_single(self, condition: dict, form_data: dict[str, Any]) -> bool:
        field = condition.get("field", "")
        oper = condition.get("operator", "")
        expected = condition.get("value")
        actual = form_data.get(field)

        if oper == "is_empty":
            return actual is None or actual == ""
        if oper == "is_not_empty":
            return actual is not None and actual != ""
        if oper == "equals":
            return str(actual) == str(expected) if actual is not None else expected is None
        if oper == "not_equals":
            return str(actual) != str(expected) if actual is not None else expected is not None
        if oper == "contains":
            return str(expected).lower() in str(actual).lower() if actual else False
        if oper == "greater_than":
            return self._to_number(actual) > self._to_number(expected)
        if oper == "less_than":
            return self._to_number(actual) < self._to_number(expected)
        return False

    def _to_number(self, val: Any) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def _eval_node(self, node: ast.AST, values: dict[str, float]) -> float:
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return values.get(node.id, 0.0)
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, values)
            right = self._eval_node(node.right, values)
            func = _BIN_OPS.get(type(node.op))
            if func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            if isinstance(node.op, ast.Div) and right == 0:
                return 0.0
            return func(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, values)
            func = _UNARY_OPS.get(type(node.op))
            if func is None:
                raise ValueError(f"Unsupported unary: {type(node.op).__name__}")
            return func(operand)
        raise ValueError(f"Unsupported node: {type(node).__name__}")
