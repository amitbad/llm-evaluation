(() => {
  "use strict";

  const page = new URL(window.location.href);
  const academy = page.origin === "https://llmacademy.testneural.in";
  const preference = "testneural_analytics_optout";
  const parameter = "analytics_optout";
  const beaconURL = "https://static.cloudflareinsights.com/beacon.min.js";
  const noticeID = "testneural-analytics-status";
  const forward = document.currentScript?.dataset.analyticsForward;
  const action = academy ? page.searchParams.get(parameter) : null;

  if (action === "1" || action === "0") {
    if (document.getElementById(noticeID)) return;
    const disable = action === "1";
    let message;
    try {
      const storage = window.localStorage;
      if (disable) storage.setItem(preference, "true");
      else storage.removeItem(preference);
      if (storage.getItem(preference) !== (disable ? "true" : null)) {
        throw new Error("Analytics preference was not saved");
      }
      message = disable
        ? "Analytics is disabled in this browser."
        : "Analytics is enabled in this browser. Future page loads may be tracked.";
    } catch {
      message = disable
        ? "Analytics was skipped for this page, but persistent exclusion could not be saved. Future page loads may be tracked."
        : "The analytics preference could not be cleared. Analytics was skipped for this page.";
    }
    page.searchParams.delete(parameter);
    try {
      window.history.replaceState(window.history.state, "", page.href);
    } catch {
      // The preference applies even if the browser disallows URL cleanup.
    }
    const notice = document.createElement("p");
    notice.id = noticeID;
    notice.setAttribute("role", "status");
    notice.textContent = message;
    document.body.prepend(notice);
    return;
  }

  // Redirect documents forward to the reader or homepage without adding a page view.
  if (forward) {
    const target = new URL(forward, page);
    target.search = page.search;
    if (page.hash) target.hash = page.hash;
    window.location.replace(target.href);
    return;
  }

  if (!academy || document.getElementById(noticeID)) return;
  try {
    if (window.localStorage.getItem(preference) === "true") return;
  } catch {
    // If we cannot read the preference, err on the side of exclusion.
    return;
  }

  if (document.querySelector('script[data-cf-beacon], script[src="' + beaconURL + '"]')) return;
  const beacon = document.createElement("script");
  beacon.async = true;
  beacon.src = beaconURL;
  beacon.setAttribute("data-cf-beacon", JSON.stringify({token: "b102aa6f36fe41628f59bd295681e891"}));
  document.head.append(beacon);
})();
