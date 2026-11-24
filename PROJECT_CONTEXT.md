# TestNeural LLM Academy project context

## Purpose and identity

TestNeural LLM Academy is a public learning site for self-study and instructor-led teaching. Its first course, **LLM Evaluation Engineering**, supports both focused study and a complete path from foundations through production. The academy uses the tagline **Learn • Evaluate • Build** and the credit **Developed by: Amit Baderia**. The target domain is [llmacademy.testneural.in](https://llmacademy.testneural.in/).

## Architecture and repository

The academy uses static HTML, CSS, and vanilla JavaScript. A Python standard-library generator builds two checked-in HTML pages. The homepage and published examples use local companion assets. The curriculum HTML embeds its styles, JavaScript, and data for offline use. Links to example pages and workbook downloads still need the companion files. Learners run the Python exercises separately.

| Location | Purpose |
| --- | --- |
| [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md) | Authoritative curriculum, including topic IDs, dependency definitions, path membership, and hour estimates |
| [TEACHING_GUIDELINES.md](TEACHING_GUIDELINES.md) | Required authoring and review standard for every new or revised lesson |
| [docs/lessons/m02-t01.md](docs/lessons/m02-t01.md) | First complete learner-facing chapter and an example of the teaching standard |
| [docs/lessons/m02-t02.md](docs/lessons/m02-t02.md) | Complete chapter on evidence, reference answers, and versioned benchmarks |
| [docs/generate_master_curriculum.py](docs/generate_master_curriculum.py) | Validates curriculum data and generates the homepage and interactive curriculum |
| [docs/index.html](docs/index.html), [docs/home.html](docs/home.html) | Generated homepage and compatibility entry point |
| [docs/master-curriculum.html](docs/master-curriculum.html), [homepage template](docs/templates/academy-home.html) | Standalone curriculum and homepage source template |
| [docs/assets/](docs/assets/) | Shared academy styles, behavior, and approved V1 branding under `branding/` |
| [Learning modes](docs/learning_modes.js), [Learning Navigator](docs/learning_navigator.js), [roadmap](docs/learning_roadmap.js), [progress backups](docs/learning_progress.js) | JavaScript embedded in the generated curriculum |
| [Read Aloud](docs/assets/lesson-reader.js) | Native speech controller embedded in the curriculum and shared by published experiment lessons |
| [docs/COURSE_AUDIT_REPORT.md](docs/COURSE_AUDIT_REPORT.md), [concepts reference](docs/concepts.html) | Course audit and published reference material |
| `docs/test*.html`, `phase-0-foundations/` through `phase-5-production-eval/` | Published example pages, existing lessons, and experiments |
| [scripts/validate_static_site.py](scripts/validate_static_site.py), [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Public file validation and general static hosting guidance |

Change curriculum definitions in Markdown and presentation in the generator, source templates, or named JavaScript and CSS sources. After editing any of these inputs, regenerate both pages, check synchronization, and validate the public file set before handing off the change.

```bash
python3 docs/generate_master_curriculum.py
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
```

## Navigation and progress

The homepage puts Quick Learning and Complete Course first. The homepage and curriculum share this primary order.

1. **Quick Learning** contains focused study plans and the Learning Paths comparison with all seven paths, plus the preparation checklist.
2. **Complete Course** shows the full sequence and labels preparation and electives as optional.
3. **Learning Roadmap** shows dependencies and supports SVG, PNG, and standalone HTML downloads.
4. **About the Course** contains course outcomes, hour estimates, and progress controls.
5. **Resources** links to published examples, the concepts reference, and the Teaching Plan. The former coverage link takes readers to the public example links.

Both learning modes use the same topic IDs and content. Quick Learning links carry both the path and the topic in the URL fragment, so reload and browser history retain the exact lesson. The guided view temporarily moves the original topic material from Complete Course and restores it when the learner leaves. Required prerequisites appear in the lesson sequence. Complete Course keeps its existing topic links and provides module breadcrumbs.

Read Aloud uses the browser’s native speech synthesis. In both learning modes, the **Listen** controls sit in a sticky right sidebar at viewport widths of 75rem or more. Below that breakpoint, a closed-by-default disclosure opens the same controls above the lesson. Closing it leaves playback running. Standalone experiments use the compact disclosure. The reader speaks the lesson or a selected section in small passages and highlights the text without moving the page. It skips controls, code blocks, output transcripts, and solution sections. Changing voice or speed restarts the current paragraph and keeps paused narration paused. Changing lessons stops playback. Hiding the tab pauses narration until the learner chooses Resume.

The Voice menu shows all distinct browser-reported English voices in groups for India, the US, the UK, and Other English. It displays the names and language codes provided by the browser. Default selection gives priority to name-based quality hints such as “Natural” or “Enhanced,” then favors India among comparable options. These names cannot establish audio quality or gender. The reader reports when it finds only voices without those hints. **Preview Voice** auditions the dropdown choice without saving it. Stop narration before previewing. **Use Voice** saves the selected voice and applies it to lessons. Speed and the saved voice use browser-local storage when available. The reader updates the list when the browser signals a change. If a saved voice is missing, it uses an available fallback and restores the saved voice if it returns. With no listed English voice, it asks the browser for English and disables voice selection and preview. Unsupported browsers show a short notice and leave lesson text available.

The shared reading layout presents the introduction, concepts, demonstrations, and exercise in study order. On wide screens, prose, headings, dividers, code, and examples share a flexible reading column beside the Listen sidebar. At narrower breakpoints, the reading column fills the available width. Guided lessons show the path in the breadcrumb and group the time estimate, completion count, and progress bar below the title. These details wrap when space is limited. Breadcrumb and study navigation links use hover styling and visible keyboard focus. Links in the lesson text keep their underlines. Outline lessons reuse the authored module objectives and label them as module-wide goals. Setup, expected outputs, answer sections, time estimates, and nonempty prerequisites use native disclosures. An outline notice distinguishes planning material from full lessons that still need to be written.

Complete chapters live in `docs/lessons/` under their lowercase topic ID. The generator places the chapter in the same shared topic view for Quick Learning and Complete Course. Use Markdown headings from level 2, the existing inline and list syntax, and labeled `python`, `bash`, or `text` fences.

Read and apply [TEACHING_GUIDELINES.md](TEACHING_GUIDELINES.md) before drafting or revising any lesson. Use it again to review the finished chapter. Begin with a familiar situation and teach why the concept matters before naming it. Follow up with a worked example, an offline lab with verified console output, and practice with separate solutions. Keep the topic's approved objectives and scope. Keep internal file mappings and development notes in [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md) and the [audit report](docs/COURSE_AUDIT_REPORT.md). The generator uses those fields for internal validation. Topics without a chapter still show their current outline.

The mandatory **Beginner Python Execution Standard** makes the online editor the first route for practice. The generator adds the editor link beside Copy Code for beginner Python blocks, and the link opens separately. Each block contains the sample data and code needed for a clean run. M01-T01 is **Rewritten — Awaiting Human Teaching Review**. Its proposed reference sequence follows one bank conversation from a missing follow-up through a controlled comparison of short and long evidence. The teaching guidelines record technical validation and human teaching-quality approval separately. The owner requested work on M03-T01 while human review of the earlier chapters is pending.

M01-T01 uses the message-order simulation to show what the app would send. A separate model test would check whether the service accepts that order. The final automated audit clarified this distinction, what the exact-match script checks, and how the assignment changes which group gets removed first. All seven Python activities and expected outputs were preserved. Human review of the lesson and browser workflow remains pending.

M01-T02 is **Rewritten — Awaiting Human Teaching Review**. It uses the same browser editor workflow and builds from a saved bank reply to simulated next-piece draws and a comparison of saved outcomes. Learners check the actual prompt and model version before attributing a difference to a sampling setting. All seven Python programs and their output examples were preserved. The 15 isolated Python runs and 29 non-browser tests passed. The live editor workflow and beginner comprehension still need human review.

M02-T01 is **Rewritten — Awaiting Human Teaching Review**. The Harbor Leaf story progresses from checking a single amount to deciding whether a small FAQ trial should go ahead. Learners document the evidence for each dimension, choose a primary failure, and keep unresolved judgments visible. The online editor workflow uses the seven original standalone Python snippets. A new independent assignment asks learners to review three saved attempts and plan a comparison that changes only the supplied policy excerpt.

M02-T02 is **Rewritten — Awaiting Human Teaching Review**. The Harbor Leaf chapter follows one policy change from source selection through reference answers, an eight-case benchmark, and a recorded scoring revision. A boundary question asks learners to choose the test that distinguishes the approved fee rule from one that charges at the minimum. The seven standalone programs use the online editor workflow. All 16 isolated Python runs and 29 non-browser tests passed. The first-time learner and live editor review remain pending.

M02-T03, **Offline, online and the evaluation lifecycle**, is **Rewritten — Awaiting Human Teaching Review**. The Harbor Leaf chapter takes learners from two saved replies through a release block, a repaired candidate’s canary, and a seven-case comparison after an incident. All 18 isolated Python runs and 29 non-browser tests passed. The replies, ratings, and timing records are fictional. Manual browser checks and first-time learner review remain pending.

M03-T01, [Exact match, normalization and rules](docs/lessons/m03-t01.md), is **Rewritten — Awaiting Human Teaching Review**. It compares exact text, normalized account names, boundary patterns, and a typed fee check on fictional Harbor Leaf replies. Sixteen isolated Python runs, static-site validation, and all 29 checked-in non-browser tests passed. The Copy Code, guided navigation, and Read Aloud tests derive their authored chapter list from curriculum topic order and matching lesson Markdown files. The live editor and first-time learner review remain pending.

M03-T02, [Structured output and schema validation](docs/lessons/m03-t02.md), is **Rewritten — Awaiting Human Teaching Review**. The fictional fee checker separates parsing, shape and schema errors, policy mismatches, unresolved evidence, and missing replies. Eighteen isolated Python runs, static-site validation, and all 29 checked-in non-browser tests passed with eight authored chapters. Browser and first-time learner review remain pending.

M03-T03, [Rubrics and a first human evaluation](docs/lessons/m03-t03.md), is **Rewritten — Awaiting Human Teaching Review**. The chapter uses full fictional Harbor Leaf replies to teach blind review, separate accuracy and completeness judgments, evidence notes, and how to resolve a disputed score. Python summarizes supplied judgments. The 16 isolated Python runs and all 29 checked-in non-browser tests passed with nine authored chapters. Browser and first-time learner review remain pending.

M04-T01, [Golden schemas, provenance and versioning](docs/lessons/m04-t01.md), is **Rewritten — Awaiting Human Teaching Review**. It converts a fictional worksheet slice to JSONL and keeps dataset versions, captured replies, and replay results separate. All 17 isolated Python runs and 29 checked-in non-browser tests passed with ten authored chapters. This Intermediate chapter supplies its own editor links immediately before the code blocks. The Copy Code test checks that placement as well as automatic toolbar links. Browser and first-time learner review remain pending.

M04-T02, [Annotation, adjudication and synthetic data](docs/lessons/m04-t02.md), is **Rewritten — Awaiting Human Teaching Review**. Learners write a label guide, resolve a disputed threshold case while preserving the original labels, and decide which fictional drafts to accept, hold, or reject. The lab records source provenance and reuse permission separately from label review. All 16 isolated Python runs and 29 checked-in non-browser tests passed with eleven authored chapters. Browser and first-time learner review remain pending.

M04-T03, [Sampling, holdouts, leakage and maintenance](docs/lessons/m04-t03.md), is **Rewritten — Awaiting Human Teaching Review**. The fictional Harbor Leaf review compares traffic and stress coverage, checks document families across a split, and drafts an August refresh while preserving the July benchmark. All 16 isolated Python runs and 29 checked-in non-browser tests passed with twelve authored chapters. Browser and first-time learner review remain pending.

[M01-T01](docs/lessons/m01-t01.md) covers tokens, message roles, and context budgets. [M01-T02](docs/lessons/m01-t02.md) uses toy sampling and saved attempts to teach settings and repeatability. [M01-T03](docs/lessons/m01-t03.md) completes Module 1 with a request trace and an offline smoke test that distinguishes wrong policy claims from missing or unreadable replies. Module 2 is also complete locally, with a verified benchmark lab in M02-T02 and a simulated incident replay in [M02-T03](docs/lessons/m02-t03.md). With M04-T03 authored, 41 topics await full chapter development. The next unfinished topic is M05-T01, **Token F1, BLEU, ROUGE and reference metrics**.

The Learning Navigator launcher appears on guided lessons at the bottom of the desktop course sidebar. On narrower screens it becomes a bottom-left icon with reserved space beside the reading column. It opens a native dialog that shows the path order, prerequisites, current lesson, and completion state. Selecting a node opens the lesson in Quick Learning. Zoom and pan are retained per path while the page stays open.

Continue Learning opens the first unfinished required topic in order. In Quick Learning and About the Course this opens a guided lesson, while Complete Course resumes in its own view. Progress is stored in the current browser's local storage when available. It does not synchronize across devices. The versioned JSON backup transfers completed topic IDs and the optional selected path. Imports require a preview and explicit apply, with merge or replace available. Reset requires confirmation.

## Deployment and development boundaries

The production plan uses a dedicated NGINX virtual host and Let's Encrypt on the Ubuntu VPS. The approved web root is `/var/www/llm-evaluation/docs` with a public URL allowlist. The private runbook specifies a read-only GitHub deploy key and isolated SSH alias `github-llm-academy`. It places the deployment script at `/var/www/llm-evaluation.deploy.sh` and validates a temporary checkout before fast-forwarding production. The vhost files, runbook, and script are maintained outside the public checkout. Production operations require owner approval and are performed by the owner. The public homepage and curriculum served the `aa01ca7` release at `/` and `/master-curriculum.html` during website QA. See the [static hosting guidance](docs/DEPLOYMENT.md) for the release checks.

This supersedes the earlier plan to version production templates here and serve from a separate release symlink. Direct serving from the approved checkout path keeps the root in `docs/`, so checkout updates are not atomic. The production runbook records how to recover with a reviewed revert and how to restore only the academy virtual host.

Develop from local `main`, which tracks clean GitHub `origin/main`. The initial public release was published from `academy-public-release` at `aa01ca7`. The local `archive/pre-clean-main-72c2e33` branch preserves the earlier history, including retired production files. Keep that branch local and outside any public merge or push.

Keep the learning site static and publicly readable without accounts, API keys, a backend, or required remote assets. Preserve stable topic IDs, approved brand assets, and the distinction between published examples and planned lessons. Use non-browser validation for current work. The repository owner performs manual browser checks. Keep curriculum, experiment, and deployment changes within the authorized task scope. Deployment and Git staging, commits, or pushes require owner authorization.

## Required documentation maintenance

- Read this file and [PROGRESS.md](PROGRESS.md) before starting development.
- Update [PROGRESS.md](PROGRESS.md) after every meaningful milestone. Distinguish implementation, automated tests, manual verification, and pending work.
- Update this file whenever architecture, requirements, or major decisions change.
- Update [BUG_TRACKER.md](BUG_TRACKER.md) whenever an issue is discovered, fixed, or reopened.
- Keep the documentation aligned with the implementation. Preserve the decision history and document the reason when a decision is superseded.
