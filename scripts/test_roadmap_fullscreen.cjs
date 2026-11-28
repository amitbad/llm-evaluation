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
const curriculum = JSON.parse(data);
const graph = require("../docs/learning_roadmap.js");

function setup(native, useObserver = true) {
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
    closest(selector) {
      const key = {"[data-select]": "select", "[data-node]": "node",
        "[data-module-reference]": "moduleReference", "[data-back]": "back"}[selector];
      return key && Object.hasOwn(this.dataset || {}, key) ? this : null;
    }
    matches(selector) { return selector === ":disabled" && this.disabled; }
    setPointerCapture() {}
    contains(node) { return this === node; }
    getBoundingClientRect() {
      return {left: 0, top: 0, right: this.clientWidth, bottom: this.clientHeight,
        width: this.clientWidth, height: this.clientHeight};
    }
    set innerHTML(markup) {
      this.markup = markup;
      this.firstElementChild = {style: {}};
      if (this.id === "road-viewport") {
        this.nodes = new Map([...markup.matchAll(/data-node="([^"]+)"/g)].map(([, id]) => {
          const node = new Element(id);
          node.dataset = {node: id};
          return [id, node];
        }));
      }
    }
    querySelector(selector) { return this.nodes?.get(/data-node="([^"]+)"/.exec(selector)?.[1]) || null; }
    querySelectorAll(selector) {
      if (selector === "details[data-disclosure][open]") return this.openDisclosures || [];
      return [closer, search, viewport, controls.at(-1)];
    }
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
    "download-status", "details", "jump", "title", "estimate", "readiness", "graph-meta", "zoom", "clear", "zoom-in", "zoom-out",
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
  let observer;
  const browser = Object.assign(new EventTarget(), {
    scrollX: 4, scrollY: 310, restored: [],
    requestAnimationFrame(callback) { setImmediate(callback); },
    scrollTo(value) { this.restored.push(value); },
  });
  if (useObserver) {
    browser.ResizeObserver = class {
      constructor(notify) { observer = notify; }
      observe(target) { assert.equal(target, viewport); }
    };
  }
  const event = (target, type, props = {}) => {
    const action = new Event(type, {cancelable: true});
    for (const [key, value] of Object.entries(props)) Object.defineProperty(action, key, {value});
    target.dispatchEvent(action);
    return action;
  };
  vm.runInNewContext(source, {document: page, window: browser, Event, CustomEvent,
    LearningProgress: require("../docs/learning_progress.js")});
  event(page, "curriculum-tab", {detail: "#roadmap"});

  const click = (target, dataset) => {
    const item = new Element("fixture");
    item.dataset = dataset;
    event(target, "click", {target: item});
    return item;
  };
  return {app, header, opener, closer, viewport, search, sidebar, heading, existingInert, page, browser, road, click,
    get requests() { return requests; }, get exits() { return exits; }, nativeExit,
    listenerCount: type => listeners.get(type)?.size ?? 0,
    size: (width, height) => { viewport.clientWidth = width; viewport.clientHeight = height; },
    resize: async (width, height) => {
      viewport.clientWidth = width;
      viewport.clientHeight = height;
      if (observer) observer();
      else browser.dispatchEvent(new Event("resize"));
      await tick();
    },
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
  assert.notEqual(ui.camera(), original, "fullscreen begins with a fitted graph");
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

test("fullscreen fits on entry, supports its own zoom and pan, and restores the windowed camera", async () => {
  const ui = setup("missing");
  ui.event(ui.road("zoom-in"), "click");
  const zoomed = ui.camera();
  ui.event(ui.viewport, "keydown", {key: "ArrowLeft"});
  const before = ui.camera();
  assert.notEqual(before, zoomed);
  ui.size(1480, 680);
  await ui.enter();
  const fitted = ui.camera();
  assert.notEqual(fitted, before);
  ui.event(ui.road("zoom-in"), "click");
  const fullscreenZoom = ui.camera();
  assert.notEqual(fullscreenZoom, fitted);
  ui.event(ui.viewport, "pointerdown", {pointerId: 1, button: 0, clientX: 80, clientY: 60});
  ui.event(ui.viewport, "pointermove", {pointerId: 1, clientX: 111, clientY: 80});
  ui.event(ui.viewport, "pointerup", {pointerId: 1});
  const full = ui.camera();
  assert.notEqual(full, fullscreenZoom);
  ui.event(ui.road("reset"), "click");
  assert.equal(ui.camera(), fitted);
  ui.size(760, 420);
  await ui.close();
  assert.equal(ui.camera(), before);
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

function plottedEdges(svg) {
  return [...svg.matchAll(/<path data-from="([^"]+)" data-to="([^"]+)" data-kind="([^"]+)"([^>]*)>/g)]
    .map(([, from, to, kind, attrs]) => ({from, to, kind, attrs}));
}

function panelButtons(markup) {
  return [...markup.matchAll(/data-select="([^"]+)"/g)].map(match => match[1]);
}

test("module graph projects all authoritative topic edges without dropping direct links", () => {
  const references = [];
  const chapters = read("MASTER_CURRICULUM.md").split(/^##### (M\d+-T\d+) — /m);
  for (let i = 1; i < chapters.length; i += 2) {
    const to = chapters[i].split("-")[0];
    for (const match of chapters[i + 1].matchAll(/^- \*\*(Mandatory|Recommended|Conditional) prerequisites\.\*\* (.*)$/gm)) {
      const kind = match[1].toLowerCase();
      for (const [, from] of match[2].matchAll(/\[(M\d+)-T\d+\]\(#m\d+-t\d+\)/g)) {
        if (from !== to) references.push([from, to, kind].join("|"));
      }
    }
  }
  const expected = [...new Set(references)].sort();
  const key = ({from, to, kind}) => [from, to, kind].join("|");
  assert.equal(expected.length, 110);
  const overview = graph.graph(curriculum, {mode: "module", optional: true});
  assert.deepEqual(plottedEdges(overview.svg).map(key).sort(), expected);
  for (const id of Object.keys(curriculum.modules)) {
    const selected = graph.target(curriculum, id);
    const dependencies = graph.moduleDependencies(curriculum, id);
    assert.deepEqual(dependencies.direct.upstream.map(key).sort(), expected.filter(edge => edge.split("|")[1] === id));
    assert.deepEqual(dependencies.direct.downstream.map(key).sort(), expected.filter(edge => edge.startsWith(id + "|")));
    const model = graph.graph(curriculum, {mode: "module", selection: selected, focus: true});
    assert.equal(model.count, 18);
    assert.deepEqual(plottedEdges(model.svg).filter(edge => edge.kind === "mandatory").map(key).sort(),
      expected.filter(edge => edge.endsWith("|mandatory")));
  }
});

test("M10 highlights separate mandatory arrows, distinct optional links, and dependent M17", () => {
  const ui = setup("native");
  ui.click(ui.viewport, {node: "M10"});
  assert.equal(ui.road("focus").checked, true);
  assert.equal(ui.road("optional").checked, undefined, "selection does not turn on the global optional toggle");
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M10"[^]*?Selected/);
  assert.equal(ui.viewport.nodes.size, 18);
  const edges = plottedEdges(ui.viewport.markup);
  const marked = (from, to, kind) => edges.find(edge => edge.from === from && edge.to === to && edge.kind === kind).attrs;
  assert.match(marked("M02", "M10", "mandatory"), /data-relation="upstream".*stroke-dasharray=""/);
  assert.match(marked("M03", "M10", "mandatory"), /data-relation="upstream".*stroke-dasharray=""/);
  assert.match(marked("M10", "M17", "mandatory"), /data-relation="downstream".*url\(#road-arrow-downstream\)/);
  assert.match(marked("M05", "M10", "recommended"), /data-relation="optional".*stroke-dasharray="8 5"/);
  assert.match(marked("M08", "M10", "conditional"), /data-relation="optional".*stroke-dasharray="2 5"/);
  assert.doesNotMatch(marked("M02", "M03", "mandatory"), /data-relation="upstream"/);
  assert.ok(edges.findIndex(edge => edge.attrs.includes('data-relation="context"')) <
    edges.findIndex(edge => edge.attrs.includes('data-relation="upstream"')));
});

test("M10 panel separates full module topics, topic prerequisites, and saved progress", () => {
  const ui = setup("native");
  const status = ui.page.getElementById("progress-m10-t01");
  status.value = "Completed";
  ui.page.getElementById("progress-m02-t01").value = "Completed";
  ui.click(ui.viewport, {node: "M10"});
  const details = ui.road("details");
  const panel = details.markup;
  assert.match(ui.road("estimate").textContent, /Advanced · 3 topics · 18h learner time · 1\/3 completed/);
  const upstream = panel.split("Required before starting this module")[1].split("Topics in this module")[0];
  assert.deepEqual(panelButtons(upstream), ["M03-T02", "M02-T01"]);
  assert.match(panel, /What this module prepares you for[\s\S]*?data-select="M17"/);
  assert.match(panel, /Optional preparation[\s\S]*?Required only for this exercise\/path/);
  const [topics, rest] = panel.split('<details class="road-route" data-disclosure="route">');
  const syllabus = topics.split("Topics in this module")[1].split("Optional preparation")[0];
  assert.deepEqual(panelButtons(syllabus), ["M10-T01", "M10-T02", "M10-T03"]);
  assert.match(syllabus, /Completed · Required for this topic: M03-T02/);
  assert.match(syllabus, /Not completed · Required for this topic: M10-T02/);
  const [route, progress] = rest.split('<details class="road-route" data-disclosure="progress">');
  assert.match(route, /^<summary>Suggested study order — step by step · 5 topics/);
  assert.deepEqual(panelButtons(route), ["M02-T01", "M03-T02", "M10-T01", "M10-T02", "M10-T03"]);
  assert.equal((route.match(/Required preparation from another module/g) || []).length, 2);
  assert.match(progress, /Available next based on your progress[\s\S]*saved topic completions/);
  const [available, preview] = progress.split("<h5>New if you complete this selection</h5>");
  assert.ok(panelButtons(available).includes("M10-T02"));
  assert.ok(!panelButtons(available).includes("M10-T01"));
  assert.ok(panelButtons(preview.split("</details>")[0]).includes("M17-T03"));
  assert.equal(status.value, "Completed");
  details.openDisclosures = [{dataset: {disclosure: "route"}}];
  ui.event(ui.page, "curriculum-progress");
  assert.match(details.markup, /data-disclosure="route" open/);
});

test("keyboard preview, panel navigation and Back connect the inspector and map", () => {
  const ui = setup("native");
  const details = ui.road("details");
  ui.click(ui.viewport, {node: "M10"});
  const panelRef = {dataset: {select: "M02"}, closest: () => panelRef, contains: () => false};
  ui.event(details, "focusin", {target: panelRef});
  assert.equal(ui.viewport.nodes.get("M02").classes.has("road-reference"), true);
  ui.event(details, "focusout", {target: panelRef});
  assert.equal(ui.viewport.nodes.get("M02").classes.has("road-reference"), false);
  ui.click(details, {select: "M02", moduleReference: ""});
  assert.match(ui.road("title").textContent, /^M02 /);
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M02"/);
  assert.match(details.markup, /Back to M10/);
  assert.equal(ui.page.activeElement, ui.road("title"));
  ui.click(details, {back: ""});
  assert.match(ui.road("title").textContent, /^M10 /);
  const node = ui.viewport.nodes.get("M03");
  const space = ui.event(ui.viewport, "keydown", {target: node, key: " "});
  assert.equal(space.defaultPrevented, true);
  assert.equal(ui.page.activeElement, ui.viewport.nodes.get("M03"));
  assert.match(ui.road("title").textContent, /^M03 /);
});

test("module focus can be disabled without hiding nodes, and Clear restores the overview", () => {
  const ui = setup("missing");
  const initial = ui.viewport.markup;
  ui.click(ui.viewport, {node: "M10"});
  const focus = ui.road("focus");
  focus.checked = false;
  ui.event(focus, "change");
  assert.equal(ui.viewport.nodes.size, 18);
  assert.doesNotMatch(ui.viewport.markup, /data-relation="upstream"|data-relation="downstream"/);
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M10"/);
  const optional = ui.road("optional");
  optional.checked = true;
  ui.event(optional, "change");
  assert.equal(plottedEdges(ui.viewport.markup).length, 110);
  optional.checked = false;
  ui.event(optional, "change");
  ui.click(ui.road("details"), {select: "M02", moduleReference: ""});
  assert.equal(focus.checked, false, "related module navigation respects the user's view choice");
  ui.event(ui.road("clear"), "click");
  assert.equal(focus.disabled, true);
  assert.equal(ui.viewport.markup, initial);
  assert.equal(ui.page.activeElement, ui.search);
  ui.click(ui.viewport, {node: "M10"});
  assert.equal(focus.checked, true, "a fresh selection gets the default focus");
});

function cards(svg) {
  return Object.fromEntries([...svg.matchAll(/<a [^>]*data-node="([^"]+)"[^>]*>[^]*?<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"/g)]
    .map(([, id, ...size]) => [id, size.map(Number)]));
}

function fittedGraphStaysInView(ui) {
  const [, width, height] = /viewBox="0 0 (\d+) (\d+)"/.exec(ui.viewport.markup);
  const [, x, y, scale] = /translate\(([^p]+)px,([^p]+)px\) scale\(([^)]+)\)/.exec(ui.camera()).map(Number);
  assert.ok(x >= 0 && y >= 0 && scale > 0);
  assert.ok(x + width * scale <= ui.viewport.clientWidth);
  assert.ok(y + height * scale <= ui.viewport.clientHeight);
}

test("fullscreen module geometry uses spare space and keeps cards and connectors inside the SVG", () => {
  const selected = graph.target(curriculum, "M17");
  const get = size => graph.graph(curriculum, {mode: "module", selection: selected, focus: true, optional: true, size});
  const normal = get(null);
  const wide = get({width: 1900, height: 640});
  const previous = cards(normal.svg);
  const expanded = cards(wide.svg);
  assert.ok(expanded.M17[2] > previous.M17[2]);
  const gap = (nodes, from, to) => nodes[to][0] - nodes[from][0] - nodes[from][2];
  assert.ok(gap(expanded, "M01", "M04") > gap(previous, "M01", "M04"));
  const verticalGap = nodes => nodes.M02[1] - nodes.M01[1] - nodes.M01[3];
  assert.ok(verticalGap(expanded) > verticalGap(previous));
  for (const size of [{width: 1900, height: 640}, {width: 1100, height: 510},
    {width: 880, height: 400}, {width: 650, height: 480}, {width: 320, height: 310}]) {
    const model = get(size);
    const nodes = cards(model.svg);
    assert.equal(Object.keys(nodes).length, 18);
    for (const [x, y, w, h] of Object.values(nodes)) {
      assert.ok(x > 0 && y > 0 && w > 0 && h > 0);
      assert.ok(x + w < model.width && y + h < model.height);
    }
    const links = plottedEdges(model.svg);
    assert.equal(links.length, 110);
    for (const {from, to, attrs} of links) {
      const xy = / d="([^"]+)"/.exec(attrs)[1].split(" ").map(Number).filter(Number.isFinite);
      const [ax, ay, aw, ah] = nodes[from], [bx, by, bw, bh] = nodes[to];
      const [startX, startY] = xy, [endX, endY] = xy.slice(-2);
      assert.ok(Math.abs(startX - ax - aw) < .001 && startY > ay && startY < ay + ah);
      assert.ok(endY > by && endY < by + bh);
      const distance = ax >= bx ? endX - bx - bw : bx - endX;
      assert.ok(distance > 0 && distance < 10, from + " to " + to);
      assert.ok(xy.every((coordinate, i) => coordinate >= 0 && coordinate <= (i % 2 ? model.height : model.width)));
    }
  }
});

test("the live header is outside the camera and exports retain branding and legend", () => {
  const header = html.match(/<header class="road-map-header"[^>]*>([\s\S]*?)<\/header>/)[1];
  assert.match(header, /TestNeural LLM Academy[\s\S]*LLM Evaluation Engineering[\s\S]*Curriculum revision.*18 modules/);
  assert.match(header, /id="road-legend"/);
  const ui = setup("missing");
  assert.match(ui.road("legend").markup, /Mandatory[\s\S]*Recommended[\s\S]*Conditional extension/);
  assert.doesNotMatch(ui.viewport.markup, /TestNeural LLM Academy/);
  const label = ui.road("graph-meta").textContent;
  const camera = ui.camera();
  ui.event(ui.road("zoom-in"), "click");
  assert.notEqual(ui.camera(), camera);
  assert.equal(ui.road("graph-meta").textContent, label);
  const output = graph.graph(curriculum, {mode: "module", exporting: true});
  assert.match(output.svg, /TestNeural LLM Academy[\s\S]*Curriculum revision.*18 modules[\s\S]*Mandatory[\s\S]*Conditional extension/);
  const topic = graph.target(curriculum, "M17-T01");
  const overview = graph.graph(curriculum, {mode: "module", selection: topic, focus: true});
  assert.equal(Object.keys(cards(overview.svg)).length, 18, "topic selection keeps all modules on the overview");
});

test("fullscreen refits on viewport and fallback resize events without repainting unchanged dimensions", async () => {
  for (const observer of [true, false]) {
    const ui = setup("missing", observer);
    ui.click(ui.viewport, {node: "M17"});
    ui.size(1450, 650);
    await ui.enter();
    fittedGraphStaysInView(ui);
    const enlarged = ui.viewport.firstElementChild;
    await ui.resize(1450, 650);
    assert.equal(ui.viewport.firstElementChild, enlarged);
    await ui.resize(700, 440);
    assert.notEqual(ui.viewport.firstElementChild, enlarged);
    fittedGraphStaysInView(ui);
    await ui.resize(320, 330);
    fittedGraphStaysInView(ui);
    assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M17"/);
    assert.equal(ui.road("focus").checked, true);
    assert.equal(ui.road("mode").value, "module");
    ui.event(ui.road("zoom-in"), "click");
    const zoom = Number(ui.road("zoom").textContent.slice(0, -1));
    await ui.resize(320, 430);
    const resized = Number(ui.road("zoom").textContent.slice(0, -1));
    assert.ok(Math.abs(resized - zoom) <= 1, "manual zoom survives a height-only resize");
    ui.event(ui.road("reset"), "click");
    fittedGraphStaysInView(ui);
  }
});

test("M17 readiness uses stored progress for its first topic and separates later work", () => {
  const ui = setup("native");
  ui.click(ui.viewport, {node: "M17"});
  const details = ui.road("details");
  assert.equal(ui.road("readiness").textContent, "Complete 4 required topics before starting with M17-T01.");
  const [required, content] = details.markup.split("Topics in this module");
  const [beforeFirst, beforeLater] = required.split("Before later topics in this module");
  assert.deepEqual(panelButtons(beforeFirst), ["M02-T01", "M02-T02", "M03-T02", "M05-T01"]);
  assert.deepEqual(panelButtons(beforeLater), ["M07-T01", "M10-T01", "M10-T02"]);
  assert.match(beforeFirst, /Required earlier in your learning path/);
  const [topics, rest] = content.split("Optional preparation");
  assert.deepEqual(panelButtons(topics), ["M17-T01", "M17-T02", "M17-T03"]);
  assert.match(topics, /href="#m17-t01">Open M17-T01 lesson/);
  assert.match(rest, /M04-T02[\s\S]*Helpful for M17-T01/);
  assert.match(rest, /This module does not have a required next module/);
  for (const id of panelButtons(beforeFirst).slice(1)) ui.page.getElementById("progress-" + id.toLowerCase()).value = "Completed";
  ui.event(ui.page, "curriculum-progress");
  assert.equal(ui.road("readiness").textContent, "Complete 1 required topic before starting with M17-T01.");
  ui.page.getElementById("progress-m02-t01").value = "Completed";
  ui.event(ui.page, "curriculum-progress");
  assert.equal(ui.road("readiness").textContent, "Ready to start — all required preparation for M17-T01 is complete.");
  assert.match(details.markup, /M10-T02[\s\S]*Not completed · Required for M17-T03/);
  ui.click(ui.viewport, {node: "M01"});
  assert.equal(ui.road("readiness").textContent, "You can start this module now.");
  assert.match(details.markup, /No required preparation\. You can start this module\./);
});

test("exercise-only requirements remain separate and prerequisite navigation leaves fullscreen active", async () => {
  const ui = setup("native");
  ui.click(ui.viewport, {node: "M18"});
  ui.size(1480, 700);
  await ui.enter();
  const details = ui.road("details");
  const [, recommended, conditional] = details.markup.split(/Optional preparation|Required only for this exercise\/path/);
  assert.ok(!panelButtons(recommended).includes("M13-T03"));
  assert.ok(panelButtons(conditional).includes("M13-T03"));
  assert.match(conditional, /M18-T02 — required for the live rollout governance extension/);
  assert.match(details.markup, /<h4>How to read this learning path<\/h4>/);
  ui.click(details, {select: "M13-T03"});
  assert.equal(ui.page.fullscreenElement, ui.app);
  assert.equal(ui.road("mode").value, "topic");
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M13-T03"/);
  assert.match(details.markup, /Back to M18/);
  ui.click(details, {back: ""});
  assert.equal(ui.page.fullscreenElement, ui.app);
  assert.equal(ui.road("mode").value, "module");
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M18"/);
  ui.click(details, {select: "M13-T03"});
  ui.size(760, 420);
  await ui.close();
  assert.equal(ui.road("mode").value, "topic");
  assert.match(ui.viewport.markup, /aria-pressed="true" data-node="M13-T03"/);
});
