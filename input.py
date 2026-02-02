import pandas as pd
from db import get_connection

def load_tasks(user_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM tasks WHERE user_id = ?",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df


def add_task(user_id, name, category, priority, due_date, duration, notes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks
        (user_id, task_name, category, priority, due_date, duration, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (user_id, name, category, priority, due_date, duration, notes))

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