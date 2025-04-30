# DevDash User Manual

## Overview

DevDash is a simple web application that allows you to view the public repositories of a GitHub user. Simply enter the username and click "Fetch Repos" to see a list of their repositories.

## Usage

1.  Open the `index.html` file in your web browser.
2.  Enter the GitHub username in the input field.
3.  Click the "Fetch Repos" button.
4.  The list of public repositories for the user will be displayed below.

## Error Handling

*   If you do not enter a username, an error message will appear.
*   If the GitHub API returns an error (e.g., user not found), an error message will be displayed.
*   If the user has no public repositories, a message will be displayed.

## Files

*   `index.html`: The main HTML file for the application.
*   `style.css`: The CSS file for styling the application.
*   `script.js`: The JavaScript file for handling the API call and displaying the results.
*   `package.json`: The package file.
