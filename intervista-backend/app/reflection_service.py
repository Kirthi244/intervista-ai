# app/reflection_service.py
"""
Reflection chain: ask the LLM to analyze recent turns and return
structured recommendations to improve the interview path.

This module uses your existing call_gemini_chat function.
"""

from typing import List, Dict, Any
import json
from .utils import call_gemini_chat

REFLECTION_PROMPT = """
You are an interview reflection engine. Given the recent conversation history, produce JSON ONLY with keys:
- summary: a 1-2 sentence high-level summary of candidate performance.
- adjustments: a list (max 2) of adjustments to the interview path (brief strings).
- recommended_next_questions: list of objects {"type": "...", "question": "..."} (max 3).

History:
{history_text}

Return only valid JSON.
"""

def _render_history(history: List[Dict[str, str]]) -> str:
    """
    Accepts history as list of {"role": "assistant"/"user", "text": "..."}
    Renders as plain text for the LLM.
    """
    lines = []
    for h in history:
        role = h.get("role", "assistant")
        text = h.get("text", "")
        lines.append(f"{role}: {text}")
    return "\n".join(lines)

async def reflect_and_recommend(history: List[Dict[str, str]], last_n: int = 6) -> Dict[str, Any]:
    """
    Ask LLM to reflect on last_n turns and return parsed JSON result.
    Falls back to a minimal structure if parsing fails.
    """
    if not isinstance(history, list):
        history = []

    hist_slice = history[-last_n:]
    history_text = _render_history(hist_slice)
    prompt = REFLECTION_PROMPT.format(history_text=history_text)

    raw = await call_gemini_chat(prompt)
    # try to parse JSON from raw output
    parsed = _extract_json_or_none(raw)
    if parsed:
        return parsed

    # fallback: return simple structure with raw text
    return {
        "summary": "",
        "adjustments": [],
        "recommended_next_questions": [],
        "raw": raw
    }

def _extract_json_or_none(text: str):
    """
    Try to parse JSON from the LLM response. Handles cases where model output
    includes text before/after JSON by extracting the first {...} block.
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    # quick attempt: direct json
    try:
        return json.loads(text)
    except Exception:
        pass

    # find first '{' and last '}' and attempt to parse progressively larger spans
    first = text.find('{')
    last = text.rfind('}')
    if first != -1 and last != -1 and last > first:
        candidate = text[first:last+1]
        try:
            return json.loads(candidate)
        except Exception:
            # try to be more permissive: replace single quotes with double (not ideal)
            candidate2 = candidate.replace("'", "\"")
            try:
                return json.loads(candidate2)
            except Exception:
                return None
    return None
