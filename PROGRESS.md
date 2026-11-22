# Project progress

Last updated **2026-11-22**. The last verified live release is `aa01ca7`. The first full lesson, M02-T01, is ready for local review.

## Implemented milestones

| Milestone | Current state |
| --- | --- |
| Repository audit and master curriculum | The audit and authoritative curriculum are in the repository. The curriculum has 18 modules, 53 topics, and seven learning paths. Estimates are 238 core hours, 54.5 elective hours, and 7 separate optional preparation hours. |
| Learning paths and roadmap | Quick Learning and Complete Course share the curriculum data and browser-local progress. The roadmap supports dependency views and diagram and plan downloads. |
| Academy redesign and deployment preparation | Approved branding, the dashboard, legacy example-page navigation, and static validation are in the repository. The production script, NGINX files, and runbook are maintained outside the public checkout. |
| Layout and progress refinements | Responsive layout rules, formatted duration displays, Continue Learning, and JSON progress export and import are implemented. |
| Navigation and project tracking | The five primary destinations are consistent across the homepage and curriculum. Learning Paths is inside Quick Learning. Instructor Resources now groups Existing Repository Coverage and Teaching Plan. Project tracking and its maintenance rules are documented. |
| Navigation icons | The homepage and curriculum each show five decorative 18-pixel SVG icons beside the primary navigation labels. Both pages use the same icon definitions and existing theme colors. |
| Production Stage A | Prepared a private handoff for the dedicated GitHub key, initial clone, academy vhost, certificate, external deployment script, and HTTPS checks. The five icons now have distinct colors from the existing blue, cyan, and violet palette. |
| Clean Git history | Fetched GitHub `main` and synchronized local `main` to `aa01ca7`. Preserved three local-only commits on `archive/pre-clean-main-72c2e33`. The old and new tips had identical files, and both worktrees were retained. |
| Website QA | Fixed curriculum tab keyboard navigation, mobile keyboard activation, the skip link, dark hover icon contrast, and theme button labels. Updated main-page search metadata and added semantic headings to the Concepts Reference. |
| Guided learning | All seven paths show an ordered lesson list and progress. Path-specific lesson links open the shared material in place, with breadcrumbs, Previous and Next, completion, and a return link. Sharing and roadmap downloads are under More Options. |
| Learning Navigator | Guided lessons have a floating preview or compact icon. The full map shows path progress, real prerequisite arrows and separate order lines. Escape and Minimize restore the launcher, and Close leaves a reopen button. |
| Guided lesson reading | Lessons have a responsive reading layout, a prominent title and progress indicator, structured activities, and collapsed time and technical details. Empty prerequisites are omitted. The existing module goals and topic text are reused and the outlines are labeled. |
| First full reference lesson | M02-T01 now teaches evaluation design through one fictional bank scenario, three worked assessments, an offline Python lab, four practice exercises with solutions, and eight knowledge checks with answers. Both learning modes use the same chapter. |
| Lesson code copying | Generated executable fences have a shared Copy Code button with success and failure feedback. Console transcripts remain plain. |
| Beginner Python tutorial | M02-T01 now builds from printing two saved amounts to a seven-step offline evaluation report. Each step includes an independent snippet, one edit to try, both expected outputs, and a checkpoint. |
| Textbook layout | Both reading modes give code, tables, and examples more room while keeping prose line lengths readable. Setup, outputs, and solutions are collapsible. The guided Navigator opens from a compact control aligned to the left sidebar. |

## Tested

