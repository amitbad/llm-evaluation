"""
test14_langfuse_evaluator.py — Langfuse Observability for a Banking Chatbot
=============================================================================
Runs banking chatbot test cases and sends every interaction to Langfuse as a
trace. Each trace contains:
  - A parent span for the full test case
  - A child span for the LLM call (model, prompt, response, latency)
  - Scores attached to the trace: keyword_pass (0/1) and response_length

What you will see in the Langfuse dashboard after running this:
  - One trace per test case, named by category
  - Latency per LLM call
  - Keyword pass/fail scores per trace
  - Filterable by category, model, score

Prerequisites:
  1. Langfuse running locally via Docker (see docs/test14.html for setup)
  2. Public + Secret keys from http://localhost:3000 → Settings → API Keys
  3. Keys filled in config.yaml under phase5_langfuse OR as env vars:
       LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY

Run:
  cd phase-5-production-eval/langfuse-observability
  python3 test14_langfuse_evaluator.py
"""

import os
import sys
import time
import json
import yaml
import openpyxl
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..")
sys.path.insert(0, PROJECT_ROOT)

from banking_bot import ask_banking_bot, load_config

# ── Config ──────────────────────────────────────────────────────────────────

def get_config() -> dict:
    cfg = load_config()
    section = cfg.get("phase5_langfuse", {})
    shared = cfg.get("shared", {})
    return {
        "bot_model":      section.get("BOT_MODEL", "llama3.1:8b"),
        "bot_provider":   section.get("BOT_PROVIDER", "ollama"),
        "ollama_url":     shared.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
        "excel_file":     section.get("EXCEL_FILE", "banking_test_cases.xlsx"),
        "test_sheet":     section.get("TEST_SHEET", "Test Cases"),
        "langfuse_host":  section.get("LANGFUSE_HOST", "http://localhost:3000"),
        "public_key":     section.get("LANGFUSE_PUBLIC_KEY", ""),
        "secret_key":     section.get("LANGFUSE_SECRET_KEY", ""),
    }


# ── Langfuse key resolution ──────────────────────────────────────────────────

def resolve_langfuse_keys(cfg: dict) -> tuple:
    public_key = cfg["public_key"] or os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = cfg["secret_key"] or os.environ.get("LANGFUSE_SECRET_KEY", "")
    return public_key, secret_key


# ── Load test cases from Excel ───────────────────────────────────────────────

def load_test_cases(excel_path: str, sheet_name: str) -> list:
    wb = openpyxl.load_workbook(excel_path)
    ws = wb[sheet_name]
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        case = dict(zip(headers, row))
        cases.append(case)
    return cases


# ── Keyword scoring ──────────────────────────────────────────────────────────

def keyword_pass(response: str, must_contain: str, must_not_contain: str) -> int:
    """Returns 1 if all keyword rules pass, 0 if any fail."""
    resp_lower = response.lower()
    if must_contain:
        for kw in [k.strip().lower() for k in must_contain.split(",") if k.strip()]:
            if kw not in resp_lower:
                return 0
    if must_not_contain:
        for kw in [k.strip().lower() for k in must_not_contain.split(",") if k.strip()]:
            if kw in resp_lower:
                return 0
    return 1


# ── Run control ─────────────────────────────────────────────────────────────

