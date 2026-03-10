import os
import json
import time
from pathlib import Path
import openpyxl
import yaml
from agent import run_agent
from report_generator import generate_report


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
RESULTS_DIR = Path(SCRIPT_DIR) / "results"

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    full_config = yaml.safe_load(f)

shared = full_config.get("shared", {})
cfg = full_config.get("phase5_agent_evaluation", {})

BOT_MODEL = cfg.get("BOT_MODEL", "qwen3.5:9b")
BOT_PROVIDER = cfg.get("BOT_PROVIDER", "ollama")
OLLAMA_URL = shared["OLLAMA_URL"]
EXCEL_FILE = cfg.get("EXCEL_FILE", "agent_test_cases.xlsx")
TEST_SHEET = cfg.get("TEST_SHEET", "Test Cases")
DEFAULT_MAX_STEPS = cfg.get("MAX_STEPS", 3)
EXCEL_PATH = os.path.join(SCRIPT_DIR, EXCEL_FILE)


def load_test_cases(path: str, sheet: str) -> list[dict]:
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        cases.append(dict(zip(headers, row)))
    return cases


def ask_run_config(total_cases: int) -> tuple[int, int]:
    print(f"\n  Loaded {total_cases} test cases.")
    print("  Run options:")
    print("  [R] Run all cases")
    print("  [L] Limited run — choose start and count")
    print()
    while True:
        choice = input("  Your choice (R/L): ").strip().upper()
        if choice == "R":
            return 1, 0
        if choice == "L":
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
        print("  Please enter R or L.")


def parse_expected_sequence(raw_value) -> list[str]:
    raw = str(raw_value or "").strip()
    if not raw or raw.lower() == "none":
        return []
    return [part.strip() for part in raw.split(">") if part.strip()]


def find_first_tool_step(trace: list[dict], tool_name: str) -> dict | None:
    for step in trace:
        if step.get("action") == "tool" and step.get("tool_name") == tool_name:
            return step
    return None


def normalize_hint_words(raw_hints: str) -> list[str]:
    if not raw_hints.strip():
        return []
    parts = raw_hints.replace(",", " ").split()
    return [part.strip().lower() for part in parts if part.strip()]


def derive_actual_final_action(trace: list[dict], stop_reason: str) -> str:
    for step in reversed(trace):
        if step.get("action") == "final":
            return "final"
    if stop_reason == "malformed_action":
        return "malformed_action"
    if stop_reason == "max_steps_reached":
        return "incomplete"
    if stop_reason == "tool_error":
        return "tool_error"
    return "unknown"


def assess_stop_quality(
    expected_sequence: list[str],
    actual_tool_sequence: list[str],
    expected_final_action: str,
    actual_final_action: str,
    stop_reason: str,
    max_steps: int,
    trace: list[dict],
) -> tuple[bool, str]:
    expected_final_action_normalized = expected_final_action.strip().lower() or "final"
    final_action_match = actual_final_action == expected_final_action_normalized
    used_steps = len(trace)

    if stop_reason == "max_steps_reached":
        return False, f"The agent hit the step limit ({max_steps}) before finishing the expected flow."

    if stop_reason == "malformed_action":
        return False, "The agent stopped because its structured action format broke before the case could complete cleanly."

    if expected_sequence != actual_tool_sequence:
        if len(actual_tool_sequence) < len(expected_sequence):
            return False, "The agent stopped too early before completing all expected tool calls."
        return False, "The agent took an unexpected tool path before stopping."

    if not final_action_match:
        return False, f"The observed final action was '{actual_final_action}' instead of the expected '{expected_final_action_normalized}'."

    if used_steps > max_steps:
        return False, "The agent exceeded the allowed step budget before stopping."

    return True, "The agent stopped at an appropriate point after completing the expected flow."


