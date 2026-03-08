"""
test10_ragas_evaluator.py — RAGAS Evaluation Script
====================================================
Reads all test cases from ragas_test_cases.xlsx.
For each case: runs the RAG bot (llama3.1:8b via Ollama),
then scores using RAGAS framework (gpt-4o-mini via OpenAI).

Metrics:
  Context Precision    — RAGAS: were retrieved chunks relevant and ranked well?
  Faithfulness         — RAGAS: are answer claims grounded in context?
  Answer Relevancy     — RAGAS: does the answer address the question? (embedding-based)

Run:
  python test10_ragas_evaluator.py
"""

import os
import sys
import time

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RAG_DIR      = os.path.abspath(os.path.join(PROJECT_ROOT, "phase-3-what-you-are-evaluating", "rag-evaluation"))

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, RAG_DIR)

import yaml
import openpyxl
from pathlib import Path
from rag_bot import get_response

CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
RESULTS_DIR = Path(SCRIPT_DIR) / "results"
EXCEL_FILE  = os.path.join(SCRIPT_DIR, "ragas_test_cases.xlsx")

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

cfg           = config["phase4_ragas"]
BOT_MODEL     = cfg["BOT_MODEL"]
BOT_PROV      = cfg["BOT_PROVIDER"]
RAGAS_MODEL   = cfg.get("RAGAS_LLM_MODEL", "gpt-4o-mini")
RAGAS_API_KEY = cfg.get("RAGAS_OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")


# ── Terminal formatting — matches Test 9 style exactly ────────────────────────

W = 68

def header(title):
    print("\n" + "═" * W)
    print(f"  {title}")
    print("═" * W)

def section(title):
    print(f"\n  ┌─ {title}")

def step(label, value=""):
    if value:
        print(f"  │  · {label:<30} {value}", flush=True)
    else:
        print(f"  │  · {label}", flush=True)

def result_line(cp, faith, ar, avg):
    def dot(s):
        if s >= 0.7: return "●"
        if s >= 0.4: return "◑"
        return "○"
    print(f"  │")
    print(f"  │  {'SCORES':>6}   ctx {dot(cp)} {int(cp*100):>3}%   "
          f"faith {dot(faith)} {int(faith*100):>3}%   "
          f"rel {dot(ar)} {int(ar*100):>3}%   "
          f"avg {int(avg*100):>3}%")

def case_separator():
    print(f"  └" + "─" * (W - 3))

def summary_table(results, total):
    avg_cp  = sum(r["context_precision"] for r in results) / total
    avg_f   = sum(r["faithfulness"]      for r in results) / total
    avg_ar  = sum(r["answer_relevancy"]  for r in results) / total
    overall = (avg_cp + avg_f + avg_ar) / 3

    print("\n" + "═" * W)
    print(f"  RAGAS EVALUATION COMPLETE — {total} cases")
    print("═" * W)
    print(f"  {'Metric':<30} {'Score':>8}   {'Bar'}")
    print(f"  {'─'*30} {'─'*8}   {'─'*20}")

    for label, score in [
        ("Context Precision",  avg_cp),
        ("Faithfulness",       avg_f),
        ("Answer Relevancy",   avg_ar),
        ("Overall",            overall),
    ]:
        bar_filled = int(score * 20)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        marker = "◀" if label == "Overall" else " "
        print(f"  {label:<30} {int(score*100):>7}%   {bar} {marker}")

    print("═" * W)

    # ── Comparison with Test 9 hand-rolled scores (from CONTEXT.md) ───────────
    test9 = {
        "Context Relevance / Precision": 0.84,
        "Faithfulness":                  1.00,
        "Answer Relevance / Relevancy":  0.66,
        "Overall":                       0.83,
    }
    ragas = {
        "Context Relevance / Precision": avg_cp,
        "Faithfulness":                  avg_f,
        "Answer Relevance / Relevancy":  avg_ar,
        "Overall":                       overall,
    }

    print(f"\n  VS TEST 9  (hand-rolled Mistral judge + keyword matching)")
    print(f"  {'─'*60}")
    print(f"  {'Metric':<34} {'Test 9':>7}   {'RAGAS':>7}   {'Diff':>6}")
    print(f"  {'─'*34} {'─'*7}   {'─'*7}   {'─'*6}")
    for metric in test9:
        t9   = test9[metric]
        rg   = ragas[metric]
        diff = rg - t9
        sign = "+" if diff >= 0 else ""
        print(f"  {metric:<34} {int(t9*100):>6}%   {int(rg*100):>6}%   {sign}{int(diff*100):>4}%")
    print(f"  {'─'*60}")

    return overall, avg_cp, avg_f, avg_ar


# ── Load test cases ────────────────────────────────────────────────────────────

