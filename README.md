# LLM Evaluation for Engineers — Hands-On, No Maths, No Fluff


## TestNeural LLM Academy

The [academy dashboard](docs/index.html) is the starting point for **LLM Evaluation Engineering**. **Quick Learning** gives each focused goal its required topics, hours, exercises and checkpoints. It also contains the Learning Paths comparison and preparation checklist. **Complete Course** follows the core sequence and lists optional preparation and electives separately. **Learning Roadmap** shows dependencies, supports pan and zoom, and offers SVG, PNG and standalone HTML downloads. **About the Course** shows the overview, hours and progress. **Resources** links to reference material and groups Existing Repository Coverage and the Teaching Plan under Instructor Resources. Published examples and planned teaching material are distinguished in the curriculum.

### Required project tracking

- Read [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) and [PROGRESS.md](PROGRESS.md) before starting development.
- Update [PROGRESS.md](PROGRESS.md) after every meaningful milestone. Record what was implemented, tested, manually verified, and what is still pending.
- Update [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) when architecture, requirements, or major decisions change. Preserve the decision history and explain why a decision was superseded.
- Update [BUG_TRACKER.md](BUG_TRACKER.md) when an issue is discovered, fixed, or reopened.
- Keep these documents aligned with the implementation and the checks actually performed.

### Design and local preview

- The approved V1 branding lives in [docs/assets/branding](docs/assets/branding/README.md). The dashboard uses the supplied banner. Navigation uses the compact mark, with a favicon and Apple touch icon. The generated curriculum embeds its branding and interface resources for offline sharing.
- The dashboard template lives in [docs/templates/academy-home.html](docs/templates/academy-home.html). Both the dashboard and standalone curriculum are generated from [MASTER_CURRICULUM.md](MASTER_CURRICULUM.md) by the same Python script. Light and dark theme selection is local to the browser, as is progress.
- Open `docs/index.html` directly with the companion files, or run `python3 -m http.server 8000 --bind 127.0.0.1` **from the repository root** and visit `http://127.0.0.1:8000/docs/`. This keeps sibling paths usable for the workbook and example report. Lessons load without a model or API key. Python exercises run separately in a local environment.
- A downloaded plan is self-contained for its topics, progress controls and roadmap. Links to separate examples require their companion files. Browser local storage and downloads can be restricted for file URLs.
- The desktop overview pairs reading with a smaller support column. On tablets and phones the columns stack. Wide tables scroll inside their own region. Durations are shown as hours and minutes. The source totals remain decimal hours.

### Saving and moving progress

**Continue Learning** opens the first unfinished required topic in order. About the Course uses the last selected path, or the beginner path by default. Opening a topic leaves its status unchanged. Both learning modes use the same progress.

Under **About the Course → Your learning progress → Manage progress**, export a JSON backup or choose one to import. A preview lists completed topics added or removed, in-progress marks cleared, and the resulting path. Merge keeps existing marks unless the backup marks the same topic complete. Replace keeps only completed topics listed in the backup. Apply the import after reviewing it, or cancel to keep current progress. Reset requires confirmation.

The version-1 JSON contains only a format identifier, version, completed topic IDs, optional selected path ID, and export timestamp. Invalid files and unknown topic IDs are rejected without changing progress. The browser stores progress locally and does not synchronize it across devices.

```json
{
  "format": "testneural-academy-progress",
  "version": 1,
  "completedTopicIds": ["M01-T01"],
  "selectedPath": "A",
  "exportedAt": "2026-01-01T00:00:00.000Z"
}
```

### Manual browser checklist

1. Open the local academy and check the five navigation items at 375, 768, 1366, 1440 and 1920 pixels. Try both themes. Check that the About overview stacks on narrower screens and that the wide hours table scrolls independently.
2. Open a Quick Learning path, mark a topic complete and check that Continue Learning advances in order. Reload and check the same topic in Complete Course.
3. Export a backup and import it in another browser profile. Preview and cancel first, then try merge and replace. Try an invalid topic ID and check that current progress remains intact.
4. Open Learning Paths from Quick Learning and check all seven paths. In Resources, open Existing Repository Coverage and Teaching Plan under Instructor Resources. Pan and zoom the roadmap, download a plan, and open its HTML offline.

### Required HTML synchronization

After any curriculum, generator, template, or embedded interface change, regenerate and check both generated pages before reviewing or committing them. Then validate the public release file set.

```bash
python3 docs/generate_master_curriculum.py
python3 docs/generate_master_curriculum.py --check
python3 scripts/validate_static_site.py
```

