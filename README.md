# LLM Evaluation — Learning Repository

A hands-on, structured learning journey for evaluating Large Language Models (LLMs) and GenAI systems.

Built for **Test Engineers** transitioning into GenAI evaluation — no data science background required.

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
git clone <repo-url>
cd llm-evaluation

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

After the first setup, just activate the venv at the start of each session: `source venv/bin/activate`

---

## Configuration

All settings live in `config.yaml` at the project root.

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

phase2_semantic_similarity:
  BOT_MODEL: "llama3.1:8b"
  EXCEL_FILE: "healthcare_test_cases.xlsx"
  TEST_SHEET: "Test Cases"

phase2_groundedness:
  BOT_MODEL: "llama3.1:8b"
  JUDGE_MODEL: "gemma2:9b"
  EXCEL_FILE: "healthcare_test_cases.xlsx"
  TEST_SHEET: "Test Cases"
```

---

## How Long Will This Take?

| Phase | Topic | Effort |
|-------|-------|--------|
| Phase 0 | Pre-requisites — Python, LLM concepts, Ollama setup | 1–2 days |
| Phase 1 | First Experiments — calling models, comparing outputs | 2–3 days |
| Phase 2 | Evaluation Techniques — metrics, deterministic eval, behavioural testing, LLM-as-a-Judge, semantic similarity | 4–6 days |
| Phase 3 | What You Are Evaluating — RAG, agents, tokenisation | 3–4 days |
| Phase 4 | Frameworks & Tools — RAGAS, DeepEval, LangSmith | 3–5 days |
| Phase 5 | Production Eval — regression, A/B, red teaming, CI/CD | 4–6 days |
| Phase 6 | Specialisation — RAG eval, safety, red teaming | 5–7 days |

**Total: approximately 3–5 weeks** depending on your pace.

---

## Repository Structure

```
llm-evaluation/
│
├── README.md
├── requirements.txt                       ← pip install -r requirements.txt
├── config.yaml                            ← all models, file names, sheet names
│
├── docs/                                  ← all documentation
│   ├── index.html                         ← OPEN THIS — main navigation hub
│   ├── home.html                          ← phase overview and status
│   ├── test1.html – test6.html            ← one file per test, results and learnings
│   ├── concepts.html                      ← key GenAI eval concepts with examples
│   └── genai_eval_learning_plan.xlsx      ← 7-phase learning roadmap, track progress here
│
├── phase-0-foundations/
│   ├── phase_eval.py                      ← basic Ollama connection test
│   └── read_squad.py
│
├── phase-1-first-experiments/
│   ├── test1_basic_test.py                ← single prompt across 4 models
│   ├── test2_full_evaluations.py          ← 3 use cases x 4 models x 3 runs
│   ├── test2_score_evaluations.py         ← manual scoring of outputs
│   └── results/
│
└── phase-2-evaluation-techniques/
    ├── test3_bleu_score_evaluation.py     ← BLEU and ROUGE automated metrics
    ├── banking-bots/                      ← banking chatbot + behavioural eval
    │   ├── bot.py                         ← banking chatbot (llama3.1:8b)
    │   ├── banking_evaluator.py           ← evaluator (modes: auto, multi-turn, interactive)
    │   └── banking_test_cases.xlsx        ← 49 behavioural test cases
    ├── llm-as-a-judge/                    ← LLM-as-a-Judge pipeline
    │   ├── llm_judge_evaluator.py         ← bot → human verdict → judge → compare
    │   ├── banking_bot_test_results.xlsx  ← fill col H before running
    │   └── results/
    └── semantic-similarity/               ← semantic similarity evaluation
        ├── healthcare_bot.py              ← City General Hospital chatbot (llama3.1:8b)
        ├── healthcare_test_cases.xlsx     ← 22 QA-format test cases (input only)
        ├── test6_semantic_similarity.py   ← runs eval, scores with cosine similarity
        ├── report_generator.py            ← generates dark-theme HTML report
        └── results/                       ← HTML report saved here after each run
    └── groundedness/                      ← groundedness scoring evaluation
        ├── groundedness_evaluator.py      ← imports healthcare bot, runs judge scoring
        ├── report_generator.py            ← generates dark-theme HTML report
        └── results/                       ← HTML report saved here after each run (not committed)
```

---

## Where to Start

1. Complete setup above
2. Open `docs/index.html` via local server:
   ```bash
   cd docs && python3 -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser
3. Open `docs/genai_eval_learning_plan.xlsx` — track your progress as you go
4. Run experiments in order — Phase 0 → Phase 1 → Phase 2

---

## What You Will Learn

By completing Phases 0–2 you will understand:

- Why LLMs need structured evaluation — they are non-deterministic, unlike traditional software
- How to design test cases for a chatbot in QA format — functional, behavioural, safety categories
- The difference between keyword matching, BLEU/ROUGE, LLM-as-a-Judge, and semantic similarity
- What hallucination types exist — confabulation, false grounding, context fabrication
- Why prompt injection is a model-level weakness, not a prompt problem
- How to use sentence embeddings and cosine similarity to evaluate meaning — not just words
- How LLM-as-a-Judge works — and why your human verdict must come before the judge's
- When a score alone is not enough — high-stakes cases require reading the actual response

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

---

## Models Used

| Model | Size | Role |
|-------|------|------|
| llama3.1:8b | 8B | Primary bot — banking and healthcare chatbot |
| mistral | 7B | Judge model in LLM-as-a-Judge |
| deepseek-r1:7b | 7B | Reasoning-focused, comparison in Phase 1 |
| gemma2:9b | 9B | Google model, comparison in Phase 1 |

---

## Notes for Learners

- **Excel is input only (from Test 6 onwards).** For semantic similarity and future tests, Excel stores test cases only. Results go to the HTML report. Earlier tests (Test 4, Test 5) do write results back to Excel — that is intentional for those exercises.
- **Read the HTML report, not the Excel.** After running any evaluator, open the generated HTML report in your browser. It shows Expected vs Bot Response side by side with colour-coded verdicts.
- **Fill your verdict before running the judge.** In `llm-as-a-judge`, always fill col H (Result) with your own Pass/Fail/Partial before running `llm_judge_evaluator.py`. The disagreements only have learning value if your verdict came first.
- **A score is not the final word.** In high-stakes domains like healthcare, always read the actual response for safety-critical cases — a lower score that provides a crisis helpline is better than a higher score that misses it.
- **You do not need to be a data scientist.** QA and testing instincts are the most valuable skill here. Threshold decisions, test case design, and reading results are all QA work.
