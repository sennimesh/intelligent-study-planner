import pandas as pd


get_statistics(tasks):
    if not tasks:
        return {
            "total": 0,
            "completed": 0,
            "pending": 0,
            "progress": 0
        }

    df = pd.DataFrame(tasks)

    total = len(df)

    completed = len(
        df[df["status"] == "Completed"]
    )

    pending = total - completed

    estimated = df["estimated_hours"].sum()
    studied = df["completed_hours"].sum()

    progress = (
        (studied / estimated) * 100
        if estimated > 0 else 0
    )

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "progress": round(progress, 1)
    }


def subject_analysis(tasks):
    if not tasks:
        return pd.DataFrame()

    df = pd.DataFrame(tasks)

    return df.groupby("subject", as_index=False)[
        ["estimated_hours", "completed_hours"]
    ].sum()