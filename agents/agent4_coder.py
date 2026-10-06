"""
agents/agent4_coder.py
Agent 4 — Code Generator & Verifier

Converts pseudocode into runnable Python, executes it in a sandbox,
and self-corrects on errors (max MAX_RETRIES attempts).
Uses Qwen2.5-coder:7b.
"""

import json
from utils.ollama_client import OllamaClient
from tools.sandbox_tool import run_in_sandbox

MODEL = "qwen2.5-coder:7b"
MAX_RETRIES = 3

SYSTEM_PROMPT = """You are an expert Python programmer specializing in numerical optimization.

Your job is to convert structured pseudocode into clean, runnable Python code.

Rules:
- Use numpy, scipy.optimize as primary libraries
- Add clear comments explaining each step
- Include a __main__ block with a simple example/test
- Handle errors gracefully
- Print results clearly

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "code": "the complete Python code as a string",
  "dependencies": ["list of pip packages needed"],
  "explanation": "brief explanation of the implementation",
  "example_usage": "how to run and what to expect",
  "confidence": 0.0,
  "confidence_note": "why confidence is at this level"
}

The code must be complete and runnable as-is.
"""

CORRECTION_SYSTEM_PROMPT = """You are an expert Python debugger specializing in numerical optimization.

You generated code that has an error. Fix it.

You MUST respond with ONLY a valid JSON object — no preamble, no explanation outside the JSON.

Output schema:
{
  "code": "the corrected complete Python code as a string",
  "fix_description": "what was wrong and what you changed",
  "dependencies": ["list of pip packages needed"],
  "confidence": 0.0,
  "confidence_note": "why confidence is at this level"
}
"""


class CodeGenerator:
    def __init__(self):
        self.client = OllamaClient(model=MODEL, timeout=180)

    def run(self, pseudocode: dict, formulation: dict) -> dict:
        pseudocode_str = json.dumps(pseudocode, indent=2)
        formulation_str = json.dumps(formulation, indent=2)

        user_prompt = f"""
Original problem formulation:
{formulation_str}

Structured pseudocode to implement:
{pseudocode_str}

Generate complete, runnable Python code implementing this optimization.
Include a simple test case in the __main__ block.
Respond ONLY with the JSON object.
"""
        result = self.client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            expect_json=True,
        )

        # Sandbox execution + self-correction loop
        code = result.get("code", "")
        execution_history = []

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"  🔧 Sandbox execution attempt {attempt}/{MAX_RETRIES}...")
            exec_result = run_in_sandbox(code)
            execution_history.append({
                "attempt": attempt,
                "success": exec_result["success"],
                "output": exec_result.get("stdout", ""),
                "error": exec_result.get("error", ""),
            })

            if exec_result["success"]:
                print(f"  ✅ Code ran successfully on attempt {attempt}.")
                result["code"] = code
                result["execution_status"] = "success"
                result["execution_output"] = exec_result.get("stdout", "")
                result["execution_history"] = execution_history
                result["agent"] = "Agent 4 — Code Generator"
                return result

            # Self-correction
            print(f"  ⚠️  Error on attempt {attempt}: {exec_result.get('error', '')[:100]}")
            if attempt < MAX_RETRIES:
                print(f"  🔄 Attempting self-correction...")
                code = self._self_correct(code, exec_result["error"], pseudocode_str)

        # All retries exhausted
        print(f"  ❌ Code could not be fixed in {MAX_RETRIES} attempts. Returning last version.")
        result["code"] = code
        result["execution_status"] = "failed"
        result["execution_history"] = execution_history
        result["agent"] = "Agent 4 — Code Generator"
        return result

    def _self_correct(self, code: str, error: str, pseudocode_str: str) -> str:
        user_prompt = f"""
The following Python code raised an error:

```python
{code}
```

Error:
{error}

Original pseudocode (for reference):
{pseudocode_str}

Fix the code. Respond ONLY with the JSON object.
"""
        try:
            correction = self.client.chat(
                system_prompt=CORRECTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                expect_json=True,
            )
            return correction.get("code", code)
        except Exception as e:
            print(f"  Self-correction failed: {e}")
            return code
