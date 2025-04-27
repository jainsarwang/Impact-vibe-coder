import logging
from models.nlp_model import NLPModel
from utils.text_processor import TextProcessor
from utils.response_generator import ResponseGenerator

class SmartChatbot:
    def __init__(self, model):
        self.model = model
        self.text_processor = TextProcessor()
        self.response_generator = ResponseGenerator()
        self.history = []
        logging.info('SmartChatbot initialized')
        
    def get_response(self, input_text):
        # Process the input text
        processed_text = self.text_processor.preprocess(input_text)
        
        # Generate embedding using the model
        embedding = self.model.generate_embedding(processed_text)
        
        # Find the most appropriate response
        response = self.response_generator.generate(embedding, self.history)
        
        # Update conversation history
        self.history.append({'input': input_text, 'response': response})
        
        return response
    
    def clear_history(self):
        self.history = []
        logging.info('Conversation history cleared')