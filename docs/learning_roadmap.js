"use strict";

const roadmapDuration = typeof LearningProgress === "undefined"
  ? require("./learning_progress.js").duration : LearningProgress.duration;

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
  const downstreamColor = "#12634e";
  const kinds = Object.keys(linkStyles);
  const values = Object.values;
  const CARD = 258;
  const STEP = 310;
  const CARD_HEIGHT = 82;
  const STAGE_HEIGHT = 34;
  const ROW_GAP = 17;

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
          if (from !== to) {
            const edge = {from, to, kind};
            result.set(edgeKey(edge), edge);
          }
        }
      }
    }
    return [...result.values()];
  }

  function available(data, completed) {
    return values(data.topics).filter(topic => !completed.has(topic.id) &&
      topic.mandatory.every(parent => completed.has(parent.id))).map(topic => topic.id);
  }

  function edgeKey({from, to, kind}) {
    return [from, to, kind].join("|");
  }

  function moduleDependencies(data, id) {
    const selected = data.modules[id];
    const roots = new Set(selected.topics);
    const upstreamTopics = new Set(selected.closure);
    const downstreamTopics = new Set(values(data.topics).filter(topic =>
      topic.closure.some(parent => roots.has(parent))).map(topic => topic.id));
    const projected = topicIds => new Set(edges(data, "topic").filter(edge => edge.kind === "mandatory" &&
      topicIds.has(edge.from) && topicIds.has(edge.to)).map(edge => edgeKey({
      from: data.topics[edge.from].module, to: data.topics[edge.to].module, kind: edge.kind,
    })));
    const direct = {upstream: [], downstream: []};
    for (const edge of edges(data, "module")) {
      if (edge.to === id) direct.upstream.push(edge);
      if (edge.from === id) direct.downstream.push(edge);
    }
    function indirect(topicIds, directEdges, endpoint) {
      const seen = new Set([id, ...directEdges.filter(edge => edge.kind === "mandatory").map(edge => edge[endpoint])]);
      return [...new Set([...topicIds].map(topic => data.topics[topic].module))]
        .filter(module => !seen.has(module)).sort();
    }
    return {
      direct,
      indirect: {upstream: indirect(upstreamTopics, direct.upstream, "from"),
                 downstream: indirect(downstreamTopics, direct.downstream, "to")},
      paths: {upstream: projected(upstreamTopics), downstream: projected(downstreamTopics)},
    };
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

  function spacing(columns, rows, contentHeight, size) {
    const inset = 34;
    const gap = STEP - CARD;
    const stageSpace = 68;
    const baseWidth = 2 * inset + columns * CARD + (columns - 1) * gap;
    const baseHeight = inset + stageSpace + contentHeight;
    const unit = size ? Math.max(.5, Math.min(size.width / baseWidth, size.height / baseHeight)) : 1;
    const extraWidth = size ? Math.max(0, size.width - baseWidth * unit) : 0;
    // Put spare width into both cards and connector gutters when height limits the fit.
    const card = CARD * unit + extraWidth * .65 / columns;
    const columnGap = gap * unit + extraWidth * .35 / Math.max(1, columns - 1);
    const extraHeight = size ? Math.max(0, size.height - baseHeight * unit) : 0;
    return {
      unit, card, columnGap, inset: inset * unit, stageSpace: stageSpace * unit,
      rowGap: ROW_GAP * unit + extraHeight / Math.max(1, rows - 1),
    };
  }

  function graph(data, options) {
    const {mode, selection, focus, optional, exportPath, title, exporting} = options;
    const markerPrefix = options.markerPrefix || "road-arrow-";
    const topicMode = mode === "topic";
    const selectedModule = !topicMode && selection?.kind === "module" ? selection.id : null;
    const moduleFocus = Boolean(selectedModule && focus && !exportPath);
    const dependencies = moduleFocus ? moduleDependencies(data, selectedModule) : null;
    const items = values(topicMode ? data.topics : data.modules);
    const asNode = key => topicMode ? key : data.topics[key].module;
    const chain = new Set((selection?.closure || []).map(asNode));
    const goals = new Set((selection?.roots || []).map(asNode));
    const next = new Set((options.unlocked || []).map(asNode));
    let links = edges(data, mode).filter(edge => edge.kind === "mandatory" || (!exportPath &&
      (optional || (moduleFocus && (edge.from === selectedModule || edge.to === selectedModule)))));
    const related = new Map();
    if (moduleFocus) {
      const mark = (ids, label, color) => {
        for (const id of ids) if (!related.has(id)) related.set(id, {label, color});
      };
      const {direct, indirect} = dependencies;
      for (const [direction, endpoint, label, color] of [
        ["upstream", "from", "Prerequisite", linkStyles.mandatory.color],
        ["downstream", "to", "Dependent", downstreamColor],
      ]) {
        mark(direct[direction].filter(edge => edge.kind === "mandatory").map(edge => edge[endpoint]), label, color);
        mark(indirect[direction], "Indirect " + label.toLowerCase(), color);
      }
      for (const kind of ["conditional", "recommended"]) {
        const label = kind === "conditional" ? "Conditional link" : "Optional link";
        mark(direct.upstream.filter(edge => edge.kind === kind).map(edge => edge.from), label, linkStyles[kind].color);
        mark(direct.downstream.filter(edge => edge.kind === kind).map(edge => edge.to), label, linkStyles[kind].color);
      }
    }
    const optionalNeighbors = new Set(optional && !exportPath ? (selection?.recommended || []).map(asNode) : []);
    if (focus && optional && !selection?.recommended) {
      for (const edge of links) {
        if (edge.kind !== "mandatory" && (goals.has(edge.from) || goals.has(edge.to))) {
          optionalNeighbors.add(edge.from);
          optionalNeighbors.add(edge.to);
        }
      }
    }
    const shown = items.filter(item => (!topicMode && !exportPath) || !selection || (!focus && !exportPath) || chain.has(item.id) ||
      (!exportPath && (next.has(item.id) || optionalNeighbors.has(item.id))));
    const groups = data.stages.map((_, index) => shown.filter(item => item.stage === index));
    const columns = groups.map((group, index) => [index, group]).filter(([, group]) => group.length);
    const labels = new Map(shown.map(item => {
      const label = lines(item.title, 30);
      return [item.id, {label, height: Math.max(CARD_HEIGHT, 40 + label.length * 18)}];
    }));
    const rows = Math.max(1, ...columns.map(([, group]) => group.length));
    // Compute the vertical budget from each complete column's wrapped card heights.
    const contentHeight = Math.max(0, ...columns.map(([, group]) => group.reduce((sum, item) =>
      sum + labels.get(item.id).height, 0) + (group.length - 1) * ROW_GAP));
    const geometry = spacing(Math.max(1, columns.length), rows, contentHeight,
      !topicMode && !exporting ? options.size : null);
    const {unit, card: cardWidth, columnGap, stageSpace, rowGap, inset} = geometry;
    const step = cardWidth + columnGap;
    const width = Math.ceil(Math.max(exporting ? 930 : 0, inset * 2 + columns.length * step - columnGap));
    // Branding and the legend are HTML in the live view. Exported images carry their own header.
    const header = exporting ? 188 : 12 * unit;
    const positions = new Map();
    let lastY = header + stageSpace;
    const stageLabels = [];
    const groupLabels = [];
    columns.forEach(([stage, group], col) => {
      const x = inset + col * step;
      const palette = stageColors[stage];
      stageLabels.push(
        '<rect x="' + x + '" y="' + header + '" width="' + cardWidth + '" height="' + STAGE_HEIGHT * unit +
        '" rx="' + 9 * unit + '" fill="' + palette.fill + '"/>' +
        '<text x="' + (x + 13 * unit) + '" y="' + (header + 22 * unit) + '" fill="' + palette.ink +
        '" font-size="' + 15 * unit + '" font-weight="700">' + xml(data.stages[stage]) + '</text>'
      );
      let y = header + stageSpace;
      let previousModule;
      group.forEach(item => {
        if (topicMode && previousModule !== item.module) {
          groupLabels.push('<text x="' + (x + 3) + '" y="' + (y + 12) + '" fill="' + palette.ink +
            '" font-size="12" font-weight="700">' + xml(item.module) + '</text>');
          previousModule = item.module;
          y += 21;
        }
        const label = labels.get(item.id).label;
        const height = labels.get(item.id).height * unit;
        positions.set(item.id, {x, y, col, label, height});
        y += height + rowGap;
      });
      lastY = Math.max(lastY, y - rowGap);
    });

    links = links.filter(edge => positions.has(edge.from) && positions.has(edge.to));
    // Spread ports along each card face while keeping the original card positions.
    const offsets = new Map(links.map(edge => [edge, {}]));
    if (!topicMode) {
      const ports = new Map();
      const add = (id, side, edge, end, other) => {
        const key = id + side;
        if (!ports.has(key)) ports.set(key, []);
        ports.get(key).push({edge, end, other});
      };
      for (const edge of links) {
        add(edge.from, "right", edge, "start", edge.to);
        add(edge.to, positions.get(edge.from).col >= positions.get(edge.to).col ? "right" : "left",
          edge, "end", edge.from);
      }
      for (const group of ports.values()) {
        group.sort((a, b) => positions.get(a.other).y - positions.get(b.other).y ||
          kinds.indexOf(a.edge.kind) - kinds.indexOf(b.edge.kind));
        const step = Math.min(8, 50 / group.length) * unit;
        group.forEach(({edge, end}, i) => { offsets.get(edge)[end] = (i - (group.length - 1) / 2) * step; });
      }
    }

    function line(edge, index) {
      const a = positions.get(edge.from);
      const b = positions.get(edge.to);
      const left = a.x + cardWidth;
      const optionShift = kinds.indexOf(edge.kind) * 4;
      const {start = optionShift, end = optionShift} = offsets.get(edge);
      const y1 = a.y + a.height / 2 + start;
      const y2 = b.y + b.height / 2 + end;
      const sameColumn = a.col === b.col;
      const reversed = a.col > b.col;
      const dest = sameColumn || reversed ? b.x + cardWidth + 3 * unit : b.x - 3 * unit;
      const gutterStep = columnGap / 13;
      let d;
      if (sameColumn) {
        const gutter = left + Math.min(inset - 3 * unit, (2 + index % 6) * gutterStep);
        const bend = Math.sign(y2 - y1) * 7 * unit;
        d = ["M", left, y1, "C", gutter, y1, gutter, y1, gutter, y1 + bend,
          "L", gutter, y2 - bend, "Q", gutter, y2, dest, y2].join(" ");
      } else if (!reversed && b.col === a.col + 1) {
        const midpoint = (left + dest) / 2 + optionShift;
        d = ["M", left, y1, "C", midpoint, y1, midpoint, y2, dest, y2].join(" ");
      } else {
        const jog = Math.min(inset - 5 * unit, (2 + index % 5) * gutterStep);
        const exit = left + jog;
        const entry = reversed ? dest + jog : dest - jog;
        const lane = header + (topicMode ? 39 + index % 5 * 4 : 37 + index % 11 * 2.5) * unit;
        d = ["M", left, y1, "L", exit, y1, "L", exit, lane, "L", entry, lane, "L", entry, y2, "L", dest, y2].join(" ");
      }
      const style = linkStyles[edge.kind];
      const attributes = ' data-from="' + edge.from + '" data-to="' + edge.to + '" data-kind="' + edge.kind + '"';
      if (selectedModule) {
        let relation = "context";
        const direct = edge.from === selectedModule || edge.to === selectedModule;
        if (moduleFocus && edge.kind === "mandatory") {
          const key = edgeKey(edge);
          if (edge.from === selectedModule || (edge.to !== selectedModule && dependencies.paths.downstream.has(key))) {
            relation = "downstream";
          } else if (edge.to === selectedModule || dependencies.paths.upstream.has(key)) {
            relation = "upstream";
          }
        } else if (moduleFocus && direct) {
          relation = "optional";
        }
        const emphasis = relation === "context" ? 0 : direct ? 2 : 1;
        const marker = relation === "downstream" ? "downstream" : edge.kind;
        const color = relation === "downstream" ? downstreamColor : style.color;
        const opacity = emphasis ? 1 : moduleFocus ? .2 : .81;
        return {emphasis, markup: '<path' + attributes + ' data-relation="' + relation + '" d="' + d + '" fill="none" stroke="' +
          color + '" stroke-width="' + (emphasis === 2 ? 3.1 : emphasis ? 2.2 : 1.6) * unit +
          '" opacity="' + opacity + '" stroke-dasharray="' + style.dash +
          '" marker-end="url(#' + markerPrefix + marker + ')"/>'};
      }
      const required = chain.has(edge.from) && chain.has(edge.to) && edge.kind === "mandatory";
      const relevant = !selection || required || (goals.has(edge.from) && next.has(edge.to)) ||
        (edge.kind !== "mandatory" && (goals.has(edge.from) || goals.has(edge.to) ||
          (optionalNeighbors.has(edge.from) && chain.has(edge.to))));
      return {emphasis: 0, markup: '<path' + attributes + ' d="' + d + '" fill="none" stroke="' + style.color + '" stroke-width="' + (required ? 2.6 : 1.6) * unit +
        '" opacity="' + (relevant ? (exporting ? 0.93 : 0.81) : 0.18) + '" stroke-dasharray="' + style.dash +
        '" marker-end="url(#' + markerPrefix + edge.kind + ')"/>'};
    }

    const connectors = links.map(line).sort((a, b) => a.emphasis - b.emphasis).map(edge => edge.markup).join("");
    const cards = shown.map(item => {
      const {x, y, label, height} = positions.get(item.id);
      const palette = stageColors[item.stage];
      const current = goals.has(item.id);
      const prerequisite = chain.has(item.id) && !current;
      const unlock = next.has(item.id) && !chain.has(item.id);
      const recommended = optionalNeighbors.has(item.id) && !chain.has(item.id);
      const relative = related.get(item.id);
      const dim = selectedModule ? moduleFocus && !current && !relative :
        selection && !chain.has(item.id) && !next.has(item.id) && !optionalNeighbors.has(item.id);
      const treatment = selectedModule ? (current ? "Selected" : relative?.label || "") :
        current ? "Target" : prerequisite ? "Required" : recommended ? "Optional" : unlock ? "Unlocked" : "";
      const border = current ? "#102c4a" : selectedModule ? relative?.color || palette.ink :
        prerequisite ? "#2d6496" : recommended ? "#66448c" : unlock ? "#26805d" : palette.ink;
      const aria = item.id + " " + item.title + ", " + roadmapDuration(item.hours) + (treatment ? ", " + treatment : "");
      const labelLines = label.map((row, i) => '<tspan x="' + (x + 14 * unit) + '" y="' +
        (y + (45 + i * 18) * unit) + '">' + xml(row) + '</tspan>').join("");
      const card = '<g><rect x="' + x + '" y="' + y +
        '" width="' + cardWidth + '" height="' + height + '" rx="' + 10 * unit + '" fill="' + (dim ? "#f1f4f7" : palette.fill) +
        '" stroke="' + (dim ? "#8996a3" : border) + '" stroke-width="' + (current ? 3.5 : treatment ? 2.4 : 1) * unit +
        ((selectedModule ? relative?.label === "Optional link" : recommended) ? '" stroke-dasharray="6 4' : '') +
        (relative?.label === "Conditional link" ? '" stroke-dasharray="2 5' : '') +
        '"/><text x="' + (x + 14 * unit) + '" y="' + (y + 19 * unit) +
        '" font-size="' + 12 * unit + '" font-weight="700" fill="' + palette.ink + '">' + item.id + " · " + roadmapDuration(item.hours) +
        '</text><text x="' + (x + cardWidth - 13 * unit) + '" y="' + (y + 19 * unit) +
        '" text-anchor="end" font-size="' + 12 * unit + '" fill="' +
        border + '" font-weight="700">' + treatment + '</text><text font-size="' + 15 * unit + '" fill="#172e42" font-weight="700">' +
        labelLines + "</text></g>";
      if (exporting) return card;
      return '<a href="#' + item.id.toLowerCase() + '" role="button" tabindex="0" aria-label="' + xml(aria) +
        '" aria-pressed="' + String(current) + '" data-node="' + item.id + '"><title>' + xml(aria) + "</title>" + card + "</a>";
    }).join("");

    const markers = [...kinds, "downstream"].map(kind => '<marker id="' + markerPrefix + kind +
      '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" fill="' + (kind === "downstream" ? downstreamColor : linkStyles[kind].color) + '"/></marker>').join("");
    const paletteLegend = data.stages.map((stage, index) => {
      const x = 30 + 167 * index;
      return '<rect x="' + x + '" y="119" width="13" height="13" rx="3" fill="' + stageColors[index].fill +
        '" stroke="' + stageColors[index].ink + '"/><text x="' + (x + 20) + '" y="130" font-size="13" fill="#203648">' +
        xml(stage) + '</text>';
    }).join("");
    const arrowLegend = kinds.map((kind, index) => {
      const x = 30 + index * 209;
      const style = linkStyles[kind];
      return '<path d="M ' + x + ' 156 h 31" stroke="' + style.color + '" stroke-width="2" stroke-dasharray="' +
        style.dash + '" marker-end="url(#' + markerPrefix + kind + ')"/><text x="' + (x + 40) +
        '" y="161" font-size="13" fill="#203648">' + style.label + '</text>';
    }).join("");
    const heading = lines(title || "LLM Evaluation Engineering · Module overview", 78);
    const firstHeading = heading[0];
    const subtitle = "Curriculum revision " + data.revision + " · " + (exportPath
      ? selection.closure.length + " topics · " + roadmapDuration(selection.total) + " learner time · Mandatory study only"
      : shown.length + (topicMode ? " topics" : " modules") + (topicMode ? " · Topic dependency links" : " · Overview of links between modules"));
    const height = Math.ceil(lastY + (exporting ? 28 : inset - header));
    const logo = data.brandIcon ? '<image href="' + xml(data.brandIcon) + '" x="30" y="12" width="35" height="35"/>' : "";
    const brand = logo + '<text x="' + (logo ? 75 : 30) +
      '" y="35" font-size="15" font-weight="700" fill="#2451a6">TestNeural LLM Academy</text>' +
      '<text x="' + (width - 30) + '" y="35" text-anchor="end" font-size="13" fill="#40596d">Developed by: Amit Baderia</text>';
    const headerText = brand + '<text x="30" y="67" font-size="23" font-weight="700" fill="#142e45">' + xml(firstHeading) +
      '</text>' + (heading.length > 1 ? '<text x="30" y="89" font-size="18" font-weight="700" fill="#142e45">' +
      xml(heading.slice(1).join(" ")) + '</text>' : "") +
      '<text x="30" y="104' +
      '" font-size="13" fill="#40596d">' + xml(subtitle) + "</text>";
    const directCards = moduleFocus ? [selectedModule, ...dependencies.direct.upstream.filter(edge =>
      edge.kind === "mandatory").map(edge => edge.from), ...dependencies.direct.downstream.filter(edge =>
      edge.kind === "mandatory").map(edge => edge.to)].map(id => positions.get(id)) : [];
    const bounds = directCards.length ? {
      left: Math.min(...directCards.map(card => card.x)),
      top: Math.min(...directCards.map(card => card.y)),
      right: Math.max(...directCards.map(card => card.x + cardWidth)),
      bottom: Math.max(...directCards.map(card => card.y + card.height)),
    } : null;
    return {
      width, height, bounds, count: shown.length,
      svg: '<svg xmlns="http://www.w3.org/2000/svg" width="' + width + '" height="' + height +
        '" viewBox="0 0 ' + width + " " + height + '" role="' + (exporting ? "img" : "group") +
        '" aria-label="' + xml(title || "Learning dependency roadmap") +
        '" font-family="system-ui, sans-serif"><title>' + xml(title || "Learning dependency roadmap") +
        '</title><desc>Arrows point from prerequisite to dependent topic or module. ' + xml(subtitle) + '</desc><defs>' +
        markers + '</defs><rect width="100%" height="100%" fill="#f8fafc"/>' +
        (exporting ? headerText + paletteLegend + arrowLegend : "") +
        stageLabels.join("") + groupLabels.join("") + connectors + cards + '</svg>',
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

  function saveBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function standaloneHTML(source, view) {
    return source.replace(/<html\b[^>]*>/i, '<html lang="en" data-initial-tab="' + xml(view) + '">');
  }

  function bindFullscreen(surface, header, opener, closer, page, browser, layoutChanged) {
    let session = null;

    function restore() {
      const previous = session;
      if (!previous) return;
      session = null;
      page.removeEventListener("fullscreenchange", fullscreenChanged);
      page.removeEventListener("keydown", fullscreenKeys, {capture: true});
      for (const sibling of previous.outside) sibling.inert = false;
      surface.classList.remove("is-fullscreen", "is-fullscreen-fallback");
      surface.removeAttribute("role");
      surface.removeAttribute("aria-modal");
      surface.removeAttribute("aria-labelledby");
      page.documentElement.classList.remove("roadmap-fullscreen");
      header.hidden = true;
      if (previous.mode !== "pending") layoutChanged(false);
      if (previous.restoreView) {
        opener.focus({preventScroll: true});
        browser.scrollTo({left: previous.x, top: previous.y, behavior: "instant"});
      }
    }

    function show(mode) {
      if (session.mode !== "pending") return;
      session.mode = mode;
      surface.classList.add("is-fullscreen");
      if (mode === "fallback") {
        surface.classList.add("is-fullscreen-fallback");
        for (let node = surface; node !== page.body; node = node.parentElement) {
          for (const sibling of node.parentElement.children) {
            if (sibling !== node && !sibling.inert) {
              sibling.inert = true;
              session.outside.push(sibling);
            }
          }
        }
      }
      surface.setAttribute("role", "dialog");
      surface.setAttribute("aria-modal", "true");
      surface.setAttribute("aria-labelledby", "road-fullscreen-title");
      page.documentElement.classList.add("roadmap-fullscreen");
      header.hidden = false;
      page.addEventListener("keydown", fullscreenKeys, {capture: true});
      layoutChanged(true);
      closer.focus({preventScroll: true});
    }

    function fullscreenChanged() {
      if (!session) return;
      if (page.fullscreenElement === surface) {
        if (session.restoreView) show("native");
        else {
          session.mode = "native";
          close(false);
        }
      } else if (session.mode === "native") restore();
    }

    async function close(restoreView = true) {
      if (!session) return;
      if (!restoreView) session.restoreView = false;
      if (session.mode === "pending" || session.closing) return;
      if (page.fullscreenElement === surface) {
        const current = session;
        current.closing = true;
        try {
          await page.exitFullscreen();
        } catch {
          // Leave the Close button and the browser's native exit available.
        }
        if (session !== current) return;
        current.closing = false;
        if (page.fullscreenElement === surface) return;
      }
      restore();
    }

    function fullscreenKeys(event) {
      if (event.key === "Escape" && session.mode === "fallback") {
        event.preventDefault();
        event.stopPropagation();
        close();
        return;
      }
      if (event.key !== "Tab" || event.altKey || event.ctrlKey || event.metaKey) return;
      const stops = Array.from(surface.querySelectorAll("a[href], button, input, select, summary, [tabindex]"))
        .filter(item => item.tabIndex >= 0 && !item.matches(":disabled") && item.getClientRects().length);
      const current = page.activeElement;
      const edge = event.shiftKey ? stops[0] : stops[stops.length - 1];
      if (!stops.includes(current) || current === edge) {
        event.preventDefault();
        (event.shiftKey ? stops[stops.length - 1] : stops[0])?.focus();
      }
    }

    opener.addEventListener("click", async () => {
      if (session) return;
      const current = {mode: "pending", restoreView: true, x: browser.scrollX, y: browser.scrollY, outside: []};
      session = current;
      if (page.fullscreenEnabled && !page.fullscreenElement && typeof surface.requestFullscreen === "function") {
        page.addEventListener("fullscreenchange", fullscreenChanged);
        try {
          await surface.requestFullscreen();
          if (session === current) {
            if (page.fullscreenElement === surface) fullscreenChanged();
            else restore();
          }
          return;
        } catch {
          if (session !== current) return;
          page.removeEventListener("fullscreenchange", fullscreenChanged);
        }
      }
      if (current.restoreView) show("fallback");
      else restore();
    });
    closer.addEventListener("click", () => close());
    return {close, active: () => Boolean(session && session.mode !== "pending")};
  }

  return {stageColors, linkStyles, xml, target, find, unlocked, available, edges, moduleDependencies, graph, rasterSize, pngBlob, saveBlob,
    standaloneHTML, bindFullscreen};
})();

if (typeof module === "object" && module.exports) module.exports = CurriculumRoadmap;



if (typeof document !== "undefined" && document.getElementById("roadmap-data")) {
  (() => {
    const road = CurriculumRoadmap;
    const data = JSON.parse(document.getElementById("roadmap-data").textContent);
    const el = id => document.getElementById("road-" + id);
    const app = document.getElementById("roadmap-app");
    const fullscreen = road.bindFullscreen(app, el("fullscreen-header"), el("fullscreen-open"),
      el("fullscreen-close"), document, window, changeFullscreenLayout);
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
    let autoFit = true;
    let frame;
    let windowedView;
    let resizePending = false;
    let drag = null;
    let initialized = false;
    let moduleFocus = true;
    let routeFocus = false;
    let history = [];
    let inspectorSelection;

    const escape = road.xml;
    const makeButton = (item, name = item.title) => '<button type="button" class="road-item" data-select="' +
      item.id + '"' + (item.topics ? ' data-module-reference' : "") +
      '><strong>' + item.id + '</strong><span>' + escape(name) + "</span></button>";

    function completedTopics() {
      return new Set(Object.keys(data.topics).filter(id =>
        document.getElementById("progress-" + id.toLowerCase()).value === "Completed"));
    }

    function titleFor(item) {
      return item.kind === "path" ? "Path " + item.id + " — " + item.title : item.id + " — " + item.title;
    }

    function topicList(ids, notes = {}, empty = "No topics in this group.") {
      if (!ids.length) return '<p class="road-empty">' + escape(empty) + '</p>';
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

    function moduleLinks(ids) {
      return '<ul class="road-list">' + ids.map(id =>
        "<li>" + makeButton(data.modules[id]) + "</li>").join("") + "</ul>";
    }

    function modulePreparation(module) {
      const external = id => data.topics[id].module !== module.id;
      const first = data.topics[module.topics[0]];
      return {
        first, firstRequired: first.closure.filter(external),
        allRequired: module.closure.filter(external),
      };
    }

    function moduleDetail(module, completed) {
      const {first, firstRequired, allRequired} = modulePreparation(module);
      const earlier = new Set(firstRequired);
      const {direct} = road.moduleDependencies(data, module.id);
      const progress = id => completed.has(id) ? "Completed" : "Not completed";
      const topicRows = (ids, describe, openLesson = false) => '<ul class="road-list road-topic-menu">' +
        ids.map(id => "<li>" + makeButton(data.topics[id]) +
          '<span class="road-topic-meta">' + progress(id) + describe(id) +
          (openLesson ? ' · <a href="#' + id.toLowerCase() + '">Open ' + id + ' lesson</a>' : "") +
          "</span></li>").join("") + "</ul>";
      const modulesFor = kind => [...new Set(direct.downstream.filter(edge => edge.kind === kind)
        .map(edge => edge.to))].sort();
      const connections = kind => module.topics.flatMap(id => data.topics[id][kind]
        .filter(item => kind !== "recommended" || !data.topics[id].conditional.some(edge => edge.id === item.id))
        .map(item => ({...item, target: id})));
      const groupNotes = (items, conditional = false) => {
        const byTopic = new Map();
        for (const item of items) {
          if (!byTopic.has(item.id)) byTopic.set(item.id, []);
          byTopic.get(item.id).push(item.target + (conditional ? " — " + item.note : ""));
        }
        return topicRows([...byTopic.keys()], id =>
          " · " + (conditional ? "" : "Helpful for ") + escape(byTopic.get(id).join("; ")));
      };
      const mandatory = connections("mandatory");
      const describeRequired = id => {
        const uses = mandatory.filter(edge => edge.id === id).map(edge => edge.target);
        return " · " + (uses.length ? "Required for " + uses.join(", ") : "Required earlier in your learning path.");
      };
      const later = allRequired.filter(id => !earlier.has(id));
      const required = !allRequired.length
        ? '<p>No required preparation. You can start this module.</p>'
        : '<p>These topics prepare you for specific lessons. Complete the required topics for the lesson you want to start.</p>' +
          '<h5>Before the first topic (' + first.id + ')</h5>' +
          (firstRequired.length ? topicRows(firstRequired, describeRequired) : '<p>No required preparation for the first topic.</p>') +
          (later.length ? '<h5>Before later topics in this module</h5>' + topicRows(later, describeRequired) : "");
      const topics = topicRows(module.topics, id => {
        const requiredIds = data.topics[id].mandatory.map(item => item.id);
        return requiredIds.length ? " · Required for this topic: " + requiredIds.join(", ") : "";
      }, true);
      const suggested = connections("recommended");
      const conditional = connections("conditional");
      const nextRequired = modulesFor("mandatory");
      const nextRecommended = modulesFor("recommended");
      const nextConditional = [];
      for (const topic of Object.values(data.topics)) {
        if (topic.module === module.id) continue;
        for (const edge of topic.conditional) {
          if (data.topics[edge.id].module === module.id) {
            nextConditional.push({id: topic.id, target: edge.id, note: edge.note});
          }
        }
      }
      return '<section class="road-reading-key"><h4>How to read this learning path</h4><dl>' +
        '<dt>Required</dt><dd>Complete this before starting the topic that uses it.</dd>' +
        '<dt>Optional</dt><dd>Helpful preparation you can skip.</dd>' +
        '<dt>Conditional</dt><dd>Required only for a specific exercise or path.</dd>' +
        '<dt>Next</dt><dd>A later module or topic that builds on this one.</dd></dl>' +
        '<p>A module arrow summarizes learning connections between topics in those modules.</p></section>' +
        '<h4>Required before starting this module</h4>' + required +
        '<h4>Topics in this module</h4><p>These are the topics covered by this module.</p>' + topics +
        '<h4>Optional preparation</h4><p>These topics may help with the listed lesson. Its required work appears above.</p>' +
        (suggested.length ? groupNotes(suggested) : '<p>No additional preparation is suggested.</p>') +
        (conditional.length ? '<h4>Required only for this exercise/path</h4>' + groupNotes(conditional, true) : "") +
        '<h4>What this module prepares you for</h4><p>These are later learning areas that build on what you study here.</p>' +
        (nextRequired.length ? '<h5>Required preparation for topics in</h5>' + moduleLinks(nextRequired)
          : '<p>This module does not have a required next module.</p>') +
        (nextRecommended.length ? '<h5>Helpful preparation for topics in</h5>' + moduleLinks(nextRecommended) : "") +
        (nextConditional.length ? '<h5>Required only for this exercise/path</h5>' + groupNotes(nextConditional, true) : "");
    }

    function renderInspector(completed, next) {
      el("clear").hidden = !selection;
      el("jump").hidden = !selection;
      focusToggle.disabled = !selection;
      exportMenu.options[1].disabled = !selection;
      if (!selection && exportMenu.value === "selection") exportMenu.value = "module";
      el("title").textContent = selection ? titleFor(selection) : "Choose a target";
      const readiness = el("readiness");
      readiness.hidden = selection?.kind !== "module";

      if (!selection) {
        inspectorSelection = null;
        el("estimate").textContent = "";
        el("details").innerHTML = "<p>Select a module to highlight its prerequisites and dependents. " +
          "Select a topic to inspect the exact requirements before studying it.</p>";
        return;
      }

      const pending = selection.closure.filter(id => !completed.has(id));
      const pendingHours = pending.reduce((total, id) => total + data.topics[id].hours, 0);
      const details = el("details");
      const keepOpen = new Set(inspectorSelection === selection.id
        ? [...details.querySelectorAll("details[data-disclosure][open]")].map(item => item.dataset.disclosure) : []);
      inspectorSelection = selection.id;
      const isModule = selection.kind === "module";
      if (isModule) {
        const {first, firstRequired, allRequired} = modulePreparation(selection);
        const remaining = firstRequired.filter(id => !completed.has(id)).length;
        if (remaining) {
          const plural = remaining === 1 ? "topic" : "topics";
          readiness.textContent = "Complete " + remaining + " required " + plural + " before starting with " + first.id + ".";
        } else if (firstRequired.length) {
          readiness.textContent = "Ready to start — all required preparation for " + first.id + " is complete.";
        } else {
          readiness.textContent = allRequired.length
            ? "You can start with " + first.id + " now. Some later topics have required preparation."
            : "You can start this module now.";
        }
      }
      el("estimate").textContent = isModule
        ? selection.difficulty + " · " + selection.topics.length + " topics · " + roadmapDuration(selection.hours) +
          " learner time · " + selection.topics.filter(id => completed.has(id)).length + "/" + selection.topics.length + " completed"
        : selection.closure.length + " topics · " + roadmapDuration(selection.total) +
          " learner time · " + roadmapDuration(pendingHours) + " still unmarked";
      const goal = selection.outcome ? "<h4>What you’ll demonstrate</h4><p>" + escape(selection.outcome) + "</p>" : "";
      const requirements = isModule
        ? moduleDetail(selection, completed)
        : selection.kind === "topic" ? selectedTopicDetail(selection)
          : '<p><a href="#quick-' + selection.id.toLowerCase() + '">Open Quick Learning plan</a></p>' +
            "<h4>Optional extensions</h4>" + topicList(selection.recommended || []);
      const targetModule = isModule ? selection.id : selection.module;
      const routeRole = id => {
        if (selection.roots.includes(id)) {
          return isModule ? "Topic in this module" : selection.kind === "topic" ? "Target topic" : "Path target";
        }
        if (!targetModule) return "Required earlier";
        return data.topics[id].module === targetModule ? "Required earlier in this module" : "Required preparation from another module";
      };
      const required = '<details class="road-route" data-disclosure="route"' + (keepOpen.has("route") ? " open" : "") +
        '><summary>Suggested study order — step by step · ' + selection.closure.length + ' topics</summary>' +
        '<p>Follow this order for the chosen topics and the required preparation that applies to them. ' +
        'Optional preparation and exercise-specific requirements are listed separately.</p>' +
        '<p>' + roadmapDuration(selection.total) + " learner time · " + roadmapDuration(pendingHours) +
        " still unmarked</p><ol>" +
        selection.closure.map(id => "<li>" + makeButton(data.topics[id]) + '<span class="road-route-hours">' +
          routeRole(id) + " · " + roadmapDuration(data.topics[id].hours) + " · " +
          (completed.has(id) ? "Completed" : "Not completed") + "</span></li>").join("") + "</ol></details>";
      const unlocks = '<details class="road-route" data-disclosure="progress"' +
        (keepOpen.has("progress") ? " open" : "") + '><summary>Available next based on your progress</summary>' +
        '<p>Availability comes from your saved topic completions. The dependency arrows show curriculum links.</p>' +
        '<h5>Available now</h5>' + topicList(road.available(data, completed), {}, "No new topics are available from your saved progress.") +
        '<h5>New if you complete this selection</h5>' + topicList(next, {}, "Completing this selection won’t make a new topic available yet.") + '</details>';
      const detailLink = selection.kind === "path" ? "" : '<p><a href="#' + selection.id.toLowerCase() +
        '">Open in Complete Course</a></p>';
      const back = history.at(-1);
      const backButton = back ? '<button type="button" data-back>Back to ' + escape(back) + '</button>' : "";
      details.innerHTML = backButton + requirements + required + unlocks + goal + detailLink;
    }

    function applyCamera() {
      viewport.firstElementChild.style.transform = "translate(" + camera.x + "px," + camera.y + "px) scale(" + camera.scale + ")";
      el("zoom").textContent = Math.round(camera.scale * 100) + "%";
    }

    function fittedCamera(model, size) {
      const {width, height, fitAll} = size;
      if (fitAll) {
        const scale = Math.min(1, Math.max(1, width - 12) / model.width, Math.max(1, height - 12) / model.height);
        return {scale, x: (width - model.width * scale) / 2, y: (height - model.height * scale) / 2};
      }
      const bounds = model.bounds;
      if (bounds) {
        const boundsWidth = bounds.right - bounds.left;
        const boundsHeight = bounds.bottom - bounds.top;
        const scale = Math.min(1, (width - 30) / boundsWidth, (height - 30) / boundsHeight);
        if (scale >= .45) {
          return {scale, x: (width - boundsWidth * scale) / 2 - bounds.left * scale,
                  y: (height - boundsHeight * scale) / 2 - bounds.top * scale};
        }
      }
      return {x: 0, y: 0, scale: Math.max(.57, Math.min(1, width / model.width))};
    }

    function resetCamera() {
      autoFit = true;
      camera = fittedCamera(visibleGraph, frame);
      applyCamera();
    }

    function zoom(factor, x = viewport.clientWidth / 2, y = viewport.clientHeight / 2) {
      const scale = Math.max(Math.min(.2, fittedCamera(visibleGraph, frame).scale), Math.min(2.6, camera.scale * factor));
      const ratio = scale / camera.scale;
      camera = {x: x - (x - camera.x) * ratio, y: y - (y - camera.y) * ratio, scale};
      autoFit = false;
      applyCamera();
    }

    function pan(x, y, user = true) {
      camera.x += x;
      camera.y += y;
      if (user) autoFit = false;
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
        pan(outer.left + (outer.width - card.width) / 2 - card.left, outer.top + (outer.height - card.height) / 2 - card.top, false);
      }
    }

    function measure() {
      return {width: viewport.clientWidth, height: viewport.clientHeight,
              fitAll: fullscreen.active() && modeMenu.value === "module"};
    }

    function paintGraph(size, next = road.unlocked(data, selection, completedTopics())) {
      frame = size;
      const isModuleView = selection?.kind === "module" && modeMenu.value === "module";
      focusToggle.checked = isModuleView ? moduleFocus : routeFocus;
      el("dependent-key").hidden = !isModuleView || !moduleFocus;
      const heading = modeMenu.value === "module" ? "Module overview" : "Topic detail";
      const dimensions = {width: Math.max(1, size.width - 24), height: Math.max(1, size.height - 24)};
      visibleGraph = road.graph(data, {
        mode: modeMenu.value, selection, focus: focusToggle.checked, optional: optionalToggle.checked, unlocked: next,
        title: "LLM Evaluation Engineering · " + heading, size: size.fitAll ? dimensions : null,
      });
      const meta = "Curriculum revision " + data.revision + " · " + Object.keys(data.modules).length + " modules" +
        (modeMenu.value === "topic" ? " · " + visibleGraph.count + " topics shown" : "") + " · " + heading;
      if (el("graph-meta").textContent !== meta) el("graph-meta").textContent = meta;
      viewport.innerHTML = visibleGraph.svg;
    }

    function draw(reset = false) {
      const completed = completedTopics();
      const next = road.unlocked(data, selection, completed);
      renderInspector(completed, next);
      paintGraph(measure(), next);
      if (reset) resetCamera();
      else applyCamera();
    }

    function resizeGraph() {
      if (!initialized) return;
      const size = measure();
      if (!size.width || !size.height ||
          (size.width === frame?.width && size.height === frame.height && size.fitAll === frame.fitAll)) return;
      const focusedNode = document.activeElement?.dataset?.node;
      const previousModel = visibleGraph;
      const previousFrame = frame;
      paintGraph(size);
      if (autoFit || !previousFrame) {
        resetCamera();
        if (!frame.fitAll) reveal(selection?.id);
      } else {
        // Preserve the center and the user's zoom relative to the old fit across resizes.
        const px = (previousFrame.width / 2 - camera.x) / camera.scale / previousModel.width;
        const py = (previousFrame.height / 2 - camera.y) / camera.scale / previousModel.height;
        const scale = Math.min(2.6, camera.scale * fittedCamera(visibleGraph, frame).scale /
          fittedCamera(previousModel, previousFrame).scale);
        camera = {scale, x: size.width / 2 - px * visibleGraph.width * scale,
                  y: size.height / 2 - py * visibleGraph.height * scale};
        applyCamera();
      }
      if (focusedNode) viewport.querySelector('[data-node="' + focusedNode + '"]')?.focus({preventScroll: true});
    }

    function scheduleResize() {
      if (resizePending) return;
      resizePending = true;
      window.requestAnimationFrame(() => {
        resizePending = false;
        resizeGraph();
      });
    }

    function changeFullscreenLayout(active) {
      if (active) windowedView = {camera: {...camera}, autoFit, frame, target: selection?.id, mode: modeMenu.value};
      const size = measure();
      if (size.width && size.height) {
        paintGraph(size);
        const saved = windowedView;
        if (!active && saved?.target === selection?.id && saved?.mode === modeMenu.value &&
            saved.frame?.width === size.width && saved.frame.height === size.height) {
          ({camera, autoFit} = saved);
          applyCamera();
        } else {
          resetCamera();
          if (!size.fitAll) reveal(selection?.id);
        }
      }
      if (!active) {
        if (!size.width || !size.height) frame = null;
        windowedView = null;
      }
    }

    function choose(id, origin) {
      const picked = road.target(data, id);
      if (!picked) return;
      const previous = selection;
      if (origin === "inspector" && previous && previous.id !== id) history.push(previous.id);
      else if (origin !== "back" && origin !== "inspector") history = [];
      selection = picked;
      pathMenu.value = selection.kind === "path" ? id : "";
      if (selection.kind === "topic") {
        modeMenu.value = "topic";
        // Topic details start with the required chain and related optional links in view.
        routeFocus = true;
        optionalToggle.checked = true;
      }
      if (selection.kind === "module") modeMenu.value = "module";
      if (selection.kind === "path") {
        modeMenu.value = "topic";
        routeFocus = origin !== "journey";
        optionalToggle.checked = true;
      }
      draw(selection.kind === "module" ? moduleFocus || previous?.kind !== "module" : routeFocus || origin !== "graph");
      if (selection.kind !== "path" && !frame.fitAll) reveal(id);
      if (origin === "graph") {
        viewport.querySelector('[data-node="' + id + '"]')?.focus({preventScroll: true});
      } else if (origin === "results" || origin === "inspector" || origin === "back") {
        el("title").tabIndex = -1;
        if (origin !== "results") el("inspector").scrollTop = 0;
        el("title").focus({preventScroll: origin === "results"});
      }
      exportMenu.value = "selection";
      if (selection.kind === "path") {
        document.dispatchEvent(new CustomEvent("curriculum-path-selected", {detail: id}));
      }
    }

    function clearSelection() {
      selection = null;
      history = [];
      pathMenu.value = "";
      moduleFocus = true;
      routeFocus = false;
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
      if (event.key === "Escape" && !fullscreen.active()) results.hidden = true;
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
      if (event.target.closest("[data-back]") && history.length) {
        choose(history.pop(), "back");
        return;
      }
      const item = event.target.closest("[data-select]");
      if (item) choose(item.dataset.select, "inspector");
    });
    for (const [eventType, entering] of [["pointerover", true], ["pointerout", false], ["focusin", true], ["focusout", false]]) {
      el("details").addEventListener(eventType, event => {
        const reference = event.target.closest("[data-module-reference]");
        if (!reference || modeMenu.value !== "module") return;
        const id = reference.dataset.select;
        const node = viewport.querySelector('[data-node="' + id + '"]');
        if (entering) {
          node?.classList.add("road-reference");
          if (eventType === "focusin") reveal(id);
        } else if (!reference.contains(event.relatedTarget) &&
                   !(eventType === "pointerout" && reference === document.activeElement)) {
          node?.classList.remove("road-reference");
        }
      });
    }
    pathMenu.addEventListener("change", () => pathMenu.value ? choose(pathMenu.value, "path") : clearSelection());
    modeMenu.addEventListener("change", () => {draw(true); if (!frame.fitAll) reveal(selection?.id);});
    focusToggle.addEventListener("change", () => {
      if (selection?.kind === "module" && modeMenu.value === "module") moduleFocus = focusToggle.checked;
      else routeFocus = focusToggle.checked;
      draw(true);
      if (!frame.fitAll) reveal(selection?.id);
    });
    optionalToggle.addEventListener("change", () => draw());
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
      road.saveBlob(new Blob([model.svg], {type: "image/svg+xml;charset=utf-8"}), filename("svg"));
      status.textContent = "SVG download requested.";
    });
    el("png").addEventListener("click", async () => {
      el("png").disabled = true;
      status.textContent = "Preparing PNG…";
      const name = filename("png");
      try {
        const png = await road.pngBlob(exportModel(), window);
        road.saveBlob(png, name);
        status.textContent = "PNG download requested.";
      } catch (error) {
        status.textContent = error.message + " Try SVG for a scalable copy.";
      } finally {
        el("png").disabled = false;
      }
    });
    el("html").addEventListener("click", () => {
      const offline = road.standaloneHTML(portableCurriculum, "roadmap");
      road.saveBlob(new Blob([offline], {type: "text/html;charset=utf-8"}), "llm-evaluation-curriculum-v" + data.revision + ".html");
      status.textContent = "Standalone HTML download requested.";
    });

    const legend = el("legend");
    legend.innerHTML = data.stages.map((stage, i) => '<li><span class="road-stage-key" style="--key:' +
      road.stageColors[i].fill + ";--key-ink:" + road.stageColors[i].ink + '"></span>' + escape(stage) + "</li>")
      .concat(Object.entries(road.linkStyles).map(([kind, style]) =>
        '<li><span class="road-edge-key road-edge-' + kind + '" aria-hidden="true"></span>' + style.label + "</li>")).join("") +
      '<li id="road-dependent-key" hidden><span class="road-edge-key road-edge-downstream" aria-hidden="true"></span>' +
      'Mandatory dependent of selection</li>';

    function enterRoadmap() {
      if (initialized) {
        scheduleResize();
        return;
      }
      initialized = true;
      app.hidden = false;
      draw(true);
      if (window.ResizeObserver) new window.ResizeObserver(scheduleResize).observe(viewport);
      else window.addEventListener("resize", scheduleResize);
    }
    document.addEventListener("curriculum-tab", event => {
      if (event.detail === "#roadmap") enterRoadmap();
      else fullscreen.close(false);
    });
    function openRoute(hash) {
      const route = /^#roadmap-([a-g]|full)$/.exec(hash);
      if (!route) return;
      enterRoadmap();
      if (route[1] === "full") {
        modeMenu.value = "module";
        exportMenu.value = "module";
        clearSelection();
      } else {
        choose(route[1].toUpperCase(), "journey");
      }
    }
    document.addEventListener("curriculum-route", event => openRoute(event.detail));
    document.addEventListener("curriculum-progress", () => {if (initialized && selection) draw();});
  })();
}