See the [static hosting notes](docs/DEPLOYMENT.md) for the public file boundary and release checks. The production runbook and service files are maintained outside this repository.


A hands-on, structured learning journey for evaluating Large Language Models (LLMs) and GenAI systems.

Built for **anyone who needs to test and evaluate LLM-based systems** — QA Engineers, Test Engineers, developers, or anyone at any stage of building or validating a GenAI product. No data science background required.

---

## Who This Is For

This repository is especially useful for QA and test professionals, but relevant to anyone involved in evaluating LLM systems.

You do not need a data science background. You do not need to understand the mathematics behind neural networks. What you need — and almost certainly already have — is the instinct to find failure modes, design test cases, question results, and think in coverage. That is the most valuable skill in GenAI evaluation, and it is not taught in any AI course.

**This is for:** QA professionals who have been told their team is moving to GenAI and want to understand what evaluation actually means in practice — built, run, and understood, not just read about.

**This is not for:** Data scientists looking for ML tooling. Developers building LLM products. Researchers benchmarking models at scale.

---

## What This Repository Is Not

- **Not a framework** — you are not installing a tool and calling its API. You build the evaluation logic yourself so you understand what frameworks do under the hood.
- **Not an academic course** — no mathematics, no statistics theory, no research papers required before you start.
- **Not a tutorial series** — no presenter walking through pre-filled notebook outputs. You run real scripts against real models and read real results.
- **Not model-specific** — nothing here is tied to a single provider. The same techniques apply whether you use Ollama, GPT-4o, Claude, or Gemini.
- **Not a replacement for frameworks** — Phase 4 onward introduces RAGAS and DeepEval, with more frameworks coming. This repository teaches you the concepts first so those frameworks make sense when you reach them.

---

## The Gap This Fills

Search for LLM evaluation resources and you will find academic papers full of mathematics, framework documentation that assumes prior knowledge, YouTube tutorials that call an API and declare success, and AI courses designed for data scientists.

None of them are built for QA engineers. None of them say: your testing instincts are the asset — here is how to apply them to a non-deterministic system.

This repository fills that gap. It covers the same evaluation techniques used by teams at AI companies — deterministic eval, LLM-as-a-Judge, semantic similarity, groundedness scoring, temperature sensitivity, RAG evaluation — taught through the lens of test design, coverage thinking, and failure analysis. The language is QA language. The framing is QA framing.

**What makes this different from everything else out there:**
- **Single place** — foundations through production eval in one structured journey, in order, with progression
- **QA framing throughout** — test cases, pass/fail rules, categories, coverage, evidence. Language you already speak.
- **Hands-on with real results** — scripts you run yourself, not pre-filled notebook outputs
- **Results documented with learning** — not just the score, but what it means and why it matters in production
- **No maths barrier** — every concept explained through examples, not equations
- **Honest about non-determinism** — tells you not to match numbers, focus on understanding what your results mean
- **Progression** — each test builds on the one before, concepts introduced when needed not dumped upfront
- **Free to start** — zero cost using local Ollama models, scalable to paid providers when ready

---

## Before You Start — Read This

This is a big topic. Take your time with it.

There is no shortcut through LLM evaluation. Each phase builds on the one before. If you rush, the later exercises will feel confusing — not because they are hard, but because the foundations were skipped. The learners who get the most from this repository are the ones who slow down, run every exercise themselves, and read the results before moving on.

**Do not try to match numbers.** You will run these experiments and get different outputs than the ones documented here. That is expected and intentional — LLMs are non-deterministic. Your 4% interest rate answer might be phrased differently from the example. Your pass rate at temperature 1.0 might be 12/15 instead of 13/15. This is not a bug. It is the subject matter. The goal is to understand *why* outputs vary and *how* to evaluate them — not to reproduce identical results.

**You are expected to think, not follow.** This repository is designed to make you an educated evaluator, not a pipeline operator. When a test fails, ask why. When results are surprising, investigate. When a concept is unclear, check the Concepts Reference before moving on. Black-box testing instincts — "it passed, move on" — do not transfer to GenAI evaluation. Understanding the failure is the work.

---

## Do You Need Paid APIs?

**No — but you can use them if you want.**

