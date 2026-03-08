"""
report_generator.py — HTML Report for DeepEval RAG Evaluation (Test 11)
Dark theme. Called by test11_deepeval_evaluator.py after all cases complete.
Output: results/deepeval_report.html
"""

from pathlib import Path
from datetime import datetime


def generate_report(results, config, results_dir: Path) -> Path:

    bot_model   = config.get("BOT_MODEL", "unknown")
    judge_model = config.get("JUDGE_MODEL", "unknown")
    threshold   = config.get("THRESHOLD", 0.5)
    timestamp   = datetime.now().strftime("%d %b %Y %H:%M")
    total       = len(results)

    # ── Aggregate scores — exclude refusal cases (None scores) ───────────────
    scored   = [r for r in results if not r.get("is_refusal")]
    refusals = [r for r in results if r.get("is_refusal")]
    n_scored = len(scored)

    avg_ctx   = sum(r["context_relevance"]   for r in scored) / n_scored if n_scored else 0
    avg_faith = sum(r["answer_faithfulness"] for r in scored) / n_scored if n_scored else 0
    avg_rel   = sum(r["answer_relevance"]    for r in scored) / n_scored if n_scored else 0
    overall   = (avg_ctx + avg_faith + avg_rel) / 3

    ctx_passed   = sum(1 for r in scored if r["context_relevance"]   >= threshold)
    faith_passed = sum(1 for r in scored if r["answer_faithfulness"] >= threshold)
    rel_passed   = sum(1 for r in scored if r["answer_relevance"]    >= threshold)
    # overall case pass: all three metrics meet threshold
    n_passed = sum(
        1 for r in scored
        if r["context_relevance"] >= threshold
        and r["answer_faithfulness"] >= threshold
        and r["answer_relevance"] >= threshold
    )

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

    def verdict_badge(passed):
        if passed:
            return '<span style="background:#1a3a2a;color:#4caf80;font-size:0.72rem;font-weight:700;padding:2px 7px;border-radius:10px;font-family:monospace">PASS</span>'
        return '<span style="background:#3a1a1a;color:#e05050;font-size:0.72rem;font-weight:700;padding:2px 7px;border-radius:10px;font-family:monospace">FAIL</span>'

    def metric_cell(score, reason):
        passed = score >= threshold
        badge  = verdict_badge(passed)
        colour = score_colour(score)
        pct    = int(round(score * 100))
        reason_safe = str(reason or "")[:140]
        return (f'<div style="margin-bottom:4px">{badge}</div>'
                f'<div style="color:{colour};font-weight:600;font-size:0.85rem;margin-bottom:4px">{pct}%</div>'
                f'<div style="color:#555;font-size:0.73rem">{reason_safe}</div>')

    # ── Summary score cards ───────────────────────────────────────────────────
    def score_card(label, avg, pass_count, denom, desc):
        c   = score_colour(avg)
        pct = int(round(avg * 100))
        pp  = int(pass_count / denom * 100) if denom else 0
        return (f'<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;padding:1rem 1.2rem;flex:1;min-width:150px">'
                f'<div style="font-size:1.8rem;font-weight:700;color:{c};margin-bottom:2px">{pct}%</div>'
                f'<div style="font-size:0.8rem;color:#4caf80;margin-bottom:4px">&#x2713; {pass_count}/{denom} passed ({pp}%)</div>'
                f'<div style="color:#b0c4de;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">{label}</div>'
                f'<div style="color:#666;font-size:0.78rem">{desc}</div>'
                f'</div>')

    cards_html = ('<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:2rem">'
        + score_card("Overall",          overall,   n_passed,     total,    f"{total} cases · threshold {threshold}")
        + score_card("Context Relevance", avg_ctx,  ctx_passed,   n_scored, "Retriever pulled right chunks?")
        + score_card("Faithfulness",      avg_faith, faith_passed, n_scored, "Answer grounded in context?")
        + score_card("Answer Relevance",  avg_rel,   rel_passed,   n_scored, "Answer addresses the question?")
        + '</div>')

    # ── Category rows ─────────────────────────────────────────────────────────
    cat_rows = ""
    for cat in sorted(cat_data.keys()):
        items   = cat_data[cat]
        s_items = [r for r in items if not r.get("is_refusal")]
        if not s_items:
            cat_rows += (f'<tr><td style="color:#ccc;font-weight:600">{cat}</td>'
                         f'<td style="color:#888;font-size:0.82rem;text-align:center">{len(items)}</td>'
                         f'<td colspan="5" style="color:#555;font-size:0.82rem;text-align:center">All refusals — not scored</td></tr>')
            continue
        c_avg  = sum(r["context_relevance"]   for r in s_items) / len(s_items)
        f_avg  = sum(r["answer_faithfulness"] for r in s_items) / len(s_items)
        r_avg  = sum(r["answer_relevance"]    for r in s_items) / len(s_items)
        ov     = (c_avg + f_avg + r_avg) / 3
        passed = sum(1 for r in s_items
                     if r["context_relevance"] >= threshold
                     and r["answer_faithfulness"] >= threshold
                     and r["answer_relevance"] >= threshold)
        c_ov = score_colour(ov)
        c_c  = score_colour(c_avg)
        c_f  = score_colour(f_avg)
        c_r  = score_colour(r_avg)
        cat_rows += (f'<tr>'
                     f'<td style="color:#ccc;font-weight:600">{cat}</td>'
                     f'<td style="color:#888;font-size:0.82rem;text-align:center">{len(items)}</td>'
                     f'<td style="color:#4caf80;text-align:center">{passed}/{len(s_items)}</td>'
                     f'<td style="color:{c_c};text-align:center">{int(round(c_avg*100))}%</td>'
                     f'<td style="color:{c_f};text-align:center">{int(round(f_avg*100))}%</td>'
                     f'<td style="color:{c_r};text-align:center">{int(round(r_avg*100))}%</td>'
                     f'<td style="color:{c_ov};font-weight:700;text-align:center">{int(round(ov*100))}%</td>'
                     f'</tr>')

    # ── Per-case rows ─────────────────────────────────────────────────────────
    case_rows = ""
    for r in results:
        is_refusal = r.get("is_refusal", False)

        chunks_html = ""
        for ch in r.get("retrieved_chunks", []):
            chunks_html += (f'<div style="color:#555;font-size:0.73rem;font-family:monospace;margin-top:2px">'
                            f'chunk {ch["id"]} [{ch["score"]}] {ch["source"]}</div>')

        answer_safe = (r["answer"]
                       .replace("&", "&amp;")
                       .replace("<", "&lt;")
                       .replace(">", "&gt;"))

        if is_refusal:
            tc_badge = ('<span style="background:#222;color:#777;font-size:0.72rem;font-weight:700;'
                        'padding:2px 7px;border-radius:10px;font-family:monospace">N/A</span>')
            ctx_td = faith_td = rel_td = '<td><div style="color:#555;font-size:0.82rem">⊘ Refusal — N/A</div></td>'
            avg_td = '<td style="text-align:center;color:#555;font-weight:700">N/A</td>'
            row_bg = ' style="background:#1e1515"'
        else:
            case_passed = (
                r["context_relevance"]   >= threshold and
                r["answer_faithfulness"] >= threshold and
                r["answer_relevance"]    >= threshold
            )
            tc_badge = verdict_badge(case_passed)
            row_bg   = '' if case_passed else ' style="background:#1e1515"'
            avg_score = (r["context_relevance"] + r["answer_faithfulness"] + r["answer_relevance"]) / 3
            avg_c     = score_colour(avg_score)
            ctx_td   = f'<td>{metric_cell(r["context_relevance"],   r.get("context_relevance_reason",   ""))}</td>'
            faith_td = f'<td>{metric_cell(r["answer_faithfulness"], r.get("answer_faithfulness_reason", ""))}</td>'
            rel_td   = f'<td>{metric_cell(r["answer_relevance"],    r.get("answer_relevance_reason",   ""))}</td>'
            avg_td   = f'<td style="text-align:center;color:{avg_c};font-weight:700">{int(round(avg_score*100))}%</td>'

        case_rows += (f'<tr{row_bg}>'
            f'<td style="color:#888;font-size:0.78rem;font-family:monospace;white-space:nowrap">'
            f'{r["tc_id"]}<br>{tc_badge}</td>'
            f'<td><div style="color:#ccc;font-size:0.85rem;margin-bottom:4px">{r["question"]}</div>'
            f'<span style="color:#888;font-size:0.75rem">{r["category"]}</span></td>'
            f'<td><div style="color:#bbb;font-size:0.82rem;margin-bottom:6px">{answer_safe}</div>{chunks_html}</td>'
            f'{ctx_td}{faith_td}{rel_td}{avg_td}'
            f'</tr>')

    # ── HTML ──────────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Test 11 — DeepEval RAG Evaluation</title>
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
  .insight {{ background:#1a2030; border-left:3px solid #e8c96a; padding:0.75rem 1rem; border-radius:4px; margin:1.5rem 0; color:#ccc; font-size:0.88rem; line-height:1.7; }}
  .insight b {{ color:#e8c96a; }}
</style>
</head>
<body>

<h1>Test 11 — DeepEval RAG Evaluation</h1>
<div class="meta">
  Bot: <b style="color:#ccc">{bot_model}</b> &nbsp;|&nbsp;
  Judge: <b style="color:#ccc">{judge_model}</b> &nbsp;|&nbsp;
  Framework: <b style="color:#ccc">DeepEval</b> &nbsp;|&nbsp;
  Threshold: <b style="color:#e8c96a">{threshold}</b> &nbsp;|&nbsp;
  Cases: <b style="color:#ccc">{total}</b> &nbsp;|&nbsp;
  Scored: <b style="color:#ccc">{n_scored}</b> &nbsp;|&nbsp;
  Refusals: <b style="color:#888">{len(refusals)}</b> &nbsp;|&nbsp;
  Generated: <b style="color:#ccc">{timestamp}</b>
</div>

<div class="insight">
  <b>What is different about this report.</b>
  Unlike Test 9 (hand-rolled scoring) and Test 10 (RAGAS), DeepEval produces a
  <b>PASS / FAIL verdict</b> per metric per case — not just a score.
  A case passes a metric when its score meets or exceeds the threshold ({threshold}).
  Rows with a red background failed at least one metric.
  This is the "unit test for LLMs" pattern: every case either passes or it doesn't.
  Reasons below each score are the judge's explanation for its verdict.
</div>

<h2>Overall Scores</h2>
{cards_html}

<div class="insight">
  <b>How DeepEval scores these metrics.</b>
  <b>ContextualRelevancy</b> — judge assesses whether the retrieved chunks contain enough information to answer the question.
  <b>Faithfulness</b> — judge checks whether each claim in the answer is supported by the retrieved context, or invented.
  <b>AnswerRelevancy</b> — judge checks whether the answer directly addresses what was asked.
  All three use <b>{judge_model}</b> as the judge via Ollama. Threshold: {threshold} — below this = FAIL.
</div>

<h2>Results by Category</h2>
<table>
  <thead><tr>
    <th>Category</th>
    <th style="text-align:center">Cases</th>
    <th style="text-align:center">Passed</th>
    <th style="text-align:center">Context Rel.</th>
    <th style="text-align:center">Faithfulness</th>
    <th style="text-align:center">Answer Rel.</th>
    <th style="text-align:center">Avg</th>
  </tr></thead>
  <tbody>{cat_rows}</tbody>
</table>

<h2>Per-Case Results</h2>
<table>
  <thead><tr>
    <th>ID</th><th>Question</th><th>Answer + Chunks</th>
    <th>Context Rel.</th><th>Faithfulness</th><th>Answer Rel.</th>
    <th style="text-align:center">Avg</th>
  </tr></thead>
  <tbody>{case_rows}</tbody>
</table>

</body>
</html>"""

    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "deepeval_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
