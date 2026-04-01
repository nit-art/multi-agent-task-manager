"""
main.py
--------
FastAPI application — the API layer for the multi-agent system.

Endpoints:
  GET  /          → Health check
  POST /query     → Send a natural language query to the Root Agent
  GET  /tasks     → Directly list all tasks
  GET  /notes     → Directly list all notes

Run locally:
  uvicorn main:app --reload --port 8080
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from database.db import init_db
from agents.root_agent import RootAgent


# ─── LIFESPAN: runs on startup ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the server starts."""
    init_db()
    yield


# ─── APP SETUP ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Agent Task & Note Manager",
    description=(
        "A hackathon-ready multi-agent AI system that manages tasks and notes "
        "using a Root Agent coordinating Task and Note sub-agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Single Root Agent instance shared across requests
root_agent = RootAgent()


# ─── REQUEST / RESPONSE MODELS ────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""
    query: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Add task and save note revise DSA"
            }
        }


class QueryResponse(BaseModel):
    """Standard response from the Root Agent."""
    agent: str
    intent: str
    status: str
    message: str
    results: list


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns system status and available agents.
    """
    return {
        "status": "ok",
        "system": "Multi-Agent Task & Note Manager",
        "version": "1.0.0",
        "agents": ["RootAgent", "TaskAgent", "NoteAgent"],
        "message": "🤖 System is running. POST to /query to get started."
    }


@app.post("/query", response_model=QueryResponse, tags=["Agent"])
def query(request: QueryRequest):
    """
    Main endpoint — sends a natural language query to the Root Agent.

    The Root Agent will:
    1. Analyze the intent
    2. Route to the correct sub-agent(s)
    3. Return structured results

    **Example queries:**
    - `"Add task study DSA"`
    - `"Save note pointers are tricky"`
    - `"Add task and save note revise DSA"` ← multi-step!
    - `"Show my tasks"`
    - `"List notes"`
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    response = root_agent.process(request.query)
    return response


@app.get("/tasks", tags=["Direct Access"])
def list_tasks():
    """
    Shortcut endpoint to list all tasks directly
    (without going through the natural language interface).
    """
    from tools.task_tools import get_tasks
    tasks = get_tasks()
    return {
        "count": len(tasks),
        "tasks": tasks
    }


@app.get("/notes", tags=["Direct Access"])
def list_notes():
    """
    Shortcut endpoint to list all notes directly
    (without going through the natural language interface).
    """
    from tools.note_tools import get_notes
    notes = get_notes()
    return {
        "count": len(notes),
        "notes": notes
    }