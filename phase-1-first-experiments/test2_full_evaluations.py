import ollama
import time
import json

models = ['deepseek-r1:7b', 'mistral', 'llama3.1:8b', 'gemma2:9b']

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

results = {}

for use_case, data in use_cases.items():
    results[use_case] = {}
    prompt = data['prompt']
    for model in models:
        results[use_case][model] = []
        for run in range(1, 4):  # 3 runs for consistency
            try:
                output, duration = query_model(model, prompt)
                results[use_case][model].append({
                    'run': run,
                    'output': output,
                    'time': duration
                })
                print(f"Completed {use_case} for {model}, run {run}")
            except Exception as e:
                results[use_case][model].append({
                    'run': run,
                    'output': f"Error: {e}",
                    'time': 0
                })
                print(f"Error in {use_case} for {model}, run {run}: {e}")

with open('evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Evaluation complete. Results saved to evaluation_results.json.")
