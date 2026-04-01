"""Note Agent - handles saving, listing, and deleting notes."""
from tools.note_tools import save_note, get_notes, delete_note

class NoteAgent:
    def __init__(self):
        self.name = "NoteAgent"

    def handle(self, action: str, data: dict) -> dict:
        if action == "save":
            content = data.get("content", "").strip()
            if not content:
                return self._error("Note content is required.")
            result = save_note(content)
            preview = result['content'][:60] + "..." if len(result['content']) > 60 else result['content']
            return {"agent": self.name, "action": "save", "status": "success",
                    "message": f"📝 Note saved: '{preview}'", "data": result}

        elif action == "list":
            notes = get_notes()
            if not notes:
                return {"agent": self.name, "action": "list", "status": "success",
                        "message": "📓 No notes found. Start by saving one!", "data": []}
            return {"agent": self.name, "action": "list", "status": "success",
                    "message": f"📓 Found {len(notes)} note(s).", "data": notes}

        elif action == "delete":
            note_id = data.get("id")
            if not note_id:
                return self._error("Note ID is required for deletion.")
            result = delete_note(int(note_id))
            if "error" in result:
                return self._error(result["error"])
            return {"agent": self.name, "action": "delete", "status": "success",
                    "message": f"🗑️ Note {note_id} deleted.", "data": result}
        else:
            return self._error(f"Unknown action '{action}' for NoteAgent.")

    def _error(self, message: str) -> dict:
        return {"agent": self.name, "status": "error", "message": f"❌ {message}", "data": None}