/* README.md */

# Frontend Setup

1.  **Install Node.js:** Make sure you have Node.js installed (version 14 or higher).
2.  **Install Dependencies:**

    ```bash
    npm install
    ```

3.  **Run the App:**

    ```bash
    npm start
    ```

    This will start the development server and open the app in your browser.

## Project Structure

*   `src/`: Contains the React components and styling.
    *   `App.js`: Main component for the chatbot interface.
    *   `App.css`: Styling for the main component.
    *   `index.js`: Entry point for the React app.
    *   `index.css`: Global styles.

## API Configuration

The frontend is configured to communicate with the backend at `http://127.0.0.1:5000`.  If your backend is running on a different address, you will need to update the `backendUrl` variable in `src/App.js`.
