import streamlit as st
import pandas as pd

from db import get_supabase

from input import add_task
from tracker import update_task_status
from input import delete_task
from input import delete_all_pending_tasks, delete_all_completed_tasks, delete_all_tasks

from scheduler import generate_schedule
from routine_generator import routine_page

# ---------------- SUPABASE CLIENT ----------------
supabase = get_supabase()


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
            "🕌 Prayers",
            "➕ Add Task",
            "✅ Completed Tasks",
            "📅 Schedule",
            "🕒 Daily Routine (Optional)",
            "⚙️ Settings",
        ],
    )

    # ---------------- LOAD TASKS (SUPABASE) ----------------
    response = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    tasks = pd.DataFrame(response.data)

    # Normalize columns
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
                "reminder_time",
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

        st.session_state.focus_mode = st.toggle("🎯 Focus Mode (Top priorities only)")

        st.divider()

        pending_count = len(tasks[tasks["status"] == "Pending"])
        completed_count = len(tasks[tasks["status"] == "Completed"])

        col1, col2 = st.columns(2)
        col1.metric("🔥 Pending Tasks", pending_count)
        col2.metric("✅ Completed Tasks", completed_count)

        st.divider()

        st.markdown("### 📋 Tasks")

        pending = tasks[tasks["status"] == "Pending"].copy()

        if not pending.empty:
            priority_map = {"High": 1, "Medium": 2, "Low": 3}
            pending["rank"] = pending["priority"].map(priority_map)
            pending = pending.sort_values(by=["rank", "due_date"])

            if st.session_state.focus_mode:
                pending = pending.head(3)
                st.info("🎯 Focus Mode ON — showing top priorities only")

            for _, row in pending.iterrows():

                icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[row["priority"]]

                done = st.checkbox(
                    f"{icon} **{row['task_name']}** | {row['category']} | Due: {row['due_date']}",
                    key=f"task_{row['id']}",
                )

                if done:
                    update_task_status(row["id"], user_id, "Completed")
                    st.success("Task completed!")
                    st.rerun()

        else:
            st.success("🎉 No pending tasks!")

    # ======================================================
    # 🕌 PRAYERS
    # ======================================================
    elif page == "🕌 Prayers":

        st.title("🕌 Daily Prayers")

        today = pd.Timestamp.today().date().isoformat()

        prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for prayer in prayers:

            existing = supabase.table("prayer_logs") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("date", today) \
                .eq("prayer_name", prayer) \
                .execute()

            st.subheader(prayer)

            if existing.data:
                st.success(f"Status: {existing.data[0]['timing_status']}")
                continue

            status = st.selectbox(
                "Select status",
                ["Select", "On Time", "Late", "Missed"],
                key=f"{prayer}_status"
            )

            if st.button("Save", key=f"{prayer}_save") and status != "Select":

                supabase.table("prayer_logs").insert({
                    "user_id": user_id,
                    "date": today,
                    "prayer_name": prayer,
                    "timing_status": status,
                    "marked_at": "now()"
                }).execute()

                st.rerun()

    # ======================================================
    # ➕ ADD TASK
    # ======================================================
    elif page == "➕ Add Task":

        st.title("➕ Add New Task")

        default_categories = ["Work", "Study", "Personal", "Health", "Family", "Errands", "Other"]

        with st.form("add_task_form", clear_on_submit=True):

            task_name = st.text_input("Task Name")
            selected_category = st.selectbox("Category", default_categories)

            if selected_category == "Other":
                custom_category = st.text_input("Custom Category")
                category = custom_category.strip() if custom_category.strip() else "Other"
            else:
                category = selected_category

            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date")
            reminder_time = st.time_input("Set Reminder Time")
            notes = st.text_input("Notes / Tags")

            submit = st.form_submit_button("Add Task")

        if submit:
            if not task_name.strip():
                st.error("Task name cannot be empty.")
            else:
                add_task(
                    user_id,
                    task_name,
                    category,
                    priority,
                    str(due_date),
                    reminder_time.strftime("%H:%M"),
                    notes
                )
                st.success(f"Task '{task_name}' added!")
                st.rerun()

    # ======================================================
    # ✅ COMPLETED TASKS
    # ======================================================
    elif page == "✅ Completed Tasks":

        st.title("Completed Tasks")

        completed = tasks[tasks["status"] == "Completed"]

        if completed.empty:
            st.info("No completed tasks yet.")
        else:

            search_term = st.text_input("Search")
            priority_filter = st.multiselect(
                "Priority",
                ["High", "Medium", "Low"],
                default=["High", "Medium", "Low"]
            )

            filtered = completed[
                completed["task_name"].str.contains(search_term, case=False, na=False) &
                completed["priority"].isin(priority_filter)
            ]

            for _, row in filtered.iterrows():

                col1, col2, col3 = st.columns([5, 1, 1])

                col1.write(f"{row['task_name']} | {row['category']} | {row['priority']}")

                if col2.checkbox("Undo", key=f"undo_{row['id']}"):
                    update_task_status(row["id"], user_id, "Pending")
                    st.rerun()

                if col3.button("Delete", key=f"del_{row['id']}"):
                    delete_task(row["id"], user_id)
                    st.rerun()

    # ======================================================
    # 📅 SCHEDULE
    # ======================================================
    elif page == "📅 Schedule":

        st.title("Suggested Schedule")

        schedule = generate_schedule(tasks)

        if not schedule:
            st.info("No tasks to schedule.")
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

    # ======================================================
    # ⚙️ SETTINGS
    # ======================================================
    elif page == "⚙️ Settings":

        st.title("Settings")

        if st.button("Delete Pending Tasks"):
            delete_all_pending_tasks(user_id)
            st.rerun()

        if st.button("Delete Completed Tasks"):
            delete_all_completed_tasks(user_id)
            st.rerun()

        if st.button("Reset All Tasks"):
            delete_all_tasks(user_id)
            st.rerun()