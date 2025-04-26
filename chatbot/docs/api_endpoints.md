
# API Endpoints

## Backend (Flask/FastAPI)

*   **/register (POST):** Registers a new user.
    *   Request: `{"username": "string", "password": "string"}`
    *   Response: `{"message": "User registered successfully"}` or `{"error": "string"}`
*   **/login (POST):** Logs in an existing user.
    *   Request: `{"username": "string", "password": "string"}`
    *   Response: `{"token": "string"}` or `{"error": "string"}`
*   **/chat (POST):** Sends a message to the chatbot and receives a response.
    *   Request: `{"message": "string", "image": "base64 encoded image (optional)", "video": "base64 encoded video (optional)"}`
    *   Response: `{"response": "string"}`
*   **/history (GET):** Retrieves the conversation history for the logged-in user.
    *   Request: None
    *   Response: `[{"user": "string", "bot": "string", "timestamp": "datetime"}, ...]`
*   **/summarize (POST):** Summarizes a given text.
    *   Request: `{"text": "string"}`
    *   Response: `{"summary": "string"}`

## Data Models

*   **User:**
    *   `username` (string): Unique username.
    *   `password` (string): Hashed password.
*   **Message:**
    *   `user` (string): User's message.
    *   `bot` (string): Bot's response.
    *   `timestamp` (datetime): Timestamp of the message.
