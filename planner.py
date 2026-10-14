import pandas as pd
from datetime import date


def calculate_score(task):
    today = date.today()

    deadline = date.fromisoformat(task["deadline"])

    days_left = max((deadline - today).days, 0)

    urgency = 10 / (days_left + 1)

    priority = task["priority"] * 3

    difficulty = task["difficulty"] * 2

    remaining = max(
        task["estimated_hours"] - task["completed_hours"],
        0
    )

    return urgency + priority + difficulty + remaining


def generate_plan(tasks, available_hours):
    if not tasks or available_hours <= 0:
        return pd.DataFrame()

    pending = [
        task.copy()
        for task in tasks
        if task["status"] != "Completed"
    ]

    for task in pending:
        task["score"] = calculate_score(task)

    pending.sort(
        key=lambda task: task["score"],
        reverse=True
    )

    plan = []
    hours_left = available_hours

    for task in pending:
        remaining = max(
            task["estimated_hours"] - task["completed_hours"],
            0
        )

        allocated = min(remaining, hours_left)

        if allocated <= 0:
            continue

        plan.append({
            "Task ID": task["id"],
            "Subject": task["subject"],
            "Task": task["title"],
            "Study Hours": round(allocated, 2),
            "Deadline": task["deadline"],
            "Score": round(task["score"], 2)
        })

        hours_left -= allocated

        if hours_left <= 0:
            break

    return pd.DataFrame(plan)