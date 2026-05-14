from db import get_supabase

supabase = get_supabase()


def update_task_status(task_id, user_id, new_status):

    supabase.table("tasks") \
        .update({"status": new_status}) \
        .eq("id", task_id) \
        .eq("user_id", user_id) \
        .execute()