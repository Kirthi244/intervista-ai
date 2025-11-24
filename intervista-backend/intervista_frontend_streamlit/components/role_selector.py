import streamlit as st

def select_role_experience():
    role = st.selectbox(
        "Select Role for Mock Interview",
        ["Software Engineer", "Sales Associate", "Retail Associate", "Data Analyst"]
    )
    experience = st.slider(
        "Experience (Years)",
        min_value=0, max_value=10, value=1
    )
    return role, experience
