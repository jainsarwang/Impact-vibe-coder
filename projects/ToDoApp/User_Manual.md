# ToDoApp User Manual

## Overview

ToDoApp is a simple to-do list application that allows users to manage their tasks efficiently. It consists of a FastAPI backend and a Streamlit frontend, with an SQLite database for storing to-do items.

## Features

*   **Add To-Do Items:** Create new to-do items with titles, descriptions, due dates, and priorities.
*   **View To-Do Items:** Display all to-do items in a table format.
*   **Mark Complete/Delete:** Mark to-do items as complete or delete them.
*   **Filter To-Do Items:** Filter to-do items by priority and due date.
*   **Show Completed To-Do Items:** Display only the completed to-do items.

## Prerequisites

Before running the application, ensure you have the following installed:

*   Python 3.6 or higher
*   pip (Python package installer)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd ToDoApp
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On macOS and Linux
    ```

3.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the FastAPI backend:**

    Open a terminal and navigate to the `ToDoApp` directory. Then, run the following command:

    ```bash
    uvicorn src.main:app --reload
    ```

    This will start the FastAPI server on `http://localhost:8000`.

2.  **Start the Streamlit frontend:**

    Open another terminal, navigate to the `ToDoApp` directory, and run the following command:

    ```bash
    streamlit run frontend/streamlit_app.py
    ```

    This will open the Streamlit application in your web browser (usually on `http://localhost:8501`).

## Usage

1.  **Adding To-Do Items:**
    *   Expand the "Add New To-Do" section.
    *   Enter the title, description (optional), due date (optional), and priority (optional).
    *   Click the "Add To-Do" button.

2.  **Viewing To-Do Items:**
    *   The to-do items are displayed in a table format.

3.  **Marking Complete/Deleting To-Do Items:**
    *   Expand the "Mark Complete/Delete To-Do" section.
    *   Enter the ID of the to-do item you want to mark as complete or delete.
    *   Click the "Mark as Complete" or "Delete" button.

4.  **Filtering To-Do Items:**
    *   Expand the "Filter To-Dos" section.
    *   Select the priority and/or due date you want to filter by.
    *   Click the "Apply Filters" button.

5.  **Showing Completed To-Do Items:**
    *   Check the "Show Completed To-Dos" checkbox to display only the completed to-do items.

## Notes

*   The SQLite database file (`todos.db`) is created in the same directory as the `src.main.py` file.
*   The backend must be running before starting the frontend.
*   The frontend communicates with the backend via HTTP requests.

