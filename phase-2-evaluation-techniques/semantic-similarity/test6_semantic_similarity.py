import os
import yaml
import openpyxl
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from healthcare_bot import get_response
from report_generator import generate

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

EXCEL_FILE  = os.path.join(SCRIPT_DIR, config["phase2_semantic_similarity"]["EXCEL_FILE"])
TEST_SHEET  = config["phase2_semantic_similarity"]["TEST_SHEET"]
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
REPORT_FILE = os.path.join(RESULTS_DIR, "semantic_similarity_report.html")

os.makedirs(RESULTS_DIR, exist_ok=True)

COL_ID           = 1
COL_SUMMARY      = 2
COL_PREREQUISITE = 3
COL_CATEGORY     = 4
COL_PROMPT       = 5
COL_EXPECTED     = 6


def get_verdict_and_meaning(score):
    if score >= 0.90: return "Pass",    "Nearly identical meaning"
    if score >= 0.80: return "Pass",    "Very similar meaning"
    if score >= 0.70: return "Partial", "Mostly correct, some drift"
    if score >= 0.60: return "Partial", "Related but missing key points"
    return "Fail", "Different meaning"


def run():
    print("\n" + "="*55)
    print("*** SEMANTIC SIMILARITY EVALUATION — HEALTHCARE BOT ***")
    print("="*55)
    print("Loading sentence transformer model (all-MiniLM-L6-v2)...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb[TEST_SHEET]

    total = ws.max_row - 1
    passed = partial = failed = 0
    results = []

    print(f"Found {total} test cases in '{TEST_SHEET}'\n")
    print("="*55)

    for row in ws.iter_rows(min_row=2, values_only=True):
        tc_id        = row[COL_ID - 1]
        summary      = row[COL_SUMMARY - 1]
        prerequisite = row[COL_PREREQUISITE - 1]
        category     = row[COL_CATEGORY - 1]
        prompt       = row[COL_PROMPT - 1]
        expected     = row[COL_EXPECTED - 1]

        if not prompt or not expected:
            continue

        print(f"\nSending prompt to bot...")
        print(f"[{tc_id}] - {summary}")
        print(f"   Prompt   : {prompt}")

        bot_response = get_response(prompt)

        emb_response = model.encode(bot_response, convert_to_tensor=True)
        emb_expected = model.encode(expected,     convert_to_tensor=True)
        score        = float(util.cos_sim(emb_response, emb_expected)[0][0])
        verdict, meaning = get_verdict_and_meaning(score)

        if verdict == "Pass":      passed  += 1
        elif verdict == "Partial": partial += 1
        else:                      failed  += 1

        results.append({
            "id":           tc_id,
            "summary":      summary,
            "prerequisite": prerequisite,
            "category":     category,
            "prompt":       prompt,
            "expected":     expected,
            "response":     bot_response,
            "score":        round(score, 4),
            "verdict":      verdict,
            "meaning":      meaning,
        })

        print(f"   Score    : {score:.4f}  →  Status: {verdict}  ({meaning})")
        print("="*55)

    run_time = datetime.now().strftime("%d %b %Y %H:%M:%S")
    generate(results, passed, partial, failed, total, run_time, REPORT_FILE)

    print(f"\nTotal test cases   : {total}")
    print(f"Pass  (>= 0.80)    : {passed}  ({100*passed//total}%)")
    print(f"Partial (0.60-0.79): {partial}  ({100*partial//total}%)")
    print(f"Fail  (< 0.60)     : {failed}  ({100*failed//total}%)")
    print(f"\nHTML report saved  : {REPORT_FILE}")
    print("="*55 + "\n")


if __name__ == "__main__":
    run()
