# LLM Evaluation Engineering — From Fundamentals to Advanced and Production

## Course overview

### Vision and audience

A long-term reference for learners entering LLM evaluation, engineers owning evaluation decisions, and instructors teaching or adapting practical labs. By the end of the core path, a learner should be able to design a versioned evaluation, build and calibrate scorers, quantify uncertainty, diagnose RAG and agent failures, and defend a production release decision. Expertise includes knowing when the evidence warrants another experiment or human review.

Start with concepts and explicit decision criteria, then build a small Python scorer. Use frameworks once learners can explain the metric and verify a result by hand. Study RAG and agents through observable inputs, outputs and states. Finish by connecting offline evaluations to release decisions, traces and monitored outcomes. The plan describes target competencies and future labs. The coverage statuses describe the current repository.

### Sequence and time estimates

Core progression spans Beginner, Intermediate, Advanced and Production. Specialized / Expert modules are electives that can be studied independently after their listed prerequisites. Topic records give the minimum preparation for focused study. Module prerequisites are the recommended sequence for a learner completing the whole module. Each stage ends with a reviewable artifact, and the capstone brings those artifacts together.

Times are planning estimates in hours. Each topic lists theory, guided hands-on implementation, independent experiments and interpretation, exercises and assessment, total learner time, and instructor-led classroom time. Instructor-led hours are a separate delivery estimate for explanation, demonstration and supervised practice. Preparation, breaks, and optional provider work are outside that estimate. Plan extra preparation for a first teaching run.

Estimates assume a learner who can use a terminal and read simple Python, coaching available for the first lab, and prepared fixtures with expected outputs. Guided times include routine setup and troubleshooting for the activity. Learners new to Python should practice reading a JSON file, looping over records, and running a test before starting guided implementation. Large downloads, hardware delays, provider wait times, deep remediation and elective live extensions vary by environment. Pilot time estimates with both a beginner and an experienced engineer.

| Strand | Modules | Topics | Theory | Guided | Experiment | Exercise | Learner total | Instructor-led |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Core | 15 | 44 | 60.5 | 74 | 60 | 43.5 | 238 | 158 |
| Elective | 3 | 9 | 14.5 | 17 | 14 | 9 | 54.5 | 36 |
| All | 18 | 53 | 75 | 91 | 74 | 52.5 | 292.5 | 194 |

### One evolving application

- **Beginner** — Evaluate a fictional bank support chatbot from six saved responses. Build exact/semantic boundary examples, a deterministic scorer and a blind human review sheet. Explain failure, uncertainty and execution error.
- **Intermediate** — Publish a versioned gold dataset, calibrate a judge on frozen examples and compare prompt versions with paired Python analysis. Verify labels, denominators and uncertainty before drawing a conclusion.
- **Advanced RAG** — Give the chatbot a fictional policy corpus. Evaluate ranked passages, context sufficiency, claims and citations, then compare retrieval changes against an oracle reference.
- **Advanced agents and safety** — Add a mock account lookup and a simulated workflow. Verify actions, arguments, state, recovery and safe refusals. Assess defensive controls from fixed fictional traces and inert records.
- **Production** — Add fixture-driven gates, trace metrics and a simulated incident. Convert a reviewed failure into a regression fixture and defend a release, hold or rollback decision.
- **Electives** — Change the task when the method needs different evidence. Use synthetic fee charts for multimodal evaluation, public-style and private fictional benchmarks for contamination lessons, and benign generated functions for test-driven code evaluation. Use the healthcare examples for transfer lessons on score validity and source grounding.

### Execution modes and tool choices

Every essential lesson starts with a fixture or simulated run that needs no model, network or credentials. Live Ollama inference and locally cached embeddings are optional hands-on extensions. The existing Test 5 configuration points to OpenAI and the existing Test 10 RAGAS integration requires OpenAI calls. These examples are references until local or fixture alternatives and effective settings are verified. Hosted graders and paid comparisons are optional, explicitly budgeted extensions.

Choose DeepEval for Python-oriented assertions and thresholds when its chosen metric fits the construct. Choose RAGAS for a RAG metric suite when the record carries its required references or evidence. Both may call judges or embeddings and need versioned adapters, explicit failure states and checked denominator behavior. Choose promptfoo for a declarative prompt and provider matrix, and OpenAI Evals for an OpenAI-centered managed grading workflow when supported graders, data handling and cost fit. Compare both on saved cases before adding a managed run.

Choose Langfuse for linked LLM traces, observations and scores. It depends on the quality of instrumented events and attached scores. OpenTelemetry is useful when correlation across services is the objective, with separate application quality measures. In defensive evaluation, Garak illustrates scanner-style coverage and PyRIT illustrates organized assessment records. Use prepared offline reports to compare their evidence formats and coverage. Tool output depends on scope, fixtures and labels, and requires review before it informs a decision.

## Learning paths

### Complete beginner

**Prerequisites.** Basic computer use. A simple Python and JSON warm-up is included in the preparation guidance. No previous LLM evaluation, statistics or model account required.

