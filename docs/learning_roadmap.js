"use strict";

const CurriculumRoadmap = (() => {
  const stageColors = [
    {fill: "#e9f6ee", ink: "#19553a"},
    {fill: "#eaf2fd", ink: "#204885"},
    {fill: "#f2ecfc", ink: "#55388c"},
    {fill: "#fff0df", ink: "#824316"},
    {fill: "#fcebf3", ink: "#82345d"},
  ];
  const linkStyles = {
    mandatory: {label: "Mandatory", color: "#254f71", dash: ""},
    recommended: {label: "Recommended", color: "#66448c", dash: "8 5"},
    conditional: {label: "Conditional extension", color: "#8a4715", dash: "2 5"},
  };
  const kinds = Object.keys(linkStyles);
  const values = Object.values;
  const CARD = 258;
  const STEP = 310;
  const CARD_HEIGHT = 82;

  function xml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;",
    })[char]);
  }

  function target(data, id) {
    const item = data.topics[id] || data.modules[id] || data.paths[id];
    if (!item) return null;
    const roots = item.roots || item.topics || [id];
    return {
      ...item, roots, kind: data.topics[id] ? "topic" : data.modules[id] ? "module" : "path",
      total: item.closure.reduce((hours, key) => hours + data.topics[key].hours, 0),
    };
  }

  function find(data, query, stage) {
    const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    return [...values(data.modules), ...values(data.topics)].filter(item => {
      const module = item.module ? data.modules[item.module] : item;
      const parent = item.module ? module.title + " " + module.id : "";
      const text = [item.id, item.title, item.description, item.concepts, parent].join(" ").toLowerCase();
      return (stage === "" || Number(stage) === module.stage) && words.every(word => text.includes(word));
    }).sort((a, b) => Number(b.id === query.trim().toUpperCase()) - Number(a.id === query.trim().toUpperCase()));
  }

  function unlocked(data, selection, completed) {
    if (!selection) return [];
    const finished = new Set([...completed, ...selection.roots]);
    const roots = new Set(selection.roots);
    return values(data.topics).filter(topic => !finished.has(topic.id) &&
      topic.mandatory.some(parent => roots.has(parent.id) && !completed.has(parent.id)) &&
      topic.mandatory.every(parent => finished.has(parent.id))).map(topic => topic.id);
  }

  function edges(data, mode) {
    const result = new Map();
    for (const topic of values(data.topics)) {
      for (const kind of kinds) {
        for (const parent of topic[kind]) {
          const from = mode === "module" ? data.topics[parent.id].module : parent.id;
          const to = mode === "module" ? topic.module : topic.id;
          if (from !== to) result.set([from, to, kind].join("|"), {from, to, kind});
        }
      }
    }
    return [...result.values()];
  }

  function simplified(edges) {
    const mandatory = edges.filter(edge => edge.kind === "mandatory");
    const targets = new Map();
    for (const edge of mandatory) {
      if (!targets.has(edge.from)) targets.set(edge.from, []);
      targets.get(edge.from).push(edge);
    }
    function bypass(edge) {
      const visited = new Set([edge.from]);
      const queue = [edge.from];
      while (queue.length) {
        for (const next of targets.get(queue.shift()) || []) {
          if (next === edge || visited.has(next.to)) continue;
          if (next.to === edge.to) return true;
          visited.add(next.to);
          queue.push(next.to);
        }
      }
      return false;
    }
    return edges.filter(edge => edge.kind !== "mandatory" || !bypass(edge));
  }

  function lines(text, max) {
    const rows = [""];
    for (const word of text.split(/\s+/)) {
      const last = rows.length - 1;
      if (rows[last] && rows[last].length + word.length + 1 > max) rows.push(word);
      else rows[last] += (rows[last] ? " " : "") + word;
    }
    return rows;
  }

  function graph(data, options) {
    const {mode, selection, focus, optional, exportPath, title, exporting} = options;
    const topicMode = mode === "topic";
    const items = values(topicMode ? data.topics : data.modules);
    const asNode = key => topicMode ? key : data.topics[key].module;
    const chain = new Set((selection?.closure || []).map(asNode));
    const goals = new Set((selection?.roots || []).map(asNode));
    const next = new Set((options.unlocked || []).map(asNode));
    let links = edges(data, mode);
    if (!optional || exportPath) links = links.filter(edge => edge.kind === "mandatory");
    if (!topicMode && !selection) links = simplified(links);
    const optionalNeighbors = new Set();
    if (focus && optional) {
      for (const edge of links) {
        if (edge.kind !== "mandatory" && (goals.has(edge.from) || goals.has(edge.to))) {
          optionalNeighbors.add(edge.from);
          optionalNeighbors.add(edge.to);
        }
      }
    }
    const shown = items.filter(item => !selection || (!focus && !exportPath) || chain.has(item.id) ||
      (!exportPath && (next.has(item.id) || optionalNeighbors.has(item.id))));
    const groups = data.stages.map((_, index) => shown.filter(item => item.stage === index));
    const columns = groups.map((group, index) => [index, group]).filter(([, group]) => group.length);
    const width = Math.max(930, columns.length * STEP + 46);
    const header = 160;
    const positions = new Map();
    let lastY = header + 55;
    const stageLabels = [];
    const groupLabels = [];
    columns.forEach(([stage, group], col) => {
      const x = 26 + col * STEP;
      const palette = stageColors[stage];
      stageLabels.push(
        '<rect x="' + x + '" y="' + header + '" width="' + CARD + '" height="34" rx="9" fill="' + palette.fill + '"/>' +
        '<text x="' + (x + 13) + '" y="' + (header + 22) + '" fill="' + palette.ink +
        '" font-size="15" font-weight="700">' + xml(data.stages[stage]) + '</text>'
      );
      let y = header + 68;
      let previousModule;
      group.forEach(item => {
        if (topicMode && previousModule !== item.module) {
          groupLabels.push('<text x="' + (x + 3) + '" y="' + (y + 12) + '" fill="' + palette.ink +
            '" font-size="12" font-weight="700">' + xml(item.module) + '</text>');
          previousModule = item.module;
          y += 21;
        }
        const label = lines(item.title, 30);
        const height = Math.max(CARD_HEIGHT, 40 + label.length * 18);
        positions.set(item.id, {x, y, col, label, height});
        y += height + 17;
      });
      lastY = Math.max(lastY, y);
    });

    function line(edge, index) {
      const a = positions.get(edge.from);
      const b = positions.get(edge.to);
      const left = a.x + CARD;
      const optionShift = kinds.indexOf(edge.kind) * 4;
      const y1 = a.y + a.height / 2 + optionShift;
      const y2 = b.y + b.height / 2 + optionShift;
      const sameColumn = a.col === b.col;
      const reversed = a.col > b.col;
      const dest = sameColumn || reversed ? b.x + CARD + 2 : b.x - 3;
      let d;
      if (sameColumn) {
        const gutter = left + 10 + (index % 6) * 4;
        d = ["M", left, y1, "C", gutter, y1, gutter, y1, gutter, y1 + Math.sign(y2 - y1) * 7,
          "L", gutter, y2 - Math.sign(y2 - y1) * 7, "Q", gutter, y2, dest, y2].join(" ");
      } else if (!reversed && b.col === a.col + 1) {
        const midpoint = (left + dest) / 2 + optionShift;
        d = ["M", left, y1, "C", midpoint, y1, midpoint, y2, dest, y2].join(" ");
      } else {
        const exit = left + 9 + index % 5 * 4;
        const entry = reversed ? dest + 10 + index % 5 * 4 : dest - 7 - index % 5 * 4;
        const lane = header + 39 + index % 5 * 4;
        d = ["M", left, y1, "L", exit, y1, "L", exit, lane, "L", entry, lane, "L", entry, y2, "L", dest, y2].join(" ");
      }
      const style = linkStyles[edge.kind];
      const required = chain.has(edge.from) && chain.has(edge.to) && edge.kind === "mandatory";
      const relevant = !selection || required || (goals.has(edge.from) && next.has(edge.to)) ||
        (edge.kind !== "mandatory" && (goals.has(edge.from) || goals.has(edge.to)));
      return '<path d="' + d + '" fill="none" stroke="' + style.color + '" stroke-width="' + (required ? 2.6 : 1.6) +
        '" opacity="' + (relevant ? (exporting ? 0.93 : 0.81) : 0.18) + '" stroke-dasharray="' + style.dash +
        '" marker-end="url(#road-arrow-' + edge.kind + ')"/>';
    }

    links = links.filter(edge => positions.has(edge.from) && positions.has(edge.to));
    const connectors = links.map(line).join("");
    const cards = shown.map(item => {
      const {x, y, label, height} = positions.get(item.id);
      const palette = stageColors[item.stage];
      const current = goals.has(item.id);
      const prerequisite = chain.has(item.id) && !current;
      const unlock = next.has(item.id) && !chain.has(item.id);
      const dim = selection && !chain.has(item.id) && !next.has(item.id) && !optionalNeighbors.has(item.id);
      const treatment = current ? "Target" : prerequisite ? "Required" : unlock ? "Unlocked" : "";
      const border = current ? "#102c4a" : prerequisite ? "#2d6496" : unlock ? "#26805d" : palette.ink;
      const aria = item.id + " " + item.title + ", " + item.hours + " hours" + (treatment ? ", " + treatment : "");
      const labelLines = label.map((row, i) => '<tspan x="' + (x + 14) + '" y="' +
        (y + 45 + i * 18) + '">' + xml(row) + '</tspan>').join("");
      const card = '<g' + (dim ? ' opacity="0.68"' : "") + '><rect x="' + x + '" y="' + y +
        '" width="' + CARD + '" height="' + height + '" rx="10" fill="' + palette.fill + '" stroke="' + border +
        '" stroke-width="' + (treatment ? 2.4 : 1) + '"/><text x="' + (x + 14) + '" y="' + (y + 19) +
        '" font-size="12" font-weight="700" fill="' + palette.ink + '">' + item.id + " · " + item.hours +
        ' h</text><text x="' + (x + CARD - 13) + '" y="' + (y + 19) + '" text-anchor="end" font-size="12" fill="' +
        border + '" font-weight="700">' + treatment + '</text><text font-size="15" fill="#172e42" font-weight="700">' +
        labelLines + "</text></g>";
      if (exporting) return card;
      return '<a href="#' + item.id.toLowerCase() + '" role="button" tabindex="0" aria-label="' + xml(aria) +
        '" aria-pressed="' + String(current) + '" data-node="' + item.id + '"><title>' + xml(aria) + "</title>" + card + "</a>";
    }).join("");

    const markers = kinds.map(kind => '<marker id="road-arrow-' + kind +
      '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" fill="' + linkStyles[kind].color + '"/></marker>').join("");
    const paletteLegend = data.stages.map((stage, index) => {
      const x = 30 + 167 * index;
      return '<rect x="' + x + '" y="90" width="13" height="13" rx="3" fill="' + stageColors[index].fill +
        '" stroke="' + stageColors[index].ink + '"/><text x="' + (x + 20) + '" y="101" font-size="13" fill="#203648">' +
        xml(stage) + '</text>';
    }).join("");
    const arrowLegend = kinds.map((kind, index) => {
      const x = 30 + index * 209;
      const style = linkStyles[kind];
      return '<path d="M ' + x + ' 127 h 31" stroke="' + style.color + '" stroke-width="2" stroke-dasharray="' +
        style.dash + '" marker-end="url(#road-arrow-' + kind + ')"/><text x="' + (x + 40) +
        '" y="132" font-size="13" fill="#203648">' + style.label + '</text>';
    }).join("");
    const heading = lines(title || "LLM Evaluation Engineering · Module overview", 78);
    const firstHeading = heading[0];
    const subtitle = "Curriculum revision " + data.revision + " · " + (exportPath
      ? selection.closure.length + " topics · " + selection.total + " learner hours · Mandatory study only"
      : shown.length + (topicMode ? " topics" : " modules") + (topicMode ? " · Topic dependency links" : " · Overview of links between modules"));
    const height = lastY + 15;
    const headerText = '<text x="30" y="39" font-size="23" font-weight="700" fill="#142e45">' + xml(firstHeading) +
      '</text>' + (heading.length > 1 ? '<text x="30" y="62" font-size="18" font-weight="700" fill="#142e45">' +
      xml(heading.slice(1).join(" ")) + '</text>' : "") +
      '<text x="' + (heading.length > 1 ? 450 : 30) + '" y="' + (heading.length > 1 ? 78 : 67) +
      '" font-size="13" fill="#40596d">' + xml(subtitle) + "</text>";
    return {
      width, height, count: shown.length,
      svg: '<svg xmlns="http://www.w3.org/2000/svg" width="' + width + '" height="' + height +
        '" viewBox="0 0 ' + width + " " + height + '" role="' + (exporting ? "img" : "group") +
        '" aria-label="' + xml(title || "Learning dependency roadmap") +
        '" font-family="system-ui, sans-serif"><title>' + xml(title || "Learning dependency roadmap") +
        '</title><desc>Arrows point from prerequisite to dependent topic or module. ' + xml(subtitle) + '</desc><defs>' +
        markers + '</defs><rect width="100%" height="100%" fill="#f8fafc"/>' + headerText + paletteLegend +
        arrowLegend + stageLabels.join("") + groupLabels.join("") + connectors + cards + '</svg>',
    };
  }

  function rasterSize(width, height) {
    const scale = Math.min(2.5, 4096 / Math.max(width, height), Math.sqrt(14000000 / (width * height)));
    return [Math.round(width * scale), Math.round(height * scale)];
  }

  async function pngBlob(model, platform) {
    const url = platform.URL.createObjectURL(new platform.Blob([model.svg], {type: "image/svg+xml;charset=utf-8"}));
    try {
      const image = new platform.Image();
      await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = () => reject(new Error("The browser could not rasterize the SVG."));
        image.src = url;
      });
      const canvas = platform.document.createElement("canvas");
      [canvas.width, canvas.height] = rasterSize(model.width, model.height);
      const context = canvas.getContext("2d");
      if (!context) throw new Error("Canvas is unavailable.");
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      return await new Promise((resolve, reject) => canvas.toBlob(blob => {
        if (blob) resolve(blob);
        else reject(new Error("The browser could not encode the PNG."));
      }, "image/png"));
    } finally {
      platform.URL.revokeObjectURL(url);
    }
  }

  return {stageColors, linkStyles, xml, target, find, unlocked, edges, graph, rasterSize, pngBlob};
})();

