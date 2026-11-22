"use strict";

(() => {
  const data = JSON.parse(document.getElementById("roadmap-data").textContent);
  const catalog = document.getElementById("quick-catalog");
  const plans = Array.from(document.querySelectorAll("[data-quick-plan]"));
  const indicators = Array.from(document.querySelectorAll("[data-plan-progress]"));
  const checks = Array.from(document.querySelectorAll("[data-complete]"));
  const returnToPlan = document.getElementById("return-to-plan");
  const hosted = location.protocol === "https:" || location.protocol === "http:";
  const road = CurriculumRoadmap;

  function syncProgress() {
    const {statuses, selectedPath} = progressState.current();
    for (const check of checks) {
      check.checked = statuses[check.dataset.complete] === "Completed";
      check.closest(".plan-step").classList.toggle("is-complete", check.checked);
    }
    for (const indicator of indicators) {
      const useSelection = indicator.dataset.planProgress === "selected";
      const path = data.paths[useSelection ? (selectedPath || "A") : indicator.dataset.planProgress];
      const progress = LearningProgress.routeProgress(path, data.topics, statuses);
      const label = indicator.querySelector("[data-resume-path]");
      if (label) label.textContent = selectedPath ? path.title : "Beginner starting point";
      indicator.querySelector("[data-plan-status]").textContent =
        progress.next ? progress.completed + " completed · " + progress.remaining +
          " remaining · " + LearningProgress.duration(progress.hours) + " left"
          : "Path complete. All " + progress.completed + " required topics are complete.";
      const next = indicator.querySelector("[data-plan-next]");
      next.hidden = !progress.next;
      if (progress.next) {
        const topic = data.topics[progress.next];
        next.href = "#" + topic.id.toLowerCase();
        next.textContent = (useSelection && !selectedPath && !progress.completed ? "Start Learning: " :
          "Continue Learning: ") + topic.title;
      }
    }
  }

  function pathGraph(path) {
    return road.graph(data, {
      mode: "topic", selection: road.target(data, path.id),
      exporting: true, exportPath: true, title: path.title, markerPrefix: "plan-" + path.id.toLowerCase() + "-arrow-",
    });
  }

  function showRoute(hash) {
    if (!/^#(?:quick(?:-[a-g])?|paths|preparation)$/.test(hash)) return;
    const key = /^#quick-([a-g])$/.exec(hash)?.[1].toUpperCase() || "";
    catalog.hidden = Boolean(key);
    for (const plan of plans) {
      plan.hidden = plan.dataset.quickPlan !== key;
    }
    returnToPlan.hidden = !key;
    if (key) {
      const link = returnToPlan.querySelector("a");
      link.href = "#quick-" + key.toLowerCase();
      link.textContent = "Return to Quick Learning plan: " + data.paths[key].title;
    }
  }

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
      const url = new URL(location.pathname, location.origin);
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

  for (const check of checks) {
    check.parentElement.hidden = false;
    check.addEventListener("change", () => {
      const menu = menus.get(check.dataset.complete);
      menu.value = check.checked ? "Completed" : "Not Started";
      menu.dispatchEvent(new Event("change"));
    });
  }

  for (const indicator of indicators) indicator.hidden = false;
  document.addEventListener("curriculum-progress", syncProgress);
  document.addEventListener("curriculum-route", event => showRoute(event.detail));
  syncProgress();
  if (!/^#quick-[a-g]$/.test(initialRoute)) showRoute("#quick");
  showRoute(initialRoute);
})();
