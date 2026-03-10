import os
import sys
import time

import ollama
import yaml

# ── ANSI colour helpers ──────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
PURPLE = "\033[35m"
WHITE  = "\033[97m"
ORANGE = "\033[38;5;214m"

def c(color, text):
    return f"{color}{text}{RESET}"

def header(text):
    print(c(CYAN, "=" * 64))
    print(c(BOLD + WHITE, f"  {text}"))
    print(c(CYAN, "=" * 64))

def subheader(text):
    print()
    print(c(YELLOW, "-" * 64))
    print(c(BOLD + YELLOW, f"  {text}"))
    print(c(YELLOW, "-" * 64))

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml")
with open(_CONFIG_FILE, "r", encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

models = _cfg.get("phase1", {}).get("MODELS", ["llama3.1:8b"])

def query_model(model, prompt):
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    end_time = time.time()
    return response['message']['content'], end_time - start_time

if __name__ == "__main__":
    print()
    header("Phase 1 — Test 1 · Basic Model Test")
    print(f"""
  {c(BOLD, 'What this script does:')}
  Sends a single joke prompt to every model listed in {c(CYAN, 'config.yaml → phase1.MODELS')}.
  Prints each model's response and how long it took.
  {c(DIM, 'No scoring. No pass/fail. Just: does it respond, and how fast?')}

  {c(BOLD, 'Dependencies:')}
  {c(GREEN, '✔')} {c(DIM, 'No prior test needed — this is the first script to run.')}
  {c(GREEN, '✔')} Ollama must be running locally  {c(DIM, '(ollama serve)')}
  {c(GREEN, '✔')} Models must be pulled           {c(DIM, '(ollama pull <model>)')}

  {c(BOLD, 'Models to query:')} {c(YELLOW, str(models))}
  {c(BOLD, 'Prompt         :')} \"Hello, can you tell me a short joke?\"
""")

    prompt = "Hello, can you tell me a short joke?"
    total = len(models)
    for i, model in enumerate(models, 1):
        subheader(f"[{i}/{total}] Querying {model} ...")
        print(f"  {c(DIM, 'Sending prompt — waiting for response...')}")
        sys.stdout.flush()
        try:
            output, duration = query_model(model, prompt)
            print(f"  {c(DIM, 'Response :')}\n")
            print(f"    {output}")
            print()
            print(f"  {c(DIM, 'Time     :')} {c(GREEN, f'{duration:.2f}s')}")
        except Exception as e:
            print(f"  {c(RED, f'Error: {e}')}")

    print()
    print(c(CYAN, "=" * 64))
    print(c(BOLD + PURPLE, "  DONE"))
    print(c(CYAN, "=" * 64))
    print(f"""
  {c(BOLD, 'What to notice:')}
  Did all models respond? Which was fastest? Did any give the same joke?
  Style differences (emoji, preamble, follow-up question) are worth noting.

  {c(BOLD, 'Next step:')}
  Run {c(CYAN, 'test2_full_evaluations.py')} — same structure but 3 use cases,
  3 runs each, results saved to JSON for scoring.
""")
    print(c(DIM, "  ─" * 32))
    print(f"  {c(BOLD, '📖 Full analysis:')} {c(CYAN, 'docs/test1.html')}  (open docs/index.html)")
    print()
