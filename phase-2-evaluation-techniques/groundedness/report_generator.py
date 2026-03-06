"""
report_generator.py — Test 7 Groundedness Scoring
Generates a dark-theme HTML report from groundedness evaluation results.
"""

from datetime import datetime


LABEL_CONFIG = {
    "GROUNDED":    {"color": "#4ade80", "bg": "rgba(74,222,128,0.08)",  "icon": "✓"},
    "PARTIAL":     {"color": "#fbbf24", "bg": "rgba(251,191,36,0.08)",  "icon": "~"},
    "UNGROUNDED":  {"color": "#f87171", "bg": "rgba(248,113,113,0.08)", "icon": "✗"},
    "PARSE_ERROR": {"color": "#a78bfa", "bg": "rgba(167,139,250,0.08)", "icon": "?"},
    "UNKNOWN":     {"color": "#94a3b8", "bg": "rgba(148,163,184,0.08)", "icon": "?"},
}


def score_bar_html(score: int) -> str:
    """Render a 3-pip score bar."""
    pips = []
    colors = {1: "#f87171", 2: "#fbbf24", 3: "#4ade80"}
    for i in range(1, 4):
        filled = i <= score
        color  = colors.get(score, "#94a3b8") if filled else "#1e293b"
        border = colors.get(score, "#94a3b8") if filled else "#334155"
        pips.append(
            f'<span style="display:inline-block;width:18px;height:18px;border-radius:4px;'
            f'background:{color};border:1px solid {border};margin-right:4px;"></span>'
        )
    return "".join(pips)


