import streamlit as st
from input import load_tasks, add_task
from tracker import update_task_status
from scheduler import generate_schedule
from routine_generator import routine_page
import pandas as pd


# ---------------- SESSION STATE ----------------
if "xp" not in st.session_state:
    st.session_state.xp = 0

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "mood" not in st.session_state:
    st.session_state.mood = "🙂 Okay"

if "focus_mode" not in st.session_state:
    st.session_state.focus_mode = False


def launch_dashboard():
    st.set_page_config(page_title="Smart Daily Planner", layout="wide")

    # Sidebar Navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
    "🏠 Home",
    "➕ Add Task",
    "✅ Completed Tasks",
    "📅 Schedule",
    "🕒 Daily Routine (Optional)"
]

    )

    tasks = load_tasks()
    tasks["Due Date"] = pd.to_datetime(tasks["Due Date"])

    # ---------------- HOME PAGE ----------------
    if page == "🏠 Home":

        # ---------- GREETING ----------
        st.markdown("## 👋 Welcome back!")
        st.write("Let’s make today productive ✨")

        # ---------- MOOD SELECTOR ----------
        st.markdown("### 🌈 How are you feeling today?")
        st.session_state.mood = st.radio(
            "",
            ["😄 Energized", "🙂 Okay", "😴 Tired", "😔 Low"],
            horizontal=True
        )

        # ---------- FOCUS MODE ----------
        st.session_state.focus_mode = st.toggle("🎯 Focus Mode (Only top priorities)")

        st.divider()

        # ---------- METRICS ----------
        pending_count = len(tasks[tasks["Status"] == "Pending"])
        completed_count = len(tasks[tasks["Status"] == "Completed"])

        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Pending Tasks", pending_count)
        col2.metric("✅ Completed", completed_count)
        col3.metric("⚡ XP", st.session_state.xp)

        st.divider()

        # ---------- TASK LIST ----------
        st.markdown("### 📋 Tasks")

        pending = tasks[tasks["Status"] == "Pending"].copy()

        priority_map = {"High": 1, "Medium": 2, "Low": 3}
        pending["PriorityRank"] = pending["Priority"].map(priority_map)

        pending = pending.sort_values(by=["PriorityRank", "Due Date"])

        if st.session_state.focus_mode:
            pending = pending.head(3)
            st.info("🎯 Focus Mode ON — showing top priorities only")

        if pending.empty:
            st.success("🎉 No pending tasks! You’re all caught up.")
            st.balloons()
        else:
            for _, row in pending.iterrows():

                # Priority color
                priority_icon = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢"
                }[row["Priority"]]

                checked = st.checkbox(
                    f"{priority_icon} **{row['Task Name']}** "
                    f"| {row['Category']} "
                    f"| Due: {row['Due Date'].date()}",
                    key=row["Task Name"]
                )

                if checked:
                    update_task_status(row["Task Name"], True)

                    # XP SYSTEM
                    if row["Priority"] == "High":
                        st.session_state.xp += 10
                    elif row["Priority"] == "Medium":
                        st.session_state.xp += 7
                    else:
                        st.session_state.xp += 5

                    st.success("✅ Task completed!")
                    st.rerun()


    # ---------------- ADD TASK PAGE ----------------
    elif page == "➕ Add Task":
        st.title("➕ Add New Task")

        with st.form("add_task_form"):
            task_name = st.text_input("Task Name")
            category = st.text_input("Category", "General")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date")
            duration = st.number_input(
                "Estimated Duration (hours)",
                min_value=0.5,
                max_value=24.0,
                value=1.0,
                step=0.5
            )
            notes = st.text_input("Notes / Tags")

            submit = st.form_submit_button("Add Task")

            if submit:
                if task_name.strip() == "":
                    st.error("Task name cannot be empty.")
                else:
                    add_task(
                        task_name,
                        category,
                        priority,
                        due_date,
                        duration,
                        notes
                    )
                    st.success("✅ Task added successfully!")
                    st.rerun()

    # ---------------- COMPLETED TASKS PAGE ----------------
    elif page == "✅ Completed Tasks":
        st.title("✅ Completed Tasks")

        completed = tasks[tasks["Status"] == "Completed"]

        if completed.empty:
            st.info("No completed tasks yet. Let’s get started 💪")
        else:
            for _, row in completed.iterrows():
                unchecked = st.checkbox(
                    f"{row['Task Name']} | {row['Category']} | Completed",
                    value=True
                )

                if not unchecked:
                    update_task_status(row["Task Name"], False)
                    st.rerun()

    # ---------------- SCHEDULE PAGE ----------------
    elif page == "📅 Schedule":
        st.title("📅 Suggested Daily Schedule")

        schedule = generate_schedule(tasks)

        if not schedule:
            st.info("No pending tasks to schedule.")
        else:
            for day, day_tasks in schedule.items():
                st.subheader(str(day))
                for t in day_tasks:
                    st.write(f"- {t}")

    # ---------------- ROUTINE PAGE ----------------
    elif page == "🕒 Daily Routine (Optional)":
        st.title("🕒 Daily Routine Generator")
        routine_page()  
