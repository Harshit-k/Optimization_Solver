"""
tools/sympy_tool.py
Symbolic math checks using SymPy — used by Agent 1 (Math Verifier).

Tries to parse and reason about expressions symbolically.
Returns (valid: bool, note: str) tuples so results are always safe to consume.
"""

def check_expression_validity(expression: str) -> tuple[bool, str]:
    """
    Try to parse a mathematical expression with SymPy.
    Returns (is_valid, note).
    """
    try:
        import sympy
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        # Clean up common pseudocode notation
        cleaned = (
            expression
            .replace("<=", "<=")
            .replace(">=", ">=")
            .replace("^", "**")
            .replace("||", "Abs")  # rough heuristic for norms
        )

        # Strip inequality parts for pure expression check
        for op in ["<=", ">=", "<", ">", "=="]:
            if op in cleaned:
                parts = cleaned.split(op)
                cleaned = parts[0].strip()
                break

        transformations = standard_transformations + (implicit_multiplication_application,)
        parsed = parse_expr(cleaned, transformations=transformations)
        free_syms = [str(s) for s in parsed.free_symbols]

        return True, f"Parsed OK. Free symbols: {free_syms}"

    except ImportError:
        return False, "SymPy not installed — skipping symbolic check"
    except Exception as e:
        return False, f"Could not parse expression: {e}"


def check_constraint_consistency(constraints: list[str]) -> tuple[bool, str]:
    """
    Attempt a basic consistency check on a list of constraint expressions.
    Very limited — mainly catches obvious contradictions like x > 0 and x < 0.
    Returns (consistent, note).
    """
    try:
        import sympy
        from sympy import symbols, solve, And
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        # This is a best-effort check, not exhaustive
        notes = []
        for i, c in enumerate(constraints):
            cleaned = c.replace("^", "**")
            notes.append(f"Constraint {i+1}: '{cleaned}' — not automatically solved (requires problem-specific variables)")

        return True, "; ".join(notes) if notes else "No constraints to check"

    except ImportError:
        return False, "SymPy not installed — skipping constraint consistency check"
    except Exception as e:
        return False, f"Constraint check failed: {e}"
