"""Validate MASTER_CURRICULUM.md and render its standalone course browser."""

import argparse
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "MASTER_CURRICULUM.md"
OUTPUT = ROOT / "docs/master-curriculum.html"
STAGES = ("Beginner", "Intermediate", "Advanced", "Production", "Specialized / Expert")
SECTIONS = ("Course overview", "Learning paths", "Repository coverage", "Teaching plan", "Detailed curriculum")
STATUSES = ("Reusable", "Needs Improvement", "Needs Correction", "New", "Not Assessed")
DIFFICULTIES = ("Beginner", "Intermediate", "Advanced", "Expert")
TIME_LABELS = ("Theory", "Guided hands-on", "Experiments", "Exercises", "Learner total", "Instructor-led")
MODULE_FIELDS = (
    "Difficulty", "Track", "Subject", "Description", "Objectives", "Prerequisites",
    "Labs", "Competencies", "Completion", "Hours",
)
TOPIC_FIELDS = (
    "Difficulty", "Why it matters", "Concepts", "Prerequisites", "Demonstration",
    "Exercise and assessment", "Hours", "Status", "Existing files", "Audit findings",
    "Reuse strategy", "Teaching and experiment gaps", "Technical corrections",
)
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
INLINE = re.compile(LINK.pattern + r"|\*\*([^*\n]+)\*\*|" + chr(96) + r"([^" + chr(96) + r"\n]+)" + chr(96))
FIELD = re.compile(r"- \*\*(.+?)\.\*\* (.+)")
NUMBER = re.compile(r"\d+(?:\.5|\.0)?")
FINDING = re.compile(r"[CSV]\d{2}")


class IDs(HTMLParser):
    """Collect fragment identifiers from a local lesson."""

    def __init__(self):
        super().__init__()
        self.values = set()

    def handle_starttag(self, tag, attrs):
        self.values.update(value for key, value in attrs if key == "id")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_hours(parts, context):
    values = [part.strip() for part in parts]
    require(len(values) == 6 and all(NUMBER.fullmatch(value) for value in values), f"Invalid hours in {context}")
    hours = tuple(float(value) for value in values)
    require(sum(hours[:4]) == hours[4] and all(value > 0 for value in hours), f"Hours do not add up in {context}")
    require(hours[5] <= hours[4], f"Classroom time exceeds learner time in {context}")
    return hours


def sum_hours(records):
    return tuple(map(sum, zip(*(record["hours"] for record in records), strict=True)))


def parse(source):
    title, body = source.split("\n", 1)
    require(title.startswith("# ") and len(title) > 2, "A course title is required")
    section_parts = re.split(r"^## (.+)\n", body, flags=re.M)
    sections = dict(zip(section_parts[1::2], section_parts[2::2], strict=True))
    require(tuple(section_parts[1::2]) == SECTIONS, "Missing, unordered or duplicate top-level sections")
    stages, records = {}, {}
    stage = module = None
    for block in sections.pop("Detailed curriculum").strip().split("\n\n"):
        if block.startswith("### "):
            stage = block[4:]
            require(stage in STAGES and stage not in stages, f"Invalid or duplicate stage {stage}")
            stages[stage] = []
            module = None
        elif block.startswith("<a id="):
            heading = re.fullmatch(r'<a id="([a-z0-9-]+)"></a>\n(#{4,5}) (M\d{2}(?:-T\d{2})?) — (.+)', block)
            require(heading is not None and stage is not None, f"Invalid record heading: {block}")
            anchor, depth, code, name = heading.groups()
            require(anchor == code.lower() and code not in records, f"Invalid or duplicate ID {code}")
            record = {"id": code, "title": name, "fields": {}}
            records[code] = record
            if len(depth) == 4:
                require("-T" not in code, f"Invalid module ID {code}")
                module = record
                module["topics"] = []
                stages[stage].append(module)
            else:
                require(module is not None and code.startswith(module["id"] + "-T"), f"Invalid topic parent for {code}")
                module["topics"].append(record)
        else:
            require(records, "Fields must follow a record heading")
            record = next(reversed(records.values()))
            require(not record["fields"], f"Unexpected block after {record['id']}")
            for line in block.splitlines():
                field = FIELD.fullmatch(line)
                require(field is not None, f"Invalid field in {record['id']}: {line}")
                key, value = field.groups()
                require(key not in record["fields"], f"Duplicate {record['id']} field {key}")
                record["fields"][key] = value
    require(tuple(stages) == STAGES and all(stages.values()), "Missing, unordered or empty stage")
    validate(stages, records, sections["Course overview"], source)
    return title[2:], sections, stages


