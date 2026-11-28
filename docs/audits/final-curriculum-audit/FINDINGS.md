# Prioritized findings

**Historical register.** Finding IDs, severities, observations and acceptance criteria reflect the original audit. Line numbers refer to the reviewed sources and may have shifted. See the [Batch 1](REMEDIATION_BATCH_1.md), [Batch 2](REMEDIATION_BATCH_2.md) and [Batch 3](REMEDIATION_BATCH_3.md) reports for local resolution evidence and [current release progress](../../../PROGRESS.md) for public verification.

Severity follows the requested P0–P3 definitions. P0 asks whether the public release can meet its stated scope. P1 is a material error or capability gap. P2 improves clarity, transfer or repeatability. Effort estimates cover the proposed correction and targeted verification by one maintainer. They exclude scheduling a human panel or deployment. No course files were changed.

## F-001 · P0 · The public full curriculum is missing the authored M18-T01 lesson

- **Location and evidence.** The public curriculum GET returned the M18-T01 topic with “Lesson outline” in its body. The public page has all 53 topic IDs, but the number includes this outline. Working-tree M18-T01 has a full lesson with four Python blocks, all replayed in this audit. The public and working-tree dependency payloads have the same SHA-256. Their whole-page hashes differ. [Working-tree lesson](../../lessons/m18-t01.md#L1) · [Outline template](../../generate_master_curriculum.py#L500) · [Public curriculum](https://llmacademy.testneural.in/master-curriculum.html)
- **Why it matters.** A learner on the public expert path cannot complete the module's advanced judge validation lab. Publishing the full course and approving this lab are separate decisions.
- **Correction and dependencies.** Review the pending M18-T01 changes, resolve F-006, obtain the required teaching review, then publish the approved snapshot through the existing release process. Keep unrelated working-tree changes separate.
- **Effort and verification.** 1–2 hours of release work after review. GET the public topic body and verify the lab, practice and editor links. Walk the M18 transitions in both course modes against the approved revision.

## F-002 · P1 · The mitigation report can mark findings verified without any retest evidence

- **Location and evidence.** `lifecycle([], [])` in M12-T03 returned VERIFIED for all five findings. The function uses the length of the received list as its verification denominator, including zero, and compares prior/current cases using positional pairing. The overall release gate independently validates full case IDs. The false verification is in finding statuses. [M12-T03 lifecycle](../../lessons/m12-t03.md#L779)
- **Why it matters.** Learners may reuse the reporting pattern and close a finding when evidence is lost or reordered.
- **Correction and dependencies.** Anchor each finding to its planned distinct case IDs and join the two captures by case ID. Absence or ambiguity should keep the finding open even when every supplied row passes.
- **Effort and verification.** 1–2 hours. Exercise empty, partial, reordered and duplicate results. Require the planned set before VERIFIED and require a genuine same-case regression before REOPENED.

## F-003 · P1 · An executed wrong-order write is downgraded in the mitigation lab

- **Location and evidence.** In the repaired A05 fixture, changing only the proposed order to a different fictional ID while retaining the executed receipt and ledger effect returned case FAIL with critical false and overall REVIEW. The executed-allowed branch checks duplicate effects and treats the action's wrong order as an ordinary mismatch. Receipts and state are matched by operation only. [M12-T03 write validation](../../lessons/m12-t03.md#L694) · [M12-T02 binding to authorization context](../../lessons/m12-t02.md#L668)
- **Why it matters.** Learners need to distinguish an allowed operation from an allowed target. The trace alone cannot identify the affected resource when the receipt and independent state omit it.
- **Correction and dependencies.** Bind the authorization, executed receipt and independent state to the approved synthetic resource and operation. Treat a corroborated out-of-scope effect as critical. Preserve uncertain scope as unknown and require review.
- **Effort and verification.** 2–4 hours. Add three inert captures with matching authorized scope, corroborated wrong scope and missing scope. Expect PASS, critical HOLD and REVIEW respectively.

## F-004 · P1 · The defensive track measures saved outcomes more than it exercises defenses through a stateful workflow

- **Location and evidence.** M12-T01 introduces direct and indirect injection and jailbreak categories. M12-T02 and M12-T03 provide strong saved document, tool and state evaluations. M11-T03 supplies a multi-turn privacy row and M16-T03 runs memory checks. The core track has no guided comparison where the learner runs a retained multi-turn policy conflict through a harmless stateful component, verifies a trust-boundary control before and after, and scores a matched permitted interaction. Conversation-history authority, role spoofing and encoded or transformed input have only partial or absent M12 practice. [M12-T01 terminology](../../lessons/m12-t01.md#L33) · [M12-T02 fixture inventory](../../lessons/m12-t02.md#L536) · [M11-T03 saved slice](../../lessons/m11-t03.md#L475)
- **Why it matters.** Reading an already-graded or canned capture cannot demonstrate that preservation of trust metadata and independent authorization works when state moves across turns. The current curriculum explicitly specifies a fixture-only M12 and meets much of that stated scope. The gap is transfer from interpretation to exercising a permitted defense.
- **Correction and dependencies.** Extend one existing lab with an instructor-authored, no-network mock that consumes inert tagged records, preserves independently assigned roles and logs a local dummy decision. Compare checked and unchecked fixture modes and score a held-out legitimate control, explicit unknown and one synthetic multi-turn outcome. Add a coverage row for retained-history and content-normalization boundaries. No external targets, scanner runs, model interaction or real payloads are needed.
- **Effort and verification.** 4–8 hours. A learner should reproduce the before/after control result and explain what the surviving matched control, the observed safe action and the missing evidence establish. See the [coverage matrix](RED_TEAMING_COVERAGE.md).

## F-005 · P1 · Defensive success and utility denominators mix plan and observation

- **Location and evidence.** Removing only the dispatch observation for A01 in M12-T02 produced `1/4 evaluated of 4 planned` even though the five planned cases stayed fixed. The planned total is computed from observed write attempts. The same report excludes rows with any missing field from the write-rate numerator even when a correlated receipt or independent ledger supports an effect. In M12-T01, replacing C1's approval with the existing denial label returned mismatch with false refusal false. The counter recognizes only the `withhold` wording. The overall gates still recognize failures or gaps. [M12-T02 report](../../lessons/m12-t02.md#L730) · [M12-T01 refusal counter](../../lessons/m12-t01.md#L510)
- **Why it matters.** A failing or missing control can make a metric look better, or make a missing attempt disappear from coverage. This affects the module's core measurement objective.
- **Correction and dependencies.** Record planned targets separately, then report offered, dispatched, independently evaluable, confirmed effect and unknown counts. Derive refusal from a rubric grounded in expected assistance, rather than a single surface label. Use M11-T01's authorized utility control definitions.
- **Effort and verification.** 2–4 hours. Confirm that lost dispatch leaves the planned denominator at five, confirmed effects stay visible, and a denial of an authorized task increments the eligible false-refusal count without counting legitimate policy denials.

## F-006 · P1 · The advanced judge lab derives candidate defaults from the gold reference

- **Location and evidence.** M18-T01 explains this fixture shortcut and notes that real judge versions need separate calibration. In a scratch probe of `assess`, a reference-only A01 edit changed both truth and the displayed default prediction from PASS to BLOCK with the candidate override mapping unchanged. The release lab is useful for gate arithmetic, but its inputs do not model independent frozen predictions. [Design disclosure](../../lessons/m18-t01.md#L218) · [Prediction builder](../../lessons/m18-t01.md#L360)
- **Why it matters.** A learner revising an annotation can silently create a different candidate capture. That undermines the label independence the topic teaches. It is a local draft issue and does not affect the current public outline.
- **Correction and dependencies.** Store frozen synthetic predictions per case and version independently of gold labels. Keep the exercise's deliberate errors and documented evidence limits. Distinguish calibration and blind evaluation snapshots and require version-matched calibration whenever learners compare deployable judges.
- **Effort and verification.** 2–4 hours. Change one gold label and assert that stored candidate payloads and their digests remain unchanged. Change the judge version and verify that old calibration is flagged and unresolved evidence routes to REVIEW.

## F-007 · P1 · The concepts reference overstates what archived framework comparisons prove

- **Location and evidence.** “Metric Calibration” attributes the Test 9 versus Test 11 relevance difference to calibration alone. Test 11 includes timeout fallback scores and mixed batch conditions. “Framework Pass / Fail” frames every case as a binary output. “Refusal Handling” says automated metrics should never score a correct refusal while M11 teaches independent refusal appropriateness and false-refusal metrics. [Concepts reference](../../concepts.html#L1276) · [Archived timeout caveat](../../test11.html#L628) · [Current M09 lesson](../../lessons/m09-t02.md#L328) · [Current safety lesson](../../lessons/m11-t01.md#L89)
- **Why it matters.** A learner may explain a measurement artifact as a judge effect, omit missing results from gate evidence or skip evaluation of legitimate refusal behavior.
- **Correction and dependencies.** Qualify the archive comparison as noncontrolled. Report measured scores, unscorable rows and criterion applicability separately. Link to M09-T02 and M11-T01 and retain the historical source artifact as-is.
- **Effort and verification.** 1–2 hours. A reader can explain why these data cannot isolate calibration and enumerate scored fail, execution error, unscorable and justified refusal.

## F-008 · P1 · Entry checkpoints lack runnable preparation materials at the first terminal-dependent transition

- **Location and evidence.** The preparation table tells novices to run a supplied script, read a saved HTTP request and convert supplied JSONL fixtures, but gives skills and checkpoints without the associated starter files or a complete guided bridge there. M01–M03 correctly provide copy-and-run editor programs. M14-T01 abruptly assumes repository-root navigation, local file setup, two terminal sessions, virtual-environment activation and package installation. Optional terminal examples earlier in the sequence do not require a novice to transfer the workflow. [Preparation table](../../../MASTER_CURRICULUM.md#L46) · [Beginner standard](../../../TEACHING_GUIDELINES.md#L24) · [M14-T01 setup](../../lessons/m14-t01.md#L49)
- **Why it matters.** The whole course can serve a person new to evaluation. A zero-setup beginner still needs a way to demonstrate the tool skills before advancing to production labs. The gap is setup and diagnosis, rather than missing evaluation theory.
- **Correction and dependencies.** Attach one reusable preparation packet with a safe scratch folder, a saved HTTP response, a JSONL example, its deliberate path error and exact expected results. Link it from P01–P05 and the M14 setup. Put the no-export trace replay before the optional viewer setup, then show clear working-directory recovery.
- **Effort and verification.** 3–6 hours plus learner pilot. Ask a first-time learner to run the local replay from a clean checkout, repair a bad path and distinguish a wrong policy reply from a request error without being told the steps.

## F-009 · P2 · The historical experiments lack a per-runner dependency and configuration map

- **Location and evidence.** README gives repository-level installation and provider notes. The historical modules also directly import packages such as `ollama` and `datasets`, which the top-level requirements file does not list. Test 14's historical Langfuse integration and M14's newer isolated teaching environments use different major SDKs. These captures are useful, but the checkout alone does not reproduce every historical run. [README setup](../../../README.md#L150) · [Top-level requirements](../../../requirements.txt) · [Test 0 data loader](../../../phase-0-foundations/explore_squad.py) · [M14 trace setup](../../lessons/m14-t01.md#L51)
- **Why it matters.** A learner may install the wrong SDK or start a provider-backed experiment expecting the archived outputs.
- **Correction and dependencies.** Add an archive manifest for each runner with runtime, explicit dependencies, provider/cost flag, inputs and outputs, and a safe saved-artifact alternative. Leave the original source and captures unchanged.
- **Effort and verification.** 3–5 hours. An independent instructor can identify the exact offline entry point and can distinguish archive requirements from the current Academy labs without discovering imports by trial and error.

## F-010 · P2 · The CI sample demonstrates the gate adapter more fully than running candidate-bound evidence in CI

- **Location and evidence.** M13-T02's optional hosted example runs `--ci repaired` on pull requests. It explicitly says the fixture does not evaluate the proposed prompt and hosted enforcement remains unverified. Students do produce audit JSON and real exit codes locally. [CI example and caveat](../../lessons/m13-t02.md#L375) · [Engineering lab](../../lessons/m13-t02.md#L586)
- **Why it matters.** A newcomer can reproduce a green status without practicing the provenance join between the proposed revision, its capture and the independent gate.
- **Correction and dependencies.** Extend the optional offline workflow with a trusted runner and two sanitized candidate artifacts bound to different candidate IDs and digests. Use M13-T01 for artifact shape and M13-T03 for approval semantics.
- **Effort and verification.** 2–4 hours. In a training repository red and green fixture artifacts produce different required results. A stale or mismatched artifact cannot clear the proposed change. A gate pass still does not deploy anything.

## F-011 · P2 · The course needs one shared boundary between a scorer status and deployment authority

- **Location and evidence.** M07-T03 names the favorable teaching outcome RELEASE. M12-T02 uses READY FOR AUTHORIZED NEXT-STAGE TESTING. M13-T03 separates a gate result from version-bound approval, and M15-T02 uses PASS as evidence for requesting limited approval. These terms are qualified within the respective lessons. A beginner on a shorter route may see RELEASE before learning who can authorize exposure. [M07-T03 release rule](../../lessons/m07-t03.md#L65) · [M12-T02 gate](../../lessons/m12-t02.md#L552) · [M13-T03 workflow](../../lessons/m13-t03.md#L340) · [M15-T02 decision defense](../../lessons/m15-t02.md#L47)
- **Why it matters.** Similar labels describe different layers. Silent replacement of a rubric score, a CI gate and a governance decision would destroy auditability.
- **Correction and dependencies.** Add a short status crosswalk near the first release illustration and link it to M13-T03. Keep case outcome, execution state, gate recommendation and approval authority separate. Preserve justified thresholds and domain-specific statuses.
- **Effort and verification.** 1–2 hours. A learner can map a passed case, a paused rollout and missing incident evidence to distinct records and can name the authorized decision owner.

## F-012 · P2 · Topic-level instructor guidance is hard to find

- **Location and evidence.** The authoritative topic template asks for instructor notes with timing, prediction prompts, learner mistakes and offline fallback. Many lessons supply learner-time estimates, prompts, worked solutions and fallback in separate sections. For example M07-T02 provides the lab and practical cautions, and M14-T01 offers technical troubleshooting, but neither provides a compact instructor run sheet mapping classroom timing to evidence and fallback. [Curriculum template](../../../MASTER_CURRICULUM.md#L130) · [M07-T02 worksheet](../../lessons/m07-t02.md#L531) · [M14-T01 worksheet](../../lessons/m14-t01.md#L384)
- **Why it matters.** An instructor can teach from the content but must assemble the guided sequence and know which optional external systems can be skipped.
- **Correction and dependencies.** Pilot a one-page run sheet for one foundation lesson, the red-team lab, and the first production lab. Reuse existing prompts and checkpoints.
- **Effort and verification.** 2–4 hours. An instructor unfamiliar with the course can pick the runnable core, estimate time, elicit a prediction and switch to a verified replay without dropping the assessment criteria.
