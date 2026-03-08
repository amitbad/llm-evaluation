import json
import os
import re
import sys
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from model_client import call_model
from tools import get_tool_schemas, run_tool


def run_agent(
    question: str,
    model: str,
    provider: str,
    ollama_url: str,
    max_steps: int = 3,
) -> dict[str, Any]:
    trace: list[dict[str, Any]] = []
    tool_schemas = get_tool_schemas()
    tool_descriptions = "\n".join(
        f'- {tool["name"]}: {tool["description"]}. Arguments: {json.dumps(tool["arguments"])}'
        for tool in tool_schemas
    )

    conversation = [
        {
            "role": "user",
            "content": question,
        }
    ]

    for step_no in range(1, max_steps + 1):
        prompt = _build_prompt(question, conversation, tool_descriptions, max_steps, step_no)
        raw_output = call_model(
            model=model,
            provider=provider,
            prompt=prompt,
            system=_system_prompt(),
            ollama_url=ollama_url,
        )
        action = _parse_action(raw_output)

        if not action:
            trace.append({
                "step": step_no,
                "action": "error",
                "raw_output": raw_output,
                "error": "Model did not return valid JSON action",
            })
            return {
                "final_answer": "I could not complete the task because the agent output was malformed.",
                "stop_reason": "malformed_action",
                "trace": trace,
            }

        if action.get("action") == "final":
            answer = str(action.get("answer", "")).strip()
            trace.append({
                "step": step_no,
                "action": "final",
                "answer": answer,
                "raw_output": raw_output,
            })
            return {
                "final_answer": answer,
                "stop_reason": "final_answer",
                "trace": trace,
            }

        if action.get("action") != "tool":
            trace.append({
                "step": step_no,
                "action": "error",
                "raw_output": raw_output,
                "error": f"Unknown action type: {action.get('action')}",
            })
            return {
                "final_answer": "I could not complete the task because the agent chose an invalid action.",
                "stop_reason": "invalid_action",
                "trace": trace,
            }

        tool_name = str(action.get("tool_name", "")).strip()
        arguments = action.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}

        tool_result = run_tool(tool_name, arguments)
        trace.append({
            "step": step_no,
            "action": "tool",
            "tool_name": tool_name,
            "arguments": arguments,
            "tool_result": tool_result,
            "raw_output": raw_output,
        })

        conversation.append({
            "role": "assistant",
            "content": raw_output,
        })
        conversation.append({
            "role": "tool",
            "content": json.dumps({
                "tool_name": tool_name,
                "result": tool_result,
            }, ensure_ascii=False),
        })

    return {
        "final_answer": "I could not complete the task within the maximum allowed steps.",
        "stop_reason": "max_steps_reached",
        "trace": trace,
    }


def _system_prompt() -> str:
    return (
        "You are a small evaluation-only banking agent. "
        "Your job is not to be clever — it is to make tool use observable and grounded. "
        "You must output JSON only. No markdown. No explanation outside JSON. "
        "When structured account data is needed, use lookup_account_status. "
        "When policy/process information is needed, use search_docs. "
        "If the request is out of banking scope, return a final answer refusing politely. "
        "If a required argument is missing, ask a clarifying question as the final answer."
    )


def _build_prompt(
    question: str,
    conversation: list[dict[str, str]],
    tool_descriptions: str,
    max_steps: int,
    current_step: int,
) -> str:
    history_lines = []
    for item in conversation:
        history_lines.append(f"{item['role'].upper()}: {item['content']}")
    history = "\n\n".join(history_lines)

    return f"""Customer question:
{question}

Available tools:
{tool_descriptions}

Conversation so far:
{history}

Current step: {current_step} of {max_steps}

Return exactly one JSON object in one of these forms:
{{"action":"tool","tool_name":"lookup_account_status","arguments":{{"account_id":"A1023"}}}}
{{"action":"tool","tool_name":"search_docs","arguments":{{"query":"dormant account reactivation"}}}}
{{"action":"tool","tool_name":"calculator","arguments":{{"expression":"50000*0.12/12"}}}}
{{"action":"final","answer":"..."}}

Rules:
- Use tools when needed.
- Do not invent account details.
- Do not call tools if the question is a greeting or clearly out of banking scope.
- If account id is missing, ask for it in a final answer.
- If a tool already returned enough information, produce the final answer.
- JSON only."""


def _parse_action(raw_output: str) -> dict[str, Any] | None:
    raw_output = str(raw_output or "").strip()
    if not raw_output:
        return None

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_output)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
