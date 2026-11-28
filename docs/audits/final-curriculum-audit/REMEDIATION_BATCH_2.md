# Final curriculum audit remediation · Batch 2

Batch 2 addresses four P1 findings. The original audit reports preserve the pre-remediation evidence.

## F-006 · Independent judge predictions

**Root cause.** The advanced judge lab filled in every prediction without an override using the expected label. Changing the answer key could change what the program called the judge’s original prediction.

**Correction.** M18-T01 uses explicit synthetic predictions per version, separate from scoring labels and criticality. The replay serializes and hashes each capture set before scoring. Contract validation still runs when labels are unavailable. Calibration snapshots have separate IDs and carry judge version and threshold. The lesson distinguishes trusted policy evidence from disclosing an answer key to a deliberately reference-aware grader.

**Verification.** The repaired fixture scored 12/12. Flipping A01’s reference produced 11/12 and one false positive with identical raw captures and SHA-256. Removing all labels retained twelve predictions, zero scored comparisons and REVIEW. Reusing v2 calibration for the repaired judge scored 12/12 and returned REVIEW. Regression tests rebuild every snapshot without reference, criticality, evidence or calibration globals, inspect predictor and serializer lookups, and compare deterministic JSON exports. The two critical false PASS controls still BLOCK at 11/12.

**Status.** Resolved in the deterministic lab. Human teaching review, live-model evaluation and publication remain pending. [M18-T01](../../lessons/m18-t01.md) · [Regression tests](../../../scripts/test_audit_batch2.py)

## F-004 · Exercise a defense across retained history

**Root cause.** The core security lab evaluated prepared outcomes. Learners could identify a broken boundary but did not exercise a control that preserved provenance across turns.

**Correction.** M12-T02 now runs a two-turn offline decision mock. It retains event IDs with normalized inert labels. The checked mode obtains each event’s source from separate fixture metadata. Missing or unrecognized provenance is a REVIEW case. A held-out legitimate control and controlled label edit accompany the comparison.

| Boundary coverage added | Observed unchecked → checked | Verification |
|---|---|---|
| Retained history and label normalization | Retained customer note ALLOW → DENY | A case and spacing edit preserved the denial. |
| Legitimate verification | ALLOW → ALLOW | The held-out legitimate control kept its result. Removing its source changed the checked outcome to REVIEW. |
| Missing provenance | ALLOW → REVIEW | The report retained the unknown without crediting a confirmed defense or allowing the dummy action. |

**Status.** Resolved for the scoped offline transfer skill. The fixture uses no network, scanner, model, external tools or writes. Its observed behavior does not measure defenses against a live target. [M12-T02](../../lessons/m12-t02.md) · [Regression tests](../../../scripts/test_audit_batch2.py)

## F-007 · Archive interpretation and refusal scoring

**Root cause.** The reference attributed a historical framework score difference to calibration despite timeout-affected values and differing batch conditions. Adjacent guidance collapsed measured results and missing evidence, then told learners to exclude refusals categorically.

**Correction.** The reference presents the reported 84% and 24% as a non-controlled comparison. It distinguishes scored failures, execution errors, unscorable cases and inapplicable criteria. An illustrative example reports 6/8 valid passes with 8/10 coverage. The reference links to the appropriate M09 and M11 lessons and separates refusal appropriateness from factual-answer criteria.

**Verification.** Tests check the qualification, categories and lesson links. Static validation resolves their destinations. Historical Test 9 and Test 11 walkthroughs match HEAD byte for byte.

**Status.** Resolved in the local site source. Browser and deployment checks remain pending. [Concepts reference](../../concepts.html#metric-calibration) · [Regression tests](../../../scripts/test_audit_batch2.py)

## F-008 · Preparation before the first terminal lab

**Root cause.** The readiness table described starter tasks without supplying a complete runnable handoff. M14-T01 introduced installation and a second terminal before the dependency-free replay.

**Correction.** P01–P05 now link to a preparation packet with an isolated scratch workflow, JSONL cases, captured HTTP requests and responses, and a standard-library script. Learners repair a misspelled relative path and distinguish an incorrect answer from an unavailable response. M14-T01 links to the packet, adds repository-root recovery and puts no-export runs before the optional viewer.

**Verification.** The scratch run reproduced the case.jsonl error at exit 1. The corrected run produced 200 PASS, 200 FAIL and 503 REQUEST_ERROR. M14’s offline replay printed FAIL_MISSING_REQUIRED_SEARCH, repair printed PASS_SEARCH_AND_SAFE_ESCALATION, and injected lookup failure exited 1 before a quality result. Running from an empty directory reproduced the documented recovery prompt. Navigation and Copy Code tests covered the generated packet and its exact code.

**Status.** The materials and offline handoff passed automated verification. A first-time learner pilot and browser acceptance remain pending. [Preparation source](../../preparation.md) · [M14-T01](../../lessons/m14-t01.md)

## Validation and remaining work

- Eight Batch 2 Python tests and all 19 Batch 1 M12 tests passed. The M12 checks compared 25 baseline and 12 variant transcripts in fresh processes. Batch 2 also compared all four M18-T01 transcripts, two report exports, the terminal exercises and the offline trace results.
- All 79 Node tests passed, including 19 navigation and 24 roadmap tests. Generator synchronization, validation of 85 public files, original-experiment coverage and diff checks passed. Two generations produced 56 identical outputs. The graph payload was byte-identical to HEAD with 53 authored topics, 18 modules and seven paths.
- The public curriculum still serves an M18-T01 outline. The local generated curriculum contains the complete corrected lesson. F-001 remains open for approved deployment and public acceptance. [Public curriculum](https://llmacademy.testneural.in/master-curriculum.html)

## Changed files and manual checks

- Lessons are M12-T02, M14-T01 and M18-T01. Site files are docs/preparation.md, docs/concepts.html, docs/generate_master_curriculum.py, docs/learning_modes.js and docs/master-curriculum.html.
- Tests are scripts/test_audit_batch2.py, scripts/test_copy_code.cjs and scripts/test_guided_navigation.cjs. This report, PROJECT_CONTEXT.md and PROGRESS.md record the status.
- Ask a first-time learner to follow P01–P05 from Quick Learning, repair the deliberate path error and run the no-export trace from a clean checkout. Have them distinguish a failed answer from a request error.
- Verify Copy Code, M18-T01 in both learning modes, and complete and selected roadmap downloads in desktop and fullscreen views. Repeat public availability checks after approved deployment.
- Finish F-001 acceptance, then prioritize P2 findings F-009 through F-012. Academy Version 1.0 remains pending.
