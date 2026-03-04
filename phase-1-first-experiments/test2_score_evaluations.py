import json

# Load the evaluation results
with open('evaluation_results.json', 'r') as f:
    data = json.load(f)

# Define metrics per use case
metrics = {
    'text_generation': ['coherence', 'creativity', 'fluency'],
    'question_answering': ['accuracy', 'completeness', 'relevance'],
    'summarization': ['completeness', 'conciseness', 'accuracy']
}

# Dict to store scores
scores = {}

print("Manual Scoring: Rate each output 1-5 for each metric (1=poor, 5=excellent).")

for use_case in data:
    scores[use_case] = {}
    print(f"\n--- {use_case.upper()} ---")
    for model in data[use_case]:
        scores[use_case][model] = {}
        print(f"\nModel: {model}")
        for run_data in data[use_case][model]:
            run = run_data['run']
            output = run_data['output']
            time_taken = run_data['time']
            print(f"\nRun {run} (Time: {time_taken:.2f}s)")
            print(f"Output: {output[:500]}...")  # Truncate for readability
            scores[use_case][model][f'run_{run}'] = {}
            for metric in metrics[use_case]:
                while True:
                    try:
                        score = int(input(f"Rate {metric} (1-5): "))
                        if 1 <= score <= 5:
                            scores[use_case][model][f'run_{run}'][metric] = score
                            break
                        else:
                            print("Please enter 1-5.")
                    except ValueError:
                        print("Invalid input. Enter a number 1-5.")

# Save scores to JSON
with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=4)

print("\nScoring complete. Scores saved to scores.json.")
