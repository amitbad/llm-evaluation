Use these timed segments within the existing lessons. They cover the runnable core and one evidence-based decision per session. Times are planning estimates for an instructor-led pilot. Prepare a printed or saved copy of each named output before class. Ask learners to write a prediction before revealing the transcript. If you switch to transcript analysis, record that the learner interpreted the output and still needs independent execution practice.

### Foundations · M01-T01 · Message order and available evidence

- **0–5 min · Set up.** Open [M01-T01](#m01-t01), Hands-On Python Exercise, Step 1. Ask learners to name the message that requests the policy and the message that supplies it.
- **5–15 min · Predict and run.** Ask what happens if the tool result is printed before the assistant lookup. Run Step 1 and its reorder experiment in the editor or local Python. Both runs print five lines, but the lookup and result reverse in the second.
- **15–25 min · Diagnose and assess.** A common mistake is treating successful Python execution as valid message ordering. Have each learner mark the request and result in both transcripts and describe one check that should reject the reversed order.
- **Offline fallback.** Use local Python 3.10+ if the browser editor is unavailable. Without Python, hand out both saved Step 1 transcripts after predictions. Use the same ordering check as the assessment.

### Defensive evaluation · M12-T02 · Retained-history control

- **0–8 min · Set up.** Open [M12-T02](#m12-t02), Guided Engineering Lab, Run a retained-history control. Identify the fictional note, the independent provenance record and the expected authorization result.
- **8–20 min · Predict and run.** Ask whether the retained note, legitimate verification record and record with missing provenance will each authorize a refund. Run the complete local Python block. The checked run prints DENY, ALLOW and REVIEW in that case order.
- **20–35 min · Diagnose and assess.** A common mistake is trusting the same label wherever it appears or treating REVIEW as proof of defense. Ask learners to map each outcome to its source and explain how they would retain the legitimate control in the retest.
- **Offline fallback.** The block needs no model, scanner or account. If Python is unavailable, hand out the saved check-off and check-on outputs. Have learners reconcile all three decisions, including the missing evidence.

### First production lab · M14-T01 · Trace and repair TC10

- **0–10 min · Set up.** Open [M14-T01](#m14-t01), Setup and run. From the repository root check the saved Test 12 captures and copy the lab to a temporary directory as instructed. Use the preparation packet if learners need help checking their location or input files.
- **10–25 min · Predict and run.** Ask whether a replay can exit 0 while the saved answer fails a required step. Run replay, repair and the intentional lookup error with `--no-export`. Compare the tool paths, outcome codes and trace IDs.
- **25–40 min · Diagnose and assess.** A common mistake is treating exit 0 or a trace ID as a quality verdict. Have learners name the missing search, explain why the repaired path can safely escalate, and identify why the injected error has no quality verdict.
- **Offline fallback.** Run the standard-library `--no-export` path and skip the optional viewer. If the checkout or terminal is unavailable, use the three saved outcomes directly below the commands. Each learner still has to distinguish execution, quality and absent evidence.
