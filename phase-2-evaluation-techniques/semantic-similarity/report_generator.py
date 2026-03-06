from datetime import datetime


def badge_colour(verdict):
    return {"Pass": "#43a047", "Partial": "#fb8c00", "Fail": "#e53935"}[verdict]


def score_bg(verdict):
    return {"Pass": "#1b2e1b", "Partial": "#2e2510", "Fail": "#2e1515"}[verdict]


def generate(results, passed, partial, failed, total, run_time, output_path):
    pass_pct    = round(100 * passed  / total) if total else 0
    partial_pct = round(100 * partial / total) if total else 0
    fail_pct    = round(100 * failed  / total) if total else 0

    rows_html = ""
    for r in results:
        badge_col = badge_colour(r["verdict"])
        score_col = score_bg(r["verdict"])
        rows_html += f"""
        <div class="case-card">

            <div class="case-header">
                <span class="tc-id">{r["id"]}</span>
                <span class="tc-summary">{r["summary"]}</span>
                <span class="badge" style="background:{badge_col}">{r["verdict"]}</span>
            </div>

            <div class="meta-row">
                <span class="lbl">Category:</span> {r["category"]}
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <span class="lbl">Prerequisite:</span> {r["prerequisite"]}
            </div>

            <div class="meta-row">
                <span class="lbl">Prompt:</span> <em>{r["prompt"]}</em>
            </div>

            <div class="score-row" style="background:{score_col}">
                <span class="lbl">Similarity Score:</span>
                <strong>{r["score"]}</strong>
                &nbsp;&nbsp;→&nbsp;&nbsp;
                <span class="meaning">{r["meaning"]}</span>
            </div>

            <div class="compare-grid">
                <div class="compare-box">
                    <div class="box-label expected-lbl">Expected Answer</div>
                    <div class="box-content">{r["expected"]}</div>
                </div>
                <div class="compare-box">
                    <div class="box-label actual-lbl">Bot Response</div>
                    <div class="box-content">{r["response"]}</div>
                </div>
            </div>

        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Semantic Similarity Report — Healthcare Bot</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; padding: 30px; }}

  .notice {{
    background: #2a2000; border-left: 5px solid #f0ad4e;
    padding: 14px 18px; margin-bottom: 28px; border-radius: 4px;
  }}
  .notice strong {{ display: block; font-size: 15px; margin-bottom: 4px; color: #f0ad4e; }}
  .notice p {{ font-size: 13px; color: #aaa; }}
  .notice code {{ background: #333; padding: 1px 6px; border-radius: 3px; color: #f0ad4e; }}

  h1 {{ font-size: 24px; color: #90caf9; margin-bottom: 4px; }}
  .run-meta {{ font-size: 12px; color: #666; margin-bottom: 28px; }}

  .summary-bar {{
    display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 36px;
  }}
  .summary-card {{
    background: #1e1e1e; border-radius: 8px; padding: 18px 28px;
    min-width: 150px; box-shadow: 0 1px 6px rgba(0,0,0,0.4); text-align: center;
    border: 1px solid #2a2a2a;
  }}
  .summary-card .num {{ font-size: 36px; font-weight: bold; }}
  .summary-card .s-lbl {{ font-size: 12px; color: #777; margin-top: 4px; }}
  .num.green {{ color: #43a047; }}
  .num.orange {{ color: #fb8c00; }}
  .num.red {{ color: #e53935; }}
  .num.blue {{ color: #90caf9; }}

  .section-title {{
    font-size: 16px; font-weight: bold; color: #90caf9;
    margin-bottom: 16px; border-bottom: 2px solid #90caf9; padding-bottom: 6px;
  }}

  .case-card {{
    background: #1e1e1e; border-radius: 8px; margin-bottom: 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.4); overflow: hidden;
    border: 1px solid #2a2a2a;
  }}

  .case-header {{
    display: flex; align-items: center; gap: 12px;
    padding: 14px 18px; background: #1a1f2e; border-bottom: 1px solid #2a2a2a;
    flex-wrap: wrap;
  }}
  .tc-id {{
    font-weight: bold; font-size: 13px; color: #90caf9;
    background: #1a2a40; padding: 3px 10px; border-radius: 12px; white-space: nowrap;
    border: 1px solid #2a4a70;
  }}
  .tc-summary {{ flex: 1; font-size: 14px; font-weight: 600; color: #e0e0e0; }}
  .badge {{
    color: #fff; font-size: 12px; font-weight: bold;
    padding: 4px 14px; border-radius: 12px; white-space: nowrap;
  }}

  .meta-row {{
    padding: 8px 18px; font-size: 13px; color: #aaa;
    border-bottom: 1px solid #2a2a2a;
  }}
  .lbl {{ font-weight: bold; color: #ccc; }}

  .score-row {{
    padding: 10px 18px; font-size: 14px;
    border-bottom: 1px solid #2a2a2a; color: #e0e0e0;
  }}
  .meaning {{ color: #aaa; font-style: italic; }}

  .compare-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
  }}
  .compare-box {{
    padding: 14px 18px; border-right: 1px solid #2a2a2a;
  }}
  .compare-box:last-child {{ border-right: none; }}
  .box-label {{
    font-size: 11px; font-weight: bold; text-transform: uppercase;
    letter-spacing: 0.5px; margin-bottom: 8px;
  }}
  .expected-lbl {{ color: #64b5f6; }}
  .actual-lbl {{ color: #ce93d8; }}
  .box-content {{ font-size: 13px; line-height: 1.6; color: #ccc; }}

  @media (max-width: 700px) {{
    .compare-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

  <div class="notice">
    <strong>⚠ This report is auto-generated on every script execution</strong>
    <p>Each time you run <code>test6_semantic_similarity.py</code> this file is overwritten with the latest results.
    If you want to keep a snapshot, rename this file before running the script again.</p>
  </div>

  <h1>Semantic Similarity Evaluation Report</h1>
  <p class="run-meta">
    Bot: City General Hospital Healthcare Bot &nbsp;|&nbsp;
    Model: llama3.1:8b &nbsp;|&nbsp;
    Thresholds: Pass ≥ 0.80 &nbsp;|&nbsp; Partial 0.60–0.79 &nbsp;|&nbsp; Fail &lt; 0.60
    <br>Generated: {run_time}
  </p>

  <div class="summary-bar">
    <div class="summary-card">
      <div class="num blue">{total}</div>
      <div class="s-lbl">Total Cases</div>
    </div>
    <div class="summary-card">
      <div class="num green">{passed} ({pass_pct}%)</div>
      <div class="s-lbl">Pass</div>
    </div>
    <div class="summary-card">
      <div class="num orange">{partial} ({partial_pct}%)</div>
      <div class="s-lbl">Partial</div>
    </div>
    <div class="summary-card">
      <div class="num red">{failed} ({fail_pct}%)</div>
      <div class="s-lbl">Fail</div>
    </div>
  </div>

  <div class="section-title">Test Case Results</div>
  {rows_html}

</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)