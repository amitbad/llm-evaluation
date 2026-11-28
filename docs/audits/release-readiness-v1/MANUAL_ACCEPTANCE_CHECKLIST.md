# V1.0 manual acceptance checklist

**Status · Pending.** Run against the approved candidate on an isolated preview first. Repeat production smoke checks after an authorized deployment. Record revision, URL, browser and OS versions, viewport, theme, expected and actual result, and any screenshot, downloaded file or console error. Keep test progress and voice preferences in a disposable profile.

## Five destinations and learning tools

| Area | Test and expected result |
| --- | --- |
| Quick Learning | Open paths A through G. Start A from preparation and open M17-T03 within G. Navigate forward through M18-T01 and M18-T02. Use Back, Forward and reload on a guided lesson address. The selected mode and topic survive reload. Finish the last topic in a path and verify it stops at the correct boundary. |
| Complete Course | Search for a known lesson title, combine a module filter with progress, and clear filters. Expand M18-T01 and check the full lesson with four runnable Python blocks. Check a prerequisite link, a topic deep link and a return to the original path. No outline substitutes for authored material. |
| Learning Roadmap | Follow the separate checks below for focus, prerequisites, fullscreen and image export. |
| About the Course | Check navigation to the five destinations, hours and track summaries, and Continue Learning. Compare the view on narrow and wide screens. The hours table scrolls within its own container where needed. |
| Resources | Open Concepts, Original Practical Tests, Instructor Run Sheet and Teaching Plan. Follow the three run-sheet links and verify the preparation material is reachable from the learning flow. Open a pinned archive source, the online editor, the full results report and the production workbook. |
| Continue Learning and progress | Complete a topic in Quick Learning, reload, and verify the same completion in Complete Course. Continue Learning opens the first unfinished required topic in the selected path. Test the completion checkbox or status control with the keyboard. |
| Backup and restore | Export a version-one backup. In another disposable profile, preview and cancel. Then import using merge and replace, and verify counts and path selection. Try malformed JSON and a backup with an invalid topic ID. Confirm that existing progress stays intact. |
| Copy Code | Copy one Unicode Python block and paste it into the external editor. Compare indentation and text, then run it. Confirm accessible status feedback and test clipboard-denied behavior. |
| Layout, access and console | Check desktop and mobile in both themes, using approximately 375, 768, 1366 and 1920 px. Tab through all five destinations and representative dialogs, links, filters and lesson controls. Check visible focus, focus restoration, readable status messages, contrast, horizontal overflow and persistent controls. With DevTools open, reload and exercise the features. Record first-party errors, failed assets and any reproducible failures. |

## Read Aloud · macOS Chrome and Safari

1. Start a fresh profile. Check the available ordered list against Samantha, Google US English, Daniel, Google UK English Female, Google UK English Male, Karen and Tessa. The locales are respectively en-US, en-US, en-GB, en-GB, en-GB, en-AU and en-ZA. Expect Samantha when available, then the first available approved voice. A profile with no approved voices should show the browser-default message and still play.
2. Select an approved voice, preview it, choose **Use Voice**, reload and switch modes. The saved voice should follow the learner where available. Note delayed discovery and which voices are actually installed.
3. Read a long paragraph with punctuation, links, repeated words and emphasis. Listen for continuity within sentences and across natural boundaries. With usable speech events, verify the active word and follow-scroll behavior. With a voice that supplies no useful timing, verify the labeled paragraph fallback and continuing narration. Confirm text selection and links still work.
4. Pause mid-sentence and resume. Stop during playback and verify highlighting clears. Change voice during playback and confirm the current paragraph restarts with the chosen voice. Switch lessons and confirm the previous narration stops. Check finish cleanup, keyboard operation and reduced motion.
5. Record separately whether voice selection, audible narration and word synchronization worked on each browser and voice pair. Record fallback as the expected result when the engine supplies no reliable word events.

## Learning Roadmap

1. Search using a topic ID and title. Select M17, change module/topic detail and confirm that required, recommended and conditional routes and the selected topic appear correctly. Check keyboard operation and progress-based readiness.
2. Pan and zoom. Enter fullscreen, resize, and check that graph scale uses the available viewport while the header and controls remain usable. Close through the button and Escape, then confirm windowed position and focus are restored. Check fallback where available.
3. Open **Download Image**. Inspect the selected learning path, complete module roadmap and complete topic roadmap. Open each as SVG and PNG. Confirm the target and only its applicable prerequisites in the selected export, all 18 modules in the complete module export, and all 53 topics in the complete topic export. Check legends, readable labels, dependency endpoints, clipping, and meaningful filenames.
4. Repeat after changing zoom, pan, focus and fullscreen. Export content and scope should be stable. Confirm Cancel and Escape produce no download, dismiss the dialog and return focus. In fullscreen, Escape should close the export dialog before exiting the roadmap where applicable.

## Teaching review and beginner pilot

- Apply the [teaching standard](../../../TEACHING_GUIDELINES.md#review-before-publishing) to the actual approved revision. Record whether the learner could explain the concept, run the exercise unaided, predict and interpret a change, identify evidence limits, and name confusing instructions.
- Observe a first-time learner using Copy Code and the editor in M01-T01. Then have them complete the preparation packet from a fresh checkout and run the first M14-T01 terminal replay. Record environment, time, help required, prediction, results and the learner's next decision.
- Use the three instructor sessions to check timings and transcript fallbacks. Record transcript interpretation and independent execution as separate evidence. Obtain explicit teaching approval and close blocking findings before any V1.0 declaration.
