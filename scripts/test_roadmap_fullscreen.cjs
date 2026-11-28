const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {resolve} = require("node:path");
const {setImmediate: tick} = require("node:timers/promises");
const {test} = require("node:test");
const vm = require("node:vm");

const read = file => readFileSync(resolve(__dirname, "..", file), "utf8");
const html = read("docs/master-curriculum.html");
const source = read("docs/learning_roadmap.js");
const data = html.match(/<script id="roadmap-data" type="application\/json">([^]*?)<\/script>/)[1];

function setup(native) {
  class Element extends EventTarget {
    constructor(id) {
      super();
      this.id = id;
      this.classes = new Set();
      this.classList = {
        add: (...items) => items.forEach(item => this.classes.add(item)),
        remove: (...items) => items.forEach(item => this.classes.delete(item)),
      };
      this.attrs = {};
      this.children = [];
      this.value = "";
      this.options = [{}, {}, {}];
      this.clientWidth = 760;
      this.clientHeight = 420;
      this.tabIndex = 0;
    }
    add(child) { this.children.push(child); child.parentElement = this; }
    setAttribute(key, value) { this.attrs[key] = value; }
    removeAttribute(key) { delete this.attrs[key]; }
    focus() { page.activeElement = this; }
    getClientRects() {
      return this.hidden || (this.id === "road-fullscreen-open" && app.classes.has("is-fullscreen")) ? [] : [{}];
    }
    closest(selector) { return selector === "[data-select]" && this.dataset?.select ? this : null; }
    matches(selector) { return selector === ":disabled" && this.disabled; }
    setPointerCapture() {}
    set innerHTML(markup) { this.markup = markup; this.firstElementChild = {style: {}}; }
    querySelector() { return null; }
    querySelectorAll() { return [closer, search, viewport, controls.at(-1)]; }
  }

  const page = new EventTarget();
  const listeners = new Map();
  const add = page.addEventListener.bind(page);
  const remove = page.removeEventListener.bind(page);
  page.addEventListener = (type, fn, options) => {
    if (!listeners.has(type)) listeners.set(type, new Set());
    listeners.get(type).add(fn);
    add(type, fn, options);
  };
  page.removeEventListener = (type, fn, options) => {
    listeners.get(type)?.delete(fn);
    remove(type, fn, options);
  };
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, new Element(id));
    return elements.get(id);
  };
  const road = id => element("road-" + id);
  const controls = ["path", "mode", "search", "stage", "results", "focus", "optional", "export",
    "download-status", "details", "jump", "title", "estimate", "zoom", "clear", "zoom-in", "zoom-out",
    "reset", "legend", "svg", "html", "png"].map(road);
  const app = element("roadmap-app");
  const header = road("fullscreen-header");
  const opener = road("fullscreen-open");
  const closer = road("fullscreen-close");
  const viewport = road("viewport");
  const search = road("search");
  const sidebar = element("sidebar");
  const heading = element("heading");
  const existingInert = element("hidden-panel");
  existingInert.inert = true;
  page.documentElement = element("html");
  page.body = element("body");
  page.documentElement.add(page.body);
  page.body.add(sidebar);
  const container = element("main");
  page.body.add(container);
  container.add(heading);
  container.add(existingInert);
  container.add(app);
  header.add(closer);
  for (const control of [header, opener, viewport, ...controls]) app.add(control);
  page.getElementById = id => element(id);
  element("roadmap-data").textContent = data;
  header.hidden = true;
  road("mode").value = "module";

  let requests = 0;
  let exits = 0;
  page.fullscreenEnabled = native !== "missing";
  page.fullscreenElement = null;
  function nativeExit() {
    page.fullscreenElement = null;
    page.dispatchEvent(new Event("fullscreenchange"));
  }
  if (native !== "missing") {
    app.requestFullscreen = async () => {
      requests++;
      if (native === "reject") throw new Error("Fullscreen denied");
      page.fullscreenElement = app;
      page.dispatchEvent(new Event("fullscreenchange"));
    };
    page.exitFullscreen = async () => { exits++; nativeExit(); };
  }
  const browser = {
    scrollX: 4, scrollY: 310, restored: [],
    scrollTo(value) { this.restored.push(value); },
  };
  const event = (target, type, props = {}) => {
    const action = new Event(type, {cancelable: true});
    for (const [key, value] of Object.entries(props)) Object.defineProperty(action, key, {value});
    target.dispatchEvent(action);
    return action;
  };
  vm.runInNewContext(source, {document: page, window: browser, Event, CustomEvent,
    LearningProgress: require("../docs/learning_progress.js")});
  event(page, "curriculum-tab", {detail: "#roadmap"});

  return {app, header, opener, closer, viewport, search, sidebar, heading, existingInert, page, browser, road,
    get requests() { return requests; }, get exits() { return exits; }, nativeExit,
    listenerCount: type => listeners.get(type)?.size ?? 0,
    enter: async () => { event(opener, "click"); await tick(); },
    close: async () => { event(closer, "click"); await tick(); },
    key: (key, props = {}) => event(page, "keydown", {key, ...props}),
    event, camera: () => viewport.firstElementChild.style.transform};
}

test("native fullscreen uses the original roadmap and closes with focus and scroll restored", async () => {
  const ui = setup("native");
  const original = ui.camera();
  await ui.enter();
  assert.equal(ui.requests, 1);
  assert.equal(ui.page.fullscreenElement, ui.app);
  assert.equal(ui.page.activeElement, ui.closer);
  assert.equal(ui.app.attrs["aria-modal"], "true");
  assert.equal(ui.header.hidden, false);
  assert.equal(ui.app.classes.has("is-fullscreen-fallback"), false);
  assert.equal(ui.camera(), original);
  assert.equal(ui.key("Escape").defaultPrevented, false, "browser owns native Escape");

  await ui.close();
  assert.equal(ui.exits, 1);
  assert.equal(ui.header.hidden, true);
  assert.equal(ui.page.activeElement, ui.opener);
  assert.equal(ui.browser.restored[0].top, 310);
  assert.equal(ui.browser.restored[0].left, 4);
  assert.equal(ui.app.classes.size, 0);
  assert.equal(ui.camera(), original);
});