def validate(stages, records, overview, source):
    audit = ROOT / "docs/COURSE_AUDIT_REPORT.md"
    known_findings = set(re.findall(r"^\| ([CSV]\d{2}) \|", audit.read_text(encoding="utf-8"), re.M)) if audit.is_file() else None
    prior = set()
    for code, record in records.items():
        fields = record["fields"]
        is_module = "topics" in record
        required = MODULE_FIELDS if is_module else TOPIC_FIELDS
        require(set(fields) == set(required), f"Missing or unexpected fields in {code}")
        require(all(value.strip() for value in fields.values()), f"Empty field in {code}")
        require(fields["Difficulty"] in DIFFICULTIES, f"Unknown difficulty in {code}")
        record["hours"] = read_hours(fields["Hours"].split("/"), code)
        prereqs = fields["Prerequisites"]
        refs = LINK.findall(prereqs)
        if prereqs != "None":
            require(", ".join(f"[{label}]({target})" for label, target in refs) == prereqs and refs,
                    f"Invalid prerequisites in {code}")
            for label, target in refs:
                require(label in prior and target == "#" + label.lower() and ("-T" in label) != is_module,
                        f"Missing or out-of-order prerequisite {label} in {code}")
        prior.add(code)

        if not is_module:
            require(fields["Status"] in STATUSES, f"Unknown status in {code}")
            files = fields["Existing files"]
            file_refs = LINK.findall(files)
            require(files == "—" or (file_refs and ", ".join(f"[{label}]({target})" for label, target in file_refs) == files),
                    f"Invalid existing files in {code}")
            require(fields["Status"] not in STATUSES[:3] or file_refs, f"Existing material must be linked in {code}")
            findings = fields["Audit findings"]
            if findings != "—":
                require(all(FINDING.fullmatch(tag) and (known_findings is None or tag in known_findings)
                            for tag in findings.split(",")), f"Unknown audit reference in {code}")

    modules = [module for stage in stages.values() for module in stage]
    for stage, group in stages.items():
        for module in group:
            track = "Elective" if stage == STAGES[-1] else "Core"
            require(module["fields"]["Track"] == track and module["topics"], f"Invalid track or empty module {module['id']}")
            require(sum_hours(module["topics"]) == module["hours"], f"Module hours do not add up in {module['id']}")
    summary = table_rows(next((block for block in overview.split("\n\n") if block.strip().startswith("| Strand |")), ""))
    require(len(summary) == 4, "A three-row course hours table is required")
    for row, name in zip(summary[1:], ("Core", "Elective", "All"), strict=True):
        group = [module for module in modules if name in ("All", module["fields"]["Track"])]
        expected = [name, str(len(group)), str(sum(len(module["topics"]) for module in group))]
        require(row[:3] == expected and read_hours(row[3:], name) == sum_hours(group),
                f"Course hours or counts do not add up for {name}")

    fragments = set()
    for _, link in LINK.findall(source):
        filename, _, fragment = link.partition("#")
        if not filename:
            require(fragment in {code.lower() for code in records}, f"Unknown curriculum link {link}")
            continue
        path = ROOT / filename
        require(path.is_relative_to(ROOT) and ".." not in Path(filename).parts and path.is_file(),
                f"Missing or invalid repository link {link}")
        if fragment and link not in fragments:
            parser = IDs()
            parser.feed(path.read_text(encoding="utf-8"))
            require(fragment in parser.values, f"Missing fragment in {link}")
            fragments.add(link)


