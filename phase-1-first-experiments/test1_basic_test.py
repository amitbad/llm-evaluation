import ollama
import time

models = ['deepseek-r1:7b', 'mistral', 'llama3.1:8b', 'gemma2:9b']

def query_model(model, prompt):
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    end_time = time.time()
    return response['message']['content'], end_time - start_time

if __name__ == "__main__":
    prompt = "Hello, can you tell me a short joke?"
    for model in models:
        try:
            output, duration = query_model(model, prompt)
            print(f"Model: {model}")
            print(f"Response: {output}")
            print(f"Time: {duration:.2f}s")
            print("-" * 50)
        except Exception as e:
            print(f"Error with {model}: {e}")
