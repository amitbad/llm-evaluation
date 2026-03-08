import json
import math
import os
import re
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "mock_account_data.json")
DOCUMENTS_DIR = os.path.join(SCRIPT_DIR, "documents")


with open(DATA_FILE, "r", encoding="utf-8") as f:
    ACCOUNT_DATA = json.load(f)


def get_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "name": "lookup_account_status",
            "description": "Look up structured account data using an exact account_id like A1023 or B204.",
            "arguments": {
                "account_id": "string — required exact account identifier"
            }
        },
        {
            "name": "search_docs",
            "description": "Search local banking documents for policy/process information and return the best matching snippets.",
            "arguments": {
                "query": "string — required search query"
            }
        },
        {
            "name": "calculator",
            "description": "Do deterministic numeric calculations when arithmetic is required.",
            "arguments": {
                "expression": "string — required arithmetic expression like 50000*0.12/12"
            }
        },
    ]


def run_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "lookup_account_status":
        return lookup_account_status(arguments.get("account_id", ""))
    if tool_name == "search_docs":
        return search_docs(arguments.get("query", ""))
    if tool_name == "calculator":
        return calculator(arguments.get("expression", ""))
    return {
        "ok": False,
        "tool_name": tool_name,
        "error": f"Unknown tool: {tool_name}"
    }


def lookup_account_status(account_id: str) -> dict[str, Any]:
    account_id = str(account_id or "").strip().upper()
    if not account_id:
        return {
            "ok": False,
            "tool_name": "lookup_account_status",
            "error": "Missing required argument: account_id"
        }

    record = ACCOUNT_DATA.get(account_id)
    if not record:
        return {
            "ok": False,
            "tool_name": "lookup_account_status",
            "account_id": account_id,
            "error": "Account not found"
        }

    return {
        "ok": True,
        "tool_name": "lookup_account_status",
        "record": record
    }


def search_docs(query: str, top_k: int = 2) -> dict[str, Any]:
    query = str(query or "").strip()
    if not query:
        return {
            "ok": False,
            "tool_name": "search_docs",
            "error": "Missing required argument: query"
        }

    query_terms = _normalise_terms(query)
    matches = []

    for filename in sorted(os.listdir(DOCUMENTS_DIR)):
        path = os.path.join(DOCUMENTS_DIR, filename)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]
        for section in sections:
            section_terms = _normalise_terms(section)
            overlap = len(query_terms & section_terms)
            if overlap > 0:
                matches.append({
                    "source": filename,
                    "score": overlap,
                    "text": section[:700]
                })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return {
        "ok": True,
        "tool_name": "search_docs",
        "query": query,
        "matches": matches[:top_k]
    }


def calculator(expression: str) -> dict[str, Any]:
    expression = str(expression or "").strip()
    if not expression:
        return {
            "ok": False,
            "tool_name": "calculator",
            "error": "Missing required argument: expression"
        }

    if not re.fullmatch(r"[0-9\s\+\-\*\/\(\)\.]+", expression):
        return {
            "ok": False,
            "tool_name": "calculator",
            "expression": expression,
            "error": "Unsafe expression"
        }

    try:
        result = eval(expression, {"__builtins__": {}}, {"math": math})
    except Exception as e:
        return {
            "ok": False,
            "tool_name": "calculator",
            "expression": expression,
            "error": f"Calculation failed: {e}"
        }

    return {
        "ok": True,
        "tool_name": "calculator",
        "expression": expression,
        "result": result
    }


def _normalise_terms(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9-]+", text.lower()))