def load_test_cases():
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb["Test Cases"]
    headers = [c.value for c in ws[1]]
    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            cases.append(dict(zip(headers, row)))
    return cases


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    header("RAGAS EVALUATOR — Phase 4 / Test 10")
    print(f"  Bot model    : {BOT_MODEL} ({BOT_PROV})")
    print(f"  RAGAS judge  : {RAGAS_MODEL} (openai)")
    print(f"  Excel file   : ragas_test_cases.xlsx")
    print(f"  Sheet        : Test Cases")
    print("═" * W)

    cases = load_test_cases()
    total = len(cases)
    print(f"\n  Loaded {total} test cases — collecting bot responses...\n")

    # ── Phase 1: run RAG bot on all cases ─────────────────────────────────────
    raw_results = []

    for i, case in enumerate(cases, 1):
        tc_id    = case["TC_ID"]
        question = case["Question"]
        category = case["Category"]

        section(f"[{i}/{total}]  {tc_id}  —  {category}")
        step(f"Q: {question}")
        print(f"  │")

        t_start    = time.time()
        bot_result = get_response(question, verbose=False)
        answer     = bot_result["answer"]
        chunks     = bot_result["retrieved_chunks"]
        latency    = round(time.time() - t_start, 2)

        chunk_ids = ", ".join(f"chunk {c['id']}" for c in chunks)
        step("Chunks retrieved", chunk_ids)
        step("Bot response time", f"{latency}s")
        step(f"A: {answer[:75]}...")
        print(f"  │")
        step("Queued for RAGAS scoring")
        case_separator()

        raw_results.append({
            "tc_id":    tc_id,
            "question": question,
            "category": category,
            "answer":   answer,
            "chunks":   chunks,
            "contexts": [c["text"] for c in chunks],
            "latency":  latency,
            "notes":    case.get("Notes", ""),
        })

    # ── Phase 2: RAGAS scoring ─────────────────────────────────────────────────
    print("\n" + "═" * W)
    print(f"  RAGAS SCORING — sending {total} cases to {RAGAS_MODEL}")
    print(f"  This will take 2–4 minutes. Do not interrupt.")
    print("═" * W + "\n")

    from ragas import evaluate, EvaluationDataset, SingleTurnSample
    from ragas.metrics.collections import context_precision, faithfulness, answer_relevancy
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"],
        )
        for r in raw_results
    ]

    # Set API key in environment — most reliable way to pass to langchain and ragas internals
    if RAGAS_API_KEY:
        os.environ["OPENAI_API_KEY"] = RAGAS_API_KEY
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(
            "\n  ✗ OPENAI_API_KEY not found.\n"
            "  Set it in config.yaml as RAGAS_OPENAI_API_KEY, or run:\n"
            "    export OPENAI_API_KEY=sk-..."
        )

    dataset    = EvaluationDataset(samples=samples)
    llm        = ChatOpenAI(model=RAGAS_MODEL)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    t_ragas = time.time()
    ragas_result = evaluate(
        dataset=dataset,
        metrics=[context_precision, faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings,
    )
    ragas_elapsed = round(time.time() - t_ragas, 1)
    print(f"\n  RAGAS scoring complete — {ragas_elapsed}s\n")

    # ── Attach per-case scores ─────────────────────────────────────────────────
    df = ragas_result.to_pandas()

    results = []
    for i, r in enumerate(raw_results):
        cp = round(float(df.iloc[i]["context_precision"]), 3)
        f  = round(float(df.iloc[i]["faithfulness"]),      3)
        ar = round(float(df.iloc[i]["answer_relevancy"]),  3)
        ov = round((cp + f + ar) / 3, 3)
        results.append({**r,
            "context_precision": cp,
            "faithfulness":      f,
            "answer_relevancy":  ar,
            "overall":           ov,
        })

    # ── Per-case score table ───────────────────────────────────────────────────
    print("  PER-CASE SCORES")
    print(f"  {'─'*W}")
    print(f"  {'ID':<6} {'Category':<32} {'CP':>5} {'F':>5} {'AR':>5} {'Avg':>5}")
    print(f"  {'─'*6} {'─'*32} {'─'*5} {'─'*5} {'─'*5} {'─'*5}")
    for r in results:
        cat_short = r["category"][:30]
        print(f"  {r['tc_id']:<6} {cat_short:<32} "
              f"{int(r['context_precision']*100):>4}% "
              f"{int(r['faithfulness']*100):>4}% "
              f"{int(r['answer_relevancy']*100):>4}% "
              f"{int(r['overall']*100):>4}%")
    print(f"  {'─'*W}")

    # ── Summary + Test 9 comparison ────────────────────────────────────────────
    overall, avg_cp, avg_f, avg_ar = summary_table(results, total)

    # ── HTML report ────────────────────────────────────────────────────────────
    print(f"\n  Generating HTML report...")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "total":                 total,
        "avg_context_precision": avg_cp,
        "avg_faithfulness":      avg_f,
        "avg_answer_relevancy":  avg_ar,
        "avg_overall":           overall,
    }

    from report_generator import generate_report
    report_path = generate_report(results, summary, RESULTS_DIR)
    print(f"  Saved: {report_path}")
    print(f"\n  Done.\n")


if __name__ == "__main__":
    run()
