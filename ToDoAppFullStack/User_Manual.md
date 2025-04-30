# ToDoAppFullStack User Manual

## Overview

ToDoAppFullStack is a full-stack to-do application built with a Streamlit frontend and a FastAPI backend, using SQLite for the database. It features user authentication (signup/login) and task management (create, read, update, delete).

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.7+
- pip (Python package installer)

## Setup

1.  **Create a project directory:**
    ```bash
    mkdir ToDoAppFullStack
    cd ToDoAppFullStack
    ```

2.  **Create subdirectories:**
    ```bash
    mkdir src
    mkdir src\backend
    mkdir src\frontend
    mkdir data
    ```

3.  **Create virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On macOS and Linux
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the FastAPI backend:**
    ```bash
    uvicorn src.backend.main:app --reload
    ```
    This command starts the FastAPI server, which will listen on `http://localhost:8000` by default.

2.  **Start the Streamlit frontend:**
    ```bash
    streamlit run src/frontend/main.py
    ```
    This command starts the Streamlit application, which will open in your web browser (usually on `http://localhost:8501`).

## Using the Application

1.  **Signup/Login:**
    - If you don't have an account, click on "Signup" in the sidebar to create a new account.
    - If you already have an account, click on "Login" and enter your username and password.

2.  **Task Management:**
    - After logging in, you can create new tasks by clicking on "Create Task" in the sidebar.
    - You can view your existing tasks by clicking on "Tasks" in the sidebar.
    - On the "Tasks" page, you can:
        - Edit a task by clicking the "Edit" button next to the task.
        - Delete a task by clicking the "Delete" button.
        - Mark a task as complete by clicking the "Mark Complete" button.

## Project Structure

```
ToDoAppFullStack/
├── data/
│   └── todo.db          # SQLite database file
├── src/
│   ├── backend/
│   │   ├── database.py    # Database configuration and models
│   │   ├── models.py        # Pydantic models for data validation
│   │   ├── auth.py          # Authentication logic
│   │   ├── main.py          # FastAPI application
│   │   └── utils.py         # Utility functions
│   ├── frontend/
│   │   └── main.py          # Streamlit application
├── requirements.txt     # Python dependencies
├── package.json         # Project metadata and scripts
└── User_Manual.md        # This user manual
```

## Backend (FastAPI)

The backend is built using FastAPI and provides the following API endpoints:

-   `POST /token`: Login and obtain an access token.
-   `POST /users`: Create a new user account.
-   `GET /users/me`: Get the current user's information.
-   `POST /items`: Create a new task.
-   `GET /items`: Get all tasks for the current user.
-   `GET /items/{item_id}`: Get a specific task by ID.
-   `PATCH /items/{item_id}`: Update a task.
-   `DELETE /items/{item_id}`: Delete a task.

## Frontend (Streamlit)

The frontend is built using Streamlit and provides a user-friendly interface for interacting with the backend API.

## Database (SQLite)

The application uses SQLite as the database to store user accounts and tasks. The database schema is defined in `src/backend/database.py`.

## Notes

-   Remember to change the `SECRET_KEY` in `src/backend/auth.py` to a strong, random value in a production environment.
-   This is a basic implementation and can be extended with additional features such as task prioritization, due dates, and more advanced filtering and searching.
