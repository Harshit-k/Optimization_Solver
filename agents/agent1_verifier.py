"""
agents/agent1_verifier.py
Agent 1 — Mathematical Verifier

Checks the formulation for mathematical and logical soundness.
Uses SymPy for symbolic verification where possible.
Uses DeepSeek-r1:7b for reasoning.
"""

import json
from utils.ollama_client import OllamaClient
from tools.sympy_tool import check_expression_validity, check_constraint_consistency
from rag.numerical_methods_rag import get_verification_context

MODEL = "deepseek-r1:7b"

SYSTEM_PROMPT = """You are a rigorous mathematical verifier specializing in optimization problems.

Your job is to critically examine a mathematical formulation and identify:
- Logical inconsistencies
- Undefined or ill-posed expressions
- Constraint conflicts
- Dimensionality issues
- Assumptions that may not hold

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "verdict": "sound | unsound | uncertain",
  "issues": [
    {
      "type": "error | warning | note",
      "location": "which part of the formulation (e.g. constraint 1, objective)",
      "description": "what the issue is",
      "suggestion": "how to fix or address it"
    }
  ],
  "uncertainties": [
    {
      "aspect": "what aspect is uncertain",
      "reason": "why you are uncertain",
      "impact": "high | medium | low"
    }
  ],
  "sympy_checks": [],
  "overall_assessment": "brief summary of the mathematical soundness",
  "confidence": 0.0,
  "confidence_note": "why confidence is at this level"
}

Be conservative — it is better to flag a potential issue than to miss one.
Always separate what you KNOW from what you ASSUMED.
"""


class MathVerifier:
    def __init__(self):
        self.client = OllamaClient(model=MODEL)

    def run(self, formulation: dict) -> dict:
        # Run SymPy checks on any expressions we can parse
        sympy_results = self._run_sympy_checks(formulation)

        context = get_verification_context()
        formulation_str = json.dumps(formulation, indent=2)

        user_prompt = f"""
Context (reference material):
{context}

Mathematical formulation to verify:
{formulation_str}

SymPy symbolic check results:
{json.dumps(sympy_results, indent=2)}

Verify this formulation for mathematical and logical soundness.
Check: consistency of constraints, well-definedness of objective, 
domain validity of variables, and any logical conflicts.
Respond ONLY with the JSON object.
"""
        result = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            expect_json=True,
        )
        result["sympy_checks"] = sympy_results
        result["agent"] = "Agent 1 — Math Verifier"
        return result

    def _run_sympy_checks(self, formulation: dict) -> list:
        checks = []

        # Try to check objective expression
        obj = formulation.get("objective", {})
        expr = obj.get("expression", "TBD")
        if expr and expr != "TBD":
            valid, note = check_expression_validity(expr)
            checks.append({
                "target": "objective expression",
                "expression": expr,
                "valid": valid,
                "note": note,
            })

        # Try to check constraint expressions
        for i, constraint in enumerate(formulation.get("constraints", [])):
            expr = constraint.get("expression", "")
            if expr:
                valid, note = check_expression_validity(expr)
                checks.append({
                    "target": f"constraint {i+1}",
                    "expression": expr,
                    "valid": valid,
                    "note": note,
                })

        return checks
