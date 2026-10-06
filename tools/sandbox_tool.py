"""
tools/sandbox_tool.py
Safe Python code execution sandbox — used by Agent 4 (Code Generator).

Runs generated code in a subprocess with a timeout.
Captures stdout, stderr, and return code.
Does NOT use eval() or exec() in the main process.
"""

import subprocess
import sys
import tempfile
import os


TIMEOUT_SECONDS = 30  # generous for optimization runs


def run_in_sandbox(code: str) -> dict:
    """
    Write code to a temp file and run it in a subprocess.

    Returns:
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "error": str,      # human-readable error summary
            "returncode": int,
        }
    """
    # Write to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        success = proc.returncode == 0

        # Build a clean error summary
        error = ""
        if not success:
            # Extract the last few lines of stderr (most relevant)
            lines = stderr.splitlines()
            relevant = lines[-10:] if len(lines) > 10 else lines
            error = "\n".join(relevant)

        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "error": error,
            "returncode": proc.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": f"Code execution timed out after {TIMEOUT_SECONDS} seconds",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": f"Sandbox error: {e}",
            "returncode": -1,
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
