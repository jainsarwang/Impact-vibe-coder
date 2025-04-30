# FinancialPDFChatbot User Manual

## Overview

The FinancialPDFChatbot is a Streamlit application that allows users to upload financial PDF documents and ask questions about their content. It uses Groq's `llama3-70b-versatile` model for generating responses.

## Prerequisites

Before running the application, ensure you have the following:

*   Python 3.7 or higher
*   The required Python packages (listed in `requirements.txt`)
*   A Groq API key (set as an environment variable `GROQ_API_KEY`)

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd FinancialPDFChatbot
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set the Groq API key:**

    Set the `GROQ_API_KEY` environment variable with your Groq API key. You can do this in your `.env` file or directly in your terminal.

    ```bash
    # Example using .env file
    echo "GROQ_API_KEY=YOUR_GROQ_API_KEY" > .env
    ```

## Running the Application

To start the chatbot application, run the following command in your terminal:

```bash
streamlit run src/chatbot.py
```

This will open the application in your web browser.

## Usage

1.  **Upload PDF Documents:**

    Click on the "Browse files" button to upload one or more financial PDF documents.

2.  **Process the PDF:**

    The application will automatically process the uploaded PDF documents and create a vectorstore for efficient question answering. A success message will be displayed once the processing is complete.

3.  **Ask Questions:**

    Enter your question in the chat input box and press Enter. The chatbot will generate a response based on the content of the uploaded PDF documents.

4.  **View the Response:**

    The chatbot's response will be displayed below the input box, along with the question you asked.

## Example Questions

*   "What is the net income for the year?"
*   "What are the key risks identified in the report?"
*   "Can you summarize the company's financial performance?"

## Troubleshooting

*   **Error: `GROQ_API_KEY not found`:**

    Ensure that you have set the `GROQ_API_KEY` environment variable correctly.

*   **Application crashes:**

    Check the console for any error messages and try restarting the application.

## Future Improvements

*   Add support for more file formats (e.g., DOCX, TXT).
*   Implement more sophisticated question answering techniques.
*   Improve the user interface and user experience.
*   Add a feature to save and load conversation history.
