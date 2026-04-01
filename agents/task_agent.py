"""Task Agent - handles task creation, listing, and updates."""
from tools.task_tools import create_task, get_tasks, update_task_status

class TaskAgent:
    def __init__(self):
        self.name = "TaskAgent"

    def handle(self, action: str, data: dict) -> dict:
        if action == "create":
            title = data.get("title", "").strip()
            if not title:
                return self._error("Task title is required.")
            result = create_task(title)
            return {"agent": self.name, "action": "create", "status": "success",
                    "message": f"✅ Task created: '{result['title']}'", "data": result}

        elif action == "list":
            tasks = get_tasks()
            if not tasks:
                return {"agent": self.name, "action": "list", "status": "success",
                        "message": "📋 No tasks found. Start by adding one!", "data": []}
            return {"agent": self.name, "action": "list", "status": "success",
                    "message": f"📋 Found {len(tasks)} task(s).", "data": tasks}

        elif action == "update":
            task_id = data.get("id")
            status = data.get("status", "done")
            if not task_id:
                return self._error("Task ID is required for update.")
            result = update_task_status(int(task_id), status)
            if "error" in result:
                return self._error(result["error"])
            return {"agent": self.name, "action": "update", "status": "success",
                    "message": f"✅ Task {task_id} marked as '{status}'.", "data": result}
        else:
            return self._error(f"Unknown action '{action}' for TaskAgent.")

    def _error(self, message: str) -> dict:
        return {"agent": self.name, "status": "error", "message": f"❌ {message}", "data": None}