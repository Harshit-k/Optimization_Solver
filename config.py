"""
config.py
Central configuration for the Optimization Co-pilot.

Edit this file to change models, timeouts, or retry limits.
"""

# ── Model assignments ──────────────────────────────────────────────────────────
# Reasoning agents use DeepSeek-r1 for chain-of-thought
REASONING_MODEL = "deepseek-r1:7b"

# Code agent uses Qwen2.5-coder for code generation
CODER_MODEL = "qwen2.5-coder:7b"

# ── Ollama settings ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 300       # seconds per request (increase if your machine is slow)
OLLAMA_TEMPERATURE = 0.2   # low = more deterministic outputs

# ── Agent retry settings ───────────────────────────────────────────────────────
MAX_JSON_RETRIES = 3       # retries if JSON parsing fails
MAX_CODE_RETRIES = 3       # self-correction attempts in Agent 4

# ── Sandbox settings ───────────────────────────────────────────────────────────
SANDBOX_TIMEOUT = 30       # seconds before killing generated code

# ── Output settings ────────────────────────────────────────────────────────────
SESSION_OUTPUT_DIR = "."   # where session JSON files are saved
CODE_OUTPUT_FILE = "output_code.py"
