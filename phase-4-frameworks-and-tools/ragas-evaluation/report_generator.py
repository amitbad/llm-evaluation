import os
from datetime import datetime


CAT_CLASS = {
    "Single Document — Clean":   "cat-clean",
    "Single Document — Numbers": "cat-numbers",
    "Cross-Document":            "cat-cross",
    "Adversarial / Confused":    "cat-adv",
    "Unanswerable":              "cat-unans",
    "Negative / Boundary / Edge":"cat-edge",
    "Retrieval Confusion":       "cat-ret",
}

def colour(val):
    """Return CSS class for a 0–1 score."""
    if val is None:
        return "warn"
    if val >= 0.75:
        return "pass"
    if val >= 0.50:
        return "warn"
    return "fail"

def pct(val):
    if val is None:
        return "—"
    return f"{val:.0%}"

def score_bar(val):
    """Small inline bar for visual scanning."""
    if val is None:
        return ""
    w = int(val * 60)
    col = "#4ade80" if val >= 0.75 else ("#fbbf24" if val >= 0.5 else "#f87171")
    return f'<span style="display:inline-block;width:{w}px;height:6px;background:{col};border-radius:3px;vertical-align:middle;margin-left:6px;"></span>'


def generate_report(results, summary, output_dir):
    now       = datetime.now().strftime("%Y-%m-%d %H:%M")
    total     = summary["total"]
    avg_cp    = summary["avg_context_precision"]
    avg_f     = summary["avg_faithfulness"]
    avg_ar    = summary["avg_answer_relevancy"]
    avg_ov    = summary["avg_overall"]

    # ── Per-category averages ─────────────────────────────────────────────────
    cat_data = {}
    for r in results:
        cat = r["category"]
        if cat not in cat_data:
            cat_data[cat] = {"cp": [], "f": [], "ar": [], "ov": []}
        cat_data[cat]["cp"].append(r["context_precision"] or 0)
        cat_data[cat]["f"].append(r["faithfulness"]      or 0)
        cat_data[cat]["ar"].append(r["answer_relevancy"]  or 0)
        cat_data[cat]["ov"].append(r["overall"]           or 0)

    cat_rows = ""
    for cat, vals in cat_data.items():
        n    = len(vals["cp"])
        c_cp = round(sum(vals["cp"]) / n, 3)
        c_f  = round(sum(vals["f"])  / n, 3)
        c_ar = round(sum(vals["ar"]) / n, 3)
        c_ov = round(sum(vals["ov"]) / n, 3)
        cls  = CAT_CLASS.get(cat, "")
        cat_rows += f"""
        <tr>
          <td><span class="cat-tag {cls}">{cat}</span></td>
          <td style="text-align:center">{n}</td>
          <td class="{colour(c_cp)}">{pct(c_cp)}{score_bar(c_cp)}</td>
          <td class="{colour(c_f)}">{pct(c_f)}{score_bar(c_f)}</td>
          <td class="{colour(c_ar)}">{pct(c_ar)}{score_bar(c_ar)}</td>
          <td class="{colour(c_ov)}" style="font-weight:700">{pct(c_ov)}{score_bar(c_ov)}</td>
        </tr>"""

    # ── Per-case rows ─────────────────────────────────────────────────────────
    case_rows = ""
    for r in results:
        cls = CAT_CLASS.get(r["category"], "")
        case_rows += f"""
        <tr>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{r['tc_id']}</td>
          <td>{r['question']}</td>
          <td><span class="cat-tag {cls}">{r['category']}</span></td>
          <td class="{colour(r['context_precision'])}">{pct(r['context_precision'])}{score_bar(r['context_precision'])}</td>
          <td class="{colour(r['faithfulness'])}">{pct(r['faithfulness'])}{score_bar(r['faithfulness'])}</td>
          <td class="{colour(r['answer_relevancy'])}">{pct(r['answer_relevancy'])}{score_bar(r['answer_relevancy'])}</td>
          <td class="{colour(r['overall'])}" style="font-weight:700">{pct(r['overall'])}{score_bar(r['overall'])}</td>
        </tr>"""

    # ── Comparison table (Test 9 hand-rolled vs RAGAS) ────────────────────────
    # Test 9 results from CONTEXT.md — hardcoded for comparison
    test9 = {
        "Context Relevance / Precision":  0.84,
        "Answer Faithfulness":            1.00,
        "Answer Relevance":               0.66,
        "Overall":                        0.83,
    }
    ragas_vals = {
        "Context Relevance / Precision":  avg_cp,
        "Answer Faithfulness":            avg_f,
        "Answer Relevance":               avg_ar,
        "Overall":                        avg_ov,
    }
    compare_rows = ""
    for metric in test9:
        t9  = test9[metric]
        rg  = ragas_vals[metric]
        diff = rg - t9
        diff_str  = f"+{diff:.0%}" if diff > 0 else f"{diff:.0%}"
        diff_col  = "pass" if diff > 0.02 else ("fail" if diff < -0.02 else "warn")
        bold = 'style="font-weight:700"' if metric == "Overall" else ""
        compare_rows += f"""
        <tr>
          <td {bold}>{metric}</td>
          <td class="warn" {bold}>{pct(t9)}</td>
          <td class="{colour(rg)}" {bold}>{pct(rg)}</td>
          <td class="{diff_col}" {bold}>{diff_str}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RAGAS Evaluation Report</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:#0d0d0f; --surface:#141417; --surface2:#1c1c21; --border:#2a2a32;
      --accent:#7c6af7; --accent2:#f7a06a; --danger:#f76a6a; --success:#6af7a0;
      --text:#e8e8f0; --muted:#7a7a90;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Syne',sans-serif; background:var(--bg); color:var(--text); padding:48px 56px; max-width:100%; line-height:1.6; }}
    .phase-badge {{ display:inline-block; font-size:10px; font-family:'JetBrains Mono',monospace; color:var(--accent); letter-spacing:3px; text-transform:uppercase; margin-bottom:10px; }}
    h1 {{ font-size:36px; font-weight:800; line-height:1.1; margin-bottom:10px; background:linear-gradient(135deg,var(--text) 40%,var(--accent)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
    .subtitle {{ color:var(--muted); font-size:14px; margin-bottom:40px; line-height:1.7; max-width:680px; }}
    h2 {{ font-size:20px; font-weight:700; color:var(--text); margin:40px 0 12px; padding-bottom:8px; border-bottom:1px solid var(--border); }}
    h3 {{ font-size:16px; font-weight:700; color:var(--accent); margin:28px 0 10px; }}
    p {{ margin-bottom:14px; font-size:14px; color:#c0c0d8; line-height:1.75; }}
    code {{ background:var(--surface2); padding:2px 7px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:12px; color:var(--accent2); }}
    pre {{ background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:16px 18px; font-family:'JetBrains Mono',monospace; font-size:12.5px; color:var(--accent2); margin:14px 0; overflow-x:auto; }}
    table {{ width:100%; border-collapse:collapse; margin:16px 0 24px; font-size:13px; }}
    th {{ background:var(--surface2); color:var(--muted); font-size:10px; font-family:'JetBrains Mono',monospace; letter-spacing:1px; text-transform:uppercase; padding:10px 13px; text-align:left; border:1px solid var(--border); font-weight:600; }}
    td {{ padding:11px 13px; border:1px solid var(--border); color:var(--text); vertical-align:top; background:var(--surface); font-size:13px; line-height:1.6; }}
    tr:hover td {{ background:var(--surface2); }}
    .info-box {{ background:var(--surface); border:1px solid var(--border); border-left:3px solid var(--accent); border-radius:10px; padding:14px 18px; margin:16px 0; font-size:13.5px; line-height:1.7; color:var(--text); }}
    .warn-box {{ background:#1a1a10; border:1px solid #3a3a20; border-left:3px solid var(--accent2); border-radius:10px; padding:14px 18px; margin:16px 0; font-size:13.5px; line-height:1.7; color:#c8c890; }}
    .danger-box {{ background:#1a1010; border:1px solid #3a2020; border-left:3px solid var(--danger); border-radius:10px; padding:14px 18px; margin:16px 0; font-size:13.5px; line-height:1.7; color:#e0b0b0; }}
    .score-row {{ display:flex; gap:10px; flex-wrap:wrap; margin:16px 0; }}
    .score-card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px 18px; min-width:150px; flex:1; }}
    .score-card .score-val {{ font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:700; margin-bottom:4px; }}
    .score-card .score-label {{ font-size:10px; font-family:'JetBrains Mono',monospace; letter-spacing:1px; text-transform:uppercase; color:var(--muted); margin-bottom:4px; }}
    .score-card .score-sub {{ font-size:11px; color:var(--muted); }}
    .pass {{ color:#4ade80; }} .fail {{ color:#f87171; }} .warn {{ color:#fbbf24; }}
    .cat-tag {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; white-space:nowrap; }}
    .cat-clean   {{ background:#0d2010; color:#4ade80; }}
    .cat-numbers {{ background:#1a102a; color:#a78bfa; }}
    .cat-cross   {{ background:#2a2a0a; color:#fbbf24; }}
    .cat-unans   {{ background:#2a0a0a; color:#f87171; }}
    .cat-adv     {{ background:#2a1a0a; color:#fb923c; }}
    .cat-edge    {{ background:#0a0a2a; color:#60a5fa; }}
    .cat-ret     {{ background:#0a2a2a; color:#2dd4bf; }}
    footer {{ margin-top:64px; padding-top:20px; border-top:1px solid var(--border); font-size:11px; color:var(--muted); font-family:'JetBrains Mono',monospace; }}
    ::-webkit-scrollbar {{ width:6px; }} ::-webkit-scrollbar-track {{ background:var(--bg); }} ::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:3px; }}
  </style>
</head>
<body>

<div class="phase-badge">Phase 4 — Frameworks &amp; Tools</div>
<h1>RAGAS Evaluation<br>Report</h1>
<p class="subtitle">
  Same 25 test cases as Test 9. Same RAG bot (<code>llama3.1:8b</code> via Ollama).<br>
  Scoring via RAGAS framework using <code>gpt-4o-mini</code> as judge.<br>
  Generated: {now}
</p>

<h2>Overall Scores</h2>
<div class="score-row">
  <div class="score-card">
    <div class="score-label">Context Precision</div>
    <div class="score-val {colour(avg_cp)}">{pct(avg_cp)}</div>
    <div class="score-sub">Was retrieved context relevant?</div>
  </div>
  <div class="score-card">
    <div class="score-label">Faithfulness</div>
    <div class="score-val {colour(avg_f)}">{pct(avg_f)}</div>
    <div class="score-sub">Is answer grounded in context?</div>
  </div>
  <div class="score-card">
    <div class="score-label">Answer Relevancy</div>
    <div class="score-val {colour(avg_ar)}">{pct(avg_ar)}</div>
    <div class="score-sub">Does answer address the question?</div>
  </div>
  <div class="score-card" style="border-color:var(--accent)">
    <div class="score-label">Overall</div>
    <div class="score-val {colour(avg_ov)}">{pct(avg_ov)}</div>
    <div class="score-sub">Average of three metrics</div>
  </div>
</div>

<h2>RAGAS vs Test 9 — Side by Side</h2>
<div class="info-box">
  Both evaluations ran on the same 25 questions using the same RAG bot. The difference is in
  how each metric is computed. Test 9 used a hand-rolled LLM judge (Mistral, Ollama) with keyword
  matching for answer relevance. RAGAS uses <code>gpt-4o-mini</code> with its own internal
  claim-extraction and embedding-based scoring pipeline.
</div>
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Test 9 (Hand-rolled)</th>
      <th>RAGAS (gpt-4o-mini)</th>
      <th>Difference</th>
    </tr>
  </thead>
  <tbody>{compare_rows}</tbody>
</table>

<h2>How RAGAS Computes Each Metric</h2>
<p>Understanding <em>how</em> RAGAS scores differs from your Test 9 approach explains why the numbers above differ.</p>

<h3>Context Precision</h3>
<p>RAGAS asks: of the chunks retrieved, how many were actually useful for answering the question?
It uses the LLM to judge relevance per chunk and weights by rank — a relevant chunk at position 1
scores higher than one at position 3. Your Test 9 context relevance scored the full context block
as a whole (0 or 1), not chunk-by-chunk.</p>

<h3>Faithfulness</h3>
<p>RAGAS breaks the answer into individual claims, then checks each claim against the context separately.
A five-sentence answer produces five separate verdicts. Your Test 9 faithfulness judge scored the
whole answer at once on a 0–3 rubric. The claim-level approach is harder to fool — a single hallucinated
sentence in an otherwise correct answer will reduce the score proportionally.</p>

<h3>Answer Relevancy</h3>
<p>This is the biggest methodological difference. RAGAS does not use keywords at all. Instead it
generates 3–5 synthetic questions from the answer, then measures cosine similarity between those
synthetic questions and the original question. A high-relevancy answer is one where the synthetic
questions closely match the original. Your Test 9 used keyword matching — which is why TC18
(correct refusal) scored 0% there but should score higher here, since RAGAS evaluates meaning
not word presence.</p>

<h2>Results by Category</h2>
<table>
  <thead>
    <tr>
      <th>Category</th>
      <th style="text-align:center">Cases</th>
      <th>Context Precision</th>
      <th>Faithfulness</th>
      <th>Answer Relevancy</th>
      <th>Overall</th>
    </tr>
  </thead>
  <tbody>{cat_rows}</tbody>
</table>

<h2>All 25 Cases</h2>
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Question</th>
      <th>Category</th>
      <th>Context Precision</th>
      <th>Faithfulness</th>
      <th>Answer Relevancy</th>
      <th>Overall</th>
    </tr>
  </thead>
  <tbody>{case_rows}</tbody>
</table>

<h2>What to Look For</h2>
<p>When reading these results, the comparison with Test 9 is more valuable than the raw numbers.
Focus on cases where RAGAS and Test 9 disagree significantly — those disagreements reveal what
each scoring method is actually measuring.</p>

<p><strong style="color:var(--accent2)">Answer Relevancy on refusal cases (TC18, TC19).</strong>
Your Test 9 keyword matching scored these near 0% because the bot's refusal wording didn't match
expected keywords. Check whether RAGAS scores them higher — it should, because the bot's refusal
is semantically consistent with an out-of-scope question.</p>

<p><strong style="color:var(--accent2)">Faithfulness on TC21 (Gold Loan age 86).</strong>
Your Test 9 faithfulness scored TC21 at 100% despite the answer being wrong. Does RAGAS catch it?
Probably not either — the reasoning failure is subtle. Both judges see the number 86 and the range
18–85 in context and answer, but neither verifies the logical conclusion drawn from them.</p>

<p><strong style="color:var(--accent2)">Context Precision on TC08 (cross-document).</strong>
Test 9 scored this at 50% context relevance. RAGAS context precision weights by rank — if the
irrelevant chunks were returned at positions 1 and 2, RAGAS will penalise more heavily than Test 9.</p>

<footer>
  phase-4-frameworks-and-tools/ragas-evaluation/results/ · RAGAS {total} cases · {now}
</footer>

</body>
</html>"""

    report_path = os.path.join(output_dir, "ragas_evaluation_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
