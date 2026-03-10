import json
import os
import sys
import time
from pathlib import Path

import yaml

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from model_client import call_model

CONFIG_PATH = PROJECT_ROOT / "config.yaml"
with open(CONFIG_PATH, encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

_section = _cfg.get("phase5_trajectory_evaluation", {})
_shared = _cfg.get("shared", {})

JUDGE_MODEL = _section.get("JUDGE_MODEL", "mistral")
JUDGE_PROVIDER = _section.get("JUDGE_PROVIDER", "ollama")
OLLAMA_URL = _shared.get("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_TRACE_FILE = _section.get("TRACE_FILE", "sample_agent_evaluation_results.json")

RESULTS_DIR = SCRIPT_DIR / "results"


def load_traces(trace_path: Path) -> dict:
    with open(trace_path, encoding="utf-8") as f:
        return json.load(f)


def _build_judge_prompt(case: dict) -> str:
    question = case.get("question", "")
    expected_behavior = case.get("expected_behavior", "")
    expected_tools = case.get("expected_tool_sequence", "none")
    actual_tools = " > ".join(case.get("actual_tool_sequence", [])) or "none"
    final_answer = case.get("final_answer", "")
    stop_reason = case.get("stop_reason", "unknown")

    steps_text = []
    for step in case.get("trace", []):
        action = step.get("action")
        if action == "tool":
            args = json.dumps(step.get("arguments", {}))
            result = json.dumps(step.get("tool_result", {}))
            steps_text.append(
                f"Step {step.get('step')}: TOOL CALL — {step.get('tool_name')} args={args}\n"
                f"  Tool result: {result}"
            )
        elif action == "final":
            steps_text.append(f"Step {step.get('step')}: FINAL ANSWER — {step.get('answer', '')}")
        else:
            steps_text.append(f"Step {step.get('step')}: ERROR — {step.get('error', '')}")

    trajectory = "\n".join(steps_text)

    return f"""You are a trajectory evaluator for a banking agent. Score the following agent trajectory on four dimensions.

QUESTION: {question}
EXPECTED BEHAVIOR: {expected_behavior}
EXPECTED TOOL SEQUENCE: {expected_tools}
ACTUAL TOOL SEQUENCE: {actual_tools}
STOP REASON: {stop_reason}

TRAJECTORY:
{trajectory}

FINAL ANSWER: {final_answer}

Score each dimension 1-5 and give a short reason. Respond ONLY with valid JSON in exactly this format:
{{
  "tool_selection": {{"score": <1-5>, "reason": "<one sentence>"}},
  "argument_quality": {{"score": <1-5>, "reason": "<one sentence>"}},
  "answer_groundedness": {{"score": <1-5>, "reason": "<one sentence>"}},
  "stop_appropriateness": {{"score": <1-5>, "reason": "<one sentence>"}},
  "overall": {{"score": <1-5>, "verdict": "<pass or fail>", "summary": "<two sentences max>"}}
}}

Scoring guide:
- tool_selection: Did the agent use the right tools in the right order? 5=exact match, 3=partially correct, 1=wrong tools or unnecessary use.
- argument_quality: Were the tool arguments correct and complete? 5=exact, 3=close but imprecise, 1=wrong or missing.
- answer_groundedness: Is the final answer grounded in the tool results, not invented? 5=fully grounded, 3=mostly grounded, 1=hallucinated.
- stop_appropriateness: Did the agent stop at the right point? 5=stopped cleanly after expected flow, 1=stopped too early or too late.
- overall: Average score rounded. verdict=pass if overall>=3, fail otherwise."""


def _parse_judge_response(raw: str) -> dict | None:
    import re
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def judge_case(case: dict) -> dict:
    prompt = _build_judge_prompt(case)
    raw = call_model(
        model=JUDGE_MODEL,
        provider=JUDGE_PROVIDER,
        prompt=prompt,
        system="You are a strict but fair LLM trajectory evaluator. Always respond with valid JSON only.",
        ollama_url=OLLAMA_URL,
    )
    scores = _parse_judge_response(raw)
    if not scores:
        return {
            "tc_id": case.get("tc_id"),
            "judge_error": True,
            "raw_judge_output": raw[:400],
        }
    return {
        "tc_id": case.get("tc_id"),
        "category": case.get("category"),
        "question": case.get("question"),
        "judge_error": False,
        "tool_selection_score": scores.get("tool_selection", {}).get("score"),
        "tool_selection_reason": scores.get("tool_selection", {}).get("reason", ""),
        "argument_quality_score": scores.get("argument_quality", {}).get("score"),
        "argument_quality_reason": scores.get("argument_quality", {}).get("reason", ""),
        "answer_groundedness_score": scores.get("answer_groundedness", {}).get("score"),
        "answer_groundedness_reason": scores.get("answer_groundedness", {}).get("reason", ""),
        "stop_appropriateness_score": scores.get("stop_appropriateness", {}).get("score"),
        "stop_appropriateness_reason": scores.get("stop_appropriateness", {}).get("reason", ""),
        "overall_score": scores.get("overall", {}).get("score"),
        "verdict": scores.get("overall", {}).get("verdict", "unknown"),
        "summary": scores.get("overall", {}).get("summary", ""),
        "raw_judge_output": raw,
    }


def save_results(scored: list[dict], meta: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {"judge_model": JUDGE_MODEL, "judge_provider": JUDGE_PROVIDER, **meta, "scored": scored}
    path = RESULTS_DIR / "trajectory_evaluation_results.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return path


def _read_limited_range() -> tuple[int, int]:
    while True:
        try:
            start = int(input("  Start from case number: ").strip())
            count = int(input("  How many cases to run:  ").strip())
            if start >= 1 and count >= 1:
                return start, count
            print("  Both values must be 1 or greater.")
        except ValueError:
            print("  Please enter a valid number.")


def _ask_run_config(total: int) -> tuple[int, int]:
    print(f"\n  Loaded {total} trajectories.")
    print("  Run options:")
    print("  [R] Score all trajectories")
    print("  [L] Limited run — choose start and count")
    print()
    while True:
        choice = input("  Your choice (R/L): ").strip().upper()
        if choice == "R":
            return 1, total
        if choice == "L":
            return _read_limited_range()
        print("  Please enter R or L.")


def main():
    print()
    print("=" * 64)
    print("  Test 13 — Trajectory Evaluation with Judge Model")
    print(f"  Judge model : {JUDGE_MODEL} ({JUDGE_PROVIDER})")
    print(f"  Trace file  : {DEFAULT_TRACE_FILE}")
    print("=" * 64)

    trace_path = SCRIPT_DIR / DEFAULT_TRACE_FILE
    if not trace_path.exists():
        trace_path = SCRIPT_DIR.parent / "agent-evaluation" / "results" / DEFAULT_TRACE_FILE
    if not trace_path.exists():
        print(f"\nERROR: Trace file not found: {DEFAULT_TRACE_FILE}")
        print("Copy a Test 12 results JSON into the trajectory-evaluation folder or update config.yaml.")
        sys.exit(1)

    data = load_traces(trace_path)
    cases = data.get("results", [])
    total = len(cases)
    meta = {
        "source_bot_model": data.get("bot_model", "unknown"),
        "trace_file": str(trace_path.name),
        "total_cases": total,
    }

    start_idx, run_count = _ask_run_config(total)
    selected = cases[start_idx - 1: start_idx - 1 + run_count]
    print(f"  Starting from case {start_idx}; scoring {len(selected)} trajectories\n")

    scored = []
    for i, case in enumerate(selected, 1):
        tc_id = case.get("tc_id", f"CASE{i}")
        question = case.get("question", "")
        print(f"[{i:02d}/{len(selected):02d}] {tc_id} — {question}")
        result = judge_case(case)
        if result.get("judge_error"):
            print(f"  Judge error — raw: {result.get('raw_judge_output', '')[:120]}")
        else:
            verdict_color = "PASS" if result.get("verdict") == "pass" else "FAIL"
            print(f"  Overall     : {result.get('overall_score')}/5 [{verdict_color}]")
            print(f"  Tool select : {result.get('tool_selection_score')}/5 — {result.get('tool_selection_reason','')}")
            print(f"  Arg quality : {result.get('argument_quality_score')}/5 — {result.get('argument_quality_reason','')}")
            print(f"  Groundedness: {result.get('answer_groundedness_score')}/5 — {result.get('answer_groundedness_reason','')}")
            print(f"  Stop timing : {result.get('stop_appropriateness_score')}/5 — {result.get('stop_appropriateness_reason','')}")
            print(f"  Summary     : {result.get('summary','')}")
        print()
        scored.append(result)
        time.sleep(2)

    json_path = save_results(scored, meta)
    from report_generator import generate_report
    report_path = generate_report(scored, {"JUDGE_MODEL": JUDGE_MODEL}, RESULTS_DIR)
    print(f"Saved JSON   : {json_path}")
    print(f"Saved report : {report_path}")
    print("Done.\n")


if __name__ == "__main__":
    main()
