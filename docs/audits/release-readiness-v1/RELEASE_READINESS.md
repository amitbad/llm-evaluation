# TestNeural LLM Academy V1.0 release readiness

**Recommendation · NO-GO for the public V1.0 release.** The local candidate passes the automated curriculum, experiment and package checks. Production is still serving the M18-T01 outline and returns HTTP 404 for the allowlisted RAG workbook. Browser acceptance, teaching review and a first-time learner pilot also remain open.

## Candidate and scope

- Assessed `main` at `3cd4ddba2a7dbc88748b4009b3a2f3ea3b1cd6c5`. At the start the index was empty. `PROGRESS.md` had unrelated local edits, and five historical audit reports were untracked. Those files were used as background and preserved.
- Batch 1 is committed at `35a35d4`, Batch 2 at `3f53f94` and Batch 3 at `8586a07`. The Read Aloud implementation and follow-up are committed at `c59d1a0` and `3cd4ddb`. The roadmap scaling and image-export fixes are committed at `4eb192f` and `97f04a1`.
- Reviewed the authoritative curriculum, teaching standard, project context, progress records, final audit findings, topic scorecard, red-team and experiment audits, all three remediation reports, reader and roadmap source and tests, and the public deployment notes. This assessment adds four reports. It makes no application, lesson, deployment or audit-history changes.

## Release gate matrix

| Gate | Status | Evidence | Required action |
| --- | --- | --- | --- |
| Curriculum completeness | **Pass** | 18 modules, 53 matching Markdown and static lesson IDs, 53 full local lesson bodies, zero outline placeholders, and seven paths. Exact embedded data matches the authoritative curriculum, including paths and prerequisites. | Keep the approved sources and generated files together. |
| Technical correctness | **Pass** | Existing audit evidence and fresh local replay agree. 87 Node tests, 34 Python regression tests and 350 offline lesson invocations behaved as expected. Local validator resolved public links and assets. | Preserve the tested revision. Test optional integrations separately if they enter release scope. |
| Audit remediation | **Pending** | F-002 through F-012 are verified within their local scope. F-001 remains open in production. Batch 3 is committed and its candidate-bound gate was rerun. | Resolve F-001. Rehearse hosted CI enforcement in a training repository if offering it as a verified walkthrough. |
| Read Aloud | **Pending** | 26 mock tests pass on the candidate. Public reader and CSS match an earlier revision. | Accept Chrome and Safari narration, voice discovery, highlighting and fallback on the intended candidate and after release. |
| Learning Roadmap | **Pending** | 24 tests pass for fullscreen, inspector, mandatory closure, export geometry, SVG/PNG, viewport independence, Cancel and Escape. | Inspect real downloads and fullscreen layout in a browser. |
| Progress tracking | **Pending** | Guided navigation tests cover shared completion, resume, reload and version-one backup preservation. | Verify browser storage, mode switching, and export/import in a disposable profile. |
| Public M18-T01 | **Fail** | The public curriculum matches `97f04a1` and serves one outline with zero Python blocks for M18-T01. The candidate has the full lesson with four blocks. | Publish the approved snapshot through the existing operator workflow and verify the body through both learning modes. |
| Deployment | **Fail** | Local package stages successfully. One of 85 public URLs returns 404 and four respond with older bytes. | Confirm the dedicated host's workbook mapping and release revision, then recheck public content and rollback readiness. |
| Browser acceptance | **Pending** | Static links, keyboard states and core interactions have code or automated coverage. No browser session was run for this assessment. | Run the desktop and mobile acceptance checklist and record browser, revision and any console errors. |
| Human teaching review | **Pending** | The teaching standard requires explicit review. The repository records rewritten lessons awaiting review. | Record qualified reviewers' findings and approval against the release revision. |
| Beginner learner pilot | **Pending** | Preparation packet and lesson outputs replay. There is no recorded first-time learner pilot. | Observe an independent learner from editor entry through the first terminal handoff. |

**Totals · 2 Pass, 2 Fail, 7 Pending.** The technical pass covers the local offline candidate.

## Verification evidence

| Check | Observed result |
| --- | --- |
| Generation and staging | Generator check passed. 56 outputs matched across two isolated rebuilds of HEAD and the worktree. The static validator passed for 85 public files. Two temporary staging runs produced the same bytes. |
| Curriculum and references | All authored IDs match the authoritative topic set and the 53 generated addresses. The five destinations, concept reference, preparation packet, instructor resource, lesson links and assets are present locally. The generator checks path totals and mandatory prerequisites. |
| Node regression suite | 87 passed, zero failures and skips. This includes 19 guided navigation, 26 Read Aloud, 24 roadmap, 7 analytics, 7 original experiments, and 4 Copy Code tests. |
| Python audit regressions | 19 M12, 8 Batch 2 and 7 Batch 3 tests passed. M12 checks preserve authorization, retest uncertainty and dispatch coverage. M18 reference changes leave saved predictions unchanged. Batch 3 confirms PASS, BLOCK and rejection of stale or mismatched captures. |
| Lesson replay | 347 standalone Python blocks across 53 lessons. 344 matched adjacent text transcripts after trimming outer whitespace. The M14-T02 workbook and M14-T03 saved-measurement outputs separately matched their 24- and 13-line transcripts. M14-T01 replay, repair and the intended lookup failure matched all three documented outcomes. A second M14-T03 invocation made fresh local timings. Its fixture task counts and cost were stable. Across 350 invocations, 349 exited zero and the intentional lookup failure exited 1. |
| Original experiments | All 15 mapped across 49 lessons. Zero unresolved source paths. All 55 distinct catalogued sources and artifacts exist locally and at the pinned archive revision. Fresh replay used deterministic lesson fixtures and saved captures. Live models, paid services and hosted integrations were outside this run. |
| External links and public files | 42 rendered HTTPS links responded 200, including 41 archive links and the online Python editor. The separate localhost link is for the optional local viewer. Of 85 allowlisted public URLs, 84 responded 200 and 80 matched local bytes. All 53 lesson address files matched. The M18-T01 address forwards to the stale master document. |
| Change hygiene | `git diff --check` passed. The existing working-tree changes and empty index were preserved. |

The checked-in commands ran on Python 3.12.7 and Node 24.12.0.

```bash
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
python3 docs/generate_master_curriculum.py --experiment-coverage
node --test scripts/test*.cjs
python3 scripts/test_m12_remediation.py
python3 scripts/test_audit_batch2.py
python3 scripts/test_audit_batch3.py
git diff --check
```

Public counts and snapshot hashes are in [deployment verification](DEPLOYMENT_VERIFICATION.md). Run the [manual acceptance checklist](MANUAL_ACCEPTANCE_CHECKLIST.md) and close the [remaining issues](REMAINING_ISSUES.md) before declaring V1.0 released.