def inline(markdown):
    def format_token(match):
        label, target, bold, code = match.groups()
        if label is not None:
            label = inline(label)
            if not target.startswith("#"):
                filename, separator, fragment = target.partition("#")
                if not filename.startswith("docs/") or not filename.endswith(".html"):
                    return label
                target = posixpath.relpath(filename, "docs") + separator + fragment
            return f'<a href="{escape(quote(target, safe="/#-._"))}">{label}</a>'
        if bold is not None:
            return f"<strong>{escape(bold)}</strong>"
        return f"<code>{escape(code)}</code>"

    rendered, offset = [], 0
    for match in INLINE.finditer(markdown):
        rendered.extend((escape(markdown[offset:match.start()]), format_token(match)))
        offset = match.end()
    rendered.append(escape(markdown[offset:]))
    return "".join(rendered)


def table_rows(markdown):
    return [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in markdown.strip().splitlines()
            if row.strip() and not re.fullmatch(r"\|[-:| ]+\|", row.strip())]


def table(headers, rows, caption):
    headings = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in headers)
    body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows)
    return (f'<div class="table-wrap" tabindex="0" role="region" aria-label="{escape(caption)}">'
            f"<table><caption>{escape(caption)}</caption><thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table></div>")


def prose(markdown):
    parts = []
    for block in markdown.strip().split("\n\n"):
        if block.startswith("### "):
            parts.append(f"<h3>{inline(block[4:])}</h3>")
        elif block.startswith("|"):
            header, *rows = table_rows(block)
            parts.append(table(header, rows, "Course hours by track"))
        elif block.startswith("- ") or re.match(r"\d+\. ", block):
            tag = "ul" if block.startswith("- ") else "ol"
            items = [re.sub(r"^(?:-|\d+\.) ", "", line) for line in block.splitlines()]
            parts.append(f"<{tag}>" + "".join(f"<li>{inline(item)}</li>" for item in items) + f"</{tag}>")
        else:
            parts.append(f"<p>{inline(' '.join(block.splitlines()))}</p>")
    return "\n".join(parts)


def time_cards(hours):
    return '<dl class="time-list" aria-label="Time estimates in hours">' + "".join(
        f"<div><dt>{label}</dt><dd>{value:g} h</dd></div>"
        for label, value in zip(TIME_LABELS, hours, strict=True)
    ) + "</dl>"


def definitions(fields, keys):
    return "<dl class=\"field-list\">" + "".join(
        f"<div><dt>{label}</dt><dd>{inline(fields[label])}</dd></div>" for label in keys
    ) + "</dl>"


def html_topic(topic, module):
    fields = topic["fields"]
    anchor = topic["id"].lower()
    options = "".join(f"<option>{status}</option>" for status in ("Not Started", "In Progress", "Completed"))
    description = definitions(fields, TOPIC_FIELDS[1:6])
    mapping = definitions(fields, TOPIC_FIELDS[8:])
    return f'''<details class="topic" id="{anchor}" data-topic="{topic['id']}" data-difficulty="{fields['Difficulty']}"
data-subject="{escape(module['fields']['Subject'])}" data-status="{fields['Status']}" data-track="{module['fields']['Track']}">
  <summary><span class="item-title"><span class="item-id">{topic['id']}</span> {escape(topic['title'])}</span>
    <span class="topic-meta">{fields['Status']} · {topic['hours'][4]:g} h</span></summary>
  <div class="topic-body">
    <div class="topic-controls"><p>{fields['Difficulty']} · {module['fields']['Track']}</p>
      <label class="js-control" hidden for="progress-{anchor}">Progress <select id="progress-{anchor}" data-progress>{options}</select></label>
      <a class="topic-link" href="#{anchor}">Link to topic</a>
    </div>
    {description}
    {time_cards(topic['hours'])}
    <h4>Repository mapping</h4>
    {mapping}
  </div>
</details>'''


