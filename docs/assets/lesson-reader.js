(() => {
  "use strict";

  const toolbar = '<details class="lesson-reader-disclosure"><summary>Listen</summary>' +
    '<div class="lesson-reader-content"><h4 class="lesson-reader-heading">Listen</h4>' +
    '<div class="lesson-reader-controls" role="group" aria-label="Listen to this lesson">' +
    '<label>Section <select data-reading-section><option>Entire lesson</option></select></label>' +
    '<button type="button" data-reading-start>Read Aloud</button>' +
    '<button type="button" data-reading-pause disabled>Pause</button>' +
    '<button type="button" data-reading-stop disabled>Stop</button>' +
    '<label>Voice <select data-reading-voice title="Changing voice restarts the current paragraph." disabled>' +
    '<option value="" disabled>No English voices listed</option></select></label>' +
    '<button type="button" data-reading-preview disabled>Preview Voice</button>' +
    '<label>Speed <select data-reading-speed title="Changing speed restarts the current paragraph.">' +
    '<option value="0.75">0.75×</option><option value="1" selected>1×</option>' +
    '<option value="1.25">1.25×</option><option value="1.5">1.5×</option></select></label>' +
    '</div><p class="lesson-reader-status" data-reading-status role="status"></p></div></details>';

  const blocked = "[hidden], [aria-hidden=true], [data-reading-skip], details:not([open]), " +
    "nav, header, footer, script, style, button, input, select, textarea, label, progress, " +
    "summary, pre, table, .lesson-output, .lesson-reader, .run-command, .file-tag, .concept-chip";
  const blocks = "h1, h2, h3, h4, h5, h6, p, li, dt, dd, blockquote, div";
  // Lesson prose can name code concepts. Skip inline shell invocations as well as command blocks.
  const command = /^(?:\$\s|(?:cd|python[\d.]*|py|pip[\d.]*|ollama|docker(?:-compose)?)\s+\S)/;
  const supported = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  const speech = supported ? window.speechSynthesis : null;
  const storageKey = "testneural-academy-reading";
  const speeds = ["0.75", "1", "1.25", "1.5"];
  const views = [];
  const preferences = {voice: "", speed: "1"};
  let active = null;
  let englishVoice;
  let choices = new Map();

  try {
    const saved = JSON.parse(window.localStorage.getItem(storageKey));
    if (typeof saved?.voice === "string") preferences.voice = saved.voice;
    if (speeds.includes(saved?.speed)) preferences.speed = saved.speed;
  } catch { /* Storage may be unavailable. */ }

  function savePreferences() {
    try { window.localStorage.setItem(storageKey, JSON.stringify(preferences)); }
    catch { /* Keep the preference for this visit. */ }
  }

  function collect(roots) {
    const entries = [];
    let owner;
    let text = "";

    function flush() {
      const phrase = text.replace(/\s+/g, " ").trim();
      if (phrase) entries.push({node: owner, text: phrase});
      text = "";
    }

    function visit(node, block) {
      if (node.nodeType === 3) {
        if (!block) return;
        if (owner !== block) flush();
        owner = block;
        text += node.textContent;
        return;
      }
      if (node.nodeType !== 1 || node.matches(blocked)) return;
      if (node.tagName === "CODE" && command.test(node.textContent.trim())) return;
      if (node.tagName === "BR" && block) {
        if (owner === block) text += " ";
        return;
      }
      const nextBlock = node.matches(blocks) ? node : block;
      if (nextBlock !== block) flush();
      for (const child of node.childNodes) visit(child, nextBlock);
      if (nextBlock !== block) flush();
    }

    for (const root of roots) {
      if (root) visit(root, null);
    }
    return entries;
  }

  function speechChunks(entries) {
    return entries.flatMap(({node, text}) => {
      const chunks = [];
      let remaining = text;
      // Keep each utterance small. Split at a word boundary when possible.
      while (remaining.length > 220) {
        const boundary = remaining.lastIndexOf(" ", 220);
        const end = boundary > 0 ? boundary : 220;
        chunks.push({node, text: remaining.slice(0, end)});
        remaining = remaining.slice(end).trimStart();
      }
      if (remaining) chunks.push({node, text: remaining});
      return chunks;
    });
  }

  function syncPreferences() {
    const value = [...choices].find(([, voice]) => voice === englishVoice)?.[0] || "";
    for (const view of views) {
      view.voice.value = value;
      view.speed.value = preferences.speed;
    }
  }

  function updateVoices() {
    const locale = voice => voice.lang.toLowerCase().replaceAll("_", "-");
    // Browsers do not expose a quality or gender rating. Use only voice-name quality hints.
    const quality = voice => Number(/\b(natural|neural|premium|enhanced|studio)\b/i.test(voice.name));
    const voices = speech.getVoices().filter(voice => voice.name && /^en(?:-|$)/.test(locale(voice)));
    voices.sort((a, b) => quality(b) - quality(a) ||
      Number(Boolean(b.localService)) - Number(Boolean(a.localService)) ||
      Number(Boolean(b.default)) - Number(Boolean(a.default)));
    const id = voice => voice.voiceURI || voice.name + "|" + locale(voice);
    const available = new Map();
    const labels = new Set();
    for (const voice of voices) {
      const label = voice.name + "|" + locale(voice);
      if (available.has(id(voice)) || labels.has(label)) continue;
      available.set(id(voice), voice);
      labels.add(label);
    }

    choices = new Map();
    for (const [region, limit] of [["en-in", 2], ["en-us", 2], ["en-gb", 1]]) {
      const regional = [...available.values()].filter(voice => locale(voice) === region);
      for (const voice of regional.slice(0, limit)) choices.set(id(voice), voice);
    }
    for (const [key, voice] of available) {
      if (choices.size === 5) break;
      choices.set(key, voice);
    }
    const saved = available.get(preferences.voice);
    if (saved && !choices.has(preferences.voice)) {
      if (choices.size === 5) choices.delete([...choices.keys()].at(-1));
      choices.set(preferences.voice, saved);
    }
    const options = [...choices.values()];
    englishVoice = saved || options.find(voice => voice.localService && voice.default) ||
      options.find(voice => voice.localService) || options[0];

    for (const view of views) {
      view.voice.length = 0;
      for (const [key, voice] of choices) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = voice.name + " · " + voice.lang;
        view.voice.append(option);
      }
      if (!choices.size) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No English voices listed";
        option.disabled = true;
        view.voice.append(option);
      }
      view.voice.disabled = !choices.size;
      view.preview.disabled = !englishVoice || Boolean(active);
    }
    syncPreferences();
  }

  function restartParagraph() {
    const session = active;
    if (!session) return;
    if (session.preview) {
      stop("Voice preview stopped.");
      return;
    }
    const node = session.queue[session.index]?.node;
    while (session.index > 0 && session.queue[session.index - 1]?.node === node) session.index -= 1;
    session.utterance = null;
    speech.cancel();
    if (session.paused) showState(session.view, "Paused. Resume restarts this paragraph with your new settings.");
    else {
      showState(session.view, "Reading. Restarted this paragraph.");
      speak(session);
    }
  }

  function showState(view, message) {
    const session = active?.view === view ? active : null;
    view.start.textContent = view.section.selectedIndex > 0 ? "Read Section" : "Read Aloud";
    view.start.disabled = !supported || !view.hasText || session?.startSection === view.section.selectedIndex;
    view.pause.disabled = !session || session.preview;
    view.pause.textContent = session?.paused ? "Resume" : "Pause";
    view.stop.disabled = !session;
    for (const reader of views) reader.preview.disabled = !englishVoice || Boolean(active);
    if (message !== undefined) view.status.textContent = message;
  }

  function refresh(view) {
    const entries = supported ? collect(view.source()) : [];
    view.hasText = entries.length > 0;
    view.headings = entries.filter(({node}) => node.tagName === view.heading).map(({node}) => node);
    view.section.length = 1;
    for (const [index, node] of view.headings.entries()) {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = node.textContent.trim();
      view.section.append(option);
    }
    view.section.disabled = !view.headings.length;
    view.speed.disabled = !supported || !view.hasText;
    showState(view, supported ? "" : "Read Aloud is unavailable in this browser.");
  }

  function clearHighlight(session) {
    session.highlight?.classList.remove("is-being-read");
    session.highlight = null;
  }

  function stop(message = "Reading stopped.") {
    if (!active) return;
    const session = active;
    active = null;
    clearHighlight(session);
    speech.cancel();
    showState(session.view, message);
  }

  function speak(session) {
    if (!isVisible(session.view)) {
      stop();
      return;
    }
    const chunk = session.queue[session.index];
    if (!chunk) {
      active = null;
      clearHighlight(session);
      showState(session.view, session.preview ? "Voice preview finished." : "Reading finished.");
      return;
    }
    if (session.highlight !== chunk.node) {
      clearHighlight(session);
      session.highlight = chunk.node;
      chunk.node.classList.add("is-being-read");
    }
    const utterance = new window.SpeechSynthesisUtterance(chunk.text);
    utterance.lang = englishVoice?.lang || "en";
    if (englishVoice) utterance.voice = englishVoice;
    utterance.rate = Number(preferences.speed);
    session.utterance = utterance;

    const current = () => active === session && session.utterance === utterance;
    utterance.onend = () => {
      if (!current()) return;
      session.utterance = null;
      session.index += 1;
      if (!session.paused) speak(session);
    };
    utterance.onerror = () => {
      if (current()) stop(session.preview ? "Voice preview could not play." :
        "Read Aloud could not continue. Select Read Aloud or Read Section to try again.");
    };
    try {
      if (speech.paused) speech.resume();
      speech.speak(utterance);
    } catch {
      if (current()) stop(session.preview ? "Voice preview could not play." :
        "Read Aloud could not start. Check your browser’s speech settings and try again.");
    }
  }

  function start(view) {
    if (view.start.disabled || document.hidden || !isVisible(view)) return;
    const entries = collect(view.source());
    const startSection = view.section.selectedIndex;
    const selected = view.headings[startSection - 1];
    const first = selected ? entries.findIndex(({node}) => node === selected) : 0;
    if (first < 0) return;
    const end = selected ? entries.findIndex(({node}, i) => i > first && node.tagName === view.heading) : -1;
    const queue = speechChunks(entries.slice(first, end < 0 ? undefined : end));
    if (!queue.length) return;
    stop();
    const session = {view, startSection, queue, index: 0, paused: false, utterance: null, highlight: null};
    active = session;
    showState(view, "Reading.");
    speak(session);
  }

  function pause(session, message = "Paused. Select Resume to continue.") {
    if (session.preview) {
      stop("Voice preview stopped.");
      return;
    }
    session.paused = true;
    speech.pause();
    showState(session.view, message);
  }

  function bind(holder, source, heading) {
    holder.innerHTML = toolbar;
    const find = name => holder.querySelector("[data-reading-" + name + "]");
    const view = {holder, source, heading, section: find("section"), start: find("start"),
      pause: find("pause"), stop: find("stop"), speed: find("speed"), status: find("status"),
      voice: find("voice"), preview: find("preview")};
    views.push(view);
    view.speed.value = preferences.speed;
    holder.hidden = false;
    view.start.addEventListener("click", () => start(view));
    view.section.addEventListener("change", () => showState(view));
    view.stop.addEventListener("click", () => {
      if (active?.view === view) stop();
    });
    view.pause.addEventListener("click", () => {
      const session = active;
      if (session?.view !== view || session.preview || document.hidden) return;
      if (!session.paused) {
        pause(session);
        return;
      }
      session.paused = false;
      showState(view, "Reading.");
      if (session.utterance) speech.resume();
      else speak(session);
    });
    view.speed.addEventListener("change", () => {
      if (!speeds.includes(view.speed.value) || view.speed.value === preferences.speed) return;
      preferences.speed = view.speed.value;
      savePreferences();
      syncPreferences();
      restartParagraph();
    });
    view.voice.addEventListener("change", () => {
      const voice = choices.get(view.voice.value);
      if (!voice) return;
      const changed = englishVoice !== voice;
      englishVoice = voice;
      preferences.voice = view.voice.value;
      savePreferences();
      syncPreferences();
      if (changed) restartParagraph();
    });
    view.preview.addEventListener("click", () => {
      if (active || !englishVoice || document.hidden || !isVisible(view)) return;
      const queue = [{node: null, text: "Hello. This is how your lessons will sound."}];
      const session = {view, preview: true, queue, index: 0, paused: false, utterance: null, highlight: null};
      active = session;
      showState(view, "Playing voice preview.");
      speak(session);
    });
    refresh(view);
    return view;
  }

  function isVisible(view) {
    return view.holder.isConnected && !view.holder.closest("[hidden], details:not([open])");
  }

  const guided = document.querySelector("[data-guided-reader]");
  const complete = document.querySelectorAll("[data-lesson-reader]");
  for (const holder of complete) {
    bind(holder, () => [holder.parentElement.querySelector(".topic-material")], "H4");
  }
  const guidedView = guided && bind(guided, () => [document.querySelector("#guided-material > .topic-material")], "H4");
  const lessonReaders = guided ? [guided, ...complete] : complete;
  if (lessonReaders.length) {
    const wide = window.matchMedia("(min-width: 75rem)");
    const disclosures = Array.from(lessonReaders, holder => holder.querySelector(".lesson-reader-disclosure"));
    const applyLayout = () => {
      for (const disclosure of disclosures) disclosure.open = wide.matches;
    };
    applyLayout();
    wide.addEventListener("change", applyLayout);
  }
  const subtitle = document.querySelector("body.academy-lesson:not(.academy-reference) > .subtitle");
  if (subtitle) {
    // The published experiments place their lesson directly between the subtitle and footer.
    const roots = [];
    for (let node = subtitle; node && node.tagName !== "FOOTER"; node = node.nextElementSibling) roots.push(node);
    const holder = document.createElement("div");
    holder.className = "lesson-reader";
    subtitle.after(holder);
    bind(holder, () => roots, "H2");
  }

  if (!speech || !(guided || complete.length || subtitle)) return;
  updateVoices();
  speech.addEventListener?.("voiceschanged", updateVoices);
  document.addEventListener("curriculum-tab", () => stop());
  document.addEventListener("curriculum-route", () => {
    stop();
    if (guidedView) refresh(guidedView);
  });
  document.addEventListener("toggle", event => {
    const disclosure = event.target;
    if (active && (!isVisible(active.view) ||
      (disclosure.matches(".topic[open]") && disclosure !== active.view.holder.closest(".topic")))) stop();
  }, true);
  document.addEventListener("input", () => {
    if (active && !isVisible(active.view)) stop();
  });
  document.addEventListener("change", () => {
    if (active && !isVisible(active.view)) stop();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && active && !active.paused) pause(active, "Paused while this tab is hidden.");
  });
  window.addEventListener("pagehide", () => stop());
  window.addEventListener("beforeprint", () => stop());
})();
