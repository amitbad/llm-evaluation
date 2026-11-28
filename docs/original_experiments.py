"""Load and render the Original Practical Tests Library."""

from collections import Counter, defaultdict
from html import escape, unescape
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/original-experiments.json"
ARCHIVE = "https://github.com/amitbad/llm-evaluation/blob/"
EVIDENCE = {
    "recorded": "Recorded Results Available",
    "methodology": "Methodology Available — Results Missing",
    "partial": "Partial Results Available",
    "reference": "Reference Only — Evidence Not Found",
}
RELEVANCE = ("Primary", "Supporting", "Related")
KINDS = ("result", "input", "method", "visual")
DESCRIPTION_FIELDS = ("title", "objective", "method", "inputs", "configuration", "findings", "limitations")
EXTENSIONS = {".html", ".md", ".py", ".json", ".xlsx", ".yml", ".csv", ".png", ".jpg", ".webp"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_path(value, root):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._/-]+", value), f"Unsafe source path: {value}")
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and ".." not in relative.parts and str(relative) == value
            and relative.suffix in EXTENSIONS, f"Unsafe source path: {value}")
    path = root / relative
    require(path.is_file() and path.resolve() == path and path.stat().st_size > 0, f"Missing or unsafe evidence: {value}")
    return path


def validate(catalog, topic_ids, discovered, root=ROOT):
    require(isinstance(catalog, dict), "Experiment catalog must be an object")
    revision = catalog.get("archive_revision")
    require(isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision), "Expected a pinned archive commit")
    entries = catalog.get("experiments")
    require(isinstance(entries, list) and entries, "Experiment catalog is empty")
    seen = set()
    for entry in entries:
        require(isinstance(entry, dict), "Experiment must be an object")
        key = entry.get("id")
        require(isinstance(key, str) and re.fullmatch(r"TEST-(0|[1-9]\d*)", key), f"Invalid experiment ID: {key}")
        require(key not in seen, f"Duplicate experiment ID: {key}")
        seen.add(key)
        for field in DESCRIPTION_FIELDS:
            require(nonempty(entry.get(field)), f"{key} needs {field}")
        source = validate_path(entry.get("source"), root)
        if source.suffix == ".html" and re.fullmatch(r"test\d+", source.stem):
            require(entry["source"] == f"docs/test{key.split('-')[1]}.html", f"{key} names the wrong walkthrough")
            heading = re.search(r"<h1\b[^>]*>(.*?)</h1>", source.read_text(encoding="utf-8"), re.S | re.I)
            title = " ".join(unescape(re.sub(r"<[^>]+>", " ", heading[1])).split()) if heading else ""
            require(entry["title"] == title, f"{key} title must match the original heading")
        state = entry.get("evidence")
        require(isinstance(state, str) and state in EVIDENCE, f"Unknown evidence state for {key}")
        results = entry.get("results")
        artifacts = entry.get("artifacts", [])
        require(isinstance(artifacts, list), f"Invalid artifacts for {key}")
        paths = {entry["source"]}
        for artifact in artifacts:
            require(isinstance(artifact, dict) and artifact.get("kind") in KINDS
                    and nonempty(artifact.get("label")), f"Invalid artifact for {key}")
            validate_path(artifact.get("path"), root)
            require(artifact["path"] not in paths, f"Duplicate evidence path for {key}: {artifact['path']}")
            paths.add(artifact["path"])
        has_result_file = any(item["kind"] == "result" for item in artifacts)
        if state in ("recorded", "partial"):
            require(nonempty(results) and (source.suffix == ".html" or has_result_file),
                    f"{key} needs a recorded result and a result source")
        else:
            require(results is None and not has_result_file, f"{key} marks results as missing but supplies results")
        links = entry.get("topics", [])
        require(isinstance(links, list), f"Invalid topic mappings for {key}")
        mapped = set()
        for mapping in links:
            require(isinstance(mapping, dict), f"Invalid mapping for {key}")
            topic = mapping.get("id")
            require(isinstance(topic, str) and topic in topic_ids, f"{key} refers to unknown topic: {topic}")
            require(topic not in mapped, f"Duplicate mapping: {key} to {topic}")
            require(mapping.get("relevance") in RELEVANCE and nonempty(mapping.get("connection")),
                    f"{key} needs a relevance classification and connection for {topic}")
            mapped.add(topic)
    require(discovered <= seen, f"Original tests missing from catalog: {', '.join(sorted(discovered - seen))}")
    return sorted(entries, key=lambda entry: int(entry["id"].split("-")[1]))


def load(topic_ids, curriculum_text):
    _, heading, crosswalk = curriculum_text.partition("### Existing lesson crosswalk\n")
    require(heading, "Original experiment crosswalk is missing")
    crosswalk = crosswalk.split("\n## ", 1)[0]
    discovered = {f"TEST-{number}" for number in re.findall(r"\bTest (\d+)\b", crosswalk)}
    discovered.update(f"TEST-{path.stem[4:]}" for path in ROOT.glob("docs/test*.html")
                      if re.fullmatch(r"test\d+", path.stem))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = validate(catalog, topic_ids, discovered)
    return catalog["archive_revision"], entries


def by_topic(entries):
    mappings = defaultdict(list)
    for entry in entries:
        for mapping in entry.get("topics", []):
            mappings[mapping["id"]].append((entry, mapping))
    return mappings


def anchor(entry):
    return "original-" + entry["id"].lower()


