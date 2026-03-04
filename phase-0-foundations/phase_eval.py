# ===================================================================
# This script performs Phase 1 evaluation of the Llama 3.1 8B model using Ollama.
# We are testing the model's ability to generate responses that contain specific required keywords for a set of predefined prompts.
# We are trying to determine if the model passes basic deterministic checks (keyword presence) and measure response latency.
# The evaluation uses a mini golden dataset and reports pass/fail status along with timing.
# ===================================================================

import ollama
import time
import re


def validate_math(output):
    # This regex looks for '4' or 'four' (case insensitive)
    pattern = r"\b(4|four)\b"
    if re.search(pattern, output.lower()):
        return True
    return False

# 1. Your 'Mini' Golden Dataset
test_cases = [
    {"prompt": "Tell a joke about a robot.", "must_contain": "robot"},
    {"prompt": "Summarize: The sky is blue because of Rayleigh scattering.", "must_contain": "scattering"},
    {
       "prompt": "What is 2+2? Answer in one word.", "must_contain": "four",
      "validator": validate_math
    }
]


def run_phase1():
    results = []
    
    for case in test_cases:
        print(f"Testing: {case['prompt']}...")
        
        # Start timer
        start_time = time.time()
        
        # Call Ollama
        response = ollama.chat(model='llama3.1:8b', messages=[
            {'role': 'user', 'content': case['prompt']},
        ])
        
        # Calculate time taken
        duration = time.time() - start_time
        output = response['message']['content']
        
        print(f"Output: {output}\n")
        
        # Deterministic Check (The "Pass/Fail")
        passed = case['must_contain'].lower() in output.lower()
        
        results.append({
            "prompt": case['prompt'],
            "output": output,
            "latency": round(duration, 2),
            "passed": passed
        })

    # Print a summary report
    print("\n--- PHASE 1 REPORT ---")
    for r in results:
        status = "✅" if r['passed'] else "❌"
        print(f"{status} | Time: {r['latency']}s | Prompt: {r['prompt']}")

if __name__ == "__main__":
    run_phase1()