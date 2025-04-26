
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# Replace with your actual API keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Function to call Groq API
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",  # Or any other Groq model
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to call Gemini API
def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message']

    # Logic to choose between Groq and Gemini
    # For simplicity, let's use Groq for short messages and Gemini for long ones
    if len(message) < 100:
        try:
            groq_response = call_groq(message)
            reply = groq_response['choices'][0]['message']['content']
            return jsonify({'reply': reply, 'source': 'Groq'})
        except Exception as e:
            print(f"Error calling Groq: {e}")
            return jsonify({'reply': 'Error processing with Groq', 'source': 'Error'})
    else:
        try:
            gemini_response = call_gemini(message)
            reply = gemini_response['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'reply': reply, 'source': 'Gemini'})
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return jsonify({'reply': 'Error processing with Gemini', 'source': 'Error'})

if __name__ == '__main__':
    app.run(debug=True)