- Non-browser checks passed for deterministic HTML synchronization, the 29 public files, and Bash syntax for the private deployment script and manual command blocks.
- Static vhost route checks covered the public files and checked that internal paths are excluded. An isolated Git fixture confirmed that the external script rejects an unreviewed SHA and dirty checkout, and fast-forwards to the validated commit.
- Static checks confirmed the primary navigation order, destinations, and Resources grouping. The generated curriculum data matches the pre-change payload, including all path totals and dependencies.
- JavaScript checks using a simulated DOM covered all seven path links, progress across modes and reloads, import and export, roadmap controls, and downloads.
- Static checks confirmed icon order, size, and decorative accessibility markup on both pages. Link labels, IDs, and destinations were preserved, and both pages regenerated byte-for-byte.
- QA rechecked the 29 public files, HTML titles, labels and IDs, JavaScript syntax, all 18 modules and 53 topics, all seven path sequences and hours, and simulated keyboard, roadmap, progress, and import/export interactions. The embedded curriculum data was byte-identical to the release.
- QA checked the CSS cascade for dark sidebar hover. Stage A's contrast sampling used the wrong hover background. The corrected check shows the lowest ratio improved from 1.51:1 to 7.59:1.
- Read-only HTTPS checks confirmed the live homepage and curriculum match `aa01ca7` byte-for-byte. Root-level Concepts Reference, CSS, JavaScript, and Test 2 URLs responded. The two exercise resources, legacy `/docs/` URLs, `/robots.txt`, and `/sitemap.xml` returned 404. The academy owner can review the exact scope in the [bug tracker](BUG_TRACKER.md).
- Guided navigation tests walked every path sequence, checked direct links, refresh, boundaries and return to Complete Course, and verified shared progress and version-one backups. Run them with `node --test scripts/test_guided_navigation.cjs`. The generator check, static site validation, and simulated roadmap and progress regression checks passed.
- Navigator tests checked all seven map layouts against the curriculum, simulated progress updates, in-path node navigation, focus, zoom and pan, and verified the mobile and reduced-motion CSS rules. Native dialog and responsive rendering still need the owner's browser acceptance.
- Reading-layout checks verified the section order and disclosures for all 53 outlines, restoration of module objectives on return to Complete Course, path progress counts, and generator and public-site validation.
- Ran the M02-T01 Python program on Python 3.12.7 for the baseline and both documented edits. All three console transcripts matched exactly. The generated chapter is shared across learning modes, the remaining 52 topic renderings and curriculum data are unchanged, and the 4.5-hour estimate stays in place for the full set of activities. It has not been timed with learners.
- Non-browser copy tests verified exact text, success reset, clipboard fallback and error feedback, and that transcripts have no button. Native clipboard permissions and sticky placement still need a manual check.
- Ran all seven revised M02-T01 snippets and their seven learner edits on Python 3.12.7. All 14 transcripts matched exactly. The rest of the lesson, the remaining topics, and the generated navigation and progress code were unchanged.
- Static checks verified the expanded reading layout markup, collapsed secondary sections, unchanged lesson text, code and outputs, and the sidebar launcher. Non-browser tests covered Copy Code, path navigation, progress, and the Navigator dialog and camera behavior.

## Manually verified

At Stage A the owner reported that DNS was verified, NGINX 1.24.0 and Certbot 5.10.0 were installed, and `sudo nginx -t` passed with pre-existing warnings. This QA verified public HTTPS responses without inspecting VPS configuration or renewing certificates. Manual browser acceptance for the current QA changes remains pending.

## Pending

1. Restore the two public exercise URLs and consider redirects from old `/docs/` links. These are production follow-ups for the owner. The QA update did not deploy or change the VPS.
2. Review the homepage and curriculum in desktop and mobile browsers using the [README checklist](README.md#manual-browser-checklist). In a guided lesson, open the Navigator, tab through controls and nodes, pan and zoom, minimize with Escape, then reopen to check the saved view. Confirm the X leaves a reopen icon, node selection stays in the path, and the floating control stays clear of lesson actions at small widths.
3. Add search metadata to the individual lesson pages and coordinate sitemap and crawler policy with the public URL allowlist.
4. Ask a beginner to try M02-T01 and record where they pause or need help. Use that feedback and the [M02-T01 chapter](docs/lessons/m02-t01.md) when expanding the remaining outlines. Check reading width, code-block scrolling, and disclosure controls in both themes.

Track confirmed issues and separate verification gaps in [BUG_TRACKER.md](BUG_TRACKER.md).
