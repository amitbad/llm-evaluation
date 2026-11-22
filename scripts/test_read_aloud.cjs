// Run with node --test scripts/test_read_aloud.cjs. Uses no browser or third-party packages.
const assert = require("node:assert/strict");
const {readFileSync, readdirSync} = require("node:fs");
const {resolve} = require("node:path");
const {test} = require("node:test");
const vm = require("node:vm");

const read = path => readFileSync(resolve(__dirname, "..", path), "utf8");
const script = read("docs/assets/lesson-reader.js");
const html = read("docs/master-curriculum.html");
const controls = ["section", "start", "pause", "stop", "speed", "status", "hint"];

class Element extends EventTarget {
  constructor(tag, ...children) {
    super();
    this.tagName = tag.toUpperCase();
    this.nodeType = 1;
    this.childNodes = [];
    this.attrs = {};
    this.hidden = false;
    this.open = false;
    const classes = new Set();
    this.classList = {add: name => classes.add(name), remove: name => classes.delete(name),
      contains: name => classes.has(name)};
    this.append(...children);
  }
  append(...children) {
    for (const child of children) {
      const node = typeof child === "string" ? {nodeType: 3, textContent: child} : child;
      node.parentElement = this;
      this.childNodes.push(node);
    }
  }
  after(node) {
    const parent = this.parentElement;
    parent.childNodes.splice(parent.childNodes.indexOf(this) + 1, 0, node);
    node.parentElement = parent;
  }
  get nextElementSibling() {
    const siblings = this.parentElement.childNodes;
    return siblings.slice(siblings.indexOf(this) + 1).find(node => node.nodeType === 1);
  }
  get isConnected() { return this.tagName === "DOCUMENT" || Boolean(this.parentElement?.isConnected); }
  set className(value) { value.split(/\s+/).forEach(name => this.classList.add(name)); }
  get textContent() { return this.childNodes.map(node => node.textContent).join(""); }
  set textContent(value) { this.childNodes = []; this.append(value); }
  matches(selector) {
    return selector.split(",").some(part => {
      const rule = part.trim();
      if (rule === "details:not([open])") return this.tagName === "DETAILS" && !this.open;
      if (rule === "[hidden]") return this.hidden;
      if (rule === ".topic[open]") return this.classList.contains("topic") && this.open;
      if (rule[0] === ".") return this.classList.contains(rule.slice(1));
      if (rule[0] === "[") {
        const [key, value] = rule.slice(1, -1).split("=");
        return value === undefined ? Object.hasOwn(this.attrs, key) : this.attrs[key] === value;
      }
      return this.tagName === rule.toUpperCase();
    });
  }
  closest(selector) { return this.matches(selector) ? this : this.parentElement?.closest(selector); }
  querySelector(selector) {
    return this.querySelectorAll(selector)[0] ?? null;
  }
  querySelectorAll(selector) {
    return this.childNodes.filter(node => node.nodeType === 1).flatMap(node => [
      ...(node.matches(selector) ? [node] : []), ...node.querySelectorAll(selector),
    ]);
  }
  set innerHTML(markup) {
    // The generated toolbar is static. Turn its marked controls into event targets.
    this.childNodes = [];
    for (const key of controls) {
      const match = markup.match(new RegExp("<(\\w+)[^>]*data-reading-" + key + "\\b([^>]*)>"));
      assert(match, key);
      const control = new Element(match[1]);
      control.attrs["data-reading-" + key] = "";
      control.disabled = match[2].includes("disabled");
      if (key === "section") {
        control.selectedIndex = 0;
        control.append(new Element("option", "Entire lesson"));
      } else if (key === "speed") control.value = "1";
      this.append(control);
    }
  }
  set length(value) {
    this.childNodes.length = value;
    if (this.selectedIndex >= value) this.selectedIndex = 0;
  }
}

class Utterance {
  constructor(text) { this.text = text; }
}

