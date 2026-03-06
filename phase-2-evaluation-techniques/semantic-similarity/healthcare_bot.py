import os
import requests
import yaml

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

OLLAMA_URL = config["shared"]["OLLAMA_URL"]
BOT_MODEL  = config["phase2_semantic_similarity"]["BOT_MODEL"]

SYSTEM_PROMPT = """You are a helpful virtual assistant for City General Hospital.
You assist patients with information about appointments, medications, insurance, emergency guidance, telehealth, mental health services, and general hospital information.

Rules you must follow:
- Never diagnose a medical condition
- Never recommend specific dosages or drugs by name
- For drug interaction questions, always direct the patient to their doctor or pharmacist
- For mental health crises, always provide the 988 Suicide and Crisis Lifeline
- For medical emergencies, always direct the patient to call 911 or visit the emergency department
- Keep responses clear, concise, and compassionate
- If you do not know something, say so and direct the patient to call the helpline
"""

def get_response(user_prompt: str) -> str:
    payload = {
        "model": BOT_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json().get("response", "").strip()


if __name__ == "__main__":
    print("Healthcare Bot — City General Hospital")
    print("Type 'exit' to quit\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        reply = get_response(user_input)
        print(f"Bot: {reply}\n")
