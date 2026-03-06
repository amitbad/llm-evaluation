import os
import yaml
import openpyxl
from datetime import datetime
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
COL_RESPONSE     = 7
COL_SCORE        = 8
COL_VERDICT      = 9


def get_meaning(score):
    if score >= 0.90: return "Nearly identical meaning"
    if score >= 0.80: return "Very similar meaning"
    if score >= 0.70: return "Mostly correct, some drift"
    if score >= 0.60: return "Related but missing key points"
    return "Different meaning"


def run():
    print("\nReading results from Excel — no bot calls will be made...")

    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb[TEST_SHEET]

    results = []
    passed = partial = failed = total = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        tc_id        = row[COL_ID - 1]
        summary      = row[COL_SUMMARY - 1]
        prerequisite = row[COL_PREREQUISITE - 1]
        category     = row[COL_CATEGORY - 1]
        prompt       = row[COL_PROMPT - 1]
        expected     = row[COL_EXPECTED - 1]
        response     = row[COL_RESPONSE - 1]
        score        = row[COL_SCORE - 1]
        verdict      = row[COL_VERDICT - 1]

        if not prompt or not expected or not response or score is None:
            print(f"  Skipping {tc_id} — no bot response found. Run test6_semantic_similarity.py first.")
            continue

        total += 1
        meaning = get_meaning(float(score))

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
            "response":     response,
            "score":        score,
            "verdict":      verdict,
            "meaning":      meaning,
        })

    if total == 0:
        print("\nNo results found in Excel. Run test6_semantic_similarity.py first.")
        return

    run_time = datetime.now().strftime("%d %b %Y %H:%M:%S")
    generate(results, passed, partial, failed, total, run_time, REPORT_FILE)

    print(f"\nReport regenerated from {total} existing results.")
    print(f"HTML report saved : {REPORT_FILE}\n")


if __name__ == "__main__":
    run()
