// Run with node --test scripts/test_guided_navigation.cjs. No browser or packages required.
const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {resolve} = require("node:path");
const {test} = require("node:test");
const vm = require("node:vm");
const {authoredLessonIds} = require("./lesson_test_data.cjs");

const read = path => readFileSync(resolve(__dirname, "..", path), "utf8");
const html = read("docs/master-curriculum.html");
const data = JSON.parse(html.match(/<script id="roadmap-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const authoredLessons = new Set(authoredLessonIds);
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1]
  .replace(read("docs/learning_roadmap.js"), "const CurriculumRoadmap = {};")
  .replace("LearningProgress.bindControls(progressState, CurriculumRoadmap.saveBlob);", "")
  .replace(read("docs/assets/lesson-reader.js"), "")
  .replace(read("docs/assets/academy.js"), "");

class Element extends EventTarget {
  constructor(props = {}) {
    super();
    Object.assign(this, {dataset: {}, children: [], value: "", attributes: {}, queries: {}, style: {},
      clientWidth: 620, clientHeight: 360, scrollLeft: 0, scrollTop: 0}, props);
    this.classList = {toggle() {}};
  }
  getAttribute(key) { return this.attributes[key]; }
  hasAttribute(key) { return Object.hasOwn(this.attributes, key); }
  setAttribute(key, value) { this.attributes[key] = value; }
  removeAttribute(key) { delete this.attributes[key]; }
  querySelector(key) { return this.queries[key] || null; }
  querySelectorAll(key) { return this.queries[key] || []; }
  matches(selector) { return selector.includes("#" + this.id) || (selector.includes(".topic") && this.dataset.topic); }
  closest(selector) {
    if (selector === ".panel") return this.panel;
    if (selector === "details" && this.dataset.topic) return this;
    if (selector === ".navigator-dock") return this.dock;
    if (selector === "[data-lesson]" && this.dataset.lesson) return this;
    return null;
  }
  append(...nodes) {
    for (const node of nodes) {
      if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(item => item !== node);
      this.children.push(node);
      node.parentElement = this;
    }
  }
  set innerHTML(value) {
    this.markup = value;
    this.children = [];
  }
  get innerHTML() { return this.markup; }
  showModal() { this.open = true; }
  close() { this.open = false; }
  setPointerCapture(id) { this.capturedPointer = id; }
  scrollTo({left, top}) { this.scrollLeft = Math.max(0, left); this.scrollTop = Math.max(0, top); }
  scrollBy(x, y) { this.scrollTo({left: this.scrollLeft + x, top: this.scrollTop + y}); }
  focus() { this.focused = true; }
  scrollIntoView() { this.scrolled = true; }
}

const lessonHash = (path, topic) => "#quick-" + path.toLowerCase() + "/" + topic.toLowerCase();

function start(hash, storage = new Map(), hosted = false) {
  const ids = new Map();
  const add = (id, props) => {
    const node = new Element({id, ...props});
    ids.set(id, node);
    return node;
  };
  const panels = ["quick", "detail", "roadmap", "overview", "resources"].map(id => add(id));
  const tabs = panels.map(panel => {
    panel.panel = panel;
    return add("tab-" + panel.id, {hash: "#" + panel.id});
  });
  const modeLinks = ["quick", "detail"].map(mode => add("mode-" + mode, {hash: "#" + mode}));
  for (const id of ["tabs", "filters", "search", "matches", "difficulty", "subject", "status", "track",
    "clear-filters", "expand", "collapse", "quick-catalog", "progress-bar", "progress-label", "storage-note",
    "course-progress", "guided-lesson", "guided-path", "guided-position", "guided-title", "guided-estimate",
    "guided-material", "guided-status", "guided-progress", "guided-progress-label",
    "guided-previous", "guided-complete", "guided-next", "guided-back"]) add(id);
  const el = id => ids.get(id);
  const dock = new Element({hidden: true});
  add("navigator-launch", {dock});
  for (const name of ["dialog", "map", "surface", "viewport", "path",
    "title", "zoom", "minimize", "close", "zoom-in", "zoom-out", "center"]) add("navigator-" + name);
  el("guided-lesson").queries.h3 = el("guided-title");
  el("course-progress").panel = el("overview");
  add("roadmap-data", {textContent: JSON.stringify(data)});
  add("return-to-plan", {queries: {a: new Element()}});
  for (const id of Object.keys(data.modules)) {
    const home = new Element();
    home.append(add("module-objectives-" + id.toLowerCase(), {home}));
  }
  const topics = Object.values(data.topics).map(topic => {
    const menu = new Element({value: "Not Started"});
    const body = new Element();
    const links = [...topic.mandatory, ...topic.recommended, ...topic.conditional].map(edge =>
      new Element({attributes: {href: "#" + edge.id.toLowerCase()}}));
    const objectives = authoredLessons.has(topic.id) ? null :
      new Element({hidden: true, queries: {"[data-lesson-objectives]": new Element()}});
    body.append(add("material-" + topic.id.toLowerCase(),
      {queries: {'a[href^="#m"]': links, ".lesson-objectives": objectives}}));
    return add(topic.id.toLowerCase(), {dataset: {topic: topic.id}, panel: el("detail"), parentElement: body,
      queries: {"[data-progress]": menu, ".item-title": {textContent: topic.title}, summary: new Element()}});
  });
  const indicator = (key, guided) => new Element({
    dataset: {planProgress: key, ...(guided ? {guided: ""} : {})},
    queries: {"[data-plan-status]": new Element(), "[data-plan-next]": new Element()},
  });
  const planActions = Object.fromEntries(Object.keys(data.paths).map(key => [key, indicator(key, true)]));
  const overviewAction = indicator("selected", true);
  const completeAction = indicator("A", false);
  const plans = Object.values(data.paths).map(path => {
    const plan = add("quick-" + path.id.toLowerCase(), {dataset: {quickPlan: path.id}, panel: el("quick")});
    plan.queries = Object.fromEntries(["[data-plan-message]", "[data-plan-visual]", "[data-plan-share]",
      "[data-plan-sharing]", "h3, summary"].map(key => [key, new Element()]));
    plan.queries["[data-step]"] = path.closure.map(topic => new Element({
      dataset: {step: topic}, queries: {a: new Element(), "[data-lesson-state]": new Element()},
    }));
    return plan;
  });
  const document = new Element({
    documentElement: {outerHTML: html, dataset: {}},
    getElementById: el,
    createElement: tag => new Element({tag}),
    queries: {"#tabs a": tabs, ".study-mode-picker a": modeLinks, ".topic": topics, "[data-quick-plan]": plans,
      "[data-plan-progress]": [...Object.values(planActions), overviewAction, completeAction],
      ".lesson-supplement, .lesson-output": [add("print-lesson-disclosure", {open: false})]},
  });
  document.querySelector = selector => el(selector.slice(1));
  const window = new EventTarget();
  const origin = hosted ? "https://llmacademy.testneural.in" : "null";
  let address = new URL(hosted ? origin + "/master-curriculum.html" : "file:///master-curriculum.html");
  address.hash = hash;
  const location = {
    origin,
    get protocol() { return address.protocol; },
    get pathname() { return address.pathname; },
    get search() { return address.search; },
    get href() { return address.href; },
    get hash() { return address.hash; },
    set hash(value) {
      if (address.hash === value) return;
      address.hash = value;
      window.dispatchEvent(new Event("hashchange"));
    },
  };
  const pushes = [];
  const history = {
    state: null,
    replaceState(_, __, href) { address = new URL(href); },
    pushState(_, __, href) {
      pushes.push(href);
      address = new URL(href);
    },
  };
  const localStorage = {
    getItem: key => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: key => storage.delete(key),
  };
  class CustomEvent extends Event {
    constructor(name, {detail}) { super(name); this.detail = detail; }
  }
  const context = vm.createContext({document, location, window, history, localStorage, Event, CustomEvent, URL});
  vm.runInContext(script, context);
  return {
    el, storage, planActions, overviewAction, completeAction, window, location, dock, pushes,
    click: (target, {metaKey = false} = {}) => {
      const event = new Event("click", {cancelable: true});
      Object.defineProperties(event, {target: {value: target}, button: {value: 0}, metaKey: {value: metaKey}});
      return document.dispatchEvent(event);
    },
    back: href => {
      address = new URL(href);
      window.dispatchEvent(new Event("hashchange"));
    },
    run: code => vm.runInContext(code, context),
    go: next => {
      if (location.hash === next) window.dispatchEvent(new Event("hashchange"));
      else location.hash = next;
    },
  };
}

test("academy lesson visits use distinct static addresses without remounting the curriculum document", () => {
  const [first, second] = data.paths.B.closure.map(id => id.toLowerCase());
  const initial = lessonHash("B", first);
  const ui = start(initial, new Map(), true);
  const firstAddress = ui.location.href;
  assert.equal(ui.location.pathname, "/lesson-" + first + ".html");
  assert.equal(ui.location.hash, initial);
  assert.equal(ui.pushes.length, 0);
  const material = ui.el("material-" + second);
  const next = lessonHash("B", second);
  const link = new Element({hash: next});
  link.closest = selector => selector === 'a[href^="#"]' ? link : null;
  assert.equal(ui.click(link, {metaKey: true}), true);
  assert.equal(ui.pushes.length, 0);
  assert.equal(ui.click(link), false);
  assert.equal(ui.location.pathname, "/lesson-" + second + ".html");
  assert.equal(ui.location.hash, next);
  assert.deepEqual(ui.pushes, [ui.location.href]);
  assert.equal(ui.el("guided-material").children[0], material);
  ui.run("navigateCurriculum(" + JSON.stringify(next) + ")");
  assert.equal(ui.pushes.length, 1);
  ui.run("navigateCurriculum('#detail')");
  assert.equal(ui.location.pathname, "/master-curriculum.html");
  const topic = ui.el(second);
  const summary = topic.querySelector("summary");
  summary.parentElement = topic;
  summary.closest = selector => selector === ".topic > summary" ? summary : null;
  assert.equal(ui.click(summary), false);
  assert.equal(ui.location.pathname, "/lesson-" + second + ".html");
  assert.equal(ui.el(second).open, true);
  ui.back(firstAddress);
  assert.equal(ui.location.pathname, "/lesson-" + first + ".html");
  assert.equal(ui.el("guided-material").children[0], ui.el("material-" + first));
  const offline = start(initial);
  assert.equal(offline.location.pathname, "/master-curriculum.html");
  assert.equal(offline.pushes.length, 0);
});

test("compact mode selector follows lesson links and preserves progress across modes", () => {
  const topic = data.paths.B.closure[0];
  const route = lessonHash("B", topic);
  const ui = start(route);
  const quick = ui.el("mode-quick");
  const complete = ui.el("mode-detail");
  assert.match(html, /<nav class="study-mode-picker" aria-label="Learning mode">\s*<a href="#quick">Quick Learning<\/a>\s*<a href="#detail">Complete Course<\/a>/);
  assert.equal(quick.getAttribute("aria-current"), "location");
  assert.equal(complete.getAttribute("aria-current"), undefined);
  ui.el("guided-complete").dispatchEvent(new Event("click"));

  ui.go(complete.hash);
  assert.equal(quick.getAttribute("aria-current"), undefined);
  assert.equal(complete.getAttribute("aria-current"), "location");
  ui.go("#" + topic.toLowerCase());
  assert.equal(complete.getAttribute("aria-current"), "location");
  assert.equal(ui.el(topic.toLowerCase()).querySelector("[data-progress]").value, "Completed");

  ui.go(quick.hash);
  assert.equal(quick.getAttribute("aria-current"), "location");
  ui.go(route);
  assert.equal(ui.el("guided-complete").textContent, "Completed");
  ui.go("#overview");
  assert.equal(quick.getAttribute("aria-current"), undefined);
  assert.equal(complete.getAttribute("aria-current"), undefined);
});

test("all seven deep-link sequences use one shared lesson and stop at their boundaries", () => {
  for (const path of Object.values(data.paths)) {
    const key = path.id.toLowerCase();
    const plan = html.match(new RegExp('<article class="quick-plan" id="quick-' + key + '"[\\s\\S]*?</article>'))[0];
    assert.deepEqual([...plan.matchAll(/data-step="([^"]+)"/g)].map(match => match[1]), path.closure);
    const firstRoute = lessonHash(path.id, path.closure[0]);
    const ui = start(firstRoute);
    const {el} = ui;
    for (const [index, topic] of path.closure.entries()) {
      const current = lessonHash(path.id, topic);
      ui.go(current);
      const material = el("material-" + topic.toLowerCase());
      assert.equal(el("detail").hidden, true);
      assert.equal(el("guided-title").textContent, data.topics[topic].title);
      assert.equal(el("guided-position").textContent, "Lesson " + (index + 1) + " of " + path.closure.length);
      assert.equal(el("guided-material").children.length, 1);
      assert.equal(el("guided-material").children[0], material);
      const objective = el("module-objectives-" + data.topics[topic].module.toLowerCase());
      const objectives = material.querySelector(".lesson-objectives");
      if (authoredLessons.has(topic)) {
        assert.equal(objectives, null);
        assert.equal(objective.parentElement, objective.home);
      } else {
        assert.equal(objectives.hidden, false);
        assert.deepEqual(objectives.querySelector("[data-lesson-objectives]").children, [objective]);
      }
      const {mandatory, recommended, conditional} = data.topics[topic];
      const expected = [...mandatory, ...recommended, ...conditional].map(edge =>
        path.closure.includes(edge.id) ? lessonHash(path.id, edge.id) : undefined);
      assert.deepEqual(material.querySelectorAll('a[href^="#m"]').map(link => link.getAttribute("href")), expected);
      assert.equal(el("guided-previous").hidden, index === 0);
      assert.equal(el("guided-next").hidden, index === path.closure.length - 1);
      if (index > 0) assert.equal(el("guided-previous").href, lessonHash(path.id, path.closure[index - 1]));
      if (index < path.closure.length - 1) assert.equal(el("guided-next").href, lessonHash(path.id, path.closure[index + 1]));
    }
    ui.go(el("guided-back").href);
    assert.equal(el("guided-material").children.length, 0);
    for (const id of Object.keys(data.modules)) {
      const objective = el("module-objectives-" + id.toLowerCase());
      assert.equal(objective.parentElement, objective.home);
    }
    assert.equal(el("quick-" + key).hidden, false);
    const currentLink = el("quick-" + key).querySelectorAll("[data-step]").at(-1).querySelector("a");
    assert.equal(currentLink.getAttribute("aria-current"), "step");
    ui.go("#quick-" + key + "/m99-t99");
    assert.equal(el("quick-" + key).hidden, false);
  }
});

test("refresh, completion, return links and version-one backups preserve shared progress", () => {
  const path = data.paths.B;
  const [first, next] = path.closure;
  const route = lessonHash("B", first);
  const ui = start(route);
  assert.equal(ui.el("guided-complete").textContent, "Mark as Completed");
  assert.equal(ui.el("guided-progress").value, 0);
  assert.equal(ui.el("guided-progress").max, path.closure.length);
  ui.el("guided-complete").dispatchEvent(new Event("click"));
  assert.equal(ui.el("guided-progress").value, 1);
  assert.equal(ui.el(first.toLowerCase()).querySelector("[data-progress]").value, "Completed");
  const resumed = start(route, ui.storage);
  assert.equal(resumed.el("guided-complete").textContent, "Completed");
  assert.equal(resumed.el("guided-title").textContent, data.topics[first].title);
  assert.equal(resumed.el("guided-progress-label").textContent, "1 of " + path.closure.length + " lessons completed");
  assert.equal(resumed.planActions.B.querySelector("[data-plan-next]").href, lessonHash("B", next));
  assert.equal(resumed.overviewAction.querySelector("[data-plan-next]").href, lessonHash("B", next));
  assert(resumed.completeAction.querySelector("[data-plan-next]").href.startsWith("#m"));
  resumed.go("#" + first.toLowerCase());
  assert.equal(resumed.el("detail").hidden, false);
  assert.equal(resumed.el(first.toLowerCase()).open, true);
  assert.equal(resumed.el("guided-material").children.length, 0);
  assert.equal(resumed.el("return-to-plan").querySelector("a").href, route);
  resumed.go(route);
  resumed.window.dispatchEvent(new Event("beforeprint"));
  assert.equal(resumed.el("guided-material").children.length, 0);
  assert.equal(resumed.el("print-lesson-disclosure").open, true);
  resumed.window.dispatchEvent(new Event("afterprint"));
  assert.equal(resumed.el("guided-material").children.length, 1);
  assert.equal(resumed.el("print-lesson-disclosure").open, false);
  resumed.run(`
    const backup = LearningProgress.parseBackup(JSON.stringify(LearningProgress.makeBackup(progressState.current())),
      curriculum.topics, curriculum.paths);
    progressState.apply(LearningProgress.projectImport(progressState.current(), backup, "replace"));
  `);
  assert.equal(resumed.el("guided-complete").textContent, "Completed");
  assert.equal(resumed.run("progressState.current().selectedPath"), "B");
  const sharing = Object.values(data.paths).find(other => other.id !== "B" && other.closure.includes(first));
  resumed.go(lessonHash(sharing.id, first));
  assert.equal(resumed.el("guided-complete").textContent, "Completed");
});

test("capstone progression preserves progress across guided and complete course modes", () => {
  const plan = data.paths.A;
  const first = "M15-T01";
  const second = "M15-T02";
  assert.equal(plan.closure[plan.closure.indexOf(first) + 1], second);
  const ui = start(lessonHash("A", first));
  ui.el("guided-complete").dispatchEvent(new Event("click"));
  assert.equal(ui.el("guided-next").href, lessonHash("A", second));
  ui.go(ui.el("guided-next").href);
  assert.equal(ui.el("guided-title").textContent, data.topics[second].title);
  assert.equal(ui.el("guided-previous").href, lessonHash("A", first));
  assert.equal(ui.run("progressState.current().statuses['M15-T01']"), "Completed");
  ui.go("#m15-t02");
  assert.equal(ui.el("m15-t02").open, true);
});

test("localized elective supports guided navigation and complete-course progress", () => {
  const topic = "M16-T01";
  const plan = data.paths.G;
  const index = plan.closure.indexOf(topic);
  assert.ok(index > 0);
  const ui = start(lessonHash("G", topic));
  assert.equal(ui.el("guided-previous").href, lessonHash("G", plan.closure[index - 1]));
  assert.equal(ui.el("guided-next").href, lessonHash("G", "M16-T02"));
  ui.el("guided-complete").dispatchEvent(new Event("click"));
  ui.go("#m16-t01");
  assert.equal(ui.el("m16-t01").open, true);
  assert.equal(ui.el("m16-t01").querySelector("[data-progress]").value, "Completed");
});

test("multimodal elective keeps navigation and progress across reading modes", () => {
  const ui = start(lessonHash("G", "M16-T02"));
  assert.equal(ui.el("guided-previous").href, lessonHash("G", "M16-T01"));
  assert.equal(ui.el("guided-next").href, lessonHash("G", "M16-T03"));
  ui.el("guided-complete").dispatchEvent(new Event("click"));
  ui.go("#m16-t02");
  assert.equal(ui.el("m16-t02").open, true);
  assert.equal(ui.el("m16-t02").querySelector("[data-progress]").value, "Completed");
});

test("lesson chapters and outlines render the reading sequence and relevant disclosures", () => {
  const sources = [...html.matchAll(/<div class="topic-material lesson-reading" id="material-([^"]+)">([\s\S]*?)\n<\/div>\n    <\/div>\n  <\/div>\n<\/details>/g)];
  assert.equal(sources.length, 53);
  assert.equal(new Set(sources.map(([, id]) => id)).size, 53);
  assert.equal([...html.matchAll(/id="module-objectives-m\d+"/g)].length, 18);
  for (const [, id, markup] of sources) {
    const topic = data.topics[id.toUpperCase()];
    const focusedTraceLesson = topic.id === "M14-T01";
    const focusedMonitoringLesson = topic.id === "M14-T02";
    const focusedOperationalLesson = topic.id === "M14-T03";
    const sections = focusedOperationalLesson ? [
      "What You Will Learn", "Start With the Saved Incident Evidence",
      "Optimize an LLM Application Under Cost, Latency and Reliability Constraints",
      "Inspect Operational Evidence in Langfuse", "Investigation Worksheet",
      "Worked Solutions to Practice", "Common Mistakes", "Lesson Summary and Next Step",
      "<summary>Detailed time estimates</summary>",
    ] : focusedMonitoringLesson ? [
      "What You Will Learn", "Start With the Saved Evidence",
      "Production Quality Monitoring: Sampling, Feedback, Drift and Alert Investigation",
      "Inspect the Alert in Langfuse", "Investigation Worksheet",
      "Worked Solutions to Practice", "Common Mistakes", "Lesson Summary and Next Step",
      "<summary>Detailed time estimates</summary>",
    ] : focusedTraceLesson ? [
      "What You Will Learn", "Why This Lesson Matters", "Observe the Saved Failure",
      "Read a Trace Before Changing the Application", "Investigate an LLM Failure Using Langfuse",
      "Monitor the Failure You Just Investigated", "Investigation Worksheet",
      "Worked Solutions to Practice", "Common Mistakes", "Lesson Summary and Next Step",
      "<summary>Detailed time estimates</summary>",
    ] : authoredLessons.has(topic.id) ? [
      "What You Will Learn", "Why This Lesson Matters", "Beginner Explanation", "Worked Demonstration",
      "Hands-On Python Exercise", "Practice Exercises", "Worked Solutions to Practice",
      "<h4>Knowledge Check</h4>", "Knowledge Check Answers", "Common Mistakes", "Lesson Summary and Next Step",
      "<summary>Detailed time estimates</summary>",
    ] : ['class="lesson-intro"', "<strong>Lesson outline.", "<h4>Learning objectives</h4>",
      "<h4>Key concepts</h4>", "<h4>Demonstrations and examples</h4>", "<h4>Practical exercise</h4>",
      "<h4>Checkpoint</h4>", "<summary>Detailed time estimates</summary>"];
    const positions = sections.map(label => markup.indexOf(label));
    assert(positions.every((position, index) => position >= 0 && (!index || position > positions[index - 1])));
    const prerequisites = [...topic.mandatory, ...topic.recommended, ...topic.conditional];
    assert.equal(markup.includes("<summary>Prerequisites</summary>"), prerequisites.length > 0);
    assert.doesNotMatch(markup, />M\d+-T\d+<\/a>/);
    assert.doesNotMatch(markup, /<details\b[^>]*\bopen\b/);
    if (focusedOperationalLesson) {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives|www\.online-python\.com/);
      assert.match(markup, /href="test12\.html"/);
      assert.match(markup, /class="language-python">[\s\S]*monotonic_ns/);
      assert.match(markup, /operational_lab\.py[^\n]*--write/);
      assert.match(markup, /operational_lab\.py[^\n]*--read scripts\/fixtures\/m14-t03-measurements\.json/);
      assert.match(markup, /langfuse-lite tree/);
      assert.match(markup, /class="lesson-disclosure lesson-supplement" data-reading-skip><summary><h4>Worked Solutions to Practice/);
    } else if (focusedMonitoringLesson) {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives|www\.online-python\.com/);
      assert.match(markup, /href="test5\.html"/);
      assert.match(markup, /class="language-python">[\s\S]*def alert_step/);
      assert.match(markup, /monitor_lab\.py[^\n]*--audit/);
      assert.match(markup, /monitor_lab\.py[^\n]*--export-langfuse/);
      assert.match(markup, /langfuse-lite tree/);
      assert.match(markup, /Saved agreement: 31\/49/);
      assert.match(markup, /class="lesson-disclosure lesson-supplement" data-reading-skip><summary><h4>Worked Solutions to Practice/);
    } else if (focusedTraceLesson) {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives|www\.online-python\.com/);
      assert.match(markup, /href="test12\.html"/);
      assert.match(markup, /class="language-python">[\s\S]*start_as_current_observation/);
      assert.match(markup, /trace_lab\.py[^\n]*--mode replay/);
      assert.match(markup, /trace_lab\.py[^\n]*--mode repair/);
      assert.match(markup, /langfuse-lite tree/);
      assert.match(markup, /langfuse-lite export/);
      assert.match(markup, /class="lesson-disclosure lesson-supplement" data-reading-skip><summary><h4>Worked Solutions to Practice/);
    } else if (topic.id === "M15-T01") {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives/);
      assert.match(markup, /Experiment A[\s\S]*Experiments B and C[\s\S]*Experiments D and E/);
      assert.match(markup, /class="language-python">[\s\S]*def replay\(saved\)/);
      assert.match(markup, /D-candidate: pass=7\/8 coverage=8\/8 BLOCK/);
      assert.match(markup, /E-repaired: pass=8\/8 coverage=8\/8 PASS/);
      assert.match(markup, /E-missing-review: pass=7\/7 coverage=7\/8 REVIEW/);
      assert.match(markup, /Design Review Before You Trust a Score/);
      assert.match(markup, /<h5>Choose one track<\/h5>/);
      assert.match(markup, /href="#m13-t02"/);
      assert.match(markup, /href="#m15-t02"/);
      assert.match(markup, /href="test12\.html"/);
      assert.match(markup, /href="test13\.html"/);
    } else if (topic.id === "M15-T02") {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives/);
      assert.match(markup, /Experiments A and B[\s\S]*Experiments C and D[\s\S]*Experiments E and F/);
      assert.match(markup, /def recovery\(release, results, windows, probe=None\)/);
      assert.match(markup, /E wording only: 4\/6 passed, coverage 6\/6, KEEP CONTAINED/);
      assert.match(markup, /E verified rollback: 6\/6 passed, coverage 6\/6, RESTORE LIMITED/);
      assert.match(markup, /Decision Memo and Incident Handoff[\s\S]*Score the teach-back/);
      for (const id of ["m13-t03", "m14-t02", "m15-t01", "m12-t03", "m14-t03", "m16-t01"]) {
        assert.ok(markup.includes('href="#' + id + '"'));
      }
      assert.match(markup, /href="test11\.html"/);
    } else if (topic.id === "M16-T01") {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives/);
      assert.match(markup, /Experiment A[\s\S]*Experiment B[\s\S]*Experiment C[\s\S]*Experiment D[\s\S]*Experiment E[\s\S]*Experiment F/);
      assert.match(markup, /मेरा रिफंड कब आएगा/);
      assert.match(markup, /Compré el producto hace quince días/);
      assert.match(markup, /₹1,23,456\.50/);
      assert.match(markup, /<caption>Localization evaluation dimensions<\/caption>/);
      assert.match(markup, /<caption>Localized support review rubric<\/caption>/);
      assert.match(markup, /F candidate: 13\/14 pass, 14\/14 evidence, BLOCK/);
      assert.match(markup, /F missing review: 13\/13 pass, 13\/14 evidence, REVIEW/);
      for (const id of ["m04-t03", "m07-t02", "m05-t02", "m16-t02"]) {
        assert.ok(markup.includes('href="#' + id + '"'));
      }
      assert.match(markup, /href="test6\.html"/);
    } else if (topic.id === "M16-T02") {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives/);
      assert.match(markup, /Experiment A[\s\S]*Experiment B[\s\S]*Experiment C[\s\S]*Experiment D[\s\S]*Experiment E[\s\S]*Experiment F[\s\S]*Experiment G/);
      assert.match(markup, /<img src="assets\/m16-t02-receipt-fees\.png" alt="Northstar sample receipt[^"]+"[^>]*max-width:100%/);
      assert.match(markup, /<caption>Northstar receipt and fee chart text equivalent<\/caption>[\s\S]*?<td>R1<\/td>[\s\S]*?<td>R2<\/td>/);
      assert.match(markup, /C negation: S\/D\/I=\(0, 1, 0\), ref=6, WER=16\.7%/);
      assert.match(markup, /G spoken disclosure: 11\/12 pass, 12\/12 coverage, BLOCK/);
      assert.match(markup, /G missing grading capture: 11\/11 pass, 11\/12 coverage, REVIEW/);
      for (const id of ["m02-t02", "m03-t03", "m04-t01", "m08-t02", "m16-t03"]) {
        assert.ok(markup.includes('href="#' + id + '"'));
      }
      assert.match(markup, /href="test7\.html"/);
    } else if (authoredLessons.has(topic.id)) {
      assert.doesNotMatch(markup, /Lesson outline\.|Module objectives/);
      assert.equal([...markup.matchAll(/<h5>Example \d\./g)].length, 3);
      assert.equal([...markup.matchAll(/<h5>Practice \d\./g)].length, 4);
      assert.equal([...markup.matchAll(/<h5>Solution \d<\/h5>/g)].length, 4);
      assert.deepEqual([...markup.matchAll(/<h5>Step (\d) — /g)].map(match => Number(match[1])),
        [1, 2, 3, 4, 5, 6, 7]);
      const lessonSource = read("docs/lessons/" + id + ".md");
      const labs = [...markup.matchAll(/<h4>Guided Engineering Lab<\/h4>([\s\S]*?)(?=<h4>)/g)];
      assert.equal(labs.length, /^## Guided Engineering Lab$/m.test(lessonSource) ? 1 : 0);
      const expectedCounts = (section, programs, outputs) => {
        assert.equal([...section.matchAll(/<pre><code class="language-python">/g)].length, programs);
        assert.equal([...section.matchAll(/<pre><code class="language-text">/g)].length, outputs);
        assert.equal([...section.matchAll(/<details class="lesson-disclosure lesson-output"><summary>Expected output<\/summary>/g)].length, outputs);
      };
      if (labs.length) {
        const [lab, body] = labs[0];
        expectedCounts(body, 1, 2);
        expectedCounts(markup.replace(lab, ""), 7, 14);
      } else {
        expectedCounts(markup, 7, 14);
      }
      assert.equal([...markup.matchAll(/<details class="lesson-disclosure lesson-supplement"(?: data-reading-skip)?>/g)].length,
        topic.id === "M01-T01" ? 2 : 3);
      assert.equal([...markup.matchAll(/class="lesson-evidence"/g)].length, topic.id === "M02-T02" ? 12 : 15);
      if (topic.id === "M01-T01") {
        assert.match(markup, /<h5>Run your first example<\/h5>[\s\S]*?<a href="https:\/\/www\.online-python\.com\/" target="_blank" rel="noopener noreferrer">Open Python Editor<\/a>/);
        assert.doesNotMatch(markup, /language-bash|m01_t01_step\.py|PowerShell/);
        assert.match(markup, /<h4>Independent Assignment<\/h4>/);
        assert.match(markup, /<a href="#m01-t02">Inference, sampling and repeatability<\/a>/);
      }
      if (topic.id === "M01-T02") {
        assert.match(markup, /<h4>Independent Assignment<\/h4>/);
        assert.match(markup, /<a href="#m01-t03">Application architecture and a first smoke test<\/a>/);
      }
      if (topic.id === "M01-T03") {
        assert.match(markup, /<h4>Independent Assignment<\/h4>/);
        assert.match(markup, /<a href="#m02-t01">Objectives, dimensions and failure taxonomy<\/a>/);
      }
      if (topic.id === "M02-T02") {
        assert.match(markup, /<h4>Independent Assignment<\/h4>/);
        assert.match(markup, /<a href="#m02-t03">Offline, online and the evaluation lifecycle<\/a>/);
      }
      if (topic.id === "M02-T03") {
        assert.match(markup, /<h4>Independent Assignment<\/h4>/);
        assert.match(markup, /<a href="#m03-t01">Exact match, normalization and rules<\/a>/);
      }
    }
  }
});

