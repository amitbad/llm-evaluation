(() => {
  "use strict";

  const toolbar = '<details class="lesson-reader-disclosure"><summary>Listen</summary>' +
    '<div class="lesson-reader-content"><h4 class="lesson-reader-heading">Listen</h4>' +
    '<div class="lesson-reader-controls" role="group" aria-label="Listen to this lesson">' +
    '<label>Section <select data-reading-section><option>Entire lesson</option></select></label>' +
    '<button type="button" data-reading-start>Read Aloud</button>' +
    '<button type="button" data-reading-pause disabled>Pause</button>' +
    '<button type="button" data-reading-stop disabled>Stop</button>' +
    '<label>Voice <select data-reading-voice disabled>' +
    '<option value="" disabled>No approved voices available</option></select></label>' +
    '<button type="button" data-reading-preview disabled>Preview Voice</button>' +
    '<button type="button" data-reading-use-voice title="Save this voice for lessons. If reading, restart the current paragraph." disabled>Use Voice</button>' +
    '<label>Speed <select data-reading-speed title="Changing speed restarts the current paragraph.">' +
    '<option value="0.75">0.75×</option><option value="1" selected>1×</option>' +
    '<option value="1.25">1.25×</option><option value="1.5">1.5×</option></select></label>' +
    '</div><p class="lesson-reader-status" data-reading-voice-info></p>' +
    '<p class="lesson-reader-status" data-reading-tracking></p>' +
    '<p class="lesson-reader-status" data-reading-status role="status"></p></div></details>';

  const blocked = "[hidden], [aria-hidden=true], [data-reading-skip], details:not([open]), " +
    "nav, header, footer, script, style, button, input, select, textarea, label, progress, " +
    "summary, pre, table, .lesson-output, .lesson-reader, .run-command, .file-tag, .concept-chip";
  const blocks = "h1, h2, h3, h4, h5, h6, p, li, dt, dd, blockquote, div";
  // Lesson prose can name code concepts. Skip inline shell invocations as well as command blocks.
  const command = /^(?:\$\s|(?:cd|python[\d.]*|py|pip[\d.]*|ollama|docker(?:-compose)?)\s+\S)/;
  const supported = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  const speech = supported ? window.speechSynthesis : null;
  const highlightName = "academy-reading-word";
  const wordHighlight = window.CSS?.highlights && typeof window.Highlight === "function" &&
    typeof document.createRange === "function";
  const storageKey = "testneural-academy-reading";
  const speeds = ["0.75", "1", "1.25", "1.5"];
  const approvedVoices = [
    ["Samantha", "en-US"], ["Google US English", "en-US"], ["Daniel", "en-GB"],
    ["Google UK English Female", "en-GB"], ["Google UK English Male", "en-GB"],
    ["Karen", "en-AU"], ["Tessa", "en-ZA"],
  ];
  const views = [];
  const preferences = {voice: "", speed: "1"};
  let active = null;
  let readingVoice = "";
  let audition = "";
  let browserVoice;
  let savedChoice = "";
  let choices = new Map();
  const locale = value => (value || "").trim().toLowerCase().replaceAll("_", "-");
  const voiceKey = (name, lang) => name.trim().toLowerCase().replace(/[\s_-]+/g, " ") + "|" + locale(lang);

  try {
    const saved = JSON.parse(window.localStorage.getItem(storageKey));
    if (typeof saved?.voice === "string") preferences.voice = saved.voice;
    if (speeds.includes(saved?.speed)) preferences.speed = saved.speed;
  } catch { /* Storage may be unavailable. */ }

  function savePreferences() {
    try { window.localStorage.setItem(storageKey, JSON.stringify(preferences)); }
    catch { /* Keep the preference for this visit. */ }
  }

  function collect(roots, mapOffsets = false) {
    const entries = [];
    let owner;
    let parts = [];
    let positions = [];
    let length = 0;
    let pendingSpace = false;

    function flush() {
      if (length) entries.push({node: owner, text: parts.join(""), positions});
      parts = [];
      positions = [];
      length = 0;
      pendingSpace = false;
    }

    function appendText(node) {
      for (const {0: piece, index} of node.textContent.matchAll(/\s+|\S+/g)) {
        if (/^\s/.test(piece)) {
          pendingSpace = true;
          continue;
        }
        if (pendingSpace && length) {
          parts.push(" ");
          length += 1;
        }
        pendingSpace = false;
        parts.push(piece);
        if (mapOffsets) positions.push({start: length, end: length + piece.length, node, offset: index});
        length += piece.length;
      }
    }

    function visit(node, block) {
      if (node.nodeType === 3) {
        if (!block) return;
        if (owner !== block) flush();
        owner = block;
        appendText(node);
        return;
      }
      if (node.nodeType !== 1 || node.matches(blocked)) return;
      if (node.tagName === "CODE" && command.test(node.textContent.trim())) return;
      if (node.tagName === "BR" && block) {
        if (owner === block) pendingSpace = true;
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
    const sentences = typeof Intl.Segmenter === "function" ? new Intl.Segmenter("en", {granularity: "sentence"}) : null;
    return entries.flatMap(entry => {
      const {text} = entry;
      const limit = 1200;
      if (!sentences || text.length <= limit) return [{entry, offset: 0, text}];
      const chunks = [];
      let start = 0;
      // The limit is a batching hint. Never interrupt a single sentence to reach it.
      function add(end) {
        const slice = text.slice(start, end).trimEnd();
        if (slice) chunks.push({entry, offset: start, text: slice});
        start = end;
      }
      for (const {index, segment} of sentences.segment(text)) {
        if (index > start && index + segment.length - start > limit) add(index);
      }
      add(text.length);
      return chunks;
    });
  }

  function showVoiceControls() {
    if (!supported) return;
    const selected = audition || readingVoice;
    let message = choices.size ? "" : "No approved voices are available. Read Aloud uses the browser’s English voice.";
    if (choices.size && preferences.voice && !savedChoice) {
      message = "The saved voice is unavailable. New playback uses the first available approved voice.";
    }
    if (choices.size && active && !active.preview) message += " Stop reading to preview a voice.";
    if (audition) message += " Choose Use Voice to save your selection for lessons.";
    for (const view of views) {
      view.preview.disabled = !selected || Boolean(active);
      view.useVoice.disabled = !selected || selected === savedChoice;
      view.voiceInfo.textContent = message.trim();
    }
  }

  function syncPreferences() {
    for (const view of views) {
      view.voice.value = audition || readingVoice;
      view.speed.value = preferences.speed;
    }
    showVoiceControls();
  }

  function updateVoices() {
    const voices = speech.getVoices();
    const english = voices.filter(voice => /^en(?:-|$)/.test(locale(voice.lang)));
    browserVoice = english.find(voice => voice.default) || english[0];
    choices = new Map();
    const labels = new Map();
    for (const [name, lang] of approvedVoices) {
      const key = voiceKey(name, lang);
      const matches = english.filter(voice => voice.name && voiceKey(voice.name, voice.lang) === key);
      const voice = matches.find(item => item.voiceURI && item.voiceURI === preferences.voice) ||
        matches.find(item => item.default) || matches[0];
      if (voice) {
        choices.set(key, voice);
        labels.set(key, name + " · " + lang);
      }
    }
    savedChoice = choices.has(preferences.voice) ? preferences.voice :
      [...choices].find(([, voice]) => preferences.voice &&
        (voice.voiceURI === preferences.voice || voice.name + "|" + locale(voice.lang) === preferences.voice))?.[0] ?? "";
    readingVoice = savedChoice || (choices.keys().next().value ?? "");
    if (!choices.has(audition) || audition === readingVoice) audition = "";

    for (const view of views) {
      view.voice.replaceChildren();
      for (const [key, label] of labels) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = label;
        view.voice.append(option);
      }
      if (!choices.size) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No approved voices available";
        option.disabled = true;
        view.voice.append(option);
      }
      view.voice.disabled = !choices.size;
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
    const entry = session.queue[session.index]?.entry;
    while (session.index > 0 && session.queue[session.index - 1]?.entry === entry) session.index -= 1;
    session.utterance = null;
    clearHighlight(session);
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
    showVoiceControls();
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
    if (wordHighlight) window.CSS.highlights.delete(highlightName);
    session.view.tracking.textContent = "";
  }

  // Both arrays are ordered by offset in the normalized utterance or paragraph.
  function firstEndingAfter(ranges, offset) {
    let from = 0;
    let to = ranges.length;
    while (from < to) {
      const middle = (from + to) >>> 1;
      if (ranges[middle].end <= offset) from = middle + 1;
      else to = middle;
    }
    return ranges[from];
  }

  function wordAt(words, index, length, textLength) {
    if (!Number.isInteger(index) || index < 0 || index >= textLength) return null;
    const word = firstEndingAfter(words, index);
    if (!word) return null;
    if (word.start <= index) return word;
    // Some engines include leading punctuation in a reported word span.
    const end = index + length;
    const next = firstEndingAfter(words, word.end);
    if (Number.isInteger(length) && length > 0 && end <= textLength &&
        word.end <= end && (!next || next.start >= end)) return word;
    return null;
  }

  function rangeFor(entry, start, end) {
    const first = firstEndingAfter(entry.positions, start);
    const last = firstEndingAfter(entry.positions, end - 1);
    if (!first || !last || start < first.start || end - 1 < last.start) return null;
    const startOffset = first.offset + start - first.start;
    const endOffset = last.offset + end - last.start;
    if (startOffset > first.node.textContent.length || endOffset > last.node.textContent.length) return null;
    const range = document.createRange();
    range.setStart(first.node, startOffset);
    range.setEnd(last.node, endOffset);
    return range;
  }

  function keepVisible(rect) {
    if (!rect || !rect.height || !window.innerHeight) return;
    const height = window.innerHeight;
    const topMargin = Math.min(72, height * .2);
    const bottomMargin = Math.min(44, height * .15);
    const visible = rect.height > height - topMargin - bottomMargin
      ? rect.bottom > topMargin && rect.top < height - bottomMargin
      : rect.top >= topMargin && rect.bottom <= height - bottomMargin;
    if (!visible) window.scrollBy?.({top: rect.top - height / 2, behavior: "instant"});
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
    const node = chunk.entry?.node || null;
    const sameBlock = session.highlight === node;
    clearHighlight(session);
    if (node) {
      session.highlight = node;
      node.classList.add("is-being-read");
      session.view.tracking.textContent = "Paragraph highlight while word timing is unavailable.";
      if (!sameBlock) keepVisible(node.getBoundingClientRect?.());
    }
    const utterance = new window.SpeechSynthesisUtterance(chunk.text);
    const voice = session.voice;
    utterance.lang = voice?.lang?.trim().replaceAll("_", "-") || "en-US";
    if (voice) utterance.voice = voice;
    utterance.rate = Number(preferences.speed);
    session.utterance = utterance;

    const current = () => active === session && session.utterance === utterance;
    if (node && wordHighlight) {
      let words;
      let lastWord = -1;
      utterance.onboundary = event => {
        if (!current() || session.paused || (event.name && event.name !== "word")) return;
        words ??= Array.from(chunk.text.matchAll(/\p{N}+(?:[.,]\p{N}+)+|[\p{L}\p{M}\p{N}]+(?:['’\u2010-][\p{L}\p{M}\p{N}]+)*/gu),
          match => ({start: match.index, end: match.index + match[0].length}));
        const word = wordAt(words, event.charIndex, event.charLength, chunk.text.length);
        if (!word || word.start <= lastWord) return;
        const range = rangeFor(chunk.entry, chunk.offset + word.start, chunk.offset + word.end);
        if (!range) return;
        if (lastWord < 0) {
          node.classList.remove("is-being-read");
          session.view.tracking.textContent = "Word highlight follows speech.";
        }
        lastWord = word.start;
        window.CSS.highlights.set(highlightName, new window.Highlight(range));
        keepVisible(range.getBoundingClientRect());
      };
    }
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
    const entries = collect(view.source(), wordHighlight);
    const startSection = view.section.selectedIndex;
    const selected = view.headings[startSection - 1];
    const first = selected ? entries.findIndex(({node}) => node === selected) : 0;
    if (first < 0) return;
    const end = selected ? entries.findIndex(({node}, i) => i > first && node.tagName === view.heading) : -1;
    const queue = speechChunks(entries.slice(first, end < 0 ? undefined : end));
    if (!queue.length) return;
    stop();
    const session = {view, startSection, queue, index: 0, paused: false, utterance: null, highlight: null,
      voice: choices.get(readingVoice) || browserVoice};
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
      voice: find("voice"), preview: find("preview"), useVoice: find("use-voice"), voiceInfo: find("voice-info"),
      tracking: find("tracking")};
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
      if (!choices.has(view.voice.value)) return;
      audition = view.voice.value === readingVoice ? "" : view.voice.value;
      syncPreferences();
    });
    view.useVoice.addEventListener("click", () => {
      const selected = audition || readingVoice;
      if (!choices.has(selected)) return;
      const voice = choices.get(selected);
      const changed = active && !active.preview ? active.voice !== voice : readingVoice !== selected;
      readingVoice = savedChoice = preferences.voice = selected;
      audition = "";
      savePreferences();
      syncPreferences();
      if (changed) {
        if (active && !active.preview) active.voice = voice;
        restartParagraph();
      }
      if (!active) showState(view, "Voice saved for reading.");
    });
    view.preview.addEventListener("click", () => {
      const voice = choices.get(audition || readingVoice);
      if (active || !voice || document.hidden || !isVisible(view)) return;
      const queue = [{text: "Let's try a quick example. Read the question, then think about what a good answer would include."}];
      const session = {view, preview: true, voice, queue, index: 0, paused: false, utterance: null, highlight: null};
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
