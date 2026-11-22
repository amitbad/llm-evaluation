"use strict";

(() => {
  const el = name => document.getElementById("navigator-" + name);
  const launch = el("launch");
  const dock = launch.closest(".navigator-dock");
  const dialog = el("dialog");
  if (typeof dialog.showModal !== "function") return;
  const map = el("map");
  const surface = el("surface");
  const viewport = el("viewport");
  const topics = curriculum.topics;
  const cameras = new Map();
  const card = {width: 224, height: 88, gapX: 44, gapY: 44, gutter: 22};
  let route = null;
  let model = null;
  let scale = 1;
  let drag = null;

  function state(id, statuses) {
    const value = statuses[id];
    const label = value === "Completed" || value === "In Progress" ? value :
      route.path.closure.indexOf(id) > route.index ? "Upcoming" : "Not started";
    return id === route.topic ? "Current · " + label : label;
  }

  function syncProgress() {
    if (!route || model?.pathId !== route.path.id) return;
    const {statuses} = progressState.current();
    model.nodes.forEach(({id, button, badge, dependencyNames}) => {
      const labels = state(id, statuses);
      button.dataset.completed = String(statuses[id] === "Completed");
      if (id === route.topic) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
      badge.textContent = labels;
      button.setAttribute("aria-label", button.dataset.title + ". " + labels + dependencyNames);
    });
    for (const edge of map.querySelectorAll("[data-from]")) {
      edge.dataset.near = String(edge.dataset.from === route.topic || edge.dataset.to === route.topic);
    }
  }

  function connection(from, to, kind) {
    const lane = kind === "order" ? 18 : kind === "mandatory" ? 0 : -12;
    const fx = from.x + card.width / 2 + lane, tx = to.x + card.width / 2 + lane;
    if (from.y === to.y) {
      if (Math.abs(from.x - to.x) > card.width + card.gapX) {
        const y = from.y - card.gutter + 4;
        return `M${fx} ${from.y} V${y} H${tx} V${to.y - 3}`;
      }
      const forward = from.x < to.x;
      const x1 = forward ? from.x + card.width : from.x;
      const x2 = forward ? to.x - 3 : to.x + card.width + 3;
      const y = from.y + card.height / 2 + lane;
      return `M${x1} ${y} H${x2}`;
    }
    const forward = from.y < to.y;
    const y1 = from.y + (forward ? card.height : 0);
    const y2 = to.y + (forward ? -3 : card.height + 3);
    const mid = (y1 + y2) / 2;
    return `M${fx} ${y1} C${fx} ${mid} ${tx} ${mid} ${tx} ${y2}`;
  }

  function layout(path) {
    const columns = Math.min(4, path.closure.length);
    const nodes = new Map();
    path.closure.forEach((id, index) => {
      const row = Math.floor(index / columns);
      const offset = index % columns;
      const column = row % 2 ? columns - 1 - offset : offset;
      nodes.set(id, {id, x: card.gutter + column * (card.width + card.gapX),
        y: card.gutter + row * (card.height + card.gapY)});
    });
    const edges = [];
    for (const [index, id] of path.closure.entries()) {
      if (index) edges.push({from: path.closure[index - 1], to: id, kind: "order"});
      for (const kind of ["mandatory", "recommended", "conditional"]) {
        for (const prerequisite of topics[id][kind]) {
          if (nodes.has(prerequisite.id)) edges.push({from: prerequisite.id, to: id, kind});
        }
      }
    }
    return {
      nodes, edges, pathId: path.id,
      width: 2 * card.gutter + columns * (card.width + card.gapX) - card.gapX,
      height: 2 * card.gutter + Math.ceil(path.closure.length / columns) * (card.height + card.gapY) - card.gapY,
    };
  }

  function draw(path) {
    model = layout(path);
    const {nodes, edges, width, height} = model;
    map.style.width = width + "px";
    map.style.height = height + "px";
    map.innerHTML = `<svg class="navigator-links" aria-hidden="true" width="${width}" height="${height}">
      <defs><marker id="navigator-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z"/></marker></defs>
      ${edges.map(({from, to, kind}) =>
        `<path class="navigator-edge-${kind}" data-from="${from}" data-to="${to}" d="${connection(nodes.get(from), nodes.get(to), kind)}"${kind === "order" ? "" : ' marker-end="url(#navigator-arrow)"'}/>`).join("")}
    </svg>`;
    for (const [index, id] of path.closure.entries()) {
      const node = nodes.get(id);
      const {title, mandatory, recommended, conditional} = topics[id];
      const button = document.createElement("button");
      const name = document.createElement("span");
      const badge = document.createElement("small");
      button.type = "button";
      button.className = "navigator-node";
      button.dataset.lesson = id;
      button.dataset.title = (index + 1) + ". " + title;
      button.style.left = node.x + "px";
      button.style.top = node.y + "px";
      name.textContent = button.dataset.title;
      button.append(name, badge);
      map.append(button);
      const related = (edges, label) => {
        const values = edges.filter(edge => nodes.has(edge.id)).map(edge => topics[edge.id].title);
        return values.length ? ". " + label + ": " + values.join(", ") : "";
      };
      Object.assign(node, {button, badge, dependencyNames: related(mandatory, "Required first") +
        related(recommended, "Recommended first") + related(conditional, "Conditional prerequisite")});
    }
  }

  function setScale(value) {
    scale = value;
    surface.style.width = model.width * scale + "px";
    surface.style.height = model.height * scale + "px";
    map.style.transform = "scale(" + scale + ")";
    el("zoom").textContent = Math.round(scale * 100) + "%";
  }

  function center() {
    const current = model.nodes.get(route.topic);
    viewport.scrollTo({
      left: (current.x + card.width / 2) * scale - viewport.clientWidth / 2,
      top: (current.y + card.height / 2) * scale - viewport.clientHeight / 2,
    });
  }

  function zoom(factor) {
    const next = Math.min(1.65, Math.max(.35, scale * factor));
    const x = viewport.clientWidth / 2, y = viewport.clientHeight / 2;
    const left = (viewport.scrollLeft + x) * next / scale - x;
    const top = (viewport.scrollTop + y) * next / scale - y;
    setScale(next);
    viewport.scrollTo({left, top});
  }

  function open() {
    if (!route || dialog.open) return;
    if (model?.pathId !== route.path.id) draw(route.path);
    el("path").textContent = route.path.title;
    syncProgress();
    dialog.showModal();
    const saved = cameras.get(route.path.id);
    setScale(saved?.scale ?? 1);
    if (saved) viewport.scrollTo(saved);
    else center();
    el("title").focus({preventScroll: true});
  }

  function dismiss(restoreFocus = true) {
    if (dialog.open) {
      cameras.set(model.pathId, {scale, left: viewport.scrollLeft, top: viewport.scrollTop});
      drag = null;
      dialog.close();
    }
    if (restoreFocus) launch.focus({preventScroll: true});
  }

  launch.addEventListener("click", open);
  el("minimize").addEventListener("click", () => dismiss());
  el("close").addEventListener("click", () => dismiss());
  el("zoom-out").addEventListener("click", () => zoom(1 / 1.2));
  el("zoom-in").addEventListener("click", () => zoom(1.2));
  el("center").addEventListener("click", () => {
    center();
    model.nodes.get(route.topic).button.focus({preventScroll: true});
  });
  dialog.addEventListener("cancel", event => {
    event.preventDefault();
    dismiss();
  });

  viewport.addEventListener("keydown", event => {
    if (event.target !== viewport) return;
    const moves = {ArrowLeft: [-80, 0], ArrowRight: [80, 0], ArrowUp: [0, -80], ArrowDown: [0, 80]};
    if (Object.hasOwn(moves, event.key)) viewport.scrollBy(...moves[event.key]);
    else if (event.key === "+" || event.key === "=") zoom(1.2);
    else if (event.key === "-") zoom(1 / 1.2);
    else return;
    event.preventDefault();
  });
  viewport.addEventListener("pointerdown", event => {
    if (event.pointerType !== "mouse" || event.button !== 0 || event.target.closest("button") || drag) return;
    drag = {id: event.pointerId, x: event.clientX, y: event.clientY};
    viewport.setPointerCapture(event.pointerId);
  });
  viewport.addEventListener("pointermove", event => {
    if (drag?.id !== event.pointerId) return;
    viewport.scrollBy(drag.x - event.clientX, drag.y - event.clientY);
    drag.x = event.clientX;
    drag.y = event.clientY;
  });
  for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) {
    viewport.addEventListener(name, event => {
      if (drag?.id === event.pointerId) drag = null;
    });
  }

  map.addEventListener("click", event => {
    const id = event.target.closest("[data-lesson]")?.dataset.lesson;
    if (!route?.path.closure.includes(id)) return;
    const hash = guidedLearning.lessonHash(route.path.id, id);
    dismiss(false);
    if (location.hash === hash) followHash(true);
    else location.hash = hash;
  });

  document.addEventListener("curriculum-route", event => {
    const next = guidedLearning.resolve(event.detail);
    if (dialog.open && (next?.topic !== route?.topic || next?.path.id !== route?.path.id)) {
      dismiss(false);
    }
    route = next?.topic ? next : null;
    dock.hidden = !route;
    syncProgress();
  });
  document.addEventListener("curriculum-progress", syncProgress);
})();
