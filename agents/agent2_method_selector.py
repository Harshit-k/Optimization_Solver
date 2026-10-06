"""
agents/agent2_method_selector.py
Agent 2 — Numerical Method Selector

Proposes and evaluates candidate numerical methods.
Does quick feasibility tests via SciPy.
Uses DeepSeek-r1:7b for reasoning.
"""

import json
from utils.ollama_client import OllamaClient
from tools.scipy_tool import run_feasibility_test
from rag.numerical_methods_rag import get_method_selection_context

MODEL = "deepseek-r1:7b"

SYSTEM_PROMPT = """You are an expert in numerical optimization methods.

Your job is to evaluate a verified optimization problem and recommend the most suitable numerical method.

You MUST:
1. Propose 2–3 candidate methods
2. Reason about each: convergence, stability, complexity, suitability
3. Recommend ONE method with a clear justification
4. Flag any stability or convergence concerns

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "candidates": [
    {
      "method": "method name",
      "full_name": "full descriptive name",
      "suitable_for": "problem types this fits",
      "convergence": "rate and conditions",
      "stability_notes": "any stability concerns",
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"],
      "scipy_function": "e.g. scipy.optimize.minimize with method='SLSQP'"
    }
  ],
  "recommended": "name of recommended method",
  "recommendation_reasoning": "detailed reasoning for the recommendation",
  "stability_warnings": ["any global stability concerns"],
  "feasibility_test_results": [],
  "hyperparameter_suggestions": {
    "tolerance": "suggested value",
    "max_iterations": "suggested value",
    "other": {}
  },
  "confidence": 0.0,
  "confidence_note": "why confidence is at this level"
}
"""


class MethodSelector:
    def __init__(self):
        self.client = OllamaClient(model=MODEL)

    def run(self, formulation: dict, verification: dict) -> dict:
        # Run a quick feasibility check using SciPy
        feasibility = self._run_feasibility_check(formulation)

        context = get_method_selection_context()
        formulation_str = json.dumps(formulation, indent=2)
        verification_str = json.dumps(verification, indent=2)

        user_prompt = f"""
Context (numerical methods reference):
{context}

Verified formulation:
{formulation_str}

Verification findings:
{verification_str}

SciPy feasibility test results:
{json.dumps(feasibility, indent=2)}

Propose and evaluate 2–3 numerical methods. Recommend the best one with clear reasoning.
Consider: problem type, constraint structure, smoothness, scale, stability.
Respond ONLY with the JSON object.
"""
        result = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            expect_json=True,
        )
        result["feasibility_test_results"] = feasibility
        result["agent"] = "Agent 2 — Method Selector"
        return result

    def _run_feasibility_check(self, formulation: dict) -> dict:
        """Try a simple feasibility probe using SciPy on a toy version of the problem."""
        problem_type = formulation.get("problem_type", "unknown")
        constraints = formulation.get("constraints", [])
        has_constraints = len(constraints) > 0

        return run_feasibility_test(problem_type, has_constraints)