def evaluate_case(tc: dict) -> dict:
    question = str(tc.get("Question", "")).strip()
    max_steps = int(tc.get("Step Limit") or DEFAULT_MAX_STEPS)
    expected_sequence = parse_expected_sequence(tc.get("Expected Tool Path"))
    expected_behavior = str(tc.get("What Good Behavior Looks Like", "")).strip()
    expected_final_action = str(tc.get("Expected End", "final")).strip().lower() or "final"
    expected_account_id = str(tc.get("Account ID (if needed)", "") or "").strip()
    expected_search_query_hints = str(tc.get("Search Hint Words", "") or "").strip()
    should_use_tool = str(tc.get("Tool Needed?", "No")).strip().lower() == "yes"
    should_refuse = str(tc.get("Refusal Expected?", "No")).strip().lower() == "yes"

    agent_result = run_agent(
        question=question,
        model=BOT_MODEL,
        provider=BOT_PROVIDER,
        ollama_url=OLLAMA_URL,
        max_steps=max_steps,
    )

    trace = agent_result.get("trace", [])
    actual_tool_sequence = [
        step.get("tool_name")
        for step in trace
        if step.get("action") == "tool"
    ]
    used_any_tool = bool(actual_tool_sequence)
    tool_match = actual_tool_sequence == expected_sequence
    unnecessary_tool_use = (not should_use_tool) and used_any_tool
    lookup_step = find_first_tool_step(trace, "lookup_account_status")
    docs_step = find_first_tool_step(trace, "search_docs")
    actual_account_id = str((lookup_step or {}).get("arguments", {}).get("account_id", "") or "").strip()
    actual_search_query = str((docs_step or {}).get("arguments", {}).get("query", "") or "").strip()

    account_id_match = True
    if expected_account_id:
        account_id_match = actual_account_id == expected_account_id

    query_hint_words = normalize_hint_words(expected_search_query_hints)
    actual_search_query_lower = actual_search_query.lower()
    search_query_hint_match = True
    if query_hint_words:
        matched = sum(1 for word in query_hint_words if word in actual_search_query_lower)
        search_query_hint_match = matched >= max(1, len(query_hint_words) // 2)

    argument_match = account_id_match and search_query_hint_match
    stop_reason = agent_result.get("stop_reason", "unknown")
    actual_final_action = derive_actual_final_action(trace, stop_reason)
    stop_quality_match, stop_quality_note = assess_stop_quality(
        expected_sequence=expected_sequence,
        actual_tool_sequence=actual_tool_sequence,
        expected_final_action=expected_final_action,
        actual_final_action=actual_final_action,
        stop_reason=stop_reason,
        max_steps=max_steps,
        trace=trace,
    )

    return {
        "tc_id": str(tc.get("TC_ID", "")),
        "category": str(tc.get("Category", "Unknown")),
        "question": question,
        "expected_behavior": expected_behavior,
        "expected_tool_sequence": " > ".join(expected_sequence) if expected_sequence else "none",
        "expected_final_action": expected_final_action,
        "expected_account_id": expected_account_id,
        "expected_search_query_hints": expected_search_query_hints,
        "should_use_tool": should_use_tool,
        "should_refuse": should_refuse,
        "max_steps": max_steps,
        "why_this_case_exists": str(tc.get("Why This Test Exists", "") or ""),
        "actual_tool_sequence": actual_tool_sequence,
        "actual_account_id": actual_account_id,
        "actual_search_query": actual_search_query,
        "actual_final_action": actual_final_action,
        "step_count": len(trace),
        "used_any_tool": used_any_tool,
        "tool_match": tool_match,
        "account_id_match": account_id_match,
        "search_query_hint_match": search_query_hint_match,
        "argument_match": argument_match,
        "stop_quality_match": stop_quality_match,
        "stop_quality_note": stop_quality_note,
        "unnecessary_tool_use": unnecessary_tool_use,
        "final_answer": agent_result.get("final_answer", ""),
        "stop_reason": stop_reason,
        "trace": trace,
    }


def save_json_results(results: list[dict], results_dir: Path) -> Path:
    output_path = results_dir / "agent_evaluation_results.json"
    payload = {
        "bot_model": BOT_MODEL,
        "bot_provider": BOT_PROVIDER,
        "excel_file": EXCEL_FILE,
        "test_sheet": TEST_SHEET,
        "total_cases": len(results),
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return output_path


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_test_cases(EXCEL_PATH, TEST_SHEET)

    print(f"\n{'=' * 64}")
    print("  Test 12 — Agent Behavior Evaluation")
    print(f"  Bot model : {BOT_MODEL} ({BOT_PROVIDER})")
    print(f"  Excel     : {EXCEL_FILE} / {TEST_SHEET}")
    print(f"  Max steps : {DEFAULT_MAX_STEPS} (default per config)")
    print(f"{'=' * 64}")

    start_from, max_cases = ask_run_config(len(cases))
    print(f"  Starting from case {start_from}; max cases = {'all' if max_cases == 0 else max_cases}\n")

    results = []
    cases_run = 0
    for i, tc in enumerate(cases, 1):
        if i < start_from:
            continue
        if max_cases and cases_run >= max_cases:
            break

        print(f"[{i:02d}/{len(cases)}] {tc.get('TC_ID', f'TC{i:02d}')} — {tc.get('Question', '')}")
        result = evaluate_case(tc)
        actual = " > ".join(result["actual_tool_sequence"]) if result["actual_tool_sequence"] else "none"
        print(f"  Expected tools : {result['expected_tool_sequence']}")
        print(f"  Actual tools   : {actual}")
        if result["expected_account_id"]:
            print(f"  Account arg    : {result['actual_account_id'] or 'missing'} ({'MATCH' if result['account_id_match'] else 'MISMATCH'})")
        if result["expected_search_query_hints"]:
            print(f"  Search args    : {'MATCH' if result['search_query_hint_match'] else 'MISMATCH'}")
        print(f"  Stop reason    : {result['stop_reason']}")
        print(f"  Stop quality   : {'MATCH' if result['stop_quality_match'] else 'MISMATCH'}")
        print(f"  Final answer   : {result['final_answer'][:120]}{'...' if len(result['final_answer']) > 120 else ''}")
        print(f"  Tool pattern   : {'MATCH' if result['tool_match'] else 'MISMATCH'}")
        print(f"  Args pattern   : {'MATCH' if result['argument_match'] else 'MISMATCH'}\n")
        results.append(result)
        cases_run += 1
        time.sleep(2)

    report_config = {
        "BOT_MODEL": BOT_MODEL,
    }
    json_path = save_json_results(results, RESULTS_DIR)
    report_path = generate_report(results, report_config, RESULTS_DIR)
    print(f"Saved JSON: {json_path}")
    print(f"Saved report: {report_path}")
    print("Done.\n")


if __name__ == "__main__":
    main()
