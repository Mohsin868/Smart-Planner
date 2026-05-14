import pandas as pd
from db import get_supabase

supabase = get_supabase()


# ---------------- LOAD TASKS ----------------
def load_tasks(user_id):
    response = supabase.table("tasks") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    return pd.DataFrame(response.data)


# ---------------- ADD TASK ----------------
def add_task(user_id, name, category, priority, due_date, reminder_time, notes):

    supabase.table("tasks").insert({
        "user_id": user_id,
        "task_name": name,
        "category": category,
        "priority": priority,
        "due_date": due_date,
        "reminder_time": reminder_time,
        "notes": notes,
        "status": "Pending"
    }).execute()


# ---------------- DELETE TASK ----------------
def delete_task(task_id, user_id):

    supabase.table("tasks") \
        .delete() \
        .eq("id", task_id) \
        .eq("user_id", user_id) \
        .execute()


# ---------------- UPDATE STATUS ----------------
def update_task_status(task_id, user_id, new_status):

    supabase.table("tasks") \
        .update({"status": new_status}) \
        .eq("id", task_id) \
        .eq("user_id", user_id) \
        .execute()


# ---------------- DELETE ALL PENDING ----------------
def delete_all_pending_tasks(user_id):

    supabase.table("tasks") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("status", "Pending") \
        .execute()


# ---------------- DELETE ALL COMPLETED ----------------
def delete_all_completed_tasks(user_id):

    supabase.table("tasks") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("status", "Completed") \
        .execute()


# ---------------- DELETE ALL TASKS ----------------
def delete_all_tasks(user_id):

    supabase.table("tasks") \
        .delete() \
        .eq("user_id", user_id) \
        .execute()