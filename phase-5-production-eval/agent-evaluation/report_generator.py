from datetime import datetime
from html import escape
from pathlib import Path


TOOL_ICONS = {
    "lookup_account_status": "🗂️",
    "search_docs": "📄",
    "calculator": "🧮",
}


def explain_stop_reason(result) -> tuple[str, str, str]:
    stop_reason = str(result.get("stop_reason", "unknown"))
    tool_match = result.get("tool_match")
    expected_tools = str(result.get("expected_tool_sequence", "none"))
    actual_tools = " > ".join(result.get("actual_tool_sequence", [])) or "none"

    if stop_reason == "final_answer":
        if tool_match:
            return (
                "Stopped normally",
                "The agent reached a final answer and its tool path matched the expected pattern.",
                "#6af7a0",
            )
        return (
            "Stopped with an incomplete or unexpected path",
            f"The agent produced a final answer, but the observed tool path ({actual_tools}) did not match the expected path ({expected_tools}).",
            "#f76a6a",
        )

    if stop_reason == "malformed_action":
        return (
            "Stopped because the action format broke",
            "The model stopped producing a valid structured action, so the evaluator halted the run instead of guessing what the agent meant.",
            "#f76a6a",
        )

    if stop_reason == "max_steps_reached":
        return (
            "Stopped after reaching the step limit",
            "The agent did not finish within the allowed number of steps, so the evaluator cut off the trajectory.",
            "#f0c040",
        )

    if stop_reason == "tool_error":
        return (
            "Stopped because a tool call failed",
            "A tool invocation returned an error, so the run could not continue safely.",
            "#f76a6a",
        )

    if stop_reason == "timeout_error":
        return (
            "Stopped because Ollama timed out",
            "The local model did not respond within the allowed time. This is a resource or load issue, not an agent logic failure. Re-run the case when the model is less busy.",
            "#f0c040",
        )

    return (
        "Stopped for an unclassified reason",
        f"The evaluator recorded the raw stop reason as '{stop_reason}'. Review the trace for the exact point where the run ended.",
        "#8a8aa0",
    )


