"""
tools/scipy_tool.py
Quick feasibility probe using SciPy — used by Agent 2 (Method Selector).

Runs a tiny toy problem that mirrors the structure of the real problem
(constrained vs unconstrained, convex vs unknown) to verify that SciPy
solvers are available and to detect obvious structural issues.
"""

import traceback


def run_feasibility_test(problem_type: str, has_constraints: bool) -> dict:
    """
    Run a small structural feasibility test using scipy.optimize.
    This is NOT solving the real problem — it's checking solver availability
    and demonstrating which methods are applicable.

    Returns a dict with test results and recommendations.
    """
    results = {
        "scipy_available": False,
        "numpy_available": False,
        "unconstrained_solver_ok": False,
        "constrained_solver_ok": False,
        "recommended_scipy_method": None,
        "notes": [],
    }

    # Check numpy
    try:
        import numpy as np
        results["numpy_available"] = True
    except ImportError:
        results["notes"].append("NumPy not installed — required for all numerical methods")
        return results

    # Check scipy
    try:
        import scipy.optimize as opt
        results["scipy_available"] = True
    except ImportError:
        results["notes"].append("SciPy not installed — run: pip install scipy")
        return results

    # Test unconstrained solver on f(x) = (x-2)^2
    try:
        import numpy as np
        res = opt.minimize(
            fun=lambda x: (x[0] - 2.0) ** 2,
            x0=[0.0],
            method="L-BFGS-B",
        )
        if res.success:
            results["unconstrained_solver_ok"] = True
            results["notes"].append("Unconstrained solver (L-BFGS-B) works correctly")
        else:
            results["notes"].append(f"Unconstrained test converged with warning: {res.message}")
    except Exception as e:
        results["notes"].append(f"Unconstrained solver test failed: {e}")

    # Test constrained solver on f(x) = (x-1)^2, subject to x >= 0.5
    try:
        import numpy as np
        res = opt.minimize(
            fun=lambda x: (x[0] - 1.0) ** 2,
            x0=[0.0],
            method="SLSQP",
            constraints=[{"type": "ineq", "fun": lambda x: x[0] - 0.5}],
        )
        if res.success:
            results["constrained_solver_ok"] = True
            results["notes"].append("Constrained solver (SLSQP) works correctly")
        else:
            results["notes"].append(f"Constrained test warning: {res.message}")
    except Exception as e:
        results["notes"].append(f"Constrained solver test failed: {e}")

    # Recommend method based on problem type
    results["recommended_scipy_method"] = _recommend_method(problem_type, has_constraints)

    return results


def _recommend_method(problem_type: str, has_constraints: bool) -> str:
    """Heuristic method recommendation based on problem structure."""
    pt = problem_type.lower()

    if "linear" in pt:
        return "scipy.optimize.linprog" if has_constraints else "scipy.optimize.minimize (method='L-BFGS-B')"
    if "mixed-integer" in pt:
        return "scipy.optimize.milp  (or use PuLP/CVXPY for richer interface)"
    if "convex" in pt and has_constraints:
        return "scipy.optimize.minimize (method='SLSQP')"
    if "convex" in pt:
        return "scipy.optimize.minimize (method='L-BFGS-B')"
    if has_constraints:
        return "scipy.optimize.minimize (method='SLSQP')"
    if "non-convex" in pt or "nonlinear" in pt:
        return "scipy.optimize.differential_evolution  (global) or minimize (method='Nelder-Mead')"

    return "scipy.optimize.minimize (method='L-BFGS-B')  [default safe choice]"
