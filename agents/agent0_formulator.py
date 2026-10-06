"""
agents/agent0_formulator.py
Agent 0 — Problem Formulator

Takes a raw word problem and produces a structured mathematical formulation.
Uses DeepSeek-r1:7b for reasoning.
"""

from utils.ollama_client import OllamaClient
from rag.numerical_methods_rag import get_formulation_context

MODEL = "deepseek-r1:7b"

SYSTEM_PROMPT = """You are a mathematical problem formulator specializing in optimization problems.

Your job is to convert a plain-language description into a precise mathematical formulation.

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "problem_type": "unconstrained | constrained | convex | non-convex | linear | nonlinear | mixed-integer | unknown",
  "objective": {
    "type": "minimize | maximize",
    "description": "plain English description of what is being optimized",
    "expression": "mathematical expression if determinable, else 'TBD'"
  },
  "variables": [
    {"name": "x", "description": "what it represents", "domain": "R | R+ | integer | binary | unknown"}
  ],
  "constraints": [
    {"expression": "g(x) <= 0", "description": "plain English meaning", "type": "inequality | equality | bound"}
  ],
  "assumptions": [
    {"assumption": "what was assumed", "reason": "why this assumption was made"}
  ],
  "clarifying_questions": [
    "Any question that would make the problem more precise (leave empty list if none needed)"
  ],
  "confidence": 0.0,
  "confidence_note": "Why confidence is at this level"
}

Confidence scoring guide:
- 0.9+: problem is fully specified, no ambiguity
- 0.7–0.9: minor ambiguities, assumptions made
- 0.5–0.7: significant assumptions, ask clarifying questions
- <0.5: problem is underspecified, flag clearly

Always be explicit about what you assumed and what you are uncertain about.
"""


class ProblemFormulator:
    def __init__(self):
        self.client = OllamaClient(model=MODEL)

    def run(self, raw_problem: str) -> dict:
        context = get_formulation_context()

        user_prompt = f"""
Context (reference material):
{context}

Raw problem description:
\"\"\"{raw_problem}\"\"\"

Formulate this as a mathematical optimization problem. Be explicit about every assumption you make.
Respond ONLY with the JSON object.
"""
        result = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            expect_json=True,
        )
        result["agent"] = "Agent 0 — Problem Formulator"
        return result
