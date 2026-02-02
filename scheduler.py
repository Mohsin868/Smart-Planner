from datetime import datetime, timedelta


def generate_schedule(tasks):
    """
    Generate a simple day-wise schedule based on pending tasks,
    priority, and due dates.
    """

    if tasks.empty:
        return {}

    # Ensure we only work with pending tasks
    tasks = tasks[tasks["status"] == "Pending"].copy()

    if tasks.empty:
        return {}

    # Priority ranking
    priority_map = {"High": 1, "Medium": 2, "Low": 3}
    tasks["rank"] = tasks["priority"].map(priority_map)

    # Sort by priority then due date
    tasks = tasks.sort_values(by=["rank", "due_date"])

    schedule = {}
    today = datetime.today().date()
    daily_hours_limit = 5
    remaining_hours = daily_hours_limit
    current_day = today

    for _, task in tasks.iterrows():
        hours_needed = task["duration"]

        while hours_needed > 0:
            if current_day not in schedule:
                schedule[current_day] = []

            allocated = min(hours_needed, remaining_hours)
            schedule[current_day].append(
                f"{task['task_name']} ({allocated}h)"
            )

            hours_needed -= allocated
            remaining_hours -= allocated

            if remaining_hours == 0:
                current_day += timedelta(days=1)
                remaining_hours = daily_hours_limit

    return schedule
