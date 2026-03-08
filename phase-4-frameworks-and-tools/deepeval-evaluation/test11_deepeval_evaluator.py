"""
test11_deepeval_evaluator.py — DeepEval RAG Evaluation
=======================================================
Phase 4 · Test 11

Framework : DeepEval (pytest-style LLM testing framework)
Bot model : llama3.1:8b via Ollama  (same as Test 9 / Test 10)
Judge     : mistral via Ollama      (same as Test 9)
Input     : ragas_test_cases.xlsx   (same 25 cases as Test 9 / Test 10)
Output    : results/deepeval_report.html

Before running:
  deepeval set-ollama --model=mistral --base-url="http://localhost:11434"

Run:
  python test11_deepeval_evaluator.py
  (from phase-4-frameworks-and-tools/deepeval-evaluation/)

What this does differently from Test 9:
  - DeepEval scores each metric and produces a PASS/FAIL verdict
  - You set a threshold (METRIC_THRESHOLD below) — anything below fails
  - This is the "unit test for LLMs" pattern: red/green, not just percentages
  - Reasons are returned by the judge explaining each verdict
"""

import os
import sys
import time
import subprocess
import yaml
import openpyxl

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RAG_DIR      = os.path.abspath(os.path.join(
    PROJECT_ROOT, "phase-3-what-you-are-evaluating", "rag-evaluation"
))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")
RESULTS_DIR  = os.path.join(SCRIPT_DIR, "results")

# model_client lives at project root
sys.path.insert(0, PROJECT_ROOT)
from model_client import call_model

# rag_bot.py is a local copy in this folder
sys.path.insert(0, SCRIPT_DIR)
from rag_bot import get_response

# report_generator lives alongside this script
sys.path.insert(0, SCRIPT_DIR)
from report_generator import generate_report

# ── Config ────────────────────────────────────────────────────────────────────
with open(CONFIG_FILE, "r") as f:
    full_config = yaml.safe_load(f)

shared = full_config.get("shared", {})
cfg    = full_config.get("phase4_deepeval", {})

BOT_MODEL    = cfg.get("BOT_MODEL",    "llama3.1:8b")
BOT_PROVIDER = cfg.get("BOT_PROVIDER", "ollama")
OLLAMA_URL   = shared.get("OLLAMA_URL", "http://localhost:11434/api/generate")
EXCEL_FILE   = cfg.get("EXCEL_FILE",   "deepeval_test_cases.xlsx")
TEST_SHEET   = cfg.get("TEST_SHEET",   "Test Cases")
TOP_K        = cfg.get("TOP_K_CHUNKS", 3)

# Judge model — read from config if present, else default to mistral
# DeepEval uses the model registered via `deepeval set-ollama` CLI command.
# The JUDGE_MODEL here is used only for the HTML report label.
JUDGE_MODEL  = "mistral"

# Pass/fail threshold — cases scoring below this on any metric are marked FAIL
METRIC_THRESHOLD = cfg.get("METRIC_THRESHOLD", 0.5)

EXCEL_PATH = os.path.join(SCRIPT_DIR, EXCEL_FILE)

# ── DeepEval imports ──────────────────────────────────────────────────────────
try:
    from deepeval.models          import OllamaModel
    from deepeval.metrics         import (
        ContextualRelevancyMetric,
        FaithfulnessMetric,
        AnswerRelevancyMetric,
    )
    from deepeval.test_case       import LLMTestCase
except ImportError as e:
    print(f"\nERROR: DeepEval import failed — {e}")
    print("Run: pip install deepeval")
    sys.exit(1)

# ── Load test cases from Excel ────────────────────────────────────────────────
def load_test_cases(path: str, sheet: str) -> list[dict]:
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        r = dict(zip(headers, row))
        cases.append(r)
    return cases


