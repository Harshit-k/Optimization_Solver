# Optimization Co-pilot — v0.1 Prototype

An AI-assisted workflow for solving optimization problems.  
**You stay in control at every step — the AI reasons, you decide.**

---

## What it does

Runs a 5-agent pipeline, pausing for your approval after each step:

```
Your word problem
      ↓
Agent 0 — Problem Formulator      (DeepSeek-r1:7b)
      ↓  [you approve]
Agent 1 — Math Verifier           (DeepSeek-r1:7b + SymPy)
      ↓  [you approve]
Agent 2 — Numerical Method Selector (DeepSeek-r1:7b + SciPy probe)
      ↓  [you approve]
Agent 3 — Pseudocode Generator    (DeepSeek-r1:7b)
      ↓  [you approve]
Agent 4 — Code Generator          (Qwen2.5-coder:7b + sandbox)
      ↓
output_code.py  +  session_<timestamp>.json
```

Each agent outputs a **confidence score** and flags explicitly what it assumed or was uncertain about.

---

## Requirements

### Software
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running

### Models (pull these before running)
```bash
ollama pull deepseek-r1:7b
ollama pull qwen2.5-coder:7b
```

### Python packages
```bash
pip install -r requirements.txt
```

---

## Quick Start

1. **Start Ollama** (in a separate terminal or as a background service):
   ```bash
   ollama serve
   ```

2. **Run the co-pilot**:
   ```bash
   python main.py
   ```

3. **Describe your problem** when prompted — plain English is fine:
   ```
   Minimize the total cost of transporting goods from 3 warehouses to 5 stores,
   given supply limits at each warehouse and demand requirements at each store.
   ```

4. **Review and approve** each agent's output. At every checkpoint:
   - Press `y` + Enter to accept and continue
   - Press `n` + Enter to provide a correction or override

5. **Collect your outputs**:
   - `output_code.py` — the generated Python solver
   - `session_<timestamp>.json` — full pipeline trace (all agent outputs)

---

## Project Structure

```
optim_copilot/
├── main.py                         # Entry point — runs the full pipeline
├── config.py                       # Model names, timeouts, settings
├── requirements.txt
│
├── agents/
│   ├── agent0_formulator.py        # Word problem → math formulation
│   ├── agent1_verifier.py          # Check mathematical soundness
│   ├── agent2_method_selector.py   # Choose numerical method
│   ├── agent3_pseudocode.py        # Generate structured pseudocode
│   └── agent4_coder.py             # Generate + verify Python code
│
├── tools/
│   ├── sympy_tool.py               # Symbolic expression checker (Agent 1)
│   ├── scipy_tool.py               # Feasibility probe (Agent 2)
│   └── sandbox_tool.py             # Safe code execution (Agent 4)
│
├── rag/
│   └── numerical_methods_rag.py    # Curated reference material per agent
│
└── utils/
    ├── ollama_client.py            # Ollama HTTP wrapper + JSON parsing
    ├── console.py                  # CLI display + human checkpoints
    └── session.py                  # Saves pipeline state to JSON
```

---

## Configuration

Edit `config.py` to change models or behaviour:

```python
REASONING_MODEL = "deepseek-r1:7b"   # used by Agents 0–3
CODER_MODEL     = "qwen2.5-coder:7b" # used by Agent 4
OLLAMA_TIMEOUT  = 120                 # seconds — increase if slow
MAX_CODE_RETRIES = 3                  # self-correction attempts
```

---

## Example Problems to Try

**Unconstrained:**
```
Find the values of x and y that minimize x squared plus y squared minus 4x minus 6y
```

**Constrained (resource allocation):**
```
A factory produces two products A and B. Product A gives profit of 5 per unit,
B gives 4 per unit. Each unit of A needs 2 hours of machine time and 1 hour of
labour. Each unit of B needs 1 hour machine time and 2 hours labour. Available:
100 machine hours and 80 labour hours. Maximize total profit.
```

**Non-convex (engineering):**
```
Minimize the weight of a hollow cylindrical pressure vessel given constraints
on internal pressure, material yield strength, and minimum wall thickness.
Variables are radius and wall thickness.
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to Ollama` | Run `ollama serve` in another terminal |
| Model not found | Run `ollama pull deepseek-r1:7b` and `ollama pull qwen2.5-coder:7b` |
| JSON parse errors | Normal occasionally — the agent will retry automatically |
| Code execution timeout | Increase `SANDBOX_TIMEOUT` in `config.py` |
| Very slow responses | This is normal for 7B models on CPU — GPU speeds it up significantly |

---

## How to Extend

- **Add RAG from papers**: Replace the static strings in `rag/numerical_methods_rag.py` with a vector store (e.g. ChromaDB + sentence-transformers).
- **Add a Streamlit UI**: Wrap `main.py` logic in Streamlit `st.chat_message` components.
- **Swap models**: Change `REASONING_MODEL` or `CODER_MODEL` in `config.py` — any Ollama model works.
- **Add domain agents**: Insert a new agent between steps, following the same pattern (system prompt → JSON output → human checkpoint).
- **Use cloud models**: Replace `OllamaClient` with an OpenAI-compatible client for Groq, Together.ai, etc.

---

## Design Principles

1. **Human always in the loop** — no agent advances without your approval
2. **No black boxes** — every agent shows its reasoning and confidence
3. **Explicit uncertainty** — agents flag what they assumed, not just what they concluded
4. **Local-first** — runs entirely on your machine, no data leaves
5. **Small agents, focused jobs** — each agent does one thing well
# Optimization_Solver
