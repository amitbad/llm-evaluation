"""
banking_bot.py — Self-contained banking chatbot for Test 14 (Langfuse Observability)
======================================================================================
Answers customer banking questions using a system prompt and an Ollama model.
All model calling logic is inlined here — no imports from other phase folders.
"""

import os
import requests
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..")

SYSTEM_PROMPT = """You are a helpful banking assistant for SecureBank.
You answer customer questions about accounts, transactions, loans, and banking policies.
Be concise, accurate, and professional.
If you do not know the answer or the question is outside banking scope, say so clearly.
Never make up account balances, transaction details, or policy rules."""


def load_config() -> dict:
    config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def call_ollama(model: str, prompt: str, system: str, ollama_url: str) -> str:
    payload = {"model": model, "prompt": prompt, "system": system, "stream": False}
    try:
        response = requests.post(ollama_url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "ERROR: Cannot connect to Ollama. Is it running? Try: ollama serve"
    except Exception as e:
        return f"ERROR: {e}"


def ask_banking_bot(question: str, model: str, ollama_url: str) -> str:
    """Ask the banking bot a question and return its answer."""
    return call_ollama(model, question, SYSTEM_PROMPT, ollama_url)