def title(entry):
    number = entry["id"].split("-")[1]
    return entry["title"] if re.match(rf"Test {number}\b", entry["title"]) else f"Test {number} — {entry['title']}"


def source_url(path, revision):
    if re.fullmatch(r"docs/test\d+\.html", path):
        return PurePosixPath(path).name
    if path == "phase-1-first-experiments/results/full_results.html":
        return "full-results.html"
    return ARCHIVE + revision + "/" + quote(path, safe="/")


def link(path, label, revision):
    return f'<a href="{escape(source_url(path, revision))}">{escape(label)}</a>'


def fields(rows):
    return '<dl class="field-list">' + "".join(
        f"<div><dt>{label}</dt><dd>{escape(value)}</dd></div>" for label, value in rows
    ) + "</dl>"


def results_text(entry):
    if entry.get("results"):
        return entry["results"]
    if entry["evidence"] == "methodology":
        return "Original methodology is available. No recorded results were found."
    return "No original methodology or recorded results were found in the archive."


def lesson_disclosure(mappings, revision):
    if not mappings:
        return ""
    cards = []
    for entry, mapping in mappings:
        summary = fields((
            ("What was tested", entry["objective"]),
            ("How it was tested", f'{entry["method"]} {entry["inputs"]} {entry["configuration"]}'),
            ("Actual results", results_text(entry)),
            ("Original findings", entry["findings"]),
            ("Evidence notes", entry["limitations"]),
            ("Connection to this lesson", f'{mapping["relevance"]}. {mapping["connection"]}'),
        ))
        direct = link(entry["source"], "View Complete Original Experiment", revision)
        evidence = next((item for item in entry.get("artifacts", []) if item["kind"] == "result"), None)
        result_link = " · " + link(evidence["path"], evidence["label"], revision) if evidence else ""
        cards.append(f'''<article data-original-experiment="{entry['id']}" data-relevance="{mapping['relevance']}">
<h5>{escape(title(entry))}</h5>
<p>{EVIDENCE[entry["evidence"]]}</p>
{summary}
<p>{direct}{result_link} · <a href="#{anchor(entry)}">Evidence files and related lessons</a></p>
</article>''')
    return '''<details class="lesson-disclosure original-experiments" data-reading-skip>
<summary>Original TestNeural Experiment</summary>
<div class="lesson-disclosure-body"><p>Historical evidence from the original repository.</p>
''' + "\n".join(cards) + "</div></details>"


def library(entries, revision, titles):
    cards = []
    for entry in entries:
        summary = fields((
            ("Objective", entry["objective"]), ("Methodology", entry["method"]),
            ("Prompts and inputs", entry["inputs"]), ("Models and configuration", entry["configuration"]),
            ("Actual results", results_text(entry)), ("Original findings", entry["findings"]),
            ("Evidence notes", entry["limitations"]),
        ))
        direct = link(entry["source"], "View Complete Original Experiment", revision)
        artifacts = "".join(
            f'<li>{link(artifact["path"], artifact["label"], revision)} <code>{escape(artifact["path"])}</code></li>'
            for artifact in entry.get("artifacts", [])
        )
        related = "".join(
            f'<li><a href="#{mapping["id"].lower()}">{mapping["id"]} — {escape(titles[mapping["id"]])}</a>'
            f' · {mapping["relevance"]}. {escape(mapping["connection"])}</li>'
            for mapping in entry.get("topics", [])
        )
        cards.append(f'''<details id="{anchor(entry)}" class="course-reference original-test" data-evidence="{entry['evidence']}">
<summary>{escape(title(entry))} · {EVIDENCE[entry["evidence"]]}</summary>
{summary}
<p>{direct} <code>{escape(entry["source"])}</code></p>
{f"<h4>Original evidence files</h4><ul>{artifacts}</ul>" if artifacts else ""}
<h4>Related curriculum lessons</h4>
{f"<ul>{related}</ul>" if related else "<p>No curriculum mapping has been recorded.</p>"}
</details>''')
    return '''<section id="original-practical-tests" aria-labelledby="original-practical-tests-title">
<h3 id="original-practical-tests-title">Original Practical Tests Library</h3>
<p>Browse the tests in their original order. The original pages and archived files retain the recorded prompts, outputs, tables, and findings that are available. Links to archived repository files open a fixed revision.</p>
''' + "\n".join(cards) + "</section>"


def coverage(entries, topic_ids):
    states = Counter(entry["evidence"] for entry in entries)
    mappings = Counter(mapping["relevance"] for entry in entries for mapping in entry.get("topics", []))
    mapped_topics = by_topic(entries)
    unlinked = sorted(set(topic_ids) - mapped_topics.keys())
    return {
        "curriculum_topics": len(topic_ids),
        "experiments": len(entries),
        "evidence_states": {name: states[name] for name in EVIDENCE},
        "with_recorded_evidence": states["recorded"] + states["partial"],
        "mapped_experiments": sum(bool(entry.get("topics")) for entry in entries),
        "unmapped_experiments": [entry["id"] for entry in entries if not entry.get("topics")],
        "linked_lessons": len(mapped_topics),
        "mappings_by_relevance": {name: mappings[name] for name in RELEVANCE},
        "lessons_by_relevance": {
            name: sum(any(mapping["relevance"] == name for _, mapping in links) for links in mapped_topics.values())
            for name in RELEVANCE
        },
        "lessons_without_references": len(unlinked),
        "unlinked_lessons": unlinked,
        "unresolved_source_paths": 0,
    }