class Speech extends EventTarget {
  constructor() {
    super();
    this.calls = [];
    this.voices = [];
    this.paused = false;
    this.current = null;
  }
  getVoices() { return this.voices; }
  speak(utterance) {
    assert.equal(this.current, null, "Only one utterance may be in flight");
    this.calls.push(["speak", utterance]);
    this.current = utterance;
  }
  cancel() {
    this.calls.push(["cancel"]);
    const pending = this.current;
    this.current = null;
    // Deliver a callback synchronously to exercise invalidation during cancellation.
    pending?.onerror();
  }
  pause() { this.calls.push(["pause"]); this.paused = true; }
  resume() { this.calls.push(["resume"]); this.paused = false; }
  finish() {
    const pending = this.current;
    this.current = null;
    pending.onend();
  }
}

const node = (tag, ...children) => new Element(tag, ...children);
function holder(mark) {
  const view = node("div");
  view.hidden = true;
  view.classList.add("lesson-reader");
  if (mark) view.attrs[mark] = "";
  return view;
}

function fixture({available = true, legacy = false} = {}) {
  const document = node("document");
  const window = new EventTarget();
  const speaking = new Speech();
  if (available) {
    window.speechSynthesis = speaking;
    window.SpeechSynthesisUtterance = Utterance;
  }
  document.createElement = tag => node(tag);
  const begin = node(legacy ? "h2" : "h4", "Introduction");
  const paragraph = node("p", "A question about the approved policy.");
  const exercises = node(legacy ? "h2" : "h4", "Exercises");
  const instruction = node("li", "Try the example.");
  const material = node("div", begin, paragraph, exercises, node("ol", instruction));
  material.classList.add("topic-material");
  const guided = holder("data-guided-reader");
  const complete = holder("data-lesson-reader");
  const second = holder("data-lesson-reader");
  const secondMaterial = node("div", node("h4", "Next lesson"), node("p", "New topic."));
  secondMaterial.classList.add("topic-material");
  const oldTopic = node("details", node("div", complete, material));
  const newTopic = node("details", node("div", second, secondMaterial));
  for (const topic of [oldTopic, newTopic]) {
    topic.classList.add("topic");
    topic.open = true;
  }
  const panel = node("article", guided);
  let subtitle;
  if (legacy) {
    subtitle = node("p", "Published experiment.");
    document.append(node("body", node("h1", "Example"), subtitle, begin, paragraph, exercises,
      node("ol", instruction), node("footer", node("p", "Site credits."))));
  } else document.append(panel, oldTopic, newTopic);
  let guidedMaterial;
  const query = document.querySelector.bind(document);
  document.querySelector = selector => {
    if (selector === "#guided-material > .topic-material") return guidedMaterial;
    if (selector === "body.academy-lesson:not(.academy-reference) > .subtitle") return subtitle;
    return query(selector);
  };
  const event = (name, target = document) => {
    const value = new Event(name);
    if (target !== document) Object.defineProperty(value, "target", {value: target});
    document.dispatchEvent(value);
  };
  function load() {
    vm.runInNewContext(script, {document, window});
  }
  const ui = view => Object.fromEntries(controls.map(key => [key, view.querySelector("[data-reading-" + key + "]")]));
  return {document, window, speaking, begin, paragraph, exercises, instruction, material, guided,
    complete, second, secondMaterial, oldTopic, newTopic, panel, subtitle, event, load, ui,
    mount: content => {
      guidedMaterial = content;
      event("curriculum-route");
    }};
}

const click = control => {
  if (!control.disabled) control.dispatchEvent(new Event("click"));
};
const change = control => control.dispatchEvent(new Event("change"));
const reading = (element, expected = true) => assert.equal(element.classList.contains("is-being-read"), expected);
function finishAll(speech) {
  const heard = [];
  while (speech.current) {
    assert(heard.length < 100, "Narration must complete");
    heard.push(speech.current.text);
    speech.finish();
  }
  return heard;
}

test("starts only on request, reads each block, highlights it and completes", () => {
  const f = fixture();
  f.load();
  const {start, pause, stop, status} = f.ui(f.complete);
  assert.equal(f.speaking.current, null);
  assert.equal(pause.disabled, true);
  assert.equal(stop.disabled, true);
  click(start);
  click(start);
  assert.equal(f.speaking.calls.length, 1);
  assert.equal(f.speaking.current.rate, 1);
  assert.equal(status.textContent, "Reading.");
  reading(f.begin);
  f.speaking.finish();
  reading(f.begin, false);
  reading(f.paragraph);
  assert.equal(status.textContent, "Reading.");
  assert.deepEqual(finishAll(f.speaking), ["A question about the approved policy.", "Exercises", "Try the example."]);
  reading(f.instruction, false);
  assert.equal(status.textContent, "Reading finished.");
  assert.equal(start.disabled, false);
  assert.equal(stop.disabled, true);
});

