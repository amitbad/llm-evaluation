import json
import sys

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
ORANGE = "\033[38;5;214m"

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

# Load the evaluation results
try:
    with open('evaluation_results.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print()
    print(c(RED, "  ✗ evaluation_results.json not found."))
    print(f"  {c(BOLD, 'Run test2_full_evaluations.py first')} to generate that file.")
    print()
    sys.exit(1)

# Define metrics per use case
metrics = {
    'text_generation': ['coherence', 'creativity', 'fluency'],
    'question_answering': ['accuracy', 'completeness', 'relevance'],
    'summarization': ['completeness', 'conciseness', 'accuracy']
}

# Count total ratings needed
total_use_cases = len(data)
total_models = len(next(iter(data.values())))
total_runs = 3
total_metrics_avg = sum(len(v) for v in metrics.values()) / len(metrics)
total_ratings = int(total_use_cases * total_models * total_runs * total_metrics_avg)

print()
header("Phase 1 — Test 2 · Manual Scoring")
print(f"""
  {c(BOLD + GREEN, '✔ NO MODEL IS CALLED. NO INTERNET NEEDED. OLLAMA DOES NOT NEED TO BE RUNNING.')}
  This script only reads the outputs that were already saved to {c(CYAN, 'evaluation_results.json')}
  by {c(CYAN, 'test2_full_evaluations.py')}. It then asks {c(BOLD, 'you')} to type a number 1–5
  for each output. That is the entire script.

  {c(BOLD, 'What this produces:')}
  Your scores are saved to {c(CYAN, 'scores.json')}. That file contains a number for every
  output across every model and use case. It is {c(BOLD, 'your personal evaluation record')} —
  a snapshot of how you judged each model on each task at this point in the course.
  You can open it any time to review your ratings.

  {c(BOLD, 'Dependency:')}
  {c(GREEN, '✔')} {c(DIM, 'evaluation_results.json found ✓ — you are ready to score')}

  {c(BOLD, 'Rating scale:')}  1 = poor  ·  2 = weak  ·  3 = ok  ·  4 = good  ·  5 = excellent
  {c(BOLD, 'Metrics by use case:')}
    text_generation    : {c(YELLOW, 'coherence · creativity · fluency')}
    question_answering : {c(YELLOW, 'accuracy · completeness · relevance')}
    summarization      : {c(YELLOW, 'completeness · conciseness · accuracy')}

  {c(ORANGE, f'✏  You will type ≈{total_ratings} numbers in total (one per metric per run).')}
  {c(DIM, 'Tip: skim the output first, then rate. It takes about 10–15 minutes at a relaxed pace.')}
  {c(DIM, 'Scores are saved to scores.json only at the very end. Do not Ctrl-C partway through.')}
""")
input(f"  {c(BOLD, 'Press Enter to start scoring...')} ")

# Dict to store scores
scores = {}
scored_count = 0

for use_case in data:
    scores[use_case] = {}
    subheader(f"Use Case: {use_case.upper()}")
    print(f"  {c(DIM, 'Metrics: ')}{c(YELLOW, ' · '.join(metrics[use_case]))}")
    for model in data[use_case]:
        scores[use_case][model] = {}
        print(f"\n  {c(BOLD, 'Model: ')}{c(CYAN, model)}")
        for run_data in data[use_case][model]:
            run = run_data['run']
            output = run_data['output']
            time_taken = run_data['time']
            print()
            print(c(YELLOW, "  " + "-" * 60))
            print(f"  {c(BOLD, f'Run {run}')}  {c(DIM, f'({time_taken:.2f}s)')}")
            print(c(YELLOW, "  " + "-" * 60))
            print(f"\n  {c(DIM, 'Output (first 500 chars):')}")  
            print(f"  {output[:500]}{'...' if len(output) > 500 else ''}")
            print()
            scores[use_case][model][f'run_{run}'] = {}
            for metric in metrics[use_case]:
                while True:
                    try:
                        raw = input(f"  {c(BOLD, f'Rate {metric}')} {c(DIM, '(1-5)')} : ")
                        score = int(raw)
                        if 1 <= score <= 5:
                            scores[use_case][model][f'run_{run}'][metric] = score
                            scored_count += 1
                            break
                        else:
                            print(f"  {c(RED, 'Please enter a number between 1 and 5.')}")
                    except ValueError:
                        print(f"  {c(RED, 'Invalid input — enter a number 1–5.')}")

# Save scores to JSON
with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=4)

print()
print(c(CYAN, "=" * 64))
print(c(BOLD + GREEN, "  ✔ Scoring complete"))
print(c(CYAN, "=" * 64))
print(f"""
  {c(BOLD, 'Scores saved to:')} {c(CYAN, 'scores.json')}
  {c(BOLD, 'Total ratings  :')} {c(GREEN, str(scored_count))}

  {c(BOLD, 'Next step:')}
  Open {c(CYAN, 'scores.json')} to inspect the raw numbers, or read
  {c(CYAN, 'docs/test2.html')} for analysis of what these scores mean.
""")
print(c(DIM, "  ─" * 32))
print(f"  {c(BOLD, '📖 Full analysis:')} {c(CYAN, 'docs/test2.html')}  (open docs/index.html)")
print()
