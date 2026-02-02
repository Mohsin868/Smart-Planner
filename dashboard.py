import streamlit as st
import pandas as pd

from input import load_tasks, add_task
from tracker import update_task_status
from input import delete_task

from scheduler import generate_schedule
from routine_generator import routine_page


# ---------------- SESSION STATE DEFAULTS ----------------
for key, value in {
    "mood": "🙂 Okay",
    "focus_mode": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value



def launch_dashboard():
    st.set_page_config(page_title="Smart Daily Planner", layout="wide")

    # ---------------- SAFETY CHECK ----------------
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        st.error("User session expired. Please log in again.")
        st.stop()

    user_id = st.session_state.user_id

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "➕ Add Task",
            "✅ Completed Tasks",
            "📅 Schedule",
            "🕒 Daily Routine (Optional)",
        ],
    )

    # ---------------- LOAD TASKS ----------------
    tasks = load_tasks(user_id)

    # Normalize column names ONCE (very important)
    if not tasks.empty:
        tasks.columns = [c.lower() for c in tasks.columns]
        tasks["due_date"] = pd.to_datetime(tasks["due_date"], errors="coerce")
    else:
        tasks = pd.DataFrame(
            columns=[
                "id",
                "task_name",
                "category",
                "priority",
                "due_date",
                "duration",
                "notes",
                "status",
            ]
        )

    # ======================================================
    # 🏠 HOME PAGE
    # ======================================================
    if page == "🏠 Home":

        st.markdown("## 👋 Welcome back!")
        st.write("Let’s make today productive ✨")

        # ---------- MOOD ----------
        st.markdown("### 🌈 How are you feeling today?")
        st.session_state.mood = st.radio(
            "",
            ["😄 Energized", "🙂 Okay", "😴 Tired", "😔 Low"],
            horizontal=True,
        )

        # ---------- FOCUS MODE ----------
        st.session_state.focus_mode = st.toggle("🎯 Focus Mode (Top priorities only)")

        st.divider()

        # ---------- METRICS ----------
        pending_count = len(tasks[tasks["status"] == "Pending"])
        completed_count = len(tasks[tasks["status"] == "Completed"])

        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Pending Tasks", pending_count)
        col2.metric("✅ Completed Tasks", completed_count)

        st.divider()

        # ---------- TASK LIST ----------
        st.markdown("### 📋 Tasks")

        pending = tasks[tasks["status"] == "Pending"].copy()

        priority_map = {"High": 1, "Medium": 2, "Low": 3}
        pending["rank"] = pending["priority"].map(priority_map)

        pending = pending.sort_values(by=["rank", "due_date"])

        if st.session_state.focus_mode:
            pending = pending.head(3)
            st.info("🎯 Focus Mode ON — showing top priorities only")

        if pending.empty:
            st.success("🎉 No pending tasks! You’re all caught up.")
            st.balloons()
        else:
            for _, row in pending.iterrows():

                icon = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢",
                }[row["priority"]]

                done = st.checkbox(
                    f"{icon} **{row['task_name']}** | {row['category']} | Due: {row['due_date'].date()}",
                    key=f"task_{row['id']}",
                )

                if done:
                    update_task_status(row["id"], user_id, "Completed")
                    st.success("✅ Task completed!")
                    st.rerun()

    # ======================================================
    # ➕ ADD TASK
    # ======================================================
    elif page == "➕ Add Task":

        st.title("➕ Add New Task")

        # ---------- CATEGORY OPTIONS ----------
        default_categories = [
            "Work",
            "Study",
            "Personal",
            "Health",
            "Family",
            "Errands",
            "Other"
        ]

        # ---------- FORM ----------
        with st.form("add_task_form", clear_on_submit=True):

            task_name = st.text_input("Task Name")

            # Category dropdown
            selected_category = st.selectbox(
                "Category",
                default_categories,
                index=0
            )

            # Custom category if "Other"
            if selected_category == "Other":
                custom_category = st.text_input("Custom Category")
                category = custom_category.strip() if custom_category.strip() else "Other"
            else:
                category = selected_category

            priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                index=1
            )

            due_date = st.date_input("Due Date")

            duration = st.number_input(
                "Estimated Duration (hours)",
                min_value=0.5,
                max_value=24.0,
                value=1.0,
                step=0.5
            )

            notes = st.text_input("Notes / Tags")

            # ---------- BUTTONS ----------
            col1, col2 = st.columns(2)
            add_btn = col1.form_submit_button("✅ Add Task")
            add_continue_btn = col2.form_submit_button("➕ Add & Add Another")

        # ---------- SUBMIT LOGIC ----------
        if add_btn or add_continue_btn:

            if not task_name.strip():
                st.error("❌ Task name cannot be empty.")
            else:
                add_task(
                    user_id,
                    task_name,
                    category,
                    priority,
                    str(due_date),
                    duration,
                    notes
                )

                st.success("✅ Task added successfully!")

                # If user chose normal Add → go back to Home
                if add_btn:
                    st.rerun()

                # If Add & Continue → clear inputs manually
                if add_continue_btn:
                    st.session_state["add_task_form"] = {}


    # ======================================================
    # ✅ COMPLETED TASKS
    elif page == "✅ Completed Tasks":
        st.title("✅ Completed Tasks")

        # Filter completed tasks
        completed = tasks[tasks["status"] == "Completed"].copy()

        if completed.empty:
            st.info("No completed tasks yet. Let’s get started 💪")
        else:
            # ---------- SEARCH & FILTER ----------
            st.markdown("### 🔍 Search & Filter")
            search_term = st.text_input("Search by Task Name or Category")
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=["High", "Medium", "Low"],
                default=["High", "Medium", "Low"]
            )

            filtered = completed[
                completed["task_name"].str.contains(search_term, case=False, na=False) |
                completed["category"].str.contains(search_term, case=False, na=False)
            ]

            filtered = filtered[filtered["priority"].isin(priority_filter)]

            # ---------- TASK LIST ----------
            st.markdown("### 📋 Completed Tasks List")
            for _, row in filtered.iterrows():
                col1, col2, col3 = st.columns([5, 1, 1])

                # Task details
                col1.write(f"**{row['task_name']}** | {row['category']} | {row['priority']} | Due: {row['due_date'].date()}")

                # Undo checkbox
                if col2.checkbox("↩️ Undo", key=f"undo_{row['id']}"):
                    update_task_status(row["id"], st.session_state.user_id, "Pending")
                    st.success(f"Task '{row['task_name']}' moved back to Pending!")
                    st.rerun()

                # Permanent Delete button
                if col3.button("🗑️ Delete", key=f"delete_{row['id']}"):
                    delete_task(row["id"], st.session_state.user_id)
                    st.success(f"Task '{row['task_name']}' deleted permanently!")
                    st.rerun()

            st.divider()

            # ---------- REFLECTION BOX ----------
            st.markdown("### ✍️ Reflection / Notes")
            reflection = st.text_area(
                "Write your thoughts or reflections on completed tasks today",
                key="reflection_box",
                height=100
            )
            if st.button("Save Reflection"):
                # For now, we can just store in session_state
                if "reflections" not in st.session_state:
                    st.session_state.reflections = []
                st.session_state.reflections.append(reflection)
                st.success("✅ Reflection saved!")
                st.rerun()



    # ======================================================
    # 📅 SCHEDULE
    # ======================================================
    elif page == "📅 Schedule":

        st.title("📅 Suggested Daily Schedule")

        schedule = generate_schedule(tasks)

        if not schedule:
            st.info("No pending tasks to schedule.")
        else:
            for day, day_tasks in schedule.items():
                st.subheader(day)
                for task in day_tasks:
                    st.write(f"- {task}")

    # ======================================================
    # 🕒 ROUTINE
    # ======================================================
    elif page == "🕒 Daily Routine (Optional)":
        routine_page()
