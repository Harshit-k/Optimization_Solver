"""
agents/agent3_pseudocode.py
Agent 3 — Pseudocode Generator

Converts the chosen numerical method into structured pseudocode
following a defined schema. This pseudocode is the contract
between the math layer and the code layer.
Uses DeepSeek-r1:7b.
"""

import json
from utils.ollama_client import OllamaClient

MODEL = "deepseek-r1:7b"

SYSTEM_PROMPT = """You are an algorithm designer who writes precise, structured pseudocode for numerical optimization.

Your pseudocode must follow a strict schema so it can be reliably converted to Python code.

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "problem_type": "unconstrained | constrained | convex | non-convex | linear | nonlinear",
  "method": "chosen method name",
  "variables": {
    "decision": "description of decision variable (e.g. x in R^n)",
    "objective": "f(x) description",
    "parameters": ["list of hyperparameters like learning_rate, tolerance"]
  },
  "initialization": [
    "step 1: ...",
    "step 2: ..."
  ],
  "algorithm_steps": [
    {
      "step": 1,
      "description": "plain English",
      "operation": "mathematical or computational operation",
      "notes": "any implementation notes"
    }
  ],
  "stopping_condition": {
    "primary": "e.g. ||gradient|| < tolerance",
    "secondary": "e.g. max_iterations exceeded",
    "tolerance": "1e-6",
    "max_iterations": 1000
  },
  "output": ["what the algorithm returns"],
  "solver_hint": {
    "scipy_method": "e.g. SLSQP",
    "requires_gradient": true,
    "requires_hessian": false,
    "handles_constraints": true
  },
  "implementation_notes": ["important notes for the coder"],
  "confidence": 0.0,
  "confidence_note": "why confidence is at this level"
}

Be precise. Every step must be unambiguous enough to implement directly.
"""


class PseudocodeGenerator:
    def __init__(self):
        self.client = OllamaClient(model=MODEL)

    def run(self, formulation: dict, method_selection: dict) -> dict:
        formulation_str = json.dumps(formulation, indent=2)
        method_str = json.dumps(method_selection, indent=2)

        user_prompt = f"""
Optimization problem formulation:
{formulation_str}

Selected numerical method:
{method_str}

Generate structured pseudocode for implementing this optimization using the recommended method.
Every step must be precise enough to implement directly in Python.
Include initialization, the main loop, stopping conditions, and outputs.
Respond ONLY with the JSON object.
"""
        result = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            expect_json=True,
        )
        result["agent"] = "Agent 3 — Pseudocode Generator"
        return result
