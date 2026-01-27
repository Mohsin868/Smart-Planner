import pandas as pd

CSV_FILE = "data/user_tasks.csv"

def load_tasks():
    return pd.read_csv(CSV_FILE)

def add_task(task_name, category, priority, due_date, duration, notes):
    tasks = load_tasks()
    
    new_task = {
        "Task Name": task_name,
        "Category": category,
        "Priority": priority,
        "Due Date": due_date,
        "Duration": duration,
        "Status": "Pending",
        "Notes": notes
    }
    
    tasks = pd.concat([tasks, pd.DataFrame([new_task])], ignore_index=True)
    tasks.to_csv(CSV_FILE, index=False)
