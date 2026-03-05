# LLM Evaluation — Learning Repository

A hands-on, structured learning journey for evaluating Large Language Models (LLMs) and GenAI systems.

Built for **QA Architects and Test Engineers** transitioning into GenAI evaluation — no data science background required.

---

## What This Repository Is

This is not a framework. It is a **learning-by-doing repository** where every concept is taught through a real exercise. You build something, run it, observe the output, and understand why it behaves the way it does.

The goal is to develop practical skills in evaluating LLM-based systems — the kind of skills needed to work as a GenAI Evaluation Engineer or AI Quality Specialist in industry.

---

## Do You Need Paid APIs?

**No.** Everything in this repository runs locally using [Ollama](https://ollama.ai).

Models used:
- `llama3.1:8b`
- `mistral`
- `deepseek-r1:7b`
- `gemma2:9b`

All are free, open-source, and run on your own machine. No OpenAI, no Anthropic, no cloud costs.

---

## Prerequisites

Before starting, make sure you have:

| Requirement | Why | How to Get It |
|-------------|-----|---------------|
| Python 3.10+ | All scripts are Python | python.org |
| Ollama | Runs LLMs locally | ollama.ai |
| At least one Ollama model | `ollama pull llama3.1:8b` | Run in terminal |
| Basic Python knowledge | Read/write loops, functions, files | automatetheboringstuff.com (free) |
| Git | To clone and track this repo | git-scm.com |

---

## Setup — First Time Only

**1. Clone the repository**
```bash
git clone <repo-url>
cd llm-evaluation
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
```

**3. Activate it**
```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**4. Install all dependencies**
```bash
pip install -r requirements.txt
```

You only need to do this once. After that, just activate the venv each time you start a new terminal session (`source venv/bin/activate`).

---

## Configuration

All shared settings live in `config.yml` at the project root. You should not need to change anything here unless you want to swap models or point to a different Excel file.

```yaml
shared:
  OLLAMA_URL: "http://localhost:11434/api/generate"

phase2:
  BOT_MODEL: "llama3.1:8b"
  EXCEL_FILE: "banking_test_cases.xlsx"
  TEST_SHEET: "Banking Bot Tests"

phase2_llm_as_a_judge:
  JUDGE_MODEL: "mistral"
  BOT_MODEL: "llama3.1:8b"
  RESULTS_SHEET: "JudgeResults"
  EXCEL_FILE: "banking_bot_test_results.xlsx"
  TEST_SHEET: "Banking Bot Tests"
```

Each script loads only its own section. `shared` acts as defaults — section values override shared where they overlap.

---

## How Long Will This Take?

This is a **self-paced plan across 7 phases**. Estimated effort per phase:

| Phase | Topic | Effort |
|-------|-------|--------|
| Phase 0 | Pre-requisites — Python, LLM concepts, Ollama setup | 1–2 days |
| Phase 1 | First Experiments — calling models, comparing outputs | 2–3 days |
| Phase 2 | Evaluation Techniques — metrics, deterministic eval, behavioural testing, LLM-as-a-Judge | 3–5 days |
| Phase 3 | What You Are Evaluating — RAG, agents, tokenisation | 3–4 days |
| Phase 4 | Frameworks & Tools — RAGAS, DeepEval, LangSmith | 3–5 days |
| Phase 5 | Production Eval — regression, A/B, red teaming, CI/CD | 4–6 days |
| Phase 6 | Specialisation — RAG eval, safety, red teaming | 5–7 days |

**Total: approximately 3–5 weeks** depending on your pace. Phases 0–2 are fully covered in this repo with working code and documentation.

---

## Repository Structure

```
llm-evaluation/
│
├── README.md                              ← You are here
├── requirements.txt                       ← Python dependencies (install with pip install -r requirements.txt)
├── config.yml                             ← Shared config for all scripts — models, file names, sheet names
├── print_folders_struct.py                ← Run this to print the project structure in terminal
│
├── docs/                                  ← All documentation and reference material
│   ├── index.html                         ← OPEN THIS in browser — main navigation hub
│   ├── home.html                          ← Landing page with phase overview
│   ├── test1.html                         ← Test 1 results and learnings
│   ├── test2.html                         ← Test 2 results and learnings
│   ├── test3.html                         ← Test 3 results and learnings
│   ├── test4.html                         ← Test 4 results and learnings
│   ├── test5.html                         ← Test 5 results and learnings
│   ├── concepts.html                      ← Key GenAI evaluation concepts with examples
│   ├── evaluation_docs.html               ← Original single-file reference (kept, do not delete)
│   └── genai_eval_learning_plan.xlsx      ← Your personal learning roadmap (track progress here)
│
├── phase-0-foundations/                   ← Pre-requisites and setup reference
│   ├── phase_eval.py                      ← Basic Ollama connection test
│   └── read_squad.py                      ← Dataset reading reference
│
├── phase-1-first-experiments/             ← Phase 1: First hands-on experiments
│   ├── test1_basic_test.py                ← Single prompt across 4 models — compare output and speed
│   ├── test2_full_evaluations.py          ← 3 use cases x 4 models x 3 runs, collect results
│   ├── test2_score_evaluations.py         ← Manual scoring of outputs (coherence, accuracy etc.)
│   └── results/                           ← Generated output files
│       ├── evaluation_results.json
│       ├── full_results.html
│       └── scores.json
│
└── phase-2-evaluation-techniques/         ← Phase 2: Systematic evaluation methods
    ├── test3_bleu_score_evaluation.py     ← BLEU and ROUGE automated metrics
    ├── banking-bots/                      ← Domain-restricted chatbot + behavioural eval suite
    │   ├── bot.py                         ← Banking chatbot (system prompt, single + multi-turn)
    │   ├── banking_evaluator.py           ← Evaluation runner (modes: auto, multi-turn, interactive)
    │   └── banking_test_cases.xlsx        ← 49 behavioural test cases across 5 categories
    └── llm-as-a-judge/                    ← LLM-as-a-Judge evaluator (Phase 2 extension)
        ├── llm_judge_evaluator.py         ← Runs bot → judge → compares to your verdict
        ├── banking_bot_test_results.xlsx  ← Test results with your verdict column (fill col H first)
        └── results/                       ← Generated JudgeResults saved here after each run
```

---

## Where to Start

1. Complete setup above (venv + pip install)
2. Open `docs/index.html` in your browser — it is your guided walkthrough with full navigation.
   - Tip: serve locally for best results: `cd docs && python3 -m http.server 8000` then open `http://localhost:8000`
3. Open `docs/genai_eval_learning_plan.xlsx` — track your progress as you go.
4. Run experiments in order — Phase 0 → Phase 1 → Phase 2.

---

## What You Will Learn

By the time you complete Phases 0–2 in this repo, you will understand:

- Why LLMs need structured evaluation — they are non-deterministic, unlike traditional software
- How to design test cases for a chatbot (functional, hallucination, refusal, context retention, prompt injection)
- The difference between deterministic eval (keyword matching) and semantic eval (meaning-based scoring)
- What hallucination types exist — confabulation, false grounding, context fabrication, financial confabulation
- Why prompt injection is a model-level weakness, not a prompt problem
- How LLM-as-a-Judge works — and why your human verdict must come before the judge's
- How to interpret disagreements between your judgement and the judge's

---

## Key Concepts

See `docs/concepts.html` for definitions of all key terms used across this repository.

---

## Learning Plan

The full 7-phase learning roadmap is in `docs/genai_eval_learning_plan.xlsx`.
Open it, update the Status column as you progress, and use it to track what to study next.

---

## Models Tested

| Model | Size | Notes |
|-------|------|-------|
| llama3.1:8b | 8B params | Primary banking bot — evaluated across all phases |
| mistral | 7B params | Used as LLM judge in Phase 2 LLM-as-a-Judge |
| deepseek-r1:7b | 7B params | Reasoning-focused, slowest but most detailed |
| gemma2:9b | 9B params | Google model, mid-range speed and quality |

---

## Notes for Learners

- **Fill in your verdict before running the judge.** In `llm-as-a-judge`, always fill col H (Result) with your own Pass/Fail/Partial before running `llm_judge_evaluator.py`. The disagreements only have learning value if your verdict came first.
- **Do not focus on which run mode is used** (`a`, `m`, `i` in the evaluator). Focus on the test categories and what they reveal about model behaviour.
- **Responses vary model to model** — the outputs in `evaluation_docs.html` are specific to `llama3.1:8b`. Your results will differ. That is expected and part of the learning.
- **You do not need to be a data scientist or AI engineer** to follow this. QA and testing instincts are the most valuable skill here.
