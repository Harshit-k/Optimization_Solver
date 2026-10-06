"""
Optimization Co-pilot — Main Entry Point
Run: python main.py
"""

import sys
from utils.console import Console
from utils.session import Session
from agents.agent0_formulator import ProblemFormulator
from agents.agent1_verifier import MathVerifier
from agents.agent2_method_selector import MethodSelector
from agents.agent3_pseudocode import PseudocodeGenerator
from agents.agent4_coder import CodeGenerator

console = Console()


def run_pipeline():
    console.banner()
    session = Session()

    # ── Step 0: Get raw problem from user ──────────────────────────────────
    console.section("STEP 0 — Describe Your Problem")
    raw_problem = console.prompt_user(
        "Describe your optimization problem in plain words\n(e.g. 'Minimize cost of production given resource constraints')"
    )
    session.set("raw_problem", raw_problem)

    # ── Agent 0: Problem Formulator ────────────────────────────────────────
    console.section("AGENT 0 — Problem Formulator")
    console.thinking("Formulating your problem mathematically...")
    agent0 = ProblemFormulator()
    formulation = agent0.run(raw_problem)
    session.set("formulation", formulation)
    console.show_output("Mathematical Formulation", formulation)

    if not console.human_checkpoint("Accept this formulation?"):
        edited = console.prompt_user("Paste your corrected formulation (as plain text, will be used as-is)")
        formulation["human_override"] = edited
        session.set("formulation", formulation)

    # ── Agent 1: Math Verifier ─────────────────────────────────────────────
    console.section("AGENT 1 — Math Verifier")
    console.thinking("Verifying mathematical soundness...")
    agent1 = MathVerifier()
    verification = agent1.run(formulation)
    session.set("verification", verification)
    console.show_output("Verification Result", verification)

    if not console.human_checkpoint("Proceed with this formulation?"):
        edited = console.prompt_user("Describe what to change / your correction")
        formulation["human_correction"] = edited
        session.set("formulation", formulation)
        console.info("Noted. Proceeding with your correction.")

    # ── Agent 2: Numerical Method Selector ────────────────────────────────
    console.section("AGENT 2 — Numerical Method Selector")
    console.thinking("Evaluating numerical methods...")
    agent2 = MethodSelector()
    method_selection = agent2.run(formulation, verification)
    session.set("method_selection", method_selection)
    console.show_output("Method Selection", method_selection)

    if not console.human_checkpoint("Accept the recommended method?"):
        override = console.prompt_user("Which method would you prefer? (or describe your preference)")
        method_selection["human_override"] = override
        session.set("method_selection", method_selection)

    # ── Agent 3: Pseudocode Generator ─────────────────────────────────────
    console.section("AGENT 3 — Pseudocode Generator")
    console.thinking("Generating structured pseudocode...")
    agent3 = PseudocodeGenerator()
    pseudocode = agent3.run(formulation, method_selection)
    session.set("pseudocode", pseudocode)
    console.show_output("Structured Pseudocode", pseudocode)

    if not console.human_checkpoint("Accept this pseudocode?"):
        edited = console.prompt_user("Paste your corrected pseudocode")
        pseudocode["human_override"] = edited
        session.set("pseudocode", pseudocode)

    # ── Agent 4: Code Generator ────────────────────────────────────────────
    console.section("AGENT 4 — Code Generator & Verifier")
    console.thinking("Generating Python code and verifying it runs...")
    agent4 = CodeGenerator()
    code_result = agent4.run(pseudocode, formulation)
    session.set("code_result", code_result)
    console.show_output("Generated Code", code_result)

    # ── Save session ───────────────────────────────────────────────────────
    output_path = session.save()
    console.section("COMPLETE")
    console.info(f"Full session saved to: {output_path}")
    console.info("The generated code is in the 'code' field of the session JSON.")
    console.info("You can also find it saved as 'output_code.py' in your working directory.")

    # Save code separately for convenience
    code_text = code_result.get("code", "# No code generated")
    with open("output_code.py", "w") as f:
        f.write(code_text)
    console.success("output_code.py written.")


if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n\n[Interrupted by user]")
        sys.exit(0)
