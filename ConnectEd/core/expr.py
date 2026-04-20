#!/usr/bin/env python3
"""
Safe Expression Evaluator for ConnectEd Diagram Parameters

Purpose:
    Allow parameterized expressions in diagrams (e.g. vector ranges, generate loops,
    property values). Equivalent to VHDL generics / Verilog parameters.

    You pass individual expressions (the parts on either side of a colon in a range).

    100% safe: no arbitrary Python execution (no eval, no exec, no imports, no __getattr__ etc.)

Supported operators (chosen for real HDL parameter usage):
    Arithmetic:   + - * / %          (all integer; / is floor division)
    Power:        **                 (optional, with safety limit on exponent)
    Bitwise:      << >> & | ^ ~      (very useful for widths and masks)
    Grouping:     ( )

No function calls, attributes, subscripts, conditionals, strings, or lists.

Example:
    ev = SafeExpressionEvaluator({"WIDTH": 32, "DATA_WIDTH": 16, "LOG2_DEPTH": 10})
    ev.evaluate("WIDTH-1")                    # → 31
    ev.evaluate("2*DATA_WIDTH + 3")           # → 35
    ev.evaluate("(1 << LOG2_DEPTH) - 1")      # → 1023
    ev.evaluate("~0")                         # → -1   (all-ones mask)
"""

import ast
from typing import Any


class SafeExpressionEvaluator:
    """
    Securely evaluates a restricted subset of arithmetic + bitwise expressions
    with variable (parameter) substitution.

    Designed specifically for HDL-style expressions in graphical diagrams.
    """

    def __init__(
        self,
        variables: dict[str, int | float] | None = None,
        *,
        allow_bitwise: bool = True,
        allow_power: bool = True,
        max_power_exponent: int = 64,
        case_sensitive: bool = True,
    ):
        self.variables: dict[str, int | float] = variables or {}
        self.allow_bitwise = allow_bitwise
        self.allow_power = allow_power
        self.max_power_exponent = max_power_exponent
        self.case_sensitive = case_sensitive

    def set_variable(self, name: str, value: int | float) -> None:
        """Add or update a parameter value (triggers re-evaluation elsewhere)."""
        self.variables[name] = value

    def evaluate(self, expr: str) -> int:
        """
        Evaluate the expression string and return an integer.

        Raises ValueError with a clear message on any problem
        (undefined variable, syntax error, unsupported operator, division by zero, etc.).
        """
        if not expr or not expr.strip():
            return 0

        expr = expr.strip()

        try:
            tree = ast.parse(expr, mode="eval")
            result = self._eval_node(tree.body)
            return int(result)
        except Exception as exc:
            raise ValueError(f"Invalid expression '{expr}': {exc}") from exc

    # ------------------------------------------------------------------ #
    # Internal recursive AST walker (whitelisted nodes only)
    # ------------------------------------------------------------------ #
    def _eval_node(self, node: ast.AST) -> int | float:
        # Numeric literals (Python 3.8+)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node.value, str) and node.value.startswith(("0x", "0b", "0o")):
                try:
                    return int(node.value, 0)
                except ValueError:
                    pass
            raise ValueError(f"Only numeric literals allowed (got {type(node.value)})")

        # Variable / parameter name
        if isinstance(node, ast.Name):
            name = node.id if self.case_sensitive else node.id.upper()
            if name in self.variables:
                val = self.variables[name]
                if isinstance(val, (int, float)):
                    return val
                raise ValueError(f"Parameter '{name}' must be numeric")
            raise ValueError(f"Undefined parameter: '{name}'")

        # Binary operators
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = node.op

            if isinstance(op, ast.Add):          return left + right
            if isinstance(op, ast.Sub):          return left - right
            if isinstance(op, ast.Mult):         return left * right
            if isinstance(op, (ast.Div, ast.FloorDiv)):
                if right == 0:
                    raise ValueError("Division by zero")
                return left // right
            if isinstance(op, ast.Mod):
                if right == 0:
                    raise ValueError("Modulo by zero")
                return left % right
            if isinstance(op, ast.Pow):
                if not self.allow_power:
                    raise ValueError("** (power) is disabled")
                if right > self.max_power_exponent:
                    raise ValueError(f"Exponent {right} exceeds safety limit ({self.max_power_exponent})")
                if right < 0:
                    raise ValueError("Negative exponents not supported")
                return left ** right

            if self.allow_bitwise:
                if isinstance(op, ast.LShift):   return left << right
                if isinstance(op, ast.RShift):   return left >> right
                if isinstance(op, ast.BitAnd):   return left & right
                if isinstance(op, ast.BitOr):    return left | right
                if isinstance(op, ast.BitXor):   return left ^ right

            raise ValueError(f"Unsupported binary operator: {type(op).__name__}")

        # Unary operators
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = node.op
            if isinstance(op, ast.UAdd):   return +operand
            if isinstance(op, ast.USub):   return -operand
            if isinstance(op, ast.Invert):
                if not self.allow_bitwise:
                    raise ValueError("~ (bitwise not) is disabled")
                return ~operand
            raise ValueError(f"Unsupported unary operator: {type(op).__name__}")

        raise ValueError(f"Unsupported expression construct: {type(node).__name__}")


# ---------------------------------------------------------------------- #
# One-shot convenience function
# ---------------------------------------------------------------------- #
def evaluate(expr: str, variables: dict[str, int | float] | None = None) -> int:
    """Quick one-line evaluation (creates a fresh evaluator)."""
    return SafeExpressionEvaluator(variables).evaluate(expr)


# ---------------------------------------------------------------------- #
# Self-test
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    params = {"WIDTH": 32, "DATA_WIDTH": 16, "LOG2_DEPTH": 10, "BUS_WIDTH": 64}

    ev = SafeExpressionEvaluator(params)

    tests = [
        ("WIDTH-1", 31),
        ("2*DATA_WIDTH + 3", 35),
        ("(1 << LOG2_DEPTH) - 1", 1023),
        ("BUS_WIDTH / 8", 8),
        ("0xFF & ((1 << WIDTH) - 1)", 255),
        ("~0", -1),
        ("WIDTH ** 2", 1024),
        ("(DATA_WIDTH + 3) / 4", 4),
    ]

    print("Testing SafeExpressionEvaluator...\n")
    all_ok = True
    for expr, expected in tests:
        try:
            result = ev.evaluate(expr)
            ok = result == expected
            status = "✓" if ok else "✗"
            if not ok:
                all_ok = False
            print(f"{status} {expr:28} → {result:6}  (expected {expected})")
        except Exception as e:
            all_ok = False
            print(f"✗ {expr:28} → ERROR: {e}")

    # Error handling tests
    try:
        ev.evaluate("WIDTH + undefined")
    except ValueError:
        print("✓ Undefined variable correctly rejected")

    try:
        ev.evaluate("1 / 0")
    except ValueError:
        print("✓ Division by zero correctly rejected")

    print("\n" + ("All tests passed!" if all_ok else "Some tests failed."))
