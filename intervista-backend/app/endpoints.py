# app/endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from .interview_service import run_interview_turn

router = APIRouter()


class InterviewRequest(BaseModel):
    role: str
    question_context: str = ""
    last_question: str = ""
    user_answer: str = ""
    history: List[Dict[str, Any]] = []
    turn_count: int = 1  # optional – useful later if you track turns in DB


@router.post("/interview")
async def interview(req: InterviewRequest):
    """
    Orchestrates a single turn of the AI interview.
    It calls run_interview_turn() which performs:
        - JSON-safe structured LLM call
        - DIPE: next-question routing engine
        - Reflection engine
        - Next question generation
    """
    try:
        result = await run_interview_turn(
            role=req.role,
            question_context=req.question_context,
            last_question=req.last_question,
            user_answer=req.user_answer,
            history=req.history,
            turn_count=req.turn_count,
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
