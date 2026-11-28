"""Validate MASTER_CURRICULUM.md and render its standalone course browser."""

import argparse
from base64 import b64encode
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import quote

import original_experiments


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "MASTER_CURRICULUM.md"
OUTPUT = ROOT / "docs/master-curriculum.html"
HOME = ROOT / "docs/index.html"
HOME_TEMPLATE = ROOT / "docs/templates/academy-home.html"
REPORT_SOURCE = ROOT / "phase-1-first-experiments/results/full_results.html"
PYTHON_EDITOR = "https://www.online-python.com/"
ASSETS = ROOT / "docs/assets"
BRANDING = ASSETS / "branding"
BRAND_FILES = ("academy-logo-banner.png", "icon-48.png", "favicon.ico", "icon-32.png", "icon-180.png")
ROADMAP_SCRIPT = ROOT / "docs/learning_roadmap.js"
MODES_SCRIPT = ROOT / "docs/learning_modes.js"
NAVIGATOR_SCRIPT = ROOT / "docs/learning_navigator.js"
PROGRESS_SCRIPT = ROOT / "docs/learning_progress.js"
READER_SCRIPT = ASSETS / "lesson-reader.js"
STAGES = ("Beginner", "Intermediate", "Advanced", "Production", "Specialized / Expert")
SECTIONS = ("Course overview", "Learning paths", "Repository coverage", "Teaching plan", "Detailed curriculum")
STATUSES = ("Reusable", "Needs Improvement", "Needs Correction", "New", "Not Assessed")
DIFFICULTIES = ("Beginner", "Intermediate", "Advanced", "Expert")
TIME_LABELS = ("Theory (hrs)", "Guided (hrs)", "Experiment (hrs)", "Exercises (hrs)",
               "Learner total (hrs)", "Instructor-led (hrs)")
