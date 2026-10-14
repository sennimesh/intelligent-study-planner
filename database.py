import sqlite3
from pathlib import Path

DB_PATH = Path("data/study_planner.db")


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                deadline TEXT NOT NULL,
                priority INTEGER NOT NULL,
                difficulty INTEGER NOT NULL,
                estimated_hours REAL NOT NULL,
                completed_hours REAL DEFAULT 0,
                status TEXT DEFAULT 'Pending'
            )
        """)


def add_task(subject, title, deadline, priority,
             difficulty, estimated_hours):

    with connect() as conn:
        conn.execute("""
            INSERT INTO tasks
            (subject, title, deadline, priority,
             difficulty, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            subject,
            title,
            deadline,
            priority,
            difficulty,
            estimated_hours
        ))


def get_tasks():
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY deadline"
        ).fetchall()

    return [dict(row) for row in rows]


def update_progress(task_id, hours):
    with connect() as conn:
        row = conn.execute("""
            SELECT estimated_hours, completed_hours
            FROM tasks WHERE id = ?
        """, (task_id,)).fetchone()

        if row is None:
            return

        estimated, completed = row
        new_hours = min(estimated, completed + hours)

        status = (
            "Completed"
            if new_hours >= estimated
            else "In Progress"
        )

        conn.execute("""
            UPDATE tasks
            SET completed_hours = ?, status = ?
            WHERE id = ?
        """, (new_hours, status, task_id))


def delete_task(task_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )