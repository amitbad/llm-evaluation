# ===================================================================
# Phase 0 — Basic LLM Evaluation
# Sends 3 prompts to a local model and applies deterministic checks.
# Model is read from config.yaml (phase0.MODEL).
# ===================================================================

import os
import re
import time

import ollama
import yaml

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml")
with open(_CONFIG_FILE, "r", encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

MODEL = _cfg.get("phase0", {}).get("MODEL", "llama3.1:8b")

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
    print(c(YELLOW, "-" * 64))
    print(c(BOLD + YELLOW, f"  {text}"))
    print(c(YELLOW, "-" * 64))

def label(key, value):
    print(f"  {c(DIM, key + ':')} {value}")

def limitation(text):
    print(f"  {c(ORANGE, '⚠  Limitation:')} {c(DIM, text)}")

def key_learning(text):
    print(f"  {c(PURPLE, '★  Key learning:')} {text}")

def footer_section(text):
    print(c(CYAN, "=" * 64))
    print(c(BOLD + PURPLE, f"  {text}"))
    print(c(CYAN, "=" * 64))

# ── Custom validator for Task 3 ──────────────────────────────────
def validate_math(output):
    pattern = r"\b(4|four)\b"
    return bool(re.search(pattern, output.lower()))

# ── Test cases ───────────────────────────────────────────────────
test_cases = [
    {"prompt": "Tell a joke about a robot.", "must_contain": "robot"},
    {"prompt": "Summarize: The sky is blue because of Rayleigh scattering.", "must_contain": "scattering"},
    {
        "prompt": "What is 2+2? Answer in one word.",
        "must_contain": "four",
        "validator": validate_math,
    },
]

TASK_DESCRIPTIONS = [
    (
        "Task 1 — Creative Generation (Keyword Check)",
        "Ask the model to tell a joke about a robot.",
        "does the output contain the word 'robot'?",
        "Verifies the model stays on topic and includes the subject it was asked about.",
        "The model could write a terrible joke and still PASS.\n"
        "  Keyword presence does not measure quality — only topic adherence.\n"
        "  This is called a Quality Failure: wrong result, but passes the check.",
    ),
    (
        "Task 2 — Summarisation (Keyword Check)",
        "Ask the model to summarise a sentence about Rayleigh scattering.",
        "does the summary mention 'scattering'?",
        "A good summary must retain the key scientific term.\n"
        "  If 'scattering' is dropped, the most important fact in the input is lost.\n"
        "  This is called Topic Drift: the output shifts away from the source subject.",
        "The model could hallucinate extra facts and still PASS.\n"
        "  It could also paraphrase correctly without using 'scattering' and FAIL\n"
        "  even though the meaning is preserved — the limit of pure keyword checks.",
    ),
    (
        "Task 3 — Arithmetic (Custom Validator)",
        "Ask the model: 'What is 2+2? Answer in one word.'",
        "does the output contain '4' or 'four' (either form accepted)?",
        "Tests whether rigid keyword matching is enough, or whether we need\n"
        "  a custom validator that accepts multiple valid answer formats.",
        "Without the custom validator, '4' would FAIL because we only checked 'four'.\n"
        "  This shows keyword matching must be replaced with smarter logic for answers\n"
        "  that have many valid equivalent forms.",
    ),
]


def run_phase0():
    print()
    header("Phase 0 — Basic LLM Evaluation")
    print(f"\n  {c(DIM, 'Model :')} {c(BOLD + WHITE, MODEL)}")
    print(f"""
  {c(BOLD, 'What we are evaluating:')}
  Can a local LLM pass simple, {c(CYAN, 'deterministic keyword checks')}?

  Each task sends a prompt to the model and applies a pass/fail
  rule to the output — {c(DIM, 'no human scoring, no external judge')}.
  This is the simplest possible evaluation: exact keyword presence.

  {c(YELLOW, '3 tasks:')} creative generation · summarisation · arithmetic
""")

    results = []

    for case, (task_title, task_what, task_check, task_why, task_limit) in zip(test_cases, TASK_DESCRIPTIONS):
        subheader(task_title)
        label("What   ", task_what)
        label("Check  ", task_check)
        label("Why    ", task_why)
        limitation(task_limit)
        print()
        label("Prompt ", c(WHITE, case["prompt"]))
        print(f"  {c(DIM, 'Running...')}")

        start_time = time.time()
        response = ollama.chat(model=MODEL, messages=[
            {"role": "user", "content": case["prompt"]},
        ])
        duration = time.time() - start_time
        output = response["message"]["content"]

        print(f"\n  {c(DIM, 'Output :')} \n{output}\n")

        validator = case.get("validator")
        passed = validator(output) if validator else case["must_contain"].lower() in output.lower()

        status = c(GREEN, "PASS ✅") if passed else c(RED, "FAIL ❌")
        print(f"  {c(DIM, 'Check  :')} must contain {c(YELLOW, repr(case['must_contain']))} → {status}  {c(DIM, f'({duration:.2f}s)')}")
        print()

        results.append({
            "title": task_title,
            "prompt": case["prompt"],
            "output": output,
            "latency": round(duration, 2),
            "passed": passed,
        })

    # ── Summary ──────────────────────────────────────────────────
    footer_section("PHASE 0 SUMMARY")
    for r in results:
        status = c(GREEN, "✅ PASS") if r["passed"] else c(RED, "❌ FAIL")
        lat = f"| {r['latency']:6.2f}s |"
        print(f"  {status} {c(DIM, lat)} {r['title']}")

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    print()
    print(f"  {c(BOLD, 'Result:')} {c(GREEN if passed_count == total else YELLOW, f'{passed_count}/{total} passed')}")
    print()

    # ── Learning takeaway ─────────────────────────────────────────
    footer_section("WHAT THIS EVALUATION DEMONSTRATED")
    print(f"""
  {c(BOLD + CYAN, 'Task 1 — Creative Generation')}
  The model stayed on topic (it said 'robot'). But we could not tell
  if the joke was good or bad. This is a {c(ORANGE, 'Quality Failure gap')} — the
  check passes even when the output quality is poor.

  {c(BOLD + CYAN, 'Task 2 — Summarisation')}
  We checked for the key term 'scattering'. If the model had dropped
  that word and drifted to a generic weather explanation, it would be
  called {c(ORANGE, 'Topic Drift')} — moving away from the source subject.
  The check catches drift, but not hallucination of extra facts.

  {c(BOLD + CYAN, 'Task 3 — Arithmetic')}
  A plain keyword check on 'four' would miss the answer '4'.
  The {c(YELLOW, 'custom validator')} accepts both — showing why rigid matching
  needs to be replaced with smarter logic for real eval pipelines.

  {c(BOLD + PURPLE, 'KEY LEARNING')}
  Keyword checks are {c(GREEN, 'fast, deterministic, and zero-cost')}.
  They catch obvious failures: topic drift, missing terms, wrong format.
  They {c(RED, 'cannot catch')}: hallucination, poor reasoning, misleading phrasing.
  That is why Phase 2 introduces LLM-as-a-Judge, semantic similarity,
  and groundedness scoring.
""")
    print(c(DIM, "  ─" * 32))
    print(f"  {c(BOLD, '📖 Read the full test page for deeper analysis and concept links:')} ")
    print(f"     {c(CYAN, 'docs/test0.html')}  (open docs/index.html in a browser)")
    print()
    print(c(CYAN, "=" * 64))


if __name__ == "__main__":
    run_phase0()
