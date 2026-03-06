"""
temperature_evaluator.py — Temperature Sensitivity Testing (Test 8)

What this tests:
  Run the full banking bot test suite at 4 temperature settings and compare
  pass rates. Shows how temperature affects consistency and reliability.

Temperatures tested: 0.0 / 0.5 / 1.0 / 1.5

  0.0 — fully deterministic, always picks the most probable word
  0.5 — slightly relaxed, minor variation
  1.0 — default for most models, noticeable variation
  1.5 — loosely bound, creative but unreliable for structured tasks

GenAI Eval concepts covered:
  1. Temperature sensitivity   — how randomness affects pass/fail outcomes
  2. Category degradation      — which test categories break first
  3. Consistency vs creativity — the core tradeoff in model configuration

Output: HTML report in results/
"""

import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import openpyxl
import yaml

# ─── Path setup ───────────────────────────────────────────────────────────────

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")

sys.path.insert(0, PROJECT_ROOT)
from model_client import call_model

# ─── Config ───────────────────────────────────────────────────────────────────

with open(CONFIG_FILE) as f:
    _cfg = yaml.safe_load(f)

_section    = _cfg["phase3_temperature"]
MODEL_NAME  = _section["BOT_MODEL"]
_PROVIDER   = _section.get("BOT_PROVIDER", _cfg["shared"].get("PROVIDER", "ollama"))
_OLLAMA_URL = _cfg["shared"].get("OLLAMA_URL", "http://localhost:11434/api/generate")
_API_KEY    = _section.get("OPENAI_API_KEY",
              _section.get("ANTHROPIC_API_KEY",
              _section.get("GEMINI_API_KEY", "")))

TEMPERATURES    = _section.get("TEMPERATURES", [0.0, 0.5, 1.0, 1.5])
TEST_CASES_FILE = Path(SCRIPT_DIR) / _section.get("EXCEL_FILE", "banking_test_cases.xlsx")
TEST_SHEET      = _section.get("TEST_SHEET", "Test Cases")
RESULTS_DIR     = Path(SCRIPT_DIR) / "results"

SYSTEM_PROMPT = """
You are a helpful banking assistant for Global Bank.

You have knowledge about the following products and fees:
  - Gold Account: 4% annual interest rate
  - Silver Account: 1% annual interest rate
  - Bronze Account: 0.5% annual interest rate
  - International wire transfer fee: $50 per transaction
  - Domestic wire transfer fee: $15 per transaction
  - Overdraft fee: $35 per occurrence
  - Monthly maintenance fee: $10 (waived if balance > $1,000)

Guidelines:
  - Always be polite, concise, and professional.
  - Only answer questions related to banking, accounts, fees, and financial products.
  - If a question is not related to banking, politely decline and remind the user
    that you can only assist with banking inquiries.
  - Never make up information. If you don't know something, say so honestly.
"""

# ─── Data models ──────────────────────────────────────────────────────────────

ExpectedType = Literal["answer", "refusal"]

@dataclass
class TestCase:
    id: int
    category: str
    summary: str
    prompt: str
    expected: ExpectedType
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)

@dataclass
class TestResult:
    case: TestCase
    temperature: float
    output: str
    passed: bool
    latency: float
    failure_reason: str = ""

# ─── Load test cases ──────────────────────────────────────────────────────────

def load_test_cases() -> list[TestCase]:
    if not TEST_CASES_FILE.exists():
        raise FileNotFoundError(f"Test cases file not found: {TEST_CASES_FILE}")

    wb = openpyxl.load_workbook(TEST_CASES_FILE, data_only=True)
    ws = wb[TEST_SHEET] if TEST_SHEET in wb.sheetnames else wb.active

    def parse_keywords(raw) -> list[str]:
        if not raw:
            return []
        return [kw.strip() for kw in str(raw).split(",") if kw.strip()]

    def is_enabled(val) -> bool:
        if val is True:
            return True
        return str(val).strip().upper() in ("YES", "TRUE", "1")

    cases = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue
        tid, category, summary, prompt, expected, must_contain_raw, must_not_raw, enabled = row[:8]
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
        ))

    print(f"  Loaded {len(cases)} test case(s) from {TEST_CASES_FILE.name}")
    return cases

