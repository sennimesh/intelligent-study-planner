import json
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

from database import (
    init_db,
    add_task,
    get_tasks,
    update_progress,
    delete_task
)

from planner import generate_plan
from analytics import get_statistics, subject_analysis


st.set_page_config(
    page_title="Intelligent Study Planner",
    page_icon="📚",
    layout="wide"
)

init_db()

SETTINGS_PATH = Path("data/settings.json")


def load_settings():
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as file:
            return json.load(file)

    return {
        "student": "Student",
        "daily_study_hours": 4,
        "weekend_study_hours": 6,
        "study_goal": "Study consistently"
    }


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(exist_ok=True)

    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)


settings = load_settings()

st.sidebar.title("📚 Study Planner")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Task",
        "My Tasks",
        "Generate Plan",
        "Analytics",
        "Settings"
    ]
)

tasks = get_tasks()


if page == "Dashboard":

    st.title("Intelligent Study Planner")

    st.write(
        f"Welcome, {settings['student']}!"
    )

    stats = get_statistics(tasks)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", stats["total"])
    col2.metric("Completed", stats["completed"])
    col3.metric("Pending", stats["pending"])
    col4.metric(
        "Progress",
        f"{stats['progress']}%"
    )

    st.subheader("Overall Progress")

    st.progress(
        min(stats["progress"] / 100, 1.0)
    )

    st.subheader("Upcoming Tasks")

    if tasks:
        df = pd.DataFrame(tasks)

        st.dataframe(
            df[
                [
                    "subject",
                    "title",
                    "deadline",
                    "status"
                ]
            ],
            use_container_width=True
        )
    else:
        st.info("No tasks added yet.")


elif page == "Add Task":

    st.title("Add New Study Task")

    with st.form("add_task_form"):

        subject = st.text_input("Subject")

        title = st.text_input("Task Title")

        deadline = st.date_input(
            "Deadline",
            min_value=date.today()
        )

        priority = st.slider(
            "Priority",
            1, 5, 3
        )

        difficulty = st.slider(
            "Difficulty",
            1, 5, 3
        )

        estimated_hours = st.number_input(
            "Estimated Study Hours",
            min_value=0.5,
            value=2.0,
            step=0.5
        )

        submitted = st.form_submit_button(
            "Save Task"
        )

        if submitted:

            if not subject.strip() or not title.strip():
                st.error(
                    "Subject and title are required."
                )
            else:
                add_task(
                    subject.strip(),
                    title.strip(),
                    deadline.isoformat(),
                    priority,
                    difficulty,
                    estimated_hours
                )

                st.success(
                    "Task added successfully!"
                )


elif page == "My Tasks":

    st.title("Manage Study Tasks")

    if not tasks:
        st.info("No tasks available.")

    else:
        for task in tasks:

            with st.expander(
                f"{task['subject']} - {task['title']}"
            ):

                st.write(
                    f"Deadline: {task['deadline']}"
                )

                st.write(
                    f"Status: {task['status']}"
                )

                st.write(
                    f"Completed: {task['completed_hours']} "
                    f"/ {task['estimated_hours']} hours"
                )

                remaining = max(
                    task["estimated_hours"]
                    - task["completed_hours"],
                    0
                )

                hours = st.number_input(
                    "Add completed hours",
                    min_value=0.0,
                    max_value=float(remaining),
                    value=0.0,
                    step=0.5,
                    key=f"hours_{task['id']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Update Progress",
                        key=f"update_{task['id']}"
                    ):
                        update_progress(
                            task["id"],
                            hours
                        )
                        st.rerun()

                with col2:
                    if st.button(
                        "Delete Task",
                        key=f"delete_{task['id']}"
                    ):
                        delete_task(task["id"])
                        st.rerun()


elif page == "Generate Plan":

    st.title("Intelligent Daily Study Plan")

    default_hours = (
        settings["weekend_study_hours"]
        if date.today().weekday() >= 5
        else settings["daily_study_hours"]
    )

    available_hours = st.number_input(
        "Available Study Hours",
        min_value=0.5,
        value=float(default_hours),
        step=0.5
    )

    if st.button("Generate Study Plan"):

        plan = generate_plan(
            tasks,
            available_hours
        )

        if plan.empty:
            st.warning(
                "No pending tasks to schedule."
            )

        else:
            st.success(
                "Study plan generated!"
            )

            st.dataframe(
                plan,
                use_container_width=True
            )

            st.metric(
                "Total Scheduled Hours",
                round(plan["Study Hours"].sum(), 2)
            )

            csv = plan.to_csv(index=False)

            st.download_button(
                "Download Plan CSV",
                csv,
                "study_plan.csv",
                "text/csv"
            )


elif page == "Analytics":

    st.title("Study Analytics")

    analysis = subject_analysis(tasks)

    if analysis.empty:
        st.info("No study data available.")

    else:
        st.subheader("Hours by Subject")

        st.bar_chart(
            analysis.set_index("subject")[
                [
                    "estimated_hours",
                    "completed_hours"
                ]
            ]
        )

        st.subheader("Detailed Statistics")

        st.dataframe(
            analysis,
            use_container_width=True
        )


elif page == "Settings":

    st.title("Planner Settings")

    student = st.text_input(
        "Student Name",
        value=settings["student"]
    )

    daily_hours = st.number_input(
        "Weekday Study Hours",
        min_value=1,
        max_value=24,
        value=settings["daily_study_hours"]
    )

    weekend_hours = st.number_input(
        "Weekend Study Hours",
        min_value=1,
        max_value=24,
        value=settings["weekend_study_hours"]
    )

    goal = st.text_area(
        "Study Goal",
        value=settings["study_goal"]
    )

    if st.button("Save Settings"):

        settings = {
            "student": student,
            "daily_study_hours": daily_hours,
            "weekend_study_hours": weekend_hours,
            "study_goal": goal
        }

        save_settings(settings)

        st.success("Settings saved!")

    st.subheader("Backup Tasks")

    st.download_button(
        "Export Tasks as JSON",
        data=json.dumps(tasks, indent=4),
        file_name="study_tasks.json",
        mime="application/json"
    )