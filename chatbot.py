#Prayag sahu
import os
import re
from datetime import datetime
from groq import Groq
import streamlit as st
from google import genai
from dotenv import load_dotenv
from google.genai import types

load_dotenv() # load the python .env file

# Load coordinator.md content
def get_prompt_template():
    try:
        with open("coordinator.md", "r") as f:
            template = f.read()
        # Escape curly braces using backslash
        template = template.replace("{", "{{").replace("}", "}}")
        # Replace `<<VAR>>` with `{VAR}`
        template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
        return template
    except FileNotFoundError:
        st.error("coordinator.md file not found. Using default system prompt.")
        return """
        You are an expert solution architect. You specialize in gathering requirements for projects.
        Your primary responsibilities are:
        - Communicate with user to get enough context about their project requirements
        - Specify requirements clearly
        - Keep asking for context if needed
        """

def apply_prompt_template(state: dict = None):
    system_prompt = get_prompt_template()
    if state:
        # Format with current time and any state variables
        current_time = datetime.now().strftime("%a %b %d %Y %H:%M:%S %z")
        system_prompt = system_prompt.format(CURRENT_TIME=current_time, **state)
    return [{"role": "system", "content": system_prompt}]

#custom css for different elemets
st.markdown(
    """
    <style>
    body {
        font-family: Arial, Helvetica, sans-serif;
        background-color: #fefcef; /* Set body background */
    }

    .stApp {
        background-color: #fefcef !important; /* Set Streamlit app background */
    }

    .stElementContainer:has(.stHeading) {
        position: sticky;
        top: 60px;
        z-index: 10;
    }

    h1 {
        text-align: center;
        color: blue;
        font-weight: bold;
        margin-bottom: 20px;
        position: sticky;
        top: 0;
        background-color: #fefcef;
        z-index: 100; /* Ensure header is above other elements */
        padding-top:10px;
        padding-bottom:10px;
    }

    .st-emotion-cache-128upt6 {
        background-color: #fefcef
    }

    .st-emotion-cache-yd4u6l
    {
        background-color:white;
    }
    .st-emotion-cache-yd4u6l textarea
    {
        background-color:white;
    }

    [data-testid="stSidebar"] {
        background-color: #f2dddd;
        color: black;
        padding: 10px;
        border-radius: 15px;
    }

    [data-testid="stSelectbox"],
    [data-testid="stSelectbox"] input {
        border-radius: 20px !important;
        padding: 5px !important;
    }

    [data-testid="stChatInputContainer"]{
        background-color:white; /*Chat Input background*/
    }

    </style>
    """,
    unsafe_allow_html=True,
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_KEY = os.getenv("GEMINI_API_KEY")

client_google = genai.Client(api_key=API_KEY)
client = Groq(api_key=GROQ_API_KEY)

# Initialize session state
if "model_names" not in st.session_state:
    st.session_state.model_names = client.models.list()

if "model_name" not in st.session_state:
    st.session_state.model_name = "llama3-70b-8192"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "top_p" not in st.session_state:
    st.session_state.top_p = 0.9

if "max_completion_tokens" not in st.session_state:
    st.session_state.max_completion_tokens = 2048

if "presence_penalty" not in st.session_state:
    st.session_state.presence_penalty = 0.0

if "frequency_penalty" not in st.session_state:
    st.session_state.frequency_penalty = 0.0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = apply_prompt_template()

# set up the client for the groq api calling
def chat_response(prompt):
    if "gemini" in st.session_state.model_name:
        response = client_google.models.generate_content_stream(
            model=st.session_state.model_name,
            contents=st.session_state.chat_history + [{"role": "user", "content": prompt}],
            config=types.GenerateContentConfig(
                temperature=st.session_state.temperature
            )
        )
        for chunk in response:
            yield chunk.text
    else:
        stream = client.chat.completions.create(
            messages=st.session_state.chat_history + [{"role": "user", "content": prompt}],
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
            top_p=st.session_state.top_p,
            max_tokens=st.session_state.max_completion_tokens,
            presence_penalty=st.session_state.presence_penalty,
            frequency_penalty=st.session_state.frequency_penalty,
            stream=True,
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content

# Model lists
model_list = []
model_list_audio = ["whisper-large-v3-turbo", "distil-whisper-large-v3-en", "whisper-large-v3"]
for model in st.session_state.model_names.data:
    if model.id not in model_list_audio:
        model_list.append(model.id)
model_list.extend(["gemini-1.5-flash", "gemini-1.5-pro"])

# UI Elements
st.title("Solution Architect Assistant")

# Chat input
prompt = st.chat_input("Enter your project requirements")

# Display chat history (excluding system message)
for message in st.session_state.chat_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    placeholder = st.empty()
    full_response = ""
    response_generator = chat_response(prompt)
    
    for chunk in response_generator:
        if chunk:
            full_response += chunk
            placeholder.markdown(full_response + "▌")
    
    placeholder.markdown(full_response)
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# Sidebar controls
with st.sidebar:
    st.header("Model Configuration")
    
    model_name = st.selectbox(
        "Model",
        options=model_list,
        index=model_list.index(st.session_state.model_name) if st.session_state.model_name in model_list else 0
    )
    st.session_state.model_name = model_name
    
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls randomness (0 = deterministic, 2 = most random)"
    )
    
    st.session_state.top_p = st.slider(
        "Top-P",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.top_p,
        step=0.1,
        help="Controls diversity via nucleus sampling"
    )
    
    st.session_state.max_completion_tokens = st.slider(
        "Max Tokens",
        min_value=128,
        max_value=8192,
        value=st.session_state.max_completion_tokens,
        step=128,
        help="Maximum number of tokens to generate"
    )
    
    st.session_state.presence_penalty = st.slider(
        "Presence Penalty",
        min_value=-2.0,
        max_value=2.0,
        value=st.session_state.presence_penalty,
        step=0.1,
        help="Positive values penalize new tokens based on whether they appear in the text so far"
    )
    
    st.session_state.frequency_penalty = st.slider(
        "Frequency Penalty",
        min_value=-2.0,
        max_value=2.0,
        value=st.session_state.frequency_penalty,
        step=0.1,
        help="Positive values penalize new tokens based on their existing frequency in the text so far"
    )
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = apply_prompt_template()
        st.rerun()