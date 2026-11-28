# Remaining V1.0 issues

Severity uses the original curriculum audit's P0–P3 scale. Items marked pending acceptance lack completion evidence. The two confirmed public failures are release blockers for the intended snapshot.

| ID | Severity and state | Evidence and impact | Owner and closure criteria |
| --- | --- | --- | --- |
| F-001 | **P0 · Locally fixed, deployment pending** | The M18-T01 alias responds 200 and matches local bytes. Its target, the public curriculum, matches `97f04a1` and contains the outline. The current candidate serves four Python labs and the full lesson locally. | Release owner publishes the reviewed snapshot. Verify the public material body, four labs and surrounding M18 navigation in Quick Learning and Complete Course. Record response hashes. |
| Deployment parity | **P1 · Confirmed public mismatch** | The curriculum, shared CSS, published-example Read Aloud script and concepts page serve older bytes. The public experience therefore lacks verified local remediation and speech changes even where a route returns 200. | Release owner verifies the candidate file set, deployed revision and cache behavior. Compare public file hashes after approved rollout. |
| RAG workbook | **P1 · Confirmed public 404** | The expected workbook is in the repository, passes XLSX ZIP integrity and is in the 85-file allowlist. Its exact public URL returns 404. The catalog's pinned GitHub artifact responded 200 and is a separate route. | Hosting owner confirms the narrow workbook mapping in the dedicated virtual host. Require HTTPS 200 and a downloaded XLSX whose hash matches the approved file. |
| Browser and accessibility acceptance | **P1 · Pending** | Mock and source checks cover the learning modes, Read Aloud, roadmap, progress and Copy Code. Real speech quality, visual highlighting, responsive layout, exports, clipboard, storage and browser console remain unobserved. | Browser reviewer executes the checklist and records macOS Chrome and Safari plus mobile results. Retest any blocking failures. |
| Teaching review and beginner pilot | **P1 · Pending** | The repository's teaching standard requires explicit human approval. The preparation packet and offline labs work in automated replay. There is no learner observation or review sign-off in the assessed evidence. | Teaching reviewer records approvals, and a first-time learner independently completes the sampled editor and terminal exercises. Record all assistance and decisions. |
| Hosted CI acceptance | **P2 · Pending for optional integration** | Batch 3 validates the M13-T02 workflow shell and offline exit codes. No hosted Actions run or branch-protection enforcement was observed. | In a training repository, run green, red and stale captures. Check the required status source and retained evidence artifact. Keep the walkthrough labeled as locally verified until then. |

## Reconciliation against the original register

| Batch | Findings | Current assessment |
| --- | --- | --- |
| 1 · `35a35d4` | F-001, F-002, F-003, F-005 | F-001 locally fixed and pending deployment. Missing retests stay unverified, critical wrong-order writes retain criticality, and lost dispatches retain the planned denominator. The M12 regression suite passed. |
| 2 · `3f53f94` | F-004, F-006, F-007, F-008 | Resolved locally within the documented scope. Retained-history controls, independent judge predictions, historical-evidence caveats and terminal preparation remain in the candidate. Public publication and novice acceptance are separate evidence. |
| 3 · `8586a07` | F-009, F-010, F-011, F-012 | Resolved locally. The runner guide, candidate-bound gate, release terminology crosswalk and instructor run sheet are present. Seven focused tests passed. The optional hosted check and instructor pilot still need acceptance. |

Sources are the [original findings](../final-curriculum-audit/FINDINGS.md) and the [Batch 1](../final-curriculum-audit/REMEDIATION_BATCH_1.md), [Batch 2](../final-curriculum-audit/REMEDIATION_BATCH_2.md) and [Batch 3](../final-curriculum-audit/REMEDIATION_BATCH_3.md) reports. The original findings and audit evidence remain intact.
