import pandas as pd

CSV_FILE = "data/user_tasks.csv"

def update_task_status(task_name, completed):
    tasks = pd.read_csv(CSV_FILE)
    tasks.loc[tasks["Task Name"] == task_name, "Status"] = (
        "Completed" if completed else "Pending"
    )
    tasks.to_csv(CSV_FILE, index=False)
