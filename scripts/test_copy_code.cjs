// Run with node --test scripts/test_copy_code.cjs.
const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {resolve} = require("node:path");
const {test} = require("node:test");
const vm = require("node:vm");
const {authoredLessonIds} = require("./lesson_test_data.cjs");

const read = path => readFileSync(resolve(__dirname, "..", path), "utf8");
const sample = '    if amount < 5000:\n        print("₹5,000 ✓ & <minimum>")\n\n';

function fixture({clipboard, fallback = () => false}) {
  const timer = new Map();
  const toolbar = {hidden: true};
  const classes = new Set();
  const status = {textContent: "", classList: {
    add: name => classes.add(name), remove: name => classes.delete(name),
  }};
  const button = {
    textContent: "Copy Code",
    addEventListener: (type, handler) => { button[type] = handler; },
    focus: () => { button.focused = true; },
  };
  const textarea = {
    focus: () => { textarea.focused = true; },
    select: () => { textarea.selected = true; },
    remove: () => { textarea.removed = true; },
  };
  const block = {
    querySelector: selector => ({
      ".lesson-copy-toolbar": toolbar, ".lesson-copy-button": button,
      ".lesson-copy-status": status, "pre > code": {textContent: sample},
    })[selector],
  };
  const document = {
    readyState: "complete",
    documentElement: {dataset: {}},
    activeElement: button,
    body: {classList: {contains: () => false}, append: field => assert.equal(field, textarea)},
    querySelectorAll: selector => selector === ".lesson-code" ? [block] : [],
    querySelector: () => null,
    createElement: tag => { assert.equal(tag, "textarea"); return textarea; },
    execCommand: command => { assert.equal(command, "copy"); return fallback(textarea); },
  };
  const window = {
    matchMedia: () => ({matches: false, addEventListener() {}}),
    addEventListener() {},
    setTimeout: (handler, delay) => {
      assert.equal(delay, 2000);
      const id = Symbol();
      timer.set(id, handler);
      return id;
    },
    clearTimeout: id => timer.delete(id),
  };
  vm.runInNewContext(read("docs/assets/academy.js"), {document, window, navigator: {clipboard}});
  return {button, status, classes, textarea, toolbar, timer};
}

test("copies the exact source and resets the success feedback", async () => {
  const copied = [];
  const ui = fixture({clipboard: {writeText: async code => copied.push(code)}});
  assert.equal(ui.toolbar.hidden, false);
  await ui.button.click();
  assert.deepEqual(copied, [sample]);
  assert.equal(ui.button.textContent, "✓ Copied!");
  assert.equal(ui.status.textContent, "Code copied to clipboard.");
  assert.equal(ui.timer.size, 1);
  [...ui.timer.values()][0]();
  assert.equal(ui.button.textContent, "Copy Code");
  assert.equal(ui.status.textContent, "");
});

test("falls back to a temporary selection and restores keyboard focus", async () => {
  const ui = fixture({fallback: field => {
    assert.equal(field.value, sample);
    assert.equal(field.selected, true);
    assert.equal(field.readOnly, true);
    return true;
  }});
  await ui.button.click();
  assert.equal(ui.button.textContent, "✓ Copied!");
  assert.equal(ui.textarea.removed, true);
  assert.equal(ui.button.focused, true);
});

test("keeps the original label and gives manual instructions when copying fails", async () => {
  const ui = fixture({clipboard: {writeText: async () => { throw Error("Denied"); }}});
  await ui.button.click();
  assert.equal(ui.button.textContent, "Copy Code");
  assert.match(ui.status.textContent, /Could not copy the code.*copy it manually/);
  assert(ui.classes.has("is-error"));
  assert.equal(ui.timer.size, 0);
  assert.equal(ui.textarea.removed, true);
});

test("generated curriculum adds buttons to executable blocks and leaves transcripts alone", () => {
  const html = read("docs/master-curriculum.html");
  const sources = authoredLessonIds.flatMap(id =>
    [...read("docs/lessons/" + id.toLowerCase() + ".md").matchAll(/^```(bash|python|text)\n([\s\S]*?)^```$/gm)]);
  const rendered = [...html.matchAll(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g)];
  const wrapped = [...html.matchAll(/<div class="lesson-code">([\s\S]*?)<\/pre>\n<\/div>/g)];
  const editor = '<a href="https://www.online-python.com/" target="_blank" rel="noopener noreferrer">Open Python Editor</a>';
  const escape = text => text.replace(/[&<>"']/g, char =>
    ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;"})[char]);
  assert.deepEqual(rendered.map(([, language, code]) => [language, code]),
    sources.map(([, language, code]) => [language, escape(code)]));
  assert.deepEqual(wrapped.map(([, markup]) => markup.match(/class="language-(\w+)"/)[1]),
    sources.filter(([, language]) => language !== "text").map(([, language]) => language));
  for (const [, markup] of wrapped) {
    assert.match(markup, /role="status"/);
    assert.match(markup, /<button type="button" class="lesson-copy-button">Copy Code<\/button>/);
    assert.equal(markup.includes(editor), markup.includes('class="language-python"'));
  }
});
