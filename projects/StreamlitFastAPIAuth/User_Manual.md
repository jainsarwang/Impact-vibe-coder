
# Streamlit and FastAPI Authentication System

This project demonstrates a simple user authentication system using Streamlit for the frontend, FastAPI for the backend, and SQLite for the database.

## Project Structure

-   `backend/`: Contains the FastAPI application (`main.py`) and the SQLite database file (`sql_app.db` - created on first run).
-   `frontend/`: Contains the Streamlit application (`app.py`).
-   `requirements.txt`: Lists the necessary Python dependencies.
-   `package.json`: Basic project metadata and scripts.
-   `User_Manual.md`: This manual.

## Setup

1.  **Clone or Download:** Get the project files.
2.  **Install Dependencies:** Navigate to the project's root directory in your terminal and install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

The application consists of two parts: the backend (FastAPI) and the frontend (Streamlit). Both need to be running simultaneously.

1.  **Start the Backend:**
    Open a terminal, navigate to the project's root directory (`StreamlitFastAPIAuth`), and run the FastAPI application using uvicorn:

    ```bash
    uvicorn backend.main:app --reload
    ```
    The `--reload` flag is useful during development as it restarts the server on code changes. The backend will run on `http://localhost:8000` by default.

2.  **Start the Frontend:**
    Open a **new** terminal window, navigate to the project's root directory (`StreamlitFastAPIAuth`), and run the Streamlit application:

    ```bash
    streamlit run frontend/app.py
    ```
    Streamlit will typically open the application in your web browser at `http://localhost:8501`.

## Usage

1.  **Sign Up:** On the initial page, click "Go to Sign Up" or navigate to the Sign Up form directly. Enter a desired username and password and click "Sign Up". If successful, you will see a success message and can then go to the Login page.
2.  **Login:** On the Login page, enter the username and password you used to sign up and click "Login". If the credentials are correct, you will be redirected to the Dashboard.
3.  **Dashboard:** This page is only accessible after successful login. It displays a welcome message with your username and a "Logout" button.
4.  **Logout:** Clicking the "Logout" button will log you out and return you to the Login page.

## Additional Features (Decided by Researcher)

-   **Secure Password Handling:** Passwords are not stored in plain text; they are hashed using bcrypt.
-   **Basic Error Handling:** The application handles cases like duplicate usernames during signup and incorrect credentials during login.
-   **Session Management:** Streamlit's `st.session_state` is used to maintain the user's authentication status across interactions.
-   **Clear Navigation:** Buttons are provided to switch between the Login and Sign Up forms.

This provides a basic framework. Further features like password reset, email verification, or more complex user profiles could be added.