test("learner HTML excludes internal technical metadata and keeps public resources", () => {
  const privateFields = ["Technical Reference", "Existing files", "Audit findings", "Reuse strategy",
    "Teaching and experiment gaps", "Technical corrections", "Existing Repository Coverage"];
  const source = read("MASTER_CURRICULUM.md");
  for (const field of privateFields) {
    assert.equal(html.includes(field), false, field);
  }
  for (const field of privateFields.slice(1, 6)) {
    assert(source.includes("**" + field + ".**"), field);
  }
  assert.match(html, /id="coverage"><a href="index.html#library">Published examples and downloads<\/a>/);
  assert.match(html, /<summary>Teaching Plan<\/summary>/);
});

function send(element, name, values = {}) {
  const event = new Event(name, {cancelable: true});
  for (const [key, value] of Object.entries(values)) Object.defineProperty(event, key, {value});
  element.dispatchEvent(event);
  return event;
}

test("compact navigator shares live progress and preserves its view through Escape, minimize, and close", () => {
  const path = data.paths.D;
  const topic = path.closure[1];
  const ui = start(lessonHash(path.id, topic));
  const nav = name => ui.el("navigator-" + name);
  assert.equal(ui.dock.hidden, false);
  assert.equal(Boolean(nav("dialog").open), false);
  send(nav("launch"), "click");
  assert.equal(nav("dialog").open, true);
  assert.equal(nav("title").focused, true);
  assert.deepEqual(nav("map").children.map(node => node.dataset.lesson), path.closure);
  const node = nav("map").children[1];
  assert.equal(node.getAttribute("aria-current"), "step");
  assert.equal(node.dataset.completed, "false");
  send(ui.el("guided-complete"), "click");
  assert.match(node.getAttribute("aria-label"), /Current · Completed.*Required first/);
  assert.equal(node.dataset.completed, "true");

  const viewport = nav("viewport");
  send(nav("center"), "click");
  assert.equal(node.focused, true);
  send(nav("zoom-in"), "click");
  assert.equal(nav("zoom").textContent, "120%");
  assert.equal(send(viewport, "keydown", {key: "ArrowRight"}).defaultPrevented, true);
  send(viewport, "pointerdown", {pointerType: "mouse", button: 0, pointerId: 1, clientX: 100, clientY: 100});
  assert.equal(viewport.capturedPointer, 1);
  const x = viewport.scrollLeft;
  send(viewport, "pointermove", {pointerId: 1, clientX: 80, clientY: 85});
  assert.equal(viewport.scrollLeft, x + 20);
  send(viewport, "pointerup", {pointerId: 1});
  const position = [viewport.scrollLeft, viewport.scrollTop];
  assert.equal(send(nav("dialog"), "cancel").defaultPrevented, true);
  assert.equal(nav("dialog").open, false);
  assert.equal(nav("launch").focused, true);
  viewport.scrollTo({left: 0, top: 0});
  send(nav("launch"), "click");
  assert.deepEqual([viewport.scrollLeft, viewport.scrollTop], position);
  assert.equal(nav("zoom").textContent, "120%");

  send(nav("minimize"), "click");
  assert.equal(nav("dialog").open, false);
  assert.equal(ui.dock.hidden, false);
  send(nav("launch"), "click");
  send(nav("close"), "click");
  assert.equal(nav("dialog").open, false);
  assert.equal(ui.dock.hidden, false);
  send(nav("launch"), "click");
  assert.equal(nav("dialog").open, true);

  send(nav("map"), "click", {target: nav("map").children[2]});
  assert.equal(ui.location.hash, lessonHash(path.id, path.closure[2]));
  assert.equal(nav("dialog").open, false);
  assert.equal(ui.el("guided-title").focused, true);
  assert.equal(ui.el(topic.toLowerCase()).querySelector("[data-progress]").value, "Completed");
  assert.equal(ui.el(path.closure[2].toLowerCase()).querySelector("[data-progress]").value, "Not Started");
  send(nav("launch"), "click");
  assert.equal(nav("map").children[2].getAttribute("aria-current"), "step");
  ui.go("#detail");
  assert.equal(ui.dock.hidden, true);
  assert.equal(nav("dialog").open, false);
});