def html_module(module):
    fields = module["fields"]
    anchor = module["id"].lower()
    topics = "\n".join(html_topic(topic, module) for topic in module["topics"])
    return f'''<details class="module" id="{anchor}">
  <summary><span class="item-title"><span class="item-id">{module['id']}</span> {escape(module['title'])}</span>
    <span class="topic-meta">{len(module['topics'])} topics · {module['hours'][4]:g} h</span>
    <span class="module-progress" hidden data-module-progress></span></summary>
  <div class="module-body">
    <p class="track">{fields['Difficulty']} · {fields['Track']} · {escape(fields['Subject'])}</p>
    {definitions(fields, MODULE_FIELDS[3:9])}
    {time_cards(module['hours'])}
    {topics}
  </div>
</details>'''


def html_stages(stages):
    result = []
    for name, modules in stages.items():
        hours = sum_hours(modules)
        content = "\n".join(map(html_module, modules))
        result.append(f'''<details class="stage" {"open" if name == "Beginner" else ""}>
  <summary><span class="stage-title">{name}</span><span class="topic-meta">{len(modules)} modules · {hours[4]:g} h</span></summary>
  <div class="stage-body">{content}</div>
</details>''')
    return "\n".join(result)


def render(title, sections, stages):
    modules = [module for group in stages.values() for module in group]
    topics = [topic for module in modules for topic in module["topics"]]
    hours = sum_hours(modules)
    coverage = Counter(topic["fields"]["Status"] for topic in topics)
    rows = []
    for module in modules:
        for topic in module["topics"]:
            fields = topic["fields"]
            rows.append([f"[{topic['id']} — {topic['title']}](#{topic['id'].lower()})",
                         fields["Status"], fields["Existing files"], fields["Audit findings"]])
    progress = f'''<div class="course-progress" id="course-progress" hidden>
  <p id="progress-label" aria-live="polite"></p>
  <progress id="progress-bar" max="{len(topics)}" value="0" aria-labelledby="progress-label"></progress>
  <p id="storage-note">Progress is saved in this browser on this device. It does not synchronize across devices.</p>
  <button type="button" id="reset-progress">Reset progress</button>
</div>'''
    detailed = filters(modules) + html_stages(stages)
    coverage_view = (prose(sections["Repository coverage"])
                     + '<ul class="status-counts">' + "".join(f"<li>{status} <strong>{coverage[status]}</strong></li>" for status in STATUSES)
                     + "</ul>" + table(("Topic", "Status", "Existing files", "Audit findings"), rows, "Coverage by topic"))
    tabs = (
        ("overview", "Curriculum Overview", prose(sections["Course overview"]) + progress),
        ("detail", "Detailed Curriculum", detailed),
        ("paths", "Learning Paths", prose(sections["Learning paths"])),
        ("coverage", "Existing Repository Coverage", coverage_view),
        ("teaching", "Teaching Plan", prose(sections["Teaching plan"])),
    )
    links = "\n".join(f'<a id="tab-{key}" href="#{key}">{name}</a>' for key, name, _ in tabs)
    panels = "\n".join(f'<section class="panel" id="{key}"><h2>{name}</h2>\n{content}\n</section>'
                       for key, name, content in tabs)
    return f'''<!doctype html>
<!-- Generated from MASTER_CURRICULUM.md by docs/generate_master_curriculum.py. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to curriculum</a>
<header class="hero">
  <div class="shell">
    <h1>{escape(title)}</h1>
    <p>{len(modules)} modules · {len(topics)} topics · {hours[4]:g} learner hours · {hours[5]:g} instructor-led hours</p>
  </div>
</header>
<main id="main" class="shell" tabindex="-1">
  <nav id="tabs" aria-label="Curriculum views">{links}</nav>
  {panels}
</main>
<script>{SCRIPT}</script>
</body>
</html>
'''


