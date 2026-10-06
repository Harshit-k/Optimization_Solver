"""
rag/numerical_methods_rag.py

Curated reference material injected into each agent's prompt.
This is the "open book" each agent gets during its task.

In a future version this would be retrieved dynamically from a vector store.
For the prototype, it is static and carefully hand-curated per agent role.
"""


def get_formulation_context() -> str:
    return """
=== OPTIMIZATION PROBLEM FORMULATION REFERENCE ===

Standard form of an optimization problem:
  minimize    f(x)
  subject to  g_i(x) <= 0,   i = 1, ..., m   (inequality constraints)
              h_j(x)  = 0,   j = 1, ..., p   (equality constraints)
              x in X                           (domain / bound constraints)

Key problem classifications:
- LINEAR: f and all constraints are linear → use linprog or simplex
- CONVEX: f is convex, feasible set is convex → global minimum guaranteed
- UNCONSTRAINED: no constraints → gradient-based methods apply directly
- NON-CONVEX: multiple local minima possible → need global or multi-start methods
- MIXED-INTEGER: some variables must be integers → MIP solvers required

Variable domains:
- Continuous (R): most common, enables gradient methods
- Non-negative (R+): common in resource allocation
- Integer / Binary: combinatorial problems

Common mistakes in formulation:
- Forgetting to bound variables (unbounded problem)
- Mixing units inconsistently
- Confusing minimization and maximization
- Over-constraining (infeasible) or under-constraining (unbounded) the problem
"""


def get_verification_context() -> str:
    return """
=== MATHEMATICAL VERIFICATION REFERENCE ===

Checklist for a sound optimization problem:
1. FEASIBILITY: Does the feasible set F = {x : g(x)<=0, h(x)=0} contain at least one point?
2. BOUNDEDNESS: Is f bounded below on F? (If not, problem is unbounded.)
3. WELL-DEFINEDNESS: Is f defined for all x in F?
4. CONSTRAINT QUALIFICATION: Are constraints well-behaved at optima (e.g. LICQ, MFCQ)?
5. CONVEXITY: Is f convex and feasible set convex? → global optimum guaranteed.

Common issues to flag:
- Equality constraints that may be infeasible (e.g. h(x)=0 with no solution)
- Objective function undefined at boundary (e.g. log(x) with x=0 possible)
- Conflicting bounds (e.g. x >= 5 and x <= 3)
- Non-smooth objective without appropriate method (e.g. L1 norm needing subgradient methods)
- Ill-conditioned problem (large differences in variable scales)

KKT conditions (necessary conditions for optimality):
  ∇f(x*) + Σλ_i ∇g_i(x*) + Σμ_j ∇h_j(x*) = 0
  λ_i >= 0,  λ_i g_i(x*) = 0  (complementary slackness)
"""


def get_method_selection_context() -> str:
    return """
=== NUMERICAL METHOD SELECTION REFERENCE ===

GRADIENT-BASED METHODS (smooth, differentiable f):
  - Gradient Descent: simple, slow convergence (linear), good for large-scale ML
  - L-BFGS-B: quasi-Newton, fast convergence, handles bounds, scipy default for unconstrained
  - Newton's Method: quadratic convergence, requires Hessian, expensive per step
  - Conjugate Gradient: good for large sparse systems, no Hessian needed

CONSTRAINED METHODS:
  - SLSQP (Sequential Least Squares Programming): handles eq + ineq constraints, gradient-based
  - Interior Point (scipy 'trust-constr'): robust for large constrained problems
  - Augmented Lagrangian: penalty-based, flexible

DERIVATIVE-FREE / GLOBAL METHODS (non-smooth or non-convex):
  - Nelder-Mead: simplex method, no gradients needed, slow, local
  - Differential Evolution: global, stochastic, good for non-convex
  - Basin Hopping: multi-start local search, good for rugged landscapes
  - Simulated Annealing: classic global, slow but general

SPECIAL STRUCTURES:
  - Linear Programming: scipy.optimize.linprog (simplex or interior point)
  - Mixed-Integer: scipy.optimize.milp, or PuLP, CVXPY, or Pyomo
  - Convex QP: CVXPY (recommended), or scipy SLSQP

STABILITY CONSIDERATIONS:
  - Ill-conditioning: scale variables to similar magnitudes
  - Non-convex: run multiple starting points
  - Noisy objective: avoid gradient methods, use derivative-free
  - Large-scale (n > 1000): prefer L-BFGS-B, avoid dense Hessian methods

CONVERGENCE CRITERIA:
  - Gradient norm: ||∇f(x)|| < tol  (for smooth problems)
  - Step size: ||x_k+1 - x_k|| < tol
  - Objective change: |f_k+1 - f_k| < tol
  - Always add max_iterations as a fallback
"""
