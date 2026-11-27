const assert = require("node:assert/strict");
const {execFileSync} = require("node:child_process");
const {existsSync, readFileSync, readdirSync} = require("node:fs");
const {resolve} = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const {authoredLessonIds} = require("./lesson_test_data.cjs");

const root = resolve(__dirname, "..");
const read = path => readFileSync(resolve(root, path), "utf8");
const {archive_revision: revision, experiments} = JSON.parse(read("docs/original-experiments.json"));
experiments.sort((a, b) => Number(a.id.slice(5)) - Number(b.id.slice(5)));
const curriculum = read("MASTER_CURRICULUM.md");
const topicIds = new Set([...curriculum.matchAll(/^##### (M\d{2}-T\d{2}) — /gm)].map(match => match[1]));
const page = read("docs/master-curriculum.html");
const home = read("docs/index.html");

function python(code) {
  return execFileSync("python3", ["-B", "-c", code], {cwd: root, encoding: "utf8"});
}

test("catalog indexes original walkthroughs and crosswalk references with valid source paths", () => {
  const ids = experiments.map(entry => entry.id);
  const crosswalk = curriculum.split("### Existing lesson crosswalk\n")[1].split("\n## ")[0];
  const expected = new Set([...crosswalk.matchAll(/\bTest (\d+)\b/g)].map(match => "TEST-" + match[1]));
  for (const filename of readdirSync(resolve(root, "docs"))) {
    const match = /^test(\d+)\.html$/.exec(filename);
    if (match) expected.add("TEST-" + match[1]);
  }
  assert.deepEqual(new Set(ids), expected);
  assert.equal(ids.length, new Set(ids).size);
  for (const entry of experiments) {
    assert.match(entry.id, /^TEST-(?:0|[1-9]\d*)$/);
    assert(existsSync(resolve(root, entry.source)), entry.source);
    const mappings = entry.topics ?? [];
    assert.equal(mappings.length, new Set(mappings.map(mapping => mapping.id)).size);
    for (const mapping of mappings) {
      assert(topicIds.has(mapping.id), mapping.id);
      assert(["Primary", "Supporting", "Related"].includes(mapping.relevance));
    }
    for (const artifact of entry.artifacts ?? []) assert(existsSync(resolve(root, artifact.path)), artifact.path);
  }
});

test("evidence states distinguish missing results from partial or recorded outcomes", () => {
  const byId = Object.fromEntries(experiments.map(entry => [entry.id, entry]));
  for (const id of ["TEST-0", "TEST-10", "TEST-14"]) {
    assert.equal(byId[id].evidence, "methodology");
    assert.equal(byId[id].results, null);
    assert((byId[id].artifacts ?? []).every(item => item.kind !== "result"));
  }
  assert.equal(byId["TEST-11"].evidence, "partial");
  assert.match(byId["TEST-11"].results, /TC15|timeout/);
  assert.equal(byId["TEST-13"].evidence, "recorded");
  const judgeData = JSON.parse(read(byId["TEST-13"].artifacts.find(item => item.path.endsWith(".json")).path));
  const verdicts = Object.values(judgeData).find(Array.isArray);
  assert.equal(verdicts.filter(row => row.verdict === "pass").length, 15);
});

test("generated library uses stable anchors and complete original links", () => {
  assert.match(home, /href="master-curriculum\.html#original-practical-tests"/);
  const library = page.split('<section id="original-practical-tests"')[1].split("</section>")[0];
  assert(library.includes("Original Practical Tests Library"));
  const contents = [...library.matchAll(/<details id="original-(test-\d+)"[^>]* data-evidence="([^"]+)">([\s\S]*?)<\/details>/g)];
  assert.equal(contents.length, experiments.length);
  for (const [i, [, id, state, content]] of contents.entries()) {
    const entry = experiments[i];
    assert.equal(id, entry.id.toLowerCase());
    assert.equal(state, entry.evidence);
    const link = /^docs\/test\d+\.html$/.test(entry.source)
      ? entry.source.slice(5)
      : `https://github.com/amitbad/llm-evaluation/blob/${revision}/${entry.source}`;
    assert(content.includes(`href="${link}">View Complete Original Experiment</a>`), id);
    assert(content.includes(`<code>${entry.source}</code>`), id);
    for (const mapping of entry.topics ?? []) assert(content.includes(`href="#${mapping.id.toLowerCase()}"`), mapping.id);
    if (state === "methodology") assert(content.includes("No recorded results were found."));
  }
});

test("authored and outline lessons show exactly their mappings without interrupting controls", () => {
  const authored = new Set(authoredLessonIds);
  for (const id of topicIds) {
    const key = id.toLowerCase();
    const start = page.indexOf(`id="material-${key}"`);
    const end = page.indexOf('<details class="topic"', start);
    const material = page.slice(start, end < 0 ? page.indexOf('<section class="panel" id="roadmap"', start) : end);
    const entries = experiments.filter(entry => entry.topics?.some(mapping => mapping.id === id));
    const references = [...material.matchAll(/data-original-experiment="([^"]+)" data-relevance="([^"]+)"/g)];
    assert.deepEqual(references.map(([, key, relevance]) => [key, relevance]),
      entries.map(entry => [entry.id, entry.topics.find(mapping => mapping.id === id).relevance]), id);
    if (!entries.length) continue;
    assert.equal([...material.matchAll(/<summary>Original TestNeural Experiment<\/summary>/g)].length, 1, id);
    assert.match(material, /<details class="lesson-disclosure original-experiments" data-reading-skip>/);
    for (const entry of entries) assert(material.includes(`href="#original-${entry.id.toLowerCase()}"`), id);
    const index = material.indexOf("<summary>Original TestNeural Experiment</summary>");
    if (authored.has(id)) {
      assert(index > material.lastIndexOf('class="lesson-copy-button"'), id);
      assert(index < material.indexOf("<h4>Lesson Summary and Next Step</h4>"), id);
    } else {
      assert(index > material.indexOf("<h4>Checkpoint</h4>"), id);
    }
  }
});

test("deep links open the Resources disclosure and give its summary keyboard focus", () => {
  const follow = page.match(/function followHash\(focus, hash = location\.hash\) \{[\s\S]+?(?=\nwindow.addEventListener\("hashchange")/)[0];
  const resources = {};
  const tab = {};
  const calls = [];
  const summary = {tagName: "SUMMARY", focus(opts) { calls.push(["focus", opts.preventScroll]); }};
  const target = {
    open: false,
    parentElement: {closest() { return null; }},
    closest(selector) { return selector === ".panel" ? resources : this; },
    querySelector(selector) { assert.equal(selector, "h3, summary"); return summary; },
    matches(selector) { return selector.split(", ").includes(".original-test"); },
    scrollIntoView(opts) { calls.push(["scroll", opts.block]); },
  };
  const context = {
    document: {
      getElementById(id) { assert.equal(id, "original-test-9"); return target; },
      dispatchEvent(event) { calls.push(["route", event.detail]); },
    },
    guidedLearning: {resolve() { return null; }, show() { return null; }},
    panels: [resources],
    tabs: [tab],
    activate(value) { assert.equal(value, tab); calls.push(["view", "resources"]); },
    CustomEvent: class { constructor(_, {detail}) { this.detail = detail; } },
  };
  assert.equal(vm.runInNewContext(follow + '\nfollowHash(true, "#original-test-9")', context), true);
  assert.equal(target.open, true);
  assert.deepEqual(calls, [["view", "resources"], ["route", "#original-test-9"], ["focus", true], ["scroll", "start"]]);
});

test("generator rejects invalid IDs, source paths and relationships before rendering", () => {
  python(`
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0, "docs")
import original_experiments as exp

raw = json.loads(Path("docs/original-experiments.json").read_text())
topics = {m["id"] for entry in raw["experiments"] for m in entry["topics"]}
discovered = {entry["id"] for entry in raw["experiments"]}

def reject(change, message):
    candidate = copy.deepcopy(raw)
    change(candidate["experiments"])
    try:
        exp.validate(candidate, topics, discovered)
    except ValueError as error:
        assert message in str(error), error
    else:
        raise AssertionError(message)

reject(lambda items: items[0].update(id="test 0"), "Invalid experiment ID")
reject(lambda items: items.append(items[0]), "Duplicate experiment ID")
reject(lambda items: items.pop(), "missing from catalog")
reject(lambda items: items[0].update(source="docs/test999.html"), "Missing or unsafe evidence")
reject(lambda items: items[0].update(source="../test0.html"), "Unsafe source path")
reject(lambda items: items[0].update(source="javascript:alert(1)"), "Unsafe source path")
reject(lambda items: items[0].update(title="Different title"), "original heading")
reject(lambda items: items[0]["topics"][0].update(id="M99-T99"), "unknown topic")
reject(lambda items: items[0]["topics"].append(items[0]["topics"][0]), "Duplicate mapping")
reject(lambda items: items[0]["topics"][0].update(relevance="Maybe"), "relevance classification")
reject(lambda items: items[0].update(results="fabricated"), "marks results as missing")
reject(lambda items: items[1].update(results=None), "needs a recorded result")
`);
});

test("metadata renders as text and optional results or mappings may be absent", () => {
  python(`
import json
from pathlib import Path
import sys
sys.path.insert(0, "docs")
import original_experiments as exp

raw = json.loads(Path("docs/original-experiments.json").read_text())
entry = raw["experiments"][0]
rev = raw["archive_revision"]
topic = entry["topics"][0]["id"]
entry.update(objective='<img src=x onerror="alert(1)">')
entry["topics"][0]["connection"] = "<script>alert(1)</script>"
del entry["results"]
del entry["artifacts"]
for output in (
    exp.lesson_disclosure([(entry, entry["topics"][0])], rev),
    exp.library([entry], rev, {item["id"]: "<title>" for item in entry["topics"]}),
):
    assert "<img" not in output and "<script>" not in output
    assert "&lt;img" in output and "&lt;script&gt;" in output
    assert "No recorded results were found." in output
del entry["topics"]
validated = exp.validate({"archive_revision": rev, "experiments": [entry]}, {topic}, {"TEST-0"})
assert "No curriculum mapping has been recorded." in exp.library(validated, rev, {})
assert exp.lesson_disclosure([], rev) == ""
`);
});
