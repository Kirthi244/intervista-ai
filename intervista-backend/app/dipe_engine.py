# app/dipe_engine.py
"""
Dynamic Interview Path Engine (DIPE)

Simple but extensible logic to pick the next question type based on:
 - last quick feedback (competency scores)
 - number of turns so far
 - simple randomness for variety
"""

from typing import Dict
import random

def choose_next_type(last_quick_feedback: Dict, turn_count: int) -> str:
    """
    Decide next question type.

    Returns one of:
      "technical", "behavioral", "follow_up", "problem_solving", "wrap_up"
    """
    # safe defaults
    if not last_quick_feedback or not isinstance(last_quick_feedback, dict):
        return "behavioral" if random.random() < 0.5 else "technical"

    comp = last_quick_feedback.get("competency_scores") or last_quick_feedback.get("scores") or {}
    # normalize values (0-10 expected)
    def get_score(k):
        try:
            v = comp.get(k, None)
            return float(v) if v is not None else 5.0
        except Exception:
            return 5.0

    tech = get_score("technical")
    comm = get_score("communication")
    prob = get_score("problem_solving")
    beh = get_score("behavioral")

    # If the candidate is weak technically -> technical probe
    if tech < 6:
        return "technical"

    # If problem solving low -> problem solving question
    if prob < 6:
        return "problem_solving"

    # If behavioral low -> probe behavioral
    if beh < 6:
        return "behavioral"

    # If communication low -> follow up for clarity
    if comm < 6:
        return "follow_up"

    # If many turns already -> consider wrap up or problem solving
    if turn_count >= 8:
        return "wrap_up"

    # otherwise alternate for variety
    choices = ["technical", "behavioral", "follow_up", "problem_solving"]
    # weigh technical slightly higher
    weights = [0.35, 0.25, 0.2, 0.2]
    return random.choices(choices, weights, k=1)[0]