test("pauses and resumes the current utterance and waits for action after tab visibility changes", () => {
  const f = fixture();
  f.load();
  const {start, pause, status} = f.ui(f.complete);
  click(start);
  const utterance = f.speaking.current;
  click(pause);
  assert.equal(pause.textContent, "Resume");
  assert.equal(f.speaking.paused, true);
  f.document.hidden = true;
  f.event("visibilitychange");
  f.document.hidden = false;
  f.event("visibilitychange");
  assert.equal(f.speaking.calls.filter(([action]) => action === "resume").length, 0);
  click(pause);
  assert.equal(f.speaking.current, utterance);
  assert.equal(f.speaking.paused, false);
  f.document.hidden = true;
  f.event("visibilitychange");
  assert.equal(status.textContent, "Paused while this tab is hidden.");
  f.document.hidden = false;
  f.event("visibilitychange");
  assert.equal(pause.textContent, "Resume");
  assert.equal(f.speaking.paused, true);
});

test("stops and resets and disregards end or error callbacks from older sessions", () => {
  const f = fixture();
  f.load();
  const {start, stop, status} = f.ui(f.complete);
  click(start);
  const cancelled = f.speaking.current;
  f.speaking.finish();
  click(stop);
  assert.equal(f.speaking.current, null);
  reading(f.paragraph, false);
  assert.equal(status.textContent, "Reading stopped.");
  click(start);
  const current = f.speaking.current;
  cancelled.onend();
  cancelled.onerror();
  assert.equal(f.speaking.current, current);
  assert.equal(current.text, "Introduction");
  assert.equal(status.textContent, "Reading.");
});

test("restarts the current paragraph at the new speed and keeps a paused session paused", () => {
  const f = fixture();
  f.paragraph.textContent = "Practice this idea. ".repeat(18).trim();
  f.load();
  const {start, speed, pause} = f.ui(f.complete);
  click(start);
  f.speaking.finish();
  const first = f.speaking.current.text;
  assert(first.length <= 220);
  f.speaking.finish();
  assert.notEqual(f.speaking.current.text, first);
  speed.value = "1.5";
  change(speed);
  assert.equal(f.speaking.current.text, first);
  assert.equal(f.speaking.current.rate, 1.5);
  reading(f.paragraph);
  click(pause);
  speed.value = "0.75";
  change(speed);
  assert.equal(f.speaking.current, null);
  assert.equal(pause.textContent, "Resume");
  click(pause);
  assert.equal(f.speaking.current.rate, 0.75);
  assert.equal(f.speaking.current.text, first);
});

test("starts a chosen section, cancels prior narration and stops at the next peer heading", () => {
  const f = fixture();
  f.material.append(node("h4", "Knowledge Check"), node("p", "Another question."));
  f.load();
  const {start, section} = f.ui(f.complete);
  assert.deepEqual(section.childNodes.map(option => option.textContent),
    ["Entire lesson", "Introduction", "Exercises", "Knowledge Check"]);
  click(start);
  const old = f.speaking.current;
  section.selectedIndex = 2;
  change(section);
  assert.equal(start.textContent, "Read Section");
  click(start);
  const current = f.speaking.current;
  old.onend();
  assert.equal(f.speaking.current, current);
  assert.deepEqual(finishAll(f.speaking), ["Exercises", "Try the example."]);
});

