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

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## How Long Will This Take?

This is a **self-paced plan across 7 phases**. Estimated effort per phase:

| Phase | Topic | Effort |
|-------|-------|--------|
| Phase 0 | Pre-requisites — Python, LLM concepts, Ollama setup | 1–2 days |
| Phase 1 | First Experiments — calling models, comparing outputs | 2–3 days |
| Phase 2 | Evaluation Techniques — metrics, deterministic eval, behavioural testing | 3–5 days |
| Phase 3 | What You Are Evaluating — RAG, agents, tokenisation | 3–4 days (mix of reading + hands-on) |
| Phase 4 | Frameworks & Tools — RAGAS, DeepEval, LangSmith | 3–5 days |
| Phase 5 | Production Eval — regression, A/B, red teaming, CI/CD | 4–6 days |
| Phase 6 | Specialisation — RAG eval, safety, red teaming | 5–7 days |

**Total: approximately 3–5 weeks** depending on your pace. Phases 0–2 are fully covered in this repo with working code and documentation.

---

## Repository Structure

```
llm-evaluation/
│
├── README.md                          ← You are here
├── requirements.txt                   ← Python dependencies
├── .gitignore
│
├── docs/                              ← All documentation and reference material
│   ├── evaluation_docs.html           ← Full learning guide with results and insights
│   ├── genai_eval_learning_plan.xlsx  ← Your personal learning roadmap (track progress here)
│   └── concepts.html                  ← Key GenAI evaluation concepts (with examples from our tests)
│
├── phase-0-foundations/               ← Pre-requisites and setup reference
│   ├── phase_eval.py                  ← Basic Ollama connection test
│   └── read_squad.py                  ← Dataset reading reference
│
├── phase-1-first-experiments/         ← Phase 1: First hands-on experiments
│   ├── test1_basic_test.py            ← Single prompt across 4 models, compare output and speed
│   ├── test2_full_evaluations.py      ← 3 use cases x 4 models x 3 runs, collect results
│   ├── test2_score_evaluations.py     ← Manual scoring of outputs (coherence, accuracy etc.)
│   └── results/                       ← Generated output files from Test 2
│       ├── evaluation_results.json
│       ├── full_results.html
│       └── scores.json
│
└── phase-2-evaluation-techniques/     ← Phase 2: Systematic evaluation methods
    ├── test3_bleu_score_evaluation.py ← BLEU and ROUGE automated metrics
    └── banking-bots/                  ← Domain-restricted chatbot + full eval suite
        ├── bot.py                     ← Banking chatbot (system prompt, single + multi-turn)
        ├── banking_evaluator.py       ← Evaluation runner (modes: auto, multi-turn, interactive)
        └── banking_test_cases.xlsx    ← Test cases: functional tests + 49 behavioural tests
```

---

## Where to Start

1. Read `docs/evaluation_docs.html` — open in any browser. It is your guided walkthrough.
2. Open `docs/genai_eval_learning_plan.xlsx` — track your progress as you go.
3. Run experiments in order — Phase 0 → Phase 1 → Phase 2.

---

## What You Will Learn

By the time you complete Phases 0–2 in this repo, you will understand:

- Why LLMs need structured evaluation — they are non-deterministic, unlike traditional software
- How to design test cases for a chatbot (functional, hallucination, refusal, context retention, prompt injection)
- The difference between deterministic eval (keyword matching) and semantic eval (meaning-based scoring)
- What hallucination types exist — confabulation, false grounding, context fabrication, financial confabulation
- Why prompt injection is a model-level weakness, not a prompt problem
- How to measure latency, pass rate, and category-level performance

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
| llama3.1:8b | 8B params | Primary model for banking bot evaluation |
| mistral | 7B params | Fastest in our tests |
| deepseek-r1:7b | 7B params | Reasoning-focused, slowest but most detailed |
| gemma2:9b | 9B params | Google model, mid-range speed and quality |

---

## Notes for Learners

- **Do not focus on which run mode is used** (`a`, `m`, `i` in the evaluator). Focus on the test categories and what they reveal about model behaviour.
- **Responses vary model to model** — the outputs in `evaluation_docs.html` are specific to `llama3.1:8b`. Your results will differ. That is expected and part of the learning.
- **You do not need to be a data scientist or AI engineer** to follow this. QA and testing instincts are the most valuable skill here.