def generate_report(results: list[dict], output_path: str, judge_model: str = "mistral") -> None:
    total     = len(results)
    grounded  = sum(1 for r in results if r["label"] == "GROUNDED")
    partial   = sum(1 for r in results if r["label"] == "PARTIAL")
    ungrounded = sum(1 for r in results if r["label"] == "UNGROUNDED")
    scores    = [r["score"] for r in results if isinstance(r["score"], int) and r["score"] > 0]
    avg_score = f"{sum(scores)/len(scores):.2f}" if scores else "N/A"
    timestamp = datetime.now().strftime("%d %b %Y, %H:%M")

    # ── Result cards ───────────────────────────────────────────────────────────
    cards_html = ""
    for i, r in enumerate(results, 1):
        label  = r.get("label", "UNKNOWN")
        score  = r.get("score", 0)
        cfg    = LABEL_CONFIG.get(label, LABEL_CONFIG["UNKNOWN"])
        color  = cfg["color"]
        bg     = cfg["bg"]
        icon   = cfg["icon"]

        expected_row = ""
        if r.get("expected"):
            expected_row = f"""
            <div class="field">
                <span class="field-label">Expected answer</span>
                <span class="field-value expected">{r['expected']}</span>
            </div>"""

        cards_html += f"""
        <div class="card" style="border-left: 3px solid {color}; background: {bg};">
            <div class="card-header">
                <span class="card-num">#{i}</span>
                <span class="badge" style="color:{color}; border-color:{color};">
                    {icon} {label}
                </span>
                <span class="score-bar">{score_bar_html(score)}</span>
                <span class="score-text" style="color:{color};">{score}/3</span>
            </div>

            <div class="field">
                <span class="field-label">Question</span>
                <span class="field-value question">{r['question']}</span>
            </div>

            {expected_row}

            <div class="field">
                <span class="field-label">Bot response</span>
                <span class="field-value bot-response">{r['bot_response']}</span>
            </div>

            <div class="field">
                <span class="field-label">Judge reasoning</span>
                <span class="field-value reason" style="color:{color};">{r['reason']}</span>
            </div>
        </div>"""

    # ── Donut chart data ───────────────────────────────────────────────────────
    donut_data = [
        ("GROUNDED",   grounded,   "#4ade80"),
        ("PARTIAL",    partial,    "#fbbf24"),
        ("UNGROUNDED", ungrounded, "#f87171"),
    ]
    donut_segments = ""
    offset = 25  # start at top
    circumference = 2 * 3.14159 * 40  # r=40 → ~251.3
    for label, count, color in donut_data:
        if count == 0:
            continue
        pct  = count / total if total else 0
        dash = pct * circumference
        donut_segments += f"""
            <circle cx="50" cy="50" r="40"
                fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{dash:.2f} {circumference:.2f}"
                stroke-dashoffset="-{offset:.2f}"
                transform="rotate(-90 50 50)"/>"""
        offset += dash  # not quite right for dashoffset but gives visual

    # Proper cumulative offset version
    donut_segments = ""
    cumulative = 0
    for label, count, color in donut_data:
        if count == 0:
            continue
        pct  = count / total if total else 0
        dash = pct * circumference
        gap  = circumference - dash
        donut_segments += f"""
            <circle cx="50" cy="50" r="40"
                fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{dash:.2f} {gap:.2f}"
                stroke-dashoffset="{circumference/4 - cumulative:.2f}"
                transform="rotate(0 50 50)"/>"""
        cumulative += dash

    # ── Full HTML ──────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Test 7 — Groundedness Scoring</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:       #0a0f1a;
    --surface:  #0f1729;
    --border:   #1e293b;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --green:    #4ade80;
    --yellow:   #fbbf24;
    --red:      #f87171;
    --accent:   #38bdf8;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    padding: 40px 24px 80px;
  }}

  /* ── Header ── */
  .header {{
    max-width: 960px;
    margin: 0 auto 48px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 32px;
  }}
  .header-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .header h1 {{
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 6px;
  }}
  .header-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
  }}

  /* ── Summary bar ── */
  .summary {{
    max-width: 960px;
    margin: 0 auto 40px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }}
  .stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
  }}
  .stat-value {{
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 6px;
  }}
  .stat-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }}

  /* ── Donut ── */
  .donut-wrap {{
    max-width: 960px;
    margin: 0 auto 40px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 32px;
    display: flex;
    align-items: center;
    gap: 48px;
    flex-wrap: wrap;
  }}
  .donut-wrap svg {{
    width: 140px;
    height: 140px;
    flex-shrink: 0;
  }}
  .donut-legend {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 3px;
    flex-shrink: 0;
  }}
  .legend-count {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    margin-left: auto;
    padding-left: 24px;
  }}

  /* ── Filter bar ── */
  .filter-bar {{
    max-width: 960px;
    margin: 0 auto 28px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 7px 16px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
  }}
  .filter-btn:hover, .filter-btn.active {{
    color: var(--text);
    border-color: var(--accent);
    background: rgba(56,189,248,0.08);
  }}

  /* ── Cards ── */
  .cards {{
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .card {{
    border-radius: 10px;
    border: 1px solid var(--border);
    padding: 24px;
    transition: transform 0.15s;
  }}
  .card:hover {{ transform: translateX(3px); }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
    flex-wrap: wrap;
  }}
  .card-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
  }}
  .badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid;
    text-transform: uppercase;
  }}
  .score-bar {{ margin-left: auto; }}
  .score-text {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    min-width: 32px;
  }}

  .field {{ margin-bottom: 14px; }}
  .field:last-child {{ margin-bottom: 0; }}
  .field-label {{
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 5px;
  }}
  .field-value {{
    display: block;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text);
  }}
  .field-value.question {{ font-weight: 600; font-size: 15px; }}
  .field-value.expected {{ color: var(--muted); font-style: italic; }}
  .field-value.reason   {{ font-size: 13px; font-style: italic; }}
  .field-value.bot-response {{
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
    color: #94a3b8;
  }}

  .hidden {{ display: none !important; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-eyebrow">LLM Evaluation · Phase 2 · Test 7</div>
  <h1>Groundedness Scoring</h1>
  <div class="header-meta">Healthcare Bot · Judge: {JUDGE_MODEL if 'JUDGE_MODEL' in dir() else 'mistral'} · {timestamp}</div>
</div>

<!-- Summary stats -->
<div class="summary">
  <div class="stat">
    <div class="stat-value" style="color:var(--text)">{total}</div>
    <div class="stat-label">Total tests</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:var(--green)">{grounded}</div>
    <div class="stat-label">Grounded</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:var(--yellow)">{partial}</div>
    <div class="stat-label">Partial</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:var(--red)">{ungrounded}</div>
    <div class="stat-label">Ungrounded</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:var(--accent)">{avg_score}</div>
    <div class="stat-label">Avg score</div>
  </div>
</div>

<!-- Donut chart -->
<div class="donut-wrap">
  <svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" stroke-width="12"/>
    {donut_segments}
    <text x="50" y="54" text-anchor="middle"
      font-family="Syne,sans-serif" font-size="16" font-weight="800"
      fill="#e2e8f0">{avg_score}</text>
  </svg>
  <div class="donut-legend">
    <div class="legend-item">
      <div class="legend-dot" style="background:#4ade80"></div>
      <span>Grounded</span>
      <span class="legend-count" style="color:#4ade80">{grounded}</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot" style="background:#fbbf24"></div>
      <span>Partial</span>
      <span class="legend-count" style="color:#fbbf24">{partial}</span>
    </div>
    <div class="legend-item">
      <div class="legend-dot" style="background:#f87171"></div>
      <span>Ungrounded</span>
      <span class="legend-count" style="color:#f87171">{ungrounded}</span>
    </div>
  </div>
</div>

<!-- Filter bar -->
<div class="filter-bar">
  <button class="filter-btn active" onclick="filterCards('ALL')">All ({total})</button>
  <button class="filter-btn" onclick="filterCards('GROUNDED')">✓ Grounded ({grounded})</button>
  <button class="filter-btn" onclick="filterCards('PARTIAL')">~ Partial ({partial})</button>
  <button class="filter-btn" onclick="filterCards('UNGROUNDED')">✗ Ungrounded ({ungrounded})</button>
</div>

<!-- Result cards -->
<div class="cards" id="cards">
{cards_html}
</div>

<script>
  function filterCards(label) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    document.querySelectorAll('.card').forEach(card => {{
      if (label === 'ALL') {{
        card.classList.remove('hidden');
      }} else {{
        const badge = card.querySelector('.badge');
        if (badge && badge.textContent.includes(label)) {{
          card.classList.remove('hidden');
        }} else {{
          card.classList.add('hidden');
        }}
      }}
    }});
  }}
</script>

</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"   Report written: {output_path}")
