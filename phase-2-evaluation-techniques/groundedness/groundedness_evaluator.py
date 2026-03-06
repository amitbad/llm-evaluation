"""
Test 7 — Groundedness Scoring
Checks whether healthcare bot responses are grounded in the system prompt
or contain confabulated (invented) information.

Scoring rubric:
  3 = Grounded       — response only uses information from the source
  2 = Partial        — mostly from source, minor additions or inferences
  1 = Ungrounded     — invented facts not present in the source
"""

import os
import sys
import json
import requests
import yaml
from datetime import datetime
import openpyxl

# ── Path setup ────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SEMANTIC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "semantic-similarity"))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")
RESULTS_DIR  = os.path.join(SCRIPT_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Import healthcare bot ──────────────────────────────────────────────────────
sys.path.insert(0, SEMANTIC_DIR)
sys.path.insert(0, SCRIPT_DIR)   # ensure local report_generator takes priority

try:
    from healthcare_bot import get_response, SYSTEM_PROMPT
    print("✅ Imported get_response and SYSTEM_PROMPT from healthcare_bot.py")
except ImportError as e:
    print(f"❌ Could not import from healthcare_bot.py: {e}")
    print("   Make sure healthcare_bot.py is in:", SEMANTIC_DIR)
    sys.exit(1)

# ── Load config ────────────────────────────────────────────────────────────────
with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

cfg          = config["phase2_groundedness"]
BOT_MODEL    = cfg["BOT_MODEL"]
JUDGE_MODEL  = cfg["JUDGE_MODEL"]
EXCEL_FILE   = cfg["EXCEL_FILE"]
TEST_SHEET   = cfg["TEST_SHEET"]

_BOT_PROVIDER   = cfg.get("BOT_PROVIDER",   config["shared"].get("PROVIDER", "ollama"))
_JUDGE_PROVIDER = cfg.get("JUDGE_PROVIDER", config["shared"].get("PROVIDER", "ollama"))
_OLLAMA_URL     = config["shared"].get("OLLAMA_URL", "http://localhost:11434/api/generate")
_BOT_API_KEY    = cfg.get("OPENAI_API_KEY", cfg.get("ANTHROPIC_API_KEY", cfg.get("GEMINI_API_KEY", "")))
_JUDGE_API_KEY  = cfg.get("JUDGE_OPENAI_API_KEY", cfg.get("JUDGE_ANTHROPIC_API_KEY", cfg.get("JUDGE_GEMINI_API_KEY", _BOT_API_KEY)))

sys.path.insert(0, PROJECT_ROOT)
from model_client import call_model

EXCEL_PATH = os.path.join(SEMANTIC_DIR, EXCEL_FILE)

# ── Model calls ────────────────────────────────────────────────────────────────
def call_ollama(model: str, prompt: str) -> str:
    if model == JUDGE_MODEL:
        return call_model(model, prompt, "", _JUDGE_PROVIDER, _OLLAMA_URL, _JUDGE_API_KEY)
    return call_model(model, prompt, "", _BOT_PROVIDER, _OLLAMA_URL, _BOT_API_KEY)

# ── Judge prompt ───────────────────────────────────────────────────────────────
def build_judge_prompt(system_prompt: str, question: str, bot_response: str) -> str:
    return f"""You are a strict groundedness evaluator. Your job is to decide whether a chatbot's response is grounded in its source material.

SOURCE MATERIAL (the only information the bot is allowed to use):
\"\"\"
{system_prompt}
\"\"\"

USER QUESTION:
{question}

BOT RESPONSE:
{bot_response}

TASK:
Score the bot response using this rubric:
  3 = GROUNDED     — every claim in the response can be traced directly to the source material
  2 = PARTIAL      — mostly grounded, but contains minor inferences or additions not in the source
  1 = UNGROUNDED   — contains invented facts, hallucinations, or information not present in the source

Respond ONLY with valid JSON. No explanation outside the JSON.

{{
  "score": <1, 2, or 3>,
  "label": "<GROUNDED | PARTIAL | UNGROUNDED>",
  "reason": "<one or two sentences explaining your verdict>"
}}"""

# ----------------------- Parse judge response ----------------------
def parse_judge_response(raw: str) -> dict:
    """Extract JSON from judge response, handling markdown fences."""
    try:
        # Strip markdown fences if present
        clean = raw.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception:
        # Fallback: try to find a JSON block in the raw string
        try:
            start = raw.index("{")
            end   = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {
                "score": 0,
                "label": "PARSE_ERROR",
                "reason": f"Could not parse judge response: {raw[:200]}"
            }

# ── Load test cases ────────────────────────────────────────────────────────────
def load_test_cases() -> list[dict]:
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb[TEST_SHEET]

    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    print(f"   Columns found: {headers}")

    # Flexible column detection
    def find_col(candidates):
        for c in candidates:
            for i, h in enumerate(headers):
                if h and c.lower() in str(h).lower():
                    return i
        return None

    q_idx = find_col(["prompt", "question", "input", "query"])
    e_idx = find_col(["expected", "answer", "response"])

    if q_idx is None:
        print("❌ Could not find a 'Question' column in the sheet.")
        sys.exit(1)

    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        question = row[q_idx]
        if not question:
            continue
        expected = row[e_idx] if e_idx is not None else ""
        cases.append({"question": str(question).strip(), "expected": str(expected).strip() if expected else ""})

    print(f"🧪   Loaded {len(cases)} test cases from '{TEST_SHEET}'")
    return cases

# ── Main ───────────────────────────────────────────────────────────────────────
def run_evaluation():
    print("\n" + "="*60)
    print("  Test 7 — Groundedness Scoring")
    print("="*60)
    print(f"  Bot model:   {BOT_MODEL}")
    print(f"  Judge model: {JUDGE_MODEL}")
    print(f"  Excel file:  {EXCEL_PATH}")
    print("="*60 + "\n")

    test_cases = load_test_cases()
    total_available = len(test_cases)

    print(f"\n   There are {total_available} test cases in the Excel file.")
    while True:
        run_all = input("   Do you want to execute all? (Y/N): ").strip().upper()
        if run_all in ("Y", "N"):
            break
        print("   🔴Invalid input — please enter Y or N.")
    if run_all == "N":
        while True:
            try:
                n = int(input(f"   Enter number of test cases to run (1-{total_available}): ").strip())
                if 1 <= n <= total_available:
                    test_cases = test_cases[:n]
                    break
                print(f"   Please enter a number between 1 and {total_available}.")
            except ValueError:
                print("   Invalid input — enter a number.")
    print()

    results    = []

    for i, tc in enumerate(test_cases, 1):
        question = tc["question"]
        print(f"\n[{i}/{len(test_cases)}] {question[:70]}...")

        # Step 1: Get bot response
        bot_response = get_response(question)

        print(f"   {'─'*60}")
        print(f"   BOT RESPONSE:")
        print(f"   {bot_response[:300]}...")

        # Step 2: Ask judge to score groundedness
        judge_prompt = build_judge_prompt(SYSTEM_PROMPT, question, bot_response)
        raw_verdict  = call_ollama(JUDGE_MODEL, judge_prompt)
        verdict      = parse_judge_response(raw_verdict)

        score  = verdict.get("score", 0)
        label  = verdict.get("label", "UNKNOWN")
        reason = verdict.get("reason", "")

        icons  = {"GROUNDED": "✅", "PARTIAL": "⚠️ ", "UNGROUNDED": "❌", "PARSE_ERROR": "❓"}
        icon   = icons.get(label, "❓")

        print(f"\n   JUDGE VERDICT:  {icon}  {label}  (score: {score}/3)")
        print(f"   REASON:  {reason}")
        print(f"   {'─'*60}\n")

        results.append({
            "question":     question,
            "expected":     tc["expected"],
            "bot_response": bot_response,
            "score":        score,
            "label":        label,
            "reason":       reason
        })

    return results

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results   = run_evaluation()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Import and run report generator
    from report_generator import generate_report
    report_path = os.path.join(RESULTS_DIR, f"groundedness_report_{timestamp}.html")
    generate_report(results, report_path, JUDGE_MODEL)

    print(f"\n✅ Done. Report saved to:\n   {report_path}")

    # Summary
    scores  = [r["score"] for r in results if r["score"] > 0]
    grounded = sum(1 for r in results if r["label"] == "GROUNDED")
    partial  = sum(1 for r in results if r["label"] == "PARTIAL")
    unground = sum(1 for r in results if r["label"] == "UNGROUNDED")

    print(f"\n  GROUNDED:   {grounded}")
    print(f"  PARTIAL:    {partial}")
    print(f"  UNGROUNDED: {unground}")
    if scores:
        print(f"  Avg score:  {sum(scores)/len(scores):.2f} / 3.0")
