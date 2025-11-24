from jinja2 import Template

INTERVIEW_TPL = Template("""
System: Act as a professional interviewer for role: {{ role }}.
Task:
1) Based on the candidate's answer produce interviewer_reply (1-2 sentences, either follow-up question or corrective hint).
2) Provide quick_feedback JSON:
{
  "score": integer 0-10,
  "strengths": [...],
  "improvements": [...],
  "competency_scores": {
    "communication": 0-10,
    "technical": 0-10,
    "problem_solving": 0-10,
    "behavioral": 0-10
  }
}
Output JSON only with keys: interviewer_reply, quick_feedback.

Context:
{{ question_context }}

Last question: {{ last_question }}
User answer: {{ user_answer }}

Conversation history:
{% for h in history %}
{{ h.from }}: {{ h.text }}
{% endfor %}
""".strip())

FEEDBACK_TPL = Template("""
System: Act as an expert interviewer and coach for role: {{ role }}.
Task: Using the conversation history below, produce JSON with keys:
- summary: 2-3 sentence summary
- scores: {communication, technical, problem_solving, behavioral} (0-10)
- improvements: 2 actionable improvements per competency
- exemplar: one rewritten exemplary answer (choose best candidate answer)
- resources: list of 3 resources {title, url}

Conversation history:
{% for h in history %}
{{ h.from }}: {{ h.text }}
{% endfor %}
""".strip())

def render_interview_prompt(role, question_context, last_question, user_answer, history):
    return INTERVIEW_TPL.render(
        role=role,
        question_context=question_context or "",
        last_question=last_question or "",
        user_answer=user_answer or "",
        history=history or []
    )

def render_feedback_prompt(role, history):
    return FEEDBACK_TPL.render(role=role, history=history or [])