By default everything runs locally using [Ollama](https://ollama.ai) — free, no account needed.

If you want stronger models as a bot or judge (GPT-4o, Claude, Gemini), the repository supports paid providers out of the box. You switch provider with one line in `config.yaml`. See the **Configuration** section below.

**Why this repository uses Ollama by default:** The experiments documented here were run on local Ollama models to keep costs at zero across hundreds of iterations during development. You are free — and encouraged — to use paid APIs. A premium model like GPT-4o or Claude will produce noticeably better results in exercises like LLM-as-a-Judge and Groundedness Scoring. The tradeoffs are cost vs quality, and you decide per script.

**Your results will differ from the documented ones — and that is fine.** A premium model may pass more tests, produce higher scores, or refuse more robustly than a local 8B model. This is not a discrepancy — it is the point. The goal is to understand the evaluation technique, not to reproduce a specific number. Use whatever model you have access to, run the exercise, and focus on what the output is telling you.

**Models used in this repository's experiments (Ollama):**
- `llama3.1:8b`
- `mistral`
- `deepseek-r1:7b`
- `gemma2:9b`

These are the models used in this repository. You can use any model available in Ollama — run `ollama list` to see what you have, or `ollama pull <model>` to download a new one.

**Supported paid providers (optional):**
- OpenAI — e.g. `gpt-4o`, `gpt-4o-mini`
- Anthropic — e.g. `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- Google Gemini — e.g. `gemini-1.5-pro`, `gemini-1.5-flash`

---

## Prerequisites

| Requirement | Why | How to Get It |
|-------------|-----|---------------|
| Python 3.10+ | All scripts are Python | python.org |
| Ollama | Runs LLMs locally | ollama.ai |
| At least one Ollama model | `ollama pull llama3.1:8b` | Run in terminal |
| Basic Python knowledge | Read/write loops, functions, files | automatetheboringstuff.com (free) |
| Git | To clone and track this repo | git-scm.com |

---

## Setup — First Time Only

```bash
# 1. Clone the repository
git clone git@github.com:amitbad/llm-evaluation.git
cd llm-evaluation

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set up API keys for paid providers
cp .env.example .env            # copy sample file
# edit .env and fill in your keys, then:
source .env                     # Mac / Linux
```

After the first setup, just activate the venv at the start of each session: `source venv/bin/activate`

---

## Configuration

All settings live in **`config.yaml`** at the project root — models, providers, file names, and sheet names for every script. Open it and read it; it is well-commented.

Key things to know:
- Each script section has its own `BOT_MODEL`, `BOT_PROVIDER`, `JUDGE_MODEL`, `JUDGE_PROVIDER` — bot and judge can use different providers independently.
- To switch to a paid provider: change two lines (`JUDGE_MODEL` and `JUDGE_PROVIDER`). Nothing else.
- API keys go in `.env` (copy `.env.example`, fill in, run `source .env`). Keys are never hardcoded. `.env` is gitignored.

> See `config.yaml` for the full configuration reference with all sections and defaults.

---

## How Long Will This Take?

| Phase | Topic | Effort |
|-------|-------|--------|
| Phase 0 | Foundations — basic eval thinking, keyword checks, benchmark data | 1 day |
| Phase 1 | First Experiments — calling models, comparing outputs, manual scoring | 2–3 days |
| Phase 2 | Evaluation Techniques — BLEU/ROUGE, deterministic eval, LLM-as-a-Judge, semantic similarity, groundedness | 4–6 days |
| Phase 3 | What You Are Evaluating — temperature sensitivity, RAG evaluation | 3–4 days |
| Phase 4 | Frameworks & Tools — RAGAS, DeepEval | 2–4 days |
| Phase 5 | Production Eval — agent evaluation, trajectory evaluation | 3–5 days |

> **Current status:** Phases 0–5 are present in the repository today, and more topics may be added over time. Test 10 RAGAS requires OpenAI credits. Test 14 Langfuse requires Docker (see `docs/test14.html` for full setup instructions).

**Total: approximately 3–5 weeks** depending on your pace.

---

## Repository Structure

```
llm-evaluation/
├── README.md
├── requirements.txt
├── config.yaml                  ← all models, providers, paths — one file for everything
├── model_client.py              ← universal caller: ollama / openai / anthropic / gemini
├── .env.example                 ← copy to .env, fill in API keys
│
├── docs/                        ← website and lesson documentation
│   ├── index.html               ← OPEN THIS — navigation hub
│   ├── home.html                ← phase overview and status
│   ├── test1.html – test14.html ← one file per test: results, learnings, findings
│   └── concepts.html            ← GenAI eval concepts reference
│
├── phase-0-foundations/
├── phase-1-first-experiments/
├── phase-2-evaluation-techniques/
│   ├── banking-bots/            ← Test 4 — behavioural eval, 49 test cases
│   ├── llm-as-a-judge/          ← Test 5 — LLM judge pipeline
│   ├── semantic-similarity/     ← Test 6 — cosine similarity eval
│   └── groundedness/            ← Test 7 — groundedness scoring
│
├── phase-3-what-you-are-evaluating/
│   ├── temperature-sensitivity/ ← Test 8 — 4 temperatures × 15 cases
│   └── rag-evaluation/          ← Test 9 — hand-rolled RAG eval (25 cases)
│       ├── documents/           ← 3 source documents
│       └── results/             ← sample_rag_evaluation_report.html for reference
│
├── phase-4-frameworks-and-tools/
│   ├── ragas-evaluation/        ← Test 10 — RAGAS framework (requires OpenAI judge)
│   └── deepeval-evaluation/     ← Test 11 — DeepEval framework (fully local via Ollama)
│       ├── documents/
│       └── results/             ← sample_deepeval_report.html for reference
│
└── phase-5-production-eval/
    ├── agent-evaluation/        ← Test 12 — Tool-calling agent eval (15 cases, qwen3.5:9b)
    │   ├── agent_test_cases.xlsx
    │   └── results/             ← sample_agent_evaluation_report.html + sample JSON
    ├── trajectory-evaluation/   ← Test 13 — Trajectory judge scoring (mistral, 4 dimensions)
    │   └── results/             ← sample_trajectory_evaluation_report.html + sample JSON
    └── langfuse-observability/  ← Test 14 — Langfuse self-hosted observability (Docker)
        ├── docker-compose.yml   ← starts Langfuse + PostgreSQL locally
        └── results/             ← langfuse_results_*.json (live run artifacts)
```

> Each phase folder contains a `results/` directory with a sample HTML report so you can see what output looks like before running anything.

---

## Where to Start

If you are new to GenAI evaluation, do not start by reading code files randomly. Start in this order:

1. Complete setup above

2. Open the documentation hub:
   ```bash
   python3 -m http.server 8000 --bind 127.0.0.1
   ```
   Open **http://127.0.0.1:8000/docs/** from a server started at the repository root.

3. Read in this order:
   - `docs/home.html` — overview of all phases
   - `docs/concepts.html` — definitions of the terms used throughout the repo
   - `docs/test0.html` — first foundations exercise
   - `docs/test1.html` — first real model comparison

4. Run the scripts in order. Do not skip ahead.
   - **Phase 0**
     - `phase-0-foundations/explore_squad.py`
     - `phase-0-foundations/phase_eval.py`
   - **Phase 1**
     - `phase-1-first-experiments/test1_basic_test.py`
     - `phase-1-first-experiments/test2_full_evaluations.py`
     - `phase-1-first-experiments/test2_score_evaluations.py`

5. Only move to the next phase when the current one makes sense.

### Recommended learning path for a first-time learner

- **Start with Phase 0** if you want to understand what an evaluation is before comparing models.
- **Start with Test 1** if you want immediate hands-on results from real models.
- **Do Test 2 right after Test 1** because it turns “one prompt, one response” into a real evaluation workflow: collect outputs first, then score them.
- **Read the matching HTML page after every script**. The script shows what happened. The HTML explains why it matters.

### Important dependency notes

- `test1_basic_test.py` has **no prior dependency**. It is the first Phase 1 script to run.
- `test2_full_evaluations.py` should be run **after Test 1**, so you know your models are working before starting a long run.
- `test2_score_evaluations.py` depends on `evaluation_results.json`, which is generated by `test2_full_evaluations.py`.
- Later phases become easier only if you have understood the earlier ones. This repository is meant to be learned in sequence.

---

## What You Will Learn

By completing Phases 0–5 you will understand:

- Why LLMs need structured evaluation — they are non-deterministic, unlike traditional software
- How to design test cases for a chatbot in QA format — functional, behavioural, safety categories
- The difference between keyword matching, BLEU/ROUGE, LLM-as-a-Judge, and semantic similarity
- What hallucination types exist — confabulation, false grounding, context fabrication
- Why prompt injection is a model-level weakness, not a prompt problem
- How to use sentence embeddings and cosine similarity to evaluate meaning — not just words
- How LLM-as-a-Judge works — and why your human verdict must come before the judge's
- When a score alone is not enough — high-stakes cases require reading the actual response
- How to evaluate whether a bot response is grounded in its source material — or invented
- How to switch between local and paid model providers with a one-line config change
- How evaluation frameworks like RAGAS and DeepEval work — and how their metric definitions differ from hand-rolled scorers using the same judge
- Why context relevance scores can differ dramatically between frameworks even with the same judge model — and what that tells you about metric calibration
- How to handle refusal cases correctly in automated evaluation — they are correct bot behaviour, not failures
- How to build a tool-calling agent with observable trajectories and evaluate tool path, argument correctness, and stop behavior deterministically
- Why binary path-matching and judge scoring answer different questions about the same trajectory — and why you need both
- What trajectory groundedness means: an agent can call the right tool and still ignore the result and answer from model memory
- How a two-layer evaluation pipeline works: deterministic checks as a fast gate, judge scoring for quality depth

This repository does **not** currently teach every GenAI evaluation topic. For example, it does not yet contain dedicated hands-on phases for Langfuse observability workflows, A/B experimentation pipelines, or red teaming programs. The focus here is: build evaluation fundamentals first, then production-style evaluation patterns you can understand end-to-end.

---

## Evaluation Methods Covered

| Test | Method | What It Measures |
|------|--------|-----------------|
| Test 0 | Foundations / Simple Checks | Basic evaluation thinking — keyword checks, topic drift, quality failure, and benchmark dataset awareness through small local examples. |
| Test 1 | Basic Model Comparison | First direct comparison across models — does each model respond, how fast is it, and how does response style differ on the same prompt? |
| Test 2 | Manual Scoring | Human judgement — coherence, accuracy, consistency |
| Test 3 | BLEU / ROUGE | Word overlap with a reference answer |
| Test 4 | Keyword Matching | Deterministic pass/fail on must-contain / must-not-contain rules |
| Test 5 | LLM-as-a-Judge | Meaning, intent, nuance — judge challenges your verdict |
| Test 6 | Semantic Similarity | Cosine similarity of sentence embeddings — meaning, not words |
| Test 7 | Groundedness Scoring | Source traceability — did the bot say this from source, or invent it? |
| Test 8 | Temperature Sensitivity | Does temperature affect pass rates? Same suite at T=0.0/0.5/1.0/1.5 across two models. |
| Test 9 | RAG Evaluation | Context Relevance, Answer Faithfulness, Answer Relevance — 21 cases across 6 categories. |
| Test 10 | RAGAS Framework | Framework-based RAG evaluation — requires OpenAI judge. Direct comparison against hand-rolled Test 9. |
| Test 11 | DeepEval Framework | Pytest-style LLM evaluation fully local via Ollama. 25 cases, 1 refusal (TC19). Overall 62%, CTX 24%, Faithfulness 82%, Answer Rel. 81%. 1/25 full PASS (TC15). Calibration analysis vs Test 9. |
| Test 12 | Agent Trajectory Eval (Deterministic) | Tool-calling agent with observable trajectories. 15 test cases. Checks tool-path match, argument correctness, stop behavior. 14/15 PASS (TC10 behaviour gap). |
| Test 13 | Agent Trajectory Eval (Judge-Scored) | Reads Test 12 JSON traces. Judge scores 4 dimensions per trajectory: tool selection, argument quality, answer groundedness, stop appropriateness. 15/15 PASS with mistral. |
| Test 14 | Langfuse Observability | Self-hosted LLM observability via Docker. Banking chatbot traces (20 cases, 6 categories) sent to Langfuse with keyword_pass scores, latency, and tags. Explore traces, spans, and score filtering in the dashboard. |

---

## Models Used

**Default (local, free via Ollama):**

| Model | Size |
|-------|------|
| llama3.1:8b | 8B |
| mistral | 7B |
| deepseek-r1:7b | 7B |
| gemma2:9b | 9B |
| qwen3.5:9b | 9B |

These are the models used in this repository. You are not limited to these — any model available in Ollama works. Change `BOT_MODEL` or `JUDGE_MODEL` in `config.yaml` to use a different one.

**Supported paid providers (optional):**

| Provider | Example Models | Key Config |
|----------|---------------|------------|
| OpenAI | e.g. gpt-4o, gpt-4o-mini | `BOT_PROVIDER: "openai"` |
| Anthropic | e.g. claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022 | `BOT_PROVIDER: "anthropic"` |
| Google Gemini | e.g. gemini-1.5-pro, gemini-1.5-flash | `BOT_PROVIDER: "gemini"` |

Bot and judge can use different providers — any combination works.

---

## Notes for Learners

- **Move in order.** The repository is designed as a sequence. Earlier tests make later ones easier to understand.
- **Do not try to match exact outputs.** LLMs are non-deterministic. Focus on understanding the evaluation method, not reproducing the same wording or score.
- **Read the HTML page after running a script.** The script shows what happened. The HTML page explains what it means.
- **Always read surprising results.** A score or pass/fail label is a signal, not the whole answer.
- **Use premium models only if you want to.** Ollama is enough to learn the techniques. Paid providers are optional.
- **Never commit `.env`.** Keep API keys local only.
