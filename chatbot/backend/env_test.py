import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API keys
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Print the API keys (for verification purposes)
print(f"Groq API Key: {groq_api_key}")
print(f"Gemini API Key: {gemini_api_key}")