# ─── Bot call with temperature ────────────────────────────────────────────────

def ask_bot(prompt: str, temperature: float) -> str:
    """Call the banking bot with a specific temperature setting."""
    import requests
    provider = _PROVIDER.lower().strip()

    if provider == "ollama":
        payload = {
            "model": MODEL_NAME,
            "prompt": f"{SYSTEM_PROMPT}\n\nUser: {prompt}",
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            response = requests.post(_OLLAMA_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"ERROR: {e}"

    elif provider == "openai":
        key = _API_KEY or os.environ.get("OPENAI_API_KEY", "")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        payload = {"model": MODEL_NAME, "messages": messages, "temperature": temperature}
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions",
                                     headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"ERROR: {e}"

    elif provider == "anthropic":
        key = _API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "max_tokens": 1024,
            "temperature": temperature,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post("https://api.anthropic.com/v1/messages",
                                     headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["content"][0]["text"].strip()
        except Exception as e:
            return f"ERROR: {e}"

    elif provider == "gemini":
        key = _API_KEY or os.environ.get("GEMINI_API_KEY", "")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {"temperature": temperature}
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"ERROR: {e}"

    else:
        return f"ERROR: Unknown provider '{provider}'"

# ─── Validation ───────────────────────────────────────────────────────────────

def validate(output: str, case: TestCase) -> tuple[bool, str]:
    lower = output.lower()

    for word in case.must_not_contain:
        if word.lower() in lower:
            return False, f"Contained forbidden keyword: '{word}'"

    if case.expected == "answer":
        missing = [kw for kw in case.must_contain if kw.lower() not in lower]
        if missing:
            return False, f"Missing keywords: {missing}"
        return True, ""

    elif case.expected == "refusal":
        REFUSAL_SIGNALS = ["banking", "assist", "cannot", "can't", "sorry", "only help", "only assist"]
        if not any(sig in lower for sig in REFUSAL_SIGNALS):
            return False, "No refusal signal found"
        missing = [kw for kw in case.must_contain if kw.lower() not in lower]
        if missing:
            return False, f"Missing refusal keywords: {missing}"
        return True, ""

    return False, f"Unknown expected type: '{case.expected}'"

# ─── Main evaluation loop ─────────────────────────────────────────────────────

def run_evaluation() -> list[TestResult]:
    test_cases = load_test_cases()
    all_results: list[TestResult] = []

    for temp_idx, temperature in enumerate(TEMPERATURES, 1):
        print(f"\n  ┌{'─'*45}┐")
        print(f"  │  Temperature {temperature}  —  run {temp_idx} of {len(TEMPERATURES)}          │")
        print(f"  └{'─'*45}┘")

        passed_count = 0
        for i, case in enumerate(test_cases, 1):
            print(f"  [{i:02d}/{len(test_cases)}] {case.summary:<42}", end="", flush=True)

            start = time.time()
            output = ask_bot(case.prompt, temperature)
            latency = round(time.time() - start, 2)

            passed, reason = validate(output, case)
            if passed:
                passed_count += 1

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}  ({latency}s)")

            all_results.append(TestResult(
                case=case,
                temperature=temperature,
                output=output,
                passed=passed,
                latency=latency,
                failure_reason=reason
            ))

        print(f"\n  ── Result: {passed_count}/{len(test_cases)} passed at temperature {temperature} ──")

    return all_results

# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  Test 8 — Temperature Sensitivity Testing")
    print(f"  Model      : {MODEL_NAME} ({_PROVIDER})")
    print(f"  Temperatures: {TEMPERATURES}")
    print(f"  Test file  : {TEST_CASES_FILE.name} → {TEST_SHEET}")
    print(f"{'='*50}")

    results = run_evaluation()

    RESULTS_DIR.mkdir(exist_ok=True)

    from report_generator import generate_report
    report_path = generate_report(results, TEMPERATURES, MODEL_NAME, RESULTS_DIR)

    print(f"\n{'='*50}")
    print(f"  ✅ Report saved → {report_path}")
    print(f"  Open in browser: file://{report_path}")
    print(f"{'='*50}\n")
