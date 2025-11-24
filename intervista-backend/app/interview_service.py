# app/interview_service.py
"""
Main interview orchestration:
 - Create structured prompt for quick micro-feedback
 - Call the LLM via utils.call_gemini_chat
 - Parse/validate JSON output
 - Use DIPE to choose next question type
 - Generate the next question (via LLM)
 - Call reflection service (lightweight) to get reflection signals
 - Return a single structured dict ready to be returned from endpoint
"""

from typing import Dict, Any, List
import json
import asyncio

from .prompts import render_interview_prompt, render_feedback_prompt
from .utils import call_gemini_chat
from .dipe_engine import choose_next_type
from .reflection_service import reflect_and_recommend

# Prompt wrapper that forces JSON for the interview turn
STRUCTURED_INTERVIEW_INSTRUCTION = """
You are a professional interviewer. You MUST return JSON only (no surrounding explanation).
Return an object with the following keys:
- interviewer_reply: string (1-2 sentence follow-up question or hint)
- quick_feedback: {
    "score": integer 0-10,
    "strengths": [string],
    "improvements": [string],
    "competency_scores": {
        "communication": 0-10,
        "technical": 0-10,
        "problem_solving": 0-10,
        "behavioral": 0-10
    }
}
Return JSON only.
"""

QUESTION_GEN_INSTRUCTION = """
You are an interviewer. Return a interview question (one sentence) of the requested type.
Type: {qtype}
Role: {role}
User Answer: {user_answer}
Context (optional): {context}
Return only the question text.
"""

def _extract_json_from_text(text: str):
    """
    Attempts to parse JSON from LLM text output robustly.
    """
    if not isinstance(text, str):
        return None
    txt = text.strip()
    # try direct
    try:
        return json.loads(txt)
    except Exception:
        pass
    # find first json-like block
    first = txt.find('{')
    last = txt.rfind('}')
    if first != -1 and last != -1 and last > first:
        candidate = txt[first:last+1]
        try:
            return json.loads(candidate)
        except Exception:
            # naive replacement single->double quotes
            try:
                candidate2 = candidate.replace("'", '"')
                return json.loads(candidate2)
            except Exception:
                return None
    return None

async def run_interview_turn(role: str,
                             question_context: str,
                             last_question: str,
                             user_answer: str,
                             history: List[Dict[str, str]] = None,
                             turn_count: int = 1) -> Dict[str, Any]:
    """
    Orchestrates a single interview step and returns structured response:
    {
      next_question: str,
      question_type: str,
      micro_feedback: {...},
      dipe_state: {...},
      reflection_signal: {...}
    }
    """
    history = history or []
    # 1) Render the interview prompt (base) and add instruction to produce JSON
    base_prompt = render_interview_prompt(
        role=role,
        question_context=question_context,
        last_question=last_question,
        user_answer=user_answer,
        history=history
    )

    full_prompt = STRUCTURED_INTERVIEW_INSTRUCTION + "\n\n" + base_prompt

    # 2) Call LLM for structured micro-feedback + interviewer reply
    raw = await call_gemini_chat(full_prompt)
    parsed = _extract_json_from_text(raw)

    # If parsing failed, attempt to salvage by asking LLM to reformat
    if parsed is None:
        # Ask LLM to convert its previous answer to JSON only
        salvage_prompt = f"Please reformat the following into valid JSON with keys interviewer_reply and quick_feedback only:\n\n{raw}\n\nJSON:"
        salvage_raw = await call_gemini_chat(salvage_prompt)
        parsed2 = _extract_json_from_text(salvage_raw)
        parsed = parsed2 if parsed2 is not None else None

    if parsed is None:
        # Fallback defaults
        interviewer_reply = f"Thanks for your answer. Could you give more detail about the architecture you used?"
        quick_feedback = {
            "score": None,
            "strengths": [],
            "improvements": [],
            "competency_scores": {}
        }
    else:
        interviewer_reply = parsed.get("interviewer_reply") or parsed.get("agent_prompt") or ""
        quick_feedback = parsed.get("quick_feedback") or parsed

    # 3) Use DIPE to pick next question type
    next_type = choose_next_type(quick_feedback, turn_count)

    # 4) Generate a next question string (call LLM)
    qgen_prompt = QUESTION_GEN_INSTRUCTION + f"\nUser Answer: {user_answer}\nContext: {question_context or ''}\nType: {next_type}\nRole: {role}"

    try:
        next_q_raw = await call_gemini_chat(qgen_prompt)
        # the question should be a single sentence; strip extra whitespace
        next_question = (next_q_raw or "").strip().strip('"').strip("'")
        # If LLM returned JSON or paragraphs, extract first line
        if "\n" in next_question:
            next_question = next_question.splitlines()[0].strip()
        # ensure it ends with '?'
        if not next_question.endswith('?'):
            next_question = next_question.rstrip('.') + '?'
    except Exception as e:
        next_question = "Could you expand on that a bit more?"

    # 5) Reflection (async) - do not block too long (fire and await short timeout)
    reflection_signal = {}
    try:
        # run reflection with modest timeout
        refl_task = reflect_and_recommend(history + [{"role":"assistant","text":interviewer_reply},{"role":"user","text":user_answer}], last_n=6)
        # await the task (it is async) but protect with timeout
        reflection_signal = await asyncio.wait_for(refl_task, timeout=10.0)
    except asyncio.TimeoutError:
        reflection_signal = {"raw": "reflection timeout"}
    except Exception as e:
        reflection_signal = {"error": str(e)}

    # 6) Build DIPE state reason (simple)
    dipe_state = {
        "route": next_type,
        "reason": f"DIPE chose {next_type} based on quick_feedback and turn_count={turn_count}"
    }

    # 7) Build final structured response
    resp = {
        "interviewer_reply": interviewer_reply,
        "quick_feedback": quick_feedback,
        "next_question": next_question,
        "question_type": next_type,
        "dipe_state": dipe_state,
        "reflection_signal": reflection_signal
    }

    return resp
