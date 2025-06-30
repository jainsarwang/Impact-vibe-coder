import logging
import json
from ..service.database import db
from ..models.model import chats_history_schema 
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph.types import State

# Create collection with strict schema validation
try:
    db.create_collection("session", validator=chats_history_schema)
    db.command({
        'collMod': 'chat_history',
        'validator': chats_history_schema,
        'validationLevel': 'strict',
        'validationAction': 'error'  # This makes it fail hard on invalid data
    })
except Exception as e:
    logging.info(f"Collection setup note: {str(e)}")
    # For existing collections, ensure the schema is applied strictly
    db.command({
        'collMod': 'chat_history',
        'validator': chats_history_schema,
        'validationLevel': 'strict',
        'validationAction': 'error'
    })
    
chat_history = db["chat_history"]

#Adding code for saving code_history starts here
def save_chat_history(state: "State") -> None:
    """
    Saves the Chat history to the chat_history collection in the database
    
    Args:
        state: The State object containing all chat history and state information
    
    Return:
        None, just saves the content in the database
    """
    logging.info("Entered into the save_chat_history to save the chat_history")
    try:
        # Convert State to a serializable dictionary
        state_dict = dict(state)
        
        # Convert messages to serializable format if they exist
        if 'messages' in state_dict and state_dict['messages']:
            serialized_messages = []
            for msg in state_dict['messages']:
                # Handle both message objects and dictionaries
                if hasattr(msg, 'dict'):  # It's a message object
                    msg_dict = msg.dict()
                    # Ensure all fields are present
                    serialized_msg = {
                        'content': msg_dict.get('content', ''),
                        'type': msg_dict.get('type', msg.__class__.__name__),
                        'additional_kwargs': msg_dict.get('additional_kwargs', {}),
                        'response_metadata': msg_dict.get('response_metadata', {}),
                        'id': msg_dict.get('id'),
                        'name': msg_dict.get('name')
                    }
                else:  # Assume it's already a dictionary
                    serialized_msg = msg
                serialized_messages.append(serialized_msg)
            state_dict['messages'] = serialized_messages
        
        update_data = {
            '$set': {
                'chat_history_id': state_dict['session_id'],
                'updated_at': datetime.now(),
                'chat': state_dict
            },
            '$setOnInsert': {
                'created_at': datetime.now()
            }
        }
        
        chat_history.update_one(
            {"chat_history_id": state_dict['session_id']},
            update_data,
            upsert=True
        )
        logging.info(f"Chat History saved successfully for session {state_dict['session_id']}")
        
    except Exception as e:
        logging.error(f"Error saving chat_history: {str(e)}", exc_info=True)
        if "Document failed validation" in str(e):
            logging.error("Validation error. State data: %s", json.dumps(state_dict, indent=2, default=str))
        # raise
    
#Adding code for saving code_history ends here