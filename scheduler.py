import pandas as pd
from datetime import datetime, timedelta

def generate_schedule(tasks, daily_limit=5):
    priority_map = {"High": 3, "Medium": 2, "Low": 1}
    
    tasks = tasks[tasks["Status"] == "Pending"].copy()
    tasks["PriorityScore"] = tasks["Priority"].map(priority_map)
    tasks["Due Date"] = pd.to_datetime(tasks["Due Date"])
    
    tasks = tasks.sort_values(
        by=["PriorityScore", "Due Date"],
        ascending=[False, True]
    )

    schedule = {}
    today = datetime.today().date()
    remaining_hours = daily_limit
    current_day = today

    for _, task in tasks.iterrows():
        hours = task["Duration"]
        while hours > 0:
            if current_day not in schedule:
                schedule[current_day] = []

            available = min(hours, remaining_hours)
            schedule[current_day].append(
                f"{task['Task Name']} ({available}h)"
            )

            hours -= available
            remaining_hours -= available

            if remaining_hours == 0:
                current_day += timedelta(days=1)
                remaining_hours = daily_limit

    return schedule
