from datetime import datetime
from html import escape
from pathlib import Path


SCORE_COLOR = {5: "#6af7a0", 4: "#a0e080", 3: "#f0c040", 2: "#f7a06a", 1: "#f76a6a"}


def _score_color(score) -> str:
    try:
        return SCORE_COLOR.get(int(score), "#8a8aa0")
    except (TypeError, ValueError):
        return "#8a8aa0"


def _score_bar(score) -> str:
    try:
        s = int(score)
    except (TypeError, ValueError):
        s = 0
    color = _score_color(s)
    filled = s
    empty = 5 - s
    return (
        f'<span style="font-family:monospace;letter-spacing:2px;color:{color}">'
        + "█" * filled + '<span style="color:#2a2a32">' + "█" * empty + "</span></span>"
        + f' <span style="color:{color};font-weight:700">{s}/5</span>'
    )


def _verdict_badge(verdict: str) -> str:
    if str(verdict).lower() == "pass":
        return '<span style="background:#6af7a022;color:#6af7a0;border:1px solid #6af7a055;border-radius:999px;padding:3px 10px;font-size:11px;font-weight:700;letter-spacing:1px">PASS</span>'
    return '<span style="background:#f76a6a22;color:#f76a6a;border:1px solid #f76a6a55;border-radius:999px;padding:3px 10px;font-size:11px;font-weight:700;letter-spacing:1px">FAIL</span>'


