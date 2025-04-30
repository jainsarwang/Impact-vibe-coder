# DevDash

A simple web application to display a GitHub user's public repositories.

## Features

- Enter a GitHub username and view their public repositories.
- Displays repository name, description, and language.
- Handles errors gracefully (e.g., user not found).
- Clean and professional user interface.

## Technologies Used

- React
- GitHub API
- CSS

## Getting Started

1.  Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2.  Navigate to the project directory:

    ```bash
    cd DevDash
    ```

3.  Install dependencies:

    ```bash
    npm install
    ```

4.  Start the development server:

    ```bash
    npm start
    ```

5.  Open your browser and navigate to `http://localhost:3000`.

## User Manual

1.  Enter a GitHub username in the input field.
2.  Click the "Fetch Repositories" button.
3.  The application will display a list of the user's public repositories, including the name, description, and language (if available).
4.  If the user is not found or there is an error, an appropriate message will be displayed.