def filters(modules):
    def select(name, label, options):
        entries = "".join(f"<option>{escape(value)}</option>" for value in options)
        return f'<label for="{name}">{label}<select id="{name}"><option value="">All</option>{entries}</select></label>'

    subjects = sorted({module["fields"]["Subject"] for module in modules})
    controls = (
        select("difficulty", "Difficulty", DIFFICULTIES),
        select("subject", "Subject area", subjects),
        select("status", "Implementation status", STATUSES),
        select("track", "Core or elective", ("Core", "Elective")),
    )
    return f'''<div id="filters" class="js-control filter-box" hidden>
  <label for="search">Search topics<input id="search" type="search" placeholder="Try confidence intervals"></label>
  <div class="selects">{"".join(controls)}</div>
  <div class="actions">
    <button type="button" id="expand">Expand all</button>
    <button type="button" id="collapse">Collapse all</button>
    <button type="button" id="clear-filters">Clear filters</button>
    <output id="matches" aria-live="polite"></output>
  </div>
</div>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the current output without writing files")
    args = parser.parse_args()
    try:
        generated = render(*parse(SOURCE.read_text(encoding="utf-8")))
        if args.check:
            require(OUTPUT.is_file() and OUTPUT.read_bytes() == generated.encode("utf-8"),
                    "Generated HTML is stale. Run python3 docs/generate_master_curriculum.py.")
            print("Curriculum source and generated HTML match.")
        else:
            OUTPUT.write_bytes(generated.encode("utf-8"))
            print(f"Generated {OUTPUT.relative_to(ROOT)}.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Curriculum validation failed: {error}\n")


CSS = """
:root { color-scheme: light; --ink:#162938; --muted:#465b68; --paper:#f4f6f5; --surface:#fff;
  --line:#cbd7d7; --accent:#075a51; --soft:#e5f1ed; font:16px/1.6 system-ui,-apple-system,sans-serif; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:var(--paper); }
[hidden] { display:none !important; }
a { color:var(--accent); text-underline-offset:.2em; }
button, select, input { font:inherit; color:inherit; }
a:focus-visible, button:focus-visible, summary:focus-visible, select:focus-visible, input:focus-visible,
[tabindex]:focus-visible { outline:3px solid #086f9c; outline-offset:3px; }
.skip-link { position:fixed; z-index:2; top:.5rem; left:.5rem; padding:.5rem .75rem; background:#fff; transform:translateY(-150%); }
.skip-link:focus { transform:none; }
.shell { width:min(1160px,100% - 3rem); margin-inline:auto; }
.hero { padding:clamp(2rem,6vw,4.6rem) 0 clamp(1.6rem,3vw,2.8rem); background:#132b39; color:#f6faf8; border-bottom:5px solid #48a493; }
h1,h2,h3,h4,p { margin:0; }
h1 { font:650 clamp(2rem,5vw,4rem)/1.08 Georgia,serif; max-width:25ch; letter-spacing:-.025em; }
.hero p { margin-top:1.25rem; color:#d1e8e3; font-weight:600; font-variant-numeric:tabular-nums; }
main { padding-bottom:3rem; }
#tabs { display:flex; flex-wrap:wrap; gap:.25rem .7rem; margin:1.1rem 0 1.65rem; border-bottom:1px solid var(--line); }
#tabs a { padding:.65rem .7rem; color:var(--ink); font-weight:650; text-decoration:none; border-bottom:3px solid transparent; }
#tabs a:hover { background:var(--soft); }
#tabs [aria-selected="true"] { color:var(--accent); border-color:var(--accent); }
.panel { padding:0 0 2rem; }
h2 { font:650 clamp(1.65rem,4vw,2.25rem)/1.15 Georgia,serif; margin-bottom:.8rem; }
h3 { margin-top:1.5rem; font-size:1.12rem; }
h4 { margin-top:1.25rem; }
.panel > p, .panel > ul, .panel > ol, .panel > h3 { max-width:80ch; }
p,.panel > ul,.panel > ol { margin-block:.65rem; }
li + li { margin-top:.4rem; }
code { font: .92em ui-monospace,SFMono-Regular,Consolas,monospace; overflow-wrap:anywhere; }
.table-wrap { overflow-x:auto; margin:1.2rem 0; padding:0 .1rem .2rem; }
table { width:100%; border-collapse:collapse; background:var(--surface); font-variant-numeric:tabular-nums; }
caption { font-weight:650; text-align:left; padding-bottom:.45rem; }
th,td { text-align:left; vertical-align:top; border-bottom:1px solid var(--line); padding:.65rem .7rem; }
th { color:#204139; background:var(--soft); }
td:first-child { min-width:7rem; }
.status-counts { display:flex; flex-wrap:wrap; gap:.5rem; list-style:none; padding:0; }
.status-counts li { background:var(--soft); border:1px solid var(--line); padding:.25rem .6rem; border-radius:.4rem; margin:0; }
.course-progress,.filter-box { border:1px solid var(--line); border-radius:.65rem; background:var(--surface); padding:1rem 1.2rem; margin:1rem 0; }
.course-progress { max-width:41rem; }
progress { display:block; width:100%; height:.9rem; accent-color:var(--accent); }
#progress-label { font-weight:700; }
#storage-note { color:var(--muted); }
button { cursor:pointer; padding:.42rem .72rem; border:1px solid #8da5a3; border-radius:.4rem; background:var(--surface); font-weight:650; }
button:hover { background:var(--soft); }
label { font-weight:650; }
select,input { display:block; width:100%; padding:.42rem .55rem; min-height:2.65rem; border:1px solid #8da5a3;
  border-radius:.35rem; background:var(--surface); }
.selects { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.65rem; margin:.75rem 0; }
.actions { display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; }
#matches { margin-left:auto; color:var(--muted); }
details { border-radius:.55rem; border:1px solid var(--line); background:var(--surface); scroll-margin-top:1rem; }
details:target { border-color:var(--accent); box-shadow:0 0 0 1px var(--accent); }
summary { display:flex; align-items:baseline; flex-wrap:wrap; gap:.3rem .7rem; padding:.7rem .9rem;
  font-weight:650; cursor:pointer; list-style:none; }
summary::-webkit-details-marker { display:none; }
summary::before { content:""; width:.45rem; height:.45rem; margin-right:.15rem; border:solid var(--accent);
  border-width:0 2px 2px 0; flex:none; transform:rotate(-45deg); align-self:center; }
details[open] > summary::before { transform:rotate(45deg); }
summary:hover { background:#edf5f3; border-radius:.55rem; }
.stage { margin-bottom:.8rem; }
.stage > summary { background:var(--soft); padding:.8rem .95rem; }
.stage-title { font-size:1.13rem; }
.stage-body,.module-body,.topic-body { padding:.25rem .85rem .85rem; }
.module { margin-top:.65rem; }
.topic { margin-top:.55rem; }
.item-title { flex:1 1 18rem; overflow-wrap:anywhere; }
.item-id { font-size:.85em; color:var(--accent); white-space:nowrap; margin-right:.2rem; }
.topic-meta,.module-progress,.track { color:var(--muted); font-size:.9rem; }
.module-progress { font-weight:500; }
.topic-controls { display:flex; align-items:center; gap:.6rem 1rem; flex-wrap:wrap; border-top:1px solid var(--line); }
.topic-controls label { display:inline-flex; align-items:center; gap:.45rem; }
.topic-controls select { width:auto; }
.topic-link { margin-left:auto; }
.field-list { margin:.6rem 0; }
.field-list > div { margin:.45rem 0; }
.field-list dt { font-weight:700; }
.field-list dd { margin:0; }
.time-list { display:grid; grid-template-columns:repeat(auto-fit,minmax(7.6rem,1fr)); gap:.35rem; margin:.8rem 0; }
.time-list div { background:#eef4f3; border-radius:.35rem; padding:.35rem .55rem; }
.time-list dt { font-size:.83rem; color:var(--muted); }
.time-list dd { margin:0; font-weight:700; font-variant-numeric:tabular-nums; }
@media (max-width:700px) {
  .shell { width:calc(100% - 1.5rem); }
  .selects { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .stage-body,.module-body,.topic-body { padding-inline:.6rem; }
  #tabs a { padding:.4rem; }
  #matches { margin-left:0; }
}
@media (max-width:360px) {
  .selects { grid-template-columns:1fr; }
}
@media print {
  @page { margin:15mm; }
  body, .hero, th, details, .stage > summary, .time-list div { background:#fff; color:#000; }
  .shell { width:100%; }
  .hero { padding:0 0 .7rem; border-bottom:1px solid #000; }
  .hero p, .track, .time-list dt, .item-id, .topic-meta { color:#000; }
  h1 { font-size:24pt; }
  h2,h3,h4,summary { break-after:avoid; }
  .panel[hidden] { display:block !important; }
  .panel { padding-top:1rem; }
  .table-wrap { overflow:visible; }
  #tabs, .skip-link, .filter-box, #course-progress, [data-module-progress], .topic-controls label, .topic-link,
  summary::before { display:none !important; }
}
"""

SCRIPT = """
"use strict";

const tabs = Array.from(document.querySelectorAll("#tabs a"));
const panels = tabs.map(tab => document.querySelector(tab.hash));
const stages = Array.from(document.querySelectorAll(".stage"));
const modules = Array.from(document.querySelectorAll(".module"));
const topics = Array.from(document.querySelectorAll(".topic"));
const disclosures = [...stages, ...modules, ...topics];
const filters = document.getElementById("filters");
const search = document.getElementById("search");
const filterNames = ["difficulty", "subject", "status", "track"];
const controls = filterNames.map(name => document.getElementById(name));
const searchText = new Map(topics.map(topic => [topic, [
  topic.querySelector(".item-title").textContent,
  ...Array.from(topic.querySelectorAll(".topic-body .field-list dd")).map(field => field.textContent)
].join(" ").toLocaleLowerCase()]));

function activate(tab) {
  tabs.forEach((item, index) => {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
    panels[index].hidden = !selected;
  });
}

document.getElementById("tabs").setAttribute("role", "tablist");
tabs.forEach((tab, index) => {
  tab.setAttribute("role", "tab");
  tab.setAttribute("aria-controls", panels[index].id);
  panels[index].setAttribute("role", "tabpanel");
  panels[index].setAttribute("aria-labelledby", tab.id);
  panels[index].tabIndex = 0;
  tab.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    activate(tab);
  });
  tab.addEventListener("keydown", event => {
    const offsets = {ArrowLeft: -1, ArrowRight: 1, Home: -index, End: tabs.length - 1 - index};
    if (event.key === " ") {
      event.preventDefault();
      activate(tab);
    } else if (Object.hasOwn(offsets, event.key)) {
      const next = tabs[(index + offsets[event.key] + tabs.length) % tabs.length];
      event.preventDefault();
      activate(next);
      next.focus();
    }
  });
});
document.querySelectorAll(".js-control").forEach(control => { control.hidden = false; });

function applyFilters() {
  const terms = search.value.trim().toLocaleLowerCase().split(/\\s+/).filter(Boolean);
  const active = terms.length > 0 || controls.some(control => control.value);
  let visible = 0;
  topics.forEach(topic => {
    const match = terms.every(term => searchText.get(topic).includes(term)) &&
      controls.every((control, index) => !control.value || control.value === topic.dataset[filterNames[index]]);
    topic.hidden = !match;
    if (match) visible += 1;
  });
  modules.forEach(module => {
    module.hidden = !module.querySelector(".topic:not([hidden])");
    if (active && !module.hidden) module.open = true;
  });
  stages.forEach(stage => {
    stage.hidden = !stage.querySelector(".module:not([hidden])");
    if (active && !stage.hidden) stage.open = true;
  });
  document.getElementById("matches").textContent = visible
    ? visible + " of " + topics.length + " topics"
    : "No matching topics";
}

function clearFilters() {
  search.value = "";
  controls.forEach(control => { control.value = ""; });
  applyFilters();
}

search.addEventListener("input", applyFilters);
controls.forEach(control => control.addEventListener("change", applyFilters));
document.getElementById("clear-filters").addEventListener("click", clearFilters);
for (const [id, open] of [["expand", true], ["collapse", false]]) {
  document.getElementById(id).addEventListener("click", () => {
    disclosures.filter(details => !details.hidden).forEach(details => { details.open = open; });
  });
}

function followHash(focus) {
  const target = document.getElementById(location.hash.slice(1));
  if (!target) return false;
  const panel = target.closest(".panel");
  if (!panel) return false;
  activate(tabs[panels.indexOf(panel)]);
  if (target.matches(".topic, .module")) {
    if (target.hidden) clearFilters();
    for (let details = target; details; details = details.parentElement.closest("details")) details.open = true;
    if (focus) target.querySelector("summary").focus({preventScroll: true});
    target.scrollIntoView({block: "start"});
  }
  return true;
}

window.addEventListener("hashchange", () => followHash(true));
document.addEventListener("click", event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link || link.hash !== location.hash || link.getAttribute("role") === "tab" ||
      event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  if (followHash(true)) event.preventDefault();
});
activate(tabs[0]);
applyFilters();
followHash(false);

const storageKey = "llm-evaluation-master-curriculum-progress-v1";
const choices = new Set(["Not Started", "In Progress", "Completed"]);
const menus = new Map(topics.map(topic => [topic.dataset.topic, topic.querySelector("[data-progress]")]));
const progressBar = document.getElementById("progress-bar");
const progressLabel = document.getElementById("progress-label");
const storageNote = document.getElementById("storage-note");
const defaultStorageNote = storageNote.textContent;

function reportStorage(available) {
  storageNote.textContent = available ? defaultStorageNote
    : "This browser is blocking local storage. Progress changes are available for this session.";
}

function updateProgress() {
  const completed = Array.from(menus.values()).filter(menu => menu.value === "Completed").length;
  progressBar.value = completed;
  progressLabel.textContent = "Course progress " + Math.round(completed * 100 / topics.length) +
    "% · " + completed + " of " + topics.length + " topics completed";
  modules.forEach(module => {
    const moduleMenus = Array.from(module.querySelectorAll("[data-progress]"));
    const done = moduleMenus.filter(menu => menu.value === "Completed").length;
    const label = module.querySelector("[data-module-progress]");
    label.textContent = Math.round(done * 100 / moduleMenus.length) + "% complete";
    label.hidden = false;
  });
}

try {
  const saved = JSON.parse(localStorage.getItem(storageKey));
  for (const [id, menu] of menus) {
    if (saved && Object.hasOwn(saved, id) && choices.has(saved[id])) menu.value = saved[id];
  }
} catch (error) {
  if (!(error instanceof SyntaxError)) reportStorage(false);
}

for (const menu of menus.values()) {
  menu.addEventListener("change", () => {
    updateProgress();
    const selected = Array.from(menus).filter(([, item]) => item.value !== "Not Started");
    const progress = Object.fromEntries(selected.map(([id, item]) => [id, item.value]));
    try {
      localStorage.setItem(storageKey, JSON.stringify(progress));
      reportStorage(true);
    } catch {
      reportStorage(false);
    }
  });
}
document.getElementById("reset-progress").addEventListener("click", () => {
  if (!window.confirm("Reset progress for all topics in this browser?")) return;
  for (const menu of menus.values()) menu.value = "Not Started";
  updateProgress();
  try {
    localStorage.removeItem(storageKey);
    reportStorage(true);
  } catch {
    reportStorage(false);
  }
});
updateProgress();
document.getElementById("course-progress").hidden = false;

let printState;
window.addEventListener("beforeprint", () => {
  if (printState) return;
  printState = disclosures.map(details => [details, details.open, details.hidden]);
  disclosures.forEach(details => {
    details.hidden = false;
    details.open = true;
  });
});
window.addEventListener("afterprint", () => {
  if (!printState) return;
  printState.forEach(([details, open, hidden]) => {
    details.open = open;
    details.hidden = hidden;
  });
  printState = null;
});
"""


if __name__ == "__main__":
    main()

