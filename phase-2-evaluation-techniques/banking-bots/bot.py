"""
bot.py — Banking Chatbot using Ollama (llama3.1:8b)

This module defines the core chatbot logic for Global Bank's assistant.
It supports both single-turn queries and multi-turn conversations.
"""

import ollama

# ─── Configuration ────────────────────────────────────────────────────────────

MODEL_NAME = "llama3.1:8b"

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
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_query},
    ]
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return response["message"]["content"]


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
        response = ollama.chat(model=MODEL_NAME, messages=self.history)
        bot_reply = response["message"]["content"]
        self.history.append({"role": "assistant", "content": bot_reply})
        return bot_reply

    def reset(self):
        """Clear conversation history (keep system prompt)."""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]