import streamlit as st


def display_feedback(feedback):
    if not feedback:
        st.info("No feedback available yet.")
        return

    st.markdown("### 📝 Post-Interview Feedback")

    # Overall Score
    score = feedback.get("score")
    st.markdown(f"**Overall Score:** {score if score is not None else '-'} / 10")

    # Strengths
    strengths = feedback.get("strengths") or []
    st.markdown("**Strengths:**")
    if strengths:
        for s in strengths:
            st.markdown(f"- {s}")
    else:
        st.markdown("- None")

    # Improvements
    improvements = feedback.get("improvements") or []
    st.markdown("**Improvements:**")
    if improvements:
        for imp in improvements:
            st.markdown(f"- {imp}")
    else:
        st.markdown("- None")

    # Competency Scores
    comp = feedback.get("competency_scores") or {}
    if comp:
        st.markdown("**Competency Scores:**")
        for k, v in comp.items():
            st.markdown(f"{k.capitalize()}: {v}/10")
            st.progress(v / 10)
    else:
        st.markdown("No competency scores available.")
