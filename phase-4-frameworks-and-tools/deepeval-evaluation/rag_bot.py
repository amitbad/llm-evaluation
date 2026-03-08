import os
import sys

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import yaml
from model_client import call_model
from retriever import retrieve

CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")

with open(CONFIG_FILE, "r") as f:
    config = yaml.safe_load(f)

cfg          = config["phase3_rag"]
BOT_MODEL    = cfg["BOT_MODEL"]
BOT_PROVIDER = cfg["BOT_PROVIDER"]
TOP_K        = cfg.get("TOP_K_CHUNKS", 3)

SYSTEM_PROMPT = """You are a helpful assistant for NextGen Banking and Finance.
Answer the customer's question using ONLY the information provided in the context below.
If the context does not contain enough information to answer, say clearly that the information is not available in our documentation.
Do not guess, invent figures, or use any knowledge outside of the provided context."""


def get_response(question, verbose=False):
    if verbose:
        print(f"  → Retrieving top {TOP_K} chunks...", flush=True)

    chunks = retrieve(question, top_k=TOP_K)

    if verbose:
        for c in chunks:
            print(f"    [score {c['score']}] chunk {c['id']} — {c['source']}")
        print(f"  → Sending to {BOT_MODEL}...", flush=True)

    context_parts = []
    for c in chunks:
        context_parts.append(f"[Source: {c['source']}]\n{c['text']}")
    context_block = "\n\n---\n\n".join(context_parts)

    user_message = f"""Context:
{context_block}

---

Customer question: {question}"""

    answer = call_model(
        provider=BOT_PROVIDER,
        model=BOT_MODEL,
        system=SYSTEM_PROMPT,
        prompt=user_message
    )

    return {
        "question":         question,
        "answer":           answer,
        "retrieved_chunks": chunks
    }


if __name__ == "__main__":
    test_questions = [
        "How long does it take to open a NextGen account?",
        "What is the penalty for an unarranged overdraft?",
        "Does NextGen offer a student current account?",
    ]

    print("=" * 60)
    print(f"RAG Bot — {BOT_MODEL} ({BOT_PROVIDER})")
    print(f"Running {len(test_questions)} test questions")
    print("=" * 60)

    for i, q in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] Q: {q}")
        result = get_response(q, verbose=True)
        print(f"  → Answer: {result['answer']}")
        print("-" * 60)

    print("\nDone.")