if (typeof module === "object" && module.exports) module.exports = CurriculumRoadmap;



if (typeof document !== "undefined" && document.getElementById("roadmap-data")) {
  (() => {
    const road = CurriculumRoadmap;
    const data = JSON.parse(document.getElementById("roadmap-data").textContent);
    const el = id => document.getElementById("road-" + id);
    const viewport = el("viewport");
    const pathMenu = el("path");
    const modeMenu = el("mode");
    const search = el("search");
    const stageMenu = el("stage");
    const results = el("results");
    const focusToggle = el("focus");
    const optionalToggle = el("optional");
    const exportMenu = el("export");
    const status = el("download-status");
    let selection = null;
    let visibleGraph;
    let camera = {x: 0, y: 0, scale: 1};
    let drag = null;
    let initialized = false;

    const escape = road.xml;
    const makeButton = (item, name = item.title) => '<button type="button" class="road-item" data-select="' +
      item.id + '"><strong>' + item.id + '</strong><span>' + escape(name) + "</span></button>";

    function completedTopics() {
      return new Set(Object.keys(data.topics).filter(id =>
        document.getElementById("progress-" + id.toLowerCase()).value === "Completed"));
    }

    function titleFor(item) {
      return item.kind === "path" ? "Path " + item.id + " — " + item.title : item.id + " — " + item.title;
    }

    function topicList(ids, notes = {}) {
      if (!ids.length) return '<p class="road-empty">None.</p>';
      return '<ul class="road-list">' + ids.map(id => "<li>" + makeButton(data.topics[id]) +
        (notes[id] ? '<p class="road-condition">' + escape(notes[id]) + "</p>" : "") + "</li>").join("") + "</ul>";
    }

    function selectedTopicDetail(topic) {
      return Object.entries(road.linkStyles).map(([kind, style]) => {
        const parents = topic[kind];
        const heading = kind === "conditional" ? "Conditional prerequisites" : style.label + " prerequisites";
        return "<h4>" + heading + "</h4>" +
          topicList(parents.map(parent => parent.id), Object.fromEntries(parents.map(parent => [parent.id, parent.note])));
      }).join("") + "<h4>Implementation readiness</h4><p>" + escape(topic.readiness) + "</p>";
    }

    function renderInspector(completed, next) {
      el("clear").hidden = !selection;
      el("jump").hidden = !selection;
      focusToggle.disabled = !selection;
      exportMenu.options[1].disabled = !selection;
      if (!selection && exportMenu.value === "selection") exportMenu.value = "module";
      el("title").textContent = selection ? titleFor(selection) : "Choose a target";

      if (!selection) {
        el("estimate").textContent = "";
        el("details").innerHTML = "<p>Start with M01 for the complete core, or pick a path or topic. " +
          "The module view groups topic links for orientation. Select a target to see its exact required route.</p>" +
          "<p>Links point from prerequisite to dependent. Full estimates exclude preparation and optional extensions.</p>";
        return;
      }

      const pending = selection.closure.filter(id => !completed.has(id));
      const pendingHours = pending.reduce((total, id) => total + data.topics[id].hours, 0);
      el("estimate").textContent = selection.closure.length + " topics · " + selection.total +
        " learner hours · " + pendingHours + " h still unmarked";
      const goal = selection.outcome ? "<h4>What you’ll demonstrate</h4><p>" + escape(selection.outcome) + "</p>" : "";
      const requirements = selection.kind === "module"
        ? "<h4>Topics in this module</h4>" + topicList(selection.topics)
        : selection.kind === "topic" ? selectedTopicDetail(selection) : "";
      const required = '<details class="road-route" open><summary>Required route in study order</summary><ol>' +
        selection.closure.map(id => "<li>" + makeButton(data.topics[id]) + '<span class="road-route-hours">' +
          data.topics[id].hours + " h" + (completed.has(id) ? " · completed" : "") + "</span></li>").join("") + "</ol></details>";
      const unlocks = "<h4>Newly unlocked with current progress</h4>" +
        (next.length ? topicList(next) : '<p class="road-empty">None. A dependent topic may still have other mandatory prerequisites.</p>');
      const detailLink = selection.kind === "path" ? "" : '<p><a href="#' + selection.id.toLowerCase() +
        '">Open in Detailed Curriculum</a></p>';
      el("details").innerHTML = goal + requirements + required + unlocks + detailLink;
    }

    function applyCamera() {
      viewport.firstElementChild.style.transform = "translate(" + camera.x + "px," + camera.y + "px) scale(" + camera.scale + ")";
      el("zoom").textContent = Math.round(camera.scale * 100) + "%";
    }

    function resetCamera() {
      camera = {x: 0, y: 0, scale: Math.max(0.57, Math.min(1, viewport.clientWidth / visibleGraph.width))};
      applyCamera();
    }

    function zoom(factor, x = viewport.clientWidth / 2, y = viewport.clientHeight / 2) {
      const scale = Math.max(0.2, Math.min(2.6, camera.scale * factor));
      const ratio = scale / camera.scale;
      camera = {x: x - (x - camera.x) * ratio, y: y - (y - camera.y) * ratio, scale};
      applyCamera();
    }

    function pan(x, y) {
      camera.x += x;
      camera.y += y;
      applyCamera();
    }

    function reveal(id) {
      if (!id) return;
      const key = modeMenu.value === "module" ? data.topics[id]?.module || id : (data.modules[id]?.topics[0] || id);
      const node = viewport.querySelector('[data-node="' + key + '"]');
      if (!node) return;
      const outer = viewport.getBoundingClientRect();
      const card = node.getBoundingClientRect();
      if (card.left < outer.left || card.right > outer.right || card.top < outer.top || card.bottom > outer.bottom) {
        pan(outer.left + (outer.width - card.width) / 2 - card.left, outer.top + (outer.height - card.height) / 2 - card.top);
      }
    }

    function draw(reset = false) {
      const completed = completedTopics();
      const next = road.unlocked(data, selection, completed);
      visibleGraph = road.graph(data, {
        mode: modeMenu.value, selection, focus: focusToggle.checked, optional: optionalToggle.checked, unlocked: next,
        title: modeMenu.value === "module" ? "LLM Evaluation Engineering · Module overview" : "LLM Evaluation Engineering · Topic roadmap",
      });
      viewport.innerHTML = visibleGraph.svg;
      renderInspector(completed, next);
      if (reset) resetCamera();
      else applyCamera();
    }

    function choose(id, origin) {
      selection = road.target(data, id);
      if (!selection) return;
      pathMenu.value = selection.kind === "path" ? id : "";
      if (selection.kind === "topic") {
        modeMenu.value = "topic";
        // Topic details start with the required chain and related optional links in view.
        focusToggle.checked = true;
        optionalToggle.checked = true;
      }
      if (selection.kind === "module") modeMenu.value = "module";
      if (selection.kind === "path") focusToggle.checked = true;
      draw(focusToggle.checked || origin !== "graph");
      if (selection.kind !== "path") reveal(id);
      if (origin === "graph") {
        viewport.querySelector('[data-node="' + id + '"]')?.focus({preventScroll: true});
      } else if (origin === "results" || origin === "inspector") {
        el("title").tabIndex = -1;
        el("title").focus({preventScroll: true});
      }
      exportMenu.value = "selection";
    }

    function clearSelection() {
      selection = null;
      pathMenu.value = "";
      focusToggle.checked = false;
      optionalToggle.checked = false;
      draw(true);
    }

    function showResults() {
      const query = search.value;
      results.hidden = !query.trim() && stageMenu.value === "";
      if (results.hidden) return;
      const matches = road.find(data, query, stageMenu.value);
      results.innerHTML = "<p>" + matches.length + " " + (matches.length === 1 ? "match" : "matches") +
        (matches.length > 12 ? " · refine to see more" : "") + "</p>" + matches.slice(0, 12)
        .map(item => makeButton(item)).join("");
    }

    search.addEventListener("input", showResults);
    stageMenu.addEventListener("change", showResults);
    search.addEventListener("keydown", event => {
      if (event.key === "Enter" && !results.hidden) {
        event.preventDefault();
        results.querySelector("[data-select]")?.click();
      }
      if (event.key === "Escape") results.hidden = true;
      if (event.key === "ArrowDown" && !results.hidden) {
        event.preventDefault();
        results.querySelector("[data-select]")?.focus();
      }
    });
    results.addEventListener("click", event => {
      const item = event.target.closest("[data-select]");
      if (!item) return;
      search.value = item.dataset.select;
      results.hidden = true;
      choose(item.dataset.select, "results");
    });
    el("details").addEventListener("click", event => {
      const item = event.target.closest("[data-select]");
      if (item) choose(item.dataset.select, "inspector");
    });
    pathMenu.addEventListener("change", () => pathMenu.value ? choose(pathMenu.value, "path") : clearSelection());
    modeMenu.addEventListener("change", () => draw(true));
    focusToggle.addEventListener("change", () => draw(true));
    optionalToggle.addEventListener("change", () => draw(true));
    el("clear").addEventListener("click", () => {clearSelection(); search.focus();});
    el("zoom-in").addEventListener("click", () => zoom(1.2));
    el("zoom-out").addEventListener("click", () => zoom(1 / 1.2));
    el("reset").addEventListener("click", resetCamera);

    viewport.addEventListener("click", event => {
      const item = event.target.closest("[data-node]");
      if (item) {
        event.preventDefault();
        choose(item.dataset.node, "graph");
      }
    });
    viewport.addEventListener("keydown", event => {
      const node = event.target.closest("[data-node]");
      if (node && event.key === " ") {
        event.preventDefault();
        choose(node.dataset.node, "graph");
        return;
      }
      if (event.target !== viewport) return;
      const directions = {ArrowLeft: [55, 0], ArrowRight: [-55, 0], ArrowUp: [0, 55], ArrowDown: [0, -55]};
      if (Object.hasOwn(directions, event.key)) pan(...directions[event.key]);
      else if (event.key === "+" || event.key === "=") zoom(1.2);
      else if (event.key === "-") zoom(1 / 1.2);
      else return;
      event.preventDefault();
    });
    viewport.addEventListener("focusin", event => {
      const node = event.target.closest("[data-node]");
      if (node) reveal(node.dataset.node);
    });
    viewport.addEventListener("pointerdown", event => {
      if (event.button !== 0 || event.target.closest("[data-node]") || drag) return;
      drag = {id: event.pointerId, x: event.clientX, y: event.clientY};
      viewport.setPointerCapture(event.pointerId);
      viewport.classList.add("panning");
    });
    viewport.addEventListener("pointermove", event => {
      if (drag?.id !== event.pointerId) return;
      pan(event.clientX - drag.x, event.clientY - drag.y);
      drag.x = event.clientX;
      drag.y = event.clientY;
    });
    for (const type of ["pointerup", "pointercancel", "lostpointercapture"]) {
      viewport.addEventListener(type, event => {
        if (drag?.id !== event.pointerId) return;
        drag = null;
        viewport.classList.remove("panning");
      });
    }
    viewport.addEventListener("wheel", event => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      const rect = viewport.getBoundingClientRect();
      zoom(event.deltaY < 0 ? 1.1 : 1 / 1.1, event.clientX - rect.left, event.clientY - rect.top);
    }, {passive: false});

    function save(blob, filename) {
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function exportModel() {
      const mode = exportMenu.value;
      const picked = mode === "selection" ? selection : null;
      const title = picked ? titleFor(picked) :
        "LLM Evaluation Engineering · " + (mode === "topic" ? "Complete topic roadmap" : "Complete module roadmap");
      return road.graph(data, {
        mode: picked ? "topic" : mode, selection: picked, exporting: true, exportPath: Boolean(picked),
        optional: optionalToggle.checked, title,
      });
    }

    function filename(extension) {
      const mode = exportMenu.value;
      const scope = mode === "selection" ? selection.id.toLowerCase() : mode;
      return "llm-evaluation-roadmap-v" + data.revision + "-" + scope + "." + extension;
    }

    el("svg").addEventListener("click", () => {
      const model = exportModel();
      save(new Blob([model.svg], {type: "image/svg+xml;charset=utf-8"}), filename("svg"));
      status.textContent = "SVG download requested.";
    });
    el("png").addEventListener("click", async () => {
      el("png").disabled = true;
      status.textContent = "Preparing PNG…";
      const name = filename("png");
      try {
        const png = await road.pngBlob(exportModel(), window);
        save(png, name);
        status.textContent = "PNG download requested.";
      } catch (error) {
        status.textContent = error.message + " Try SVG for a scalable copy.";
      } finally {
        el("png").disabled = false;
      }
    });
    el("html").addEventListener("click", () => {
      const offline = portableCurriculum.replace("<html lang=\"en\">", '<html lang="en" data-initial-tab="roadmap">');
      save(new Blob([offline], {type: "text/html;charset=utf-8"}), "llm-evaluation-curriculum-v" + data.revision + ".html");
      status.textContent = "Standalone HTML download requested.";
    });

    el("legend").innerHTML = data.stages.map((stage, i) => '<li><span class="road-stage-key" style="--key:' +
      road.stageColors[i].fill + ";--key-ink:" + road.stageColors[i].ink + '"></span>' + escape(stage) + "</li>")
      .concat(Object.entries(road.linkStyles).map(([kind, style]) =>
        '<li><span class="road-edge-key road-edge-' + kind + '"></span>' + style.label + "</li>")).join("");

    function enterRoadmap() {
      if (initialized) return;
      initialized = true;
      document.getElementById("roadmap-app").hidden = false;
      draw(true);
    }
    document.addEventListener("curriculum-tab", event => {
      if (event.detail === "#roadmap") enterRoadmap();
    });
    document.addEventListener("curriculum-progress", () => {if (initialized && selection) draw();});
    if (!document.getElementById("roadmap").hidden) enterRoadmap();
  })();
}

