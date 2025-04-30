# User Manual for SmartTaskManager

## Introduction

SmartTaskManager is a to-do list application that helps you manage your tasks effectively. It allows you to add, manage, track, prioritize, categorize, and filter tasks.

## Features

*   **Add Tasks:** Add new tasks with titles, descriptions, due dates, priorities, and tags.
*   **View Tasks:** View a list of all tasks with their details.
*   **Mark Tasks as Complete:** Mark tasks as complete or incomplete.
*   **Edit Tasks:** Edit existing tasks to update their details.
*   **Delete Tasks:** Delete tasks that are no longer needed.
*   **Filter Tasks:** Filter tasks by status, priority, or tags.
*   **Search Tasks:** Search tasks by title or description.
*   **Sort Tasks:** Sort tasks by due date and priority.
*   **Subtasks:** Add subtasks to tasks to break them down into smaller steps.

## Installation

1.  Make sure you have Python installed (version 3.7 or higher).
2.  Clone the repository to your local machine.
3.  Navigate to the project directory.
4.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On macOS and Linux
    ```
5.  Install the required dependencies:
    ```bash
    pip install -r src/requirements.txt
    ```

## Usage

1.  Start the FastAPI backend:
    ```bash
    python src/backend/main.py
    ```
2.  Start the Streamlit frontend:
    ```bash
    streamlit run src/frontend/app.py
    ```
3.  Open the Streamlit app in your browser (usually at `http://localhost:8501`).

## Configuration

*   **Database URL:** The database URL is configured in the `.env` file. You can change the database URL to use a different database.

## Contributing

If you would like to contribute to SmartTaskManager, please fork the repository and submit a pull request.
