# Smart Task Analyzer

A mini task management application that **intelligently scores and prioritizes tasks** using multiple factors such as urgency, importance, effort, and dependencies. The goal is to help users decide **what to work on first** with clear, explainable reasoning.

This project was built as a technical assignment focusing on **algorithm design, clean backend architecture, edge-case handling, testing, and a functional frontend UI**.

---

## Features

### Core Features

- Intelligent task priority scoring
- Multiple prioritization strategies:
  - **Smart Balance** (default – balanced between urgency, importance, effort, dependencies)
  - **Fastest Wins** (prioritize low-effort, quick wins)
  - **High Impact** (maximize importance & blocking power)
  - **Deadline Driven** (prioritize tasks by due date)
- Human-readable explanations for each task’s score
- Circular dependency detection (flags tasks that are part of cycles)
- REST API built with Django + Django REST Framework
- Frontend using HTML, CSS, and Vanilla JavaScript
- Unit tests for the scoring algorithm

### API Endpoints

- `POST /api/tasks/analyze/`  
  Accepts a JSON array of tasks and returns them sorted by priority score, with explanations.

- `GET /api/tasks/suggest/`  
  Uses tasks stored in the database and returns the **top 3 tasks** the user should work on today, with scores and explanations.

---

## 🛠 Tech Stack

### Backend

- Python 3.8+
- Django 4.2+
- Django REST Framework
- django-cors-headers
- SQLite (default Django DB for local development)

### Frontend

- HTML
- CSS
- JavaScript (Fetch API, no frameworks)

---

## Project Structure

```text
task-analyser/
├── backend/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── requirements.txt
│   ├── task_analyzer/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── tasks/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── serializers.py
│       ├── scoring.py
│       ├── urls.py
│       └── tests.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```
