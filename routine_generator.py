import streamlit as st
from datetime import time


def routine_page():
    st.title("🕒 Personalized Daily Routine Generator")

    st.markdown("""
    This is **optional**.

    Answer a few questions and we’ll design a **balanced daily routine**
    for your lifestyle — not just study.
    """)

    st.divider()

    with st.form("routine_form"):
        wake_time = st.time_input("Wake-up time", time(6, 30))
        sleep_time = st.time_input("Sleep time", time(22, 30))

        work_hours = st.number_input(
            "Work / Uni hours per day",
            min_value=0,
            max_value=16,
            value=6
        )

        include_prayer = st.checkbox("Include prayer / reflection time", True)
        include_exercise = st.checkbox("Include exercise", True)

        free_time_level = st.selectbox(
            "How much free time do you want?",
            ["Low", "Medium", "High"]
        )

        generate = st.form_submit_button("✨ Generate Routine")

    if generate:
        st.subheader("📅 Your Suggested Daily Routine")
        st.divider()

        routine = []

        routine.append(f"🛏 Wake up at {wake_time.strftime('%H:%M')}")

        if include_prayer:
            routine.append("🙏 Prayer / Reflection")

        routine.append("🚿 Shower & Breakfast")
        routine.append(f"💼 Work / Uni ({work_hours} hrs)")
        routine.append("🍽 Lunch & Rest")

        if include_exercise:
            routine.append("🏃 Exercise / Walk")

        if free_time_level == "High":
            routine.append("🎮 Long Free Time / Family / Hobbies")
        elif free_time_level == "Medium":
            routine.append("📖 Light Personal Tasks / Relax")
        else:
            routine.append("🧠 Minimal Free Time / Wind Down")

        routine.append("🌙 Prepare for sleep")
        routine.append(f"😴 Sleep at {sleep_time.strftime('%H:%M')}")

        for step in routine:
            st.write(step)

        st.success("Routine generated successfully ✨")
