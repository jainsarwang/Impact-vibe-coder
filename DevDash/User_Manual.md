# DevDash User Manual

## Introduction

DevDash is a simple web application that allows you to view a GitHub user's public repositories. This manual will guide you through the steps to use the application.

## Usage

1.  **Enter GitHub Username:**
    - In the input field, type the GitHub username of the user whose repositories you want to view.

2.  **Fetch Repositories:**
    - Click the "Fetch Repositories" button.
    - The application will then fetch the user's public repositories from the GitHub API.

3.  **View Repositories:**
    - If the user is found and the repositories are successfully fetched, a list of repositories will be displayed below the input field.
    - For each repository, the following information is displayed:
        - **Repository Name:** The name of the repository.
        - **Description:** A brief description of the repository (if available).
        - **Language:** The primary programming language used in the repository (if available).

4.  **Error Handling:**
    - If the user is not found, an error message "User not found" will be displayed.
    - If there is any other error during the fetching process, an error message "Could not fetch projects" will be displayed.

## Example

1.  Enter the username `github` in the input field.
2.  Click the "Fetch Repositories" button.
3.  You will see a list of GitHub's public repositories.

## Troubleshooting

- If you encounter any issues, make sure that:
    - You have a stable internet connection.
    - The GitHub username you entered is correct.
    - The GitHub API is accessible.

## Contact

If you have any questions or issues, please contact the developer.
