"""
evaluation.py — Functional Evaluation Suite for the Global Bank Chatbot

GenAI Eval concepts covered:
  1. Test case design     — stored in banking_test_cases.xlsx (edit there, not here!)
  2. Keyword validation   — must_contain / must_not_contain per test case
  3. Latency measurement  — how long does the model take per query?
  4. Pass-rate metric     — aggregate quality score across the suite
  5. Category breakdown   — see which types of questions the bot struggles with
  6. Multi-turn testing   — does the bot hold context across follow-ups?

Run modes:
  a — Automated evaluation (runs all enabled test cases, prints a report)
  m — Multi-turn context demo
  i — Interactive free chat
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import openpyxl

from bot import MODEL_NAME, BankingChatSession, ask_banking_bot

# ─── Config ───────────────────────────────────────────────────────────────────

TEST_CASES_FILE = Path(__file__).parent / "banking_test_cases.xlsx"

# ─── Data Model ───────────────────────────────────────────────────────────────

ExpectedType = Literal["answer", "refusal"]


@dataclass
class TestCase:
    id: int
    summary: str
    prompt: str
    expected: ExpectedType
    category: str = "general"
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class TestResult:
    case: TestCase
    output: str
    passed: bool
    latency: float
    failure_reason: str = ""


# ─── Load Test Cases from Excel ───────────────────────────────────────────────

def load_test_cases(path: Path = TEST_CASES_FILE) -> list[TestCase]:
    """
    Read enabled test cases from the 'TestCases' sheet of the Excel file.

    Column layout:
      A=ID, B=Category, C=Summary, D=Prompt, E=Expected,
      F=Must Contain, G=Must NOT Contain, H=Enabled, I=Notes
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Test cases file not found: {path}\n"
            "Make sure banking_test_cases.xlsx is in the same folder as evaluation.py."
        )

    wb = openpyxl.load_workbook(path, data_only=True)

    if "TestCases" in wb.sheetnames:
        ws = wb["TestCases"]
    else:
        ws = wb.active
        print(f"  ⚠️  Sheet 'TestCases' not found — using first sheet: '{ws.title}'")

    def is_enabled(val) -> bool:
        """Accepts True (boolean), 'YES', 'TRUE', '1' as enabled."""
        if val is True:
            return True
        return str(val).strip().upper() in ("YES", "TRUE", "1")

    def parse_keywords(raw) -> list[str]:
        if not raw:
            return []
        return [kw.strip() for kw in str(raw).split(",") if kw.strip()]

    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue

        tid, category, summary, prompt, expected, must_contain_raw, must_not_raw, enabled = row[:8]
        notes = row[8] if len(row) > 8 else ""

        if not is_enabled(enabled):
            continue

        cases.append(TestCase(
            id=int(tid) if tid else 0,
            category=str(category).strip() if category else "general",
            summary=str(summary).strip() if summary else "",
            prompt=str(prompt).strip() if prompt else "",
            expected=str(expected).strip().lower(),
            must_contain=parse_keywords(must_contain_raw),
            must_not_contain=parse_keywords(must_not_raw),
            notes=str(notes).strip() if notes else "",
        ))

    print(f"  Loaded {len(cases)} enabled test case(s) from {path.name}")
    return cases


# ─── Validation Logic ─────────────────────────────────────────────────────────

def validate(output: str, case: TestCase) -> tuple[bool, str]:
    """Returns (passed, failure_reason). Empty failure_reason = pass."""
    lower = output.lower()

    for word in case.must_not_contain:
        if word.lower() in lower:
            return False, f"Output contained forbidden keyword: '{word}'"

    if case.expected == "answer":
        missing = [kw for kw in case.must_contain if kw.lower() not in lower]
        if missing:
            return False, f"Missing expected keywords: {missing}"
        return True, ""

    elif case.expected == "refusal":
        REFUSAL_SIGNALS = ["banking", "assist", "cannot", "can't", "sorry", "only help", "only assist"]
        if not any(sig in lower for sig in REFUSAL_SIGNALS):
            return False, "No refusal signal found in output"
        missing = [kw for kw in case.must_contain if kw.lower() not in lower]
        if missing:
            return False, f"Missing expected refusal keywords: {missing}"
        return True, ""

    return False, f"Unknown expected type: '{case.expected}'"


# ─── Automated Evaluation ─────────────────────────────────────────────────────

