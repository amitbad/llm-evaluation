"""
report_generator.py — HTML Report for Temperature Sensitivity Testing
Dark theme. Called by temperature_evaluator.py after all runs complete.
"""

from pathlib import Path
from datetime import datetime


def generate_report(results, temperatures, model_name, results_dir: Path) -> Path:
    from temperature_evaluator import TestResult

    # ── Aggregate data ────────────────────────────────────────────────────────

    # Pass rate per temperature
    temp_stats = {}
    for t in temperatures:
        t_results = [r for r in results if r.temperature == t]
        passed = sum(1 for r in t_results if r.passed)
        total = len(t_results)
        avg_lat = sum(r.latency for r in t_results) / total if total else 0
        temp_stats[t] = {"passed": passed, "total": total, "avg_lat": avg_lat}

    # Category breakdown per temperature
    categories = sorted(set(r.case.category for r in results))

    cat_temp_stats = {}
    for cat in categories:
        cat_temp_stats[cat] = {}
        for t in temperatures:
            t_cat = [r for r in results if r.temperature == t and r.case.category == cat]
            passed = sum(1 for r in t_cat if r.passed)
            cat_temp_stats[cat][t] = {"passed": passed, "total": len(t_cat)}

    # Per-case results across all temperatures
    test_cases = sorted(set((r.case.id, r.case.summary, r.case.category) for r in results))

    # ── Helper: colour for pass rate ─────────────────────────────────────────
    def rate_colour(passed, total):
        if total == 0:
            return "#666"
        pct = passed / total * 100
        if pct == 100:
            return "#4caf80"
        elif pct >= 75:
            return "#f0c040"
        elif pct >= 50:
            return "#e08030"
        else:
            return "#e05050"

    def pass_badge(passed, total):
        colour = rate_colour(passed, total)
        pct = round(passed / total * 100) if total else 0
        return f'<span style="color:{colour};font-weight:600">{passed}/{total} ({pct}%)</span>'

    # ── Summary table rows ────────────────────────────────────────────────────
    summary_rows = ""
    for t in temperatures:
        s = temp_stats[t]
        pct = round(s["passed"] / s["total"] * 100) if s["total"] else 0
        colour = rate_colour(s["passed"], s["total"])
        bar_width = pct
        label = {0.0: "Deterministic", 0.5: "Slightly relaxed",
                 1.0: "Default / balanced", 1.5: "Loosely bound"}.get(t, "")
        summary_rows += f"""
        <tr>
          <td><span style="font-size:1.1rem;font-weight:700;color:#e8c96a">{t}</span></td>
          <td style="color:#aaa;font-size:0.85rem">{label}</td>
          <td style="color:{colour};font-weight:600">{s['passed']}/{s['total']}</td>
          <td style="color:{colour};font-weight:700">{pct}%</td>
          <td>
            <div style="background:#2a2a2a;border-radius:4px;height:14px;width:180px">
              <div style="background:{colour};width:{bar_width}%;height:14px;border-radius:4px;transition:width 0.3s"></div>
            </div>
          </td>
          <td style="color:#aaa">{s['avg_lat']:.2f}s</td>
        </tr>"""

    # ── Category breakdown rows ───────────────────────────────────────────────
    cat_rows = ""
    for cat in categories:
        cells = f'<td style="color:#ccc;font-weight:600">{cat}</td>'
        for t in temperatures:
            s = cat_temp_stats[cat][t]
            cells += f'<td>{pass_badge(s["passed"], s["total"])}</td>'
        cat_rows += f"<tr>{cells}</tr>"

    # ── Per-case detail rows ──────────────────────────────────────────────────
    case_rows = ""
    for case_id, summary, category in test_cases:
        cells = f'<td style="color:#aaa;font-size:0.8rem">#{case_id}</td>'
        cells += f'<td style="color:#ccc;font-size:0.85rem">{summary}</td>'
        cells += f'<td><span style="color:#888;font-size:0.75rem">{category}</span></td>'
        for t in temperatures:
            r = next((x for x in results if x.temperature == t and x.case.id == case_id), None)
            if r is None:
                cells += '<td>—</td>'
            elif r.passed:
                cells += '<td><span style="color:#4caf80;font-size:1rem">✅</span></td>'
            else:
                reason_short = r.failure_reason[:60] + "..." if len(r.failure_reason) > 60 else r.failure_reason
                cells += f'<td><span style="color:#e05050;font-size:1rem" title="{reason_short}">❌</span></td>'
        case_rows += f"<tr>{case_rows and '' or ''}{cells}</tr>"

    # Rebuild properly
    case_rows = ""
    for case_id, summary, category in test_cases:
        row = f'<td style="color:#aaa;font-size:0.8rem">#{case_id}</td>'
        row += f'<td style="color:#ccc;font-size:0.85rem">{summary}</td>'
        row += f'<td><span style="color:#888;font-size:0.75rem">{category}</span></td>'
        for t in temperatures:
            r = next((x for x in results if x.temperature == t and x.case.id == case_id), None)
            if r is None:
                row += '<td>—</td>'
            elif r.passed:
                row += '<td style="text-align:center"><span style="color:#4caf80">✅</span></td>'
            else:
                reason_short = r.failure_reason[:80].replace('"', "'")
                row += f'<td style="text-align:center"><span style="color:#e05050" title="{reason_short}">❌</span></td>'
        case_rows += f"<tr>{row}</tr>"

    # ── Temperature column headers ────────────────────────────────────────────
    temp_headers = "".join(f'<th>T={t}</th>' for t in temperatures)

    # ── Failures detail section ───────────────────────────────────────────────
    failures_html = ""
    for t in temperatures:
        failed = [r for r in results if r.temperature == t and not r.passed]
        if not failed:
            continue
        failures_html += f'<h3 style="color:#e8c96a;margin-top:2rem">Temperature {t} — {len(failed)} failure(s)</h3>'
        for r in failed:
            snippet = r.output[:300].replace("<", "&lt;").replace(">", "&gt;")
            failures_html += f"""
            <div style="background:#1e1e1e;border:1px solid #333;border-radius:6px;padding:1rem;margin-bottom:0.75rem">
              <div style="color:#ccc;font-weight:600;margin-bottom:0.4rem">#{r.case.id} — {r.case.summary}</div>
              <div style="color:#aaa;font-size:0.82rem;margin-bottom:0.3rem"><b>Prompt:</b> {r.case.prompt}</div>
              <div style="color:#e07070;font-size:0.82rem;margin-bottom:0.5rem"><b>Reason:</b> {r.failure_reason}</div>
              <div style="color:#777;font-size:0.8rem"><b>Output:</b> {snippet}{'...' if len(r.output) > 300 else ''}</div>
            </div>"""

    if not failures_html:
        failures_html = '<p style="color:#4caf80">No failures across any temperature setting.</p>'

    # ── HTML ──────────────────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")
    total_runs = len(results)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test 8 — Temperature Sensitivity</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding: 2rem; line-height: 1.6; }}
  h1 {{ color: #e8c96a; font-size: 1.6rem; margin-bottom: 0.25rem; }}
  h2 {{ color: #b0c4de; font-size: 1.1rem; margin: 2rem 0 0.75rem; border-bottom: 1px solid #333; padding-bottom: 0.4rem; }}
  h3 {{ color: #e8c96a; font-size: 1rem; }}
  .meta {{ color: #888; font-size: 0.85rem; margin-bottom: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.88rem; }}
  th {{ background: #1e1e1e; color: #b0c4de; text-align: left; padding: 0.6rem 0.8rem; border-bottom: 2px solid #333; }}
  td {{ padding: 0.55rem 0.8rem; border-bottom: 1px solid #222; vertical-align: middle; }}
  tr:hover td {{ background: #1a1a1a; }}
  .insight {{ background: #1a2030; border-left: 3px solid #e8c96a; padding: 0.75rem 1rem; border-radius: 4px; margin: 1.5rem 0; color: #ccc; font-size: 0.88rem; }}
  .insight b {{ color: #e8c96a; }}
</style>
</head>
<body>

<h1>Test 8 — Temperature Sensitivity Testing</h1>
<div class="meta">
  Model: <b style="color:#ccc">{model_name}</b> &nbsp;|&nbsp;
  Total runs: <b style="color:#ccc">{total_runs}</b> &nbsp;|&nbsp;
  Generated: <b style="color:#ccc">{timestamp}</b>
</div>

<h2>Pass Rate by Temperature</h2>
<table>
  <thead><tr>
    <th>Temperature</th><th>Behaviour</th><th>Passed</th><th>Pass Rate</th><th>Visual</th><th>Avg Latency</th>
  </tr></thead>
  <tbody>{summary_rows}</tbody>
</table>

<div class="insight">
  <b>Key insight:</b> As temperature increases, the model picks less probable words — 
  responses become more varied and creative but less reliably correct. 
  Factual tests (account_info, fees) degrade less than behavioural tests (off_topic, adversarial) 
  because numbers act as anchors while refusal is a trained behaviour sensitive to randomness.
</div>

<h2>Category Breakdown</h2>
<table>
  <thead><tr><th>Category</th>{temp_headers}</tr></thead>
  <tbody>{cat_rows}</tbody>
</table>

<h2>Per-Test Results (hover ❌ for failure reason)</h2>
<table>
  <thead><tr><th>#</th><th>Summary</th><th>Category</th>{temp_headers}</tr></thead>
  <tbody>{case_rows}</tbody>
</table>

<h2>Failure Details</h2>
{failures_html}

</body>
</html>"""

    report_path = results_dir / "temperature_sensitivity_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
