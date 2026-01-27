import pandas as pd
import os

CSV_FILE = "data/tasks.csv"

COLUMNS = [
    "Task Name",
    "Category",
    "Priority",
    "Due Date",
    "Duration",
    "Notes",
    "Status"
]

def load_tasks():
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    # Create CSV if it does not exist
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

    return pd.read_csv(CSV_FILE)


def add_task(task_name, category, priority, due_date, duration, notes):
    df = load_tasks()

    new_task = {
        "Task Name": task_name,
        "Category": category,
        "Priority": priority,
        "Due Date": due_date,
        "Duration": duration,
        "Notes": notes,
        "Status": "Pending"
    }

    df.loc[len(df)] = new_task
    df.to_csv(CSV_FILE, index=False)
