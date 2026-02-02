from db import get_connection


def update_task_status(task_id, user_id, new_status):
    """
    Update task status for a specific task belonging to a specific user.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ? AND user_id = ?
        """,
        (new_status, task_id, user_id)
    )

    conn.commit()
    conn.close()
