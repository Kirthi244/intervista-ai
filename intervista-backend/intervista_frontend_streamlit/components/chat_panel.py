# chat_panel.py
import streamlit as st
from streamlit_chat import message

def display_chat(history):
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 0

    for h in history:
        key = f"msg_{st.session_state.msg_counter}"
        message(
            h["text"],
            is_user=h["from"] == "user",
            key=key
        )
        st.session_state.msg_counter += 1
