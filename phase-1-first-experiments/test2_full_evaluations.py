import json
import os
import sys
import time

import ollama
import yaml

# ── ANSI colour helpers ──────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
PURPLE = "\033[35m"
WHITE  = "\033[97m"

def c(color, text):
    return f"{color}{text}{RESET}"

def header(text):
    print(c(CYAN, "=" * 64))
    print(c(BOLD + WHITE, f"  {text}"))
    print(c(CYAN, "=" * 64))

def subheader(text):
    print()
    print(c(YELLOW, "-" * 64))
    print(c(BOLD + YELLOW, f"  {text}"))
    print(c(YELLOW, "-" * 64))

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml")
with open(_CONFIG_FILE, "r", encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

models = _cfg.get("phase1", {}).get("MODELS", ["llama3.1:8b"])

def query_model(model, prompt):
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    end_time = time.time()
    return response['message']['content'], end_time - start_time

# We define 3 use cases: text generation, question answering, and summarization
use_cases = {
    'text_generation': {
        'prompt': "Write a short story about a robot who discovers a hidden garden on Earth."
    },
    'question_answering': {
        'prompt': "Explain why renewable energy is important for the environment."
    },
    'summarization': {
        'text': "Climate change is a long-term change in temperature and typical weather patterns in a place. It is caused by human activities like burning fossil fuels, which release greenhouse gases into the atmosphere. These gases trap heat, leading to global warming. Effects include rising sea levels, extreme weather, and threats to wildlife. To combat it, we need to reduce emissions, use renewable energy, and protect forests.",
        'prompt': "Summarize the following text in 50 words or less: " + "Climate change is a long-term change in temperature and typical weather patterns in a place. It is caused by human activities like burning fossil fuels, which release greenhouse gases into the atmosphere. These gases trap heat, leading to global warming. Effects include rising sea levels, extreme weather, and threats to wildlife. To combat it, we need to reduce emissions, use renewable energy, and protect forests."
    }
}

total_calls = len(use_cases) * len(models) * 3
call_num = 0

print()
header("Phase 1 — Test 2 · Full Evaluations")
print(f"""
  {c(BOLD, 'What this script does:')}
  Runs {c(YELLOW, '3 use cases')} × {c(YELLOW, str(len(models)) + ' model(s)')} × {c(YELLOW, '3 runs')} = {c(BOLD, str(total_calls) + ' model calls total')}.
  Saves every output to {c(CYAN, 'evaluation_results.json')} for manual scoring.
  {c(DIM, 'No scoring here — that is done separately in test2_score_evaluations.py.')}

  {c(BOLD, 'Dependency on Test 1:')}
  {c(GREEN, '✔')} {c(DIM, 'Run test1_basic_test.py first to confirm all models respond.')}
  {c(GREEN, '✔')} Ollama must be running  {c(DIM, '(ollama serve)')}

  {c(BOLD, 'Use cases :')} text_generation · question_answering · summarization
  {c(BOLD, 'Models    :')} {c(YELLOW, str(models))}
  {c(BOLD, 'Runs each :')} 3  {c(DIM, '(to check consistency across identical prompts)')}

  {c(DIM, 'This may take several minutes. Each line below = one completed call.')}
""")
sys.stdout.flush()

results = {}

for use_case, data in use_cases.items():
    results[use_case] = {}
    prompt = data['prompt']
    subheader(f"Use case: {use_case.upper()}")
    print(f"  {c(DIM, 'Prompt: ')}{prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    for model in models:
        results[use_case][model] = []
        for run in range(1, 4):  # 3 runs for consistency
            call_num += 1
            progress = f"[{call_num}/{total_calls}]"
            print(f"  {c(DIM, progress)} {c(YELLOW, model)} run {run}/3 — {c(DIM, 'waiting...')}", end="", flush=True)
            try:
                output, duration = query_model(model, prompt)
                results[use_case][model].append({
                    'run': run,
                    'output': output,
                    'time': duration
                })
                print(f"\r  {c(DIM, progress)} {c(YELLOW, model)} run {run}/3 — {c(GREEN, f'done ({duration:.2f}s)')}          ")
            except Exception as e:
                results[use_case][model].append({
                    'run': run,
                    'output': f"Error: {e}",
                    'time': 0
                })
                print(f"\r  {c(DIM, progress)} {c(YELLOW, model)} run {run}/3 — {c(RED, f'error: {e}')}")

with open('evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=4)

print()
print(c(CYAN, "=" * 64))
print(c(BOLD + GREEN, "  ✔ All calls complete"))
print(c(CYAN, "=" * 64))
print(f"""
  {c(BOLD, 'Results saved to:')} {c(CYAN, 'evaluation_results.json')}
  {c(BOLD, 'Total calls    :')} {c(GREEN, str(total_calls))} ({len(use_cases)} use cases × {len(models)} model(s) × 3 runs)

  {c(BOLD, 'Next step:')}
  Run {c(CYAN, 'test2_score_evaluations.py')} to manually score each output (1–5)
  and save scores to {c(CYAN, 'scores.json')}.
""")
print(c(DIM, "  ─" * 32))
print(f"  {c(BOLD, '📖 Full analysis:')} {c(CYAN, 'docs/test2.html')}  (open docs/index.html)")
print()
