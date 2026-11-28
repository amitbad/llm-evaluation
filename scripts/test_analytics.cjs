// Simulate loading documents without contacting Cloudflare or opening a browser.
const assert = require("node:assert/strict");
const {readFileSync, readdirSync} = require("node:fs");
const {join} = require("node:path");
const {test} = require("node:test");
const vm = require("node:vm");

const docs = join(__dirname, "..", "docs");
const source = readFileSync(join(docs, "assets", "analytics.js"), "utf8");
const origin = "https://llmacademy.testneural.in";
const beaconURL = "https://static.cloudflareinsights.com/beacon.min.js";
const preference = "testneural_analytics_optout";

function load(path, {values = new Map(), denied, historyDenied = false, forward, existing = []} = {}) {
  const scripts = [...existing];
  const notices = [];
  const state = {reader: true};
  let url = new URL(path, origin);
  let redirected;
  const storage = {
    getItem: key => values.get(key) ?? null,
    setItem(key, value) {
      if (denied !== "write") values.set(key, value);
    },
    removeItem(key) {
      if (denied !== "write") values.delete(key);
    },
  };
  const document = {
    currentScript: {dataset: {analyticsForward: forward}},
    getElementById: id => notices.find(node => node.id === id),
    querySelector: selector => scripts.find(node =>
      (selector.includes("script[data-cf-beacon]") && node.attributes?.["data-cf-beacon"]) ||
      selector.includes('script[src="' + node.src + '"]')),
    createElement: tag => ({tag, attributes: {}, setAttribute(key, value) { this.attributes[key] = value; }}),
    body: {prepend: node => notices.unshift(node)},
    head: {append: node => scripts.push(node)},
  };
  const window = {
    get localStorage() {
      if (denied === "read") throw new Error("Storage unavailable");
      return storage;
    },
    location: {get href() { return url.href; }, replace: next => { redirected = next; }},
    history: {
      state,
      replaceState(received, _, next) {
        assert.equal(received, state);
        if (historyDenied) throw new Error("History unavailable");
        url = new URL(next);
      },
    },
  };
  const run = () => vm.runInNewContext(source, {URL, window, document});
  run();
  return {scripts, notices, values, run, get url() { return url; }, get redirected() { return redirected; }};
}

test("loads one asynchronous Cloudflare beacon with the exact public token", () => {
  const page = load("/master-curriculum.html#detail");
  page.run();
  assert.equal(page.scripts.length, 1);
  const [beacon] = page.scripts;
  assert.equal(beacon.tag, "script");
  assert.equal(beacon.src, beaconURL);
  assert.equal(beacon.async, true);
  assert.deepEqual(JSON.parse(beacon.attributes["data-cf-beacon"]), {token: "b102aa6f36fe41628f59bd295681e891"});
  assert.equal(page.values.size, 0);
  assert.equal(page.notices.length, 0);
  assert.equal(load("/", {existing: [{src: beaconURL}]}).scripts.length, 1);
  assert.equal(load("/", {existing: [{src: beaconURL + "/version", attributes: {"data-cf-beacon": "{}"}}]}).scripts.length, 1);
});

test("sets exclusion before loading, keeps other URL data and persists across documents", () => {
  const activated = load("/?theme=dark&analytics_optout=1&analytics_optout=0#start");
  activated.run();
  assert.equal(activated.url.href, origin + "/?theme=dark#start");
  assert.equal(activated.values.get(preference), "true");
  assert.equal(activated.scripts.length, 0);
  assert.equal(activated.notices.length, 1);
  assert.equal(activated.notices[0].attributes.role, "status");
  assert.match(activated.notices[0].textContent, /disabled in this browser/);
  for (const path of [activated.url.href, "/lesson-m01-t01.html#quick-b/m01-t01", "/test2.html", "/full-results.html"]) {
    assert.equal(load(path, {values: activated.values}).scripts.length, 0);
  }
  assert.equal(load("/").scripts.length, 1);
});

test("clears exclusion and waits until a subsequent page load to track", () => {
  const values = new Map([[preference, "true"], ["course-progress", "untouched"]]);
  const page = load("/?analytics_optout=0#start", {values});
  page.run();
  assert.deepEqual([...values], [["course-progress", "untouched"]]);
  assert.equal(page.url.href, origin + "/#start");
  assert.match(page.notices[0].textContent, /Future page loads may be tracked/);
  assert.equal(page.scripts.length, 0);
  assert.equal(load("/lesson-m01-t01.html", {values}).scripts.length, 1);
});

test("does not claim persistence on denied storage, failed writes or failed clearing", () => {
  for (const denied of ["read", "write"]) {
    const disabled = load("/?analytics_optout=1", {denied});
    assert.equal(disabled.scripts.length, 0);
    assert.equal(disabled.url.search, "");
    assert.match(disabled.notices[0].textContent, /persistent exclusion could not be saved/);
    const enabled = load("/?analytics_optout=0", {denied, values: new Map([[preference, "true"]])});
    assert.equal(enabled.scripts.length, 0);
    assert.match(enabled.notices[0].textContent, /could not be cleared/);
  }
  assert.equal(load("/", {denied: "read"}).scripts.length, 0);
  const blockedHistory = load("/?analytics_optout=1", {historyDenied: true});
  assert.equal(blockedHistory.scripts.length, 0);
  assert.equal(blockedHistory.values.get(preference), "true");
});

test("redirects legacy and lesson addresses without a second beacon or forwarding an opt-out", () => {
  const home = load("/home.html", {forward: "index.html"});
  assert.equal(home.redirected, origin + "/index.html");
  assert.equal(home.scripts.length, 0);
  const open = load("/lesson-m01-t01.html#quick-b/m01-t01", {forward: "master-curriculum.html#m01-t01"});
  assert.equal(open.redirected, origin + "/master-curriculum.html#quick-b/m01-t01");
  assert.equal(open.scripts.length, 0);
  const optout = load("/home.html?analytics_optout=1", {forward: "index.html"});
  assert.equal(optout.redirected, undefined);
  assert.equal(optout.scripts.length, 0);
  assert.equal(optout.values.get(preference), "true");
});

test("does not send analytics from local, downloaded or preview pages", () => {
  for (const url of ["file:///tmp/master-curriculum.html", "http://localhost:8000/", "https://preview.example/"]) {
    const page = load(url + "?analytics_optout=1");
    assert.equal(page.scripts.length, 0);
    assert.equal(page.values.size, 0);
  }
});

test("each published page has one local loader and every lesson has a generated address", () => {
  const master = readFileSync(join(docs, "master-curriculum.html"), "utf8");
  const topics = [...master.matchAll(/<details class="topic" id="(m\d{2}-t\d{2})"/g)].map(match => match[1]);
  assert.ok(topics.length);
  const pages = readdirSync(docs).filter(page => page.endsWith(".html"));
  assert.deepEqual(pages.filter(page => page.startsWith("lesson-")).sort(),
    topics.map(topic => "lesson-" + topic + ".html").sort());
  for (const page of pages) {
    const html = readFileSync(join(docs, page), "utf8");
    assert.equal([...html.matchAll(/<script src="assets\/analytics\.js" defer\b/g)].length, 1, page);
    assert.doesNotMatch(html, /<script[^>]+(?:cloudflareinsights\.com|data-cf-beacon)/, page);
    if (page.startsWith("lesson-")) {
      const target = "master-curriculum.html#" + page.slice(7, -5);
      assert.ok(html.includes('data-analytics-forward="' + target + '"'), page);
      assert.ok(html.includes('<a href="' + target + '"'), page);
    }
  }
});