**Entry checkpoint.** Open a saved response and identify the question, answer and evidence. Progress through [M01](#m01)–[M03](#m03), [M04](#m04)–[M07](#m07), then the advanced and production modules in order. After M03, explain a false pass and show the fixture scorer distinguishes a transport error from a model failure.

### Intermediate engineer

**Prerequisites.** Python, terminal and JSON familiarity, and the ability to explain a normalized rule and a reference answer.

**Entry checkpoint.** Given one labeled case, implement a check, identify an unsupported conclusion and explain how you would save the response and score. If successful, enter at [M04](#m04). Review [M03](#m03) for structured checks and rubrics where needed. Complete [M07](#m07) before making comparative performance claims.

### Advanced engineer

**Prerequisites.** Versioned cases, anchored evaluator or judge, paired comparison, and the relevant architecture. Start from the topic cards when your prior experience satisfies the listed prerequisites.

**Entry checkpoint.** Explain one evaluator false pass and one case where offline evidence cannot justify a release. Enter at [M08](#m08) for RAG, [M10](#m10) for agents, [M12](#m12) for defensive assessment, or [M13](#m13) for production gates. Take any of [M16](#m16)–[M18](#m18) after their required modules.

### Instructor preparation

**Prerequisites.** Be able to complete the learner assessment and explain both expected and unexpected results. Verify the teaching environment and exact inputs, code, labels and outputs for the demonstration.

**Entry checkpoint.** Replay the chosen lab offline, grade a good submission and a borderline one, and prepare a fallback when any live extension fails. Use the Teaching Plan, the individual topic demonstrations and assessments, and the module completion criteria. For a first class, teach [M01](#m01)–[M03](#m03) and pilot the fixture timings before planning further sessions.

## Repository coverage

### Reading the mapping

The course audit in `docs/COURSE_AUDIT_REPORT.md` records evidence and impact. Each topic lists its current status, source files, relevant findings, suggested reuse, missing teaching and experiments, and corrections for a future implementation phase. Reusable means a substantial part already supports the topic. Needs Improvement indicates useful but incomplete material. Needs Correction identifies a defect affecting the intended lesson. New indicates absent substantive coverage. Not Assessed is reserved for insufficient evidence. Validation items beginning with V require further investigation. Current HTML/JSON reports illustrate past runs, and the teaching plan calls for separate answer keys.

### Existing lesson crosswalk

- [Test 0](docs/test0.html) contributes [evaluation design](#m02) and [deterministic checks](#m03). [Test 1](docs/test1.html) contributes [the smoke test](#m01-t03). [Test 2](docs/test2.html) contributes [human review](#m03-t03) and [repeatability](#m07-t01).
- [Test 3](docs/test3.html) contributes [reference metrics](#m05-t01). [Test 4](docs/test4.html) contributes [rules](#m03-t01), [dataset authoring](#m04-t02) and [safety scope](#m11).
- [Test 5](docs/test5.html) contributes [pointwise judging](#m06-t01). [Test 6](docs/test6.html) contributes [semantic similarity](#m05-t02). [Test 7](docs/test7.html) contributes [grounding](#m08-t02) and [evaluator robustness](#m18-t01).
- [Test 8](docs/test8.html) contributes [sampling](#m01-t02) and [controlled experiments](#m07). [Test 9](docs/test9.html) contributes [RAG diagnosis](#m08).
- Test 10 contributes RAGAS code to [the framework comparison](#m09-t02). Its script and dataset paths are in that topic's mapping. [Test 11](docs/test11.html) contributes DeepEval setup, metrics and pitfalls to the same topic.
- [Test 12](docs/test12.html) and [Test 13](docs/test13.html) contribute [agent outcome and trajectory scoring](#m10). [Test 14](docs/test14.html) contributes [observability and trace scoring](#m14-t01).
- The [repository README](README.md), [course hub](docs/index.html), [home page](docs/home.html), and [concepts reference](docs/concepts.html) support navigation, setup and terminology. Use the Master Curriculum for the recommended learning order.

## Teaching plan

### Mandatory lesson standard

1. State observable learning objectives.
2. Give prerequisites, setup, input artifacts and an entry checkpoint.
3. Explain the concept in plain language.
4. Explain why it exists.
5. State the problem it solves and constraints on use.
6. Give realistic engineering use cases.
7. Work a small example by hand with a known answer.
8. Increase complexity gradually, including a conflicting or ambiguous case.
9. Give a step-by-step Python implementation or reproducible Python replay when the topic concerns a managed workflow.
10. Explain code sections that change behavior, scores or denominators.
11. Show expected artifacts and key execution results.
12. Interpret results and what decisions they can support.
13. Demonstrate common mistakes.
14. Explain limitations and failure cases, including evaluator failure where relevant.
15. Include a guided experiment with one controlled variable.
16. Assign independent exercises with measurable outputs.
17. Provide solutions or verification criteria, including accepted alternative solutions.
18. Include instructor notes with timing, prediction prompts, common learner errors and offline fallback.
19. Document troubleshooting and how to identify failure stage.
20. Include knowledge checks and observable completion criteria.
21. Connect the current topic to earlier and later evaluation decisions.

### Classroom preparation and assessment

Each session should use the topic's prerequisite check and demonstrations, then ask learners to predict a result before running it. Prepare a small known-answer fixture, one common misconception and a harder case. Grade claims against evidence and review inclusion, decision policy and exceptions. Where output is stochastic, grade expected invariants and justified decisions. For the capstone, require an annotated dataset, manifest, replayable report, failure diagnosis and release recommendation. Ask a peer to reproduce the result.

At least one teaching variant for core labs should use standard-library Python and prepared data. Where a framework is the objective, provide a fixture containing its inputs and results and prepare a pinned optional environment. Instructors should try the first run on target classroom hardware and define bounds for compute, data handling and spend before optional live sessions.

### Implementation sequence

1. **First milestone** — Deliver the M01–M03 fixture-first slice, the starter M04-T01 schema and the first M06-T01 judge replay. Use exactly shared response IDs across the human, rule and judge evidence. Supply a handout, annotated answer key, instructor demonstration and local fixture verification before updating requirements for optional runs.
2. Build the dataset and measurement spine in M04–M07. Establish reliable denominators, anchors, held-out cases, paired comparisons and uncertainty exercises before publishing example baselines.
3. Add M08–M12 around the same contract. Reuse the banking corpus and traces. Verify gold passage and final-state controls before framework demos. Prepare safety and defensive-review fixtures for bounded, fictional labs.
4. Add M13–M15 after the offline gates are stable. Introduce sampled synthetic traffic, redacted tracing and incident-to-regression review.
5. Build electives once the relevant core artifacts are stable. Add tracks based on learner need and verify each against a separate domain-specific rubric.

### Maintenance, versioning and regeneration

Curriculum revision 1.0.

Use stable module and topic IDs. Edit titles and passages in place. Allocate new IDs for new learning objectives and preserve old IDs in a deprecation record when retiring a topic. Increment the curriculum revision when changing expected competencies, prerequisites or coverage. Version datasets, prompts, model snapshots and evaluator definitions independently and link those versions from lesson materials.

Update the per-topic mapping whenever a lesson or experiment changes. Review all dependent topics when a prerequisite changes. A topic is ready for implementation sign-off when the lesson follows the standard, an instructor has replayed it, a learner can verify its output and the audit-linked corrections are resolved or documented. Re-estimate time after actual pilots, and record scope changes with the relevant IDs.

The Markdown is authoritative. Run `python3 docs/generate_master_curriculum.py` from the repository root with Python 3.10 or newer to regenerate the standalone HTML. Use `python3 docs/generate_master_curriculum.py --check` to verify the checked-in artifact matches exactly. Edit the structured Markdown fields and rerun the generator. Use explicit anchors for IDs, comma-separated linked prerequisites, and the fixed time column order. The generator validates finding IDs against the audit when that file is present. The HTML is a portable view of the plan. Repository lesson links require the companion lesson files. Progress is stored in the browser for the current device and may depend on file URL and privacy settings.

## Detailed curriculum


### Beginner

<a id="m01"></a>
#### M01 — How LLM applications behave

- **Difficulty.** Beginner
- **Track.** Core
- **Subject.** Foundations
- **Description.** Follow a request from user input to model output. Learn which settings and components can change the evidence an evaluator sees.
- **Objectives.** Trace a generation request, explain output variability, and locate failure boundaries in a model-backed application.
- **Prerequisites.** None
- **Labs.** Replay a fictional bank help request as plain text, then read its saved request and result envelopes.
- **Competencies.** Label the request, model configuration, response and failure stage in a fresh replay.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 3 / 4 / 2.5 / 1.5 / 11 / 7.5

<a id="m01-t01"></a>
##### M01-T01 — Tokens, messages and context windows

- **Difficulty.** Beginner
- **Why it matters.** Missing evidence or truncation can look like a reasoning failure.
- **Concepts.** Tokens versus words, system and user roles, context budget, truncation, input/output limits and message ordering.
- **Prerequisites.** None
- **Demonstration.** Compare two saved prompts that differ only in whether the fee schedule fits in the supplied context.
- **Exercise and assessment.** Mark which evidence the model saw and predict when the reply should abstain.
- **Hours.** 1 / 1 / 1 / 0.5 / 3.5 / 2.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test1.html`](docs/test1.html), [`model_client.py`](model_client.py)
- **Audit findings.** S08
- **Reuse strategy.** Reuse the single request and shared adapter as diagrams.
- **Teaching and experiment gaps.** Add a token-budget worksheet and trace with a truncated prompt.
- **Technical corrections.** Keep model selection and effective request settings visible.

<a id="m01-t02"></a>
##### M01-T02 — Inference, sampling and repeatability

- **Difficulty.** Beginner
- **Why it matters.** A fixed prompt can yield different responses, and generation errors need their own outcome.
- **Concepts.** Next-token sampling, temperature, top-p, seed limits, maximum output tokens, stop conditions and model snapshots.
- **Prerequisites.** [M01-T01](#m01-t01)
- **Demonstration.** Inspect repeated saved completions and compare a changed setting with repeated runs under one setting.
- **Exercise and assessment.** Explain which difference the dataset can support and what metadata it lacks.
- **Hours.** 1 / 1.5 / 1 / 0.5 / 4 / 2.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test8.html`](docs/test8.html), [`phase-3-what-you-are-evaluating/temperature-sensitivity/temperature_evaluator.py`](phase-3-what-you-are-evaluating/temperature-sensitivity/temperature_evaluator.py)
- **Audit findings.** C08,V02
- **Reuse strategy.** Keep the observed temperature comparison as an experiment-design critique.
- **Teaching and experiment gaps.** Add replayable repeated draws and a parameter glossary.
- **Technical corrections.** Remove universal conclusions based on a single fixed-order run.

<a id="m01-t03"></a>
##### M01-T03 — Application architecture and a first smoke test

- **Difficulty.** Beginner
- **Why it matters.** A working request establishes connectivity and enables stage-specific diagnosis.
- **Concepts.** Client, prompt assembly, inference server, retrieval, tools, post-processing, transport errors and end-to-end elapsed time.
- **Prerequisites.** [M01-T01](#m01-t01)
- **Demonstration.** Follow a frozen request through a tiny Python fixture reader. Optionally compare with a single local model call after setup.
- **Exercise and assessment.** Classify timeout, malformed output and plausible-but-wrong response, then name which stage owns each.
- **Hours.** 1 / 1.5 / 0.5 / 0.5 / 3.5 / 2.5
- **Status.** Reusable
- **Existing files.** [`docs/test1.html`](docs/test1.html), [`phase-1-first-experiments/test1_basic_test.py`](phase-1-first-experiments/test1_basic_test.py), [`config.yaml`](config.yaml)
- **Audit findings.** C11,S06,S08,V02
- **Reuse strategy.** Retain the smoke-test idea and worked terminal output.
- **Teaching and experiment gaps.** Add setup preflight and a one-model replay option.
- **Technical corrections.** Qualify timing and creativity observations and verify direct requirements before teaching live setup.

<a id="m02"></a>
#### M02 — Design the evaluation

- **Difficulty.** Beginner
- **Track.** Core
- **Subject.** Foundations
- **Description.** Translate a user goal and potential harm into an evaluation contract with cases, acceptance criteria and decisions.
- **Objectives.** Select an evaluation unit, define outcomes, and explain when to use offline and online evidence.
- **Prerequisites.** [M01](#m01)
- **Labs.** Draft a one-page evaluation contract for fictional fee and account-support questions.
- **Competencies.** Given an ambiguous feature, specify intended behavior, cases, labels, failure categories and a decision owner.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 3 / 3.5 / 3 / 2.5 / 12 / 8

<a id="m02-t01"></a>
##### M02-T01 — Objectives, dimensions and failure taxonomy

- **Difficulty.** Beginner
- **Why it matters.** A score helps only if it answers a decision the team can act on.
- **Concepts.** Correctness, completeness, relevance, groundedness, usability, safety, cost, latency, evaluation units and error versus failure.
- **Prerequisites.** [M01-T03](#m01-t03)
- **Demonstration.** Classify saved fee answers that are incorrect, incomplete, unsupported or unavailable due to infrastructure.
- **Exercise and assessment.** Write one measurable requirement and matching counterexample for each of three dimensions.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Improvement
- **Existing files.** [`docs/concepts.html`](docs/concepts.html), [`docs/test0.html`](docs/test0.html)
- **Audit findings.** C05,S02
- **Reuse strategy.** Start with the audit's false-pass examples and glossary.
- **Teaching and experiment gaps.** Add objective-to-check worksheet and worked failure tree.
- **Technical corrections.** Make failure, evaluator error and N/A explicit.

<a id="m02-t02"></a>
##### M02-T02 — Ground truth, references and benchmarks

- **Difficulty.** Beginner
- **Why it matters.** Valid answers can differ in wording, and some cases require abstention or multiple acceptable labels.
- **Concepts.** Gold evidence, reference answer sets, expected behavior, benchmark validity, dataset rows and uncertain or unanswerable examples.
- **Prerequisites.** [M02-T01](#m02-t01)
- **Demonstration.** Inspect a saved extractive QA example and a synthetic banking record with two acceptable answers.
- **Exercise and assessment.** Write a case with a source, acceptable answers, an abstention label and one known false positive.
- **Hours.** 1 / 1 / 1 / 1 / 4 / 2.5
- **Status.** Reusable
- **Existing files.** [`docs/test0.html`](docs/test0.html), [`phase-0-foundations/explore_squad.py`](phase-0-foundations/explore_squad.py), [`docs/concepts.html`](docs/concepts.html)
- **Audit findings.** S06,V03
- **Reuse strategy.** Retain the SQuAD schema and multiple gold answers walkthrough.
- **Teaching and experiment gaps.** Supply a reviewed local fixture and contrast extractive versus generative tasks.
- **Technical corrections.** Describe the download dependency or use the offline fixture.

<a id="m02-t03"></a>
##### M02-T03 — Offline, online and the evaluation lifecycle

- **Difficulty.** Beginner
- **Why it matters.** Offline quality estimates and live user outcomes answer different questions.
- **Concepts.** Development replay, shadow evaluation, canary, online experiments, regression suites, incident feedback and release evidence.
- **Prerequisites.** [M02-T01](#m02-t01)
- **Demonstration.** Follow a fictional fee-policy failure from labeled case to offline gate, monitored release and incident review.
- **Exercise and assessment.** Classify evidence sources for an offline bug, a silent production failure and a user outcome metric.
- **Hours.** 1 / 1 / 1 / 0.5 / 3.5 / 2.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test14.html`](docs/test14.html), [`README.md`](README.md)
- **Audit findings.** V04
- **Reuse strategy.** Reuse the offline-to-monitoring distinction.
- **Teaching and experiment gaps.** Add a lifecycle diagram, evidence worksheet and decision scenarios.
- **Technical corrections.** Describe offline traces and causal online experiments as separate evidence.

<a id="m03"></a>
#### M03 — Deterministic checks and first human review

- **Difficulty.** Beginner
- **Track.** Core
- **Subject.** Techniques
- **Description.** Build the first evaluator from frozen outputs and learn where human judgment adds evidence.
- **Objectives.** Implement stable assertions, validate structured data and explain a disagreement using a rubric.
- **Prerequisites.** [M02](#m02)
- **Labs.** Score one fixture containing a correct answer, good paraphrase, incorrect close answer, correct abstention, over-refusal and execution error.
- **Competencies.** Submit a runnable fixture scorer and a reviewed answer sheet that identifies false passes and false fails.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 3 / 4.5 / 3 / 3 / 13.5 / 9

<a id="m03-t01"></a>
##### M03-T01 — Exact match, normalization and rules

- **Difficulty.** Beginner
- **Why it matters.** String matches are fast and inspectable but can miss valid aliases and accept wrong claims.
- **Concepts.** Exact match, case and whitespace normalization, Unicode caution, regex boundaries, canonical aliases, numeric checks, precision and recall.
- **Prerequisites.** [M02-T02](#m02-t02)
- **Demonstration.** Implement normalized matches and a typed fee check in Python. Compare with a substring baseline.
- **Exercise and assessment.** Write a truth table for punctuation, negation, an amount mismatch and an acceptable paraphrase.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Correction
- **Existing files.** [`docs/test0.html`](docs/test0.html), [`phase-0-foundations/phase_eval.py`](phase-0-foundations/phase_eval.py), [`docs/test4.html`](docs/test4.html), [`phase-2-evaluation-techniques/banking-bots/banking_evaluator.py`](phase-2-evaluation-techniques/banking-bots/banking_evaluator.py)
- **Audit findings.** C05,S02,S09
- **Reuse strategy.** Use the documented false pass and workbook as starter data.
- **Teaching and experiment gaps.** Add fixed expected outputs and error classification.
- **Technical corrections.** Separate 15 automated from 49 manual cases and replace misleading refusal detection in the verified lab.

<a id="m03-t02"></a>
##### M03-T02 — Structured output and schema validation

- **Difficulty.** Beginner
- **Why it matters.** Valid JSON can still contain invalid field values or unsafe business outcomes.
- **Concepts.** Parsing, types, required and nullable fields, enums, ranges, schema versions, cross-field invariants and invalid-output handling.
- **Prerequisites.** [M03-T01](#m03-t01)
- **Demonstration.** Read mock fee replies using Python and apply explicit field and domain checks after parsing.
- **Exercise and assessment.** Write fixtures for missing, malformed, invalid and business-correct records.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Improvement
- **Existing files.** [`phase-5-production-eval/agent-evaluation/agent.py`](phase-5-production-eval/agent-evaluation/agent.py), [`docs/test12.html`](docs/test12.html), [`phase-2-evaluation-techniques/groundedness/groundedness_evaluator.py`](phase-2-evaluation-techniques/groundedness/groundedness_evaluator.py)
- **Audit findings.** S04,S05
- **Reuse strategy.** Reuse action and judge output schemas as later examples.
- **Teaching and experiment gaps.** Add a beginner classifier or extraction schema and trusted outcomes.
- **Technical corrections.** Check top-level shape and field constraints before reading values.

<a id="m03-t03"></a>
##### M03-T03 — Rubrics and a first human evaluation

- **Difficulty.** Beginner
- **Why it matters.** Human scores vary when criteria, inputs and evidence are underspecified.
- **Concepts.** Anchored ordinal scales, binary decisions, blind review, N/A, evidence notes and response IDs.
- **Prerequisites.** [M02-T02](#m02-t02), [M03-T01](#m03-t01)
- **Demonstration.** Blind-score several saved full replies using one criterion at a time and discuss disagreements.
- **Exercise and assessment.** Submit a revised rubric with a low, middle and high anchor and justify one disputed case.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Correction
- **Existing files.** [`docs/test2.html`](docs/test2.html), [`phase-1-first-experiments/test2_score_evaluations.py`](phase-1-first-experiments/test2_score_evaluations.py), [`phase-1-first-experiments/results/scores.json`](phase-1-first-experiments/results/scores.json)
- **Audit findings.** S01,C01
- **Reuse strategy.** Retain the capture/score split and human-first review.
- **Teaching and experiment gaps.** Supply canonical full responses, annotations and scoring key.
- **Technical corrections.** Blind model labels, show full output and save each decision with its source response ID.

### Intermediate

<a id="m04"></a>
#### M04 — Evaluation dataset engineering

- **Difficulty.** Intermediate
- **Track.** Core
- **Subject.** Dataset Engineering
- **Description.** Build data with documented coverage, adjudicated labels, and a defensible separation between development and final evaluation.
- **Objectives.** Design a golden dataset schema, curate inputs and labels, and manage sampling and updates.
- **Prerequisites.** [M03](#m03)
- **Labs.** Publish a versioned miniature banking dataset with a manifest, slices and isolated holdout.
- **Competencies.** Another learner can validate the schema, reproduce the split and trace each label to evidence.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4 / 5 / 4 / 3 / 16 / 10.5

<a id="m04-t01"></a>
##### M04-T01 — Golden schemas, provenance and versioning

- **Difficulty.** Intermediate
- **Why it matters.** A score cannot be reproduced if cases, labels and outputs drift independently.
- **Concepts.** Stable case and response IDs, data contracts, task metadata, source references, append-only runs, version manifests and validation.
- **Prerequisites.** [M02-T02](#m02-t02), [M03-T02](#m03-t02)
- **Demonstration.** Convert a workbook slice to JSONL and validate field types, unique IDs and references.
- **Exercise and assessment.** Create a revision that changes a label and generate a manifest explaining the effect on previous results.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Improvement
- **Existing files.** [`phase-2-evaluation-techniques/banking-bots/banking_test_cases.xlsx`](phase-2-evaluation-techniques/banking-bots/banking_test_cases.xlsx), [`phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx`](phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx)
- **Audit findings.** S09,S11,S15,S16,V03
- **Reuse strategy.** Borrow realistic categories and documented fields.
- **Teaching and experiment gaps.** Add schema, manifest, converter and duplicate or missing-row fixtures.
- **Technical corrections.** Separate canonical input from run artifacts and catch invalid ranges.

<a id="m04-t02"></a>
##### M04-T02 — Annotation, adjudication and synthetic data

- **Difficulty.** Intermediate
- **Why it matters.** Synthetic breadth is useful when human review and source-backed validation preserve label quality.
- **Concepts.** Annotation instructions, independent labels, disagreement and arbitration, structured generation from policy, review and rejection, provenance and license.
- **Prerequisites.** [M03-T03](#m03-t03), [M04-T01](#m04-t01)
- **Demonstration.** Review synthetic policy examples with two readers, adjudicate disagreements and quarantine ambiguous rows.
- **Exercise and assessment.** Submit a label guide, one disagreement record and a synthetic-data acceptance rule.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/test4.html`](docs/test4.html), [`phase-5-production-eval/langfuse-observability/create_test_cases.py`](phase-5-production-eval/langfuse-observability/create_test_cases.py), [`phase-2-evaluation-techniques/llm-as-a-judge/banking_bot_test_results.xlsx`](phase-2-evaluation-techniques/llm-as-a-judge/banking_bot_test_results.xlsx)
- **Audit findings.** C01,V03
- **Reuse strategy.** Reuse the interactive case-writing prompt and fixed workbook generator as simple precursors.
- **Teaching and experiment gaps.** Add double-label and synthetic validation exercises with defective rows.
- **Technical corrections.** Freeze exact outputs before calling verdicts comparable.

<a id="m04-t03"></a>
##### M04-T03 — Sampling, holdouts, leakage and maintenance

- **Difficulty.** Intermediate
- **Why it matters.** Aggregate gains may hide weak slices or reflect tuning on the evaluation set.
- **Concepts.** Representative and stratified sampling, rare-case oversampling, adversarial edge cases, grouped splits, deduplication, train/test contamination, dataset refresh and retirement.
- **Prerequisites.** [M04-T01](#m04-t01), [M04-T02](#m04-t02)
- **Demonstration.** Split cases by document family, detect near-duplicates, and compare representative coverage with policy-weighted stress coverage.
- **Exercise and assessment.** Explain how to handle a new policy release without exposing or silently changing the holdout.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** V03
- **Reuse strategy.** Build a new split and maintenance lab using the fictional policies as domain context.
- **Teaching and experiment gaps.** Add distribution cards, near-duplicate examples and coverage thresholds.
- **Technical corrections.** —

<a id="m05"></a>
#### M05 — Reference metrics, embeddings and hybrid scoring

- **Difficulty.** Intermediate
- **Track.** Core
- **Subject.** Techniques
- **Description.** Use several fast scorers on the same answers and investigate divergent results before setting a threshold.
- **Objectives.** Compute overlap and semantic similarity, compare error patterns, and design a hybrid decision rule.
- **Prerequisites.** [M03](#m03), [M04](#m04)
- **Labs.** Build a Python scorecard for factual banking answers, paraphrases and unsupported claims.
- **Competencies.** Explain a false positive and false negative for each proxy and defend a held-out decision rule.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4 / 4.5 / 4 / 3 / 15.5 / 10.5

<a id="m05-t01"></a>
##### M05-T01 — Token F1, BLEU, ROUGE and reference metrics

- **Difficulty.** Intermediate
- **Why it matters.** Surface overlap offers a useful baseline for bounded tasks and can penalize correct paraphrases.
- **Concepts.** Token precision/recall/F1, n-grams, BLEU brevity and smoothing, sentence versus corpus BLEU, ROUGE-N and ROUGE-L, multiple references and optional chrF.
- **Prerequisites.** [M03-T01](#m03-t01), [M04-T01](#m04-t01)
- **Demonstration.** Count overlap by hand and in Python, then compare with sacreBLEU and rouge-score on frozen summaries.
- **Exercise and assessment.** Rank a paraphrase and a false high-overlap answer, state the metric scale and explain the mismatch.
- **Hours.** 1.5 / 1.5 / 1 / 1 / 5 / 3.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test3.html`](docs/test3.html), [`phase-2-evaluation-techniques/test3_bleu_score_evaluation.py`](phase-2-evaluation-techniques/test3_bleu_score_evaluation.py)
- **Audit findings.** C10,S06,S08
- **Reuse strategy.** Retain the one-passage example as a simple entry point.
- **Teaching and experiment gaps.** Add token F1, two references, per-case answer key and offline inputs.
- **Technical corrections.** Correct claims equating overlap with quality or removing human bias.

<a id="m05-t02"></a>
##### M05-T02 — Embeddings and semantic similarity

- **Difficulty.** Intermediate
- **Why it matters.** Cosine can find paraphrases while giving high scores to changed amounts or opposite meanings.
- **Concepts.** Vectors, cosine, embeddings from pretrained encoders, model/version effects, threshold calibration and triage.
- **Prerequisites.** [M04-T03](#m04-t03), [M05-T01](#m05-t01)
- **Demonstration.** Compute cosine on toy vectors, then compare cached embedding results for near-miss answers.
- **Exercise and assessment.** Evaluate two thresholds on held-out data and explain which factual errors go to deterministic checks.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test6.html`](docs/test6.html), [`phase-2-evaluation-techniques/semantic-similarity/test6_semantic_similarity.py`](phase-2-evaluation-techniques/semantic-similarity/test6_semantic_similarity.py), [`phase-2-evaluation-techniques/semantic-similarity/healthcare_test_cases.xlsx`](phase-2-evaluation-techniques/semantic-similarity/healthcare_test_cases.xlsx)
- **Audit findings.** C09,S02,S11,S16
- **Reuse strategy.** Reuse the healthcare near misses and threshold discussion.
- **Teaching and experiment gaps.** Add cached vectors, negations and numeric contrast pairs.
- **Technical corrections.** Separate similarity bands from correctness and exclude transport errors.

<a id="m05-t03"></a>
##### M05-T03 — Combining evaluators and handling uncertainty

- **Difficulty.** Intermediate
- **Why it matters.** An aggregate can hide an unacceptable error or an evaluator failure.
- **Concepts.** Hard gates, rule plus proxy cascades, metric applicability, score vectors, disagreement, human escalation and threshold trade-offs.
- **Prerequisites.** [M04-T03](#m04-t03), [M05-T01](#m05-t01), [M05-T02](#m05-t02)
- **Demonstration.** Apply a numeric gate, semantic triage and human review to one fixture and compare with a single averaged score.
- **Exercise and assessment.** Propose and defend an escalation rule with coverage and error counts.
- **Hours.** 1 / 1.5 / 1.5 / 1 / 5 / 3.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test6.html`](docs/test6.html), [`docs/test9.html`](docs/test9.html), [`docs/test13.html`](docs/test13.html)
- **Audit findings.** C02,C05,C09,S02
- **Reuse strategy.** Reuse proxy disagreement and two-layer scoring examples.
- **Teaching and experiment gaps.** Add a decision table, N/A controls and escalation cost.
- **Technical corrections.** Keep hard constraints visible and avoid double-counting correlated evidence.

<a id="m06"></a>
#### M06 — Model judges and comparative evaluation

- **Difficulty.** Intermediate
- **Track.** Core
- **Subject.** Judges
- **Description.** Validate judge evidence with human labels before delegating consequential decisions to an evaluator.
- **Objectives.** Build pointwise and comparative rubrics, measure inter-rater agreement and diagnose judge bias.
- **Prerequisites.** [M04](#m04), [M05](#m05)
- **Labs.** Evaluate identical, frozen responses with human raters, a local or replayed judge and a deterministic baseline.
- **Competencies.** Produce a held-out judge report with valid verdict coverage, per-class errors, agreement and bias checks.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 5 / 4.5 / 3 / 17 / 11

<a id="m06-t01"></a>
##### M06-T01 — Pointwise LLM-as-a-Judge

- **Difficulty.** Intermediate
- **Why it matters.** A model can scale rubric application while producing confident but unsupported labels.
- **Concepts.** Criterion isolation, pointwise scoring, anchors, reference-guided versus reference-free evaluation, evidence spans, schema validation and fallback.
- **Prerequisites.** [M03-T02](#m03-t02), [M04-T02](#m04-t02), [M05-T03](#m05-t03)
- **Demonstration.** Compare a structured saved judge verdict with a human adjudication on the exact same response.
- **Exercise and assessment.** Reject malformed, out-of-range and unsupported verdicts and record why each was unscorable.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test5.html`](docs/test5.html), [`phase-2-evaluation-techniques/llm-as-a-judge/llm_judge_evaluator.py`](phase-2-evaluation-techniques/llm-as-a-judge/llm_judge_evaluator.py), [`phase-2-evaluation-techniques/llm-as-a-judge/banking_bot_test_results.xlsx`](phase-2-evaluation-techniques/llm-as-a-judge/banking_bot_test_results.xlsx), [`config.yaml`](config.yaml)
- **Audit findings.** C01,S04,S07,S08,S09
- **Reuse strategy.** Keep the human-first disagreement review.
- **Teaching and experiment gaps.** Add frozen responses with history, anchor examples and local replay verdicts.
- **Technical corrections.** Align response IDs, validate schema, correct provider defaults and stop guessing verdicts from text.

<a id="m06-t02"></a>
##### M06-T02 — Human agreement, calibration and bias

- **Difficulty.** Intermediate
- **Why it matters.** Human and model disagreements identify ambiguous rubrics, default preferences and systematic miss rates.
- **Concepts.** Percent agreement, confusion matrices, Cohen's kappa intuition, prevalence effects, repeat judge consistency, verbosity/style and model self-preference, held-out calibration.
- **Prerequisites.** [M04-T02](#m04-t02), [M04-T03](#m04-t03), [M06-T01](#m06-t01)
- **Demonstration.** Compare independent human and judge labels on a frozen table using Python and inspect disagreement by slice.
- **Exercise and assessment.** Recalibrate on anchors and report held-out error rates, sample sizes and unresolved disagreements.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/test5.html`](docs/test5.html), [`docs/test7.html`](docs/test7.html), [`docs/test13.html`](docs/test13.html)
- **Audit findings.** C01,C07,C12,S09,V03
- **Reuse strategy.** Use documented disagreements and the perfect trajectory result as review prompts.
- **Teaching and experiment gaps.** Add authoritative evidence labels, second-rater labels and an ambiguous example.
- **Technical corrections.** Distinguish uncertain human labels from adjudicated targets and reconcile sample counts.

<a id="m06-t03"></a>
##### M06-T03 — Pairwise comparisons and ranking

- **Difficulty.** Intermediate
- **Why it matters.** Comparative judgments can simplify preference assessment and are sensitive to order and tie policy.
- **Concepts.** Blind randomization, position swaps, tie and abstain policies, win rates, Bradley–Terry intuition, nontransitivity and multi-model uncertainty.
- **Prerequisites.** [M06-T01](#m06-t01), [M06-T02](#m06-t02)
- **Demonstration.** Score the same answer pairs in reversed order and construct a win/tie table from saved judgments.
- **Exercise and assessment.** Detect an order-sensitive pair and justify whether the evidence supports a ranking.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Build on the pointwise frozen fixture with a revised rubric.
- **Teaching and experiment gaps.** Add three-system comparisons, balanced order and tie controls.
- **Technical corrections.** —

<a id="m07"></a>
#### M07 — Reproducibility, statistics and experiments

- **Difficulty.** Intermediate
- **Track.** Core
- **Subject.** Statistics
- **Description.** Start with visual and intuitive examples, then write small Python analyses on frozen cases.
- **Objectives.** Explain variability, quantify paired uncertainty, choose sample sizes and detect regressions.
- **Prerequisites.** [M04](#m04), [M06](#m06)
- **Labs.** Compare two fictional banking configurations using repeated responses, case-level aggregation and Python resampling.
- **Competencies.** Reproduce the report from a manifest and reach a defensible improvement, regression or inconclusive decision.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 5 / 5.5 / 4.5 / 3 / 18 / 12

<a id="m07-t01"></a>
##### M07-T01 — Variance, repetition and score aggregation

- **Difficulty.** Intermediate
- **Why it matters.** Repeated draws from the same case measure variation within that case and do not add independent case coverage.
- **Concepts.** Analysis units, between/within-case variance, seeds and effective config, repeated measures, macro/micro means, slice weights, denominators and missingness.
- **Prerequisites.** [M01-T02](#m01-t02), [M04-T03](#m04-t03), [M05-T03](#m05-t03)
- **Demonstration.** Plot saved repeated outcomes in a case-by-setting table, change slice weights and observe a reversed aggregate.
- **Exercise and assessment.** Report attempted, valid and scorable rates separately and explain what would reproduce the result.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test2.html`](docs/test2.html), [`phase-1-first-experiments/test2_full_evaluations.py`](phase-1-first-experiments/test2_full_evaluations.py), [`docs/test8.html`](docs/test8.html), [`phase-3-what-you-are-evaluating/temperature-sensitivity/temperature_evaluator.py`](phase-3-what-you-are-evaluating/temperature-sensitivity/temperature_evaluator.py)
- **Audit findings.** C08,C11,S02,S08,V04
- **Reuse strategy.** Reuse repeated tasks and the temperature variation as critique material.
- **Teaching and experiment gaps.** Add grouped replay, warm/cold controls and aggregation walkthrough.
- **Technical corrections.** Qualify one-draw claims and preserve run and stage metadata.

<a id="m07-t02"></a>
##### M07-T02 — Confidence intervals, significance and sample size

- **Difficulty.** Intermediate
- **Why it matters.** Small apparent differences can be sampling noise or too small to matter operationally.
- **Concepts.** Effect size, confidence interval intuition, paired case bootstrap, permutation test intuition, practical significance, power/sample planning and multiplicity.
- **Prerequisites.** [M07-T01](#m07-t01)
- **Demonstration.** Resample whole case pairs in Python and compare the interval with an independent-sample calculation.
- **Exercise and assessment.** Vary sample size or minimum effect and explain why a result is inconclusive without overclaiming equivalence.
- **Hours.** 2 / 2 / 1.5 / 1 / 6.5 / 4.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Treat existing pass-rate tables as hypotheses for new exercises.
- **Teaching and experiment gaps.** Add hand-resampling diagram, code and answer sheet for clustered outputs.
- **Technical corrections.** —

<a id="m07-t03"></a>
##### M07-T03 — Comparing models, prompts and A/B variants

- **Difficulty.** Intermediate
- **Why it matters.** A regression decision depends on what changed, what was held fixed and which risks matter.
- **Concepts.** Paired offline experiments, locked baselines, key slices, noninferiority margins, guardrails, offline versus randomized online A/B effects and regression reporting.
- **Prerequisites.** [M02-T03](#m02-t03), [M07-T02](#m07-t02)
- **Demonstration.** Compare frozen prompt versions on the same case IDs, then simulate a user-randomized A/B with exposure logs.
- **Exercise and assessment.** Write a rollout recommendation with effect size, uncertainty, guardrails, confounds and stopping criteria.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/test8.html`](docs/test8.html), [`docs/test11.html`](docs/test11.html)
- **Audit findings.** C04,C08,C11,V04
- **Reuse strategy.** Keep the comparative examples as discussion prompts.
- **Teaching and experiment gaps.** Add controlled one-variable tests and simulated online outcomes.
- **Technical corrections.** Match inputs and judge or attribute changes explicitly.

### Advanced

<a id="m08"></a>
#### M08 — RAG system evaluation

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** RAG
- **Description.** Evaluate retrieval and generation independently before judging end-to-end answers.
- **Objectives.** Measure ranked retrieval, score claims and citations, and isolate the failing pipeline stage.
- **Prerequisites.** [M05](#m05), [M06](#m06), [M07](#m07)
- **Labs.** Reuse fictional policy guides and create one labeled replay from query through citations.
- **Competencies.** Diagnose a held-out failure and verify a targeted change against retrieval and answer metrics.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 5.5 / 6 / 5 / 3 / 19.5 / 13.5

<a id="m08-t01"></a>
##### M08-T01 — Ingestion, chunking and ranked retrieval

- **Difficulty.** Advanced
- **Why it matters.** A generator cannot reliably cite supporting evidence that the retriever missed.
- **Concepts.** Parsing, chunking and overlap, source IDs, sparse/dense/hybrid retrieval, top-k, gold relevance, Precision@k, Recall@k, MRR, nDCG and unlabeled passages.
- **Prerequisites.** [M04-T01](#m04-t01), [M05-T02](#m05-t02), [M07-T01](#m07-t01)
- **Demonstration.** Hand-score two ranked lists and reproduce metrics in Python before changing chunks in a replay.
- **Exercise and assessment.** Add a graded relevance judgment and explain a case where MRR and Recall@k disagree.
- **Hours.** 2 / 2 / 1.5 / 1 / 6.5 / 4.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test9.html`](docs/test9.html), [`phase-3-what-you-are-evaluating/rag-evaluation/chunker.py`](phase-3-what-you-are-evaluating/rag-evaluation/chunker.py), [`phase-3-what-you-are-evaluating/rag-evaluation/retriever.py`](phase-3-what-you-are-evaluating/rag-evaluation/retriever.py), [`phase-3-what-you-are-evaluating/rag-evaluation/chunks.json`](phase-3-what-you-are-evaluating/rag-evaluation/chunks.json), [`phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx`](phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx)
- **Audit findings.** C02
- **Reuse strategy.** Retain the paragraph chunker, retriever and ranked evidence.
- **Teaching and experiment gaps.** Add gold passage IDs, graded gains and hand-computed solutions.
- **Technical corrections.** Keep document origin stable and declare the handling of empty gold sets.

<a id="m08-t02"></a>
##### M08-T02 — Context sufficiency, answer correctness and citations

- **Difficulty.** Advanced
- **Why it matters.** Answers may be correct without supporting evidence or faithfully repeat stale information.
- **Concepts.** Context relevance versus sufficiency, claim correctness, groundedness/faithfulness, hallucination, citation validity/entailment/completeness, answerability and abstention.
- **Prerequisites.** [M06-T01](#m06-t01), [M08-T01](#m08-t01)
- **Demonstration.** Annotate claims and source IDs for four examples, including a supported but wrong answer and a valid abstention.
- **Exercise and assessment.** Grade a fabricated citation, an unsupported correct answer and an unwarranted refusal separately.
- **Hours.** 2 / 2 / 1.5 / 1 / 6.5 / 4.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test7.html`](docs/test7.html), [`phase-2-evaluation-techniques/groundedness/groundedness_evaluator.py`](phase-2-evaluation-techniques/groundedness/groundedness_evaluator.py), [`docs/test9.html`](docs/test9.html), [`phase-3-what-you-are-evaluating/rag-evaluation/rag_evaluator.py`](phase-3-what-you-are-evaluating/rag-evaluation/rag_evaluator.py)
- **Audit findings.** C02,C03,C12,S04,S09
- **Reuse strategy.** Reuse the invented-specifics and misleading-aggregate cases as exercises.
- **Teaching and experiment gaps.** Add authoritative facts, claim-to-span labels and explicit refusal expectations.
- **Technical corrections.** Separate source evidence from behavior policy, and reconcile conflicting sample labels.

<a id="m08-t03"></a>
##### M08-T03 — Failure attribution, optimization and RAG regression

- **Difficulty.** Advanced
- **Why it matters.** A better response score does not show whether retrieval or generation improved.
- **Concepts.** Oracle retrieval, controlled context swaps, distractors, stale and conflicting sources, held-out slices, threshold tuning and regression gates.
- **Prerequisites.** [M07-T03](#m07-t03), [M08-T01](#m08-t01), [M08-T02](#m08-t02)
- **Demonstration.** Score one baseline against oracle passage and one retrieval change using the same tasks and answer rubric.
- **Exercise and assessment.** Identify the root cause for a replayed failure and specify a regression test with a failure-stage assertion.
- **Hours.** 1.5 / 2 / 2 / 1 / 6.5 / 4.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test9.html`](docs/test9.html), [`phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx`](phase-3-what-you-are-evaluating/rag-evaluation/rag_test_cases.xlsx), [`docs/test11.html`](docs/test11.html)
- **Audit findings.** C02,C04,S09
- **Reuse strategy.** Keep the TC21 and retrieval-confusion walkthroughs.
- **Teaching and experiment gaps.** Add oracle controls, fixed generator outputs and before/after regression fixtures.
- **Technical corrections.** Use answer/claim outcomes and correct sample denominators.

<a id="m09"></a>
#### M09 — Framework adapters and tool selection

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Frameworks
- **Description.** Apply commercial and open tooling through a neutral evaluation contract and compare definitions on matched inputs.
- **Objectives.** Map case objects and metrics, explain assumptions and select an adapter based on evidence and operational needs.
- **Prerequisites.** [M06](#m06), [M07](#m07), [M08](#m08)
- **Labs.** Use one fixture set to compare a hand-computed scorer and two adapter result shapes.
- **Competencies.** Show per-case parity where metrics match and explain one intentional divergence.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4 / 5 / 3.5 / 3 / 15.5 / 10.5

<a id="m09-t01"></a>
##### M09-T01 — Common evaluator contract and framework selection

- **Difficulty.** Advanced
- **Why it matters.** Portable contracts keep experiments reproducible when a framework or judge changes.
- **Concepts.** Case/response IDs, metric intent and input schema, results with valid/error/N/A, provenance, offline runner versus hosted service, cost, telemetry and capability fit.
- **Prerequisites.** [M04-T01](#m04-t01), [M05-T03](#m05-t03), [M07-T03](#m07-t03)
- **Demonstration.** Map one frozen evaluation record to candidate adapter inputs and verify a known score against Python.
- **Exercise and assessment.** Write a tool-choice memo covering local replay, lockfile/platform, data boundary and migration cost.
- **Hours.** 1 / 1.5 / 1 / 1 / 4.5 / 3
- **Status.** Needs Improvement
- **Existing files.** [`docs/test11.html`](docs/test11.html), [`requirements.txt`](requirements.txt), [`config.yaml`](config.yaml)
- **Audit findings.** C04,S06,S08,S15,V02
- **Reuse strategy.** Reuse case-object explanation and framework comparison as a discussion starter.
- **Teaching and experiment gaps.** Add a neutral schema, checked score parity, deterministic preflight and explicit version metadata.
- **Technical corrections.** Distinguish scoring constructs and identify effective settings.

<a id="m09-t02"></a>
##### M09-T02 — DeepEval and RAGAS on frozen RAG records

- **Difficulty.** Advanced
- **Why it matters.** Named metrics can answer different questions and require different labels or model calls.
- **Concepts.** DeepEval test cases, contextual relevance, faithfulness and thresholds. RAGAS variants for context precision, faithfulness and response relevance, reference requirements and judge/embedding calls. Choose DeepEval for Python assertions and RAGAS for retrieval/generation metric suites when prerequisites match.
- **Prerequisites.** [M08-T02](#m08-t02), [M09-T01](#m09-t01)
- **Demonstration.** Walk one saved record through both adapters and compare which passages, claims and answers drive scores. Verify known zero, N/A and timeout cases.
- **Exercise and assessment.** Explain one matched-input metric disagreement, required reference, expected runtime and optional hosted cost.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Correction
- **Existing files.** [`docs/test11.html`](docs/test11.html), [`phase-4-frameworks-and-tools/deepeval-evaluation/test11_deepeval_evaluator.py`](phase-4-frameworks-and-tools/deepeval-evaluation/test11_deepeval_evaluator.py), [`phase-4-frameworks-and-tools/ragas-evaluation/test10_ragas_evaluator.py`](phase-4-frameworks-and-tools/ragas-evaluation/test10_ragas_evaluator.py), [`phase-4-frameworks-and-tools/ragas-evaluation/ragas_test_cases.xlsx`](phase-4-frameworks-and-tools/ragas-evaluation/ragas_test_cases.xlsx)
- **Audit findings.** C03,C04,S03,S08,S15,V01
- **Reuse strategy.** Retain Test 11 explanations and use Test 10 code as an adapter candidate.
- **Teaching and experiment gaps.** Add Test 10 teaching notes, tested variant mapping and saved outputs for replay.
- **Technical corrections.** Pin compatible versions, preflight credentials before calls, join by ID and preserve errors and denominators.

<a id="m09-t03"></a>
##### M09-T03 — promptfoo and OpenAI Evals

- **Difficulty.** Advanced
- **Why it matters.** Declarative and hosted runs can support review workflows once score meaning is understood.
- **Concepts.** promptfoo for declarative prompt/provider matrices and assertions. OpenAI Evals for evaluation definitions, datasets and grader/runs in an OpenAI-centered workflow. Compare portability, supported graders, spend, data visibility and versioning.
- **Prerequisites.** [M09-T01](#m09-t01)
- **Demonstration.** Translate two frozen prompts and one deterministic grading rule into declarative and hosted-style evaluation specs. Inspect mock results locally.
- **Exercise and assessment.** Recommend a tool for a CI matrix and another for a team using managed grading, with limits and a fixture fallback.
- **Hours.** 1.5 / 1.5 / 1 / 1 / 5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Reuse the common contract rather than duplicating metrics.
- **Teaching and experiment gaps.** Add a local matrix lab and an offline mock of the hosted workflow.
- **Technical corrections.** —

<a id="m10"></a>
#### M10 — Agent and workflow evaluation

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Agents
- **Description.** Evaluate what a workflow does, what state it leaves behind and how it recovers under controlled failures.
- **Objectives.** Measure calls, arguments, outputs, observable planning, task completion and recovery within budgets.
- **Prerequisites.** [M05](#m05), [M06](#m06), [M07](#m07), [M08](#m08)
- **Labs.** Replay frozen traces for fictional account and policy tasks against mock tool results and state.
- **Competencies.** Score alternative valid paths and reject a plausible answer that leaves an incorrect or unauthorized state.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 6 / 4.5 / 3 / 18 / 12

<a id="m10-t01"></a>
##### M10-T01 — Execution model, structured calls and tool contracts

- **Difficulty.** Advanced
- **Why it matters.** Tool response quality and authorization can fail independently of language quality.
- **Concepts.** Agent loop, action schemas, tool selection, typed arguments, tool outputs, permissions, required/optional calls, refusals and step limits.
- **Prerequisites.** [M03-T02](#m03-t02), [M05-T03](#m05-t03), [M08-T01](#m08-t01)
- **Demonstration.** Validate two calls to a read-only mock bank tool and compare traces for an unnecessary call and a useful clarification.
- **Exercise and assessment.** Identify an incorrect argument and verify the corresponding result, action and trust boundary.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Correction
- **Existing files.** [`docs/test12.html`](docs/test12.html), [`phase-5-production-eval/agent-evaluation/agent.py`](phase-5-production-eval/agent-evaluation/agent.py), [`phase-5-production-eval/agent-evaluation/tools.py`](phase-5-production-eval/agent-evaluation/tools.py), [`phase-5-production-eval/agent-evaluation/test12_agent_evaluator.py`](phase-5-production-eval/agent-evaluation/test12_agent_evaluator.py), [`phase-5-production-eval/agent-evaluation/agent_test_cases.xlsx`](phase-5-production-eval/agent-evaluation/agent_test_cases.xlsx)
- **Audit findings.** C06,S05,S13
- **Reuse strategy.** Reuse local mock data, tools and visible schemas.
- **Teaching and experiment gaps.** Add typed validators, authorization fixtures and expected tool outcomes.
- **Technical corrections.** Replace unbounded arithmetic evaluation and carry typed tool errors through replay.

<a id="m10-t02"></a>
##### M10-T02 — Trajectories, planning outcomes and final state

- **Difficulty.** Advanced
- **Why it matters.** A path may look plausible while the task remains incomplete, and multiple paths may satisfy the same goal.
- **Concepts.** State invariants, event/order constraints, task completion, alternative plans, trace-grounding, stop reasons, partial success and judgment N/A.
- **Prerequisites.** [M06-T01](#m06-t01), [M10-T01](#m10-t01)
- **Demonstration.** Replay a trace with a missing second step and another with a different valid path. Compare state checks and qualitative judgments.
- **Exercise and assessment.** Explain why a perfect trajectory score can hide missed behavior and defend an outcome-first rubric.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Correction
- **Existing files.** [`docs/test12.html`](docs/test12.html), [`docs/test13.html`](docs/test13.html), [`phase-5-production-eval/trajectory-evaluation/test13_trajectory_evaluator.py`](phase-5-production-eval/trajectory-evaluation/test13_trajectory_evaluator.py), [`phase-5-production-eval/trajectory-evaluation/sample_agent_evaluation_results.json`](phase-5-production-eval/trajectory-evaluation/sample_agent_evaluation_results.json), [`phase-5-production-eval/trajectory-evaluation/results/sample_trajectory_evaluation_results.json`](phase-5-production-eval/trajectory-evaluation/results/sample_trajectory_evaluation_results.json)
- **Audit findings.** C06,C07,S05
- **Reuse strategy.** Retain the Test 12 to Test 13 replay and compare both scoring layers.
- **Teaching and experiment gaps.** Add hard negatives, goal-state predicates, annotated alternative paths and scoring denominators.
- **Technical corrections.** Validate judged dimensions and compute verdicts independently.

<a id="m10-t03"></a>
##### M10-T03 — Recovery, reliability and efficiency

- **Difficulty.** Advanced
- **Why it matters.** Retries may improve success while increasing cost, delay or duplicated side effects.
- **Concepts.** Scripted faults, timeouts, retry budgets, idempotency, interrupted state, recoverability, success per cost and latency versus task completion.
- **Prerequisites.** [M07-T01](#m07-t01), [M10-T02](#m10-t02)
- **Demonstration.** Replay a bounded transient failure and compare retry policy, end state and cost from simulated timings.
- **Exercise and assessment.** Demonstrate a safe retry, then choose a threshold for recovery within budget.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/test12.html`](docs/test12.html), [`phase-5-production-eval/agent-evaluation/agent.py`](phase-5-production-eval/agent-evaluation/agent.py), [`phase-5-production-eval/agent-evaluation/test12_agent_evaluator.py`](phase-5-production-eval/agent-evaluation/test12_agent_evaluator.py)
- **Audit findings.** S02,S05,S13
- **Reuse strategy.** Reuse the practical timeout discussion with mock faults.
- **Teaching and experiment gaps.** Add state snapshots, failure injection, latency and token trace fields.
- **Technical corrections.** Separate infrastructure errors and test idempotency before discussing writes.

<a id="m11"></a>
#### M11 — Safety and responsible AI evaluation

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Safety
- **Description.** Establish a safety measurement plan that covers risky outcomes and permitted use.
- **Objectives.** Classify risk, evaluate refusal and over-refusal, audit fairness and privacy, and verify safety regressions.
- **Prerequisites.** [M04](#m04), [M06](#m06), [M07](#m07)
- **Labs.** Score a synthetic safety set against a fictional bank policy and document uncertain labels.
- **Competencies.** Produce a risk matrix, slice report and explicit release criteria with review paths for severe or ambiguous cases.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 5 / 4.5 / 3 / 17 / 11

<a id="m11-t01"></a>
##### M11-T01 — Risk taxonomy, harmful content and refusal

- **Difficulty.** Advanced
- **Why it matters.** Safety depends on intended policy and on continuing to answer permissible requests.
- **Concepts.** Severity, toxic or harmful output categories, policy versus factual correctness, appropriate refusal, over-refusal and safe alternatives.
- **Prerequisites.** [M04-T02](#m04-t02), [M05-T03](#m05-t03), [M06-T02](#m06-t02)
- **Demonstration.** Label fixed benign assessment fixtures as answer, abstain, refuse or escalate with expected behavior and reason.
- **Exercise and assessment.** Report correct refusals and false refusals with their own denominators and adjudicate a borderline case.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** Needs Correction
- **Existing files.** [`docs/test4.html`](docs/test4.html), [`docs/test5.html`](docs/test5.html), [`docs/test7.html`](docs/test7.html), [`docs/test11.html`](docs/test11.html)
- **Audit findings.** C03,C05,C12
- **Reuse strategy.** Reuse examples of scope, uncertainty and high-stakes policies with fictionalized answers.
- **Teaching and experiment gaps.** Add a severity rubric, acceptable alternatives and balanced refusal fixtures.
- **Technical corrections.** Validate behavior beyond keywords and keep abstention separate.

<a id="m11-t02"></a>
##### M11-T02 — Bias, fairness and privacy controls

- **Difficulty.** Advanced
- **Why it matters.** A global metric can hide subgroup harms, and observability can increase unnecessary data exposure.
- **Concepts.** Counterfactual and matched-slice tests, label and population bias, disparate error rates, consent, data minimization and synthetic sensitive-data checks.
- **Prerequisites.** [M04-T03](#m04-t03), [M07-T02](#m07-t02), [M11-T01](#m11-t01)
- **Demonstration.** Compare matched fictional customers and inspect privacy controls with dummy records.
- **Exercise and assessment.** Explain confounds and identify what evidence and review are needed before a fairness or privacy claim.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** S12
- **Reuse strategy.** Use the fictional banking context without importing personal data.
- **Teaching and experiment gaps.** Add paired cases, synthetic trace receipts and human review protocol.
- **Technical corrections.** —

<a id="m11-t03"></a>
##### M11-T03 — Robustness, safety benchmarks and regression

- **Difficulty.** Advanced
- **Why it matters.** A high benchmark average can hide severe edge cases, instability or a new false refusal.
- **Concepts.** Perturbation controls, held-out safety sets, stress versus representative evaluation, repeated runs, false-pass severity, escalation and lockboxes.
- **Prerequisites.** [M07-T03](#m07-t03), [M11-T01](#m11-t01), [M11-T02](#m11-t02)
- **Demonstration.** Apply harmless formatting and paraphrase variants to a frozen safety set, then compare a policy update by severity.
- **Exercise and assessment.** Design a slice-sensitive safety gate and state what the benchmark cannot establish.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/test4.html`](docs/test4.html), [`docs/test8.html`](docs/test8.html), [`docs/test9.html`](docs/test9.html)
- **Audit findings.** C08,C13
- **Reuse strategy.** Adapt existing scope and robustness discussions.
- **Teaching and experiment gaps.** Add fixed controls, independent labels and reproducible safety regression cases.
- **Technical corrections.** Report independent case counts and preserve critical slices.

<a id="m12"></a>
#### M12 — Defensive red-team evaluation

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Red Teaming
- **Description.** Plan and assess authorized defensive tests of isolated fictional systems using fixed benign scenarios, synthetic records and mock tools.
- **Objectives.** Identify trust boundaries, measure observed policy violations and verify mitigations on matched evidence.
- **Prerequisites.** [M08](#m08), [M10](#m10), [M11](#m11)
- **Labs.** Evaluate canned outcomes from a fictional bank with document and tool trust boundaries, then write a mitigation regression report.
- **Competencies.** Explain what was measured, what was in scope, which fixes held and what evidence remains uncertain.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 5 / 4.5 / 3 / 17 / 11

<a id="m12-t01"></a>
##### M12-T01 — Threat modeling, scope and test design

- **Difficulty.** Advanced
- **Why it matters.** A clear threat model links input channels and assets to the defensive behavior expected of the system.
- **Concepts.** Direct and indirect prompt injection as threat categories, jailbreaks, protected assets, trust boundaries, authorized test scope, containment and harmless fixtures.
- **Prerequisites.** [M08-T03](#m08-t03), [M10-T01](#m10-t01), [M11-T03](#m11-t03)
- **Demonstration.** Diagram user, document and tool trust boundaries. Inspect inert labels for prepared policy-conflict cases.
- **Exercise and assessment.** Specify assets, failure outcomes, negative controls, test boundaries and responsible reporting.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/concepts.html#prompt-injection`](docs/concepts.html#prompt-injection), [`docs/test4.html`](docs/test4.html), [`docs/test9.html`](docs/test9.html)
- **Audit findings.** C13
- **Reuse strategy.** Reuse the glossary and fixed scope examples for discussion.
- **Teaching and experiment gaps.** Add threat-model worksheet and prewritten benign outcome fixtures.
- **Technical corrections.** Treat system controls and authorization as independently testable.

<a id="m12-t02"></a>
##### M12-T02 — Defensive checks for RAG, agents and data exposure

- **Difficulty.** Advanced
- **Why it matters.** Untrusted content, permission mistakes and exposure can occur even when an assistant response sounds appropriate.
- **Concepts.** Indirect document trust, RAG provenance, mock-tool authorization, least privilege, synthetic exposure markers, attack-success denominators and matched normal cases.
- **Prerequisites.** [M10-T02](#m10-t02), [M11-T02](#m11-t02), [M12-T01](#m12-t01)
- **Demonstration.** Compare saved control-off and control-on records from an isolated mock system. Check the simulated authorization decision and whether a dummy marker reached the output.
- **Exercise and assessment.** Calculate observed violation rate by scenario and distinguish authorization failures from correct refusals and unavailable evidence.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** C13
- **Reuse strategy.** Carry forward mock states and separate answer/authorization labels from M10.
- **Teaching and experiment gaps.** Add canned before/after traces, benign marker receipts and a scoring key.
- **Technical corrections.** —

<a id="m12-t03"></a>
##### M12-T03 — Mitigation verification, reporting and defensive tooling

- **Difficulty.** Advanced
- **Why it matters.** A change needs independent evidence on fixed cases, unseen controls and ordinary permitted behavior.
- **Concepts.** Re-test protocols, severity and reproducible evidence, reporting and ownership. Garak and PyRIT report vocabulary and scope constraints. Static contract and replay checks for targeted controls.
- **Prerequisites.** [M12-T02](#m12-t02)
- **Demonstration.** Read prepared Garak and PyRIT report excerpts and reconcile their labels with a manually scored, held-out synthetic fixture.
- **Exercise and assessment.** Write a red-team finding and verification memo with coverage, confirmed failures, false refusals, remediation and remaining risk.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** C13
- **Reuse strategy.** Use offline report interpretation alongside the neutral contract.
- **Teaching and experiment gaps.** Add fictional report exports, outcome labels and mitigation regression worksheet.
- **Technical corrections.** —

### Production

<a id="m13"></a>
#### M13 — Continuous evaluation and releases

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Production Engineering
- **Description.** Turn evaluation evidence into reliable checks and release decisions while preserving diagnostic artifacts.
- **Objectives.** Design a versioned pipeline, define CI/CD quality gates, and decide when to pause or roll back.
- **Prerequisites.** [M07](#m07), [M09](#m09), [M10](#m10), [M12](#m12)
- **Labs.** Turn the bank fixture suite into an offline CI run with immutable candidate artifacts and a release decision.
- **Competencies.** Demonstrate pass, fail and insufficient evidence paths and replay the report from its manifest.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 5.5 / 4.5 / 3 / 17.5 / 11.5

<a id="m13-t01"></a>
##### M13-T01 — Evaluation pipelines and versioned run contracts

- **Difficulty.** Advanced
- **Why it matters.** A run must be attributable to one prompt, model, dataset, scorer and configuration.
- **Concepts.** Build and score separation, immutable run metadata, fixtures and live tiers, parallelism, caching, secure config, evaluator error taxonomy and artifact integrity.
- **Prerequisites.** [M04-T01](#m04-t01), [M07-T01](#m07-t01), [M09-T01](#m09-t01)
- **Demonstration.** Build a fixture-driven pipeline design with preflight, case selection, outputs, version tags and safe report rendering.
- **Exercise and assessment.** Reconstruct a run manifest and classify invalid input, evaluator timeout and valid failure.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Correction
- **Existing files.** [`config.yaml`](config.yaml), [`model_client.py`](model_client.py), [`requirements.txt`](requirements.txt), [`phase-3-what-you-are-evaluating/rag-evaluation/report_generator.py`](phase-3-what-you-are-evaluating/rag-evaluation/report_generator.py)
- **Audit findings.** S02,S06,S07,S08,S10,S11,S14,S15
- **Reuse strategy.** Reuse config, adapters and report layouts as examples to review.
- **Teaching and experiment gaps.** Add dry-run, version contract, harmless markup fixture and reproducible environment profile.
- **Technical corrections.** Separate errors from data, escape reports, verify links and remove tracked secret guidance.

<a id="m13-t02"></a>
##### M13-T02 — CI/CD quality gates and regression evidence

- **Difficulty.** Advanced
- **Why it matters.** A flaky or underpowered gate can block safe changes or let critical regressions through.
- **Concepts.** Stable baselines, fast and slow tiers, absolute and relative thresholds, uncertainty, critical-slice gates, retry policy, artifact review and exceptions.
- **Prerequisites.** [M07-T03](#m07-t03), [M11-T03](#m11-t03), [M13-T01](#m13-t01)
- **Demonstration.** Simulate candidate releases with performance regressions and metric failures, using the same locked fixtures.
- **Exercise and assessment.** Implement a three-way decision and justify how a critical regression overrides aggregate improvement.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** V04
- **Reuse strategy.** Build on the fixture scorecard and the neutral contract.
- **Teaching and experiment gaps.** Add local CI simulation, audit log, uncertainty and infrastructure-failure tests.
- **Technical corrections.** —

<a id="m13-t03"></a>
##### M13-T03 — Release decisions, rollback and governance

- **Difficulty.** Advanced
- **Why it matters.** A release requires ownership, explicit risk acceptance and a reversible decision backed by evidence.
- **Concepts.** Version sign-off, model and prompt change management, canary/shadow comparison, kill criteria, rollback, approval trail and evidence retention.
- **Prerequisites.** [M02-T03](#m02-t03), [M12-T03](#m12-t03), [M13-T02](#m13-t02)
- **Demonstration.** Write a release packet and run a tabletop rollback after a synthetic severe-slice regression.
- **Exercise and assessment.** Present the owner, decision, rollback trigger, evidence link and follow-up dataset change.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** C13,V04
- **Reuse strategy.** Reuse the training traces and scores as mock release evidence.
- **Teaching and experiment gaps.** Add policy, sign-off and rollback templates plus decision scenarios.
- **Technical corrections.** —

<a id="m14"></a>
#### M14 — Observability, operations and review loops

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Production Engineering
- **Description.** Follow live-style evidence from a trace into triage, labeling, drift detection and regression checks.
- **Objectives.** Instrument traces, sample responsibly, define alerts and understand cost, latency and operational reliability.
- **Prerequisites.** [M07](#m07), [M10](#m10), [M11](#m11), [M13](#m13)
- **Labs.** Simulate a bank support incident using synthetic traces, a dashboard export and an offline score pipeline.
- **Competencies.** Explain which signal moved, identify the cause and turn it into a versioned regression case with a traceable owner.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 6 / 4 / 3 / 17.5 / 12

<a id="m14-t01"></a>
##### M14-T01 — Traces, monitoring and Langfuse

- **Difficulty.** Advanced
- **Why it matters.** Observability makes eval context inspectable across stages and repeated incidents.
- **Concepts.** Trace/span/generation concepts, correlation IDs, tags, scored observations, telemetry loss and redaction. Choose Langfuse for inspectable LLM traces and scores with suitable deployment/data controls. Consider OpenTelemetry for cross-service context, with application-specific quality scoring elsewhere.
- **Prerequisites.** [M11-T02](#m11-t02), [M13-T01](#m13-t01)
- **Demonstration.** Follow a bank request through a saved trace and associate outcome, case ID, model and latency. Optionally reproduce with local Langfuse.
- **Exercise and assessment.** Annotate a trace and show which fields to retain, redact or drop before collection.
- **Hours.** 1.5 / 2 / 1 / 1 / 5.5 / 4
- **Status.** Needs Correction
- **Existing files.** [`docs/test14.html`](docs/test14.html), [`phase-5-production-eval/langfuse-observability/test14_langfuse_evaluator.py`](phase-5-production-eval/langfuse-observability/test14_langfuse_evaluator.py), [`phase-5-production-eval/langfuse-observability/docker-compose.yml`](phase-5-production-eval/langfuse-observability/docker-compose.yml)
- **Audit findings.** C05,S07,S08,S12,S16,V02
- **Reuse strategy.** Preserve the walkthrough and dashboard exploration.
- **Teaching and experiment gaps.** Add de-identified export/replay, telemetry failure and trace coverage example.
- **Technical corrections.** Correct provider/range claims and use loopback, safe credentials and payload controls.

<a id="m14-t02"></a>
##### M14-T02 — Production sampling, human feedback, drift and alerts

- **Difficulty.** Advanced
- **Why it matters.** Trace populations, user feedback and evaluator behavior can change independently.
- **Concepts.** Representative trace sampling, consent and retention, label delays, human-in-the-loop triage, selection bias, input/answer/evaluator drift, control charts and alert triage.
- **Prerequisites.** [M04-T03](#m04-t03), [M07-T02](#m07-t02), [M14-T01](#m14-t01)
- **Demonstration.** Compare synthetic weeks with changing traffic mix and delayed labels. Produce an alert and review queue.
- **Exercise and assessment.** Distinguish drift from instrumentation loss and promote reviewed cases into an offline suite.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** S12,V04
- **Reuse strategy.** Use Test 14 categories as context for a synthetic monitoring dataset.
- **Teaching and experiment gaps.** Add trace sampling weights, dashboards, feedback routing and alert scenarios.
- **Technical corrections.** —

<a id="m14-t03"></a>
##### M14-T03 — Cost, tail latency and operational reliability

- **Difficulty.** Advanced
- **Why it matters.** Per-call averages can hide long waits, retry spend and the cost of an evaluation pipeline itself.
- **Concepts.** TTFT, TPOT, duration, latency percentiles, tokens, cost per valid case, concurrency, error budget, SLOs and degradation modes.
- **Prerequisites.** [M07-T01](#m07-t01), [M10-T03](#m10-t03), [M14-T01](#m14-t01)
- **Demonstration.** Compute p50/p95 and cost per valid outcome from a trace export that includes warm-ups, retries and judge calls.
- **Exercise and assessment.** Defend a cost and latency budget and diagnose an incident where quality improved but reliability worsened.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** Needs Improvement
- **Existing files.** [`docs/concepts.html`](docs/concepts.html), [`docs/test8.html`](docs/test8.html), [`docs/test11.html`](docs/test11.html), [`docs/test14.html`](docs/test14.html)
- **Audit findings.** C08,S03,V04
- **Reuse strategy.** Reuse the performance definitions and real latency anomalies as prompts.
- **Teaching and experiment gaps.** Add token and percentile calculations, load profiles and cost model.
- **Technical corrections.** Separate inference, evaluation and end-to-end timing and record failed attempts.

<a id="m15"></a>
#### M15 — End-to-end capstone

- **Difficulty.** Advanced
- **Track.** Core
- **Subject.** Production Engineering
- **Description.** Demonstrate ownership of evaluation from goals and annotated data to release evidence and incident follow-up.
- **Objectives.** Integrate a release-quality suite, explain decision trade-offs and defend results in a teaching demonstration.
- **Prerequisites.** [M08](#m08), [M09](#m09), [M10](#m10), [M11](#m11), [M12](#m12), [M13](#m13), [M14](#m14)
- **Labs.** Submit a replayable evaluation package for one fictional feature spanning chatbot, RAG or agent behavior and production evidence.
- **Competencies.** A peer can reproduce the result, challenge the decision and rerun a regression after a simulated incident.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 2 / 3.5 / 4 / 3.5 / 13 / 8

<a id="m15-t01"></a>
##### M15-T01 — Design review and reproducible suite

- **Difficulty.** Advanced
- **Why it matters.** A clear evidence plan lets teammates challenge a metric before the implementation hides its assumptions.
- **Concepts.** Acceptance criteria, risk assessment, golden set versions, independent rubric review, paired baselines and environment constraints.
- **Prerequisites.** [M08-T03](#m08-t03), [M09-T01](#m09-t01), [M10-T03](#m10-t03), [M11-T03](#m11-t03), [M13-T02](#m13-t02)
- **Demonstration.** Draft the contract, choose a track and have a peer run your frozen evaluation plan.
- **Exercise and assessment.** Submit a verified manifest and a suite containing good, incorrect, ambiguous and unscorable cases.
- **Hours.** 1 / 2 / 2 / 1.5 / 6.5 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** V03,V04
- **Reuse strategy.** Draw on the banking fixtures and course scorecards.
- **Teaching and experiment gaps.** Add briefs for FAQ, support RAG and account workflow variants and a grading rubric.
- **Technical corrections.** —

<a id="m15-t02"></a>
##### M15-T02 — Decision defense, incident response and teaching

- **Difficulty.** Advanced
- **Why it matters.** Releasing and teaching an evaluation requires explaining what evidence can support under uncertainty.
- **Concepts.** Decision memo, incident diagnosis, drift or regression, ownership, release/hold/rollback, credible evidence and peer feedback.
- **Prerequisites.** [M12-T03](#m12-t03), [M13-T03](#m13-t03), [M14-T02](#m14-t02), [M14-T03](#m14-t03), [M15-T01](#m15-t01)
- **Demonstration.** Diagnose a scripted incident, add a regression test and teach one evaluation failure with a reproducible demonstration.
- **Exercise and assessment.** Defend the release decision and show a peer can verify the corrected outcome from the submitted artifacts.
- **Hours.** 1 / 1.5 / 2 / 2 / 6.5 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** V04
- **Reuse strategy.** Use selected historical examples as prompts for the oral defense.
- **Teaching and experiment gaps.** Add instructor scoring rubric, incident variants and model answers.
- **Technical corrections.** —

### Specialized / Expert

<a id="m16"></a>
#### M16 — Evaluation across languages and modalities

- **Difficulty.** Expert
- **Track.** Elective
- **Subject.** Specialization
- **Description.** Adapt data and rubrics when text quality measures fail to capture language, visual or long-context requirements.
- **Objectives.** Design slice-aware metrics and evidence for three settings with different failure modes.
- **Prerequisites.** [M04](#m04), [M05](#m05), [M07](#m07), [M08](#m08)
- **Labs.** Build a small, domain-specific slice on top of the bank case contract and calibrate it.
- **Competencies.** Demonstrate why a baseline score changes meaning and validate a revised rubric on held-out cases.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 5.5 / 4.5 / 3 / 17.5 / 11.5

<a id="m16-t01"></a>
##### M16-T01 — Multilingual and localized evaluation

- **Difficulty.** Expert
- **Why it matters.** Translation coverage and native-language correctness can diverge, especially for domain terms.
- **Concepts.** Native annotations, locale and register, code-switching, script normalization, multilingual embeddings and stratified comparisons.
- **Prerequisites.** [M04-T03](#m04-t03), [M05-T02](#m05-t02), [M07-T02](#m07-t02)
- **Demonstration.** Compare translated and native fictional FAQ cases against language-specific policies and evaluate normalization choices.
- **Exercise and assessment.** Produce a per-locale scorecard and identify translation leakage and subgroup uncertainty.
- **Hours.** 1.5 / 1.5 / 1.5 / 1 / 5.5 / 3.5
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Retain the case schema and threshold lesson.
- **Teaching and experiment gaps.** Add native reviewer guidance, parallel fixtures and locale-specific test controls.
- **Technical corrections.** —

<a id="m16-t02"></a>
##### M16-T02 — Multimodal evaluation

- **Difficulty.** Expert
- **Why it matters.** A fluent answer can hallucinate a visual detail or attach the right explanation to the wrong region.
- **Concepts.** OCR/chart and image QA, visual evidence, modality-specific metrics, region grounding, abstention and accessibility.
- **Prerequisites.** [M04-T01](#m04-t01), [M05-T03](#m05-t03), [M08-T02](#m08-t02)
- **Demonstration.** Score answers to fictional fee charts using annotated cells, regions and text references.
- **Exercise and assessment.** Identify unsupported claims and report errors by modality and extraction stage.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Adapt claim and citation scoring to image regions.
- **Teaching and experiment gaps.** Add accessible synthetic charts, labeled regions and verification examples.
- **Technical corrections.** —

<a id="m16-t03"></a>
##### M16-T03 — Long-context evidence and memory

- **Difficulty.** Expert
- **Why it matters.** More context can degrade evidence use or change which policy applies.
- **Concepts.** Position sensitivity, interference, distractors, multi-document synthesis, recency, context budget and memory consistency.
- **Prerequisites.** [M01-T01](#m01-t01), [M07-T03](#m07-t03), [M08-T03](#m08-t03)
- **Demonstration.** Use saved prompts with the same evidence in different positions and label unsupported conclusions.
- **Exercise and assessment.** Report controlled position and context-length effects across slices.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Reuse the RAG evidence and oracle-control structure.
- **Teaching and experiment gaps.** Add controlled contexts, staged difficulty and held-out document families.
- **Technical corrections.** —

<a id="m17"></a>
#### M17 — Specialized outputs and coordinated systems

- **Difficulty.** Expert
- **Track.** Elective
- **Subject.** Specialization
- **Description.** Verify outcomes for typed extraction, generated code and collaboration between agents.
- **Objectives.** Choose precise task outcomes and analyze errors hidden by generic text scores.
- **Prerequisites.** [M03](#m03), [M07](#m07), [M10](#m10), [M11](#m11)
- **Labs.** Apply the case contract to one specialization and verify outcomes with deterministic fixtures.
- **Competencies.** Submit a domain-specific failure taxonomy and reproducible scorecard against examples that defeat a generic judge.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 4.5 / 6 / 4.5 / 3 / 18 / 12

<a id="m17-t01"></a>
##### M17-T01 — Structured extraction and classification

- **Difficulty.** Expert
- **Why it matters.** A document can produce correct fields with wrong entities or invalid records.
- **Concepts.** Field and record scoring, strict/normalized matches, null/unknown, span alignment, type and value checks, confidence and per-class error.
- **Prerequisites.** [M03-T02](#m03-t02), [M04-T02](#m04-t02), [M07-T01](#m07-t01)
- **Demonstration.** Score synthetic form extraction against typed fields and entity IDs with Python.
- **Exercise and assessment.** Explain how micro F1 hides a critical rare-field miss and add a matching gate.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Adapt beginner schema checks and proposed annotation contract.
- **Teaching and experiment gaps.** Add forms, field-level answer key and negative controls.
- **Technical corrections.** —

<a id="m17-t02"></a>
##### M17-T02 — Code-generation evaluation

- **Difficulty.** Expert
- **Why it matters.** Generated code needs evidence from compilation, behavior, safety and resource bounds.
- **Concepts.** Functional tests, cases and hidden tests, pass@k intuition, runtime/error categorization, resource controls, offline isolation and static review.
- **Prerequisites.** [M03-T02](#m03-t02), [M07-T01](#m07-t01), [M11-T03](#m11-t03)
- **Demonstration.** Evaluate canned benign pure functions against fixed inputs and captured results in a restricted teaching runner.
- **Exercise and assessment.** Distinguish a compilation failure, wrong answer and timeout and interpret pass@k assumptions.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** —
- **Reuse strategy.** Reuse typed outcomes and locked holdout principles.
- **Teaching and experiment gaps.** Add harmless functions, run-result fixtures and isolated test harness design.
- **Technical corrections.** —

<a id="m17-t03"></a>
##### M17-T03 — Multi-agent coordination

- **Difficulty.** Expert
- **Why it matters.** A successful individual reply can hide lost handoffs or inconsistent shared state.
- **Concepts.** Role boundaries, coordination and handoff metrics, shared state, conflict resolution, redundancy, team-level success and coordination overhead.
- **Prerequisites.** [M10-T02](#m10-t02), [M10-T03](#m10-t03), [M11-T03](#m11-t03)
- **Demonstration.** Replay a mock support handoff where one agent omits a required state field. Compare with a valid delegated workflow.
- **Exercise and assessment.** Verify global invariants, handoff quality and team cost from saved events.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** C06
- **Reuse strategy.** Extend the single-agent trace schema with actor and handoff IDs.
- **Teaching and experiment gaps.** Add coordination and conflicting-state fixtures with outcome labels.
- **Technical corrections.** —

<a id="m18"></a>
#### M18 — Evaluator robustness and evaluation research

- **Difficulty.** Expert
- **Track.** Elective
- **Subject.** Specialization
- **Description.** Keep scores meaningful as evaluators, datasets and deployed models change.
- **Objectives.** Stress-test evaluators, manage model migration, identify contamination risk and assess emerging methods.
- **Prerequisites.** [M06](#m06), [M07](#m07), [M12](#m12), [M13](#m13), [M14](#m14)
- **Labs.** Audit an evaluator and recommend a replacement strategy using anchors, holdout tests and monitored deployment evidence.
- **Competencies.** Deliver a reproducible audit with known limits and an evidence-based tool or research recommendation.
- **Completion.** Complete all topic assessments and submit the module artifact described above for peer or instructor replay.
- **Hours.** 5.5 / 5.5 / 5 / 3 / 19 / 12.5

<a id="m18-t01"></a>
##### M18-T01 — Advanced judge design and evaluator robustness

- **Difficulty.** Expert
- **Why it matters.** Judge ensembles and better prompts remain vulnerable to common correlated errors.
- **Concepts.** Evidence-conditioned judgments, multi-judge agreement versus accuracy, selective review, style perturbations, evaluator drift and defensive handling of untrusted inputs.
- **Prerequisites.** [M06-T02](#m06-t02), [M06-T03](#m06-t03), [M12-T03](#m12-t03)
- **Demonstration.** Compare judge configurations on fixed ambiguous and transformed answers, then estimate reliability and review rates.
- **Exercise and assessment.** Justify a human escalation boundary and explain one shared judge blind spot.
- **Hours.** 2 / 2 / 1.5 / 1 / 6.5 / 4.5
- **Status.** Needs Improvement
- **Existing files.** [`docs/test7.html`](docs/test7.html), [`docs/test13.html`](docs/test13.html), [`phase-5-production-eval/trajectory-evaluation/results/sample_trajectory_evaluation_results.json`](phase-5-production-eval/trajectory-evaluation/results/sample_trajectory_evaluation_results.json)
- **Audit findings.** C07,C12,S04,S05
- **Reuse strategy.** Retain the false-confidence examples as hard negatives.
- **Teaching and experiment gaps.** Add independent anchors, repeat tests and disagreement/error review.
- **Technical corrections.** Validate score consistency and delimit evidence and input roles.

<a id="m18-t02"></a>
##### M18-T02 — Benchmark contamination and model migration

- **Difficulty.** Expert
- **Why it matters.** Benchmarks can overstate capability and model swaps can change outputs, costs and judge behavior simultaneously.
- **Concepts.** Time/source holdouts, contamination and benchmark overfitting, matched migration suites, rating comparability, shadowing and rollback.
- **Prerequisites.** [M04-T03](#m04-t03), [M07-T03](#m07-t03), [M13-T03](#m13-t03)
- **Demonstration.** Compare public-style versus private synthetic holdouts, then simulate migration with old/new model and fixed/judge variants.
- **Exercise and assessment.** Identify confounds and defend a migration plan for rare and severe slices.
- **Hours.** 1.5 / 2 / 1.5 / 1 / 6 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** C11,V03
- **Reuse strategy.** Reuse the benchmark example and release packet structure.
- **Teaching and experiment gaps.** Add sealed slices, contamination indicators and migration fixtures.
- **Technical corrections.** —

<a id="m18-t03"></a>
##### M18-T03 — Emerging evaluation methods and research literacy

- **Difficulty.** Expert
- **Why it matters.** Evaluation methods need a testable hypothesis and comparisons against simpler baselines.
- **Concepts.** Active evaluation and adaptive sampling, preference modeling, redacted behavioral simulations, living benchmarks, measure validity and reproducible method reviews.
- **Prerequisites.** [M06-T03](#m06-t03), [M07-T03](#m07-t03), [M14-T02](#m14-t02)
- **Demonstration.** Simulate risk-aware active case selection, then compare estimates and label costs with uniform sampling.
- **Exercise and assessment.** Write a method card with construct, assumptions, evidence limits and a replication plan.
- **Hours.** 2 / 1.5 / 2 / 1 / 6.5 / 4
- **Status.** New
- **Existing files.** —
- **Audit findings.** V04
- **Reuse strategy.** Reuse the evaluation contract and comparison harness.
- **Teaching and experiment gaps.** Add method review template, simulation data and a replication exercise.
- **Technical corrections.** —
