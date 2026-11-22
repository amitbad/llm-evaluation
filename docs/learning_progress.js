"use strict";

const LearningProgress = (() => {
  const format = "testneural-academy-progress";
  const version = 1;
  const statusKey = "llm-evaluation-master-curriculum-progress-v1";
  const pathKey = "llm-evaluation-master-curriculum-selected-path-v1";
  const values = ["In Progress", "Completed"];
  const backupKeys = new Set(["format", "version", "completedTopicIds", "selectedPath", "exportedAt"]);

  function duration(hours) {
    const minutes = Math.round(hours * 60);
    const remainder = minutes % 60;
    return Math.floor(minutes / 60) + "h" + (remainder ? " " + remainder + "m" : "");
  }

  function validPath(key, paths) {
    return typeof key === "string" && Object.hasOwn(paths, key);
  }

  function parseBackup(text, topics, paths) {
    let backup;
    try { backup = JSON.parse(text); } catch { throw new Error("The file is not valid JSON."); }
    if (!backup || typeof backup !== "object" || Array.isArray(backup) ||
        backup.format !== format || backup.version !== version) {
      throw new Error("This is not a supported academy progress backup.");
    }
    if (Object.keys(backup).some(key => !backupKeys.has(key)) || !Array.isArray(backup.completedTopicIds)) {
      throw new Error("The backup has unexpected fields or a missing completed-topic list.");
    }
    const date = typeof backup.exportedAt === "string" ? new Date(backup.exportedAt) : null;
    if (!date || !Number.isFinite(date.valueOf()) || date.toISOString() !== backup.exportedAt) {
      throw new Error("The backup has an invalid export timestamp.");
    }
    if (Object.hasOwn(backup, "selectedPath") && !validPath(backup.selectedPath, paths)) {
      throw new Error("The backup refers to an unknown learning path.");
    }
    if (backup.completedTopicIds.some(id => typeof id !== "string" || !Object.hasOwn(topics, id))) {
      throw new Error("The backup contains unknown or invalid topic IDs. No progress was changed.");
    }
    if (new Set(backup.completedTopicIds).size !== backup.completedTopicIds.length) {
      throw new Error("The backup lists the same topic more than once.");
    }
    return backup;
  }

  function makeBackup(current, exportedAt = new Date().toISOString()) {
    return {
      format, version,
      completedTopicIds: Object.keys(current.statuses).filter(id => current.statuses[id] === "Completed"),
      ...(current.selectedPath ? {selectedPath: current.selectedPath} : {}),
      exportedAt,
    };
  }

  function projectImport(current, backup, mode) {
    if (mode !== "merge" && mode !== "replace") throw new Error("Choose a valid import mode.");
    const statuses = mode === "merge" ? {...current.statuses} : {};
    for (const id of backup.completedTopicIds) statuses[id] = "Completed";
    return {
      statuses,
      selectedPath: backup.selectedPath || (mode === "merge" ? current.selectedPath : null),
    };
  }

  function previewImport(current, backup, mode, paths) {
    const next = projectImport(current, backup, mode);
    const added = backup.completedTopicIds.filter(id => current.statuses[id] !== "Completed").length;
    const removed = Object.keys(current.statuses).filter(id => current.statuses[id] === "Completed" &&
      next.statuses[id] !== "Completed").length;
    const cleared = Object.keys(current.statuses).filter(id => current.statuses[id] === "In Progress" &&
      !next.statuses[id]).length;
    const path = next.selectedPath ? paths[next.selectedPath].title : "Complete Beginner (default)";
    return "Completed topics added: " + added + ". Completed topics removed: " + removed +
      ". In-progress marks cleared: " + cleared + ". Resume path: " + path + ".";
  }

  function readLocal(storage, topics, paths) {
    let saved;
    try { saved = JSON.parse(storage.getItem(statusKey)); } catch (error) {
      if (!(error instanceof SyntaxError)) throw error;
    }
    const statuses = Object.fromEntries(Object.keys(topics)
      .filter(id => saved && Object.hasOwn(saved, id) && values.includes(saved[id]))
      .map(id => [id, saved[id]]));
    const path = storage.getItem(pathKey);
    return {statuses, selectedPath: validPath(path, paths) ? path : null};
  }

  function writeLocal(storage, current) {
    storage.setItem(statusKey, JSON.stringify(current.statuses));
    if (current.selectedPath) storage.setItem(pathKey, current.selectedPath);
    else storage.removeItem(pathKey);
  }

  function routeProgress(path, topics, statuses) {
    const pending = path.closure.filter(id => statuses[id] !== "Completed");
    return {
      completed: path.closure.length - pending.length,
      remaining: pending.length,
      hours: pending.reduce((total, id) => total + topics[id].hours, 0),
      next: pending[0],
    };
  }

  function bindControls(state, saveBlob) {
    const fileInput = document.getElementById("import-progress");
    const panel = document.getElementById("import-preview");
    const status = document.getElementById("import-status");
    const summary = document.getElementById("import-summary");
    let pending = null;
    let request = 0;
    const mode = () => panel.querySelector("[name=import-mode]:checked").value;

    function discard(message) {
      request++;
      pending = null;
      fileInput.value = "";
      panel.hidden = true;
      status.textContent = message;
    }

    function review() {
      if (pending) summary.textContent = previewImport(state.current(), pending, mode(), state.paths);
    }

    fileInput.addEventListener("change", async () => {
      const file = fileInput.files[0];
      discard(file ? "Reading backup…" : "");
      const token = request;
      if (!file) return;
      try {
        if (file.size > 64 * 1024) throw new Error("The backup is larger than 64 KB.");
        const text = await file.text();
        if (token !== request) return;
        pending = parseBackup(text, state.topics, state.paths);
        panel.querySelector("[value=merge]").checked = true;
        panel.hidden = false;
        status.textContent = "Backup checked. Review the changes before applying.";
        review();
      } catch (error) {
        if (token === request) discard(error.message);
      }
    });
    panel.addEventListener("change", review);
    document.addEventListener("curriculum-progress", review);
    document.getElementById("apply-import").addEventListener("click", () => {
      if (!pending) return;
      state.apply(projectImport(state.current(), pending, mode()));
      discard("Progress imported.");
      fileInput.focus();
    });
    document.getElementById("cancel-import").addEventListener("click", () => {
      discard("Import cancelled. Progress is unchanged.");
      fileInput.focus();
    });
    document.getElementById("export-progress").addEventListener("click", () => {
      const text = JSON.stringify(makeBackup(state.current()), null, 2) + "\n";
      saveBlob(new Blob([text], {type: "application/json"}), "testneural-academy-progress.json");
      status.textContent = "Progress backup download requested.";
    });
    document.getElementById("reset-progress").addEventListener("click", () => {
      if (!window.confirm("Reset all saved topic progress and your selected path in this browser?")) return;
      discard("Progress reset.");
      state.apply({statuses: {}, selectedPath: null});
    });
  }

  return {duration, parseBackup, makeBackup, projectImport, previewImport, readLocal, writeLocal,
          routeProgress, bindControls};
})();
if (typeof module === "object" && module.exports) module.exports = LearningProgress;