test("full map includes only path lessons, real dependency arrows, and separate order lines", () => {
  for (const path of Object.values(data.paths)) {
    const ui = start(lessonHash(path.id, path.closure[0]));
    send(ui.el("navigator-launch"), "click");
    const map = ui.el("navigator-map");
    assert.equal(map.children.length, path.closure.length);
    const members = new Set(path.closure);
    const edges = [...map.innerHTML.matchAll(/class="navigator-edge-(\w+)" data-from="([^"]+)" data-to="([^"]+)"[^>]*\/>/g)];
    const expected = path.closure.slice(1).map((id, i) => "order " + path.closure[i] + " " + id);
    for (const id of path.closure) {
      for (const kind of ["mandatory", "recommended", "conditional"]) {
        for (const edge of data.topics[id][kind]) if (members.has(edge.id)) expected.push(kind + " " + edge.id + " " + id);
      }
    }
    assert.deepEqual(edges.map(match => match.slice(1).join(" ")).sort(), expected.sort());
    for (const [markup, kind] of edges) assert.equal(markup.includes("marker-end="), kind !== "order");
  }

  const css = read("docs/assets/academy.css");
  assert.match(css, /\.navigator-dock\s*\{\s*position:fixed; inset-inline-start:/);
  assert.match(css, /\.academy-layout:has\(\.navigator-dock:not\(\[hidden\]\)\) > \.academy-main\s*\{\s*margin-inline-start:/);
  assert.match(html, /<div class="academy-sidebar-column">[\s\S]*?<\/details>\s*<aside class="navigator-dock"[^>]* hidden>/);
  assert.match(html, /<span class="navigator-label">Learning Navigator<\/span>/);
  assert.match(css, /@media\(max-width:620px\) \{\s*#navigator-dialog \{ width:calc\(100% - \.75rem\); height:94vh; height:94dvh/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
  assert.match(html, /<dialog id="navigator-dialog" aria-labelledby="navigator-title" aria-describedby="navigator-help">/);
});
