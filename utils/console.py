"""
utils/console.py
Rich CLI output — sections, agent outputs, human checkpoints.
Uses only stdlib + optional `rich` for pretty printing.
Falls back gracefully if rich is not installed.
"""

import json

try:
    from rich.console import Console as RichConsole
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich import box
    RICH = True
    _rc = RichConsole()
except ImportError:
    RICH = False


class Console:
    def banner(self):
        msg = """
╔══════════════════════════════════════════════════════╗
║         Optimization Co-pilot  v0.1 (prototype)     ║
║         AI-assisted solver — Human always in loop   ║
╚══════════════════════════════════════════════════════╝
"""
        print(msg)

    def section(self, title: str):
        bar = "─" * 54
        print(f"\n{bar}")
        print(f"  {title}")
        print(f"{bar}")

    def thinking(self, msg: str):
        print(f"\n  ⏳ {msg}")

    def info(self, msg: str):
        print(f"  ℹ  {msg}")

    def success(self, msg: str):
        print(f"  ✅ {msg}")

    def warning(self, msg: str):
        print(f"  ⚠️  {msg}")

    def show_output(self, title: str, data: dict):
        """Pretty-print an agent's output dict."""
        print(f"\n  ── {title} ──")
        self._render_dict(data, indent=4)

    def _render_dict(self, data: dict, indent: int = 2):
        pad = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{pad}{key}:")
                self._render_dict(value, indent + 2)
            elif isinstance(value, list):
                print(f"{pad}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        self._render_dict(item, indent + 4)
                        print()
                    else:
                        print(f"{pad}  • {item}")
            elif key == "code" and isinstance(value, str):
                print(f"{pad}{key}:")
                print()
                for line in value.splitlines():
                    print(f"{pad}  {line}")
                print()
            else:
                # Truncate very long strings for display
                display_val = str(value)
                if len(display_val) > 300:
                    display_val = display_val[:300] + "..."
                print(f"{pad}{key}: {display_val}")

    def prompt_user(self, prompt: str) -> str:
        print(f"\n  ❓ {prompt}")
        print("  > ", end="", flush=True)
        return input().strip()

    def human_checkpoint(self, question: str) -> bool:
        """
        Pause and ask the human to approve or reject.
        Returns True if approved, False if rejected/wants to edit.
        """
        print(f"\n  ┌─ HUMAN CHECKPOINT {'─'*34}")
        print(f"  │  {question}")
        print(f"  │  [y] Yes, proceed   [n] No, I want to edit")
        print(f"  └{'─'*52}")
        while True:
            print("  > ", end="", flush=True)
            choice = input().strip().lower()
            if choice in ("y", "yes", ""):
                return True
            elif choice in ("n", "no"):
                return False
            else:
                print("  Please enter y or n")