def run_evaluation():
    print(f"\n{'='*65}")
    print(f"  Global Bank Chatbot — Evaluation Suite")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Test cases file: {TEST_CASES_FILE.name}")
    print(f"{'='*65}\n")

    test_cases = load_test_cases()
    if not test_cases:
        print("No enabled test cases found. Set Enabled=TRUE in banking_test_cases.xlsx.")
        return

    # ── Ask how many test cases to run ───────────────────────────────────────
    print(f"  {len(test_cases)} enabled test case(s) available.")
    while True:
        choice = input("  How many to run? (enter a number or ALL): ").strip().upper()
        if choice == "ALL":
            selected = test_cases
            break
        elif choice.isdigit():
            n = int(choice)
            if n <= 0:
                print("  Please enter a number greater than 0.")
            elif n > len(test_cases):
                print(f"  Only {len(test_cases)} test cases available. Running all.")
                selected = test_cases
                break
            else:
                selected = test_cases[:n]
                break
        else:
            print("  Invalid input. Enter a number or ALL.")

    print(f"\n  Running {len(selected)} test(s)...\n")
    results: list[TestResult] = []

    for i, case in enumerate(selected, 1):
        print(f"  [{i:02d}/{len(selected)}] [{case.category:<15}] {case.summary}")
        start = time.time()
        output = ask_banking_bot(case.prompt)
        latency = round(time.time() - start, 2)

        passed, reason = validate(output, case)
        results.append(TestResult(case=case, output=output, passed=passed,
                                  latency=latency, failure_reason=reason))

        status = "✅ PASS" if passed else f"❌ FAIL — {reason}"
        print(f"             {status}  ({latency}s)")

    _print_report(results)


def _print_report(results: list[TestResult]):
    total    = len(results)
    n_passed = sum(1 for r in results if r.passed)
    pass_pct = n_passed / total * 100

    print(f"\n{'─'*65}")
    print(f"  OVERALL:  {n_passed}/{total} passed  ({pass_pct:.1f}%)")
    print(f"{'─'*65}\n")

    categories: dict[str, list[TestResult]] = {}
    for r in results:
        categories.setdefault(r.case.category, []).append(r)

    print(f"  {'Category':<20} {'Pass':<6} {'Total':<6} {'Rate':<9} {'Avg Latency'}")
    print(f"  {'─'*20} {'─'*5} {'─'*5} {'─'*8} {'─'*12}")
    for cat, cat_results in categories.items():
        cat_pass = sum(1 for r in cat_results if r.passed)
        avg_lat  = sum(r.latency for r in cat_results) / len(cat_results)
        rate     = cat_pass / len(cat_results) * 100
        flag     = "  ⚠️" if rate < 100 else ""
        print(f"  {cat:<20} {cat_pass:<6} {len(cat_results):<6} {rate:<8.0f}%  {avg_lat:.2f}s{flag}")

    failed = [r for r in results if not r.passed]
    if failed:
        print(f"\n  ❌ Failed Tests ({len(failed)}):")
        print(f"  {'─'*60}")
        for r in failed:
            print(f"\n  #{r.case.id} {r.case.summary}")
            print(f"  Prompt  : {r.case.prompt}")
            print(f"  Reason  : {r.failure_reason}")
            snippet = r.output[:220].replace("\n", " ")
            print(f"  Output  : {snippet}{'...' if len(r.output) > 220 else ''}")

    latencies = [r.latency for r in results]
    print(f"\n  Latency — min: {min(latencies):.2f}s  max: {max(latencies):.2f}s  avg: {sum(latencies)/len(latencies):.2f}s")
    print(f"\n{'='*65}")
    print(f"  💡 To add/edit/disable tests, open banking_test_cases.xlsx and rerun.\n")


# ─── Multi-turn Demo ──────────────────────────────────────────────────────────

def run_multiturn_demo():
    print("\n>> Multi-turn demo — bot remembers earlier messages in the session.\n")
    session = BankingChatSession()
    turns = [
        "Hi! What accounts do you offer?",
        "What interest rate does the Gold one pay?",
        "And if I wanted to send money abroad, what would that cost?",
        "Can you recommend a good pizza place nearby?",
    ]
    for msg in turns:
        print(f"You : {msg}")
        print(f"Bot : {session.chat(msg)}\n")


# ─── Interactive Mode ─────────────────────────────────────────────────────────

def run_interactive():
    print("\n>> Interactive chat — type 'exit' to quit, 'reset' to clear history.\n")
    session = BankingChatSession()
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            session.reset()
            print("(Conversation history cleared)\n")
            continue
        print(f"Bot: {session.chat(user_input)}\n")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nGlobal Bank Chatbot — Evaluation & Demo Tool")
    print("  a = Automated evaluation")
    print("  m = Multi-turn context demo")
    print("  i = Interactive free chat")
    mode = input("\nChoose mode: ").strip().lower()

    if mode == "a":
        run_evaluation()
    elif mode == "m":
        run_multiturn_demo()
    elif mode == "i":
        run_interactive()
    else:
        print("Invalid choice. Exiting.")