def generate_report(results, config, results_dir: Path) -> Path:
    bot_model = config.get("BOT_MODEL", "unknown")
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")
    total = len(results)
    tool_cases = sum(1 for r in results if r.get("used_any_tool"))
    correct_tool = sum(1 for r in results if r.get("tool_match") is True)
    correct_arguments = sum(1 for r in results if r.get("argument_match") is True)
    correct_stop_quality = sum(1 for r in results if r.get("stop_quality_match") is True)
    unnecessary_tool = sum(1 for r in results if r.get("unnecessary_tool_use"))
    refusals = sum(1 for r in results if r.get("should_refuse"))

    def card(label, value, desc, color="#7c6af7"):
        return f'''<div style="background:#17171c;border:1px solid #2a2a32;border-radius:14px;padding:18px;flex:1;min-width:180px">
          <div style="font-size:30px;font-weight:800;color:{color};margin-bottom:6px">{value}</div>
          <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#b8b8c8;margin-bottom:6px">{label}</div>
          <div style="font-size:12px;color:#76768a">{desc}</div>
        </div>'''

    cards = f'''<div style="display:flex;gap:14px;flex-wrap:wrap;margin:24px 0 28px;">
      {card('Cases', total, 'All Test 12 agent cases', '#f7a06a')}
      {card('Tool Used', tool_cases, 'Cases where at least one tool was invoked', '#6af7a0')}
      {card('Right Tool Pattern', f'{correct_tool}/{total}', 'Expected tool sequence matched exactly', '#7c6af7')}
      {card('Right Arguments', f'{correct_arguments}/{total}', 'Expected account IDs and query hints matched the observed tool arguments', '#5dd6ff')}
      {card('Right Stop Behavior', f'{correct_stop_quality}/{total}', 'Agent stopped at the appropriate point for the expected flow', '#a78bfa')}
      {card('Unnecessary Tool Use', unnecessary_tool, 'Cases where a tool was used but should not have been', '#f76a6a')}
      {card('Refusal Cases', refusals, 'Out-of-scope or boundary cases expecting refusal', '#f0c040')}
    </div>'''

    rows = []
    for r in results:
        trace_html = ""
        for step in r.get("trace", []):
            if step.get("action") == "tool":
                icon = TOOL_ICONS.get(step.get("tool_name"), "🔧")
                trace_html += f'''<div style="background:#131318;border:1px solid #2a2a32;border-radius:12px;padding:14px;margin-bottom:10px">
                  <div style="font-size:12px;color:#8a8aa0;margin-bottom:6px">STEP {step.get('step')}</div>
                  <div style="font-size:15px;font-weight:700;color:#f7a06a;margin-bottom:8px">{icon} Tool Invoked — {escape(str(step.get('tool_name','')))}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#d0d0dc;margin-bottom:8px"><b>Arguments:</b> {escape(str(step.get('arguments', {})))}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#9ea0b4;white-space:pre-wrap"><b>Tool Output:</b> {escape(str(step.get('tool_result', {})))}</div>
                </div>'''
            elif step.get("action") == "final":
                trace_html += f'''<div style="background:#131a14;border:1px solid #22422a;border-radius:12px;padding:14px;margin-bottom:10px">
                  <div style="font-size:12px;color:#8a8aa0;margin-bottom:6px">STEP {step.get('step')}</div>
                  <div style="font-size:15px;font-weight:700;color:#6af7a0;margin-bottom:8px">✅ Final Answer</div>
                  <div style="font-size:13px;color:#d8d8e5;white-space:pre-wrap">{escape(str(step.get('answer','')))}</div>
                </div>'''
            else:
                trace_html += f'''<div style="background:#1d1414;border:1px solid #4a2323;border-radius:12px;padding:14px;margin-bottom:10px">
                  <div style="font-size:12px;color:#8a8aa0;margin-bottom:6px">STEP {step.get('step')}</div>
                  <div style="font-size:15px;font-weight:700;color:#f76a6a;margin-bottom:8px">⚠️ Agent Error</div>
                  <div style="font-size:13px;color:#d8d8e5;white-space:pre-wrap">{escape(str(step.get('error','Unknown error')))}</div>
                </div>'''

        status_color = "#6af7a0" if r.get("tool_match") else "#f76a6a"
        status_label = "MATCH" if r.get("tool_match") else "MISMATCH"
        stop_title, stop_explanation, stop_color = explain_stop_reason(r)
        argument_status_color = "#6af7a0" if r.get("argument_match") else "#f76a6a"
        argument_status_label = "MATCH" if r.get("argument_match") else "MISMATCH"
        stop_quality_color = "#6af7a0" if r.get("stop_quality_match") else "#f76a6a"
        stop_quality_label = "MATCH" if r.get("stop_quality_match") else "MISMATCH"
        rows.append(f'''<div style="background:#141417;border:1px solid #2a2a32;border-radius:14px;padding:14px 16px;margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px">
            <div>
              <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#8a8aa0">{escape(str(r.get('tc_id','')))} · {escape(str(r.get('category','')))}</span>
              <div style="font-size:15px;font-weight:700;color:#ececf5;line-height:1.3;margin-top:2px">{escape(str(r.get('question','')))}</div>
            </div>
            <div style="background:{status_color}22;color:{status_color};border:1px solid {status_color}55;border-radius:999px;padding:4px 10px;font-size:11px;font-weight:700;letter-spacing:1px;white-space:nowrap">{status_label}</div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1.6fr;gap:12px;align-items:start">
            <div style="display:flex;flex-direction:column;gap:8px">
              <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px">
                <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Expected</div>
                <div style="font-size:12px;color:#c0c0d4;margin-bottom:4px">{escape(str(r.get('expected_behavior','')))}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#b8b8c8;line-height:1.8">
                  Tools: {escape(str(r.get('expected_tool_sequence','')))} &nbsp;|&nbsp;
                  Account: {escape(str(r.get('expected_account_id','')) or '—')} &nbsp;|&nbsp;
                  Steps: {escape(str(r.get('max_steps','')))}
                </div>
              </div>
              <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px">
                <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Observed</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#d8d8e5;line-height:1.9">
                  Tools: {escape(' > '.join(r.get('actual_tool_sequence', [])) or 'none')}<br>
                  Account: {escape(str(r.get('actual_account_id','')) or '—')} &nbsp;|&nbsp; Query: {escape(str(r.get('actual_search_query','')) or '—')}<br>
                  Stop: {escape(str(r.get('stop_reason','')))} &nbsp;|&nbsp; Steps: {escape(str(r.get('step_count','')))}
                </div>
              </div>
              <div style="display:flex;gap:6px;flex-wrap:wrap">
                <div style="background:{argument_status_color}14;border:1px solid {argument_status_color}44;border-radius:8px;padding:6px 10px;flex:1;min-width:80px">
                  <div style="font-size:10px;color:{argument_status_color};font-weight:700;letter-spacing:0.5px">ARGS</div>
                  <div style="font-size:12px;color:#ececf5;font-weight:700">{argument_status_label}</div>
                </div>
                <div style="background:{stop_quality_color}14;border:1px solid {stop_quality_color}44;border-radius:8px;padding:6px 10px;flex:1;min-width:80px">
                  <div style="font-size:10px;color:{stop_quality_color};font-weight:700;letter-spacing:0.5px">STOP</div>
                  <div style="font-size:12px;color:#ececf5;font-weight:700">{stop_quality_label}</div>
                  <div style="font-size:11px;color:#9a9aaa;margin-top:2px">{escape(stop_title)}</div>
                </div>
              </div>
            </div>
            <div>
              <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Trace</div>
              {trace_html}
            </div>
          </div>
        </div>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test 12 — Agent Behavior Evaluation</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0d0d0f; color:#e8e8f0; font-family:'Syne',sans-serif; padding:28px; line-height:1.6; }}
  h1 {{ font-size:30px; color:#f7a06a; margin-bottom:8px; }}
  h2 {{ font-size:18px; color:#c9c9d6; margin:26px 0 14px; }}
  .meta {{ color:#8a8aa0; font-size:13px; margin-bottom:8px; }}
  .note {{ background:#141417; border:1px solid #2a2a32; border-left:4px solid #7c6af7; padding:14px 16px; border-radius:12px; color:#cbcbda; font-size:14px; }}
  @media (max-width: 1100px) {{
    body {{ padding:18px; }}
    div[style*='grid-template-columns:1.1fr 1.6fr'] {{ display:block !important; }}
  }}
</style>
</head>
<body>
  <h1>Test 12 — Agent Behavior Evaluation</h1>
  <div class="meta">Bot: <b style="color:#d8d8e5">{escape(str(bot_model))}</b> &nbsp;|&nbsp; Cases: <b style="color:#d8d8e5">{total}</b> &nbsp;|&nbsp; Generated: <b style="color:#d8d8e5">{timestamp}</b></div>
  <div class="note">This report is evaluation-first: the goal is to show whether the agent invoked tools when needed, with what arguments, and how the final answer used those tool outputs. Tool invocations are shown with explicit icons: 🗂️ account lookup, 📄 document search, 🧮 calculator.</div>
  {cards}
  <h2>Per-Case Trace</h2>
  {''.join(rows)}
</body>
</html>'''

    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "agent_evaluation_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    return report_path