def get_run_options(total: int) -> tuple:
    print(f"\n  Total test cases loaded: {total}")
    print("\n  Run options:")
    print("  [R] Run all cases")
    print("  [L] Limited run — choose start and count")
    print()
    choice = input("  Your choice (R/L): ").strip().upper()
    if choice == "L":
        start = int(input("  Start from case number: ").strip()) - 1
        count = int(input("  How many cases to run: ").strip())
        end = min(start + count, total)
    else:
        start = 0
        end = total
    return start, end


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    cfg = get_config()
    public_key, secret_key = resolve_langfuse_keys(cfg)

    if not public_key or not secret_key:
        print("\n  ✗ ERROR: Langfuse API keys not found.")
        print("    Fill in LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in config.yaml")
        print("    under the phase5_langfuse section, or set them as environment variables.")
        print("    Get your keys from: http://localhost:3000 → Settings → API Keys")
        sys.exit(1)

    # Initialise Langfuse client
    try:
        from langfuse import Langfuse
    except ImportError:
        print("\n  ✗ ERROR: langfuse package not installed.")
        print("    Run: pip install 'langfuse>=2,<3'")
        sys.exit(1)

    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=cfg["langfuse_host"],
    )

    print(f"\n  ✓ Langfuse client initialised → {cfg['langfuse_host']}")
    print(f"  ✓ Model: {cfg['bot_model']} via {cfg['bot_provider']}")

    # Load test cases
    excel_path = os.path.join(SCRIPT_DIR, cfg["excel_file"])
    cases = load_test_cases(excel_path, cfg["test_sheet"])

    start_idx, end_idx = get_run_options(len(cases))
    cases_to_run = cases[start_idx:end_idx]

    print(f"\n  Running {len(cases_to_run)} case(s) — traces will appear in Langfuse dashboard.\n")
    print("  " + "─" * 60)

    results = []
    pass_count = 0

    for i, case in enumerate(cases_to_run):
        case_num    = start_idx + i + 1
        question    = str(case.get("Question", "")).strip()
        category    = str(case.get("Category", "general")).strip()
        must_have   = str(case.get("MustContain", "") or "").strip()
        must_not    = str(case.get("MustNotContain", "") or "").strip()
        notes       = str(case.get("Notes", "") or "").strip()

        print(f"\n  [{case_num}] {category}")
        print(f"  Q: {question}")

        # ── Langfuse trace ────────────────────────────────────────────────
        trace = langfuse.trace(
            name=f"banking-bot-tc{case_num:02d}",
            input=question,
            metadata={
                "category": category,
                "model": cfg["bot_model"],
                "case_number": case_num,
                "notes": notes,
            },
            tags=[category, cfg["bot_model"], "test14"],
        )

        # ── LLM span ──────────────────────────────────────────────────────
        span = trace.span(
            name="llm-call",
            input={"question": question, "model": cfg["bot_model"]},
        )

        t_start = time.time()
        response = ask_banking_bot(question, cfg["bot_model"], cfg["ollama_url"])
        latency = round(time.time() - t_start, 2)

        span.end(
            output={"response": response},
            metadata={"latency_seconds": latency},
        )

        # ── Score ─────────────────────────────────────────────────────────
        kw_pass = keyword_pass(response, must_have, must_not)
        pass_count += kw_pass

        trace.score(
            name="keyword_pass",
            value=float(kw_pass),
            comment=f"MustContain='{must_have}' | MustNotContain='{must_not}'",
        )

        trace.score(
            name="response_length_chars",
            value=float(len(response)),
        )

        trace.score(
            name="latency_seconds",
            value=latency,
        )

        # ── Update trace output ───────────────────────────────────────────
        trace.update(
            output=response,
        )

        result_row = {
            "case_number": case_num,
            "category": category,
            "question": question,
            "response": response,
            "latency_seconds": latency,
            "keyword_pass": kw_pass,
        }
        results.append(result_row)

        verdict = "PASS" if kw_pass else "FAIL"
        print(f"  A: {response[:120]}{'...' if len(response) > 120 else ''}")
        print(f"  → {verdict} | latency: {latency}s | chars: {len(response)}")

    # ── Flush Langfuse queue ──────────────────────────────────────────────────
    langfuse.flush()

    # ── Save JSON results ─────────────────────────────────────────────────────
    results_dir = os.path.join(SCRIPT_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(results_dir, f"langfuse_results_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    # ── Summary ───────────────────────────────────────────────────────────────
    total_run = len(cases_to_run)
    print("  " + "═" * 60)
    print("  RESULTS SUMMARY")
    print("  " + "─" * 60)
    print("  Cases run   : " + str(total_run))
    print("  Keyword PASS: " + str(pass_count) + " / " + str(total_run))
    print("  Keyword FAIL: " + str(total_run - pass_count) + " / " + str(total_run))
    avg_latency = sum(r["latency_seconds"] for r in results) / total_run if total_run else 0
    print("  Avg latency : " + str(avg_latency) + "s")
    print("  " + "─" * 60)
    print("  JSON saved  : results/langfuse_results_" + timestamp + ".json")
    print("  " + "─" * 60)
    print("\n  ✓ All traces sent to Langfuse.")
    print("  → Open http://localhost:3000 and navigate to Traces to explore.\n")


if __name__ == "__main__":
    main()
