from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import gemini
from agno.tools.duckduckgo import DuckDuckGoTools

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GEMINI_API_KEY"]
os.environ["GROQ_API_KEY"]

agent1 = Agent(
    model  = Groq(
        id = "llama-3.3-70b-versatile",
        provider = "Groq",
        response_format = 
        {
            """
            Hii, Solving you query
            """
        },
    ),
    
) 
