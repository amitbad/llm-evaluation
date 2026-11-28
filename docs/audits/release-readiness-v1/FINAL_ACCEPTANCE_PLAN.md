# V1.0 final acceptance plan

**Status · Pending human execution.** Use the [staged candidate and revision pin](RELEASE_EXECUTION_CHECKLIST.md) in a disposable profile. Test macOS Chrome and Safari on desktop, plus Chrome and Safari on supported mobile devices. Check both themes at narrow and wide widths. Use keyboard navigation on desktop.

For every row, record `ID | revision | OS / browser / version | viewport | Pass / Fail / Pending | actual result | evidence or issue`. Mark Pass only when the observed result matches the row. Record a failure with reproducible steps and an owner. A missing device, voice, browser or reviewer leaves the applicable check pending. Keep screenshots and test artifacts free of personal data.

| ID | Action | Expected result and evidence to record |
| --- | --- | --- |
| NAV-1 | Open Quick Learning paths A–G one by one. Compare topic totals and open an early and final topic in each. | A 44, B 8, C 7, D 5, E 5, F 15 and G 53. The lesson list stays in order and the last lesson has no out-of-path Next. Record each path result separately. |
| NAV-2 | Search and filter Complete Course, open M18-T01, navigate to a prerequisite, then open M18-T01 in Quick Learning G and reload. | Clear resets filters. The full lesson has four Python blocks. Deep links, progress state and browser Back/Forward preserve the intended topic and mode. Record final URLs. |
| NAV-3 | Visit About the Course and Resources. Open the preparation packet, concept reference and instructor run sheet. Choose the homepage workbook download. | Navigation reaches useful content. The workbook downloads from the existing route and opens in a spreadsheet reader. Record status and checksum after deployment. |
| CODE-1 | Copy the M01-T01 Step 1 block and paste it into the Python editor. Run the baseline and the reorder experiment. | Text and indentation match. Both outputs have five lines. The two reordered lines appear in the predicted positions. Record the transcript and Copy Code feedback. |
| PROG-1 | Complete a lesson in Quick Learning, reload and open Complete Course. Choose Continue Learning. | Completion agrees across modes and reload. Continue Learning targets the first unfinished required topic in the chosen path. Record the original and resumed topic IDs. |
| PROG-2 | Export progress. In another profile preview and cancel, then import with merge and replace. Try malformed JSON. | Downloaded version-one backup is usable. Cancel and invalid JSON leave progress intact. Merge and replace give the stated outcomes. Record counts and path after each action. |
| ROAD-1 | Select M17 from roadmap search, try keyboard navigation, and inspect dependencies. Pan, zoom, enter fullscreen, resize, then exit. | Inspector and graph agree on the selection and dependency types. The graph scales while controls stay visible. Windowed position and focus return after Exit or Escape. Record screenshots before and after. |
| ROAD-2 | Download selected M17 path, full module graph and full topic graph as SVG and PNG. Repeat after zoom, pan and fullscreen. Try Cancel and Escape. | Selected path shows the target and applicable prerequisite closure. Complete files represent all 18 modules or 53 topics. Downloads are legible and viewport-independent. Cancel/Escape create no file and return focus. Record filenames and format checks. |
| READ-1 | Check voices in fresh Chrome and Safari profiles. Preview and save an available nondefault voice, reload and change lessons. | Only installed approved voices appear, in order. Samantha is preferred when present. Saved voice persists. With no approved voice, the browser-default message appears and speech still works. Record installed voices and result per browser. |
| READ-2 | Read a long paragraph with a link, emphasis and repeated words. Listen and observe scrolling. Use a voice with unusable boundary events if available. | No repeatable application-induced mid-sentence pause. Usable events track the words across markup. Without usable events the labeled paragraph highlight remains, and narration continues. Record voice, timing observations and fallback coverage. |
| READ-3 | Pause mid-sentence, Resume, Stop, change voice and navigate during playback. | Pause/Resume continues the same utterance. Stop, completion and lesson changes clear tracking. Applying a new voice restarts only the current paragraph. Record any doubled or stuck playback. |
| LAYOUT-1 | Try desktop and mobile at representative widths near 375, 768 and 1366 px. Open dialogs, toggle themes and inspect console/network. | No clipped essential controls or page-wide overflow. Focus is visible and restored. Controls remain usable with touch and keyboard. Record first-party console errors, failed assets and screen evidence. |

Approved voices in order are Samantha (en-US), Google US English (en-US), Daniel (en-GB), Google UK English Female (en-GB), Google UK English Male (en-GB), Karen (en-AU) and Tessa (en-ZA). Real narration behavior is a manual result. See the [feature acceptance notes](MANUAL_ACCEPTANCE_CHECKLIST.md) for additional scenarios.

## Teaching review script

Use the actual lesson page and complete the baseline before opening solutions. Give each reviewer the candidate SHA, the lesson objective from the curriculum, and a blank result sheet. For each selection, ask the reviewer to predict a change, run it independently and explain their ensuing evaluation decision.

| Level | Exercise | Evidence for review |
| --- | --- | --- |
| Beginner · M01-T01 | Use the online editor for Step 1, then move the tool result above the lookup. | Explain why the program still runs and why the message order is invalid. Check whether instructions, expected output and the explanation are discoverable. |
| Intermediate · M06-T02 | In Step 4 change the stated deadline from 30 to 90 days, holding labels fixed. | Explain why unanimous labels can still be wrong and cite the relevant evidence. Check that the lesson distinguishes agreement from correctness before using the result. |
| Advanced · M18-T01 | Run the judge replay and inspect the critical false approval and missing-evidence scenarios. | Explain why a strong aggregate cannot override a critical miss. Identify the independent prediction and reference inputs and the reason the missing-evidence case is held for review. Verify that exercise instructions and expected outputs support the decision. |

Ask the five questions in the [teaching standard](../../../TEACHING_GUIDELINES.md#review-before-publishing). For each lesson record `reviewer role | lesson and section | revision | technical accuracy | progression | example quality | exercise run and interpretation | confusion or assistance | required correction | approve / changes required / pending`. Sampled acceptance provides evidence for those lessons. Record any additional approvals required by the owner separately.

Run the independent [beginner pilot](BEGINNER_PILOT.md) before release sign-off. Retest any blocking correction on the final pinned candidate.
