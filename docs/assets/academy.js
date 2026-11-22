(() => {
  const root = document.documentElement;
  const themeKey = "testneural-academy-theme";
  const preferred = window.matchMedia("(prefers-color-scheme: dark)");
  let selection;
  try { selection = localStorage.getItem(themeKey); } catch { /* File storage can be unavailable. */ }

  function applyTheme() {
    const theme = ["light", "dark"].includes(selection) ? selection : preferred.matches ? "dark" : "light";
    root.dataset.theme = theme;
    for (const button of document.querySelectorAll("[data-theme-toggle]")) {
      button.textContent = theme === "dark" ? "Light theme" : "Dark theme";
      button.setAttribute("aria-label", theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
  }

  async function copyCode(text) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // Some local files and browsers restrict the Clipboard API.
    }

    const previousFocus = document.activeElement;
    const field = document.createElement("textarea");
    field.value = text;
    field.readOnly = true;
    field.className = "lesson-copy-fallback";
    document.body.append(field);
    try {
      field.focus({preventScroll: true});
      field.select();
      if (!document.execCommand("copy")) throw new Error("Clipboard copy failed.");
    } finally {
      field.remove();
      previousFocus?.focus({preventScroll: true});
    }
  }

  function setupCopyButtons() {
    for (const block of document.querySelectorAll(".lesson-code")) {
      const toolbar = block.querySelector(".lesson-copy-toolbar");
      const button = block.querySelector(".lesson-copy-button");
      const status = block.querySelector(".lesson-copy-status");
      const code = block.querySelector("pre > code");
      let copying = false;
      let reset;
      button.addEventListener("click", async () => {
        if (copying) return;
        copying = true;
        window.clearTimeout(reset);
        button.textContent = "Copy Code";
        status.classList.remove("is-error");
        status.textContent = "";
        try {
          await copyCode(code.textContent);
          button.textContent = "✓ Copied!";
          status.textContent = "Code copied to clipboard.";
          reset = window.setTimeout(() => {
            button.textContent = "Copy Code";
            status.textContent = "";
          }, 2000);
        } catch {
          status.classList.add("is-error");
          status.textContent = "Could not copy the code. Select it and copy it manually.";
        } finally {
          copying = false;
        }
      });
      toolbar.hidden = false;
    }
  }

  function setup() {
    setupCopyButtons();
    if (document.body.classList.contains("academy-lesson")) {
      const header = document.createElement("header");
      header.className = "lesson-header";
      header.innerHTML = '<a class="academy-brand" href="index.html"><img src="assets/branding/icon-48.png" width="32" height="32" alt=""><span>TestNeural LLM Academy</span></a>' +
        '<nav aria-label="Learning modes"><a href="master-curriculum.html#quick">Quick Learning</a><a href="master-curriculum.html#detail">Complete Course</a></nav>' +
        '<button type="button" data-theme-toggle>Dark theme</button>';
      header.querySelector("img").addEventListener("error", event => { event.target.hidden = true; });
      document.body.prepend(header);
      const footer = document.createElement("footer");
      footer.className = "academy-footer lesson-footer";
      footer.innerHTML = '<a href="index.html">TestNeural LLM Academy</a><span>Developed by: Amit Baderia</span>';
      document.body.append(footer);
      for (const table of document.body.querySelectorAll("table")) {
        const region = document.createElement("div");
        region.className = "lesson-table";
        region.tabIndex = 0;
        region.setAttribute("role", "region");
        region.setAttribute("aria-label", table.caption?.textContent.trim() || "Lesson table");
        table.before(region);
        region.append(table);
      }
    }

    applyTheme();
    preferred.addEventListener("change", applyTheme);
    window.addEventListener("storage", event => {
      if (event.key !== themeKey && event.key !== null) return;
      selection = event.key === themeKey ? event.newValue : null;
      applyTheme();
    });

    for (const button of document.querySelectorAll("[data-theme-toggle]")) {
      button.addEventListener("click", () => {
        selection = root.dataset.theme === "dark" ? "light" : "dark";
        try { localStorage.setItem(themeKey, selection); } catch { /* Apply for this visit. */ }
        applyTheme();
      });
    }

    const sidebar = document.querySelector(".academy-sidebar");
    if (sidebar) {
      const mobile = window.matchMedia("(max-width: 960px)");
      sidebar.open = !mobile.matches;
      mobile.addEventListener("change", event => { sidebar.open = !event.matches; });
      sidebar.addEventListener("click", event => {
        if (mobile.matches && event.detail > 0 && event.target.closest("a[href]")) sidebar.open = false;
      });
    }
  }

  applyTheme();
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup, {once: true});
  else setup();
})();
