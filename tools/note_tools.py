"""
tools/note_tools.py
-------------------
Tool-functions used by the Note Agent.
"""

from database.db import get_connection


def save_note(content: str) -> dict:
    """
    Insert a new note into the database.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (content) VALUES (?)",
        (content.strip(),)
    )
    conn.commit()
    note_id = cur.lastrowid
    conn.close()

    return {"id": note_id, "content": content.strip()}


def get_notes() -> list:
    """
    Retrieve all notes, newest first.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content, created_at FROM notes ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_note(note_id: int) -> dict:
    """
    Delete a note by its ID.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()

    if affected == 0:
        return {"error": f"No note found with id {note_id}"}

    return {"id": note_id, "message": "Note deleted."}