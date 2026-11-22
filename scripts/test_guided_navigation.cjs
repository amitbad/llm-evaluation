// Run with node --test scripts/test_guided_navigation.cjs. No browser or packages required.
const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {resolve} = require("node:path");
const {test} = require("node:test");
const vm = require("node:vm");

const read = path => readFileSync(resolve(__dirname, "..", path), "utf8");
const html = read("docs/master-curriculum.html");
const data = JSON.parse(html.match(/<script id="roadmap-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1]
  .replace(read("docs/learning_roadmap.js"), "const CurriculumRoadmap = {};")
  .replace("LearningProgress.bindControls(progressState, CurriculumRoadmap.saveBlob);", "")
  .replace(read("docs/assets/academy.js"), "");

class Element extends EventTarget {
  constructor(props = {}) {
    super();
    Object.assign(this, {dataset: {}, children: [], value: "", attributes: {}, queries: {}}, props);
    this.classList = {toggle() {}};
  }
  getAttribute(key) { return this.attributes[key]; }
  setAttribute(key, value) { this.attributes[key] = value; }
  removeAttribute(key) { delete this.attributes[key]; }
  querySelector(key) { return this.queries[key] || null; }
  querySelectorAll(key) { return this.queries[key] || []; }
  matches(selector) { return selector.includes("#" + this.id) || (selector.includes(".topic") && this.dataset.topic); }
  closest(selector) { return selector === ".panel" ? this.panel : selector === "details" && this.dataset.topic ? this : null; }
  append(node) {
    if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(item => item !== node);
    this.children.push(node);
    node.parentElement = this;
  }
  focus() { this.focused = true; }
  scrollIntoView() { this.scrolled = true; }
}

const lessonHash = (path, topic) => "#quick-" + path.toLowerCase() + "/" + topic.toLowerCase();

function start(hash, storage = new Map()) {
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
  for (const id of ["tabs", "filters", "search", "matches", "difficulty", "subject", "status", "track",
    "clear-filters", "expand", "collapse", "quick-catalog", "progress-bar", "progress-label", "storage-note",
    "course-progress", "guided-lesson", "guided-path", "guided-position", "guided-title", "guided-estimate",
    "guided-material", "guided-status", "guided-previous", "guided-complete", "guided-next", "guided-back"]) add(id);
  const el = id => ids.get(id);
  el("guided-lesson").queries.h3 = el("guided-title");
  el("course-progress").panel = el("overview");
  add("roadmap-data", {textContent: JSON.stringify(data)});
  add("return-to-plan", {queries: {a: new Element()}});
  const topics = Object.values(data.topics).map(topic => {
    const menu = new Element({value: "Not Started"});
    const body = new Element();
    const links = [...topic.mandatory, ...topic.recommended, ...topic.conditional].map(edge =>
      new Element({attributes: {href: "#" + edge.id.toLowerCase()}}));
    body.append(add("material-" + topic.id.toLowerCase(), {queries: {'a[href^="#m"]': links}}));
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
    queries: {"#tabs a": tabs, ".topic": topics, "[data-quick-plan]": plans,
      "[data-plan-progress]": [...Object.values(planActions), overviewAction, completeAction]},
  });
  document.querySelector = selector => el(selector.slice(1));
  const location = {hash, protocol: "file:"};
  const window = new EventTarget();
  const localStorage = {
    getItem: key => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: key => storage.delete(key),
  };
  class CustomEvent extends Event {
    constructor(name, {detail}) { super(name); this.detail = detail; }
  }
  const context = vm.createContext({document, location, window, localStorage, Event, CustomEvent});
  vm.runInContext(script, context);
  return {
    el, storage, planActions, overviewAction, completeAction, window,
    run: code => vm.runInContext(code, context),
    go: next => { location.hash = next; window.dispatchEvent(new Event("hashchange")); },
  };
}

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
  ui.el("guided-complete").dispatchEvent(new Event("click"));
  assert.equal(ui.el(first.toLowerCase()).querySelector("[data-progress]").value, "Completed");
  const resumed = start(route, ui.storage);
  assert.equal(resumed.el("guided-complete").textContent, "Completed");
  assert.equal(resumed.el("guided-title").textContent, data.topics[first].title);
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
  resumed.window.dispatchEvent(new Event("afterprint"));
  assert.equal(resumed.el("guided-material").children.length, 1);
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
