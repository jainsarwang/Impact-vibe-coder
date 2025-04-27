import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models.nlp_model import NLPModel
from chatbot import SmartChatbot

load_dotenv()

app = Flask(__name__)
model = NLPModel()
chatbot = SmartChatbot(model)

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    message = data.get('message', '')
    response = chatbot.get_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'False') == 'True')