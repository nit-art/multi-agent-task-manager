"""
agents/root_agent.py
---------------------
The Root Agent is the BRAIN of the system.
It receives the raw user query, figures out the intent,
and routes the request to the correct sub-agent(s).

This is where multi-agent coordination happens!

Supported intents:
  - add task / create task
  - show tasks / list tasks / get tasks
  - save note / add note
  - show notes / list notes / get notes
  - multi-step: "add task AND save note"
  - update task (mark done)
"""

import re
from agents.task_agent import TaskAgent
from agents.note_agent import NoteAgent


class RootAgent:
    """
    Main controller agent.
    Parses user queries and delegates to sub-agents.
    """

    def __init__(self):
        self.name = "RootAgent"
        # Initialize sub-agents
        self.task_agent = TaskAgent()
        self.note_agent = NoteAgent()

    def process(self, query: str) -> dict:
        """
        Main entry point. Accepts a plain English query.
        Returns a structured response with results from sub-agents.

        Examples:
          "Add task study DSA"
          "Save note revise pointers"
          "Add task and save note revise DSA"
          "Show my tasks"
          "List notes"
        """
        query = query.strip()
        if not query:
            return self._error("Query cannot be empty.")

        query_lower = query.lower()

        # ─── DETECT MULTI-STEP INTENT ─────────────────────────────────────────
        # Check if the user wants BOTH a task AND a note in one query
        # e.g., "add task and save note revise DSA"
        has_task_intent = self._has_task_intent(query_lower)
        has_note_intent = self._has_note_intent(query_lower)

        if has_task_intent and has_note_intent:
            return self._handle_multistep(query, query_lower)

        # ─── SINGLE INTENT ROUTING ────────────────────────────────────────────

        # --- Task: Create ---
        if self._is_create_task(query_lower):
            content = self._extract_content(query, task_keywords + task_action_keywords)
            return self._wrap([
                self.task_agent.handle("create", {"title": content})
            ], "Task creation")

        # --- Task: List ---
        if self._is_list_tasks(query_lower):
            return self._wrap([
                self.task_agent.handle("list", {})
            ], "Task listing")

        # --- Task: Update/Complete ---
        if self._is_update_task(query_lower):
            task_id = self._extract_id(query_lower)
            return self._wrap([
                self.task_agent.handle("update", {"id": task_id, "status": "done"})
            ], "Task update")

        # --- Note: Save ---
        if self._is_save_note(query_lower):
            content = self._extract_content(query, note_keywords + note_action_keywords)
            return self._wrap([
                self.note_agent.handle("save", {"content": content})
            ], "Note saving")

        # --- Note: List ---
        if self._is_list_notes(query_lower):
            return self._wrap([
                self.note_agent.handle("list", {})
            ], "Note listing")

        # ─── FALLBACK ────────────────────────────────────────────────────────
        return {
            "agent": self.name,
            "intent": "unknown",
            "status": "error",
            "message": (
                "🤔 I didn't understand that. Try:\n"
                "  • 'Add task <title>'\n"
                "  • 'Show tasks'\n"
                "  • 'Save note <content>'\n"
                "  • 'Show notes'\n"
                "  • 'Add task and save note <text>'"
            ),
            "results": []
        }

    # ─── MULTI-STEP HANDLER ───────────────────────────────────────────────────

    def _handle_multistep(self, query: str, query_lower: str) -> dict:
        """
        Handle queries that require BOTH a task AND a note.
        Splits the combined content and delegates to both sub-agents.

        Example: "add task and save note revise DSA"
          → task: "revise DSA"
          → note: "revise DSA"
        """
        # Extract the meaningful content after all keywords
        all_keywords = task_keywords + task_action_keywords + note_keywords + note_action_keywords + ["and"]
        content = self._extract_content(query, all_keywords)

        results = []

        # Call Task Agent
        task_result = self.task_agent.handle("create", {"title": content})
        results.append(task_result)

        # Call Note Agent
        note_result = self.note_agent.handle("save", {"content": content})
        results.append(note_result)

        return {
            "agent": self.name,
            "intent": "multi-step (task + note)",
            "status": "success",
            "message": f"🔀 Multi-step workflow completed for: '{content}'",
            "results": results
        }

    # ─── INTENT DETECTION HELPERS ────────────────────────────────────────────

    def _has_task_intent(self, q: str) -> bool:
        return any(kw in q for kw in task_action_keywords)

    def _has_note_intent(self, q: str) -> bool:
        return any(kw in q for kw in note_action_keywords)

    def _is_create_task(self, q: str) -> bool:
        return any(kw in q for kw in ["add task", "create task", "new task"])

    def _is_list_tasks(self, q: str) -> bool:
        return any(kw in q for kw in ["show task", "list task", "get task", "my task", "show my task", "all task"])

    def _is_update_task(self, q: str) -> bool:
        return any(kw in q for kw in ["complete task", "done task", "finish task", "mark task", "update task"])

    def _is_save_note(self, q: str) -> bool:
        return any(kw in q for kw in ["save note", "add note", "create note", "new note", "take note"])

    def _is_list_notes(self, q: str) -> bool:
        return any(kw in q for kw in ["show note", "list note", "get note", "my note", "all note"])

    # ─── CONTENT EXTRACTION HELPERS ──────────────────────────────────────────

    def _extract_content(self, query: str, keywords: list) -> str:
        """
        Strip known command keywords from the query to get the
        meaningful content (e.g., the task title or note text).
        """
        text = query.strip()
        # Sort keywords longest-first to avoid partial matches
        for kw in sorted(keywords, key=len, reverse=True):
            # Case-insensitive removal
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            text = pattern.sub("", text)
        return text.strip(" .,!?")

    def _extract_id(self, query: str) -> int | None:
        """Extract the first number from the query (used as an ID)."""
        match = re.search(r'\d+', query)
        return int(match.group()) if match else None

    # ─── RESPONSE WRAPPER ────────────────────────────────────────────────────

    def _wrap(self, results: list, intent: str) -> dict:
        """Wrap single-agent results in a standard top-level response."""
        all_ok = all(r.get("status") == "success" for r in results)
        return {
            "agent": self.name,
            "intent": intent,
            "status": "success" if all_ok else "partial",
            "message": results[0].get("message", "") if results else "",
            "results": results
        }

    def _error(self, message: str) -> dict:
        return {
            "agent": self.name,
            "intent": "error",
            "status": "error",
            "message": f"❌ {message}",
            "results": []
        }


# ─── KEYWORD LISTS ────────────────────────────────────────────────────────────
# These are used both for intent detection and content extraction

task_action_keywords = ["add task", "create task", "new task",
                        "show task", "list task", "get task",
                        "complete task", "done task", "finish task",
                        "mark task", "update task", "my task"]

note_action_keywords = ["save note", "add note", "create note", "new note",
                        "take note", "show note", "list note", "get note",
                        "my note"]

task_keywords = ["task"]
note_keywords = ["note"]