# ── Ollama RAM management ─────────────────────────────────────────────────────
def restart_ollama(wait=20):
    """Kill and restart Ollama between cases to free RAM and prevent TimeoutErrors."""
    print("  ↻ Restarting Ollama to free RAM...")
    subprocess.run(["pkill", "-f", "ollama serve"], capture_output=True)
    subprocess.run(["pkill", "-f", "ollama runner"], capture_output=True)
    time.sleep(4)
    subprocess.Popen(["ollama", "serve"],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    time.sleep(wait)
    print(f"  ↻ Ollama ready (waited {wait}s)\n")


# ── Interactive run control ───────────────────────────────────────────────────
def ask_run_config() -> tuple[int, int]:
    """Ask user how many cases to run and from where. Returns (start, max)."""
    print("\n  Run options:")
    print("  [R] Run all cases")
    print("  [L] Limited run — choose start and count")
    print()
    while True:
        choice = input("  Your choice (R/L): ").strip().upper()
        if choice == "R":
            return 1, 0
        elif choice == "L":
            while True:
                try:
                    start = int(input("  Start from case number: ").strip())
                    count = int(input("  How many cases to run:  ").strip())
                    if start < 1 or count < 1:
                        print("  Both values must be 1 or greater. Try again.")
                        continue
                    return start, count
                except ValueError:
                    print("  Please enter a valid number.")
        else:
            print("  Please enter R or L.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Test 11 — DeepEval RAG Evaluation")
    print(f"  Bot   : {BOT_MODEL} ({BOT_PROVIDER})")
    print(f"  Judge : {JUDGE_MODEL} (Ollama — set via deepeval set-ollama)")
    print(f"  Cases : {EXCEL_FILE} / {TEST_SHEET}")
    print(f"  Threshold : {METRIC_THRESHOLD}")
    print(f"{'='*60}")

    START_FROM_CASE, MAX_CASES = ask_run_config()
    print(f"\n  From case : {START_FROM_CASE}  |  Max cases : {'all' if MAX_CASES == 0 else MAX_CASES}")
    print(f"{'='*60}\n")

    # ── Set up OllamaModel for DeepEval judge ─────────────────────────────────
    judge = OllamaModel(
        model=JUDGE_MODEL,
        base_url="http://localhost:11434",
        temperature=0,
        timeout=600,
    )

    # Warm up mistral before the loop — first call after bot inference is slowest
    # This forces mistral to load into RAM once so scoring calls don't cold-start
    print("  Warming up judge model...")
    try:
        import requests
        requests.post("http://localhost:11434/api/generate",
                      json={"model": JUDGE_MODEL, "prompt": "Say ok.", "stream": False},
                      timeout=120)
        print("  Judge ready.\n")
    except Exception as e:
        print(f"  Warm-up failed (non-fatal): {e}\n")

    # ── Instantiate metrics ───────────────────────────────────────────────────
    # threshold=METRIC_THRESHOLD means score < threshold → FAIL
    # include_reason=True makes the judge explain its verdict
    ctx_metric   = ContextualRelevancyMetric(threshold=METRIC_THRESHOLD, model=judge, include_reason=True, async_mode=False)
    faith_metric  = FaithfulnessMetric(      threshold=METRIC_THRESHOLD, model=judge, include_reason=True, async_mode=False)
    rel_metric    = AnswerRelevancyMetric(   threshold=METRIC_THRESHOLD, model=judge, include_reason=True, async_mode=False)

    # ── Load test cases ───────────────────────────────────────────────────────
    print(f"Loading test cases from: {EXCEL_PATH}")
    cases = load_test_cases(EXCEL_PATH, TEST_SHEET)
    print(f"Loaded {len(cases)} cases.\n")

    results = []

    cases_run = 0
    for i, tc in enumerate(cases, 1):
        tc_id    = tc.get("TC_ID", f"TC{i:02d}")
        question = tc.get("Question", "").strip()
        category = tc.get("Category", "Unknown")

        if i < START_FROM_CASE:
            print(f"[{i:02d}/{len(cases)}] Skipping (START_FROM_CASE={START_FROM_CASE})")
            continue

        print(f"[{i:02d}/{len(cases)}] {tc_id} — {question[:70]}")

        # ── Phase 1: Run RAG bot ──────────────────────────────────────────────
        try:
            bot_result = get_response(question)
            answer = bot_result["answer"]
            retrieved_chunks = bot_result["retrieved_chunks"]
        except Exception as e:
            print(f"  ERROR running bot: {e}")
            answer = f"ERROR: {e}"
            retrieved_chunks = []

        # Build retrieval_context list for DeepEval (list of strings)
        chunk_texts = [c.get("text", "") for c in retrieved_chunks if c.get("text")]

        print(f"  Bot answer : {answer[:80]}{'...' if len(answer) > 80 else ''}")
        print(f"  Chunks     : {len(chunk_texts)} retrieved")

        # Let RAM settle after bot inference before handing off to judge
        time.sleep(5)

        # ── Phase 2: Build DeepEval test case ─────────────────────────────────
        # LLMTestCase is the core DeepEval object.
        # input           = the question asked
        # actual_output   = what the bot said
        # retrieval_context = the chunks the RAG bot used (list of strings)
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=chunk_texts if chunk_texts else ["No context retrieved."],
        )

        # ── Phase 3: Score each metric ────────────────────────────────────────
        # Each .measure() call sends the test case to the judge (mistral via Ollama)
        # and returns a score + reason + pass/fail verdict.

        # Refusal detection — if the bot said it doesn't have the information,
        # DeepEval metrics hang trying to decompose a null answer into claims.
        # These are correct bot behaviours — record as N/A, not as failures.
        REFUSAL_PHRASES = [
            "not available", "don't have", "do not have", "cannot find",
            "no information", "not found", "outside the scope", "not able to",
            "i'm sorry", "i am sorry", "unable to", "not in the",
            "not covered", "not provided", "cannot answer",
        ]
        is_refusal = any(p in answer.lower() for p in REFUSAL_PHRASES)

        if is_refusal:
            print(f"  ⊘ Refusal detected — skipping DeepEval metrics (N/A)\n")
            results.append({
                "tc_id":    tc_id,
                "question": question,
                "category": category,
                "answer":   answer,
                "retrieved_chunks": [
                    {"id": c.get("id", "?"), "score": c.get("score", 0), "source": c.get("source", "")}
                    for c in retrieved_chunks
                ],
                "context_relevance":          None,
                "answer_faithfulness":        None,
                "answer_relevance":           None,
                "context_relevance_reason":   "Refusal — not scored",
                "answer_faithfulness_reason": "Refusal — not scored",
                "answer_relevance_reason":    "Refusal — not scored",
                "overall_pass":               None,
                "is_refusal":                 True,
            })
            cases_run += 1
            if MAX_CASES and cases_run >= MAX_CASES:
                break
            continue

        def safe_measure(metric, tc_obj, label):
            """Run a metric, return (score, reason, passed). Catch errors gracefully."""
            try:
                metric.measure(tc_obj)
                return metric.score, getattr(metric, "reason", ""), metric.is_successful()
            except Exception as e:
                print(f"    WARNING: {label} metric failed — {e}")
                return 0.0, f"Metric error: {e}", False

        print(f"  Scoring context relevance...")
        ctx_score,   ctx_reason,   ctx_pass   = safe_measure(ctx_metric,   test_case, "ContextualRelevancy")

        print(f"  Scoring faithfulness...")
        faith_score, faith_reason, faith_pass = safe_measure(faith_metric,  test_case, "Faithfulness")

        print(f"  Scoring answer relevance...")
        rel_score,   rel_reason,   rel_pass   = safe_measure(rel_metric,    test_case, "AnswerRelevancy")

        avg = (ctx_score + faith_score + rel_score) / 3
        overall_pass = ctx_pass and faith_pass and rel_pass

        status = "✓ PASS" if overall_pass else "✗ FAIL"
        print(f"  → ctx={ctx_score:.2f}({'P' if ctx_pass else 'F'})  "
              f"faith={faith_score:.2f}({'P' if faith_pass else 'F'})  "
              f"rel={rel_score:.2f}({'P' if rel_pass else 'F'})  "
              f"avg={avg:.2f}  {status}\n")

        results.append({
            "tc_id":    tc_id,
            "question": question,
            "category": category,
            "answer":   answer,
            "retrieved_chunks": [
                {"id": c.get("id", "?"), "score": c.get("score", 0), "source": c.get("source", "")}
                for c in retrieved_chunks
            ],
            "context_relevance":           ctx_score,
            "answer_faithfulness":         faith_score,
            "answer_relevance":            rel_score,
            "context_relevance_reason":    ctx_reason,
            "answer_faithfulness_reason":  faith_reason,
            "answer_relevance_reason":     rel_reason,
            "ctx_pass":   ctx_pass,
            "faith_pass": faith_pass,
            "rel_pass":   rel_pass,
            "overall_pass": overall_pass,
            "is_refusal": False,
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    total        = len(results)
    scored       = [r for r in results if not r.get("is_refusal")]
    refusal_count = total - len(scored)
    ctx_avg    = sum(r["context_relevance"]   for r in scored) / len(scored) if scored else 0
    faith_avg  = sum(r["answer_faithfulness"] for r in scored) / len(scored) if scored else 0
    rel_avg    = sum(r["answer_relevance"]    for r in scored) / len(scored) if scored else 0
    overall    = (ctx_avg + faith_avg + rel_avg) / 3
    pass_count = sum(1 for r in scored if r["overall_pass"])

    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Cases run      : {total}")
    print(f"  Scored         : {len(scored)}  (metrics applied)")
    print(f"  Refusals       : {refusal_count}  (N/A — correct bot behaviour, not scored)")
    print(f"  Overall PASS   : {pass_count}/{len(scored)} ({pass_count/len(scored)*100:.0f}% of scored)" if scored else "  Overall PASS   : 0/0")
    print(f"  Context Rel.   : {ctx_avg*100:.0f}%")
    print(f"  Faithfulness   : {faith_avg*100:.0f}%")
    print(f"  Answer Rel.    : {rel_avg*100:.0f}%")
    print(f"  Overall avg    : {overall*100:.0f}%")
    print(f"{'='*60}\n")

    # ── Generate HTML report ──────────────────────────────────────────────────
    from pathlib import Path
    report_config = {
        "BOT_MODEL":   BOT_MODEL,
        "JUDGE_MODEL": JUDGE_MODEL,
        "THRESHOLD":   METRIC_THRESHOLD,
    }
    report_path = generate_report(results, report_config, Path(RESULTS_DIR))
    print(f"Report saved to: {report_path}\n")


if __name__ == "__main__":
    main()
