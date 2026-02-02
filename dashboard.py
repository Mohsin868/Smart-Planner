import streamlit as st
import pandas as pd


import os
import openai

from input import load_tasks, add_task
from tracker import update_task_status
from input import delete_task
from input import delete_all_pending_tasks, delete_all_completed_tasks, delete_all_tasks

from scheduler import generate_schedule
from routine_generator import routine_page



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
            "🤖 Smart Assistant",
            "➕ Add Task",
            "✅ Completed Tasks",
            "📅 Schedule",
            "🕒 Daily Routine (Optional)",
            "⚙️ Settings",
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

    # =====================================================
    # 🤖 SMART ASSISTANT
    # =====================================================
    elif page == "🤖 Smart Assistant":
        st.title("🤖 Smart Assistant")

        query = st.text_input("Ask your assistant:", placeholder="e.g., What are my tasks today?")

    if st.button("Send"):
        tasks_df = load_tasks(user_id)
        tasks_today = tasks_df[tasks_df['due_date'] == pd.Timestamp.today().strftime("%Y-%m-%d")]

        tasks_list = [
            f"{row['task_name']} | {row['priority']} | {row['reminder_time']} | {row['category']}"
            for _, row in tasks_today.iterrows()
        ]
        tasks_text = "\n".join(tasks_list) if tasks_list else "No tasks for today."

        prompt = f"""
        You are a helpful assistant for a productivity app. 
        The user has the following tasks for today:
        {tasks_text}

        User question: {query}

        Answer concisely and helpfully.
        """
        try:
            import openai
        except ModuleNotFoundError:
            openai = None
        st.warning("Smart Agent is unavailable. Install 'openai' in requirements.txt.")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            answer = response['choices'][0]['message']['content']
        except Exception as e:
            answer = f"Error: {str(e)}"

        st.markdown(f"**Assistant:** {answer}")

    # ======================================================
    # ➕ ADD TASK
    # ======================================================
    elif page == "➕ Add Task":

        st.title("➕ Add New Task")

        default_categories = [
            "Work", "Study", "Personal", "Health",
            "Family", "Errands", "Other"
        ]

        with st.form("add_task_form", clear_on_submit=True):

            task_name = st.text_input("Task Name")

            selected_category = st.selectbox(
                "Category",
                default_categories
            )

            if selected_category == "Other":
                custom_category = st.text_input("Custom Category")
                category = custom_category.strip() if custom_category.strip() else "Other"
            else:
                category = selected_category

            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date")

            # Instead of duration
            reminder_time = st.time_input(
                "Set Reminder Time",
                value=pd.to_datetime("09:00").time()
            )

            


            notes = st.text_input("Notes / Tags")

            submit = st.form_submit_button("✅ Add Task")

        if submit:
            if not task_name.strip():
                st.error("❌ Task name cannot be empty.")
            else:
                add_task(
                    user_id,
                    task_name,
                    category,
                    priority,
                    str(due_date),
                    reminder_time.strftime("%H:%M"), # Format time as HH:MM,
                    notes
                )
                # Set success flag
                st.session_state.task_added_msg = f"✅ Task '{task_name}' added successfully!"

                # Redirect to Home
                st.session_state.page = "🏠 Home"
                st.rerun()



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

    # ======================================================
    # Settings
    # ======================================================
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")

        st.markdown("### 🧹 Clear Tasks")

        if st.button("Delete All Pending Tasks"):
            if st.confirm("Are you sure you want to delete ALL pending tasks?"):
                delete_all_pending_tasks(user_id)
                st.success("✅ All pending tasks deleted.")
                st.rerun()
        if st.button("Delete All Completed Tasks"):
            if st.confirm("Are you sure you want to delete ALL completed tasks?"):
                delete_all_completed_tasks(user_id)
                st.success("✅ All completed tasks deleted.")
                st.rerun()
        if st.button("Delete All Tasks / Reset Account"):
            if st.confirm("Are you sure you want to delete ALL tasks? This cannot be undone."):
                delete_all_tasks(user_id)
                st.success("✅ All tasks deleted. Account reset.")
                st.rerun()

