
# README

## Backend Setup

1.  **Install Python:** Make sure you have Python 3.7+ installed.
2.  **Install Dependencies:**
    ```bash
    pip install flask flask-cors
    ```
3.  **Set API Keys:**
    *   Set the `GROQ_API_KEY` and `GEMINI_API_KEY` environment variables with your actual API keys.
    ```bash
    set GROQ_API_KEY=your_groq_api_key
    set GEMINI_API_KEY=your_gemini_api_key
    ```
4.  **Run the App:**
    ```bash
    python app.py
    ```

## API Endpoints

*   **/register (POST):** Registers a new user.
*   **/login (POST):** Logs in an existing user.
*   **/chat (POST):** Sends a message to the chatbot and receives a response.
*   **/history (GET):** Retrieves the conversation history for the logged-in user.
*   **/summarize (POST):** Summarizes a given text.

**Note:** This is a basic implementation and needs to be improved for production use.  Specifically, user authentication and data storage should be handled with more secure methods.