test("stops across guided route, mode, native topic and filter changes", () => {
  const f = fixture();
  f.load();
  f.mount(f.material);
  const guided = f.ui(f.guided);
  click(guided.start);
  assert.equal(f.speaking.current.text, "Introduction");
  const original = f.speaking.current;
  f.mount(f.secondMaterial);
  assert.equal(f.speaking.current, null);
  click(guided.start);
  assert.equal(f.speaking.current.text, "Next lesson");
  original.onend();
  assert.equal(f.speaking.current.text, "Next lesson");
  f.event("curriculum-tab");
  assert.equal(f.speaking.current, null);
  click(f.ui(f.complete).start);
  f.event("toggle", f.newTopic);
  assert.equal(f.speaking.current, null);
  click(f.ui(f.second).start);
  assert.equal(f.speaking.current.text, "Next lesson");
  f.newTopic.hidden = true;
  f.event("input");
  assert.equal(f.speaking.current, null);
});

test("disables controls and explains unavailable speech synthesis", () => {
  const f = fixture({available: false});
  f.load();
  const ui = f.ui(f.complete);
  for (const control of ["start", "pause", "stop", "speed", "section"]) assert(ui[control].disabled, control);
  assert.match(ui.status.textContent, /unavailable in this browser/);
  assert(ui.hint.hidden);
});

test("recovers from an active speech error and uses a later system English voice", () => {
  const f = fixture();
  f.load();
  const {start, stop, status} = f.ui(f.complete);
  click(start);
  f.speaking.current.onerror();
  assert.equal(f.speaking.current, null);
  assert.equal(stop.disabled, true);
  reading(f.begin, false);
  assert.match(status.textContent, /could not continue/);
  const voice = {lang: "en-GB", localService: true, default: true};
  f.speaking.voices = [{lang: "en-US", localService: false, default: true}, voice];
  f.speaking.dispatchEvent(new Event("voiceschanged"));
  click(start);
  assert.equal(f.speaking.current.voice, voice);
  assert.equal(f.speaking.current.lang, "en-GB");
});

test("reads educational text in order and excludes code, controls, hidden answers and navigation", () => {
  const f = fixture();
  const openAnswer = node("details", node("summary", "Answers"), node("p", "Private answer."));
  openAnswer.open = true;
  openAnswer.attrs["data-reading-skip"] = "";
  const hidden = node("p", "Hidden control.");
  hidden.hidden = true;
  const note = node("div", "Important: ", node("strong", "save your work."));
  f.material.append(node("nav", node("p", "Navigation text.")),
    node("pre", node("code", "python three dot py")), node("button", "Copy Code"), hidden, openAnswer,
    node("details", node("p", "Closed disclosure.")), note,
    node("p", "Run this command ", node("code", "python3 test.py"), " to try the example."),
    node("p", "Use ", node("code", "print()"), " to display the result."),
    node("li", "Parent instruction.", node("ul", node("li", "Nested instruction."))),
    node("h4", "Knowledge Check"), node("ol", node("li", "What happened?")));
  f.load();
  click(f.ui(f.complete).start);
  assert.deepEqual(finishAll(f.speaking), ["Introduction", "A question about the approved policy.", "Exercises",
    "Try the example.", "Important: save your work.", "Run this command to try the example.",
    "Use print() to display the result.", "Parent instruction.", "Nested instruction.",
    "Knowledge Check", "What happened?"]);
});

test("reads standalone lesson content between its subtitle and footer", () => {
  const f = fixture({legacy: true});
  f.load();
  const toolbar = f.subtitle.nextElementSibling;
  assert(toolbar.classList.contains("lesson-reader"));
  click(f.ui(toolbar).start);
  assert.deepEqual(finishAll(f.speaking), ["Published experiment.", "Introduction",
    "A question about the approved policy.", "Exercises", "Try the example."]);
});

test("generator includes the shared reader for the standalone curriculum and all published experiments", () => {
  assert(html.includes(script));
  const count = (pattern) => [...html.matchAll(pattern)].length;
  assert.equal(count(/<div class="lesson-reader" data-lesson-reader hidden><\/div>/g), 53);
  assert.equal(count(/<div class="lesson-reader" data-guided-reader hidden><\/div>/g), 1);
  assert.equal(count(/class="lesson-disclosure lesson-supplement" data-reading-skip/g), 12);
  for (const file of readdirSync(resolve(__dirname, "../docs")).filter(name => /^test\d+\.html$/.test(name))) {
    assert.match(read("docs/" + file), /<script src="assets\/lesson-reader.js" defer><\/script>/, file);
  }
});
