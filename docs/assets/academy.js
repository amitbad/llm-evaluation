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

  function setup() {
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
