# LLM Evaluation — Learning Repository

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
- **Not a replacement for frameworks** — Phase 4 onward introduces RAGAS, DeepEval, and LangSmith. This repository teaches you the concepts first so those frameworks make sense when you reach them.

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

## What This Repository Is

This is not a framework. It is a **learning-by-doing repository** where every concept is taught through a real exercise. You build something, run it, observe the output, and understand why it behaves the way it does.

The goal is to develop practical skills in evaluating LLM-based systems — the kind of skills needed to work as a GenAI Evaluation Engineer or AI Quality Specialist in industry.

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
| Phase 0 | Pre-requisites — Python, LLM concepts, Ollama setup | 1–2 days |
| Phase 1 | First Experiments — calling models, comparing outputs | 2–3 days |
| Phase 2 | Evaluation Techniques — metrics, deterministic eval, behavioural testing, LLM-as-a-Judge, semantic similarity | 4–6 days |
| Phase 3 | What You Are Evaluating — RAG, agents, tokenisation | 3–4 days |
| Phase 4 | Frameworks & Tools — RAGAS, DeepEval, LangSmith, Promptfoo | 3–5 days |
| Phase 5 | Production Eval — regression, A/B, red teaming, CI/CD, Langfuse, agent evaluation, multi-turn, structured output | 6–8 days |
| Phase 6 | Specialisation — RAG eval full pipeline, safety and red teaming, bias and fairness, multi-modal, model drift | 5–7 days |

> **Current status:** Phase 5 Tests 12 and 13 complete. Test 10 RAGAS pending OpenAI credits.

**Total: approximately 4–6 weeks** depending on your pace.

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
├── docs/                        ← all documentation (serve with python3 -m http.server 8000)
│   ├── index.html               ← OPEN THIS — navigation hub
│   ├── home.html                ← phase overview and status
│   ├── test1.html – test13.html ← one file per test: results, learnings, findings
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
    └── trajectory-evaluation/   ← Test 13 — Trajectory judge scoring (mistral, 4 dimensions)
        └── results/             ← sample_trajectory_evaluation_report.html + sample JSON
```

> Each phase folder contains a `results/` directory with a sample HTML report so you can see what output looks like before running anything.

---

## Where to Start

1. Complete setup above
2. Open the documentation hub:
   ```bash
   cd docs && python3 -m http.server 8000
   ```
   Open **http://localhost:8000** — read each test page in order as you go.
3. Open `docs/genai_eval_learning_plan.xlsx` — track your progress
4. Run experiments in order — Phase 0 → Phase 1 → Phase 2 → …

---

## What You Will Learn

By completing Phases 0–4 you will understand:

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

---

## Evaluation Methods Covered

| Test | Method | What It Measures |
|------|--------|-----------------|
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

- **Take your time.** This is not a small topic. Each phase is designed to be absorbed, not completed. If something feels unclear, slow down — do not push forward hoping it will make sense later.
- **Do not try to match results.** LLMs are non-deterministic. Your outputs will differ from the documented ones even on identical prompts. That is expected. Focus on understanding the technique and what the results are telling you — not on reproducing specific numbers.
- **You are here to understand, not to execute.** When a test fails, ask why. When a score surprises you, read the actual response. Black-box testing instincts — "it passed, move on" — do not apply here. The failure is often the most valuable part.
- **Premium models will give different results.** If you use GPT-4o or Claude instead of a local Ollama model, you will see higher pass rates, better groundedness scores, and more consistent refusals. That is not a problem with the documented experiments — it is expected. Use whatever model you have and understand what it tells you about that model.
- **Excel is input only (from Test 6 onwards).** For semantic similarity and future tests, Excel stores test cases only. Results go to the HTML report. Earlier tests (Test 4, Test 5) do write results back to Excel — that is intentional for those exercises.
- **Read the HTML report, not the Excel.** After running any evaluator, open the generated HTML report in your browser. It shows Expected vs Bot Response side by side with colour-coded verdicts.
- **Fill your verdict before running the judge.** In `llm-as-a-judge`, always fill col H (Result) with your own Pass/Fail/Partial before running `llm_judge_evaluator.py`. The disagreements only have learning value if your verdict came first.
- **A score is not the final word.** In high-stakes domains like healthcare, always read the actual response for safety-critical cases — a lower score that provides a crisis helpline is better than a higher score that misses it.
- **You do not need to be a data scientist.** QA and testing instincts are the most valuable skill here. Threshold decisions, test case design, and reading results are all QA work.
- **Never commit `.env`.** It is in `.gitignore` by default. API keys in `.env` stay local. If you add a key directly to `config.yaml` instead, make sure `config.yaml` is also gitignored or the key field is left blank before committing.
