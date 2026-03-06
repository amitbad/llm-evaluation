"""
bot.py — Banking Chatbot using Ollama (llama3.1:8b)

This module defines the core chatbot logic for Global Bank's assistant.
It supports both single-turn queries and multi-turn conversations.
"""

import os
import sys
import yaml

# ─── Path setup + config ──────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CONFIG_FILE  = os.path.join(PROJECT_ROOT, "config.yaml")

sys.path.insert(0, PROJECT_ROOT)
from model_client import call_model

with open(CONFIG_FILE) as f:
    _cfg = yaml.safe_load(f)

MODEL_NAME  = _cfg["phase2"]["BOT_MODEL"]
_PROVIDER   = _cfg["phase2"].get("BOT_PROVIDER", _cfg["shared"].get("PROVIDER", "ollama"))
_OLLAMA_URL = _cfg["shared"].get("OLLAMA_URL", "http://localhost:11434/api/generate")
_API_KEY    = _cfg["phase2"].get("OPENAI_API_KEY",
              _cfg["phase2"].get("ANTHROPIC_API_KEY",
              _cfg["phase2"].get("GEMINI_API_KEY", "")))

SYSTEM_PROMPT = """
You are a helpful banking assistant for Global Bank.

You have knowledge about the following products and fees:
  - Gold Account: 4% annual interest rate
  - Silver Account: 1% annual interest rate
  - Bronze Account: 0.5% annual interest rate
  - International wire transfer fee: $50 per transaction
  - Domestic wire transfer fee: $15 per transaction
  - Overdraft fee: $35 per occurrence
  - Monthly maintenance fee: $10 (waived if balance > $1,000)

Guidelines:
  - Always be polite, concise, and professional.
  - Only answer questions related to banking, accounts, fees, and financial products.
  - If a question is not related to banking, politely decline and remind the user
    that you can only assist with banking inquiries.
  - Never make up information. If you don't know something, say so honestly.
"""

# ─── Single-turn Query ────────────────────────────────────────────────────────

def ask_banking_bot(user_query: str) -> str:
    """
    Send a single user query to the banking bot and return its response.

    Args:
        user_query: The user's question or message.

    Returns:
        The bot's response as a string.
    """
    return call_model(MODEL_NAME, user_query, SYSTEM_PROMPT, _PROVIDER, _OLLAMA_URL, _API_KEY)


# ─── Multi-turn Conversation ──────────────────────────────────────────────────

class BankingChatSession:
    """
    Maintains conversation history so the bot can handle follow-up questions.

    Example:
        session = BankingChatSession()
        session.chat("What is the Gold Account interest rate?")
        session.chat("How does that compare to the Silver Account?")  # bot remembers context
    """

    def __init__(self):
        self.history: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str) -> str:
        """Add user message, get bot reply, store both in history."""
        self.history.append({"role": "user", "content": user_message})
        bot_reply = call_model(MODEL_NAME, user_message, SYSTEM_PROMPT, _PROVIDER, _OLLAMA_URL, _API_KEY)
        self.history.append({"role": "assistant", "content": bot_reply})
        return bot_reply

    def reset(self):
        """Clear conversation history (keep system prompt)."""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]