"""
tools/task_tools.py
-------------------
Tool-functions used by the Task Agent.
Each function is a single, focused action on the 'tasks' table.
"""

from database.db import get_connection


def create_task(title: str) -> dict:
    """
    Insert a new task into the database.

    Args:
        title: Short description of what needs to be done.

    Returns:
        Dict with id, title, status of the newly created task.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, status) VALUES (?, ?)",
        (title.strip(), "pending")
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()

    return {"id": task_id, "title": title.strip(), "status": "pending"}


def get_tasks() -> list:
    """
    Retrieve every task, newest first.

    Returns:
        List of task dicts.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, title, status, created_at FROM tasks ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_task_status(task_id: int, status: str) -> dict:
    """
    Change a task's status field.

    Args:
        task_id: The numeric id of the task.
        status:  New status — 'pending', 'in_progress', or 'done'.

    Returns:
        Dict confirming the update, or an error dict.
    """
    valid = ["pending", "in_progress", "done"]
    if status not in valid:
        return {"error": f"Invalid status. Choose from: {valid}"}

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    affected = cur.rowcount
    conn.close()

    if affected == 0:
        return {"error": f"No task found with id {task_id}"}

    return {"id": task_id, "status": status, "message": "Task updated."}