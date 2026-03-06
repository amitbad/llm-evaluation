"""
model_client.py — Universal Model Caller
=========================================
Lives at project root. Used by all phase scripts.

Supported providers:
  ollama    — local models via Ollama (default, free)
  openai    — GPT-4o, GPT-4o-mini, etc.
  anthropic — Claude Sonnet, Claude Haiku, etc.
  gemini    — Gemini 1.5 Pro, Gemini 1.5 Flash, etc.

API Key resolution order (first found wins):
  1. api_key argument passed directly to call_model()
  2. Environment variable (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)

config.yaml example — mixed providers:
  phase2_groundedness:
    BOT_MODEL: "llama3.1:8b"
    BOT_PROVIDER: "ollama"
    JUDGE_MODEL: "gpt-4o-mini"
    JUDGE_PROVIDER: "openai"
    OPENAI_API_KEY: "sk-..."        # or leave blank to use env var

Usage:
  from model_client import call_model

  response = call_model(model="llama3.1:8b", prompt="Hello", system="You are...")
  response = call_model(model="gpt-4o-mini", prompt="Hello", provider="openai", api_key="sk-...")
"""

import os
import requests


def call_model(
    model: str,
    prompt: str,
    system: str = "",
    provider: str = "ollama",
    ollama_url: str = "http://localhost:11434/api/generate",
    api_key: str = ""
) -> str:
    """
    Send a prompt to any supported model provider and return the response text.

    Args:
        model:       Model name e.g. "llama3.1:8b", "gpt-4o-mini", "claude-3-5-haiku-20241022"
        prompt:      The user message / prompt
        system:      Optional system prompt
        provider:    "ollama" | "openai" | "anthropic" | "gemini"
        ollama_url:  Ollama endpoint (only used when provider="ollama")
        api_key:     API key — if blank, falls back to environment variable

    Returns:
        Response text as a string, or "ERROR: ..." on failure.
    """
    provider = provider.lower().strip()

    if provider == "ollama":
        return _call_ollama(model, prompt, system, ollama_url)
    elif provider == "openai":
        return _call_openai(model, prompt, system, _resolve_key(api_key, "OPENAI_API_KEY"))
    elif provider == "anthropic":
        return _call_anthropic(model, prompt, system, _resolve_key(api_key, "ANTHROPIC_API_KEY"))
    elif provider == "gemini":
        return _call_gemini(model, prompt, system, _resolve_key(api_key, "GEMINI_API_KEY"))
    else:
        return f"ERROR: Unknown provider '{provider}'. Use: ollama | openai | anthropic | gemini"


def _resolve_key(config_key: str, env_var: str) -> str:
    """
    Return config_key if set, otherwise fall back to environment variable.
    config.yaml key wins — allows per-project override.
    env var fallback — allows secure storage outside the repo.
    """
    if config_key and config_key.strip():
        return config_key.strip()
    return os.environ.get(env_var, "")


# ── Ollama ─────────────────────────────────────────────────────────────────────

def _call_ollama(model: str, prompt: str, system: str, url: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "ERROR: Cannot connect to Ollama. Is it running? Try: ollama serve"
    except Exception as e:
        return f"ERROR: {e}"


# ── OpenAI ─────────────────────────────────────────────────────────────────────

def _call_openai(model: str, prompt: str, system: str, api_key: str) -> str:
    if not api_key:
        return "ERROR: No OpenAI API key found. Set OPENAI_API_KEY in config.yaml section or as environment variable."

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": messages}

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError:
        return f"ERROR: OpenAI API error — {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"ERROR: {e}"


# ── Anthropic ──────────────────────────────────────────────────────────────────

def _call_anthropic(model: str, prompt: str, system: str, api_key: str) -> str:
    if not api_key:
        return "ERROR: No Anthropic API key found. Set ANTHROPIC_API_KEY in config.yaml section or as environment variable."

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system:
        payload["system"] = system

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"].strip()
    except requests.exceptions.HTTPError:
        return f"ERROR: Anthropic API error — {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"ERROR: {e}"


# ── Gemini ─────────────────────────────────────────────────────────────────────

def _call_gemini(model: str, prompt: str, system: str, api_key: str) -> str:
    if not api_key:
        return "ERROR: No Gemini API key found. Set GEMINI_API_KEY in config.yaml section or as environment variable."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.HTTPError:
        return f"ERROR: Gemini API error — {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return f"ERROR: {e}"
