# Multi-Agent Task & Note Manager

## 🚀 Overview

This project is a multi-agent AI system built using FastAPI and Python. It demonstrates coordination between multiple agents to manage tasks and notes.

## 🧠 Architecture

- Root Agent (controller)
- Task Agent (task management)
- Note Agent (note management)
- SQLite database for storage

## ⚙️ Features

- Add tasks
- Save notes
- Multi-step workflows (task + note)
- Retrieve stored data
- API-based interaction

## 🔄 Workflow

User → Root Agent → Sub Agents → Tools → Database → Response

## 🧪 Example Queries

- Add task study DSA
- Save note revise pointers
- Add task and save note revise trees
- Show tasks
- Show notes

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8080
```
