"use strict";

const guidedLearning = (() => {
  const data = curriculum;
  const catalog = document.getElementById("quick-catalog");
  const plans = Array.from(document.querySelectorAll("[data-quick-plan]"));
  const indicators = Array.from(document.querySelectorAll("[data-plan-progress]"));
  const returnToPlan = document.getElementById("return-to-plan");
  const hosted = location.protocol === "https:" || location.protocol === "http:";
  const road = CurriculumRoadmap;
  const guided = name => document.getElementById("guided-" + name);
  const lastViewed = new Map();
  let active = null;
  let mounted = null;

  const pathHash = key => "#quick-" + key.toLowerCase();
  const lessonHash = (key, topic) => pathHash(key) + "/" + topic.toLowerCase();

  function resolve(hash) {
    const match = /^#quick-([a-g])(?:\/(m\d{2}-t\d{2}))?$/.exec(hash);
    if (!match) return null;
    const path = data.paths[match[1].toUpperCase()];
    const index = path.closure.indexOf(match[2]?.toUpperCase());
    return {path, index, topic: path.closure[index], overview: pathHash(path.id)};
  }

  function restoreMaterial() {
    if (!mounted) return;
    for (const [link, href] of mounted.links) link.setAttribute("href", href);
    if (mounted.outline) {
      mounted.outline.home.append(mounted.outline.objective);
      mounted.outline.section.hidden = true;
    }
    mounted.parent.append(mounted.node);
    mounted = null;
  }

  function mountMaterial(route) {
    const node = document.getElementById("material-" + route.topic.toLowerCase());
    const section = node.querySelector(".lesson-objectives");
    let outline = null;
    if (section) {
      const moduleId = data.topics[route.topic].module.toLowerCase();
      const objective = document.getElementById("module-objectives-" + moduleId);
      outline = {objective, home: objective.parentElement, section};
      section.querySelector("[data-lesson-objectives]").append(objective);
      section.hidden = false;
    }
    const links = Array.from(node.querySelectorAll('a[href^="#m"]'), link => [link, link.getAttribute("href")]);
    mounted = {node, links, parent: node.parentElement, outline};
    for (const [link, href] of links) {
      const topic = href.slice(1).toUpperCase();
      if (route.path.closure.includes(topic)) link.setAttribute("href", lessonHash(route.path.id, topic));
      else link.removeAttribute("href");
    }
    guided("material").append(node);
  }

  function syncProgress() {
    const {statuses, selectedPath} = progressState.current();
    for (const indicator of indicators) {
      const useSelection = indicator.dataset.planProgress === "selected";
      const path = data.paths[useSelection ? (selectedPath || "A") : indicator.dataset.planProgress];
      const progress = LearningProgress.routeProgress(path, data.topics, statuses);
      const label = indicator.querySelector("[data-resume-path]");
      if (label) label.textContent = selectedPath ? path.title : "Beginner starting point";
      indicator.querySelector("[data-plan-status]").textContent =
        progress.next ? progress.completed + " completed · " + progress.remaining +
          " remaining · " + LearningProgress.duration(progress.hours) + " left"
          : "Path complete. All " + progress.completed + " required lessons are complete.";
      const next = indicator.querySelector("[data-plan-next]");
      next.hidden = !progress.next;
      if (progress.next) {
        const topic = data.topics[progress.next];
        next.href = indicator.dataset.guided !== undefined ? lessonHash(path.id, topic.id) : "#" + topic.id.toLowerCase();
        const started = progress.completed || statuses[topic.id] || lastViewed.has(path.id);
        next.textContent = (started ? "Continue Learning: " : "Start Learning: ") + topic.title;
      }
    }
    for (const plan of plans) {
      const path = data.paths[plan.dataset.quickPlan];
      const current = lastViewed.get(path.id) || LearningProgress.routeProgress(path, data.topics, statuses).next;
      for (const step of plan.querySelectorAll("[data-step]")) {
        const {step: topic} = step.dataset;
        const complete = statuses[topic] === "Completed";
        step.classList.toggle("is-complete", complete);
        const link = step.querySelector("a");
        if (topic === current) link.setAttribute("aria-current", "step");
        else link.removeAttribute("aria-current");
        const state = step.querySelector("[data-lesson-state]");
        state.hidden = false;
        state.textContent = (topic === current ? "Current lesson · " : "") + (statuses[topic] || "Not Started");
      }
    }
    returnToPlan.hidden = !selectedPath;
    if (selectedPath) {
      const last = lastViewed.get(selectedPath);
      const link = returnToPlan.querySelector("a");
      link.href = last ? lessonHash(selectedPath, last) : pathHash(selectedPath);
      link.textContent = "Return to Quick Learning: " + data.paths[selectedPath].title;
    }
    if (active) {
      const status = statuses[active.topic];
      const complete = status === "Completed";
      const progress = LearningProgress.routeProgress(active.path, data.topics, statuses);
      const total = active.path.closure.length;
      guided("progress").max = total;
      guided("progress").value = progress.completed;
      guided("progress-label").textContent = progress.completed + " of " + total + " lessons completed";
      guided("complete").setAttribute("aria-disabled", String(complete));
      guided("complete").textContent = complete ? "Completed" : "Mark as Completed";
      guided("status").textContent = "Lesson progress: " + (status || "Not Started");
    }
  }

  function pathGraph(path) {
    return road.graph(data, {
      mode: "topic", selection: road.target(data, path.id),
      exporting: true, exportPath: true, title: path.title, markerPrefix: "plan-" + path.id.toLowerCase() + "-arrow-",
    });
  }

  function show(hash, route) {
    restoreMaterial();
    active = route?.topic ? route : null;
    guided("lesson").hidden = !active;
    if (route || ["#quick", "#paths", "#preparation", "#preparation-packet"].includes(hash)) {
      catalog.hidden = Boolean(route);
      for (const plan of plans) plan.hidden = Boolean(active) || plan.dataset.quickPlan !== route?.path.id;
    }
    if (active) {
      const {path, index, topic, overview} = active;
      lastViewed.set(path.id, topic);
      guided("path").textContent = path.title;
      guided("path").href = overview;
      guided("back").href = overview;
      guided("position").textContent = "Lesson " + (index + 1) + " of " + path.closure.length;
      guided("title").textContent = data.topics[topic].title;
      guided("estimate").textContent = LearningProgress.duration(data.topics[topic].hours) + " estimated study time";
      for (const [control, relative] of [["previous", -1], ["next", 1]]) {
        const neighbor = path.closure[index + relative];
        guided(control).hidden = !neighbor;
        guided(control).href = neighbor ? lessonHash(path.id, neighbor) : overview;
      }
      mountMaterial(active);
    }
    if (route && progressState.current().selectedPath !== route.path.id) progressState.select(route.path.id);
    else syncProgress();
    return active ? guided("lesson") : null;
  }

  guided("complete").addEventListener("click", () => {
    if (!active) return;
    const current = progressState.current();
    if (current.statuses[active.topic] === "Completed") return;
    progressState.apply({...current, statuses: {...current.statuses, [active.topic]: "Completed"}});
  });
  window.addEventListener("beforeprint", restoreMaterial);
  window.addEventListener("afterprint", () => {
    if (active && !mounted) mountMaterial(active);
  });

  for (const plan of plans) {
    const path = data.paths[plan.dataset.quickPlan];
    const fragment = "#quick-" + path.id.toLowerCase();
    const feedback = plan.querySelector("[data-plan-message]");
    const visual = plan.querySelector("[data-plan-visual]");
    visual.hidden = false;
    visual.addEventListener("toggle", () => {
      if (visual.open && !visual.querySelector("svg")) {
        visual.querySelector("div").innerHTML = pathGraph(path).svg;
      }
    });

    const share = plan.querySelector("[data-plan-share]");
    share.hidden = !hosted;
    plan.querySelector("[data-plan-sharing]").textContent = hosted
      ? "Copy a link to this exact path or download an offline copy."
      : "Share the downloaded HTML file. This local file address only works on your device.";
    share.addEventListener("click", async () => {
      const url = new URL("master-curriculum.html", location.href);
      url.hash = fragment;
      const field = plan.querySelector("[data-plan-url]");
      try {
        await navigator.clipboard.writeText(url.href);
        field.hidden = true;
        feedback.textContent = "Path link copied.";
      } catch {
        field.hidden = false;
        field.value = url.href;
        field.focus();
        field.select();
        feedback.textContent = "Copy the selected path link.";
      }
    });

    for (const button of plan.querySelectorAll("[data-plan-download]")) {
      button.hidden = false;
      button.addEventListener("click", async () => {
        const format = button.dataset.planDownload;
        const filename = "llm-evaluation-path-" + path.id.toLowerCase() + "-v" + data.revision + "." + format;
        button.disabled = true;
        try {
          let blob;
          if (format === "html") {
            const offline = road.standaloneHTML(portableCurriculum, fragment.slice(1));
            blob = new Blob([offline], {type: "text/html;charset=utf-8"});
          } else if (format === "svg") {
            blob = new Blob([pathGraph(path).svg], {type: "image/svg+xml;charset=utf-8"});
          } else {
            feedback.textContent = "Preparing PNG…";
            blob = await road.pngBlob(pathGraph(path), window);
          }
          road.saveBlob(blob, filename);
          feedback.textContent = format.toUpperCase() + " download requested.";
        } catch (error) {
          feedback.textContent = "Download could not be prepared. " + error.message;
        } finally {
          button.disabled = false;
        }
      });
    }
  }

  for (const indicator of indicators) indicator.hidden = false;
  document.addEventListener("curriculum-progress", syncProgress);
  show("#quick", null);
  return {resolve, show, lessonHash};
})();
