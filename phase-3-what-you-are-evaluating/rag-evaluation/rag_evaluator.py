"""
rag_evaluator.py — RAG Evaluation Script
==========================================
Reads all test cases from rag_test_cases.xlsx.
For each case: retrieves chunks, gets bot answer, scores 3 ways.

Scoring:
  Context Relevance    — LLM judge (mistral): did retriever pull the right chunks?
  Answer Faithfulness  — LLM judge (mistral): is the answer grounded in context?
  Answer Relevance     — keyword matching: does the answer contain expected keywords?

Run:
  python rag_evaluator.py
"""

import os
import sys
import time

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import yaml
import pandas as pd
from pathlib import Path
from model_client import call_model
from rag_bot import get_response

CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")
RESULTS_DIR  = Path(SCRIPT_DIR) / "results"

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

cfg          = config["phase3_rag"]
JUDGE_MODEL    = cfg["JUDGE_MODEL"]
JUDGE_PROVIDER = cfg["JUDGE_PROVIDER"]
EXCEL_FILE     = os.path.join(SCRIPT_DIR, cfg["EXCEL_FILE"])
TEST_SHEET     = cfg["TEST_SHEET"]


# ── Scoring functions ─────────────────────────────────────────────────────────

def score_context_relevance(question, chunks):
    """Ask judge: did the retriever pull chunks relevant to this question?"""
    chunks_text = "\n\n".join(
        f"[Chunk {c['id']} — {c['source']}]\n{c['text']}" for c in chunks
    )
    prompt = f"""You are an evaluation judge. A question was asked and the following chunks were retrieved from a document corpus.

Question: {question}

Retrieved chunks:
{chunks_text}

Task: Judge whether the retrieved chunks contain the information needed to answer this question.

Respond in this exact format:
SCORE: <0.0 or 0.5 or 1.0>
REASON: <one sentence>

Scoring guide:
1.0 — chunks contain the answer clearly
0.5 — chunks are partially relevant but incomplete
0.0 — chunks are irrelevant or missing key information"""

    response = call_model(
        provider=JUDGE_PROVIDER,
        model=JUDGE_MODEL,
        prompt=prompt
    )
    return _parse_judge_response(response)


def score_answer_faithfulness(question, answer, chunks):
    """Ask judge: is the answer grounded in the retrieved chunks?"""
    chunks_text = "\n\n".join(
        f"[Chunk {c['id']} — {c['source']}]\n{c['text']}" for c in chunks
    )
    prompt = f"""You are an evaluation judge. A bot was given context chunks and a question, then produced an answer.

Question: {question}

Context chunks provided to the bot:
{chunks_text}

Bot answer: {answer}

Task: Judge whether the bot's answer is faithful to the provided context — meaning it only uses information present in the chunks and does not invent or add information not found there.

Respond in this exact format:
SCORE: <0.0 or 0.5 or 1.0>
REASON: <one sentence>

Scoring guide:
1.0 — answer is fully grounded in the context, nothing invented
0.5 — answer is mostly grounded but adds minor details not in context
0.0 — answer contains invented information not present in context"""

    response = call_model(
        provider=JUDGE_PROVIDER,
        model=JUDGE_MODEL,
        prompt=prompt
    )
    return _parse_judge_response(response)


def score_answer_relevance(answer, expected_keywords):
    """Keyword match: what proportion of expected keywords appear in the answer?"""
    if not expected_keywords or str(expected_keywords).strip() == "nan":
        return 0.0
    keywords = [k.strip().lower() for k in str(expected_keywords).split(",") if k.strip()]
    if not keywords:
        return 0.0
    answer_lower = answer.lower()
    matched = sum(1 for k in keywords if k in answer_lower)
    return round(matched / len(keywords), 2)


def _parse_judge_response(response):
    """Extract SCORE and REASON from judge response."""
    score = 0.0
    reason = response.strip()
    for line in response.splitlines():
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = float(line.replace("SCORE:", "").strip())
            except ValueError:
                score = 0.0
        if line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()
    return score, reason


# ── Terminal formatting helpers ───────────────────────────────────────────────

W = 68  # terminal width

def header(title):
    print("\n" + "─" * W)
    print(f"  {title}")
    print("─" * W)

def section(title):
    print(f"\n  ┌─ {title}")

def step(label, value=""):
    if value:
        print(f"  │  {'·'} {label:<30} {value}", flush=True)
    else:
        print(f"  │  {'·'} {label}", flush=True)