def generate_report(scored: list[dict], config: dict, results_dir: Path) -> Path:
    judge_model = config.get("JUDGE_MODEL", "unknown")
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")
    total = len(scored)
    errors = sum(1 for r in scored if r.get("judge_error"))
    passed = sum(1 for r in scored if str(r.get("verdict", "")).lower() == "pass")
    failed = total - errors - passed

    def _avg(field):
        vals = [r.get(field) for r in scored if not r.get("judge_error") and r.get(field) is not None]
        return round(sum(vals) / len(vals), 1) if vals else "—"

    avg_tool = _avg("tool_selection_score")
    avg_args = _avg("argument_quality_score")
    avg_ground = _avg("answer_groundedness_score")
    avg_stop = _avg("stop_appropriateness_score")
    avg_overall = _avg("overall_score")

    def card(label, value, desc, color="#7c6af7"):
        return f'''<div style="background:#17171c;border:1px solid #2a2a32;border-radius:12px;padding:14px 16px;flex:1;min-width:140px">
          <div style="font-size:26px;font-weight:800;color:{color};margin-bottom:4px">{value}</div>
          <div style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#b8b8c8;margin-bottom:4px">{label}</div>
          <div style="font-size:11px;color:#76768a">{desc}</div>
        </div>'''

    summary_cards = f'''<div style="display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 24px">
      {card("Trajectories", total, "Total cases scored", "#f7a06a")}
      {card("Pass", passed, "Overall score ≥ 3", "#6af7a0")}
      {card("Fail", failed, "Overall score < 3", "#f76a6a")}
      {card("Judge Errors", errors, "Could not parse judge output", "#f0c040")}
      {card("Avg Overall", avg_overall, "Mean judge score across all cases", "#7c6af7")}
      {card("Avg Tool Select", avg_tool, "Mean tool selection score", "#5dd6ff")}
      {card("Avg Groundedness", avg_ground, "Mean answer groundedness score", "#a78bfa")}
    </div>'''

    rows = []
    for r in scored:
        tc_id = escape(str(r.get("tc_id", "")))
        category = escape(str(r.get("category", "")))
        question = escape(str(r.get("question", "")))

        if r.get("judge_error"):
            rows.append(f'''<div style="background:#141417;border:1px solid #3a2020;border-radius:12px;padding:12px 14px;margin-bottom:10px">
              <span style="font-size:11px;color:#8a8aa0;font-family:monospace">{tc_id} · {category}</span>
              <div style="font-size:14px;font-weight:700;color:#ececf5;margin:4px 0 8px">{question}</div>
              <div style="color:#f76a6a;font-size:12px">⚠️ Judge error — could not parse output. Raw: <code style="font-size:11px">{escape(str(r.get("raw_judge_output",""))[:200])}</code></div>
            </div>''')
            continue

        verdict = str(r.get("verdict", "")).lower()
        rows.append(f'''<div style="background:#141417;border:1px solid #2a2a32;border-radius:12px;padding:12px 14px;margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px">
            <div>
              <span style="font-size:11px;color:#8a8aa0;font-family:monospace">{tc_id} · {category}</span>
              <div style="font-size:15px;font-weight:700;color:#ececf5;margin-top:2px">{question}</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center">
              <span style="font-size:13px;color:#b8b8c8">Overall: {_score_bar(r.get("overall_score"))}</span>
              {_verdict_badge(verdict)}
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:8px">
            <div style="background:#101016;border:1px solid #23232c;border-radius:8px;padding:8px 10px">
              <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Tool Selection</div>
              <div style="margin-bottom:4px">{_score_bar(r.get("tool_selection_score"))}</div>
              <div style="font-size:11px;color:#a0a0b8">{escape(str(r.get("tool_selection_reason","")))} </div>
            </div>
            <div style="background:#101016;border:1px solid #23232c;border-radius:8px;padding:8px 10px">
              <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Argument Quality</div>
              <div style="margin-bottom:4px">{_score_bar(r.get("argument_quality_score"))}</div>
              <div style="font-size:11px;color:#a0a0b8">{escape(str(r.get("argument_quality_reason","")))} </div>
            </div>
            <div style="background:#101016;border:1px solid #23232c;border-radius:8px;padding:8px 10px">
              <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Answer Groundedness</div>
              <div style="margin-bottom:4px">{_score_bar(r.get("answer_groundedness_score"))}</div>
              <div style="font-size:11px;color:#a0a0b8">{escape(str(r.get("answer_groundedness_reason","")))} </div>
            </div>
            <div style="background:#101016;border:1px solid #23232c;border-radius:8px;padding:8px 10px">
              <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Stop Appropriateness</div>
              <div style="margin-bottom:4px">{_score_bar(r.get("stop_appropriateness_score"))}</div>
              <div style="font-size:11px;color:#a0a0b8">{escape(str(r.get("stop_appropriateness_reason","")))} </div>
            </div>
          </div>
          <div style="background:#0e0e14;border:1px solid #23232c;border-radius:8px;padding:8px 10px;font-size:12px;color:#c0c0d8">
            <b style="color:#8a8aa0">Judge summary:</b> {escape(str(r.get("summary","")))}
          </div>
        </div>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test 13 — Trajectory Evaluation</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0d0d0f; color:#e8e8f0; font-family:'Syne',sans-serif; padding:28px; line-height:1.6; }}
  h1 {{ font-size:28px; color:#f7a06a; margin-bottom:6px; }}
  h2 {{ font-size:16px; color:#c9c9d6; margin:22px 0 12px; }}
  .meta {{ color:#8a8aa0; font-size:12px; margin-bottom:8px; }}
  .note {{ background:#141417; border:1px solid #2a2a32; border-left:4px solid #7c6af7; padding:12px 14px; border-radius:10px; color:#cbcbda; font-size:13px; margin-bottom:8px; }}
  code {{ background:#1c1c22; padding:1px 5px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#f7a06a; }}
</style>
</head>
<body>
  <h1>Test 13 — Trajectory Evaluation</h1>
  <div class="meta">Judge: <b style="color:#d8d8e5">{escape(judge_model)}</b> &nbsp;|&nbsp; Cases: <b style="color:#d8d8e5">{total}</b> &nbsp;|&nbsp; Generated: <b style="color:#d8d8e5">{timestamp}</b></div>
  <div class="note">Test 13 uses a judge model to score each Test 12 trajectory on four independent dimensions: tool selection, argument quality, answer groundedness, and stop appropriateness. It does not re-run the agent — it reads the saved JSON trace and evaluates the quality of each decision in the trajectory.</div>
  {summary_cards}
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:24px">
    <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px 12px;text-align:center">
      <div style="font-size:20px;font-weight:800;color:#5dd6ff">{avg_tool}</div>
      <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-top:2px">Avg Tool Select</div>
    </div>
    <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px 12px;text-align:center">
      <div style="font-size:20px;font-weight:800;color:#a78bfa">{avg_args}</div>
      <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-top:2px">Avg Arg Quality</div>
    </div>
    <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px 12px;text-align:center">
      <div style="font-size:20px;font-weight:800;color:#6af7a0">{avg_ground}</div>
      <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-top:2px">Avg Groundedness</div>
    </div>
    <div style="background:#101016;border:1px solid #23232c;border-radius:10px;padding:10px 12px;text-align:center">
      <div style="font-size:20px;font-weight:800;color:#f0c040">{avg_stop}</div>
      <div style="font-size:10px;color:#8a8aa0;letter-spacing:1px;text-transform:uppercase;margin-top:2px">Avg Stop Timing</div>
    </div>
  </div>
  <h2>Per-Case Judge Scores</h2>
  {''.join(rows)}
  <footer style="margin-top:40px;padding-top:14px;border-top:1px solid #2a2a32;font-size:11px;color:#8a8aa0;font-family:'JetBrains Mono',monospace">
    Test 13 · Judge: {escape(judge_model)} · {total} trajectories scored · output: trajectory_evaluation_results.json
  </footer>
</body>
</html>'''

    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "trajectory_evaluation_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    return report_path