test("browser-native exit clears temporary state without calling exitFullscreen again", async () => {
  const ui = setup("native");
  await ui.enter();
  ui.nativeExit();
  assert.equal(ui.exits, 0);
  assert.equal(ui.header.hidden, true);
  assert.equal(ui.listenerCount("fullscreenchange"), 0);
  assert.equal(ui.listenerCount("keydown"), 0);
  assert.equal(ui.page.documentElement.classes.has("roadmap-fullscreen"), false);
  assert.equal(ui.app.attrs.role, undefined);
  assert.equal(ui.page.activeElement, ui.opener);
});

test("unsupported and rejected fullscreen keep the diagram available in a keyboard-accessible fallback", async () => {
  for (const native of ["missing", "reject"]) {
    const ui = setup(native);
    await ui.enter();
    assert.equal(ui.app.classes.has("is-fullscreen-fallback"), true);
    assert.equal(ui.sidebar.inert, true);
    assert.equal(ui.heading.inert, true);
    assert.equal(ui.page.documentElement.classes.has("roadmap-fullscreen"), true);
    assert.equal(ui.listenerCount("fullscreenchange"), 0);
    assert.equal(ui.key("Tab", {shiftKey: true}).defaultPrevented, true);
    assert.notEqual(ui.page.activeElement, ui.closer);
    assert.equal(ui.key("Tab").defaultPrevented, true);
    assert.equal(ui.page.activeElement, ui.closer);

    assert.equal(ui.key("Escape").defaultPrevented, true);
    assert.equal(ui.app.classes.size, 0);
    assert.equal(ui.sidebar.inert, false);
    assert.equal(ui.heading.inert, false);
    assert.equal(ui.existingInert.inert, true);
    assert.equal(ui.page.activeElement, ui.opener);
    assert.equal(ui.browser.restored.length, 1);
    assert.equal(ui.key("Escape").defaultPrevented, false);
  }
});

test("fullscreen preserves zoom and pan, including changes made while expanded", async () => {
  const ui = setup("missing");
  ui.event(ui.road("zoom-in"), "click");
  const zoomed = ui.camera();
  ui.event(ui.viewport, "keydown", {key: "ArrowLeft"});
  const before = ui.camera();
  assert.notEqual(before, zoomed);
  await ui.enter();
  assert.equal(ui.camera(), before);
  ui.viewport.clientWidth = 1120;
  ui.viewport.clientHeight = 280;
  ui.event(ui.road("zoom-in"), "click");
  const fullscreenZoom = ui.camera();
  assert.notEqual(fullscreenZoom, before);
  ui.event(ui.viewport, "pointerdown", {pointerId: 1, button: 0, clientX: 80, clientY: 60});
  ui.event(ui.viewport, "pointermove", {pointerId: 1, clientX: 111, clientY: 80});
  ui.event(ui.viewport, "pointerup", {pointerId: 1});
  const full = ui.camera();
  assert.notEqual(full, fullscreenZoom);
  await ui.close();
  assert.equal(ui.camera(), full);
  assert.equal(ui.header.hidden, true);
});

test("search and selection remain available in fullscreen and navigation releases the overlay", async () => {
  const ui = setup("missing");
  await ui.enter();
  ui.search.value = "M15";
  ui.event(ui.search, "input");
  assert.equal(ui.road("results").hidden, false);
  const item = new EventTarget();
  item.dataset = {select: "M15"};
  item.closest = () => item;
  ui.event(ui.road("results"), "click", {target: item});
  assert.match(ui.road("title").textContent, /M15/);
  const node = new EventTarget();
  node.dataset = {node: "M08"};
  node.closest = () => node;
  assert.equal(ui.event(ui.viewport, "click", {target: node}).defaultPrevented, true);
  assert.match(ui.road("title").textContent, /M08/);
  ui.event(ui.page, "curriculum-tab", {detail: "#detail"});
  assert.equal(ui.app.classes.size, 0);
  assert.equal(ui.browser.restored.length, 0, "explicit navigation keeps its own page focus and position");
});

test("rapid clicks and repeated entry do not accumulate fullscreen or Escape listeners", async () => {
  const ui = setup("native");
  for (let i = 0; i < 3; i++) {
    ui.event(ui.opener, "click");
    await ui.enter();
    assert.equal(ui.requests, i + 1);
    assert.equal(ui.listenerCount("fullscreenchange"), 1);
    assert.equal(ui.listenerCount("keydown"), 1);
    await ui.close();
    assert.equal(ui.listenerCount("fullscreenchange"), 0);
    assert.equal(ui.listenerCount("keydown"), 0);
  }
  assert.equal(ui.browser.restored.length, 3);
});

test("generated roadmap uses a visible toolbar action and viewport-sized fullscreen styling", () => {
  assert.match(html, /<button[^>]+id="road-fullscreen-open"[^>]*>\s*<svg[^>]*aria-hidden="true"/);
  assert.match(html, /<div id="road-fullscreen-header"[^>]*hidden>[\s\S]*?<button[^>]*aria-label="Close fullscreen roadmap"/);
  assert.match(html, /#roadmap-app\.is-fullscreen-fallback \{[^}]*position:fixed[^}]*height:100dvh/);
  assert.match(html, /#roadmap-app\.is-fullscreen #road-viewport \{[^}]*flex:1 1 0/);
});