MODULE_FIELDS = (
    "Difficulty", "Track", "Subject", "Description", "Objectives",
    "Labs", "Competencies", "Completion", "Hours",
)
DEPENDENCIES = ("Mandatory prerequisites", "Recommended prerequisites", "Conditional prerequisites")
TOPIC_FIELDS = (
    "Difficulty", "Why it matters", "Concepts", *DEPENDENCIES, "Implementation readiness", "Demonstration",
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
    return title[2:], sections, stages, roadmap_data(stages, sections["Learning paths"], source)


def linked_ids(value, context, conditional=False):
    if value == "—":
        return []
    result = []
    for entry in value.split(" / " if conditional else ", "):
        label, separator, note = entry.partition(" — ")
        link = LINK.fullmatch(label)
        require(link and link[2] == "#" + link[1].lower(), f"Invalid link in {context}: {entry}")
        require((separator and note.strip()) if conditional else not separator,
                f"Expected {'a condition' if conditional else 'only a linked ID'} in {context}: {entry}")
        result.append({"id": link[1], "note": note})
    require(len({edge["id"] for edge in result}) == len(result), f"Duplicate links in {context}")
    return result


def mandatory_closures(topics):
    """Return each topic and its distinct mandatory ancestors in curriculum order."""
    closures, visiting = {}, set()

    def visit(topic_id):
        require(topic_id in topics, f"Missing prerequisite {topic_id}")
        require(topic_id not in visiting, f"Mandatory dependency cycle at {topic_id}")
        if topic_id not in closures:
            visiting.add(topic_id)
            parents = topics[topic_id]["mandatory"]
            closures[topic_id] = {topic_id}.union(*(visit(parent["id"]) for parent in parents))
            visiting.remove(topic_id)
        return closures[topic_id]

    for topic_id in topics:
        visit(topic_id)
    order = {topic_id: index for index, topic_id in enumerate(topics)}
    for topic_id, topic in topics.items():
        for parent in topic["mandatory"]:
            require(order[parent["id"]] < order[topic_id], f"Out-of-order mandatory prerequisite {parent['id']} in {topic_id}")
    return {topic_id: sorted(closure, key=order.__getitem__) for topic_id, closure in closures.items()}


def roadmap_data(stages, learning_paths, source):
    modules, topics = {}, {}
    for stage_index, group in enumerate(stages.values()):
        for module in group:
            code, fields = module["id"], module["fields"]
            modules[code] = {
                "id": code, "title": module["title"], "stage": stage_index, "hours": module["hours"][4],
                "difficulty": fields["Difficulty"],
                "track": fields["Track"], "description": fields["Description"], "outcome": fields["Competencies"],
                "topics": [topic["id"] for topic in module["topics"]],
            }
            for topic in module["topics"]:
                key, info = topic["id"], topic["fields"]
                topics[key] = {
                    "id": key, "title": topic["title"], "stage": stage_index, "module": code,
                    "hours": topic["hours"][4], "description": info["Why it matters"], "concepts": info["Concepts"],
                    "outcome": info["Exercise and assessment"], "readiness": info["Implementation readiness"],
                    **{kind: linked_ids(info[field], f"{key} {field}", kind == "conditional")
                       for kind, field in zip(("mandatory", "recommended", "conditional"), DEPENDENCIES, strict=True)},
                }
    closures = mandatory_closures(topics)
    for key, topic in topics.items():
        topic["closure"] = closures[key]
        for kind in ("recommended", "conditional"):
            for parent in topic[kind]:
                require(parent["id"] in topics and parent["id"] != key, f"Invalid {kind} prerequisite {parent['id']} in {key}")
    for code, module in modules.items():
        module["closure"] = combined_closure(module["topics"], topics)

    blocks = learning_paths.split("\n\n")
    preparation = table_rows(next((block for block in blocks if block.startswith("| ID | Readiness skill |")), ""))
    total = re.search(r"Allow \*\*(\d+(?:\.5)?) learner hours\*\*", learning_paths)
    require(len(preparation) > 1 and total, "Missing preparation table or total")
    prep_ids = [row[0] for row in preparation[1:]]
    require(len(set(prep_ids)) == len(prep_ids) and all(re.fullmatch(r"P\d{2}", key) for key in prep_ids),
            "Invalid or duplicate preparation IDs")
    require(all(len(row) == 5 and all(row) and NUMBER.fullmatch(row[-1]) and float(row[-1]) > 0
                for row in preparation[1:]), "Invalid preparation row")
    require(sum(float(row[-1]) for row in preparation[1:]) == float(total[1]), "Preparation hours do not add up")
    for key, topic in topics.items():
        for skill in re.findall(r"\bP\d{2}\b", topic["readiness"]):
            require(skill in prep_ids, f"Unknown preparation skill {skill} in {key}")
    paths = table_rows(next((block for block in blocks if block.startswith("| Path | Name |")), ""))
    require(len(paths) == 8 and all(len(row) == 5 for row in paths), "Expected learning paths A–G")
    require([row[0] for row in paths[1:]] == list("ABCDEFG"), "Missing, duplicate or unordered learning path IDs")
    result = {}
    for key, name, value, count, hours in paths[1:]:
        if key in ("A", "G"):
            required = "Core" if key == "A" else "All"
            require(value == required, f"Path {key} must target {required}")
            targets = [code for code, module in modules.items() if required in ("All", module["track"])]
        else:
            targets = [edge["id"] for edge in linked_ids(value, f"path {key}")]
        require(targets and all(target in topics or target in modules for target in targets),
                f"Invalid target for path {key}")
        roots = {topic for target in targets for topic in (modules[target]["topics"] if target in modules else [target])}
        closure = combined_closure(roots, topics)
        if key == "A":
            require(set(closure) == roots, "Core topics must not require an elective")
        require(count == str(len(closure)) and NUMBER.fullmatch(hours)
                and float(hours) == sum(topics[topic]["hours"] for topic in closure), f"Stale totals for path {key}")
        result[key] = {"id": key, "title": name, "roots": [topic for topic in topics if topic in roots], "closure": closure,
                       "hours": float(hours)}
    goals = table_rows(next((block for block in blocks if block.startswith("| Path | Audience |")), ""))
    require(len(goals) == len(result) + 1 and [row[0] for row in goals[1:]] == list(result),
            "Expected a goal and checkpoint for each learning path")
    for row in goals[1:]:
        require(len(row) == 6 and all(row), "Each path needs an audience, goal, outcome, checkpoint and extensions")
        key, audience, goal, outcome, checkpoint, extensions = row
        path = result[key]
        suggested = {edge["id"] for edge in linked_ids(extensions, f"path {key} extensions")}
        require(suggested <= topics.keys() and not suggested.intersection(path["closure"]),
                f"Invalid optional extension in path {key}")
        recommended = {edge["id"] for topic in path["closure"] for edge in topics[topic]["recommended"]}
        optional = (suggested | recommended).difference(path["closure"])
        path.update(
            audience=audience, goal=goal, outcome=outcome, checkpoint=checkpoint,
            recommended=[topic for topic in topics if topic in optional],
        )
    revision = re.search(r"^Curriculum revision (\d+(?:\.\d+)+)\.$", source, re.M)
    require(revision, "A curriculum revision is required for roadmap exports")
    return {"modules": modules, "topics": topics, "paths": result, "stages": STAGES,
            "revision": revision[1], "preparation": float(total[1])}


def combined_closure(roots, topics):
    included = {item for topic in roots for item in topics[topic]["closure"]}
    return [topic for topic in topics if topic in included]


def validate(stages, records, overview, source):
    audit = ROOT / "docs/COURSE_AUDIT_REPORT.md"
    known_findings = set(re.findall(r"^\| ([CSV]\d{2}) \|", audit.read_text(encoding="utf-8"), re.M)) if audit.is_file() else None
    for code, record in records.items():
        fields = record["fields"]
        is_module = "topics" in record
        required = MODULE_FIELDS if is_module else TOPIC_FIELDS
        require(set(fields) == set(required), f"Missing or unexpected fields in {code}")
        require(all(value.strip() for value in fields.values()), f"Empty field in {code}")
        require(fields["Difficulty"] in DIFFICULTIES, f"Unknown difficulty in {code}")
        record["hours"] = read_hours(fields["Hours"].split("/"), code)
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
            if target == PYTHON_EDITOR:
                return f'<a href="{PYTHON_EDITOR}" target="_blank" rel="noopener noreferrer">{label}</a>'
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


def duration(hours):
    total = round(float(hours) * 60)
    whole, minutes = divmod(total, 60)
    return f"{whole}h" + (f" {minutes}m" if minutes else "")


def prose(markdown):
    parts = []
    for block in markdown.strip().split("\n\n"):
        if block.startswith("### "):
            parts.append(f"<h3>{inline(block[4:])}</h3>")
        elif block.startswith("|"):
            header, *rows = table_rows(block)
            caption = {
                "Path": "Learning path goals" if header[1] == "Audience" else "Learning path estimates",
                "ID": "Preparation skills",
                "Dimension and purpose": "Localization evaluation dimensions",
                "Review criterion": "Localized support review rubric",
                "Multimodal dimension": "Multimodal evaluation dimensions",
                "Evidence region": "Northstar receipt and fee chart text equivalent",
                "Evaluation stage": "Where to attribute a multimodal failure",
                "Multimodal review criterion": "Multimodal support review rubric",
                "Source": "Northstar starter evidence",
                "Evidence or memory dimension": "Long-context evaluation dimensions",
                "Memory lifecycle step": "Memory lifecycle audit",
                "Routing label": "Northstar intake label definitions",
                "Evidence situation": "Missing or ambiguous intake evidence",
                "Extraction review criterion": "Structured intake annotation rubric",
                "Local implementation": "Observed order-list runtime and allocations",
                "Code quality dimension": "Code-generation evaluation dimensions",
                "Code review criterion": "Generated patch review rubric",
                "Coordination measure": "Multi-agent coordination metric denominators",
                "Evaluation dimension": "Northstar coordination checks",
                "Coordination review criterion": "Multi-agent human review rubric",
            }.get(header[0], "Course hours by track")
            if header[0] == "Strand":
                header[3:] = TIME_LABELS
                rows = [row[:3] + [duration(value) for value in row[3:]] for row in rows]
            elif header[-1] == "Learner hours":
                header[-1] = "Learner total (hrs)"
                rows = [row[:-1] + [duration(row[-1])] for row in rows]
            parts.append(table(header, rows, caption))
        elif block.startswith("- ") or re.match(r"\d+\. ", block):
            tag = "ul" if block.startswith("- ") else "ol"
            items = [re.sub(r"^(?:-|\d+\.) ", "", line) for line in block.splitlines()]
            parts.append(f"<{tag}>" + "".join(f"<li>{inline(item)}</li>" for item in items) + f"</{tag}>")
        else:
            parts.append(f"<p>{inline(' '.join(block.splitlines()))}</p>")
    return "\n".join(parts)


def time_cards(hours):
    return '<dl class="time-list" aria-label="Time estimates in hours">' + "".join(
        f"<div><dt>{label}</dt><dd>{duration(value)}</dd></div>"
        for label, value in zip(TIME_LABELS, hours, strict=True)
    ) + "</dl>"


def definitions(fields, keys, value_ids=None):
    entries = []
    for label in keys:
        value = inline(fields[label])
        if value_ids and label in value_ids:
            value = f'<span id="{value_ids[label]}">{value}</span>'
        entries.append(f"<div><dt>{label}</dt><dd>{value}</dd></div>")
    return '<dl class="field-list">' + "".join(entries) + "</dl>"


def named_references(text, titles):
    return LINK.sub(lambda match: f"[{titles.get(match[1], match[1])}]({match[2]})", text)


def authored_lesson(topic_id, difficulty, experiment_disclosure):
    source = ROOT / "docs/lessons" / f"{topic_id.lower()}.md"
    if not source.is_file():
        return None
    text = source.read_text(encoding="utf-8")
    rendered = []
    folded_headings = {"Setup and run", "Worked Solutions to Practice", "Knowledge Check Answers"}
    evidence_labels = {"User question.", "Approved reference.", "Actual LLM response.", "Assessment.",
                       "Failure classification."}
    editor_link = inline(f"[Open Python Editor]({PYTHON_EDITOR})") if difficulty == "Beginner" else ""
    disclosure_level = None

    def render_text(chunk):
        nonlocal disclosure_level
        require("```" not in chunk, f"Invalid code fence in {source.name}")
        for block in chunk.strip().split("\n\n"):
            heading = re.fullmatch(r"(#{2,4}) (.+)", block)
            if heading:
                level = len(heading[1]) + 2
                if disclosure_level is not None and level <= disclosure_level:
                    rendered.append("</div></details>")
                    disclosure_level = None
                label = heading[2]
                markup = f"<h{level}>{inline(label)}</h{level}>"
                if label == "Lesson Summary and Next Step" and experiment_disclosure:
                    rendered.append(experiment_disclosure)
                if label in folded_headings:
                    skip = " data-reading-skip" if label != "Setup and run" else ""
                    rendered.append(f'<details class="lesson-disclosure lesson-supplement"{skip}><summary>{markup}</summary>'
                                    '<div class="lesson-disclosure-body">')
                    disclosure_level = level
                else:
                    rendered.append(markup)
            elif block:
                image = re.fullmatch(r"!\[([^\]\n]+)\]\((docs/assets/[a-z0-9/_-]+\.png)\)", block)
                if image:
                    alt, source_path = image.groups()
                    asset = posixpath.relpath(source_path, "docs")
                    rendered.append(f'<p><img src="{escape(asset)}" alt="{escape(alt)}" loading="lazy" '
                                    'style="max-width:100%;height:auto"></p>')
                    continue
                evidence = re.fullmatch(r"\*\*(.+?)\*\* (.+)", block)
                if evidence and evidence[1] in evidence_labels:
                    label, value = evidence.groups()
                    rendered.append(f'<p class="lesson-evidence"><strong>{escape(label)}</strong>'
                                    f' <span>{inline(value)}</span></p>')
                else:
                    rendered.append(prose(block))

    offset = 0
    for match in re.finditer(r"(?m)^```(bash|python|text)\n([\s\S]*?)^```[ \t]*$", text):
        render_text(text[offset:match.start()])
        language, code = match.groups()
        block = f'<pre><code class="language-{language}">{escape(code)}</code></pre>'
        if language == "text":
            block = f'<details class="lesson-disclosure lesson-output"><summary>Expected output</summary>{block}</details>'
        else:
            editor = f"\n    {editor_link}" if language == "python" and editor_link else ""
            block = f'''<div class="lesson-code">
  <div class="lesson-copy-toolbar" hidden>
    <span class="lesson-copy-status" role="status"></span>
    <button type="button" class="lesson-copy-button">Copy Code</button>{editor}
  </div>
  {block}
</div>'''
        rendered.append(block)
        offset = match.end()
    render_text(text[offset:])
    if disclosure_level is not None:
        rendered.append("</div></details>")
    if experiment_disclosure and experiment_disclosure not in rendered:
        rendered.append(experiment_disclosure)
    return '<div class="lesson-section lesson-chapter" data-lesson-search>' + "\n".join(rendered) + "</div>"


def lesson_material(topic, titles, experiment_mappings, archive_revision):
    fields = topic["fields"]
    prerequisites = {key: named_references(fields[key], titles) for key in DEPENDENCIES if fields[key] != "—"}
    preparation = ""
    if prerequisites:
        preparation = f'''
  <details class="lesson-disclosure" data-reading-skip>
    <summary>Prerequisites</summary>
    <div class="lesson-disclosure-body">{definitions(prerequisites, prerequisites)}</div>
  </details>'''
    experiments = original_experiments.lesson_disclosure(experiment_mappings.get(topic["id"], []), archive_revision)
    chapter = authored_lesson(topic["id"], fields["Difficulty"], experiments)
    reading = "\n" + chapter + preparation if chapter is not None else f'''
  <p class="lesson-intro" data-lesson-search>{inline(fields["Why it matters"])}</p>
  <p class="lesson-note"><strong>Lesson outline.</strong> This page contains the planned concepts and activities. The full lesson still needs development.</p>
  <section class="lesson-section lesson-objectives" hidden>
    <h4>Learning objectives</h4>
    <h5>Module objectives</h5>
    <p data-lesson-objectives></p>
  </section>
  <section class="lesson-section lesson-concepts">
    <h4>Key concepts</h4>
    <p data-lesson-search>{inline(fields["Concepts"])}</p>
  </section>{preparation}
  <section class="lesson-section lesson-example">
    <h4>Demonstrations and examples</h4>
    <p data-lesson-search>{inline(fields["Demonstration"])}</p>
    <p class="lesson-note" data-lesson-search><strong>Setup and preparation.</strong> {inline(fields["Implementation readiness"])}</p>
  </section>
  <section class="lesson-section lesson-exercise">
    <h4>Practical exercise</h4>
    <p data-lesson-search>{inline(fields["Exercise and assessment"])}</p>
  </section>
  <section class="lesson-section lesson-checkpoint">
    <h4>Checkpoint</h4>
    <p>Use the exercise above to check your understanding before marking this lesson complete.</p>
  </section>{experiments}'''
    return f'''<div class="topic-material lesson-reading" id="material-{topic['id'].lower()}">{reading}
  <details class="lesson-disclosure" data-reading-skip>
    <summary>Detailed time estimates</summary>
    <div class="lesson-disclosure-body">{time_cards(topic['hours'])}</div>
  </details>
</div>'''


def html_topic(topic, module, titles, experiment_mappings, archive_revision):
    fields = topic["fields"]
    anchor = topic["id"].lower()
    options = "".join(f"<option>{status}</option>" for status in ("Not Started", "In Progress", "Completed"))
    return f'''<details class="topic" id="{anchor}" data-topic="{topic['id']}" data-difficulty="{fields['Difficulty']}"
data-subject="{escape(module['fields']['Subject'])}" data-status="{fields['Status']}" data-track="{module['fields']['Track']}">
  <summary><span class="item-title"><span class="item-id">{topic['id']}</span> {escape(topic['title'])}</span>
    <span class="topic-meta">{fields['Status']} · {duration(topic['hours'][4])}</span></summary>
  <div class="topic-body">
    <nav class="study-breadcrumb" aria-label="Topic location"><ol>
      <li><a href="#detail">Complete Course</a></li>
      <li><a href="#{module["id"].lower()}">{escape(module["title"])}</a></li>
      <li aria-current="location">{escape(topic["title"])}</li>
    </ol></nav>
    <div class="topic-controls"><p>{fields['Difficulty']} · {module['fields']['Track']}</p>
      <label class="js-control" hidden for="progress-{anchor}">Progress <select id="progress-{anchor}" data-progress>{options}</select></label>
      <a class="topic-link" href="#{anchor}">Link to topic</a>
    </div>
    <div class="lesson-layout">
      <aside class="lesson-reader" data-lesson-reader aria-label="Listen" hidden></aside>
      {lesson_material(topic, titles, experiment_mappings, archive_revision)}
    </div>
  </div>
</details>'''


def html_module(module, titles, experiment_mappings, archive_revision):
    fields = module["fields"]
    anchor = module["id"].lower()
    topics = "\n".join(html_topic(topic, module, titles, experiment_mappings, archive_revision)
                       for topic in module["topics"])
    return f'''<details class="module" id="{anchor}">
  <summary><span class="item-title"><span class="item-id">{module['id']}</span> {escape(module['title'])}</span>
    <span class="topic-meta">{len(module['topics'])} topics · {duration(module['hours'][4])}</span>
    <span class="module-progress" hidden data-module-progress></span></summary>
  <div class="module-body">
    <p class="track">{fields['Difficulty']} · {fields['Track']} · {escape(fields['Subject'])}</p>
    {definitions(fields, MODULE_FIELDS[3:8], {"Objectives": f"module-objectives-{anchor}"})}
    {time_cards(module['hours'])}
    {topics}
  </div>
</details>'''


def html_stages(stages, titles, experiment_mappings, archive_revision):
    result = []
    for name, modules in stages.items():
        hours = sum_hours(modules)
        content = "\n".join(html_module(module, titles, experiment_mappings, archive_revision) for module in modules)
        result.append(f'''<details class="stage" {"open" if name == "Beginner" else ""}>
  <summary><span class="stage-title">{name}</span><span class="topic-meta">{len(modules)} modules · {duration(hours[4])}</span></summary>
  <div class="stage-body">{content}</div>
</details>''')
    return "\n".join(result)


def roadmap_view(data):
    paths = "".join(f'<option value="{path["id"]}">{path["id"]} — {escape(path["title"])}</option>'
                    for path in data["paths"].values())
    stages = "".join(f'<option value="{index}">{escape(stage)}</option>' for index, stage in enumerate(data["stages"]))
    return f'''<noscript><p>The interactive roadmap uses JavaScript. Learning Paths under Quick Learning and the Complete Course list the same prerequisites and estimates.</p></noscript>
<div id="roadmap-app" hidden>
  <div id="road-fullscreen-header" class="road-fullscreen-header" hidden>
    <strong id="road-fullscreen-title">Learning Roadmap</strong>
    <button type="button" id="road-fullscreen-close" aria-label="Close fullscreen roadmap">
      <span aria-hidden="true">×</span> Close
    </button>
  </div>
  <p>Select a module to highlight its prerequisites and dependents. Arrows point from prerequisite to dependent. Open the topic study route for the exact lessons and study order.</p>
  <div class="road-controls">
    <div class="road-search">
      <label for="road-search">Find a module or topic</label>
      <input id="road-search" type="search" placeholder="Try M08, citations or calibration" aria-controls="road-results">
      <div class="road-results" id="road-results" hidden aria-label="Search matches"></div>
    </div>
    <label for="road-stage">Find within stage<select id="road-stage"><option value="">All stages</option>{stages}</select></label>
    <label for="road-path">Learning path<select id="road-path"><option value="">Choose A–G</option>{paths}</select></label>
    <label for="road-mode">Graph detail<select id="road-mode"><option value="module">Module overview</option><option value="topic">Topic detail</option></select></label>
  </div>
  <ul id="road-legend" class="road-legend" aria-label="Graph legend"></ul>
  <div class="road-workspace">
    <div class="road-board">
      <div class="road-toolbar">
        <button type="button" id="road-zoom-out" aria-label="Zoom out">−</button>
        <output id="road-zoom" aria-label="Zoom level"></output>
        <button type="button" id="road-zoom-in" aria-label="Zoom in">+</button>
        <button type="button" id="road-reset">Reset view</button>
        <button type="button" id="road-fullscreen-open" aria-haspopup="dialog" aria-controls="roadmap-app">
          <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>
          </svg> Fullscreen
        </button>
        <label><input id="road-focus" type="checkbox" aria-describedby="road-help" disabled> Focus on selection</label>
        <label><input id="road-optional" type="checkbox"> Show all optional links</label>
        <a href="#road-inspector" id="road-jump" hidden>Selection details</a>
      </div>
      <div id="road-viewport" tabindex="0" role="region" aria-label="Learning dependency graph" aria-describedby="road-help"></div>
      <p id="road-help">Module focus emphasizes the selection’s links, including its optional links. Turn off focus to see the full map at normal contrast. Drag to pan, or focus the map and use arrow keys and + or −.</p>
    </div>
    <aside id="road-inspector" class="road-inspector" aria-label="Selected target">
      <div class="road-inspector-head"><h3 id="road-title">Choose a target</h3><button type="button" id="road-clear" hidden>Clear</button></div>
      <p id="road-estimate" role="status" aria-live="polite"></p>
      <div id="road-details"></div>
    </aside>
  </div>
  <div class="road-downloads">
    <label for="road-export">Export graph<select id="road-export">
      <option value="module">Complete module roadmap</option>
      <option value="selection" disabled>Selected path or target</option>
      <option value="topic">Complete topic roadmap</option>
    </select></label>
    <button type="button" id="road-svg">Download SVG</button>
    <button type="button" id="road-png">Download PNG</button>
    <button type="button" id="road-html">Download HTML</button>
    <output id="road-download-status" aria-live="polite"></output>
  </div>
</div>'''


def lesson_link(path_id, topic):
    return f'<a href="#quick-{path_id.lower()}/{topic["id"].lower()}">{escape(topic["title"])}</a>'


def course_topic_link(topic):
    return f'<a href="#{topic["id"].lower()}">{escape(topic["title"])}</a>'


def quick_plan(path, data):
    key = path["id"].lower()
    topics = data["topics"]
    closure = path["closure"]
    steps = []
    for code in closure:
        topic = topics[code]
        steps.append(f'''<li class="plan-step" data-step="{code}">
  <div class="plan-step-heading">{lesson_link(key, topic)}<span>{duration(topic["hours"])}</span></div>
  <p class="lesson-state" data-lesson-state hidden></p>
</li>''')
    optional = "".join(f'<li>{course_topic_link(topics[code])} · {duration(topics[code]["hours"])}</li>'
                       for code in path["recommended"])
    outside = [code for code in topics if code not in closure and code not in path["recommended"]]
    skipped = "".join(f'<li>{course_topic_link(topics[code])}</li>' for code in outside)
    return f'''<article class="quick-plan" id="quick-{key}" data-quick-plan="{path["id"]}">
  <nav class="study-breadcrumb" aria-label="Path location"><ol>
    <li><a href="#quick">Quick Learning</a></li>
    <li aria-current="location">{escape(path["title"])}</li>
  </ol></nav>
  <h3 tabindex="-1">{escape(path["title"])}</h3>
  <p class="path-metrics">{len(closure)} lessons · {duration(path["hours"])} learner time</p>
  <p>{inline(path["goal"])}</p>
  <div class="plan-resume" data-plan-progress="{path["id"]}" data-guided hidden>
    <a class="mode-action" data-plan-next href="#quick-{key}/{closure[0].lower()}">Start Learning</a>
    <p role="status" data-plan-status></p>
  </div>
  <h4>Lessons in order</h4>
  <p>The list includes everything you need to study first. Open a lesson and mark it complete after its checkpoint.</p>
  <ol class="plan-steps">{"".join(steps)}</ol>
  <section class="plan-finish"><h4>Verify your understanding</h4><p>{inline(path["checkpoint"])}</p></section>
  <details><summary>More Options</summary>
    <dl class="plan-brief">
      <div><dt>Who this is for</dt><dd>{inline(path["audience"])}</dd></div>
      <div><dt>Practical outcome</dt><dd>{inline(path["outcome"])}</dd></div>
    </dl>
    <div class="plan-tools">
      <a href="#roadmap-{key}">Open path in Learning Roadmap</a>
      <button type="button" data-plan-download="html" hidden>Download Learning Plan</button>
      <button type="button" data-plan-download="svg" hidden>Download Roadmap SVG</button>
      <button type="button" data-plan-download="png" hidden>Download Roadmap PNG</button>
      <button type="button" data-plan-share hidden>Copy path link</button>
    </div>
    <p class="plan-share-note" data-plan-sharing></p><p role="status" data-plan-message></p>
    <input type="url" data-plan-url hidden readonly aria-label="Shareable learning path URL">
    <details class="plan-visual" data-plan-visual hidden><summary>Dependency diagram</summary><div></div></details>
  </details>
  <details><summary>Recommended extensions ({len(path["recommended"])})</summary>
    <p>These optional links open Complete Course. Their hours are separate from this path.</p>
    {f"<ul>{optional}</ul>" if optional else "<p>There are no additional recommended topics for this path.</p>"}
  </details>
  <details><summary>Other topics you can skip for this goal ({len(outside)})</summary>
    <p>These links open Complete Course.</p>
    {f"<ul>{skipped}</ul>" if skipped else "<p>This route covers every other topic or lists it above as an extension.</p>"}
  </details>
</article>'''


def quick_view(data, learning_paths, titles):
    cards = []
    plans = []
    for key, path in data["paths"].items():
        href = "#quick-" + key.lower()
        cards.append(f'''<article class="path-card">
  <h3><a href="{href}">{escape(path["title"])}</a></h3>
  <p class="path-metrics">{len(path["closure"])} lessons · {duration(path["hours"])} learner time</p>
  <p>{inline(path["goal"])}</p><p><strong>For</strong> {inline(path["audience"])}</p>
  <p><strong>What you’ll build</strong> {inline(path["outcome"])}</p>
  <details><summary>Prerequisites and checkpoint</summary>
    <p>Required foundations are included in the lesson sequence.</p>
    <p><strong>Final checkpoint</strong> {inline(path["checkpoint"])}</p>
  </details>
  <a class="mode-action" href="{href}" aria-label="Open {escape(path["title"])} learning plan">Open learning plan</a>
</article>''')
        plans.append(quick_plan(path, data))
    reference = prose(named_references(learning_paths.replace("**Complete Learning**", "**Complete Course**"), titles)).replace(
        "<h3>Preparation / Getting Started</h3>", '<h3 id="preparation" tabindex="-1">Preparation / Getting Started</h3>')
    return f'''<div id="quick-catalog">
  <p class="mode-tagline">Learn what you need. Skip what you don't.</p>
  <p>Choose a goal for a route with every required topic and checkpoint. Plans use the full topic material and share your progress with Complete Course.</p>
  <p><a href="#paths">Compare all learning paths and preparation options</a></p>
  <div class="path-grid">{"".join(cards[1:-1])}</div>
  <h3>Broader plans</h3><div class="path-grid">{"".join(cards[:1] + cards[-1:])}</div>
  <details id="paths" class="course-reference">
    <summary>Learning Paths and preparation</summary>
    <p>Topic and module links in this comparison open Complete Course. Choose a path above to study in Quick Learning.</p>
    {reference}
    <p><a href="#roadmap">Open the Learning Roadmap</a></p>
  </details>
</div>
{"".join(plans)}
<article class="guided-lesson" id="guided-lesson" hidden>
  <nav class="study-breadcrumb" aria-label="Lesson location"><ol>
    <li><a href="#quick">Quick Learning</a></li>
    <li><a id="guided-path" href="#quick"></a></li>
    <li id="guided-position" aria-current="location"></li>
  </ol></nav>
  <header class="guided-header">
    <h3 id="guided-title" tabindex="-1" aria-describedby="guided-position"></h3>
    <p id="guided-estimate" class="path-metrics"></p>
    <div class="guided-progress">
      <label id="guided-progress-label" for="guided-progress"></label>
      <progress id="guided-progress" value="0" aria-labelledby="guided-progress-label"></progress>
    </div>
  </header>
  <div class="lesson-layout">
    <aside class="lesson-reader" data-guided-reader aria-label="Listen" hidden></aside>
    <div id="guided-material"></div>
  </div>
  <p id="guided-status" role="status"></p>
  <nav class="guided-actions" aria-label="Lesson actions">
    <a id="guided-previous" href="#quick" hidden>Previous Lesson</a>
    <button id="guided-complete" class="mode-action" type="button">Mark as Completed</button>
    <a id="guided-next" href="#quick" hidden>Next Lesson</a>
    <a id="guided-back" href="#quick">Back to Learning Path</a>
  </nav>
  <dialog id="navigator-dialog" aria-labelledby="navigator-title" aria-describedby="navigator-help">
    <header class="navigator-header">
      <div><h2 id="navigator-title" tabindex="-1">Learning Navigator</h2><p id="navigator-path"></p></div>
      <div class="navigator-controls">
        <button type="button" id="navigator-minimize">Minimize</button>
        <button type="button" id="navigator-close" aria-label="Close Learning Navigator">×</button>
      </div>
    </header>
    <div class="navigator-controls">
      <button type="button" id="navigator-zoom-out" aria-label="Zoom out">−</button>
      <output id="navigator-zoom" aria-label="Zoom level">100%</output>
      <button type="button" id="navigator-zoom-in" aria-label="Zoom in">+</button>
      <button type="button" id="navigator-center">Find current lesson</button>
    </div>
    <p id="navigator-help">Scroll or drag the map to move around. When the map has focus, use arrow keys to pan and + or − to zoom. Select a lesson to open it.</p>
    <ul class="navigator-legend" aria-label="Connection types">
      <li class="navigator-order">Dashed line: lesson order</li>
      <li class="navigator-required">Solid arrow: required prerequisite</li>
      <li class="navigator-optional">Dotted arrow: recommended or conditional prerequisite</li>
    </ul>
    <div id="navigator-viewport" tabindex="0" role="region" aria-label="Learning path map">
      <div id="navigator-surface"><div id="navigator-map"></div></div>
    </div>
  </dialog>
</article>
<noscript><p>Guided lesson links use JavaScript. Use <a href="#detail">Complete Course</a> to read the same topics.</p></noscript>'''


def complete_view(data, detailed):
    core, all_topics = data["paths"]["A"], data["paths"]["G"]
    elective = all_topics["hours"] - core["hours"]
    return f'''<p class="mode-tagline">From beginner to advanced evaluation engineering.</p>
<div class="complete-strands">
  <a href="#preparation"><strong>Optional preparation</strong><span>{duration(data["preparation"])} · readiness exercises</span></a>
  <a href="#m01"><strong>Core curriculum</strong><span>{duration(core["hours"])} · {len(core["closure"])} topics · foundations to production</span></a>
  <a href="#m16"><strong>Optional electives</strong><span>{duration(elective)} · {len(all_topics["closure"]) - len(core["closure"])} specialized topics</span></a>
</div>
<div class="plan-resume" data-plan-progress="A" hidden>
  <p role="status" data-plan-status></p><a class="mode-action" data-plan-next href="#m01-t01">Start core curriculum</a>
</div>
<p><a href="#roadmap-full">Open the full dependency roadmap</a></p>
<p id="return-to-plan" hidden><a href="#quick">Return to Quick Learning</a></p>
{detailed}'''


def branding_ready():
    return all((BRANDING / name).is_file() for name in BRAND_FILES)


def brand_uri(name):
    return "data:image/png;base64," + b64encode((BRANDING / name).read_bytes()).decode("ascii")


def brand_links(embedded=False):
    if not branding_ready():
        return ""
    ico = brand_uri("icon-48.png") if embedded else "assets/branding/favicon.ico"
    icon32 = brand_uri("icon-32.png") if embedded else "assets/branding/icon-32.png"
    touch = brand_uri("icon-180.png") if embedded else "assets/branding/icon-180.png"
    return (f'<link rel="icon" href="{ico}">\n<link rel="icon" type="image/png" sizes="32x32" href="{icon32}">\n'
            f'<link rel="apple-touch-icon" sizes="180x180" href="{touch}">')


def academy_header(embedded=False):
    icon = ""
    if branding_ready():
        source = brand_uri("icon-48.png") if embedded else "assets/branding/icon-48.png"
        icon = f'<img src="{source}" width="32" height="32" alt="">'
    prefix = "" if embedded else "master-curriculum.html"
    return f'''<header class="academy-top"><div class="academy-wrap">
  <a class="academy-brand" href="index.html">{icon}<span>TestNeural LLM Academy</span></a>
  <div class="academy-top-actions">
    <nav class="academy-top-modes" aria-label="Learning modes">
      <a href="{prefix}#quick">Quick Learning</a>
      <a href="{prefix}#detail">Complete Course</a>
    </nav>
    <button type="button" data-theme-toggle>Dark theme</button>
  </div>
</div></header>'''


ACADEMY_MENU = '''<summary><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor"
stroke-width="1.7" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span class="menu-label">Course navigation</span></summary>'''
ACADEMY_FOOTER = '''<footer class="academy-wrap academy-footer">
  <span>TestNeural LLM Academy · Learn • Evaluate • Build</span><span>Developed by: Amit Baderia</span>
</footer>'''
ACADEMY_NAVIGATION = (
    ("quick", "Quick Learning", "zap", "M13 2 4 14h7l-1 8 10-12h-7V2Z"),
    ("detail", "Complete Course", "book-open",
     "M12 7c-2-2-5-3-10-2v14c5-1 8 0 10 2 2-2 5-3 10-2V5c-5-1-8 0-10 2Zm0 0v14"),
    ("roadmap", "Learning Roadmap", "map", "M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3V6Zm6-3v15m6-12v15"),
    ("overview", "About the Course", "graduation-cap",
     "m2 9 10-5 10 5-10 5-10-5Zm4 2v5c3 3 9 3 12 0v-5m4-2v7"),
    ("resources", "Resources", "folder-open",
     "M3 20V6a2 2 0 0 1 2-2h4l2 2h7a2 2 0 0 1 2 2v2M3 20h16l3-10H6L3 20Z"),
)


def academy_navigation(homepage=False):
    links = []
    for key, label, icon, path in ACADEMY_NAVIGATION:
        fragment = "roadmap-full" if homepage and key == "roadmap" else key
        href = f"master-curriculum.html#{fragment}" if homepage else f"#{fragment}"
        link_id = "" if homepage else f' id="tab-{key}"'
        links.append(
            f'<a{link_id} href="{href}"><svg class="academy-nav-icon" data-icon="{icon}" '
            'viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" '
            'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{path}"/></svg>{label}</a>'
        )
    return "\n".join(links)


def analytics_loader(forward=None):
    route = f' data-analytics-forward="{escape(forward)}"' if forward else ""
    return f'<script src="assets/analytics.js" defer{route}></script>'


def render_home(data):
    cards = []
    for key in "BCDEF":
        path = data["paths"][key]
        link = "#quick-" + key.lower()
        cards.append(f'''<article class="academy-card">
          <h3>{escape(path["title"])}</h3>
          <p class="card-time">{duration(path["hours"])} learner time · {len(path["closure"])} topics</p>
          <p>{inline(path["goal"])}</p>
          <a class="academy-button secondary" href="master-curriculum.html{link}">Open learning plan</a>
        </article>''')
    banner = ('<img src="assets/branding/academy-logo-banner.png" width="2172" height="724" '
              'alt="TestNeural LLM Academy. Learn, Evaluate, Build. Developed by Amit Baderia.">') if branding_ready() else (
                  "<strong>TestNeural LLM Academy · Learn • Evaluate • Build</strong>")
    tokens = {
        "BRAND_ICONS": brand_links(), "HEADER": academy_header(), "MENU": ACADEMY_MENU,
        "NAVIGATION": academy_navigation(homepage=True),
        "BANNER": banner, "PATHS": "".join(cards), "FOOTER": ACADEMY_FOOTER,
        "ANALYTICS_LOADER": analytics_loader(),
        "CORE": duration(data["paths"]["A"]["hours"]), "PREP": duration(data["preparation"]),
        "ELECTIVE": duration(data["paths"]["G"]["hours"] - data["paths"]["A"]["hours"]),
    }
    return re.sub(r"@([A-Z_]+)@", lambda match: tokens[match[1]], HOME_TEMPLATE.read_text(encoding="utf-8"))


def render_lesson_address(topic):
    anchor = topic["id"].lower()
    title = escape(topic["title"])
    target = f"master-curriculum.html#{anchor}"
    return f'''<!doctype html>
<!-- Generated by docs/generate_master_curriculum.py. The curriculum contains the lesson. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · TestNeural LLM Academy</title>
<link rel="canonical" href="https://llmacademy.testneural.in/{target}">
{analytics_loader(target)}
</head>
<body>
<main>
<h1>{title}</h1>
<p><a href="{target}">Open this lesson in the curriculum</a></p>
</main>
</body>
</html>
'''


def overview_view(section, data):
    blocks = section.strip().split("\n\n")
    reading = prose("\n\n".join(block for block in blocks if not block.startswith("| Strand |")))
    hours_table = prose(next(block for block in blocks if block.startswith("| Strand |")))
    core, full = data["paths"]["A"], data["paths"]["G"]
    return f'''<div class="overview-grid">
  <div class="overview-reading">{reading}</div>
  <aside class="overview-support" aria-label="Course summary and progress">
    <section class="overview-card">
      <h3>Course at a glance</h3>
      <dl class="overview-stats">
        <div><dt>Modules</dt><dd>{len(data["modules"])}</dd></div>
        <div><dt>Topics</dt><dd>{len(data["topics"])}</dd></div>
        <div><dt>Core study</dt><dd>{duration(core["hours"])}</dd></div>
        <div><dt>Electives</dt><dd>{duration(full["hours"] - core["hours"])}</dd></div>
      </dl>
      <p><a href="#course-hours">See the time breakdown</a></p>
    </section>
    <section class="overview-card">
      <h3>First time here?</h3>
      <p>Check your readiness before starting the foundations.</p>
      <p><a href="#preparation">Optional preparation · {duration(data["preparation"])}</a></p>
    </section>
    <section class="overview-card" id="course-progress" aria-labelledby="course-progress-title" hidden>
      <h3 id="course-progress-title">Your learning progress</h3>
      <p id="progress-label"></p>
      <progress id="progress-bar" max="{len(data["topics"])}" value="0" aria-labelledby="progress-label"></progress>
      <div class="overview-resume" data-plan-progress="selected" data-guided hidden>
        <p data-resume-path></p>
        <p role="status" data-plan-status></p>
        <a class="mode-action" data-plan-next href="#m01-t01">Continue Learning</a>
      </div>
      <p id="storage-note">Progress stays in this browser. Export a backup to move it to another device.</p>
      <details class="progress-tools">
        <summary>Manage progress</summary>
        <button type="button" id="export-progress">Export JSON</button>
        <label for="import-progress">Import progress JSON</label>
        <input id="import-progress" type="file" accept=".json,application/json">
        <p id="import-status" role="status"></p>
        <fieldset id="import-preview" hidden>
          <legend>Review import</legend>
          <label><input type="radio" name="import-mode" value="merge" checked> Merge with current progress</label>
          <label><input type="radio" name="import-mode" value="replace"> Replace current progress</label>
          <p id="import-summary" aria-live="polite"></p>
          <button type="button" id="apply-import">Apply import</button>
          <button type="button" id="cancel-import">Cancel</button>
        </fieldset>
        <button type="button" id="reset-progress">Reset progress</button>
      </details>
    </section>
  </aside>
</div>
<section id="course-hours" aria-labelledby="course-hours-title">
  <h3 id="course-hours-title">Course time breakdown</h3>
  {hours_table}
</section>'''


def render(title, sections, stages, data, experiment_catalog):
    modules = [module for group in stages.values() for module in group]
    topics = [topic for module in modules for topic in module["topics"]]
    titles = {item["id"]: item["title"] for item in (*modules, *topics)}
    revision, entries = experiment_catalog
    detailed = filters(modules) + html_stages(stages, titles, original_experiments.by_topic(entries), revision)
    views = {
        "quick": quick_view(data, sections["Learning paths"], titles),
        "detail": complete_view(data, detailed),
        "roadmap": roadmap_view(data),
        "overview": overview_view(sections["Course overview"], data),
        "resources": f'''<p id="coverage"><a href="index.html#library">Published examples and downloads</a> ·
  <a href="concepts.html">Concepts reference</a> · <a href="#original-practical-tests">Original Practical Tests Library</a></p>
{original_experiments.library(entries, revision, titles)}
<section aria-labelledby="instructor-resources-title">
  <h3 id="instructor-resources-title">Instructor Resources</h3>
  <details id="teaching" class="course-reference">
    <summary>Teaching Plan</summary>
    {prose(sections["Teaching plan"])}
  </details>
</section>''',
    }
    panels = "\n".join(f'<section class="panel" id="{key}"><h2>{label}</h2>\n{views[key]}\n</section>'
                       for key, label, _, _ in ACADEMY_NAVIGATION)
    branded_data = {**data, "brandIcon": brand_uri("icon-48.png") if branding_ready() else ""}
    payload = json.dumps(branded_data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    roadmap_script = ROADMAP_SCRIPT.read_text(encoding="utf-8")
    modes_script = MODES_SCRIPT.read_text(encoding="utf-8")
    navigator_script = NAVIGATOR_SCRIPT.read_text(encoding="utf-8")
    progress_script = PROGRESS_SCRIPT.read_text(encoding="utf-8")
    reader_script = READER_SCRIPT.read_text(encoding="utf-8")
    academy_css = (ASSETS / "academy.css").read_text(encoding="utf-8")
    academy_js = (ASSETS / "academy.js").read_text(encoding="utf-8")
    return f'''<!doctype html>
<!-- Generated from MASTER_CURRICULUM.md and the original experiment catalog by docs/generate_master_curriculum.py. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Explore the LLM Evaluation Engineering curriculum, including focused learning paths, topic prerequisites, and an interactive roadmap.">
<title>{escape(title)} · TestNeural LLM Academy</title>
{brand_links(embedded=True)}
<link rel="canonical" href="https://llmacademy.testneural.in/master-curriculum.html">
{analytics_loader()}
<style>{CSS}{ROADMAP_CSS}{MODES_CSS}{academy_css}</style>
</head>
<body class="academy-page">
<a class="skip-link" href="#main">Skip to curriculum</a>
{academy_header(embedded=True)}
<div class="academy-wrap academy-layout">
  <div class="academy-sidebar-column">
    <details class="academy-sidebar" open>
      {ACADEMY_MENU}
      <nav id="tabs" aria-label="Curriculum views">{academy_navigation()}</nav>
    </details>
    <aside class="navigator-dock" aria-label="Learning Navigator" hidden>
      <button type="button" id="navigator-launch" aria-label="Learning Navigator" aria-haspopup="dialog" aria-controls="navigator-dialog">
        <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M6 6h5l3 6h4M6 18h5l3-6"/><circle cx="4" cy="6" r="2"/><circle cx="4" cy="18" r="2"/><circle cx="20" cy="12" r="2"/>
        </svg>
        <span class="navigator-label">Learning Navigator</span>
      </button>
    </aside>
  </div>
<main id="main" class="academy-main" tabindex="-1">
  <header class="curriculum-heading">
    <h1>LLM Evaluation Engineering</h1>
    <p>{len(modules)} modules · {len(topics)} topics · {duration(data["paths"]["A"]["hours"])} core study · <a href="#course-progress">Your progress</a></p>
  </header>
  <nav class="study-mode-picker" aria-label="Learning mode">
    <a href="#quick">Quick Learning</a>
    <a href="#detail">Complete Course</a>
  </nav>
  {panels}
</main>
</div>
{ACADEMY_FOOTER}
<script id="roadmap-data" type="application/json">{payload}</script>
<script>
const portableCurriculum = "<!doctype html>\\n" + document.documentElement.outerHTML
  .replace(/<script src="assets\\/analytics\\.js"[^>]*><\\/script>/, "");
{progress_script}
{SCRIPT}
{roadmap_script}
{modes_script}
{navigator_script}
LearningProgress.bindControls(progressState, CurriculumRoadmap.saveBlob);
followCurrentRoute(false, initialRoute);
{reader_script}
{academy_js}
</script>
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
    parser.add_argument("--experiment-coverage", action="store_true", help="Validate and report original experiment coverage")
    args = parser.parse_args()
    try:
        source = SOURCE.read_text(encoding="utf-8")
        curriculum = parse(source)
        topic_ids = curriculum[-1]["topics"].keys()
        experiments = original_experiments.load(topic_ids, source)
        if args.experiment_coverage:
            print(json.dumps(original_experiments.coverage(experiments[1], topic_ids), indent=2))
            if not args.check:
                return
        report = REPORT_SOURCE.read_text(encoding="utf-8").replace("</head>", f"    {analytics_loader()}\n</head>", 1)
        outputs = {OUTPUT: render(*curriculum, experiments), HOME: render_home(curriculum[-1]),
                   OUTPUT.with_name("full-results.html"): report}
        lesson_outputs = {
            OUTPUT.with_name(f"lesson-{topic_id.lower()}.html"): render_lesson_address(topic)
            for topic_id, topic in curriculum[-1]["topics"].items()
        }
        stale_addresses = set(OUTPUT.parent.glob("lesson-*.html")) - lesson_outputs.keys()
        require(not stale_addresses, "Remove obsolete lesson addresses: " +
                ", ".join(sorted(path.name for path in stale_addresses)))
        outputs.update(lesson_outputs)
        if not branding_ready():
            missing = ", ".join(name for name in BRAND_FILES if not (BRANDING / name).is_file())
            print(f"Using text branding. Missing assets: {missing}")
        for path, content in outputs.items():
            if args.check:
                require(path.is_file() and path.read_bytes() == content.encode("utf-8"),
                        f"{path.name} is stale. Run python3 docs/generate_master_curriculum.py.")
            else:
                path.write_bytes(content.encode("utf-8"))
                print(f"Generated {path.relative_to(ROOT)}.")
        if args.check:
            print("Curriculum, homepage, lesson addresses and published report match their sources.")
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
.skip-link { position:fixed; z-index:9; top:.5rem; left:.5rem; padding:.5rem .75rem; background:var(--surface); transform:translateY(-150%); }
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
.topic-controls { display:flex; align-items:center; gap:.2rem .75rem; flex-wrap:wrap; border-top:1px solid var(--line); }
.topic-controls p { margin:0; }
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

ROADMAP_CSS = """
#roadmap > h2 { margin-bottom:.5rem; }
#roadmap-app > p { max-width:75ch; }
.road-controls { display:grid; grid-template-columns:2fr 1fr 1.35fr 1fr; gap:.65rem; align-items:start; }
.road-search { position:relative; }
.road-results { position:absolute; z-index:2; top:100%; width:max(100%, min(24rem, 90vw)); max-height:22rem;
  overflow:auto; padding:.35rem .55rem .55rem; background:white; border:1px solid var(--line);
  border-radius:.45rem; box-shadow:0 6px 22px #142e4526; }
.road-results p { margin:.25rem .4rem; color:var(--muted); font-size:.86rem; }
.road-legend { display:flex; flex-wrap:wrap; gap:.3rem 1rem; padding:0; margin:.9rem 0 .65rem; list-style:none; }
.road-legend li { display:inline-flex; align-items:center; gap:.34rem; margin:0; color:#344b5c; font-size:.85rem; }
.road-stage-key { width:.85rem; height:.85rem; border:1px solid var(--key-ink); border-radius:.2rem; background:var(--key); }
.road-edge-key { width:1.45rem; border-top:2px solid #254f71; }
.road-edge-recommended { border-top-style:dashed; border-color:#66448c; }
.road-edge-conditional { border-top-style:dotted; border-color:#8a4715; }
.road-edge-downstream { border-color:#12634e; }
.road-workspace { display:grid; grid-template-columns:minmax(0, 2.7fr) minmax(17rem,1fr); gap:.75rem; }
.road-workspace:has(#road-clear[hidden]) { grid-template-columns:1fr; }
.road-board, .road-inspector { min-width:0; background:#fff; border:1px solid var(--line); border-radius:.65rem; }
.road-toolbar { display:flex; flex-wrap:wrap; align-items:center; gap:.4rem .55rem; padding:.6rem; }
.road-toolbar button { padding:.28rem .55rem; }
.road-toolbar output { min-width:3rem; text-align:center; font-variant-numeric:tabular-nums; }
.road-toolbar label { display:inline-flex; gap:.32rem; align-items:center; font-size:.84rem; font-weight:600; }
.road-toolbar input { display:inline; width:1rem; height:1rem; min-height:0; accent-color:var(--accent); }
#road-jump { margin-left:auto; font-size:.84rem; }
#road-viewport { height:clamp(23rem,58vh,40rem); position:relative; overflow:hidden; cursor:grab;
  touch-action:none; border-block:1px solid var(--line); background:#f8fafc; }
#road-viewport.panning { cursor:grabbing; user-select:none; }
#road-viewport > svg { position:absolute; top:0; left:0; max-width:none; transform-origin:0 0; }
#road-viewport [data-node] { cursor:pointer; text-decoration:none; }
#road-viewport [data-node]:hover rect, #road-viewport [data-node]:focus-visible rect,
#road-viewport [data-node].road-reference rect { stroke:#086f9c; stroke-width:4; }
#road-help { font-size:.86rem; color:var(--muted); margin:.45rem .72rem .6rem; }
.road-inspector { padding:.8rem; max-height:calc(clamp(23rem,58vh,40rem) + 6rem); overflow:auto; }
.road-inspector-head { display:flex; gap:.65rem; align-items:start; justify-content:space-between; }
.road-inspector h3 { margin:0; line-height:1.3; }
.road-inspector h4 { margin-top:.95rem; font-size:.92rem; }
.road-inspector h5 { margin:.65rem 0 .28rem; font-size:.84rem; }
.road-dependency { border-inline-start:3px solid #254f71; margin:.55rem 0; padding:.12rem .48rem .35rem; }
.road-downstream { border-inline-start-color:#12634e; }
.road-dependency h5 .road-edge-key { display:inline-block; margin-inline-end:.38rem; vertical-align:middle; }
.road-inspector .road-current { background:#eaf2fd; color:#102c4a; padding:.35rem .55rem; font-weight:700; border-radius:.3rem; }
.road-inspector p { margin:.36rem 0; font-size:.89rem; }
#road-estimate { font-weight:700; color:#19553a; }
.road-list { margin:.25rem 0; padding:0; list-style:none; }
.road-list li { margin:.2rem 0; }
.road-item { display:flex; align-items:baseline; gap:.45rem; width:100%; padding:.3rem .4rem; border:0; text-align:left;
  font-size:.86rem; font-weight:500; line-height:1.4; }
.road-item strong { color:#245377; white-space:nowrap; }
.road-item:focus-visible, [data-back]:focus-visible { outline:2px solid #086f9c; outline-offset:1px; }
.road-inspector .road-condition { margin:.15rem .4rem .45rem; color:#784113; }
.road-empty { color:var(--muted); }
.road-route { margin-top:.9rem; }
.road-route summary { padding:.45rem .55rem; font-size:.9rem; }
.road-route ol { margin:.25rem .3rem .6rem; padding-left:1.5rem; font-size:.85rem; }
.road-route-hours { margin-left:.4rem; color:var(--muted); }
.road-downloads { display:flex; flex-wrap:wrap; align-items:end; gap:.55rem; margin-top:.85rem; }
.road-downloads output { flex:1 1 100%; font-size:.87rem; color:var(--muted); }
#road-fullscreen-open, #road-fullscreen-close { display:inline-flex; align-items:center; gap:.35rem; min-height:2.75rem; }
#road-fullscreen-open svg { flex:none; }
.road-fullscreen-header { display:flex; align-items:center; justify-content:space-between; gap:1rem;
  position:sticky; top:0; z-index:3; background:var(--page); }
.road-fullscreen-header button span { font-size:1.25em; line-height:1; }
html.roadmap-fullscreen, html.roadmap-fullscreen body { overflow:hidden; overscroll-behavior:none; }
#roadmap-app.is-fullscreen {
  display:flex; flex-direction:column; gap:.65rem; margin:0; border:0; max-width:none; max-height:none;
  width:100%; height:100%; overflow:auto; overscroll-behavior:contain; background:var(--page); color:var(--text);
  padding:max(.65rem, env(safe-area-inset-top)) max(.65rem, env(safe-area-inset-right))
    max(.65rem, env(safe-area-inset-bottom)) max(.65rem, env(safe-area-inset-left));
}
#roadmap-app.is-fullscreen-fallback { position:fixed; inset:0; z-index:100; height:100vh; height:100dvh; }
#roadmap-app.is-fullscreen > * { flex-shrink:0; }
#roadmap-app.is-fullscreen > p, #roadmap-app.is-fullscreen #road-fullscreen-open { display:none; }
#roadmap-app.is-fullscreen .road-legend, #roadmap-app.is-fullscreen .road-downloads { margin:0; }
#roadmap-app.is-fullscreen .road-workspace { flex:1 0 16rem; grid-template-rows:minmax(0,1fr); }
#roadmap-app.is-fullscreen .road-workspace:has(#road-clear[hidden]) .road-inspector { display:none; }
#roadmap-app.is-fullscreen .road-board { display:flex; flex-direction:column; min-height:0; }
#roadmap-app.is-fullscreen #road-viewport { flex:1 1 0; min-height:7rem; height:auto; }
#roadmap-app.is-fullscreen .road-inspector { max-height:none; }
@media (max-width:850px) {
  .road-controls { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .road-workspace { grid-template-columns:1fr; }
  .road-inspector { max-height:none; }
  #roadmap-app.is-fullscreen .road-workspace { flex:none; grid-template-rows:clamp(20rem, 62dvh, 38rem) auto; }
  #roadmap-app.is-fullscreen .road-inspector { overflow:visible; }
}
@media (max-width:440px) {
  .road-controls { grid-template-columns:1fr; }
  .road-results { width:100%; }
  #road-viewport { height:22rem; }
  #roadmap-app.is-fullscreen .road-controls { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media print {
  #roadmap { display:none !important; }
}
"""

MODES_CSS = """
.path-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.85rem; }
.mode-tagline { font-size:1.13rem; font-weight:700; }
.path-card,.quick-plan,.plan-resume,.complete-strands a { background:#fff; border:1px solid var(--line); border-radius:.7rem; }
.path-card { display:flex; align-items:start; flex-direction:column; padding:1rem; border-top:4px solid #43886c; }
.path-card:nth-child(3n+2) { border-top-color:#6c68a3; }
.path-card:nth-child(3n) { border-top-color:#377498; }
.path-card h3,.quick-plan h3 { margin:0; }
.path-card p { margin:.35rem 0; }
.path-card details { width:100%; margin:.45rem 0; background:#f6f8fa; }
.path-card details p { margin:.4rem .7rem; }
.path-card .mode-action { margin-top:auto; }
.mode-action { display:inline-block; padding:.35rem .7rem; background:#075a51; color:white; font-weight:700;
  border-radius:.38rem; text-decoration:none; }
.mode-action:hover { background:#06483f; }
.path-metrics { font-weight:750; color:#174e44; }
.quick-plan { padding:clamp(.8rem,3vw,1.45rem); margin:1rem 0; scroll-margin-top:1rem; }
.quick-plan > h3 { font-size:clamp(1.35rem,3vw,1.85rem); }
.plan-brief dt { font-weight:700; }
.plan-brief dd { margin:0 0 .5rem; }
.plan-tools { display:flex; align-items:center; flex-wrap:wrap; gap:.55rem .75rem; }
.plan-tools a { font-weight:700; }
.plan-tools button { padding:.35rem .6rem; }
.plan-share-note { color:var(--muted); font-size:.9rem; }
.plan-resume { padding:.6rem .75rem; margin:.7rem 0; background:#eff7f3; }
.plan-resume p { margin:.15rem 0 .45rem; font-weight:650; }
.plan-steps { padding-left:1.6rem; }
.plan-step { padding:.75rem .85rem; border-bottom:1px solid var(--line); }
.plan-step.is-complete { background:#f1f8f2; }
.plan-step p { margin:.25rem 0; }
.plan-step-heading { display:flex; flex-wrap:wrap; gap:.3rem 1rem; justify-content:space-between; align-items:baseline; }
.plan-step-heading span { font-weight:700; white-space:nowrap; }
.plan-finish { padding:.65rem .85rem; margin:.8rem 0; background:#eaf0fa; border-radius:.5rem; }
.plan-finish h4 { margin:0; }
.quick-plan details { margin:.6rem 0; }
.quick-plan details > p { margin:.4rem .8rem; }
.plan-visual > div { overflow:auto; }
.plan-visual svg { display:block; max-width:100%; min-width:42rem; height:auto; }
.complete-strands { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.7rem; }
.complete-strands a { display:grid; padding:.65rem .8rem; }
.complete-strands span { color:var(--ink); font-size:.91rem; }
@media(max-width:640px) { .path-grid,.complete-strands { grid-template-columns:1fr; } }
@media print {
  .study-mode-picker,.plan-resume,.plan-tools { display:none !important; }
}
"""

SCRIPT = """
"use strict";

const tabs = Array.from(document.querySelectorAll("#tabs a"));
const modeLinks = document.querySelectorAll(".study-mode-picker a");
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
  ...Array.from(topic.querySelectorAll(".topic-material [data-lesson-search], .topic-material .field-list dd")).map(field => field.textContent)
].join(" ").toLocaleLowerCase()]));

function activate(tab) {
  tabs.forEach((item, index) => {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
    panels[index].hidden = !selected;
  });
  for (const link of modeLinks) {
    if (link.hash === tab.hash) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
  document.dispatchEvent(new CustomEvent("curriculum-tab", {detail: tab.hash}));
}

function openTab(tab) {
  activate(tab);
  if (location.hash !== tab.hash) navigateCurriculum(tab.hash);
}

const tabList = document.getElementById("tabs");
tabList.setAttribute("role", "tablist");
tabList.setAttribute("aria-orientation", "vertical");
tabs.forEach((tab, index) => {
  tab.setAttribute("role", "tab");
  tab.setAttribute("aria-controls", panels[index].id);
  panels[index].setAttribute("role", "tabpanel");
  panels[index].setAttribute("aria-labelledby", tab.id);
  panels[index].tabIndex = 0;
  tab.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    openTab(tab);
  });
  tab.addEventListener("keydown", event => {
    const offsets = {ArrowUp: -1, ArrowDown: 1, ArrowLeft: -1, ArrowRight: 1,
                     Home: -index, End: tabs.length - 1 - index};
    if (event.key === " ") {
      event.preventDefault();
      openTab(tab);
    } else if (Object.hasOwn(offsets, event.key)) {
      const next = tabs[(index + offsets[event.key] + tabs.length) % tabs.length];
      event.preventDefault();
      openTab(next);
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

function followHash(focus, hash = location.hash) {
  const roadRoute = /^#roadmap-(?:[a-g]|full)$/.test(hash);
  const studyRoute = guidedLearning.resolve(hash);
  const target = document.getElementById(roadRoute ? "roadmap" : studyRoute?.overview.slice(1) || hash.slice(1));
  if (!target) return false;
  const panel = target.closest(".panel");
  if (!panel) return false;
  activate(tabs[panels.indexOf(panel)]);
  const lesson = guidedLearning.show(hash, studyRoute);
  document.dispatchEvent(new CustomEvent("curriculum-route", {detail: hash}));
  if (lesson) {
    if (focus) lesson.querySelector("h3").focus({preventScroll: true});
    lesson.scrollIntoView({block: "start"});
    return true;
  }
  if (target.matches(".topic, .module") && target.hidden) clearFilters();
  for (let disclosure = target.closest("details"); disclosure; disclosure = disclosure.parentElement.closest("details")) {
    disclosure.open = true;
  }
  if (target.matches(".topic, .module")) {
    if (focus) target.querySelector("summary").focus({preventScroll: true});
    target.scrollIntoView({block: "start"});
  } else if (target.matches(".quick-plan, #preparation, #paths, #teaching, #coverage, #course-progress, #original-practical-tests, .original-test")) {
    if (focus) {
      const heading = target.querySelector("h3, summary") || target;
      if (heading.tagName !== "SUMMARY") heading.tabIndex = -1;
      heading.focus({preventScroll: true});
    }
    target.scrollIntoView({block: "start"});
  }
  return true;
}

// Cloudflare's Path dimension groups fragments on the same document URL.
// Give a lesson a real static address while keeping the current reader mounted.
function curriculumAddress(hash) {
  if (location.origin !== "https://llmacademy.testneural.in") return null;
  const guided = guidedLearning.resolve(hash);
  const target = document.getElementById(hash.slice(1));
  if (!guided && !target?.closest(".panel") && !/^#roadmap-(?:[a-g]|full)$/.test(hash)) return null;
  const topic = guided?.topic || target?.dataset.topic;
  const page = topic ? "lesson-" + topic.toLowerCase() + ".html" : "master-curriculum.html";
  return new URL(page + location.search + hash, location.href);
}

function navigateCurriculum(hash) {
  const address = curriculumAddress(hash);
  if (address?.href === location.href) return followHash(true, hash);
  if (address) {
    try {
      history.pushState(history.state, "", address.href);
    } catch {
      // The fragment still works if the browser disallows History API updates.
      if (location.hash !== hash) location.hash = hash;
      else return followHash(true, hash);
      return true;
    }
    return followHash(true, hash);
  }
  if (location.hash !== hash) location.hash = hash;
  else return followHash(true, hash);
  return true;
}

function followCurrentRoute(focus, hash = location.hash) {
  const address = curriculumAddress(hash);
  if (address && location.pathname !== address.pathname) {
    try {
      history.replaceState(history.state, "", address.href);
    } catch {
      // Keep the valid fragment and continue to show the requested lesson.
    }
  }
  return followHash(focus, hash);
}

window.addEventListener("hashchange", () => followCurrentRoute(true));
document.addEventListener("click", event => {
  if (event.defaultPrevented || event.button !== 0 ||
      event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest('a[href^="#"]');
  if (link && !link.hasAttribute("target") && !link.hasAttribute("download") && link.getAttribute("role") !== "tab") {
    if (curriculumAddress(link.hash) ? navigateCurriculum(link.hash) :
        link.hash === location.hash && followHash(true)) event.preventDefault();
    return;
  }
  const summary = event.target.closest(".topic > summary");
  const topic = summary?.parentElement;
  if (topic && !topic.open && curriculumAddress("#" + topic.id)) {
    event.preventDefault();
    navigateCurriculum("#" + topic.id);
  }
});
const preferredTab = document.documentElement.dataset.initialTab;
const initialRoute = location.hash || (preferredTab ? "#" + preferredTab : "#overview");
activate(tabs[0]);
applyFilters();

const curriculum = JSON.parse(document.getElementById("roadmap-data").textContent);
const menus = new Map(topics.map(topic => [topic.dataset.topic, topic.querySelector("[data-progress]")]));
const progressBar = document.getElementById("progress-bar");
const progressLabel = document.getElementById("progress-label");
const storageNote = document.getElementById("storage-note");
const defaultStorageNote = storageNote.textContent;
let selectedPath = null;

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
  document.dispatchEvent(new Event("curriculum-progress"));
}

function readProgress() {
  return {
    statuses: Object.fromEntries(Array.from(menus)
      .filter(([, menu]) => menu.value !== "Not Started").map(([id, menu]) => [id, menu.value])),
    selectedPath,
  };
}

function setProgress(current, persist) {
  selectedPath = current.selectedPath;
  for (const [id, menu] of menus) menu.value = current.statuses[id] || "Not Started";
  if (persist) {
    try {
      LearningProgress.writeLocal(localStorage, current);
      reportStorage(true);
    } catch {
      reportStorage(false);
    }
  }
  updateProgress();
}

try {
  setProgress(LearningProgress.readLocal(localStorage, curriculum.topics, curriculum.paths), false);
} catch {
  reportStorage(false);
}
const progressState = {
  topics: curriculum.topics, paths: curriculum.paths, current: readProgress,
  apply(current) { setProgress(current, true); },
  select(key) {
    if (Object.hasOwn(curriculum.paths, key) && key !== selectedPath) {
      this.apply({...readProgress(), selectedPath: key});
    }
  },
};
for (const menu of menus.values()) menu.addEventListener("change", () => progressState.apply(readProgress()));
document.addEventListener("curriculum-path-selected", event => {
  progressState.select(event.detail);
});
window.addEventListener("storage", event => {
  if (event.key === null || event.key?.startsWith("llm-evaluation-master-curriculum-")) {
    try {
      setProgress(LearningProgress.readLocal(localStorage, curriculum.topics, curriculum.paths), false);
    } catch {
      reportStorage(false);
    }
  }
});
updateProgress();
document.getElementById("course-progress").hidden = false;

let printState;
window.addEventListener("beforeprint", () => {
  if (printState) return;
  const printable = [...disclosures, ...document.querySelectorAll(".lesson-supplement, .lesson-output")];
  printState = printable.map(details => [details, details.open, details.hidden]);
  printable.forEach(details => {
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