def result_line(ctx, faith, rel, avg):
    def dot(s):
        if s >= 0.7: return "●"
        if s >= 0.4: return "◑"
        return "○"
    print(f"  │")
    print(f"  │  {'SCORES':>6}   ctx {dot(ctx)} {int(ctx*100):>3}%   "
          f"faith {dot(faith)} {int(faith*100):>3}%   "
          f"rel {dot(rel)} {int(rel*100):>3}%   "
          f"avg {int(avg*100):>3}%")

def case_separator():
    print(f"  └" + "─" * (W - 3))

def summary_table(results, total):
    avg_ctx   = sum(r["context_relevance"]   for r in results) / total
    avg_faith = sum(r["answer_faithfulness"] for r in results) / total
    avg_rel   = sum(r["answer_relevance"]    for r in results) / total
    overall   = (avg_ctx + avg_faith + avg_rel) / 3

    print("\n" + "═" * W)
    print(f"  EVALUATION COMPLETE — {total} cases")
    print("═" * W)
    print(f"  {'Metric':<30} {'Score':>8}   {'Bar'}")
    print(f"  {'─'*30} {'─'*8}   {'─'*20}")

    for label, score in [
        ("Context Relevance",    avg_ctx),
        ("Answer Faithfulness",  avg_faith),
        ("Answer Relevance",     avg_rel),
        ("Overall",              overall),
    ]:
        bar_filled = int(score * 20)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        marker = "◀" if label == "Overall" else " "
        print(f"  {label:<30} {int(score*100):>7}%   {bar} {marker}")

    print("═" * W)


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("\n" + "═" * W)
    print(f"  RAG EVALUATOR — Test 9")
    print("═" * W)
    print(f"  Bot model    : {cfg['BOT_MODEL']} ({cfg['BOT_PROVIDER']})")
    print(f"  Judge model  : {JUDGE_MODEL} ({JUDGE_PROVIDER})")
    print(f"  Excel file   : {cfg['EXCEL_FILE']}")
    print(f"  Sheet        : {TEST_SHEET}")
    print("═" * W)

    # Load test cases
    df = pd.read_excel(EXCEL_FILE, sheet_name=TEST_SHEET)
    total = len(df)
    print(f"\n  Loaded {total} test cases — starting evaluation...\n")

    results = []

    for i, row in df.iterrows():
        tc_id    = str(row["TC_ID"])
        question = str(row["Question"])
        category = str(row["Category"])
        keywords = row.get("Expected Keywords", "")

        section(f"[{i+1}/{total}]  {tc_id}  —  {category}")
        step(f"Q: {question}")
        print(f"  │")

        # Step 1 — bot response
        step("Getting bot response...")
        t_start = time.time()
        bot_result = get_response(question, verbose=False)
        answer = bot_result["answer"]
        chunks = bot_result["retrieved_chunks"]
        latency = round(time.time() - t_start, 2)

        chunk_ids = ", ".join(f"chunk {c['id']}" for c in chunks)
        step("Chunks retrieved", chunk_ids)
        step("Bot response time", f"{latency}s")
        step(f"A: {answer}")
        print(f"  │")

        # Step 2 — context relevance
        step("Scoring context relevance...")
        ctx_score, ctx_reason = score_context_relevance(question, chunks)
        step("Context relevance", f"{int(ctx_score*100)}%  —  {ctx_reason[:45]}")

        # Step 3 — answer faithfulness
        step("Scoring answer faithfulness...")
        faith_score, faith_reason = score_answer_faithfulness(question, answer, chunks)
        step("Answer faithfulness", f"{int(faith_score*100)}%  —  {faith_reason[:45]}")

        # Step 4 — answer relevance
        rel_score = score_answer_relevance(answer, keywords)
        step("Answer relevance (keywords)", f"{int(rel_score*100)}%")

        avg = round((ctx_score + faith_score + rel_score) / 3, 2)
        result_line(ctx_score, faith_score, rel_score, avg)
        case_separator()

        results.append({
            "tc_id":                      tc_id,
            "question":                   question,
            "category":                   category,
            "answer":                     answer,
            "retrieved_chunks":           chunks,
            "latency":                    latency,
            "context_relevance":          ctx_score,
            "context_relevance_reason":   ctx_reason,
            "answer_faithfulness":        faith_score,
            "answer_faithfulness_reason": faith_reason,
            "answer_relevance":           rel_score,
        })

    # Summary
    summary_table(results, total)

    # Generate report
    print(f"\n  Generating HTML report...")
    from report_generator import generate_report
    report_path = generate_report(results, cfg, RESULTS_DIR)
    print(f"  Saved: {report_path}")
    print(f"\n  Done.\n")


if __name__ == "__main__":
    run()
