"""
report_generator.py — HTML Report for RAG Evaluation
Dark theme. Called by rag_evaluator.py after all cases complete.
Output: results/rag_evaluation_report.html
"""

from pathlib import Path
from datetime import datetime


def generate_report(results, config, results_dir: Path) -> Path:

    bot_model   = config.get("BOT_MODEL", "unknown")
    judge_model = config.get("JUDGE_MODEL", "unknown")
    timestamp   = datetime.now().strftime("%d %b %Y %H:%M")
    total       = len(results)

    # ── Aggregate scores ──────────────────────────────────────────────────────
    avg_ctx   = sum(r["context_relevance"]   for r in results) / total
    avg_faith = sum(r["answer_faithfulness"] for r in results) / total
    avg_rel   = sum(r["answer_relevance"]    for r in results) / total
    overall   = (avg_ctx + avg_faith + avg_rel) / 3

    # ── Category breakdown ────────────────────────────────────────────────────
    from collections import defaultdict
    cat_data = defaultdict(list)
    for r in results:
        cat_data[r["category"]].append(r)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def score_colour(score):
        if score >= 0.7: return "#4caf80"
        if score >= 0.4: return "#f0c040"
        return "#e05050"

    def bar(score):
        pct = int(score * 100)
        c = score_colour(score)
        return f'''<div style="display:flex;align-items:center;gap:8px;">
          <div style="background:#2a2a2a;border-radius:4px;height:10px;width:120px">
            <div style="background:{c};width:{pct}%;height:10px;border-radius:4px"></div>
          </div>
          <span style="color:{c};font-weight:600;font-size:0.85rem">{pct}%</span>
        </div>'''

    # ── Summary score cards ───────────────────────────────────────────────────
    def score_card(label, score, desc):
        c = score_colour(score)
        pct = int(score * 100)
        return f'''<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;padding:1rem 1.2rem;flex:1;min-width:140px">
          <div style="font-size:1.8rem;font-weight:700;color:{c};margin-bottom:4px">{pct}%</div>
          <div style="color:#b0c4de;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">{label}</div>
          <div style="color:#666;font-size:0.78rem">{desc}</div>
        </div>'''

    cards_html = f'''<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:2rem">
      {score_card("Overall", overall, f"{total} cases · 3 metrics")}
      {score_card("Context Relevance", avg_ctx, "Retriever pulled right chunks?")}
      {score_card("Answer Faithfulness", avg_faith, "Answer grounded in context?")}
      {score_card("Answer Relevance", avg_rel, "Answer addresses the question?")}
    </div>'''

    # ── Category rows ─────────────────────────────────────────────────────────
    cat_rows = ""
    for cat in sorted(cat_data.keys()):
        items = cat_data[cat]
        c_avg = sum(r["context_relevance"]   for r in items) / len(items)
        f_avg = sum(r["answer_faithfulness"] for r in items) / len(items)
        r_avg = sum(r["answer_relevance"]    for r in items) / len(items)
        ov    = (c_avg + f_avg + r_avg) / 3
        c = score_colour(ov)
        cat_rows += f"""<tr>
          <td style="color:#ccc;font-weight:600">{cat}</td>
          <td style="color:#888;font-size:0.82rem;text-align:center">{len(items)}</td>
          <td>{bar(c_avg)}</td>
          <td>{bar(f_avg)}</td>
          <td>{bar(r_avg)}</td>
          <td style="color:{c};font-weight:700;text-align:center">{int(ov*100)}%</td>
        </tr>"""

    # ── Per-case rows ─────────────────────────────────────────────────────────
    case_rows = ""
    for r in results:
        ctx_c   = score_colour(r["context_relevance"])
        faith_c = score_colour(r["answer_faithfulness"])
        rel_c   = score_colour(r["answer_relevance"])
        avg     = (r["context_relevance"] + r["answer_faithfulness"] + r["answer_relevance"]) / 3
        avg_c   = score_colour(avg)

        chunks_html = ""
        for c in r.get("retrieved_chunks", []):
            chunks_html += f'<div style="color:#555;font-size:0.75rem;font-family:monospace">chunk {c["id"]} [{c["score"]}] {c["source"]}</div>'

        ctx_reason   = r.get("context_relevance_reason", "")[:120]
        faith_reason = r.get("answer_faithfulness_reason", "")[:120]

        answer_safe = r["answer"].replace("<", "&lt;").replace(">", "&gt;")

        case_rows += f"""<tr>
          <td style="color:#888;font-size:0.78rem;font-family:monospace;white-space:nowrap">{r['tc_id']}</td>
          <td>
            <div style="color:#ccc;font-size:0.85rem;margin-bottom:4px">{r['question']}</div>
            <span style="color:#888;font-size:0.75rem">{r['category']}</span>
          </td>
          <td>
            <div style="color:#bbb;font-size:0.82rem;margin-bottom:6px">{answer_safe}</div>
            {chunks_html}
          </td>
          <td>
            <div style="color:{ctx_c};font-weight:600;font-size:0.85rem;margin-bottom:4px">{int(r['context_relevance']*100)}%</div>
            <div style="color:#555;font-size:0.75rem">{ctx_reason}</div>
          </td>
          <td>
            <div style="color:{faith_c};font-weight:600;font-size:0.85rem;margin-bottom:4px">{int(r['answer_faithfulness']*100)}%</div>
            <div style="color:#555;font-size:0.75rem">{faith_reason}</div>
          </td>
          <td>
            <div style="color:{rel_c};font-weight:600;font-size:0.85rem">{int(r['answer_relevance']*100)}%</div>
          </td>
          <td style="text-align:center;color:{avg_c};font-weight:700">{int(avg*100)}%</td>
        </tr>"""

    # ── HTML ──────────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test 9 — RAG Evaluation</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#121212; color:#e0e0e0; font-family:'Segoe UI',sans-serif; padding:2rem; line-height:1.6; }}
  h1 {{ color:#e8c96a; font-size:1.6rem; margin-bottom:0.25rem; }}
  h2 {{ color:#b0c4de; font-size:1.1rem; margin:2rem 0 0.75rem; border-bottom:1px solid #333; padding-bottom:0.4rem; }}
  .meta {{ color:#888; font-size:0.85rem; margin-bottom:2rem; }}
  table {{ width:100%; border-collapse:collapse; margin-bottom:1.5rem; font-size:0.88rem; }}
  th {{ background:#1e1e1e; color:#b0c4de; text-align:left; padding:0.6rem 0.8rem; border-bottom:2px solid #333; }}
  td {{ padding:0.55rem 0.8rem; border-bottom:1px solid #222; vertical-align:top; }}
  tr:hover td {{ background:#1a1a1a; }}
  .insight {{ background:#1a2030; border-left:3px solid #e8c96a; padding:0.75rem 1rem; border-radius:4px; margin:1.5rem 0; color:#ccc; font-size:0.88rem; }}
  .insight b {{ color:#e8c96a; }}
</style>
</head>
<body>

<h1>Test 9 — RAG Evaluation</h1>
<div class="meta">
  Bot: <b style="color:#ccc">{bot_model}</b> &nbsp;|&nbsp;
  Judge: <b style="color:#ccc">{judge_model}</b> &nbsp;|&nbsp;
  Cases: <b style="color:#ccc">{total}</b> &nbsp;|&nbsp;
  Generated: <b style="color:#ccc">{timestamp}</b>
</div>

<h2>Overall Scores</h2>
{cards_html}

<div class="insight">
  <b>How scoring works:</b>
  <b>Context Relevance</b> — {judge_model} judges whether retrieved chunks contain what's needed to answer.
  <b>Answer Faithfulness</b> — {judge_model} judges whether the answer stays within the retrieved context or invents information.
  <b>Answer Relevance</b> — keyword matching against expected keywords from the test cases.
  All scores: 0% / 50% / 100%.
</div>

<h2>Results by Category</h2>
<table>
  <thead><tr>
    <th>Category</th><th style="text-align:center">Cases</th>
    <th>Context Relevance</th><th>Answer Faithfulness</th><th>Answer Relevance</th>
    <th style="text-align:center">Avg</th>
  </tr></thead>
  <tbody>{cat_rows}</tbody>
</table>

<h2>Per-Case Results</h2>
<table>
  <thead><tr>
    <th>ID</th><th>Question</th><th>Answer + Chunks</th>
    <th>Context Rel.</th><th>Faithfulness</th><th>Relevance</th><th style="text-align:center">Avg</th>
  </tr></thead>
  <tbody>{case_rows}</tbody>
</table>

</body>
</html>"""

    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "rag_evaluation_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
