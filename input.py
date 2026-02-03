import pandas as pd
from ddb import get_connection

def load_tasks(user_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM tasks WHERE user_id = ?",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df


def add_task(user_id, name, category, priority, due_date, reminder_time, notes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks
        (user_id, task_name, category, priority, due_date, reminder_time, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (user_id, name, category, priority, due_date, reminder_time, notes))

    conn.commit()
    conn.close()

def delete_task(task_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )

    conn.commit()
    conn.close()

def update_task_status(task_id, user_id, new_status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?",
        (new_status, task_id, user_id)
    )

    conn.commit()
    conn.close()

def delete_all_pending_tasks(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE user_id = ? AND status = 'Pending'",
        (user_id,)
    )

    conn.commit()
    conn.close()

def delete_all_completed_tasks(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE user_id = ? AND status = 'Completed'",
        (user_id,)
    )

    conn.commit()
    conn.close()

def delete_all_tasks(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()