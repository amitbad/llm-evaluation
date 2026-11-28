# Static hosting and release checks

TestNeural LLM Academy is a static site. Serve the academy homepage, curriculum, published lesson examples, and their assets directly from the web server. The learning interface needs no backend, database, or build service.

## Validate a release

From the repository root, run the generator and check for synchronization before committing the generated pages. The validator also checks that local links and embedded assets resolve within the public file set.

```bash
python3 docs/generate_master_curriculum.py
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
```

For a host that serves a separate release directory, the validator can copy the allowlisted files to an empty directory outside the checkout. Paths are preserved for relative links and the published exercise workbook.

```bash
python3 scripts/validate_static_site.py --stage /path/to/empty-release-directory
```

## Public file boundary

Expose only the pages, assets and exercise workbook accepted by the validator. A web server serving directly from `docs/` needs an explicit URL allowlist and a mapping for the workbook. Keep site configuration, deployment scripts, SSH keys, certificate material, and internal project files private.

Production uses a dedicated NGINX virtual host and Let's Encrypt. Operators keep the VPS runbook and deployment files outside this repository. Validate NGINX before a reload, verify the academy over HTTPS after a release, and record the release revision for rollback.

## Cloudflare Web Analytics

The shared `/assets/analytics.js` loader runs only on the Academy's HTTPS origin. It checks this browser's preference before adding one asynchronous beacon with the public site token. Quick Learning and Complete Course use the same generated `/lesson-mNN-tNN.html` addresses for the same lesson. The addresses keep the original fragment to restore the reading mode and use the existing curriculum document. Cloudflare can report these visits by Path through its single-page navigation handling. The homepage and lesson address forwarding pages let the destination handle measurement, so the forwarding step adds no extra beacon. [Cloudflare navigation tracking](https://developers.cloudflare.com/web-analytics/get-started/web-analytics-spa/) · [Cloudflare dimensions](https://developers.cloudflare.com/web-analytics/data-metrics/dimensions/)

1. In **Cloudflare Dashboard → Web Analytics → Manage site**, check `llmacademy.testneural.in` and select **Enable with JS Snippet installation** when the site is proxied. For a DNS-only site, confirm the existing manual snippet setup. Check the live page source for any separately injected Cloudflare beacon. Owner exclusion is only reliable for the repository loader. An edge-injected beacon can run independently and must be disabled. [Cloudflare setup](https://developers.cloudflare.com/web-analytics/get-started/)
2. Commit and push the analytics change, then deploy with the existing static release runbook. Confirm that the production allowlist serves `/assets/analytics.js`, `/full-results.html` and the generated `/lesson-mNN-tNN.html` files. The published report contains the original report with the loader added at generation time. Verify that a direct lesson URL and a refresh of a guided lesson both return to the intended content.
3. On **each** Mac or mobile browser you use, open the [exclusion URL](https://llmacademy.testneural.in/?analytics_optout=1). Confirm that the page reports exclusion and drops the query parameter. In Chrome DevTools or Safari Web Inspector, check Local Storage for `testneural_analytics_optout` equal to `true`. Refresh and open two lessons with the Network log preserved. Expect no requests for `beacon.min.js` or `cdn-cgi/rum`. For mobile use remote inspection when available. Reload or close Academy tabs that were open before you activated exclusion.
4. In a separate browser profile with no exclusion and with content blocking disabled for this check, visit the site, open two different lessons, refresh one, then navigate away with the Network log preserved. Check for the beacon script and RUM delivery. In the private **Web Analytics** dashboard for the hostname, check **Visits**, **Page views**, and the **Path** dimension for the two lesson addresses. Data can take a few minutes to appear. [Cloudflare setup](https://developers.cloudflare.com/web-analytics/get-started/) · [Cloudflare dimensions](https://developers.cloudflare.com/web-analytics/data-metrics/dimensions/)

The [re-enable URL](https://llmacademy.testneural.in/?analytics_optout=0) clears the browser preference. Tracking can resume on a subsequent page load. Preferences are per browser profile and may disappear in private browsing or after clearing site data. If storage cannot be read, the loader skips tracking. If a preference cannot be saved or cleared, the page displays a warning. The preference only affects future events from this loader. Existing analytics and server or CDN logs are unaffected. The loader adds no cookies, visitor identifiers or fingerprinting and sends no browser storage values. Reports stay in the owner's Cloudflare dashboard.

No CSP is declared in the current homepage markup or its checked HTTPS response headers. If an applicable policy is introduced, keep the existing rules and permit the Cloudflare beacon in `script-src` and `https://cloudflareinsights.com` in `connect-src` for manual installation. [Cloudflare CSP guidance](https://developers.cloudflare.com/web-analytics/faq/#what-do-i-need-to-add-to-my-content-security-policy-csp)
