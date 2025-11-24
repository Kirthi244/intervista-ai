import streamlit as st
from components.chat_panel import display_chat
from components.feedback_panel import display_feedback
from components.role_selector import select_role_experience
from components.voice_input import get_voice_input, speak_text
from services.api import post_interview
import hashlib

# ---------------------------
# App Config
# ---------------------------
st.set_page_config(
    page_title="InterVista AI",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

st.markdown("""
<div style="background: linear-gradient(90deg, #4CAF50, #81C784); padding: 20px; border-radius: 10px;">
<h1 style='text-align:center;color:white;'>InterVista AI Mock Interview</h1>
<p style='text-align:center;color:white;'>Practice interviews with real-time AI feedback</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Session State Initialization
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "question" not in st.session_state:
    st.session_state.question = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "role" not in st.session_state:
    st.session_state.role = ""
if "experience" not in st.session_state:
    st.session_state.experience = 1
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 1
if "interview_ended" not in st.session_state:
    st.session_state.interview_ended = False
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

TOTAL_TURNS = 10

# ---------------------------
# Sidebar: Role + Experience
# ---------------------------
with st.sidebar:
    st.subheader("🔧 Interview Settings")
    st.session_state.candidate_name = st.text_input(
        "Candidate Name:", st.session_state.get("candidate_name", "")
    )
    st.session_state.role, st.session_state.experience = select_role_experience()

    st.session_state.department = st.selectbox(
        "Department / Team", ["Engineering", "Sales", "Marketing", "Support", "Data"]
    )

    st.session_state.interview_type = st.radio(
        "Interview Type", ["Technical", "HR", "Mixed"]
    )

    st.session_state.language = st.selectbox(
        "Preferred Language", ["English", "Spanish", "French", "Other"]
    )

    st.session_state.confidence = st.slider(
        "Difficulty Level (1-10):", 1, 10, st.session_state.get("confidence", 5)
    )

    if st.button("🏁 End Interview"):
        st.session_state.interview_ended = True
        st.success("Interview Ended! Feedback below ⬇️")

# ---------------------------
# Progress Tracker
# ---------------------------
st.markdown(f"### Turn: {st.session_state.turn_count}/{TOTAL_TURNS}")
st.progress(min(st.session_state.turn_count / TOTAL_TURNS, 1.0))


# ---------------------------
# Handle User Answer
# ---------------------------
def handle_answer(answer_text):
    """Process user answer and update chat"""
    if not answer_text.strip():
        return

    # Append user's answer
    st.session_state.history.append({"from": "user", "text": answer_text})

    # Backend call
    payload = {
        "role": st.session_state.role,
        "question_context": f"Experience: {st.session_state.experience} years",
        "last_question": st.session_state.question,
        "user_answer": answer_text,
        "history": st.session_state.history,
        "turn_count": st.session_state.turn_count
    }

    res = post_interview(payload)

    # Append bot reply
    bot_reply = res.get("interviewer_reply", "Hmm, can you elaborate?")
    st.session_state.history.append({"from": "bot", "text": bot_reply})
    st.session_state.question = res.get("next_question", bot_reply)
    st.session_state.feedback = res.get("quick_feedback", {})
    st.session_state.turn_count += 1

    # Speak bot reply
    speak_text(bot_reply)

# ---------------------------
# Start Interview: First Question
# ---------------------------
if st.session_state.turn_count == 1 and not st.session_state.question:
    payload = {
        "role": st.session_state.role,
        "question_context": f"Experience: {st.session_state.experience} years",
        "last_question": "",
        "user_answer": "",
        "history": st.session_state.history,
        "turn_count": st.session_state.turn_count
    }
    res = post_interview(payload)
    first_question = res.get("interviewer_reply", "Let's start the interview!")
    st.session_state.history.append({"from": "bot", "text": first_question})
    st.session_state.question = res.get("next_question", first_question)
    st.session_state.feedback = res.get("quick_feedback", {})
    speak_text(first_question)

# ---------------------------
# User Input: Text + Voice
# ---------------------------
col1, col2 = st.columns([4,1])
with col1:
    st.text_input(
        "💬 Type your answer here and press Enter:",
        key="user_input",
        on_change=lambda: handle_answer(st.session_state.user_input),
        value=""
    )

with col2:
    if st.button("🎙️ Speak Answer"):
        voice_text = get_voice_input()  # get voice input
        handle_answer(voice_text)       # pass directly to handler

# ---------------------------
# Display Chat
# ---------------------------
st.markdown("### 💬 Conversation")
display_chat(st.session_state.history)

# ---------------------------
# End Interview Feedback
# ---------------------------
if st.session_state.interview_ended or st.session_state.turn_count > TOTAL_TURNS:
    st.markdown("---")
    st.markdown("<h2 style='color:#4CAF50;'>🏆 Interview Feedback</h2>", unsafe_allow_html=True)
    display_feedback(st.session_state.feedback)
    st.stop()
