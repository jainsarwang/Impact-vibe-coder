import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI as ChatGemini
from src.config.agents import LLMType
from google import genai

# Groq Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Updated model names based on Groq's current offerings
REASONING_MODEL_GROQ = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Good for reasoning tasks
BASIC_MODEL_GROQ = "llama-3.3-70b-versatile"  # Good general purpose model
VL_MODEL_GROQ = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Most capable model available

# Gemini Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


# Cache for LLM instances
_llm_cache: dict[LLMType, ChatOpenAI] = {}

def create_groq_llm(model: str, temperature: float = 0.0) -> ChatOpenAI:
    """Create a Groq LLM instance using LangChain's ChatOpenAI with Groq's API"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")

    return ChatOpenAI(
        model=model,
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )

def create_gemini_llm(model: str, response_schema = None, temperature: float = 0.0) -> ChatGemini:
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    llm = ChatGemini(
        model=model,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    if response_schema:
        # Simply pass the schema to guide the response format
        llm = llm.with_config({
            "response_schema": response_schema
        })

    return llm

def get_llm_by_type(llm_type: LLMType, schema = None) -> ChatOpenAI | genai.Client:
    """Get LLM instance by type. Returns cached instance if available."""

    if llm_type == "basic":
        if GOOGLE_API_KEY:
            llm = create_gemini_llm(model="gemini-2.5-flash-preview-04-17", response_schema=schema)
    elif llm_type == "reasoning":
        if GROQ_API_KEY:
            llm = create_gemini_llm(model="gemini-2.0-flash", response_schema=schema)
        else:
            raise ValueError("GROQ_API_KEY environment variable not set for basic LLM.")
    elif llm_type == "vision":
        if GROQ_API_KEY:
            llm = create_gemini_llm(model="gemini-2.0-flash", response_schema=schema)
        else:
            raise ValueError("GROQ_API_KEY environment variable not set for vision LLM.")
    elif llm_type == "version_llm":
        if GOOGLE_API_KEY:
            llm = create_groq_llm(BASIC_MODEL_GROQ)
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}")

    _llm_cache[llm_type] = llm
    return llm

# Initialize LLMs for different purposes - now these will be cached
reasoning_llm = None
basic_llm = None
version_llm =None
try:
    reasoning_llm = get_llm_by_type("reasoning")
    basic_llm = get_llm_by_type("basic")
    vl_llm = get_llm_by_type("vision")
    version_llm = get_llm_by_type("version_llm")
    
except ValueError as e:
    print(f"Error initializing LLMs: {e}")
    print("Please check:")
    if "GEMINI_API_KEY" in str(e):
        print("1. Your GEMINI_API_KEY is set correctly")
    if "GROQ_API_KEY" in str(e):
        print("2. Your GROQ_API_KEY is set correctly")
        print("3. The Groq model names are current for Groq's API")
        print("4. You have access to these Groq models")
    raise
except Exception as e:
    print(f"An unexpected error occurred during LLM initialization: {e}")
    raise